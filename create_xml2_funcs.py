#! /usr/bin/env python

# Program : create_template.py
# Author  : Peter Uhe, modified from script by Neil Massey
# Purpose : create the xml template for the HadAM3P experiment

import xml.dom.minidom as dom
from StringIO import StringIO
from ANC import *
import random
random.seed(1)	# ensure reproducibility!

def pretty_print(d):
	x = d.toxml().strip()
	c = 0
	e = 0
	y = ""
	while e != -1:
		e = x.find("><", c)
		y += x[c:e+1] + "\n    "
		c = e+1
	return y

def toprettyxmlf(node, encoding='utf-8'):
    tmpStream = StringIO()
    PrettyPrint(node, stream=tmpStream, encoding=encoding, indent='\t')
    return tmpStream.getvalue()

def GenPertList(include_zero_pert=False):
	# generate a list of possible perturbation files
	pert_list = []
	pert_base_year = "ic1961"
	pert_suffix = "_N96"
	scale_set = ["10", "11", "12", "14", "16"]

	for mm in range(1,13):
		for dd in range(1,30):
			for sc in range(0,5):
				pert_str = pert_base_year + "%02d" % mm + "%02d_" % dd + \
                           scale_set[sc] + pert_suffix
				pert_list.append(pert_str)

	# shuffle the list so it has a random order of perturbations
	random.shuffle(pert_list)
	# add the zero perturbation to the front of the list
	if include_zero_pert:
		pert_list.insert(0, "ic00000000_10_N96")

	return pert_list

def GenAM4PertList(res, include_zero_pert=False):
        # generate a list of possible perturbation files
        pert_list = []
        pert_prefix = "ic_"+res+"_"

        for mm in range(1,13):
		if mm == 12:
			year='2002'
		else:
			year='2003'

                for dd in range(0,59):
                	pert_str = pert_prefix + year + "%02d" % mm + "_%06d" % dd 
                        pert_list.append(pert_str)

        # shuffle the list so it has a random order of perturbations
        random.shuffle(pert_list)
        # add the zero perturbation to the front of the list
        if include_zero_pert:
                pert_list.insert(0, "icN144_testzero")

        return pert_list


######################

# Take dictionary of parameters and add experiment to the xml
def CreateExperiment(xml_doc, params_dict):
	# xml_doc   = xml document to append to
	# anc       = alpha numeric counter representing expt id
	# year      = year
	# pert_file = string for perturbation file to use

	# Set experiment and parameters tags and add to document
	root = xml_doc.documentElement
	whitespace=xml_doc.createTextNode('\n\t')
	root.appendChild(whitespace)
	expt_node = xml_doc.createElement('experiment')
	root.appendChild(expt_node)
#	whitespace=xml_doc.createTextNode('\n\t')
#	expt_node.appendChild(whitespace)
	parm_node = xml_doc.createElement('parameters')
	expt_node.appendChild(parm_node)
	

	# Loop over parameters and add
	for param,value in sorted(params_dict.iteritems()):
		whitespace=xml_doc.createTextNode('\n\t\t')
		parm_node.appendChild(whitespace)
		node=xml_doc.createElement(param)
		parm_node.appendChild(node)
		node.appendChild(xml_doc.createTextNode(str(value)))

	whitespace=xml_doc.createTextNode('\n\t')
	parm_node.appendChild(whitespace)
	
#	whitespace=xml_doc.createTextNode('\n\t')
#	expt_node.appendChild(whitespace)

#########################

# Adds batch tags to xml file
def AddBatch(xml_doc,batch_name,batch_desc,batch_owner,syear):
	root = xml_doc.documentElement
	
	node=xml_doc.createElement('batch_name')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(batch_name))
	
	node=xml_doc.createElement('batch_desc')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(batch_desc))
	
	node=xml_doc.createElement('batch_owner')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(batch_owner))
	
	node=xml_doc.createElement('batch_start_year')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(str(syear)))


#########################

# Adds batch tags to xml file
def AddBatchDict(xml_doc,batch):
	root = xml_doc.documentElement

	for key,val in sorted(batch.iteritems()):
		whitespace=xml_doc.createTextNode('\n\t')
		root.appendChild(whitespace)
		node=xml_doc.createElement('batch_'+key)
		root.appendChild(node)
		node.appendChild(xml_doc.createTextNode(str(val)))
	
