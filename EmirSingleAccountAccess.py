######################################################################################################

# Author: PRAKASH S S <prakash@secpod.com>
# Date: 05/07/2019
# Requirement python 3.6
# verify EM-Responses(IR) there in host details page with mongodb

#######################################################################################################
import os,re,sys
from collections import OrderedDict
from os.path import expanduser
import json
import io
import paramiko
import requests
from bs4 import BeautifulSoup as bs
from cryptography.hazmat.primitives.serialization import ssh

#******************************************HTML-TABLE-PARSER************************************************************************#
def sp_table_parser(html_content, table_id=None):
    print('#***********GET ALL EM RELATED DETAILS FROM UI*******************#')
    try:
        soup = bs(html_content, 'html.parser')
        if table_id is not None:
            table = soup.find('table', id=table_id)
        else:
            table = soup.find('table')
        headings = [th.get_text().strip()
        for th in table.find("tr").find_all("th")]
        ui_data = []
        for row in table.find_all("tr")[1:]:
            dataset = dict(zip(headings, (td.get_text() for td in row.find_all("td"))))
            ui_data.append(dataset)
        return ui_data

    except Exception as msg:
        print(msg)
        return

#***************************************** TO-OPEN-CONNECTION **********************************************************#
def connopen(host, uname, pwd):
    print('#**********************TO OPEN THE CONNECTION**********************#')
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=uname, password=pwd)
    print("Connection Open")

#**********************************TO-COLLECT IR's FROM MONGODB ********************************************************#
def mongodata():
    print('#**********************GET THE DATA FROM MONGO BY QUERYING*********#')
    host = '192.168.2.17'
    uname = 'root'
    pwd = 'secpod'
    connopen(host, uname, pwd)
    print(" --------remove all Em related older files is going on --------")
    cmd0 = "rm -rf ~/EMresponse.json ~/Emqueries.json ~/EMfinalresponse.json"
    ssh.exec_command(cmd0)
    print("# --------removed all older files is done --------")
    collection = 'sp1vwtpn7vwx6zo'
    #device = input("Enter the device name: ") #want to enter device name just uncomment and insert device in cm2 query in front of device name
    mongouname = 'admin'
    mongopwd = 'S3CP0d@M0n90U53r'
    cmd1 = "mongoexport -h 127.0.0.1:27017 -d Queries -c" + collection +" -q '"+ '{"query.category" : "EM","query.family":"unix"}' + "' -u " + mongouname + " -p " + mongopwd + " --authenticationDatabase " + '"admin" --pretty -o ~/Emqueries.json'
    ssh.exec_command(cmd1)
    cmd2 = "mongoexport -h 127.0.0.1:27017 -d devicecommandmap -c" + collection +" -q '"+ '{"device-name":"'+device+'"}' + "' -u " + mongouname + " -p " + mongopwd + " --authenticationDatabase " + '"admin" --pretty -o ~/EMresponse.json'
    ssh.exec_command(cmd2)
    cmd1 = 'sshpass -p "secpod" scp root@192.168.2.17:~/Emqueries.json ~/Emqueriespretty.json'
    cmd2 = 'sshpass -p "secpod" scp root@192.168.2.17:~/EMresponse.json ~/EMresponsepretty.json'
    print("Copying mongo data")
    (os.system(cmd1))
    if (os.system(cmd1)) == 0:
        print("<<<<<< extracted data from Mongodb>>>>>>")
    else:
        print("###### extraction from Mongo failed######")
    (os.system(cmd2))
    if (os.system(cmd2)) == 0:
        print("<<<<<< extracted data from Mongodb>>>>>>")
        Emresponsefile=home + "/EMresponsepretty.json"
        fptr = open(Emresponsefile, 'r')
        json_data = fptr.read()
        json_list = re.findall(r'"command-id":[\s\S]*?"[\s\S]*?"[\s\S]*?', json_data)
        for list1 in json_list:
            list1 = "{" + list1 + "}"
            device_info = json.loads(list1)
            print("Extracted command id in proper json format : ", device_info)
            command_id=(device_info['command-id'])
            cmd3 = "mongoexport -h 127.0.0.1:27017 -d commandcommandsuitemap -c " + collection + " -q '" + '{"command-id":"'+command_id+'"}' + "' -u " + mongouname + " -p " + mongopwd + " --authenticationDatabase " + '"admin" --pretty >> ~/EMfinalresponse.json'
            print("command sent to the mongo db : " , cmd3)
            ssh.exec_command(cmd3)
            cmd3 = 'sshpass -p "secpod" scp root@192.168.2.17:~/EMfinalresponse.json ~/EMFinalresponsepretty.json'
            (os.system(cmd3))
            if (os.system(cmd3)) == 0:
                print("<<<<<< extracted data from Mongo>>>>>>")
            else:
                print("###### extraction from Mongo failed######")
        ssh.close()
    else:
        print("###### extraction from Mongo failed######")

