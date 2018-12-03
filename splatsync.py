#!/usr/bin/env python3

import argparse
import configparser
import git
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

from base10x60timestamp.b1060time import get_b1060_timestamp_from_epoch


def parse_arguments():
    """ see http://docs.python.org/library/argparse """
    parser = argparse.ArgumentParser(
        description='Sync Pinboard with local data')
    parser.add_argument('dest', help='optional download destination', 
        nargs='*', default=None)
    parser.add_argument('--nocommit', help='no commits to git repos',
        action="store_true")
    parser.add_argument('--nofetch', help='no retrieving export from pinboard.in',
        action="store_true")

    return parser.parse_args()


def load_config_file():
    configfile = os.path.expanduser("~/.pinboardrc")

    config = configparser.RawConfigParser()
    with open(configfile, "r") as f:
        config.read_file(f)
    return config


def get_pinboard_apitoken(config):
    api_token = config.get("authentication", "api_token")

    return api_token


# TODO - turn pinboard_splatter into library that I can import easily
# TODO - port (back) to python3
def run_pinboard_splatter(exportfile, message, commitflag):
    config = load_config_file()

    # splatter data
    splatter_data = config.get("splatter", "data_dir")

    #xxx cd ~/pinboard/pinboard-splatter/data
    os.chdir(splatter_data)
    if(True):
        out_bytes = subprocess.check_output(['pinsplat', exportfile])

    if commitflag:
        repo = git.Repo('.')
        regexp = re.compile(r'(hash/json/|hash/mime/)')
        addthese = [x for x in repo.untracked_files if regexp.match(x)]
        modded = [x.a_path for x in repo.index.diff(None).iter_change_type('M')]

        if (len(addthese) + len(modded)) > 0:
            repo.index.add(addthese)
            repo.index.add(modded)
            repo.index.commit(message)

    return True


def main(argv=None):
    """ Sync Pinboard with local data """

    # initialize all the configuration
    args = parse_arguments()
    commitflag = (not args.nocommit)
    fetchflag = (not args.nofetch)
    config = load_config_file()
    pbauthkey = get_pinboard_apitoken(config)
    b1060str = get_b1060_timestamp_from_epoch(time.time())

    backupdir = config.get("backup", "backup_dir")

    filepart = "pinboard_export-" + b1060str + ".json"

    wget_target = os.path.join(backupdir, filepart)

    baseurl = 'https://api.pinboard.in/v1/posts/all?format=json'
    authpart = '&auth_token=' + pbauthkey

    if args.dest:
        wget_target = os.path.join(os.getcwd(), args.dest[0])
        filepart = os.path.basename(args.dest[0])

    # get the export from pinboard.in
    if fetchflag:
        urllib.request.urlretrieve(baseurl + authpart, wget_target)

    # set up the staging area
    export_stage = config.get("backup", "export_stage")
    os.chdir(export_stage)

    export_basename = 'pinboard-export.json'
    export_fullname = os.path.join(export_stage, export_basename)

    # update pinboard-export
    if fetchflag or args.dest:
        shutil.copy(wget_target, 'pinboard-export.json')

    message =  'automatic update from ' + filepart

    # check in the result
    if commitflag:
        repo = git.Repo('.')
        index = repo.index
        modded = [x.a_path for x in repo.index.diff(None).iter_change_type('M')]
        if len(modded) > 0:
            index.add(['pinboard-export.json'])
            index.commit(message)
    else:
        print('no commit')

    run_pinboard_splatter(export_fullname, message, commitflag)


if __name__ == '__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)