#########################


# Adds batch tags to xml file
# Note when including the batchid, the workgen scripts will 
# NOT insert batch entries into the database!
def AddExistingBatch(xml_doc,batchid,batch_name,batch_desc,batch_owner,syear):
	root = xml_doc.documentElement
	
	node=xml_doc.createElement('batchid')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(str(batchid)))

	node=xml_doc.createElement('batch_name')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(batch_name))
	
	node=xml_doc.createElement('batch_desc')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(batch_desc))
	
	node=xml_doc.createElement('batch_owner')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(batch_owner))
	
	node=xml_doc.createElement('batch_start_year')
	root.appendChild(node)
	node.appendChild(xml_doc.createTextNode(str(syear)))

#########################

# Adds sub batch tags to xml file
def AddSubBatch(xml_doc,sb_id,sb_start,sb_stop,sb_desc):
	print 'Added Sub Batch',sb_id
	root = xml_doc.documentElement
	sb_node = xml_doc.createElement('sub_batch')
	root.appendChild(sb_node)

	node=xml_doc.createElement('sub_batch_id')
	sb_node.appendChild(node)
	node.appendChild(xml_doc.createTextNode(str(sb_id)))
	
	node=xml_doc.createElement('umid_start')
	sb_node.appendChild(node)
	node.appendChild(xml_doc.createTextNode(sb_start))
	
	node=xml_doc.createElement('umid_stop')
	sb_node.appendChild(node)
	node.appendChild(xml_doc.createTextNode(sb_stop))
	
	node=xml_doc.createElement('sub_batch_desc')
	sb_node.appendChild(node)
	node.appendChild(xml_doc.createTextNode(sb_desc))

##########################


# Adds experiments for a given list of restart dumps 
# and initial condition perturbations
def CreatePertExpts(xml_doc,params_dict,restarts,pert_start,pert_end,anc):	
	# restart dumps:
	tmp=restarts.split(',')
	fatmos=tmp[0].strip()
	params_dict['file_atmos']=fatmos
	if len(tmp)>1:
		fregion=tmp[1].strip()
		params_dict['file_region']=fregion
	pert_list = GenPertList()[pert_start:pert_end] 
	
	for i,pert in enumerate(pert_list):
		params_dict['file_pert']=pert
		params_dict['exptid']=anc.Get()
		CreateExperiment(xml_doc,params_dict)
		anc.Next()
	return params_dict['exptid'] # Last added umid


##########################

# Adds experiments for a given dictionary of parameters
# and initial condition perturbations
def CreatePertExpts2(xml_doc,params_dict,pert_start,pert_end,anc, res = 'N96'):	
	# Create list of perturbations
	if res == 'N96':
		pert_list = GenPertList()[pert_start:pert_end] 
	else:
		pert_list = GenAM4PertList(res)[pert_start:pert_end]
	
	for pert in pert_list:
		params_dict['file_pert']=pert
		params_dict['exptid']=anc.Get()
		CreateExperiment(xml_doc,params_dict)
		anc.Next()
	return params_dict['exptid'] # Last added umid
	
	
#############################
	
def remove_whitespace_nodes(node, unlink=False):
    """Removes all of the whitespace-only text decendants of a DOM node.
    
    When creating a DOM from an XML source, XML parsers are required to
    consider several conditions when deciding whether to include
    whitespace-only text nodes. This function ignores all of those
    conditions and removes all whitespace-only text decendants of the
    specified node. If the unlink flag is specified, the removed text
    nodes are unlinked so that their storage can be reclaimed. If the
    specified node is a whitespace-only text node then it is left
    unmodified."""
    remove_list = []
    for child in node.childNodes:
        if child.nodeType == dom.Node.TEXT_NODE and \
           not child.data.strip():
            remove_list.append(child)
        elif child.hasChildNodes():
            remove_whitespace_nodes(child, unlink)
    for node in remove_list:
        node.parentNode.removeChild(node)
        if unlink:
            node.unlink()
