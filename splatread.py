#!/usr/bin/env python3
#import sys, argparse, fileinput, bs4
import argparse, email, fileinput, sys

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


