
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import pytest
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import assertException
from src.shinerainsevenlib.plugins.plugin_store import SrssStoreBasic, SrssStoreException
from src.shinerainsevenlib.files import join, getSize, writeAll, ensureEmptyDirectory
from test.test_core.common import fxDirPlain

from test_plugin_store import fixture_temp_db, MockCursor, StoreDemo, StoreOperationsDemo

class TestEndToEnd:
    def testEndToEnd(self):
        # should not allow null hashes
        with pytest.raises(Exception, match='.*NOT NULL constraint failed.*'):
            dbpath = './test.db'
            files.deleteSure(dbpath)
            with CityDatabase(dbpath) as db:
                db.txnBegin()
                db.insert({'cityName': 'val1'})
                db.txnCommit()

        # should not allow dupe hashes
        with pytest.raises(Exception, match='.*UNIQUE constraint failed.*'):
            dbpath = './test.db'
            files.deletesure(dbpath)
            with CityDatabase(dbpath) as db:
                db.txnBegin()
                db.insert({'cityID': '/test/a', 'cityName': 'val1'})
                db.insert({'cityID': '/test/b', 'cityName': 'val2'})
                db.insert({'cityID': '/test/c', 'cityName': 'val1'})
                db.txnCommit()

        # test inserts and gets
        dbpath = './test.db'
        files.deletesure(dbpath)
        with CityDatabase(dbpath) as db:
            db.txnBegin()
            db.insert({'cityID': '/test/a', 'cityName': 'val1'})
            db.insert({'cityID': '/test/b', 'cityName': 'val2', 'cityNickname': 'cityNicknameVal1'})
            db.insert({'cityID': '/test/c', 'cityName': 'val3', 'stateName': 'stateNameVal1'})
            db.txnCommit()

        with CityDatabase(dbpath) as db:
            db.txnBegin()
            got = db.searchByCityName('val0')
            assert got == None

            got = db.searchByCityName('val1')
            assert got['cityID'] == '/test/a'
            assert got['cityName'] == 'val1'
            assert got['cityNickname'] == None
            assert got['stateName'] == None

            got = db.searchByCityName('val2')
            assert got['cityID'] == '/test/b'
            assert got['cityName'] == 'val2'
            assert got['cityNickname'] == 'cityNicknameVal1'
            assert got['stateName'] == None

            got = db.searchByCityName('val3')
            assert got['cityID'] == '/test/c'
            assert got['cityName'] == 'val3'
            assert got['cityNickname'] == None
            assert got['stateName'] == 'stateNameVal1'
            db.txnCommit()

        # test updates
        with CityDatabase(dbpath) as db:
            db.txnBegin()
            db.update({'cityName': 'val2'}, {'stateName': 'stateNameValNew'})
            db.update({'cityName': 'val3'}, {'stateName': 'stateNameValModified'})
            db.txnCommit()
        
        with CityDatabase(dbpath) as db:
            db.txnBegin()
            got = db.searchByCityName('val1')
            assert got['cityID'] == '/test/a'
            assert got['cityName'] == 'val1'
            assert got['cityNickname'] == None
            assert got['stateName'] == None

            got = db.searchByCityName('val2')
            assert got['cityID'] == '/test/b'
            assert got['cityName'] == 'val2'
            assert got['cityNickname'] == 'cityNicknameVal1'
            assert got['stateName'] == 'stateNameValNew'

            got = db.searchByCityName('val3')
            assert got['cityID'] == '/test/c'
            assert got['cityName'] == 'val3'
            assert got['cityNickname'] == None
            assert got['stateName'] == 'stateNameValModified'
            db.txnCommit()




class TestNoSchema:
    def testOpeningWithNoSchemaVersion(self, fixture_temp_db):
        db, dbpath = fixture_temp_db
        db.cursor().execute('DELETE from shinerainsevenlib_store_properties WHERE 1')
        db.close()
        with pytest.raises(SrssStoreException) as exc:
            db.connectOrCreate(dbpath)
        exc.match('DB is empty or comes from a different version. Expected schema version 1, got None')

class CityDatabase(StoreOperationsDemo):
    def __init__(self, dbpath=None, flags=None, autoConnect=True):
        super().__init__(dbpath, flags, autoConnect)
    
    def getFieldNamesAndAttributes(self):
        schema = { 'CityDatabase': {
                'cityID': {'initprops': 'not null'},
                'cityName': {'initprops': 'not null', 'index': 'unique'},
                'cityNickname': {},
                'countyName': {},
                'stateName': {},
            }
        }

        return schema

    def searchByCityName(self, cityName):
        return self.query_one({'cityName': cityName})
    
    def updateByCityName(self, cityName, newData):
        res = self.update({'cityName': cityName}, newData)
        self.onInsertOrUpdateRow()
        return res
        