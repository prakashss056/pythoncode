######################################################################################################
# Author: PRAKASH S S <prakash@secpod.com>
# Date: 28/05/2019
# Requirement python 3.6
# Verify vulnarable application names collected by agent with the data in mongoDB - Windows/Linux/Mac
#######################################################################################################
import os
import re
import json
import io
from os.path import expanduser
import paramiko
from pprint import pprint
from pprint import *
from collections import OrderedDict
from cryptography.hazmat.primitives.serialization import ssh
class Vulnarability:
    home = expanduser("~")
#####################.....copy agent file from REMOTE MACHINE...... ##################
    def connopen(self,host, uname, pwd):
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host,username=uname,password=pwd)
        print("Connection Open")
    def copyagentfile(self):
            cmd =input("Enter your os Linux/Mac/Windows : ")
            if cmd == "Linux" or cmd == "Mac" or cmd == "mac" or cmd == "linux":
                uname =input("Enter agent machine's username and ip(xxxx@192.168.xx.yy): ")
                pwd =input("Enter agent machine's password: ")
                cmdlin = "sshpass -p " + pwd + " scp " + uname + ":/var/log/saner/spsaneragent.log ~/agentlog.log"
                print(cmdlin)
                os.system(cmdlin)
                if (os.system(cmdlin)) == 0:
                    print("log_data<<<<<<Agent log file copied>>>>>>")
                else:
                    print("######Agent log file copying failed######")
                    exit()
            elif cmd == "Windows" or cmd == "windows":
                ip =input("Enter agent username and IP(192.168.xx.yy): ")
                credential =input("Enter agent username and IP(username%password): ")
                cmdwin = 'smbclient \'//' + ip + '/c$\' -c \'lcd ' +Vulnarability().home + '; cd "Program Files\Secpod Saner\logs"; get spsaneragent.log testagentlogfile.log\' -U ' + credential + ''
                print(cmdwin)
                os.system(cmdwin)
                if (os.system(cmdwin)) == 0:
                    print("<<<<<<Agent log file copied>>>>>>")
                else:
                    print("######Agent log file copying failed######")
                    exit()
########################...."READING AGENT LOG"....########################3.
    def agentdictionary(self):
            filesystempath=('' + Vulnarability().home + '/agentlog.log')
            fptr = open(filesystempath,'r',)
            content=fptr.read()
            Host_details=re.findall(r'{[\s]*?"results":[\s\S]*?}[\s]*?][\s]*?}[\s]*?}[\s]*?}[\s]*?}',content,re.M|re.I)
            pprint(Host_details)
            VM_Results=result=re.findall(r'results json[\s]*?({[\s]*?"results"[\s\S]*?][\s]*?}[\s]*?}[\s]*?})[\s]*?\d+-\d+-\d+',content)
            pprint(VM_Results)
            #self.compare(json.loads(VM_Results[0]))
            if Host_details:
                print('---------------HOST DETAILS----------------------------------')
                Host_json=json.loads(Host_details[0])
                pprint(Host_json)
                hostjsonpretty = json.dumps(Host_json, indent=2, sort_keys=True)
                with io.open(""+ Vulnarability().home + "/AgentHostpretty.json", 'w') as f:
                    f.write(hostjsonpretty)
            if VM_Results:
                print('------------------------VM DETAILS---------------------------')
                VM_json=json.loads(VM_Results[0])
                VM_jsonpretty = json.dumps(VM_json, indent=2, sort_keys=True)
                with io.open("" + Vulnarability().home + "/vmagentpretty.json", 'w') as f:
                    f.write(str(VM_jsonpretty))
                return json.loads(VM_Results[0])
    def mongodata(self):
            host = '192.168.2.17'
            uname = 'root'
            pwd = 'secpod'
            Vulnarability().connopen(host,uname,pwd)
            collection = input("Enter the collection name: ")
            device = input("Enter the device name: ")
            mongouname = 'admin'
            mongopwd = 'S3CP0d@M0n90U53r'
            cmd = "mongoexport -h 127.0.0.1:27017 -d SanerDB -c " + collection + " -q '" + '{"results.sysinfo.primary_host_name":"' + device + '"}' + "' -u " + mongouname + " -p " + mongopwd + " --authenticationDatabase " + '"admin" --pretty -o ~/vmmongo.json'
            ssh.exec_command(cmd)
            ssh.close()
            cmd = 'sshpass -p "secpod" scp root@192.168.2.17:~/vmmongo.json ~/vmmongopretty.json'
            print("Copying mongo data")
            (os.system(cmd))
            if (os.system(cmd)) == 0:
                print("<<<<<<DSI extracted from Mongo>>>>>>")
            else:
                print("######DSI extraction from Mongo failed######")
#########################..........comparing agent and mongodb logs......#######################
    def compare(self,log_data,mongo_data):
        #import pdb;pdb.set_trace()
        list1=list()
        list2=list()
        for result in log_data['results']['assets']['asset']:
            list1.append(result['name'])
        for result in mongo_data['results']['assets']['asset']:
            list2.append(result['name'])
        if not (set(list1)-set(list2)):
             print("match")
        else :
              print('non-unique elements in agent-log : ',list(set(list1)-set(list2)))
        if not (set(list2) - set(list1)):
            print("match")
        else:
            print('non-unique elements in ancor-log : ', list(set(list2) - set(list1)))
###################
if __name__ == "__main__":
    ssh = paramiko.SSHClient()
    Vulnarability().copyagentfile()
    log_data=Vulnarability().agentdictionary()
    print(log_data)
    Vulnarability().mongodata()
    mongo_data= json.load(open(""+Vulnarability().home +"/vmmongopretty.json"), object_pairs_hook=OrderedDict)
    print(mongo_data)
    Vulnarability().compare(log_data,mongo_data)
########################################################################################################################
















