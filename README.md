pinsplat - Splatter bookmarks file into little bitty ones.

Overview
========

Processes a [json formatted Pinboard export][pinboard_export] and splits
each bookmark into a separate file.  The generated .json files are pretty
much just a copy of the individual file.  The generated .mime files are
named using a novel 8-letter domain abbreviation for a fully-qualified
domain name (FQDN). They also use the [base10x60timestamp] in the name.

Features I would like to implement one day:

* Ability to edit a bookmark, and push the edited version to Pinboard
* Export bookmarks into [orgmode format]

Usage
=====

    Usage: pinsplat [-h] [bmkjson]

    positional arguments:
      bmkjson     bookmarks.json file

    optional arguments:
      -h, --help  show this help message and exit


Dependencies
============

Requires the following:
* [python_requests] module.
* [base10x60timestamp] module

Probably some other stuff too....

Credits
=======
Most code written by Rob Lanphier.  The 2016 starting point was a script
published by Ed Gauthier in 2012 as [pinboard_linkrot].

[pinboard_export]: https://pinboard.in/export/
[python_requests]: http://docs.python-requests.org/en/latest/
[orgmode format]: https://karl-voit.at/2017/09/23/orgmode-as-markup-only/
[base10x60timestamp]: https://github.com/robla/base10x60timestamp
[pinboard_linkrot]: https://github.com/edgauthier/pinboard_linkrot
