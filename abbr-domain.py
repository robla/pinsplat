#!/usr/bin/env python3
# import sys, argparse, fileinput, bs4

import argparse
import hashlib
import string
import struct
import sys
import urllib.parse


def sha1_3char_abbr(x):
    '''
    1. Make SHA-1 of the input string (x)
    2. Take the first couple of bytes
    3. base64 encode those
    The result should be 3 characters long
    '''
    # unpack assuming big endian
    thishash = hashlib.sha1(x.encode('utf-8')).digest()
    n = struct.unpack('>H', thishash[0:2])[0]
    # some code adapted from http://stackoverflow.com/questions/561486/
    ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
        string.digits + '-_'
    BASE = len(ALPHABET)
    s = []
    while True:
        n, r = divmod(n, BASE)
        s.append(ALPHABET[r])
        if n == 0: break
    return ''.join(reversed(s))


def get_domain_abbr(fqdn):
    '''
    Make a unique-ish 8-letter domain abbreviation for a fully qualified domain name

    The full abbreviation is calculated:
    1 - first letter of the domain
    2-4 - next 3 consonants
    5 - last letter of the domain
    6-8 - base64 of the first couple of bytes of a SHA1

    The goal is to balance uniqueness with readability and memorability.  This is probably waaaaay overthought ;-)
    '''
    domain = fqdn.split('.')[-2]
    if(domain == 'com' or domain == 'ac' or domain == 'org' or domain == 'co'):
        domain = fqdn.split('.')[-3]
    pt1 = domain[0]
    pt2 = ''.join([x for x in domain[1:] if x not in 'aeiou'])[0:3]
    pt3 = domain[-1]
    pt4 = sha1_3char_abbr(fqdn)
    return pt1 + pt2 + pt3 + pt4


def parse_arguments():
    """ see http://docs.python.org/library/argparse """
    parser = argparse.ArgumentParser(
        description='get 8 char abbreviation from URL')
    parser.add_argument('url', help='url to pull domain from',
        nargs='?', default=None)
    return parser.parse_args()


def main(argv=None):
    """ get 8 char abbreviation from URL """

    args = parse_arguments()
    fqdn = urllib.parse.urlparse(args.url).netloc
    print((get_domain_abbr(fqdn)))


def test():
    urlstring = """http://www.eventbrite.com/e/virtual-worlds-in-the-new-year-tickets-90936995
    http://tinyurl.com/6gqfor
    http://tinyurl.com/yp2fwu
    http://westseattleblog.com/2009/05/house-fire-in-arbor-heights/
    http://www.theage.com.au/news/national/steaks-of-the-desert-a-feral-camel-solution/2005/09/12/1126377213156.html
    http://vigrxknowhow.com/2010/01/save-mysql.html
    http://www.gyford.com/phil/writing/2009/05/11/pretend_office.php
    https://pypi.python.org/pypi/jsonwidget/0.1.2
    http://www.everydayonething.com/
    http://blog.robla.net/2010/doing-the-conferency-talky-thing/"""
    urls = urlstring.split()
    for url in urls:
        fqdn = urllib.parse.urlparse(url).netloc
        print(fqdn)
        print((get_domain_abbr(fqdn)))
        print((hashlib.sha1(fqdn.encode('utf-8')).hexdigest()))
        print((sha1_3char_abbr(fqdn)))
        print((struct.unpack('>H', hashlib.sha1(fqdn.encode('utf-8')).digest()[0:2])))


if __name__ == '__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)
