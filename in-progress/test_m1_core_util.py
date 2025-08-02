

    
    

    

    @pytest.mark.skipif('not isPy3OrNewer')
    def test_modtimeRendered(self, fixture_dir):
        files.writeall(join(fixture_dir, 'a.txt'), 'contents')
        curtimeWritten = files.getModTimeNs(join(fixture_dir, 'a.txt'), asMillisTime=True)
        curtimeNow = getNowAsMillisTime()

        # we expect it to be at least within 1 day
        dayMilliseconds = 24 * 60 * 60 * 1000
        assert abs(curtimeWritten - curtimeNow) < dayMilliseconds

        # so we expect at least the date to match
        nCharsInDate = 10
        scurtimeWritten = renderMillisTime(curtimeWritten)
        scurtimeNow = renderMillisTime(curtimeNow)
        assert scurtimeWritten[0:nCharsInDate] == scurtimeNow[0:nCharsInDate]

    

    def test_checkOrderedDictEqualitySame(self):
        d1 = OrderedDict()
        d1['a'] = 1
        d1['b'] = 2
        d1same = OrderedDict()
        d1same['a'] = 1
        d1same['b'] = 2
        assert d1 == d1
        assert d1 == d1same
        assert d1same == d1

    def test_checkOrderedDictEqualityDifferentOrder(self):
        d1 = OrderedDict()
        d1['a'] = 1
        d1['b'] = 2
        d2 = OrderedDict()
        d2['b'] = 2
        d2['a'] = 1
        assert d1 != d2

    def test_checkOrderedDictEqualityDifferentValues(self):
        d1 = OrderedDict()
        d1['a'] = 1
        d1['b'] = 2
        d2 = OrderedDict()
        d2['a'] = 1
        d2['b'] = 3
        assert d1 != d2

def dateParserAvailable():
    "Checks if the dateparser module is available."
    try:
        import dateparser
        return True
    except ImportError:
        return False

if not dateParserAvailable:
    print("We will skip dateparsing tests because the module dateparser is not found.")



    
