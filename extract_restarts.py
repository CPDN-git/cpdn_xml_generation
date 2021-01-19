##############################################################################
# Program  : extract_restarts.py
# Author   : Sarah Sparrow
# Created  : 17/01/2017
# Purpose  : To extract and rename restart files from a simulation
##############################################################################
import sys,os,getopt,glob
import numpy as np
import zipfile
import zlib
from checkdate_ancil_dump import checkdate


model_types=["global","coupled","nested"]

prefixes=['atmos','region','ocean']

class Vars:
    #input command line variables
    batch=0
    data_dir='/group_workspaces/jasmin/cssp_china/wp1/lotus/cpdn/lotus/'
    out_dir='/group_workspaces/jasmin/cssp_china/users/ssparrow01/actual_restarts/'
    model_type='nested'
    dry_run=False
    pass


##############################################################################


def Usage():
    print("Usage :\n"\
    "	--batch=	batch number to extract restarts from\n"\
    "	--data_dir=	location of the batch directory\n"\
    "	--out_dir=	location to put the extracted restarts in\n"\
    "	--model_type=	model type enter 'global', 'coupled' or 'nested'\n"\
	"	--dry_run	do a dry run without extracting files")

    sys.exit()


##############################################################################


def ProcessCommandLineOpts():
    # Process the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:],'',['batch=','data_dir=','out_dir=','model_type=','dry_run'])
        if len(opts) == 0:
            Usage()
        for opt, val in opts:
            if opt == '--batch':
                Vars.batch=val
            elif opt == '--data_dir':
                Vars.data_dir=val
            elif opt =='--out_dir':
                Vars.out_dir=val
            elif opt == '--model_type':
                if val in model_types:
                    Vars.model_type=val
                else:
                    print("Please use a valid model type")
                    Usage()
            elif opt=='--dry_run':
                Vars.dry_run=True
    except getopt.GetoptError:
        Usage()

##############################################################################
def extract_restarts():
    path=Vars.data_dir+'batch_'+Vars.batch+'/successful/*/*_restart.zip'
    print(path)
    restart_zips=glob.glob(path)

    restart_lines=[]
	
    for restart_zip in restart_zips:
        rzip=zipfile.ZipFile(restart_zip,'r')
        file_name=restart_zip.split('/')[-1]
        if Vars.model_type=='nested':
            file_id_split=file_name.split('_')[1:4]
            region=file_name.split('_')[2]
            dpos=2
            prefix_ids=[0,1]
        if Vars.model_type=='global':
            file_id_split=file_name.split('_')[1:4]
            dpos=2
            prefix_ids=[0]
        if Vars.model_type=='coupled':
            file_id_split=file_name.split('_')[1:3]
            dpos=1
            prefix_ids=[0,2]

        try:
            # check to see if it's a valid zip or invalid compressed data to inflate
            rzip.extractall(Vars.out_dir)
        except zipfile.BadZipfile as err:
            print("Bad zip file ",err)
            continue
        except zlib.error as err:
            print("Invalid compressed data to inflate ",err)
            continue
        except:
            pass

        line=[]
        for pid in prefix_ids:
            old_file=prefixes[pid]+"_restart.day"
            (okay,rdate)=checkdate(Vars.out_dir+old_file)
            file_id_split[dpos]=rdate
            file_id="_".join(file_id_split)
            new_file=prefixes[pid][0]+'start_b'+Vars.batch+'_'+file_id
            if not (okay):
                print('Error', new_file)
            else:
                if Vars.dry_run:
                    print(Vars.out_dir)
                    print(old_file,new_file)
                else:
                    print(old_file,new_file)
                    if os.path.isfile(Vars.out_dir+new_file) or os.path.isfile(Vars.out_dir+new_file+'.gz'):
                        print("Already extracted")
                    else:
                        try:
                            os.rename(Vars.out_dir+old_file,Vars.out_dir+new_file)
                        except:
                            if os.path.exists(Vars.out_dir+old_file):
                                os.remove(Vars.out_dir+old_file)
                                pass
                # Create the line for the csv file information
                line.append(new_file)
        restart_lines.append(','.join(line))
	
    # write out the csv file
    if Vars.dry_run:
        print(restart_lines)
    else:
        f=open(Vars.out_dir+'batch_'+Vars.batch+'_restarts.csv','w')
        for rline in restart_lines:    
            f.write(rline+'\n')
				
#Main controling function
def main():
    ProcessCommandLineOpts()
    extract_restarts()
    print('Finished!')

#Washerboard function that allows main() to run on running this file
if __name__=="__main__":
  main()
