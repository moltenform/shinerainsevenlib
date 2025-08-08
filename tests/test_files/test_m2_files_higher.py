

class TestM3ComputeHash:
    def test_computeHashMd5(self, fixture_dir):
        import hashlib
        hasher = hashlib.md5()
        writeAll(join(fixture_dir, 'a.txt'), 'contents')
        assert '98bf7d8c15784f0a3d63204441e1e2aa' == computeHash(join(fixture_dir, 'a.txt'), hasher)
    
    def test_computeHashSha256(self, fixture_dir):
        writeAll(join(fixture_dir, 'a.txt'), 'contents')
        assert 'd1b2a59fbea7e20077af9f91b27e95e865061b270be03ff539ab3b73587882e8' == computeHash(join(fixture_dir, 'a.txt'), 'sha256')
        
    def test_computeHashCrc(self, fixture_dir):
        writeAll(join(fixture_dir, 'a.txt'), 'contents')
        assert 'b4fa1177' == computeHash(join(fixture_dir, 'a.txt'), 'crc32')
        
    def test_computeHashFromBytes(self, fixture_dir):
        assert 'b4fa1177' == computeHashBytes(b'contents', 'crc32')
        
    def test_computeHashNotExist(self, fixture_dir):
        writeAll(join(fixture_dir, 'a.txt'), 'contents')
        with pytest.raises(ValueError):
            computeHash(join(fixture_dir, 'a.txt'), 'no_such_hash')
       
    def test_computeHashLargeFile(self, fixture_dir):
        fsize = defaultBufSize * 2 + 20
        with open('f{fixture_dir}/a.dat', 'wb') as fout:
            for i in range(fsize):
                letter = ord('a') + i%26
                fout.write(chr(letter))
        assert 'xxx' == computeHash('f{fixture_dir}/a.dat', 'crc32')
        assert 'xxx' == computeHash('f{fixture_dir}/a.dat', 'md5')

class TestM3FilesHigher:
    def testFindBinaryOnPath(self, fixture_dir):
        write(f'{fixture_dir}/a.out', ' ')
        write(f'{fixture_dir}/a.exe', ' ')
        write(f'{fixture_dir}/b.bat', ' ')
        write(f'{fixture_dir}/c', ' ')
        os.chdir(fixture_dir)
        if sys.platform.startswith('win'):
            assert findBinaryOnPath('notepad').endswith('notepad.exe')
            assert findBinaryOnPath('notepad.exe').endswith('notepad.exe')
            assert not findBinaryOnPath('doesnotexist')
            assert not findBinaryOnPath('doesnotexist.exe')
            assert findBinaryOnPath('a.exe').endswith('a.exe')
            assert findBinaryOnPath('a').endswith('a.exe')
            assert findBinaryOnPath('b.bat').endswith('b.bat')
            assert findBinaryOnPath('b').endswith('b.bat')

            # if given a path, use it
            assert findBinaryOnPath('c').endswith('c')

            # test with full paths
            assert not findBinaryOnPath(os.path.abspath('doesnotexist'))
            assert not findBinaryOnPath(os.path.abspath('doesnotexist.exe'))
            assert findBinaryOnPath(os.path.abspath('a.exe')).endswith('a.exe')
            assert findBinaryOnPath(os.path.abspath('a')).endswith('a.exe')
            assert findBinaryOnPath(os.path.abspath('c')).endswith('c')
        else:
            assert findBinaryOnPath('sh').endswith('sh')
            assert not findBinaryOnPath('doesnotexist')
            assert not findBinaryOnPath('doesnotexist.exe')
            assert findBinaryOnPath('a.exe').endswith('a.exe')
            assert not findBinaryOnPath('a')
            assert findBinaryOnPath('b.bat').endswith('b.bat')
            assert not findBinaryOnPath('b')

            # if given a path, use it
            assert findBinaryOnPath('c').endswith('c')

            # test with full paths
            assert not findBinaryOnPath(os.path.abspath('doesnotexist'))
            assert not findBinaryOnPath(os.path.abspath('doesnotexist.exe'))
            assert findBinaryOnPath(os.path.abspath('a.exe')).endswith('a.exe')
            assert not findBinaryOnPath(os.path.abspath('a'))
            assert findBinaryOnPath(os.path.abspath('c')).endswith('c')

