#!/usr/bin/env python
#############################################################################
#
#  Program : checkdate_ancil_dump.py
#  Author  : Peter Uhe
#  Date    : 07/01/14
#  Purpose : Function to  check that dump files are for the first of the month
#  Requires : read_um.py sourced from https://github.com/nrmassey/cpdn_ancil_maker
#	      01/06/16 SNS amended to return restart date
#############################################################################

import sys, os, gzip
from read_um import *
import glob

#############################################################################

# Function that checks if the dump file starts on the first of the month
# Returns True if first of the month, else false.  
#
def checkdate(infile):
	# read the file as a binary file
	#fh = gzip.open(infile, 'rb')
	fh = open(infile, 'rb')
	fix_hdr = read_fixed_header(fh)
	pp_hdrs = read_pp_headers(fh, fix_hdr)
	# check date in fix_hdr
	year = fix_hdr[27]
	mon = fix_hdr[28]
	day = fix_hdr[29]
#	print 'date of ancil/dump file'
	restart_date=str(year).zfill(4)+"-"+str(mon).zfill(2)+"-"+str(day).zfill(2)
	fh.close()	
	if day==1:
		return (True,restart_date)
	else: 
		return (False,restart_date)

#############################################################################

# Main script takes a list of (comma delimeted) pairs of dump files which are gzipped
# It writes out another list, of "good" files with only the dumps that start on the first of the month
#
if __name__ == "__main__":
	# Original list of dump files
	dump_list="start_dumps.txt"
	#Location of dump files 
	ancil_start='/storage/download/hadam3p/ancil/'
	# List of good dump files
	goodname='good_'+os.path.basename(dump_list)
	fgood=open(goodname,'w')

	# Loop over dump files
	for line in open(dump_list):
		atmos,region=line.split()
		fatmos=ancil_start+atmos.strip(' ,')
		fregion=ancil_start+region.strip(' ,')
		if checkdate(fatmos) and checkdate(fregion):
			fgood.write(line)
		else:
			print('bad file:',atmos.strip(' ,'),region.strip(' ,'))
	fgood.close()
