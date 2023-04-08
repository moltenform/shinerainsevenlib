# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

import pytest
import tempfile
from ..common_util import isPy3OrNewer
from ..store import Store, StoreWithCrudHelpers, StoreException
from ..files import join, getsize, writeall, ensureEmptyDirectory

class TestStorage(object):
    def test_that_schema_version_is_set(self, fixture_temp_db):
        db, _ = fixture_temp_db
        assert db.row_exists(db.cursor(), 'SELECT * FROM ben_python_common_store_properties WHERE schema_version==1')

    def test_that_wrong_schema_version_is_not_set(self, fixture_temp_db):
        db, _ = fixture_temp_db
        assert not db.row_exists(db.cursor(), 'SELECT * FROM ben_python_common_store_properties WHERE schema_version==2')

    def test_opening_with_no_schema_version(self, fixture_temp_db):
        db, dbpath = fixture_temp_db
        db.cursor().execute('DELETE FROM ben_python_common_store_properties WHERE 1')
        db.close()
        with pytest.raises(StoreException) as exc:
            db.connect_or_create(dbpath)
        exc.match('DB is empty or comes from a different version. Expected schema version 1, got None')

    def test_opening_with_prev_schema_version(self, fixture_temp_db):
        db, dbpath = fixture_temp_db
        db.cursor().execute('UPDATE ben_python_common_store_properties SET schema_version=0 WHERE 1')
        db.close()
        with pytest.raises(StoreException) as exc:
            db.connect_or_create(dbpath)
        exc.match('DB is empty or comes from a different version. Expected schema version 1, got 0')

    def test_opening_with_future_schema_version(self, fixture_temp_db):
        db, dbpath = fixture_temp_db
        db.cursor().execute('UPDATE ben_python_common_store_properties SET schema_version=2 WHERE 1')
        db.close()
        with pytest.raises(StoreException) as exc:
            db.connect_or_create(dbpath)
        exc.match('DB is empty or comes from a different version. Expected schema version 1, got 2')

    def test_emptyDatabaseException(self, fixture_temp_db):
        db, dbpath = fixture_temp_db
        writeall(dbpath, '')
        assert 0 == getsize(dbpath)
        with pytest.raises(StoreException) as exc:
            db.connect_or_create(dbpath)
        exc.match('Schema version table not found')

    def test_commitTransaction(self, fixture_temp_db):
        db, _ = fixture_temp_db
        db.cursor().execute('INSERT INTO testtable(a, b, c) VALUES (1, 2, 3)')
        db.txn_begin()
        db.cursor().execute('INSERT INTO testtable(a, b, c) VALUES (4, 5, 6)')
        db.cursor().execute('INSERT INTO testtable(a, b, c) VALUES (7, 8, 9)')
        db.txn_commit()
        assert db.row_exists(db.cursor(), 'SELECT * FROM testtable WHERE c==3')
        assert db.row_exists(db.cursor(), 'SELECT * FROM testtable WHERE c==6')
        assert db.row_exists(db.cursor(), 'SELECT * FROM testtable WHERE c==9')

    def test_rollbackTransaction(self, fixture_temp_db):
        db, _ = fixture_temp_db
        db.cursor().execute('INSERT INTO testtable(a, b, c) VALUES (1, 2, 3)')
        db.txn_begin()
        db.cursor().execute('INSERT INTO testtable(a, b, c) VALUES (4, 5, 6)')
        db.cursor().execute('INSERT INTO testtable(a, b, c) VALUES (7, 8, 9)')
        db.txn_rollback()
        assert db.row_exists(db.cursor(), 'SELECT * FROM testtable WHERE c==3')
        assert not db.row_exists(db.cursor(), 'SELECT * FROM testtable WHERE c==6')
        assert not db.row_exists(db.cursor(), 'SELECT * FROM testtable WHERE c==9')

