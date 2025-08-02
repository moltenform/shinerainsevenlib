

class TestStrToListAndSet:
    def test_strToList(self):
        lst = strToList('''a\nbb\nc''')
        assert lst == ['a', 'bb', 'c']

        lst = strToList('''a\r\nbb\r\nc''')
        assert lst == ['a', 'bb', 'c']

        lst = strToList('''\r\na\r\n  bb  \r\nc\r\n''')
        assert lst == ['a', 'bb', 'c']

    def test_strToListWithComments(self):
        lst = strToList('''a\n#comment\nbb\nc''')
        assert lst == ['a', 'bb', 'c']

        lst = strToList('''a\r\n#comment\r\nbb\r\nc''')
        assert lst == ['a', 'bb', 'c']

        lst = strToList('''\r\n#comment\r\na\r\n  bb  \r\nc\r\n''')
        assert lst == ['a', 'bb', 'c']

    def test_strToSetWithComments(self):
        lst = strToSet('''a\n#comment\nbb\nc''')
        assert lst == set(['a', 'bb', 'c'])

        lst = strToSet('''a\r\n#comment\r\nbb\r\nc''')
        assert lst == set(['a', 'bb', 'c'])

        lst = strToSet('''\r\n#comment\r\na\r\n  bb  \r\nc\r\n''')
        assert lst == set(['a', 'bb', 'c'])

class TestEntryFromStrings:
    def testBasic(self):
        pass


class TestParseOrFallback:
    def testBasic(self):
        pass


class TestClampNumber:
    def testBasic(self):
        pass


class TestCompareAsSets:
    def testBasic(self):
        pass

class TestThrowIfDuplicates:
    def testBasic(self):
        pass

class TestMergeDict:
    def testBasic(self):
        pass


class TestMergePrintable:
    def testBasic(self):
        pass

