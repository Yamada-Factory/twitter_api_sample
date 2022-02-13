import urllib.parse

def encodeUrl(url):
    return urllib.parse.urlencode(url)

def quote(text,  safe=''):
    return urllib.parse.quote(text, safe=safe)
