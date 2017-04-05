#!/usr/bin/env python
#import sys, argparse, fileinput, bs4
from __future__ import with_statement
from __future__ import absolute_import
import argparse
import email
import fileinput
import sys

import dateutil.parser
import hashlib
import string
import struct
import time
import urllib
import urlparse 

from io import open


def sha1_3char_abbr(x):
    u'''
    1. Make SHA-1 of the input string (x)
    2. Take the first couple of bytes
    3. base64 encode those
    The result should be 3 characters long
    '''
    # unpack assuming big endian
    thishash = hashlib.sha1(x.encode(u'utf-8')).digest()
    n = struct.unpack(u'>H', thishash[0:2])[0]
    # some code adapted from http://stackoverflow.com/questions/561486/
    ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
        string.digits + u'-_'
    BASE = len(ALPHABET)
    s = []
    while True:
        n, r = divmod(n, BASE)
        s.append(ALPHABET[r])
        if n == 0:
            break
    while(len(s) < 3):
        s.append(ALPHABET[0])
    return u''.join(reversed(s))


def get_domain_abbr(fqdn):
    u'''
    Make a unique-ish 8-letter domain abbreviation for a fully qualified
    domain name

    The full abbreviation is calculated:
    1 - first letter of the domain
    2-4 - next 3 consonants (or less if there aren't that many)
    5 - last letter of the domain
    6-8 - base64 of the first couple of bytes of a SHA1

    The goal is to balance uniqueness with readability and memorability.
    This is probably waaaaay overthought ;-)
    '''
    if fqdn == u'localhost':
        return u'localhst'

    domainbits = fqdn.split(u'.')
    if domainbits[0] == u'www':
        domainbits.pop(0)
    if len(u''.join(domainbits)) < 7 or len(domainbits[-1]) > 3:
        domain = u''.join(domainbits)
    elif len(u''.join(domainbits[-2:-1])) < 7:
        domain = u''.join(domainbits[-3:-1])
    elif domainbits[-1] == u'com':
        domain = domainbits[-2]
    else:
        domain = u''.join(domainbits[-2:-1])

    pt1 = domain[0]
    pt2 = u''.join([x for x in domain[1:-1] if x not in u'aeiou'])[0:3]
    pt3 = domain[-1]
    pt123 = pt1 + pt2 + pt3
    while(len(pt123) < 5):
        pt123 += u'-'
    pt4 = sha1_3char_abbr(fqdn)
    pt123 + pt4
    return pt123 + pt4


def get_filename_from_mimemsg(mimemsg):
    tmpurl = mimemsg[u'href']

    fqdn = urlparse.urlparse(tmpurl).netloc
    scheme = urlparse.urlparse(tmpurl).scheme
    if scheme == u'http' or scheme == u'https':
        domainabbr = get_domain_abbr(fqdn)
    else:
        domainabbr = u'nodomain'

    tmpdate = mimemsg[u'time']
    ttup = dateutil.parser.parse(tmpdate).timetuple()
    datestr = time.strftime(u"%Y%m%d", ttup)
    timestr = get_base64_time(ttup)
    shortsum = u'-' + mimemsg[u'hash'][0:7]
    retval = domainabbr + u'-' + datestr + u'-' + timestr + shortsum
    if not len(retval) == 29:
        print >>sys.stderr, u"retval: " + retval
        print >>sys.stderr, u"len: " + unicode(len(retval))
        raise ValueError(u"{} is {}/29 chars".format(retval, len(retval)))

    return retval


def get_base64_digit(x):
    # some code adapted from http://stackoverflow.com/questions/561486/
    ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
        string.digits + u'-_'
    BASE = len(ALPHABET)
    r = x % BASE
    if x < 0 or x >= BASE:
        raise BaseException(
            unicode(x) + u' is out of range to represent as single base64 digit')
    return(ALPHABET[r])


def get_base64_time(ttup):
    return get_base64_digit(ttup.tm_hour) + \
        get_base64_digit(ttup.tm_min) + \
        get_base64_digit(ttup.tm_sec)


def parse_arguments():
    u""" see http://docs.python.org/library/argparse """
    parser = argparse.ArgumentParser(
        description=u'Print prettified htmlfile to stdout')
    parser.add_argument(u"-n", u"--nameonly", help=u"get the filename, not everything",
        action=u"store_true")
    parser.add_argument(u'htmlfile', help=u'raw html to clean up',
                        nargs=u'?', default=None)
    return parser.parse_args()


def main(argv=None):
    u""" <http://www.crummy.com/software/BeautifulSoup/> prettify"""

    args = parse_arguments()
    if args.nameonly:
        with open(args.htmlfile, u'r') as f:
            splatstr = f.read()
        f.closed
        mimemsg = email.message_from_string(splatstr)
        print get_filename_from_mimemsg(mimemsg)
        sys.exit()

    splatstr = u"".join(fileinput.input())
    mimemsg = email.message_from_string(splatstr)

    tags = mimemsg[u'tags'].split(u' ')
    print u'Filename: ' + get_filename_from_mimemsg(mimemsg)
    print u' '.join([u'@' + tag for tag in tags])
    print
    print u' '.join([u'[[' + tag + u']]' for tag in tags])
    print
    print u'[[' + mimemsg[u'href'] + u'|' + mimemsg[u'description'] + u']]'
    print mimemsg[u'time']
    print
    print mimemsg.get_payload()


if __name__ == u'__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)
