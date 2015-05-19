#!/usr/bin/env python
#
# Copyright (C) 2014 Vangelis Tasoulas <vangelis@tasoulas.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#################################################################################
###### DEPENDENCIES
# You will need pysrt library to be able to run this script.
# sudo easy_install pysrt

###### SHORT DESCRIPTION
# This script will read an srt subtitle, it will remove empty/blank subtitle
# lines that render the subtitles unusable in many smart media players,
# and it will save the output in utf-8 encoding.
#
# The encoding of the input subtitle will be autoguessed, or it can be supplied
# by the user in case the autoguessing fails.

import pysrt
import chardet
import argparse
import os

VERSION="0.0.1"

parser = argparse.ArgumentParser(description="{} version {}. This simple script will remove blank"
                                             "subtitles and trim leading and trailing whitespaces.".format(
                                             "Subtitle Cleaner", VERSION
                                             )
                                )

parser.add_argument("-v", "--version",
                    action="version", default=argparse.SUPPRESS,
                    version=VERSION,
                    help="show program's version number and exit")

parser.add_argument("-i", "--input-filename", required=True,
                    action="store",
                    dest="filename",
                    help="The subtitle (srt) file to clean")

parser.add_argument("-o", "--output-filename",
                    action="store",
                    dest="output_filename",
                    help="The output file to save the cleaned subtitle")

parser.add_argument("-e", "--encoding",
                    action="store",
                    dest="encoding",
                    help="The encoding of the input file. If not provided, an attempt will be made to autoguess.")

parser.add_argument("-r", "--replace-original",
                    action="store_true",
                    default=False,
                    dest="fix_in_place",
                    help="The cleaned srt file will overwrite the original file. WARNING: Use this with care, especially if you let the script to autoguess the input character encoding!")

opts = parser.parse_args()

filename = opts.filename
if opts.output_filename:
    if opts.fix_in_place:
        print("ERROR: Cannot combine --replace-original and --output-filename options. Please use only one of them.")
        exit(1)
    output_filename = opts.output_filename
else:
    if opts.fix_in_place:
        output_filename = filename
    else:
        output_filename = os.path.join(os.path.dirname(filename), "Cleaned-{0}".format(os.path.basename(filename)))

if opts.encoding:
    encoding = opts.encoding
else:
    content = open(filename, "r").read()
    guess = chardet.detect(content)
    encoding = guess['encoding']
    detection_confidence = round(guess['confidence'], 3) * 100
    print("Detected encoding '{0}' with {1}% confidence.".format(encoding, detection_confidence))

subs = pysrt.open(filename, encoding=encoding)

# Trim white spaces
text_stripped = []
for i in range(len(subs)):
    orig_text = subs[i].text
    stripped_text = subs[i].text.strip()
    if orig_text != stripped_text:
        text_stripped.append(subs[i].index)
        subs[i].text = subs[i].text.strip()

# Find the list index of the empty lines. This is different than the srt index!
# The list index starts from 0, but the srt index starts from 1.
count = 0
to_delete = []
for sub in subs:
    if not sub.text:
        to_delete.append(count)
    count = count + 1

to_delete.sort(reverse=True)

# Delete the empty/blank subtitles
for i in to_delete:
    del subs[i]

# Fix Index and trim white spaces
for i in range(len(subs)):
    subs[i].index = i + 1

if not text_stripped and not to_delete:
    print("Subtitle clean. No changes made.")
    # If no subtitle changes were made, just convert the subtitle file to UTF-8
    if(encoding.lower() != "utf8" and encoding.lower() != "utf-8"):
        print("Converting to UTF-8 and saving file to {0}".format(output_filename))
        subs.save(output_filename, encoding='utf-8')
else:
    print("Index of subtitles deleted: {0}".format([i + 1 for i in to_delete]))
    print("Index of subtitles trimmed: {0}".format(text_stripped))
    print("Saving UTF-8 encoded file to '{0}'".format(output_filename))
    subs.save(output_filename, encoding='utf-8')
