
import time

# "millistime" is number of milliseconds past epoch (unix time * 1000)
def renderMillisTime(millisTime):
    t = millisTime / 1000.0
    import time
    return time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(t))

def renderMillisTimeStandard(millisTime):
    t = millisTime / 1000.0
    import time
    return time.strftime("%Y-%m-%d %I:%M:%S", time.localtime(t))

def getNowAsMillisTime():
    import time
    t = time.time()
    return int(t * 1000)

class EnglishDateParserWrapper(object):
    def __init__(self, dateOrder='MDY'):
        # default to month-day-year
        # restrict to English, less possibility of accidentally parsing a non-date string
        import dateparser
        settings = {'STRICT_PARSING': True}
        if dateOrder:
            settings['DATE_ORDER'] = dateOrder
        self.p = dateparser.date.DateDataParser(languages=['en'], settings=settings)

    def parse(self, s):
        return self.p.get_date_data(s)['date_obj']

    def fromFullWithTimezone(self, s):
        # compensate for +0000
        # Wed Nov 07 04:01:10 +0000 2018
        pts = s.split(' ')
        newpts = []
        isTimeZone = ''
        for pt in pts:
            if pt.startswith('+'):
                assertEq('', isTimeZone)
                isTimeZone = ' ' + pt
            else:
                newpts.append(pt)
        return ' '.join(newpts) + isTimeZone

    def getDaysBefore(self, baseDate, n):
        import datetime
        assertTrue(isinstance(n, int))
        diff = datetime.timedelta(days=n)
        return baseDate - diff

    def getDaysBeforeInMilliseconds(self, sBaseDate, nDaysBefore):
        import datetime
        dObj = self.parse(sBaseDate)
        diff = datetime.timedelta(days=nDaysBefore)
        dBefore = dObj - diff
        return int(dBefore.timestamp() * 1000)

    def toUnixMilliseconds(self, s):
        assertTrue(isPy3OrNewer, 'requires python 3 or newer')
        dt = self.parse(s)
        return int(dt.timestamp() * 1000)
    
    