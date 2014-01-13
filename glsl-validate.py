#!/usr/bin/python
import argparse
import os
import re
import shutil
import subprocess

DIR=os.path.dirname(os.path.realpath(__file__))

# Load in prefix files, see the prefix directory for examples
VERTEX_PREFIX = ""
FRAGMENT_PREFIX = ""
with open(os.path.join(DIR, "prefix/prefix.vert"), 'r') as f:
    VERTEX_PREFIX = f.read()
with open(os.path.join(DIR, "prefix/prefix.frag"), 'r') as f:
    FRAGMENT_PREFIX = f.read()

def standalone():
    parser = argparse.ArgumentParser(description='Validate three.js shaders')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+',
                               help='files to validate')
    args = parser.parse_args()
    files = args.files
    bad_extensions = filter(lambda f: not re.match('^\.(vert|frag)$', os.path.splitext(f)[1]), files)
    for f in bad_extensions:
        print "Invalid file: %s, only support .frag and .vert files" % f
        exit(1)

if __name__ == "__main__":
    standalone()
