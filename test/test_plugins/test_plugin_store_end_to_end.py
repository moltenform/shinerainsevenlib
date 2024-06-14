
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from src.shinerainsoftsevenutil.standard import *
from src.shinerainsoftsevenutil.core import assertException
from src.shinerainsoftsevenutil.plugins.plugin_store import SrssStoreBasic, SrssStoreException
from src.shinerainsoftsevenutil.files import join, getSize, writeAll, ensureEmptyDirectory
from test.test_core.common import fixture_dir

from test_plugin_store import fixture_temp_db, MockCursor, StoreDemo

class TestEndToEnd:
    def testEndToEnd(self):
        # should not allow null hashes
    with pytest.raises(Exception, 'NOT NULL constraint failed'):
            dbpath = './test.db'
        files.deletesure(dbpath)
        with GlobalImageInformationCache(dbpath) as globalDb:
            globalDb.begin()
            globalDb.insert({'fileBytesHash': 'val1'})
            globalDb.end()
            getWithDifferentExt('./file_no_ext', '.new')

    # should not allow dupe hashes
    with pytest.raises(Exception, 'UNIQUE constraint failed'):
        dbpath = './test.db'
        files.deletesure(dbpath)
        with GlobalImageInformationCache(dbpath) as globalDb:
            globalDb.begin()
            globalDb.insert({'filePath': '/test/a', 'fileBytesHash': 'val1'})
            globalDb.insert({'filePath': '/test/b', 'fileBytesHash': 'val2'})
            globalDb.insert({'filePath': '/test/c', 'fileBytesHash': 'val1'})
            globalDb.end()

    # test inserts and gets
    dbpath = './test.db'
    files.deletesure(dbpath)
    with GlobalImageInformationCache(dbpath) as globalDb:
        globalDb.begin()
        globalDb.insert({'filePath': '/test/a', 'fileBytesHash': 'val1'})
        globalDb.insert({'filePath': '/test/b', 'fileBytesHash': 'val2', 'pixelsHash': 'pixelsHashVal1'})
        globalDb.insert({'filePath': '/test/c', 'fileBytesHash': 'val3', 'averageHash': 'averageHashVal1'})
        globalDb.end()

    with GlobalImageInformationCache(dbpath) as globalDb:
        globalDb.begin()
        got = globalDb.getByFileBytesHash('val0')
        assert got == None
        got = globalDb.getByFileBytesHash('val1')
        assert got['filePath'] == '/test/a'
        assert got['fileBytesHash'] == 'val1'
        assert got['pixelsHash'] == None
        assert got['averageHash'] == None
        got = globalDb.getByFileBytesHash('val2')
        assert got['filePath'] == '/test/b'
        assert got['fileBytesHash'] == 'val2'
        assert got['pixelsHash'] == 'pixelsHashVal1'
        assert got['averageHash'] == None
        got = globalDb.getByFileBytesHash('val3')
        assert got['filePath'] == '/test/c'
        assert got['fileBytesHash'] == 'val3'
        assert got['pixelsHash'] == None
        assert got['averageHash'] == 'averageHashVal1'
        globalDb.end()

    # test updates
    with GlobalImageInformationCache(dbpath) as globalDb:
        globalDb.begin()
        globalDb.update({'fileBytesHash': 'val2'}, {'averageHash': 'averageHashValNew'})
        globalDb.update({'fileBytesHash': 'val3'}, {'averageHash': 'averageHashValModified'})
        globalDb.end()
    
    with GlobalImageInformationCache(dbpath) as globalDb:
        globalDb.begin()
        got = globalDb.getByFileBytesHash('val1')
        assert got['filePath'] == '/test/a'
        assert got['fileBytesHash'] == 'val1'
        assert got['pixelsHash'] == None
        assert got['averageHash'] == None
        got = globalDb.getByFileBytesHash('val2')
        assert got['filePath'] == '/test/b'
        assert got['fileBytesHash'] == 'val2'
        assert got['pixelsHash'] == 'pixelsHashVal1'
        assert got['averageHash'] == 'averageHashValNew'
        got = globalDb.getByFileBytesHash('val3')
        assert got['filePath'] == '/test/c'
        assert got['fileBytesHash'] == 'val3'
        assert got['pixelsHash'] == None
        assert got['averageHash'] == 'averageHashValModified'
        globalDb.end()




class TestCrudHelper:
    def test_opening_with_no_schema_version(self, fixture_temp_db):
        db, dbpath = fixture_temp_db
        db.cursor().execute('DELETE FROM ben_python_common_store_properties WHERE 1')
        db.close()
        with pytest.raises(StoreException) as exc:
            db.connect_or_create(dbpath)
        exc.match('DB is empty or comes from a different version. Expected schema version 1, got None')

class GlobalImageInformationCache(StoreWithCrudHelpersDemo):
    def get_field_names_and_attributes(self):
        schema = { 'GlobalImageInformationCache': {
                'filePath': {'initprops': 'not null'},
                'fileBytesHash': {'initprops': 'not null', 'index': 'unique'},
                'pixelsHash': {},
                'perceptualHash': {},
                'averageHash': {},
            }
        }

        return schema

    def getByFileBytesHash(self, fileBytesHash):
        return self.query_one({'fileBytesHash': fileBytesHash})
    
    def updateByFileBytesHash(self, fileBytesHash, newData):
        res = self.update({'fileBytesHash': fileBytesHash}, newData)
        self.onInsertOrUpdateRow()
        return res
        