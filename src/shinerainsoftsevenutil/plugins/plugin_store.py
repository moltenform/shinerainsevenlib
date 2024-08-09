
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

# SrssStore, a database abstraction layer
# as of Nov 2022, apsw can be installed by simply running python -m pip install apsw

import re
from .plugin_fileexts import *
from .. import files
from .. import core as srss
from ..core import assertTrue, assertEq

class SrssStoreBasic:
    """
    SrssStore, a database abstraction layer

    1) SrssStore should be about as simple as using pickle/jsonpickle, but scaling better
    2) SrssStore handles common tasks like checking latest schema
    3) SrssStore doesn't have pysqlite's unclear transaction semantics
    4) better than jsonpickle because of indexes and reduced writing-to-disk
    5) SrssStore is an abstract layer that can support different backends
    """

    conn = None
    in_txn = False

    def addSchema(self, cursor):
        raise NotImplementedError('please inherit from Store and implement this method')

    def currentSchemaVersionNumber(self):
        raise NotImplementedError('please inherit from Store and implement this method')

    def stampSchemaVersion(self, cursor):
        if self.currentSchemaVersionNumber() is None:
            return

        cursor.execute('CREATE TABLE shinerainsoftsevenutil_store_properties(schema_version INT)')
        cursor.execute(
            'INSERT INTO shinerainsoftsevenutil_store_properties(schema_version) VALUES(?)',
            [self.currentSchemaVersionNumber()],
        )

    def verifySchemaVersion(self):
        if self.currentSchemaVersionNumber() is None:
            return

        cursor = self.conn.cursor()
        try:
            valid = False
            got = None
            for version in cursor.execute(
                'SELECT schema_version FROM shinerainsoftsevenutil_store_properties'
            ):
                got = int(version[0])
                if got == int(self.currentSchemaVersionNumber()):
                    valid = True

            if not valid:
                raise SrssStoreException(
                    'DB is empty or comes from a different version. Expected schema version %s, got %s'
                    % (int(self.currentSchemaVersionNumber()), got)
                )
        except Exception as e:
            if 'SQLError: no such table:' in str(srss.getCurrentException()):
                raise SrssStoreException(
                    '\n\nSchema version table not found, maybe this is a 0kb empty db. Please delete the db and try again.'
                ) from e
            else:
                raise

    def cursor(self):
        return self.conn.cursor()

    def rowExists(self, cursor, *args):
        for _row in cursor.execute(*args):
            return True
        return False

    def connectOrCreate(self, dbpath, flags=None):
        import apsw
        if flags is None:
            flags = apsw.SQLITE_OPEN_NOMUTEX | apsw.SQLITE_OPEN_READWRITE | apsw.SQLITE_OPEN_CREATE
        did_exist = files.isFile(dbpath)
        self.conn = apsw.Connection(dbpath, flags=flags)
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA temp_store = memory')
        cursor.execute('PRAGMA page_size = 16384')
        cursor.execute('PRAGMA cache_size = 1000')
        if not did_exist:
            self.txnBegin()
            cursor = self.conn.cursor()
            self.addSchema(cursor)
            self.stampSchemaVersion(cursor)
            self.txnCommit()

        self.verifySchemaVersion()

    def txnBegin(self):
        assertTrue(not self.in_txn, 'txnBegin when in')
        self.cursor().execute('BEGIN TRANSACTION')
        self.in_txn = True

    def txnRollback(self):
        assertTrue(self.in_txn, 'txnRollback when not in')
        self.cursor().execute('ROLLBACK TRANSACTION')
        self.in_txn = False

    def txnCommit(self):
        assertTrue(self.in_txn, 'txnCommit when not in')
        self.cursor().execute('COMMIT TRANSACTION')
        self.in_txn = False

    def close(self):
        if self.in_txn:
            self.txnRollback()

        if self.conn:
            self.conn.close()
            self.conn = None

class SrssStore(SrssStoreBasic):
    def __init__(self, dbpath=None, flags=None, autoConnect=True):
        assertTrue(srss.isPy3OrNewer, 'Python 3 required')
        super().__init__()

        self.re_check = re.compile('^[a-zA-Z0-9]+$')
        self.schema = self.getFieldNamesAndAttributes()
        self.default_tbl = list(self.schema)[0]
        if autoConnect:
            self.connectOrCreate(dbpath, flags)

    def getFieldNamesAndAttributes(self):
        # example return {'tblName': {'fld1': {'initprops': 'not null'}, 'fld2': {'index': True}, 'fld3': {}}}
        raise NotImplementedError('please inherit from Store and implement this method')

    def addSchema(self, cursor):
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
                        raise SrssStoreException('unknown index type')

                    cursor.execute(
                        'CREATE ' +
                        modifier +
                        ' INDEX ix_' +
                        self._check(tbl) +
                        '_' +
                        self._check(fld) +
                        ' on ' +
                        self._check(tbl) +
                        '(' +
                        self._check(fld) +
                        ')'
                    )

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
        s = 'DELETE FROM ' + self._check(table) + ' WHERE '
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
        s = 'UPDATE ' + self._check(table) + ' SET '
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
        s = 'SELECT ' + allflds + ' FROM ' + self._check(table) + ' WHERE '
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
                results.append(self.tupleToDict(self.schema[table], record))
            return results
        else:
            return []

    def queryOne(self, conditions, table=None):
        results = self.query(conditions, table, limit=1)
        return results[0] if results else None

    def tupleToDict(self, tableSchema, tpl):
        assertEq(len(tpl), len(tableSchema), 'different lengths')
        fldnames = (fld for fld in tableSchema)
        return dict(zip(fldnames, tpl))

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _check(self, s):
        if not self.re_check.match(s):
            raise SrssStoreException('invalid identifier (only alphanumeric reqd) ' + s)

        return s

class SrssStoreException(Exception):
    def __str__(self):
        return 'SrssStoreException: ' + Exception.__str__(self)
