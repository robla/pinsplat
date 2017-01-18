#!/usr/bin/env python

from __future__ import division
import requests
import json
import sys
import codecs
import locale

def FIXMEOUT(string):
    print(string)

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

def splatter_summary_header():
    msg = '#Pinboard splatter results\n'
    return msg

def splatter_summary_footer(num_links):
    return '\n%s Saved\n' % (num_links)

def invalid_link_message(status, link):
    return '- Invalid link (%s): [%s](%s)  ' % (status, link['description'], link['href'])

def save_link_json(link):
    import os
    linkfilename = os.path.join('hash', 'json', link['hash'] + ".json")
    retval = json.dumps(link, indent=4)
    with open(linkfilename, 'wt') as f:
        f.write(retval)
    import dateutil.parser
    linkdate = dateutil.parser.parse(link['time'])
    import time
    linktimetuple = time.mktime(linkdate.timetuple())
    os.utime(linkfilename, (linktimetuple, linktimetuple))
    #FIXMEOUT(linkdate)
    return retval
    #return '- [%s](%s)  ' % (link['description'], link['href'])
    
def fix_date_on_file(linkfilename, linktimestring):
    import dateutil.parser
    import time, os
    linkdate = dateutil.parser.parse(linktimestring)
    linktimetuple = time.mktime(linkdate.timetuple())
    os.utime(linkfilename, (linktimetuple, linktimetuple))
    return linkdate

def save_link_mime(link):
    import os, copy

    import email, sys, json
    mimemsg = email.message_from_string("")

    headers = copy.copy(link)
    body = headers.pop(u'extended')

    for hname, hval in headers.iteritems():
        mimemsg[hname] = hval

    mimemsg.set_payload(body.encode('utf-8'))

    filename = os.path.join('hash', 'mime', link['hash'] + ".mime")
    with open(filename, 'wt') as f:
        f.write(mimemsg.as_string())

    linkdate = fix_date_on_file(filename, link['time'])
    return True


def process_links(links, ignore_tags):
    num_bad_links = 0
    num_links_processed = 0

    print splatter_summary_header()

    try:
        for link in links:
            save_link_json(link)
            save_link_mime(link)
            num_links_processed += 1
    except KeyboardInterrupt:
        print "\nProcessing cancelled..."
        pass
    
    print splatter_summary_footer(num_links_processed)
        
def process_bookmarks_file(filename, ignore_tags = []):
    with open(filename) as f:
        bookmarks = json.load(f)
        process_links(bookmarks, ignore_tags)
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: pinboard-splatter.py <bookmarks.json>'
        print '  See zkw splatter for more'
        exit(1)
    process_bookmarks_file(sys.argv[1], sys.argv[2:])
