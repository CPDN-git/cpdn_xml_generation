#! /usr/bin/env python

# Program : create_template.py
# Author  : Peter Uhe, modified from script by Neil Massey
# Purpose : create the xml template for the HadAM3P experiment

import os
import xml.dom.minidom as dom
from xml.dom.minidom import getDOMImplementation
from StringIO import StringIO
from ANC import *
import random
import getopt,sys
random.seed(1)  # ensure reproducibility!

from create_xml2_funcs import CreatePertExpts2,AddBatchDict,remove_whitespace_nodes
from create_header_funcs import *

class Vars:
        #input command line variables
        site=""
        pass


##############################################################################


def Usage():
        print "Usage :  --site=         specify 'dev' or 'main' site"
        sys.exit()


##############################################################################


def ProcessCommandLineOpts():

        # Process the command line arguments
        try:
                opts, args = getopt.getopt(sys.argv[1:],'',
                ['site='])

                if len(opts) == 0:
                        Usage()
                for opt, val in opts:
                        if opt == '--site':
                                Vars.site=val
        except getopt.GetoptError:
                Usage()

##############################################################################


	
##############################
if __name__ == "__main__":
	# Firstly read any command line options
	ProcessCommandLineOpts()

	# Parameters that are the same for historical and natural simulations
	params={}
	params['model_start_month']=12
	params['run_years']=1
	params['run_months']=1
	params['file_solar']='solar_1985_2020'
	params['file_volcanic']='volc_1985_2020'
	params['file_sulphox']='oxi.addfa'
	params['file_atmos']='xhjlya.start.0000.360.new'
	params['file_region']='generic_start_eas50_aabbw'
	params['file_ghg']='ghg_defaults'
	params['restart_upload_month']=12
        # for new region with triffid, should always be a certain times of 360, so 360, 720, 1080, etc., if do not want to run triffid
	# set triffid_period to be longer than your run period.
	params['triffid_period']=720	

	# Set up the xml doc - Remember to check/alter the header info as required
        impl = getDOMImplementation()
        # Set up doc
        upload_loc="dev"
        app_config="config_wah2.2_eas50.xml"

        # define stash files in the order global,regional (or global only)
        stash_files=["xaakm_global_basic_2016-04-18.stashc","xacxf_region_basic_2016-07-19_v5.stashc"]


	# Set up doc
	xml_doc = impl.createDocument(None, "WorkGen", None)
        root = xml_doc.documentElement

        make_header(xml_doc,Vars.site,upload_loc,app_config,stash_files)
	
	# Set up number of perturbations 
	pert_start=0
	pert_end = 55
	
	first_year=1985
	last_year=2014


	# Set start umid		
	start_umid = "a000"
	anc = ANC()
	anc.Start(start_umid) # next set


	print "Creating experiments... "

	# Possible ozone/so2dms files (depending on decade)
	ozone_files={1980:'ozone_hist_N96_1979_1990v2',1990:'ozone_hist_N96_1989_2000v2',2000:'ozone_rcp45_N96_1999_2010v2',2010:'ozone_rcp45_N96_2009_2020v2'}
	so2dms_files={1980:'so2dms_hist_N96_1979_1990v2',1990:'so2dms_hist_N96_1989_2000v2',2000:'so2dms_rcp45_N96_1999_2010',2010:'so2dms_rcp45_N96_2009_2020'}

	for year in range(first_year,last_year+1):
		params['model_start_year']=year
		decade=(year+1)/10*10 #For last year in the decade use the next decade for ancil files		
#		decade=year/10*10
		params['file_ozone']=ozone_files[decade]
		params['file_so2dms']=so2dms_files[decade]
		params['file_sst']='ALLclim_ancil_14months_OSTIA_sst_'+str(year)+'-12-01_'+str(year+2)+'-01-30'
		params['file_sice']='ALLclim_ancil_14months_OSTIA_ice_'+str(year)+'-12-01_'+str(year+2)+'-01-30'

		end_umid=CreatePertExpts2(xml_doc,params,pert_start,pert_end,anc)
	
	# Add in batch tags:
	batch={}
	batch['name']="WAH2 East Asia 50km 1986-2015"
	batch['desc']="Spin up runs for WAH2 East Asia 50km climatology for 1986-2015 (starting dec 1985)"
	batch['owner']="Sarah Sparrow <sarah.sparrow@oerc.ox.ac.uk>"
	batch['tech_info']="55 initial condition perturbations per year, all from generic start dumps, forced by OSTIA SSTs and sea-ice"
	batch['proj']='LOTUS'
	batch['first_start_year']=first_year
	batch['last_start_year']=last_year
	batch['umid_start']=start_umid
	batch['umid_end']=end_umid
	AddBatchDict(xml_doc,batch)
	
	######## Write out the file ########
	
	xml_out='wu_wah2_eas50_basic_spinup_climatology_1985-2013_' + str(params['model_start_year']) + "_" +\
			  start_umid + '_' + end_umid + '.xml'
	if not os.path.exists('xmls'):
		os.makedirs('xmls')
	fh = open("xmls/"+xml_out, 'w')
	print 'Writing to:',xml_out,'...'
        remove_whitespace_nodes(xml_doc)
        xml_doc.writexml(fh,newl='\n',addindent='\t')
        fh.close()
	
        count = xml_doc.getElementsByTagName("experiment").length

	print "Number of workunits: ",count


	print 'Done!'