@pytest.mark.skipif('not isPy3OrNewer')
class TestCrudHelper(object):
    def test_addSchema(self):
        o = StoreWithCrudHelpersDemo(autoConnect=False)
        cursor = MockCursor()
        o.add_schema(cursor)
        assert len(cursor.queries) == 3
        assert cursor.queries[0] == 'CREATE TABLE firstTable (fld1 not null, fld2 , fld3 )'
        assert cursor.queries[1] == 'CREATE  INDEX ix_firstTable_fld2 on firstTable(fld2)'
        assert cursor.queries[2] == 'CREATE TABLE secondTable (oFld1 , oFld2 , oFld3 )'
        
    def test_addUniqueIndex(self):
        class StoreWithCrudHelpersDemoUnique(StoreWithCrudHelpers):
            def get_field_names_and_attributes(self):
                return {'firstTable': {'fld1': {'initprops': 'not null'}, 'fld2': {'index': 'unique'}, 'fld3': {}},
                    'secondTable': {'oFld1': {}, 'oFld2': {}, 'oFld3': {}},
                    }
        o = StoreWithCrudHelpersDemoUnique(autoConnect=False)
        cursor = MockCursor()
        o.add_schema(cursor)
        assert len(cursor.queries) == 3
        assert cursor.queries[0] == 'CREATE TABLE firstTable (fld1 not null, fld2 , fld3 )'
        assert cursor.queries[1] == 'CREATE UNIQUE INDEX ix_firstTable_fld2 on firstTable(fld2)'
        assert cursor.queries[2] == 'CREATE TABLE secondTable (oFld1 , oFld2 , oFld3 )'
    
    def test_insert(self):
        o = StoreWithCrudHelpersDemo(autoConnect=False)
        o.insert({'fld1': 'val1', 'fld3': 'val3'})
        assert o.mockCursor.queries[0] == 'INSERT INTO firstTable (fld1, fld3) VALUES (?, ?)'
        assert o.mockCursor.queryParams[0] == ['val1', 'val3']

    def test_delete(self):
        o = StoreWithCrudHelpersDemo(autoConnect=False)
        o.delete({'fld1': 'val1', 'fld3': 'val3'})
        assert o.mockCursor.queries[0] == 'DELETE FROM firstTable WHERE fld1 = ? AND fld3 = ?'
        assert o.mockCursor.queryParams[0] == ['val1', 'val3']
    
    def test_update(self):
        o = StoreWithCrudHelpersDemo(autoConnect=False)
        o.update({'fld1': 'val1', 'fld3': 'val3'}, {'fld1': 'newVal1', 'fld3': 'newVal3'})
        assert o.mockCursor.queries[0] == 'UPDATE firstTable SET fld1 = ? , fld3 = ? WHERE fld1 = ? AND fld3 = ?'
        assert o.mockCursor.queryParams[0] == ['newVal1', 'newVal3', 'val1', 'val3']

    def test_update_two(self):
        o = StoreWithCrudHelpersDemo(autoConnect=False)
        o.update({'fld2': 'f2'}, {'fld1': 'newVal1', 'fld3': 'newVal3'})
        assert o.mockCursor.queries[0] == 'UPDATE firstTable SET fld1 = ? , fld3 = ? WHERE fld2 = ?'
        assert o.mockCursor.queryParams[0] == ['newVal1', 'newVal3', 'f2']
    
    def test_query(self):
        o = StoreWithCrudHelpersDemo(autoConnect=False)
        o.query({'fld1': 'val1', 'fld3': 'val3'})
        assert o.mockCursor.queries[0] == 'SELECT fld1, fld2, fld3 FROM firstTable WHERE fld1 = ? AND fld3 = ?'
        assert o.mockCursor.queryParams[0] == ['val1', 'val3']

class StoreDemo(Store):
    def add_schema(self, cursor):
        cursor.execute('CREATE TABLE testtable(a, b, c)')
        cursor.execute('CREATE INDEX ix_testtable_c on testtable(c)')

    def current_schema_version_number(self):
        return 1

class MockCursor():
    def __init__(self):
        self.queries = []
        self.queryParams = []
    def execute(self, s, params=None):
        self.queries.append(s)
        self.queryParams.append(params)

class StoreWithCrudHelpersDemo(StoreWithCrudHelpers):
    def __init__(self, dbpath=None, flags=None, autoConnect=True):
        super().__init__(dbpath, flags, autoConnect)
        self.mockCursor = MockCursor()

    def get_field_names_and_attributes(self):
        return {'firstTable': {'fld1': {'initprops': 'not null'}, 'fld2': {'index': True}, 'fld3': {}},
            'secondTable': {'oFld1': {}, 'oFld2': {}, 'oFld3': {}},
            }

    def cursor(self):
        return self.mockCursor

@pytest.fixture()
def fixture_temp_db():
    basedir = join(tempfile.gettempdir(), u'ben_python_common_test', u'empty')
    ensureEmptyDirectory(basedir)
    db = StoreDemo()
    dbpath = join(basedir, 'test.db')
    db.connect_or_create(dbpath)
    yield db, dbpath

    # ensure that the db connection is closed after test.
    db.close()
    db = None
    ensureEmptyDirectory(basedir)
