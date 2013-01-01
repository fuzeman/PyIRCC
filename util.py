import urllib
import urllib2
import urlparse
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


def http_get(baseUrl, headers, **kwargs):
    print baseUrl
    url = urlparse.urljoin(baseUrl, '?' + url_query_join(**kwargs))
    print url

    request = urllib2.Request(url=url, headers=headers)
    conn = urllib2.urlopen(request)
    data = conn.read()
    conn.close()

    return data


def url_query_join(**kwargs):
    args = []
    for k, v in kwargs.items():
        args.append('='.join((k, urllib.quote_plus(v))))
    return '&'.join(args)