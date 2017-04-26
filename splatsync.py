#!/usr/bin/env python3

import argparse
import configparser
import git
import os
import re
import shutil
import subprocess
import sys
import urllib.request


def parse_arguments():
    """ see http://docs.python.org/library/argparse """
    parser = argparse.ArgumentParser(
        description='Sync Pinboard with local data')
    parser.add_argument('dest', help='optional download destination', 
        nargs='*', default=None)
    return parser.parse_args()


def load_config_file():
    configfile = os.path.expanduser("~/.pinboardrc")

    config = configparser.RawConfigParser()
    with open(configfile, "r") as f:
        config.readfp(f)
    return config


def get_pinboard_apitoken(config):
    api_token = config.get("authentication", "api_token")

    return api_token


# TODO - turn epoch into a library that I can import easily
def epoch_minusb():
    out_bytes = subprocess.check_output(['epoch','-b'])
    return out_bytes.decode("utf8").split('\n')[0]


# TODO - turn pinboard_splatter into library that I can import easily
# TODO - port (back) to python3
def run_pinboard_splatter(exportfile, message):
    config = load_config_file()

    # splatter data
    splatter_data = config.get("splatter", "data_dir")

    #xxx cd ~/pinboard/pinboard-splatter/data
    os.chdir(splatter_data)
    if(True):
        out_bytes = subprocess.check_output(['pinsplat', exportfile])

    repo = git.Repo('.')
    regexp = re.compile(r'(hash/json/|hash/mime/)')
    addthese = [x for x in repo.untracked_files if regexp.match(x)]
    repo.index.add(addthese)
    repo.index.commit(message)
    return True


def main(argv=None):
    """ Sync Pinboard with local data """

    # initialize all the configuration
    args = parse_arguments()
    config = load_config_file()
    pbauthkey = get_pinboard_apitoken(config)
    timepart = epoch_minusb()

    backupdir = config.get("backup", "backup_dir")

    filepart = "pinboard_export-" + timepart + ".json"

    wget_target = os.path.join(backupdir, filepart)

    baseurl = 'https://api.pinboard.in/v1/posts/all?format=json'
    authpart = '&auth_token=' + pbauthkey

    if(args.dest):
        wget_target = args.dest[0]
        filepart = os.path.basename(args.dest[0])

    # get the export from pinboard.in
    if(True):
        pinboardjson = urllib.request.URLopener()
        pinboardjson.retrieve(baseurl + authpart, wget_target)

    # set up the staging area
    export_stage = config.get("backup", "export_stage")
    os.chdir(export_stage)

    export_basename = 'pinboard-export.json'
    export_fullname = os.path.join(export_stage, export_basename)

    # update pinboard-export
    if(True):
        shutil.copy(wget_target, 'pinboard-export.json')
    
    message =  'automatic update from ' + filepart

    # check in the result
    if(True):
        repo = git.Repo('.')
        index = repo.index
        index.add(['pinboard-export.json'])
        index.commit(message)

    run_pinboard_splatter(export_fullname, message)


if __name__ == '__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)

