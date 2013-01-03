import urllib
import urllib2
import urlparse
import xml.etree.ElementTree as et

__author__ = 'Dean Gardiner'


def get_xml(url):
    conn = urllib2.urlopen(url)
    data = conn.read()
    conn.close()

    try:
        return et.fromstring(data)
    except et.ParseError:
        print "get_xml", "parse error"
        return None


def http_get(baseUrl, headers, **kwargs):
    url = urlparse.urljoin(baseUrl, '?' + url_query_join(**kwargs))

    request = urllib2.Request(url=url, headers=headers)
    conn = urllib2.urlopen(request)
    data = conn.read()
    conn.close()

    return data

def http_post(url, headers, post_data):
    request = urllib2.Request(url=url, data=post_data, headers=headers)
    conn = urllib2.urlopen(request)
    data = conn.read()
    conn.close()

    return data

def url_query_join(**kwargs):
    args = []
    for k, v in kwargs.items():
        args.append('='.join((k, urllib.quote_plus(v))))
    return '&'.join(args)


def class_string(class_name, newLines=True, **kwargs):
    output = []
    for k, v in kwargs.items():
        if isinstance(v, str):
            output.append('\t' + str(k) + ': "' + v + '"')
        else:
            output.append('\t' + str(k) + ': ' + str(v))

    if newLines:
        return '<' + class_name + '\n' + '\n'.join(output) + '\n>'
    else:
        return '<' + class_name + ' ' + ','.join(output) + ' >'

def class_string_instance(instance, names, newLines=True):
    class_name = instance.__class__.__name__
    kwargs = {}

    for name in names:
        if hasattr(instance, name):
            kwargs[name] = getattr(instance, name)

    return class_string(class_name, newLines=newLines, **kwargs)