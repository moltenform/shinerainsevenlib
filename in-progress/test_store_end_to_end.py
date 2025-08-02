# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

import pytest
import tempfile
from ..store import Store, StoreWithCrudHelpers, StoreException
from ..files import join, getSize, writeAll, ensureEmptyDirectory
from .test_store import StoreWithCrudHelpersDemo, fixture_temp_db

class TestCrudHelper:
    def test_opening_with_no_schema_version(self, fixture_temp_db):
        db, dbpath = fixture_temp_db
        db.cursor().execute('DELETE FROM shinerainsoftsevencommon_store_properties WHERE 1')
        db.close()
        with pytest.raises(StoreException) as exc:
            db.connectOrCreate(dbpath)
        
        exc.match('DB is empty or comes from a different version. Expected schema version 1, got None')
        
