
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from src.shinerainsevenlib.standard import *
from tests.test_core.common import fixture_dir
from src.shinerainsevenlib.core import assertException

class TestTemporary:
    def testSrssFileIteratorDirectoryFilter(self):
        for SEP in ('/', '\\'):
            assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', ''))
            assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', 'abcd'))
            assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'ab{SEP}cd'))

            assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node{SEP}_modules{SEP}b'))
            assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}notnode_modules{SEP}b'))
            assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}notnode_modules{SEP}'))
            assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}notnode_modules'))
            assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modulesnot{SEP}b'))
            assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modulesnot{SEP}'))
            assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modulesnot'))
            assert (srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modules{SEP}b'))
            assert (srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modules{SEP}'))
            assert (srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modules'))
    
    def testCleanupTempFilesOnException(self, fixture_dir):
        files.writeAll(f'{fixture_dir}/a.txt', 'aaa')
        files.writeAll(f'{fixture_dir}/b.txt', 'bbb')
        files.writeAll(f'{fixture_dir}/c.txt', 'ccc')
        with srss.CleanupTempFilesOnException() as cleanup:
            # clean up a newly created file
            files.writeAll(f'{fixture_dir}/new.txt', 'new')
            cleanup.registerTempFile(f'{fixture_dir}/new.txt')
            assertTrue(files.exists(f'{fixture_dir}/new.txt'))

            # clean up a previously made file
            cleanup.registerTempFile(f'{fixture_dir}/a.txt')
            assertTrue(files.exists(f'{fixture_dir}/a.txt'))

            # should silently skip non-existant files
            cleanup.registerTempFile(f'{fixture_dir}/not-exist.txt')
            assertTrue(not files.exists(f'{fixture_dir}/not-exist.txt'))
        
        # check they were deleted
        assertTrue(not files.exists(f'{fixture_dir}/new.txt'))
        assertTrue(not files.exists(f'{fixture_dir}/a.txt'))
        assertTrue(not files.exists(f'{fixture_dir}/not-exist.txt'))

        # should also cleanup if exceptions occur
        def fn():
            with srss.CleanupTempFilesOnException() as cleanup:
                cleanup.registerTempFile(f'{fixture_dir}/b.txt')
                raise RuntimeError("cause exception")

        # should delete b but leave behind the other file(s)
        assertException(fn, RuntimeError, "cause exception")
        assertTrue(not files.exists(f'{fixture_dir}/b.txt'))
        assertTrue(files.exists(f'{fixture_dir}/c.txt'))

