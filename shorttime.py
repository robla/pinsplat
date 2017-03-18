#!/usr/bin/env python3

import argparse
import sys

import dateutil.parser
import string


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
        description='get 3 byte time from timestr')
    parser.add_argument('timestr', help='url to pull domain from',
        nargs='?', default=None)
    return parser.parse_args()


def main(argv=None):
    """ get 3 char time abbreviation from datetime string (e.g. 
        2017-03-16T06:40:16Z => GoQ)"""

    args = parse_arguments()

    ttup = dateutil.parser.parse(args.timestr).timetuple()

    print(get_base64_time(ttup))



if __name__ == '__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)
