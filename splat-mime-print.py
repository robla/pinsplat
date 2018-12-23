#!/usr/bin/env python3
"""
Print pinsplat mime files in sane format.  Possibly a one-liner,
possibly as json
"""
import argparse
import email
import fileinput
import glob
import json
import os
import signal
import sys

from io import open


def get_mimemsg_from_mimefile(mimefile):
    with open(mimefile, 'r') as f:
        splatstr = f.read()
    f.closed
    return email.message_from_string(splatstr)


def get_json_from_mimemsg(mimemsg):
    splatdict = dict(mimemsg.items())
    splatdict['extended'] = mimemsg.get_payload()
    return json.dumps(splatdict, indent=4)


def get_oneliner_from_mimemsg(mimemsg):
    outdict = dict(mimemsg.items())
    desc = email.header.decode_header(outdict['description'])[0]
    # decode_header returns a list of tuples, often with 'utf-8' as the
    # second part of the tuple.  So if we get a tuple with something
    # other than "None", we'll pass that along to Python3's str to get
    # it converted to UTF-8
    if(desc[1]):
        outdict['description'] = str(*desc)
    else:
        outdict['description'] = desc[0]

    outdict['hash'] = outdict['hash'][0:7]
    outdict['href'] = outdict['href'].replace("https://", "")
    outdict['href'] = outdict['href'].replace("http://", "")
    outdict['href'] = outdict['href'].replace("www.", "")
    outdict['href'] = outdict['href'][0:25]
    outdict['time'] = outdict['time'][0:10]
    tags = mimemsg['tags'].split(' ')
    outdict['tags'] = ' '.join(['#' + tag for tag in tags])
    return "{hash} - {time} - {href} - {description} - {tags:20.20} ".format(**outdict)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Print pinsplat mime files in sane format')

    parser.add_argument(
        'mimefiles', help='pinsplat.mime file', nargs='*', default=None)
    parser.add_argument('--json', '-j',
                        help='print as json',
                        action="store_true")
    args = parser.parse_args()
    splatdir = os.environ.get('SPLATDIR')
    if(args.mimefiles):
        mimefiles = args.mimefiles
    else:
        mimefiles = filter(os.path.isfile, glob.glob(splatdir + "/*"))

    # Trap SIGPIPE so that annoying exceptions go away when piping to
    # "less"/"head"/"tail"/etc
    # per https://stackoverflow.com/a/11423337/314034
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    sortedfiles = sorted(
        mimefiles, key=lambda x: os.path.getmtime(x), reverse=True)
    for mimefile in sortedfiles:
        mimemsg = get_mimemsg_from_mimefile(mimefile)

        if(args.json):
            print(get_json_from_mimemsg(mimemsg))
        else:
            print(get_oneliner_from_mimemsg(mimemsg), flush=True)


if __name__ == u'__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)
