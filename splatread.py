#!/usr/bin/env python3
#import sys, argparse, fileinput, bs4
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
        if n == 0:
            break
    while(len(s) < 3):
        s.append(ALPHABET[0])
    return ''.join(reversed(s))


def get_domain_abbr(fqdn):
    '''
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
    if fqdn == 'localhost':
        return 'localhst'

    domainbits = fqdn.split('.')
    if domainbits[0] == 'www':
        domainbits.pop(0)
    if len(''.join(domainbits)) < 7 or len(domainbits[-1]) > 3:
        domain = ''.join(domainbits)
    elif len(''.join(domainbits[-2:-1])) < 7:
        domain = ''.join(domainbits[-3:-1])
    elif domainbits[-1] == 'com':
        domain = domainbits[-2]
    else:
        domain = ''.join(domainbits[-2:-1])

    pt1 = domain[0]
    pt2 = ''.join([x for x in domain[1:-1] if x not in 'aeiou'])[0:3]
    pt3 = domain[-1]
    pt123 = pt1 + pt2 + pt3
    while(len(pt123) < 5):
        pt123 += '-'
    pt4 = sha1_3char_abbr(fqdn)
    pt123 + pt4
    return pt123 + pt4


def get_filename_from_mimemsg(mimemsg):
    tmpurl = mimemsg['href']

    fqdn = urllib.parse.urlparse(tmpurl).netloc
    scheme = urllib.parse.urlparse(tmpurl).scheme
    if scheme == 'http' or scheme == 'https':
        domainabbr = get_domain_abbr(fqdn)
    else:
        domainabbr = 'nodomain'

    tmpdate = mimemsg['time']
    ttup = dateutil.parser.parse(tmpdate).timetuple()
    datestr = time.strftime("%Y%m%d", ttup)
    timestr = get_base64_time(ttup)
    shortsum = '-' + mimemsg['hash'][0:7]
    retval = domainabbr + '-' + datestr + '-' + timestr + shortsum
    if not len(retval) == 29:
        print("retval: " + retval, file=sys.stderr)
        print("len: " + str(len(retval)), file=sys.stderr)
        raise ValueError("{} is {}/29 chars".format(retval, len(retval)))

    return retval


def get_base64_digit(x):
    # some code adapted from http://stackoverflow.com/questions/561486/
    ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
        string.digits + '-_'
    BASE = len(ALPHABET)
    r = x % BASE
    if x < 0 or x >= BASE:
        raise BaseException(
            str(x) + ' is out of range to represent as single base64 digit')
    return(ALPHABET[r])


def get_base64_time(ttup):
    return get_base64_digit(ttup.tm_hour) + \
        get_base64_digit(ttup.tm_min) + \
        get_base64_digit(ttup.tm_sec)


def parse_arguments():
    """ see http://docs.python.org/library/argparse """
    parser = argparse.ArgumentParser(
        description='Print prettified htmlfile to stdout')
    parser.add_argument("-n", "--nameonly", help="get the filename, not everything",
        action="store_true")
    parser.add_argument('htmlfile', help='raw html to clean up',
                        nargs='?', default=None)
    return parser.parse_args()


def main(argv=None):
    """ <http://www.crummy.com/software/BeautifulSoup/> prettify"""

    args = parse_arguments()
    if args.nameonly:
        with open(args.htmlfile, 'r') as f:
            splatstr = f.read()
        f.closed
        mimemsg = email.message_from_string(splatstr)
        print(get_filename_from_mimemsg(mimemsg))
        sys.exit()

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
