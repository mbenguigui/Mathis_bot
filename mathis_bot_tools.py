import pywikibot
import pytz


def can_run(site):
    page = pywikibot.Page(site, u'Discussion utilisateur:Mathis bot')
    return not page.text


def timestamp_to_date(timestamp):
    month = (u'janvier', u'février', u'mars', u'avril', u'mai', u'juin', u'juillet', u'août', u'septembre',
             u'octobre', u'novembre', u'décembre')
    return u'{} {} {} à {}:{:0>2}'.format(timestamp.day,
                                          month[timestamp.month-1],
                                          timestamp.year,
                                          timestamp.hour,
                                          timestamp.minute)


def utc_to_paris(timestamp):
    return pytz.timezone('UTC').localize(timestamp).astimezone(pytz.timezone('Europe/Paris'))
