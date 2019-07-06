pinsplat - Splatter bookmarks file into little bitty ones.

Overview
========

Processes a [json formatted Pinboard export][pinboard_export] and tests each
link to determine if it's reachable. Invalid links are reported, along with
a reason, in markdown formatted text.

Usage
=====

    Usage: pinsplat [-h] [bmkjson]

    positional arguments:
      bmkjson     bookmarks.json file

    optional arguments:
      -h, --help  show this help message and exit


Dependencies
============

Requires the Python [Requests][python_requests] module.

[pinboard_export]: https://pinboard.in/export/
[python_requests]: http://docs.python-requests.org/en/latest/

Probably some other stuff too....