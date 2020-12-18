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
    parser.add_argument("--resolution", default="N48", help="The model resolution: 'N96','N144','N216'. Defaults to N96")
    parser.add_argument("--model", default="hadcm3s", help="The model to use hadam4, wah2, hadcm3s. Defaults to wah2")

    args = parser.parse_args()

    # Parameters that are the same for historical and natural simulations
    params={}
    params['model_start_month']=12
    params['run_years']=10
    params['run_months']=0
    params['file_solar']='solar_n00a'
    params['file_ozone']='ozone_hadcm3_1859.be.32'
    params['file_so2dms']='DMSallNH3SO21859.be.32'
    params['file_spec_sw']='spec3a_sw_3_asol2c_hadcm3'
    params['file_spec_lw']='spec3a_lw_3_asol2c_hadcm3'
    params['file_volcanic']='volc_c000a_72'
    params['file_volc']='NAT_VOLC'
    params['file_sulphox']='sulpc_oxidants_19_A2_1990'
    params['file_ghg']='ghg_preindust'
    params['field_pert']=5 
    params['file_flux']='waterfix.ancil.be.32'

    # Set up the xml doc - Remember to check/alter the header info as required
    impl = getDOMImplementation()
    
    # Set up upload location
    upload_loc="upload11"
	
    app_config="config_hadcm3s_v2.2_yearly.xml"

    pack_files=["global_pack_data_docile.xml","regional_pack_data.xml"]
    
    # define stash files in the order global,regional (or global only)
    stash_files=["xabnk.stashc.monthly_TCRE_full"]

    # Set up doc
    xml_doc = impl.createDocument(None, "WorkGen", None)
    root = xml_doc.documentElement

    make_header(xml_doc,args.site,upload_loc,app_config,stash_files,pack_files)
	
    # Set up number of perturbations 
    pert_start=0
    pert_end =74
    npert=pert_end-pert_start

    first_year=1900
    last_year=1900


    # Set start umid		
    start_umid = "a000"
    anc = ANC()
    anc.Start(start_umid) # next set


    print("Creating experiments... ")

    for year in range(first_year,last_year+1):
        params['model_start_year']=year
        params['file_atmos']='n7q2_1900.astart'
        params['file_ocean']='n7q2_1900.ostart'
        end_umid=CreatePertExpts2(xml_doc,params,pert_start,pert_end,anc,args.resolution)
	
    # Add in batch tags:
    batch={}
    batch['name']="EUCP Spinup experiment"
    batch['desc']="EUCP spinup experiment  with constant pre-industrial forcings"
    batch['owner']="Chris O'Reilly <christopher.oreilly@physics.ox.ac.uk>,Sarah Sparrow <sarah.sparrow@oerc.ox.ac.uk>"
    batch['tech_info']=str(npert)+" initial conditions perturbations of 1900 standard physics restart.  Simulations forced with constant pre-industrial forcing."
    batch['proj']='EUCP'
    batch['first_start_year']=first_year
    batch['last_start_year']=last_year
    batch['umid_start']=start_umid
    batch['umid_end']=end_umid
    AddBatchDict(xml_doc,batch)
    
    ######## Write out the file ########
	
    xml_out='wu_hadcm3s_EUCP_spinup_' +start_umid + '_' + end_umid + '.xml'
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
