# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.
# db_store, a simple database abstraction layer
#
# raison d'etre
# 1) db_store.py should be roughly as simple as using plain pickle/jsonpickle, but scaling better
# 2) db_store.py handles common tasks like checking latest schema
# 3) db_store.py doesn't have pysqlite's unexpected transaction semantics
# 4) sqlite is better than jsonpickle because of indexes and reduced writing-to-disk
# 5) eventually, db_store.py can be an abstract layer supporting different backends

# Update Nov 2022: 
# to install apsw, run
#    python -m pip install apsw
# Older instructions:
#    install a apsw release from the rogerbinns website, or run a command like this,
#    python -m pip install --user
#    https://github.com/rogerbinns/apsw/releases/download/3.16.2-r1/apsw-3.16.2-r1.zip
#    --global-option=fetch --global-option=--version --global-option=3.16.2 --global-option=--all
#    --global-option=build --global-option=--enable-all-extensions

from ..common_util import *
from .. import files
import apsw
import sys
import re


class Store(object):
    conn = None
    in_txn = False

    def add_schema(self, cursor):
        raise NotImplementedError('please inherit from Store and implement this method')

    def current_schema_version_number(self):
        raise NotImplementedError('please inherit from Store and implement this method')

    def stamp_schema_version(self, cursor):
        if self.current_schema_version_number() is None:
            return

        cursor.execute('CREATE TABLE ben_python_common_store_properties(schema_version INT)')
        cursor.execute('INSERT INTO ben_python_common_store_properties(schema_version) VALUES(?)',
            [self.current_schema_version_number()])

    def verify_schema_version(self):
        if self.current_schema_version_number() is None:
            return

        cursor = self.conn.cursor()
        try:
            valid = False
            got = None
            for version in cursor.execute('SELECT schema_version FROM ben_python_common_store_properties'):
                got = int(version[0])
                if got == int(self.current_schema_version_number()):
                    valid = True

            if not valid:
                raise StoreException('DB is empty or comes from a different version. Expected schema version %s, got %s' %
                    (int(self.current_schema_version_number()), got))
        except:
            if 'SQLError: no such table:' in str(sys.exc_info()[1]):
                raise StoreException(
                    '\n\nSchema version table not found, maybe this is a 0kb empty db. Please delete the db and try again.')
            else:
                raise

    def cursor(self):
        return self.conn.cursor()

    def row_exists(self, cursor, *args):
        for row in cursor.execute(*args):
            return True
        return False

    def connect_or_create(self, dbpath, flags=None):
        if flags is None:
            flags = apsw.SQLITE_OPEN_NOMUTEX | apsw.SQLITE_OPEN_READWRITE | apsw.SQLITE_OPEN_CREATE
        did_exist = files.isfile(dbpath)
        self.conn = apsw.Connection(dbpath, flags=flags)
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA temp_store = memory')
        cursor.execute('PRAGMA page_size = 16384')
        cursor.execute('PRAGMA cache_size = 1000')
        if not did_exist:
            self.txn_begin()
            cursor = self.conn.cursor()
            self.add_schema(cursor)
            self.stamp_schema_version(cursor)
            self.txn_commit()

        self.verify_schema_version()

    def txn_begin(self):
        assertTrue(not self.in_txn, 'txn_begin when in')
        self.cursor().execute('BEGIN TRANSACTION')
        self.in_txn = True

    def txn_rollback(self):
        assertTrue(self.in_txn, 'txn_rollback when not in')
        self.cursor().execute('ROLLBACK TRANSACTION')
        self.in_txn = False

    def txn_commit(self):
        assertTrue(self.in_txn, 'txn_commit when not in')
        self.cursor().execute('COMMIT TRANSACTION')
        self.in_txn = False

    def close(self):
        if self.in_txn:
            self.txn_rollback()
        
        if self.conn:
            self.conn.close()
            self.conn = None