#**************************** TO-SEPARATE EM:IR's FROM EDR:IR's ********************************************************#
def EM():
    print("#************ SEPARATING EM IR's FROM THE EDR IR's **************************")
    Emfinalresponsefile = home + "/EMFinalresponsepretty.json"
    fptr = open(Emfinalresponsefile, 'r')
    withEDRir_json = fptr.read()
    EMIR_json = re.findall(r'{[\s\S]*?"type":[\s\S]*?}[\s\S]*?', withEDRir_json)
    print(EMIR_json)
    for list2 in EMIR_json:
        #import pdb;pdb.set_trace()
        onlyEM = json.loads(list2)
        if onlyEM['type']!='EM':
            continue
        emirpretty = json.dumps(onlyEM, indent=2, sort_keys=True)
        with io.open(home + "/onlyEMpretty.json", "a") as f:
            f.write(emirpretty)
        print(emirpretty)

#****************************** TO COLLECT ONLY IR-NAMES FROM EM:IR-FILE ***********************************************#
def store_dbdata():
    print("#************ COLLECTING ONLY IR NAMES EM***************************")
    try:
        dbfile=home + "/onlyEMpretty.json"
        if dbfile:
            fptr = open(dbfile, 'r')
            content = fptr.read()
            listofnames=re.findall(r'{[\s\S]*?}[\s\S]*?}',content)
            mongo_names=[]
            for list3 in set(listofnames):
                name = json.loads(list3)
                namelist = (name['name'])
                (mongo_names.append(namelist))
            return mongo_names
    except:
        print(" **** THERE IS NO EM FROM MONGODB SO FILE IS NOT CREATED. & IN UI ALSO THIS MUST BE :[' No data available'] ")
        sys.exit(1)

#**********************************TO COMPARE IR's B/W VISER-DATA & MONGO DATA *****************************************#
def compare(list1,list2):
    print("# ************ COMPARING MONGODB IR's AND VISER IR's***************************")
    if not (set(list1)-set(list2)):
        print("match : Comparing viser IR's with mongodb IR's and if any mismatch in viser-IR's -->write viser ir's in else part ")
    else :
        print('non-unique elements in ui_data: ',list(set(list1)-set(list2)))
    if not (set(list2) - set(list1)):
        print("match : Comparing Mongodb IR's with viser IR's and if any mismatch in mongodb-IR's -->write mongodb ir's in else part")
    else:
        print('non-unique elements in mongo_data : ', list(set(list2) - set(list1)))

#******************************************MAIN-STARTS******************************************************************#
if __name__=='__main__':
    payload = {'command': 'login',
               'username': 'prakash@secpod.com',
               'password': 'S3cP0d@'}
    verify=False
    with requests.Session() as s:
        home=s.post('https://192.168.2.16/control.jsp', data=payload, headers={'User-Agent': 'Mozilla/5.0'},allow_redirects=True,verify=False)
        if home.status_code == 200 or home.status_code == 500:
            device=input('Please Enter device name which you want to query the data : ')
            Emurl=s.get("https://192.168.2.16/HostEMdetail.jsp?command=device&hostname="+device)
            html_content=Emurl.text
            #print(html_content)
            #print(sp_table_parser(html_content=html_content,table_id='ioaqueryhost'))
    udata=sp_table_parser(html_content=html_content, table_id='irqueryhost')
    viser_names=[]
    for info in udata:
        vname=info['Name']
        viser_names.append(vname)
    home = expanduser("~")
    ssh = paramiko.SSHClient()
    mongodata()
    EM()
    print('-------> IR collected From The Viser <-----------', viser_names)
    mongo_names=store_dbdata()
    print('-------> IR Collected Fron MongoDB <------------- ',mongo_names)
    compare(viser_names,mongo_names)

#****************************************** CODE - ENDS ****************************************************************#
# NOTE: This will work only user as having the accesss for 1 account