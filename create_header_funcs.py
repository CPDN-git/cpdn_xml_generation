#! /usr/bin/env python

# Program : create_header_template.py
# Author  : Sarah Sparrow
# Purpose : create the xml header

import xml.dom.minidom as dom
from StringIO import StringIO
from ANC import *
import random
random.seed(1)  # ensure reproducibility!

class SiteInfo:
        #site specific variables - start off empty
        download_url=""
        download_dir=""
	project_dir=""
        pass


def get_upload_info(upload_loc,vn="2.2"):
	# Dictionary of upload file handlers
	upload_info_dict={"dev":("dev","http://vorvadoss.oerc.ox.ac.uk/cpdnboinc_dev_cgi/file_upload_handler"),\
         	"upload2":("upload2","http://upload2.cpdn.org/cgi-bin/file_upload_handler"),\
                "upload3":("upload3","http://upload3.cpdn.org/cgi-bin/file_upload_handler"),\
                "upload4":("upload4","http://upload4.cpdn.org/cgi-bin/file_upload_handler"),\
                "upload5":("upload5","http://upload5.cpdn.org/cpdn_cgi_main/file_upload_handler"),\
                "upload6":("upload6","http://upload6.cpdn.org/cgi-bin/file_upload_handler"),\
                "upload7":("upload7","http://upload7.cpdn.org/cgi-bin/file_upload_handler"),\
                "upload8":("upload8","http://upload8.cpdn.org/cgi-bin/file_upload_handler"),
		"upload9":("upload9","http://upload9.cpdn.org/cgi-bin/file_upload_handler"),
		"upload10":("upload10","http://upload10.cpdn.org/cgi-bin/file_upload_handler"),
		"upload11":("upload11","http://upload11.cpdn.org/cgi-bin/file_upload_handler"),
		"upload12":("upload12","http://upload12.cpdn.org/cgi-bin/file_upload_handler")}
	
	upload_handler=upload_info_dict[upload_loc][1]
	upload_template="upload_templates/"+upload_info_dict[upload_loc][0]+vn+"/result_template_"+upload_loc
	
	return upload_handler,upload_template

def set_main_site():
	SiteInfo.download_url="http://download.cpdn.org/download/"
	SiteInfo.download_dir="/storage/download/"
	SiteInfo.project_dir="/storage/www/cpdnboinc"

def set_dev_site():
	SiteInfo.download_url="http://vorvadoss.oerc.ox.ac.uk/cpdnboinc_dev/download"
        SiteInfo.download_dir="/storage/boinc/projects/cpdnboinc_dev/download"
        SiteInfo.project_dir="/var/www/boinc/projects/cpdnboinc_dev"

def set_alpha_site():
        SiteInfo.download_url="http://vorvadoss.oerc.ox.ac.uk/cpdnboinc_alpha/download"
        SiteInfo.download_dir="/storage/boinc/projects/cpdnboinc_alpha/download"
        SiteInfo.project_dir="/var/www/boinc/projects/cpdnboinc_alpha"

def get_namelist_dir(app_config):
	app=app_config.split("_")[1]
	if app=="hadam3p" or app=="hadam3pm2":
		namelist_dir="Weather_At_Home"
	elif app=="hadcm3n":
		namelist_dir="HadCM3N"
	elif app=="hadcm3s":
		namelist_dir="HadCM3S"
	else:
		namelist_dir=app
	
	return namelist_dir

def make_header(xml_doc,site,upload_loc,app_config,stash_files,vn="2.2"):
	# Add xml header elements
	root = xml_doc.documentElement
	root.appendChild(xml_doc.createComment("App configuration settings i.e. model, region, triffid etc"))
        node=xml_doc.createElement('app_config')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode('config_dir/'+app_config))

	# Set upload information
	upload_handler,upload_template=get_upload_info(upload_loc,vn)
	root.appendChild(xml_doc.createComment("Upload information"))
	node=xml_doc.createElement('upload_handler')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(upload_handler))

        node=xml_doc.createElement('result_template_prefix')
        root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(upload_template))
	
	# Set download information
	if site=="main":
		set_main_site()
	elif site=="dev":
		set_dev_site()
	elif site=="alpha":
		set_alpha_site()

	root.appendChild(xml_doc.createComment("Download information for participants to get workunits"))
	node=xml_doc.createElement('download_url_base')
        root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(SiteInfo.download_url))

	node=xml_doc.createElement('download_dir_base')
        root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(SiteInfo.download_dir))

	node=xml_doc.createElement('project_dir')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(SiteInfo.project_dir))

	# Set namelist dir
	namelist_dir=get_namelist_dir(app_config)
	node=xml_doc.createElement('namelist_dir')
        root.appendChild(node)
	node.appendChild(xml_doc.createTextNode('namelist_template_files/'+namelist_dir))

	# Add stash files
	root.appendChild(xml_doc.createComment("Stash to use in the simulations"))
        stash_tags=["global_stashc","region_stashc"]
	for i,stash_tag in enumerate (stash_tags[0:len(stash_files)]):
		node=xml_doc.createElement(stash_tag)
        	root.appendChild(node)
		node.appendChild(xml_doc.createTextNode(stash_files[i]))
