#! /usr/bin/env python

# Program : create_template.py
# Author  : Peter Uhe, modified from script by Neil Massey
# Purpose : create the xml template for the HadAM3P experiment

import xml.dom.minidom as dom
from xml.dom.minidom import getDOMImplementation
from StringIO import StringIO
from ANC import *
import random
import getopt,os,sys
import lxml.etree
random.seed(1)  # ensure reproducibility!

from create_xml2_funcs import CreatePertExpts,AddBatchDict,remove_whitespace_nodes
from create_header_funcs import *

models=['CCSM4','CanESM2', 'CNRM-CM5', 'CSIRO-Mk3', 'GFDL-CM3', 'GISS-E2-H', 'GISS-E2-R', 'HadGEM2-ES', 'IPSL-CM5A-LR', 'IPSL-CM5A-MR', 'MIROC-ESM','MMM','NorESM1-M']

class Vars:
        #input command line variables
        generic=False
        site=""
        pass


##############################################################################


def Usage():
        print "Usage :  --generic       uses generic restart files\n"\
        "       --site=         specify 'dev' or 'main' site"

        sys.exit()


##############################################################################


def ProcessCommandLineOpts():

        # Process the command line arguments
        try:
                opts, args = getopt.getopt(sys.argv[1:],'',
                ['generic','site='])

                if len(opts) == 0:
                        Usage()
                for opt, val in opts:
                        if opt == '--generic':
                                Vars.generic=True
                        elif opt == '--site':
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
	params['run_years']=0
	params['run_months']=10
	params['file_solar']='solar_1985_2020'
	params['file_volcanic']='volc_1985_2020'
	params['file_sulphox']='oxi.addfa'
	params['file_atmos']='xhjlya.start.0000.360.new'
	params['file_region']='generic_start_eas50_aabbw'
	params['file_ghg']='file_ghg_1850'
	params['restart_upload_month']=4

	# Set up doc
        upload_loc="upload2"
        app_config="config_wah2.2_eas50.xml"
        # define stash files in the order global,regional (or global only)
        stash_files=["global_lotus_stash_2016-12-04.stashc","regional_lotus_stash_2016-12-04.stashc"]


	impl = getDOMImplementation()

        xml_doc = impl.createDocument(None, "WorkGen", None)
        root = xml_doc.documentElement
                
        make_header(xml_doc,Vars.site,upload_loc,app_config,stash_files)

	# Set up number of perturbations 
	pert_start=0
	pert_end =8
	
	first_year=2016
	last_year=2016


	# Set start umid		
	start_umid = "n000"
	anc = ANC()
	anc.Start(start_umid) # next set

	restarts_list='batch_lists/batch_702_restarts.csv'

	print "Creating experiments... "

	# Possible ozone/so2dms files (depending on decade)
	ozone_files={1980:'ozone_preind_N96_1879_0000Pv5',1990:'ozone_preind_N96_1879_0000Pv5',2000:'ozone_preind_N96_1879_0000Pv5',2010:'ozone_preind_N96_1879_0000Pv5'}
	so2dms_files={1980:'so2dms_prei_N96_1855_0000P',1990:'so2dms_prei_N96_1855_0000P',2000:'so2dms_prei_N96_1855_0000P',2010:'so2dms_prei_N96_1855_0000P'}
	tech_info_details=""
	model_start_umid=start_umid
	for year in range(first_year,last_year+1):
		params['model_start_year']=year
		decade=(year+1)/10*10 #For last year in the decade use the next decade for ancil files		
#		decade=year/10*10
		params['file_ozone']=ozone_files[decade]
		params['file_so2dms']=so2dms_files[decade]
		params['file_sice']='OSICE_natural_0000P'
		#tech_info_details += " Year "+str(year)+": "
		for model in models:
			params['file_sst']='NATclim_ancil_14months_OSTIA_sst_'+model+'_'+str(year)+'-12-01_'+str(year+2)+'-01-30'
			i=0
			sumid=model_start_umid
                	for restarts in open(restarts_list):
                        	if i>=75: # Take only 75 restarts per year
                                	break
                        	end_umid=CreatePertExpts(xml_doc,params,restarts,pert_start,pert_end,anc)
                        	i=i+1
			tech_info_details += ", "+model+":"+sumid+"-"+end_umid
			model_start_umid=end_umid
	# Add in batch tags:
	batch={}
	batch['name']="WAH2 East Asia 50km Natural 2017"
	batch['desc']="2nd generation WAH2 East Asia 50km Naturals for 2017 (starting dec 2016)"
	batch['owner']="Sarah Sparrow <sarah.sparrow@oerc.ox.ac.uk>"
	batch['tech_info']="Restarts from batch 702, 13 CMIP5 Natural only patterns"+tech_info_details
	batch['proj']='LOTUS'
	batch['first_start_year']=first_year
	batch['last_start_year']=last_year
	batch['umid_start']=start_umid
	batch['umid_end']=end_umid
	AddBatchDict(xml_doc,batch)
	
	######## Write out the file ########
	
	xml_out='wu_wah2_eas50_natural_2gen_2017_' +\
			  start_umid + '_' + end_umid + '.xml'
        if not os.path.exists('xmls'):
                    os.makedirs('xmls')
        fh = open("xmls/"+xml_out, 'w')
        print 'Writing to:',xml_out,'...'
        remove_whitespace_nodes(xml_doc)
        xml_doc.writexml(fh,newl='\n',addindent='\t')
        fh.close()
       
        # Print out the number of xmls
        count = xml_doc.getElementsByTagName("experiment").length 
        print "Number of workunits: ",count
        
        print 'Done!'	
