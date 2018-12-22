#!/usr/bin/env python3
"""
Print pinsplat mime files in sane format.  Possibly a one-liner,
possibly as json
"""
import argparse
import email
import fileinput
import sys

from io import open


def get_mimemsg_from_mimefile(mimefile):
    with open(mimefile, 'r') as f:
        splatstr = f.read()
    f.closed
    return email.message_from_string(splatstr)


def get_json_from_mimemsg(mimemsg):
    import json
    splatdict = dict(mimemsg.items())
    splatdict['extended'] = mimemsg.get_payload()
    return json.dumps(splatdict, indent=4)


def get_oneliner_from_mimemsg(mimemsg):
    outdict=dict(mimemsg.items())
    outdict['hash']=outdict['hash'][0:7]
    outdict['href']=outdict['href'][8:25]
    outdict['time']=outdict['time'][0:10]
    tags=mimemsg['tags'].split(' ')
    outdict['tags']=' '.join(['#' + tag for tag in tags])
    return "{hash} - {time} - {href} - {description} - {tags:20.20} ".format(**outdict)


def main(argv = None):
    parser=argparse.ArgumentParser(
        description = 'Print pinsplat mime files in sane format')

    parser.add_argument('mimefile', help = 'pinsplat.mime file')
    parser.add_argument('--json', '-j',
                        help = 'print as json',
                        action = "store_true")
    args=parser.parse_args()

    mimemsg=get_mimemsg_from_mimefile(args.mimefile)

    if(args.json):
        print(get_json_from_mimemsg(mimemsg))
    else:
        print(get_oneliner_from_mimemsg(mimemsg))


if __name__ == u'__main__':
    exit_status=main(sys.argv)
    sys.exit(exit_status)
