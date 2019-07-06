#!/usr/bin/env python

from __future__ import division
import argparse
import calendar
import codecs
import copy
import dateutil.parser
import email
import json
import locale
import os
import requests
import sys
import time
import splatread

# use preferred encoding, even when piping output to another program or file
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


def get_link_status(url):
    return url


def valid_link(status):
    return (status == requests.codes.ok)


def ignored_link(link, ignore_tags):
    ignore_tags = set(ignore_tags)
    link_tags = link['tags'].split(' ')
    return True if ignore_tags.intersection(link_tags) else False


def invalid_link_message(status, link):
    return '- Invalid link (%s): [%s](%s)  ' % (status, link['description'], link['href'])


def save_link_json(link):
    import os
    linkfilename = os.path.join('hash', 'json', link['hash'] + ".json")
    retval = json.dumps(link, indent=4)
    with open(linkfilename, 'wt') as f:
        f.write(retval)
    linkdate = dateutil.parser.parse(link['time'])
    linktimetuple = time.mktime(linkdate.timetuple())
    os.utime(linkfilename, (linktimetuple, linktimetuple))
    # FIXMEOUT(linkdate)
    return retval
    # return '- [%s](%s)  ' % (link['description'], link['href'])


def fix_date_on_file(linkfilename, linktimestring):
    linkdate = dateutil.parser.parse(linktimestring)
    linktime_local = calendar.timegm(linkdate.timetuple())
    os.utime(linkfilename, (time.time(), linktime_local))
    return linkdate


def save_link_mime(link):
    mimemsg = email.message_from_string("")

    headers = copy.copy(link)
    body = headers.pop(u'extended')

    for hname, hval in headers.iteritems():
        mimemsg[hname] = hval

    mimemsg.set_payload(body.encode('utf-8'))

    linkdate = dateutil.parser.parse(link['time'])
    linkdatestr = time.strftime("%Y-%m-%d", linkdate.timetuple())
    #filename = os.path.join('hash', 'mimetmp', linkdatestr +
    #                        "-" + link['hash'][:7] + ".mime")
    splatpart = splatread.get_filename_from_mimemsg(mimemsg)
    filename = os.path.join('hash', 'mime', splatpart + ".mime")

    with open(filename, 'wt') as f:
        f.write(mimemsg.as_string())

    linkdate = fix_date_on_file(filename, link['time'])
    return True


def process_links(links, ignore_tags):
    num_bad_links = 0
    num_links_processed = 0

    try:
        for link in links:
            save_link_json(link)
            save_link_mime(link)
            num_links_processed += 1
    except KeyboardInterrupt:
        print "\nProcessing cancelled..."
        pass


def process_bookmarks_file(filename, ignore_tags=[]):
    with open(filename) as f:
        bookmarks = json.load(f)
        process_links(bookmarks, ignore_tags)


def parse_arguments():
    """ see http://docs.python.org/library/argparse """
    parser = argparse.ArgumentParser(
        description='Splatter bookmarks file into little bitty ones')
    parser.add_argument('bmkjson', help='bookmarks.json file', 
        nargs='?', default=None)
    return parser.parse_args()


def main(argv=None):
    """Splatter bookmarks file into little bitty ones"""

    args = parse_arguments()

    process_bookmarks_file(args.bmkjson)


if __name__ == '__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)
