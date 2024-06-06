
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

# ruff: noqa

import pytest
import tempfile
from ..common_util import isPy3OrNewer
from ..store import Store, StoreWithCrudHelpers, StoreException
from ..files import join, getsize, writeall, ensureEmptyDirectory
from .test_store import StoreWithCrudHelpersDemo, fixture_temp_db

@pytest.mark.skipif('not isPy3OrNewer')
class TestCrudHelper(object):
    def test_opening_with_no_schema_version(self, fixture_temp_db):
        db, dbpath = fixture_temp_db
        db.cursor().execute('DELETE FROM ben_python_common_store_properties WHERE 1')
        db.close()
        with pytest.raises(StoreException) as exc:
            db.connect_or_create(dbpath)
        exc.match('DB is empty or comes from a different version. Expected schema version 1, got None')
        
def testGlobalImageInformationCache():
    print('Running testGlobalImageInformationCache')
    # should not allow null hashes
    def tryNullHash():
        dbpath = './test.db'
        files.deletesure(dbpath)
        with GlobalImageInformationCache(dbpath) as globalDb:
            globalDb.begin()
            globalDb.insert({'fileBytesHash': 'val1'})
            globalDb.end()
    assertException(tryNullHash, Exception, 'NOT NULL constraint failed')

    # should not allow dupe hashes
    def tryMakeDupe():
        dbpath = './test.db'
        files.deletesure(dbpath)
        with GlobalImageInformationCache(dbpath) as globalDb:
            globalDb.begin()
            globalDb.insert({'filePath': '/test/a', 'fileBytesHash': 'val1'})
            globalDb.insert({'filePath': '/test/b', 'fileBytesHash': 'val2'})
            globalDb.insert({'filePath': '/test/c', 'fileBytesHash': 'val1'})
            globalDb.end()
    assertException(tryMakeDupe, Exception, 'UNIQUE constraint failed')

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
        assertEq(None, got)
        got = globalDb.getByFileBytesHash('val1')
        assertEq('/test/a', got['filePath'])
        assertEq('val1', got['fileBytesHash'])
        assertEq(None, got['pixelsHash'])
        assertEq(None, got['averageHash'])
        got = globalDb.getByFileBytesHash('val2')
        assertEq('/test/b', got['filePath'])
        assertEq('val2', got['fileBytesHash'])
        assertEq('pixelsHashVal1', got['pixelsHash'])
        assertEq(None, got['averageHash'])
        got = globalDb.getByFileBytesHash('val3')
        assertEq('/test/c', got['filePath'])
        assertEq('val3', got['fileBytesHash'])
        assertEq(None, got['pixelsHash'])
        assertEq('averageHashVal1', got['averageHash'])
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
        assertEq('/test/a', got['filePath'])
        assertEq('val1', got['fileBytesHash'])
        assertEq(None, got['pixelsHash'])
        assertEq(None, got['averageHash'])
        got = globalDb.getByFileBytesHash('val2')
        assertEq('/test/b', got['filePath'])
        assertEq('val2', got['fileBytesHash'])
        assertEq('pixelsHashVal1', got['pixelsHash'])
        assertEq('averageHashValNew', got['averageHash'])
        got = globalDb.getByFileBytesHash('val3')
        assertEq('/test/c', got['filePath'])
        assertEq('val3', got['fileBytesHash'])
        assertEq(None, got['pixelsHash'])
        assertEq('averageHashValModified', got['averageHash'])
        globalDb.end()
        

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
        