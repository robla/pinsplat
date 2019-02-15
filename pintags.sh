#!/bin/bash
if [ ! -d "$SPLATDIR" ]; then
  echo "variable SPLATDIR needs to point to the directory that pinboard-splatter mime files are in"
  exit 1
fi
cd "$SPLATDIR"
grep '^tags: ' * | cut -d' ' -f2- | sed 's/ /\n/g' | sort -u
