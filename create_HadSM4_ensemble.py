#! /usr/bin/env python

# Program : create_template.py
# Author  : Peter Uhe, modified from script by Neil Massey
# Purpose : create the xml template for the HadAM3P experiment

import os
import xml.dom.minidom as dom
from xml.dom.minidom import getDOMImplementation
from io import StringIO
from ANC import *
import random
import getopt,sys
import argparse
random.seed(1)  # ensure reproducibility!

from create_xml2_funcs import CreatePertExpts2,AddBatchDict,remove_whitespace_nodes
from create_header_funcs import *

	
##############################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", help="Which site is the submission for 'dev' or 'main'?")
    parser.add_argument("--model", default="hadsm4", help="The model to use hadam4, wah2, hadcm3s. Defaults to wah2")
    parser.add_argument("--resolution", default="N144", help="The model resolution: 'N96','N144','N216'. Defaults to N96")
    parser.add_argument("--region", default="global", help="The model region: 'global','eu25','eas50' etc. Defaults to global")

    args = parser.parse_args()

    # Parameters that are the same for historical and natural simulations
    params={}
    params['model_start_month']=10
    params['run_years']=0
    params['run_months']=1
    params['file_solar']='solar_1985_2020'
    params['file_ozone']='ozone_c6_N144_1310-1409'
    params['file_so2dms']='SO2DMS_c6_N144_1310-1409'
    params['file_surf_curr']='uvc_GLO_ice_water_030507'
    params['file_heatcon']='xotawa.pc.Q.2013_c5day_s6'
    params['file_volcanic']='volc_1985_2020'
    params['file_volc']='VOLC38_LR'
    params['file_sulphox']='sulpc_ox_A2_1990_N144L38'
    params['file_ghg']='ghg_defaults'
    params['restart_upload_month']=0
    params['field_pert']=5 

    # Set up the xml doc - Remember to check/alter the header info as required
    impl = getDOMImplementation()
    
    # Set up upload location
    upload_loc="upload11"
	
    if args.model=="hadsm4":
        app_config="config_"+args.model+"_"+args.resolution.lower()+".xml"


    # define stash files in the order global,regional (or global only)
    stash_files=["slab_n144.stashc"]

    # define stash packing files in the order global, regional (or global only) HadAM4 only
    if args.model=="hadsm4":
        pack_files=["global_pack_data_docile.xml"]
    else:
        pack_files=""

    # Set up doc
    xml_doc = impl.createDocument(None, "WorkGen", None)
    root = xml_doc.documentElement

    make_header(xml_doc,args.site,upload_loc,app_config,stash_files,pack_files)
	
    # Set up number of perturbations 
    pert_start=0
    pert_end =5
    npert=pert_end-pert_start

    first_year=2013
    last_year=2013


    # Set start umid		
    start_umid = "a000"
    anc = ANC()
    anc.Start(start_umid) # next set


    print("Creating experiments... ")

    for year in range(first_year,last_year+1):
        params['model_start_year']=year
        params['file_atmos']='xpaef.start'
        end_umid=CreatePertExpts2(xml_doc,params,pert_start,pert_end,anc,args.resolution)
	
    # Add in batch tags:
    batch={}
    batch['name']="HadSM4 test experiment"
    batch['desc']="Test simulation for HadSM4 for CMIP6 forcings"
    batch['owner']="Matthias Aengenheyster <matthias.aengenheyster@wolfson.ox.ac.uk>,Sarah Sparrow <sarah.sparrow@oerc.ox.ac.uk>"
    batch['tech_info']=str(npert)+" initial conditions perturbations of 1 restarts.  Simulations forced with CMIP6 data."
    batch['proj']='DPHIL'
    batch['first_start_year']=first_year
    batch['last_start_year']=last_year
    batch['umid_start']=start_umid
    batch['umid_end']=end_umid
    AddBatchDict(xml_doc,batch)
    
    ######## Write out the file ########
	
    xml_out='wu_hadsm4_test_' +start_umid + '_' + end_umid + '.xml'
    if not os.path.exists('xmls'):
        os.makedirs('xmls')
    fh = open("xmls/"+xml_out, 'w')
    print('Writing to:',xml_out,'...')
    remove_whitespace_nodes(xml_doc)
    xml_doc.writexml(fh,newl='\n',addindent='\t')
    fh.close()
	
    count = xml_doc.getElementsByTagName("experiment").length

    print("Number of workunits: ",count)


    print('Done!')
