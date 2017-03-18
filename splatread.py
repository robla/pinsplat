#!/usr/bin/env python3
#import sys, argparse, fileinput, bs4
import argparse, email, fileinput, sys

import dateutil.parser
import hashlib
import string
import struct
import time
import urllib


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


def get_filename_from_mimemsg(mimemsg):
    tmpurl = mimemsg['href']

    fqdn = urllib.parse.urlparse(tmpurl).netloc
    domainabbr = get_domain_abbr(fqdn)

    tmpdate = mimemsg['time']
    ttup = dateutil.parser.parse(tmpdate).timetuple()
    datestr = time.strftime("%Y%m%d", ttup)
    timestr = get_base64_time(ttup)

    return domainabbr + '-' + datestr + '-' + timestr


def get_base64_digit(x):
    # some code adapted from http://stackoverflow.com/questions/561486/
    ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
               string.digits + '-_'
    BASE = len(ALPHABET)
    r = x % BASE
    if x < 0 or x >= BASE:
        raise BaseException(str(x) + ' is out of range to represent as single base64 digit')
    return(ALPHABET[r])


def get_base64_time(ttup):
    return get_base64_digit(ttup.tm_hour) + \
            get_base64_digit(ttup.tm_min) + \
            get_base64_digit(ttup.tm_sec)


def parse_arguments():
    """ see http://docs.python.org/library/argparse """
    parser = argparse.ArgumentParser(
        description='Print prettified htmlfile to stdout')
    parser.add_argument('htmlfile', help='raw html to clean up', 
        nargs='?', default=None)
    return parser.parse_args()


def main(argv=None):
    """ <http://www.crummy.com/software/BeautifulSoup/> prettify"""

    args = parse_arguments()
    splatstr = "".join(fileinput.input())
    mimemsg = email.message_from_string(splatstr)

    tags = mimemsg['tags'].split(' ')
    print('Filename: ' + get_filename_from_mimemsg(mimemsg))
    print(' '.join(['@' + tag for tag in tags]))
    print()
    print(' '.join(['[[' + tag + ']]' for tag in tags]))
    print()
    print('[[' + mimemsg['href'] + '|' + mimemsg['description'] + ']]') 
    print(mimemsg['time'])
    print()
    print(mimemsg.get_payload())


if __name__ == '__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)