class StoreWithCrudHelpers(Store):
    def  __init__(self, dbpath=None, flags=None, autoConnect=True):
        assertTrue(isPy3OrNewer, 'Python 3 required')
        super().__init__()

        self.re_check = re.compile('^[a-zA-Z0-9]+$')
        self.schema = self.get_field_names_and_attributes()
        self.default_tbl = [tbl for tbl in self.schema][0]
        if autoConnect:
            self.connect_or_create(dbpath, flags)
    
    def get_field_names_and_attributes(self):
        # example return {'tblName': {'fld1': {'initprops': 'not null'}, 'fld2': {'index': True}, 'fld3': {}}}
        raise NotImplementedError('please inherit from Store and implement this method')
    
    def add_schema(self, cursor):
        for tbl in self.schema:
            # add fields
            tblschema = self.schema[tbl]
            s = 'CREATE TABLE %s (' % self._check(tbl)
            to_add = []
            for fld in tblschema:
                to_add.append(self._check(fld) + ' ' + tblschema[fld].get('initprops', ''))
            s += ', '.join(to_add)
            s += ')'
            cursor.execute(s)

            # add index
            for fld in tblschema:
                if tblschema[fld].get('index'):
                    modifier = ''
                    if tblschema[fld].get('index') == 'unique':
                        modifier = 'UNIQUE'
                    elif tblschema[fld].get('index') is True:
                        modifier = ''
                    else:
                        raise Exception('unknown index type')

                    cursor.execute('CREATE ' + modifier + ' INDEX ix_' + self._check(tbl) +  \
                        '_' + self._check(fld) + ' on ' + self._check(tbl) + '(' + self._check(fld) + ')')

    def insert(self, record_data, table=None):
        # record_data is a dict from field names to values
        table = table or self.default_tbl
        s = 'INSERT INTO ' + self._check(table) + ' ('
        flds = [self._check(fld) for fld in record_data]
        markers = ['?' for _ in record_data]
        s += ', '.join(flds) + ') VALUES (' + ', '.join(markers) + ')'
        vals = [record_data[fld] for fld in record_data]
        cursor = self.cursor()
        return cursor.execute(s, vals)

    def delete(self, conditions, table=None):
        # conditions is a dict from field names to values
        table = table or self.default_tbl
        s = 'DELETE FROM ' +  self._check(table) + ' WHERE '
        conditionflds = [self._check(fld) + ' = ?' for fld in conditions]
        s += ' AND '.join(conditionflds)
        vals = [conditions[fld] for fld in conditions]
        cursor = self.cursor()
        return cursor.execute(s, vals)
    
    def update(self, conditions, updates, table=None):
        # conditions an updates is a dict from field names to values
        updateflds = [self._check(fld) + ' = ?' for fld in updates]
        conditionflds = [self._check(fld) + ' = ?' for fld in conditions]

        table = table or self.default_tbl
        s = 'UPDATE ' +  self._check(table) + ' SET '
        s += ' , '.join(updateflds) + ' WHERE '
        s += ' AND '.join(conditionflds)
        updatevals = [updates[fld] for fld in updates]
        conditionvals = [conditions[fld] for fld in conditions]
        cursor = self.cursor()
        return cursor.execute(s, updatevals + conditionvals)

    def query(self, conditions, table=None, limit=None):
        # conditions is a dict from field names to values
        table = table or self.default_tbl
        allflds = ', '.join([self._check(fld) for fld in self.schema[table]])
        s = 'SELECT ' + allflds + ' FROM ' +  self._check(table) + ' WHERE '
        conditionflds = [self._check(fld) + ' = ?' for fld in conditions]
        s += ' AND '.join(conditionflds)
        if limit:
            s += ' LIMIT ' + self._check(str(limit))
        vals = [conditions[fld] for fld in conditions]
        cursor = self.cursor()
        raw_results = cursor.execute(s, vals)
        if raw_results:
            results = []
            for record in raw_results:
                results.append(self._tuple_to_dict(self.schema[table], record))
            return results
        else:
            return []
    
    def query_one(self, conditions, table=None):
        results = self.query(conditions, table, limit=1)
        return results[0] if results else None

    def _tuple_to_dict(self, tableschema, tpl):
        assertEq(len(tpl), len(tableschema), 'different lengths')
        fldnames = (fld for fld in tableschema)
        return dict(zip(fldnames, tpl))
    
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
    
    def _check(self, s):
        if not self.re_check.match(s):
            raise Exception('invalid identifier (only alphanumeric reqd) ' + s)
            
        return s

class StoreException(Exception):
    def __str__(self):
        return 'StoreException: ' + Exception.__str__(self)


