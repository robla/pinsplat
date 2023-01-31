#!/usr/bin/env python

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


def invalid_link_message(status, link):
    return '- Invalid link (%s): [%s](%s)  ' % (status, link['description'], link['href'])


def fix_date_on_file(linkfilename, linktimestring):
    linkdate = dateutil.parser.parse(linktimestring)
    linktime_local = calendar.timegm(linkdate.timetuple())
    os.utime(linkfilename, (time.time(), linktime_local))
    return linkdate


# 3.   Third function called
def process_links_save_mime(links, mimedir_string):
    for link in links:
        # save_link_mime(link, mimedir_string)
        mimemsg = email.message_from_string("")

        headers = copy.copy(link)
        body = headers.pop('extended')

        for hname, hval in headers.items():
            mimemsg[hname] = hval

        mimemsg.set_payload(body.encode('utf-8'))

        linkdate = dateutil.parser.parse(link['time'])
        linkdatestr = time.strftime("%Y-%m-%d", linkdate.timetuple())
        #filename = os.path.join(mimedir_string, linkdatestr +
        #                        "-" + link['hash'][:7] + ".mime")
        splatpart = splatread.get_filename_from_mimemsg(mimemsg)
        filename = os.path.join(mimedir_string, splatpart + ".mime")

        mime_filehandle = open(filename, 'wt')

        with mime_filehandle as f:
            try:
                 f.write(mimemsg.as_string())
            except:
                 raise Exception("Line 85: inscrutable error")

        linkdate = fix_date_on_file(filename, link['time'])
        return True


# 2.   Second function called
def process_links_save_json(bookmarks, jsondir_string):
    for link in bookmarks:
        #FIXME-- save_link_json(link, jsondir_string)
        linkfilename = os.path.join(jsondir_string, link['hash'] + ".json")
        jsonoutputstring = json.dumps(link, indent=4)
        linkhandle = open(linkfilename, 'wt')
        linkhandle.write(jsonoutputstring)
        linkdate = dateutil.parser.parse(link['time'])
        linktimetuple = time.mktime(linkdate.timetuple())
        os.utime(linkfilename, (linktimetuple, linktimetuple))

    # FIXMEOUT(linkdate)
    # return retval
    # return '- [%s](%s)  ' % (link['description'], link['href'])



##########################
#  1.  First function called
#

def process_bookmarks_file(input_filename):
    """Process a JSON-based bookmark file downloaded from pinboard.in"""
    mimedir_string="mime-pinboardmarks"
    jsondir_string="json-pinboardmarks"
    
    try:
        os.makedirs(jsondir_string)
    except FileExistsError:
        pass

    try:
        os.makedirs(mimedir_string)
    except FileExistsError:
        pass
   
    bookmarks = json.load(open(input_filename))
    #FFFFFFFFFIXMEAUGUST20in2022FFFFFFFFFFFFFFFFFFFFFFFFFFFFF - headers = copy.copy(link)
 
    process_links_save_json(bookmarks, jsondir_string)
    process_links_save_mime(bookmarks, mimedir_string)


def main(argv=None):
    """Splatter bookmarks file into little bitty ones"""
    # see http://docs.python.org/library/argparse """
    parser = argparse.ArgumentParser(
        description='Splatter bookmarks file into little bitty ones')
    parser.add_argument('bmkjson', help='bookmarks.json file', 
        nargs='?', default=None)
    args = parser.parse_args()

    process_bookmarks_file(args.bmkjson)


if __name__ == '__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)
