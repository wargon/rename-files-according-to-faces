#!/usr/bin/python

''' 
Copyright (C) 2013 Laurent Wargon laurent@wargon.org

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
'''

'''
Thanks to Joshua Klontz for his advise
https://groups.google.com/forum/?fromgroups#!searchin/openbr-dev/wargon/openbr-dev/7_NYi0rXOjU/Mpkpgxo98csJ
'''

import os, sys, ntpath, shutil
import subprocess, shlex

def shell_exec(command_line):
  args = shlex.split(command_line)
  subprocess.call(args)

def create():

  # remove file if existe
  list_file = [ gallery_gal, gallery_csv, scores, identities_csv ]
  for filename in list_file:
    if os.path.exists(filename):
      os.remove(filename)

  # First you'll need to generate a gallery of enrolled templates:
  shell_exec('br -useGui 0 -algorithm FaceRecognition -enrollAll -enroll ' + directory + ' "' + gallery_gal + ';' + gallery_csv + '[separator=;]"')
  # Two files will be created: 
  # meds.gal contains the face templates. 
  # meds.csv is a human-readable output of template metadata to be used later.

  # Then you need to create a self-similarity matrix, by comparing all the templates against each other:
  shell_exec('br -useGui 0 -algorithm FaceRecognition -compare ' + gallery_gal + ' . ' + scores)

  # Finally, cluster the score matrix into identities:
  shell_exec('br -useGui 0 -cluster ' + scores + ' ' + cursor + ' ' + identities_csv)

  # Every row in identities.csv will be a unique identity. Each number in identities.csv is the index of the template in meds.gal. You can figure out which face this number corresponds to by looking it up in meds.csv. A value of 278 in identities.csv is the 278th entry in meds.csv. Try changing the value '5' to other values in the range 1-10 to get different levels of clustering aggressiveness.


if len(sys.argv) < 2:
  sys.stderr.write("Usage: %s directory cursor\n" % (sys.argv[0],))
  sys.exit(1)

directory      = sys.argv[1]
gallery_gal    = 'gallery.gal'
gallery_csv    = 'gallery.csv'
scores         = 'scores.mtx'
identities_csv = 'identities.csv'
cursor         = sys.argv[2]

create()

gallery_csv_ptr = open(gallery_csv)
gallery_dict = {}

identities_csv_ptr = open(identities_csv)
identities_lines = identities_csv_ptr.readlines()
identities_lines.sort()

for line in gallery_csv_ptr:
  elmt = line.split(',')
  photo_whith_path = elmt[0]
  photo  = ntpath.basename(photo_whith_path)
  index = elmt[16]
  gallery_dict[index] = photo

dir_dst = directory + '_classified/'
if os.path.isdir (dir_dst):
  shutil.rmtree (dir_dst)
os.mkdir (dir_dst)

k = 0
for line in identities_lines:
  k = k + 1
  elmt = line.split(',')
  i = 0
  for n in elmt:
    i = i + 1
    n = n.rstrip('\n')
    src = gallery_dict.get(n, '-')
    if not src == '-': 
      N = str (n)
      K = str (k)
      I = str (i)
      dst_name = dir_dst + '{:03}'.format(k) + '_' + '{:02}'.format(i) + '_' + src
      src_name = directory + '/' + src
      shutil.copy (src_name, dst_name)
      # print src_name + ' ' + dst_name 

