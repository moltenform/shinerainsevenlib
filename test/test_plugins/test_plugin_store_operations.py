
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from src.shinerainsoftsevenutil.standard import *
from src.shinerainsoftsevenutil.core import assertException
from src.shinerainsoftsevenutil.plugins.plugin_store import SrssStoreBasic, SrssStoreException
from src.shinerainsoftsevenutil.files import join, getSize, writeAll, ensureEmptyDirectory
from test.test_core.common import fixture_dir

from test_plugin_store import fixture_temp_db, MockCursor, StoreDemo, StoreOperationsDemo


class TestStoreOperations:
    def test_addSchema(self):
        o = StoreOperationsDemo(autoConnect=False)
        cursor = MockCursor()
        o.addSchema(cursor)
        assert len(cursor.queries) == 3
        assert cursor.queries[0] == 'CREATE TABLE firstTable (fld1 not null, fld2 , fld3 )'
        assert cursor.queries[1] == 'CREATE  INDEX ix_firstTable_fld2 on firstTable(fld2)'
        assert cursor.queries[2] == 'CREATE TABLE secondTable (oFld1 , oFld2 , oFld3 )'

    def test_addUniqueIndex(self):
        class StoreOperationsDemoUnique(StoreOperationsDemo):
            def getFieldNamesAndAttributes(self):
                return {'firstTable': {'fld1': {'initprops': 'not null'}, 'fld2': {'index': 'unique'}, 'fld3': {}},
                    'secondTable': {'oFld1': {}, 'oFld2': {}, 'oFld3': {}}}
            
        o = StoreOperationsDemoUnique(autoConnect=False)
        cursor = MockCursor()
        o.addSchema(cursor)
        assert len(cursor.queries) == 3
        assert cursor.queries[0] == 'CREATE TABLE firstTable (fld1 not null, fld2 , fld3 )'
        assert cursor.queries[1] == 'CREATE UNIQUE INDEX ix_firstTable_fld2 on firstTable(fld2)'
        assert cursor.queries[2] == 'CREATE TABLE secondTable (oFld1 , oFld2 , oFld3 )'

    def test_insert(self):
        o = StoreOperationsDemo(autoConnect=False)
        o.insert({'fld1': 'val1', 'fld3': 'val3'})
        assert o.mockCursor.queries[0] == 'INSERT INTO firstTable (fld1, fld3) VALUES (?, ?)'
        assert o.mockCursor.queryParams[0] == ['val1', 'val3']

    def test_delete(self):
        o = StoreOperationsDemo(autoConnect=False)
        o.delete({'fld1': 'val1', 'fld3': 'val3'})
        assert o.mockCursor.queries[0] == 'DELETE FROM firstTable WHERE fld1 = ? AND fld3 = ?'
        assert o.mockCursor.queryParams[0] == ['val1', 'val3']

    def test_update(self):
        o = StoreOperationsDemo(autoConnect=False)
        o.update({'fld1': 'val1', 'fld3': 'val3'}, {'fld1': 'newVal1', 'fld3': 'newVal3'})
        assert o.mockCursor.queries[0] == 'UPDATE firstTable SET fld1 = ? , fld3 = ? WHERE fld1 = ? AND fld3 = ?'
        assert o.mockCursor.queryParams[0] == ['newVal1', 'newVal3', 'val1', 'val3']

    def test_update_two(self):
        o = StoreOperationsDemo(autoConnect=False)
        o.update({'fld2': 'f2'}, {'fld1': 'newVal1', 'fld3': 'newVal3'})
        assert o.mockCursor.queries[0] == 'UPDATE firstTable SET fld1 = ? , fld3 = ? WHERE fld2 = ?'
        assert o.mockCursor.queryParams[0] == ['newVal1', 'newVal3', 'f2']

    def test_query(self):
        o = StoreOperationsDemo(autoConnect=False)
        o.query({'fld1': 'val1', 'fld3': 'val3'})
        assert o.mockCursor.queries[0] == 'SELECT fld1, fld2, fld3 FROM firstTable WHERE fld1 = ? AND fld3 = ?'
        assert o.mockCursor.queryParams[0] == ['val1', 'val3']



