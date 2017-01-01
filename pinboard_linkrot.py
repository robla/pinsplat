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

def linkrot_summary_header(ignore_tags):
    msg = '#Pinboard linkrot results\n'
    if ignore_tags:
        msg += '\n**Ignored tags:** %s\n' % (', '.join(ignore_tags))
    return msg

def linkrot_summary_footer(num_bad_links, num_good_links):
    linkrot = int(num_bad_links/num_good_links*100)
    return '\n%s%% linkrot (%s/%s)\n' % (linkrot, num_bad_links, num_good_links)

def invalid_link_message(status, link):
    return '- Invalid link (%s): [%s](%s)  ' % (status, link['description'], link['href'])

def save_link(link):
    import os
    linkfilename = os.path.join('hash', link['hash'])
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

def process_links(links, ignore_tags):
    num_bad_links = 0
    num_links_processed = 0

    print linkrot_summary_header(ignore_tags)

    try:
        for link in links:
            if ignored_link(link, ignore_tags): 
                continue
            #status = get_link_status(link['href'])
            save_link(link)
            num_links_processed += 1
    except KeyboardInterrupt:
        print "\nProcessing cancelled..."
        pass
    
    print linkrot_summary_footer(num_bad_links, num_links_processed)
        
def process_bookmarks_file(filename, ignore_tags = []):
    with open(filename) as f:
        bookmarks = json.load(f)
        process_links(bookmarks, ignore_tags)
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: pinboard_linkrot.py <bookmarks.json> [space separated tags to ignore]'
        exit(1)
    process_bookmarks_file(sys.argv[1], sys.argv[2:])
