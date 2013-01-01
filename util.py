import urllib
import xml.etree.ElementTree as et

__author__ = 'Dean Gardiner'


def get_xml(url):
    conn = urllib.urlopen(url)
    data = conn.read()
    conn.close()

    try:
        return et.fromstring(data)
    except et.ParseError:
        print "get_xml", "parse error"
        return None