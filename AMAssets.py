######################################################################################################

# Author: PRAKASH S S <prakash@secpod.com>
# Date: 05/07/2019
# Requirement python 3.6
# verify EM-Responses(IR) there in host details page with mongodb
# should import sp_saner_lib.py as depenency file

#######################################################################################################
import datetime
from venv import logger
import sp_saner_lib
import os,re,sys
from collections import OrderedDict
from os.path import expanduser
import json
import io
import paramiko
import requests
from bs4 import BeautifulSoup as bs
from cryptography.hazmat.primitives.serialization import ssh
from EmirSingleAccountAccess import sp_table_parser

#######################################################################################################
class AM:

    def LOGIN(self):
        ancor_ip = "192.168.2.16"
        saner_username = "sharath@secpod.com"
        saner_passwd = "S3cP0d@"
        ssl_verify = False
        saner_lib_obj = sp_saner_lib.SPSanerLibFunctions(ancor_ip, ssl_verify, logger)
        login_success = saner_lib_obj.sp_saner_login(saner_username, saner_passwd)
        if not login_success:
            print(str(datetime.datetime.now()) + " : Login Failed" + "\n")
            return
        else:
            print("Login Successful")
            self.select_account(saner_lib_obj, 'sp1ihe70djarj0f')
            self.AM_Publishers(saner_lib_obj)

            '''
            print("********************************************************")
            print("** COLLECT AM_SOFTWARE ASSETS LIST **")
            self.AM_softwareAssets(saner_lib_obj)
            print("********************************************************")
            print("** COLLECT AM_RARELY_USED_APPLICATION LIST **")
            self.AM_rarelyusedAssets(saner_lib_obj)
            print("********************************************************")
            print("** COLLECT BLACKLISTED_ASSETS LIST **")
            self.AM_BlacklistedAssets(saner_lib_obj)
            print("********************************************************")
            print("** COLLECT AM_OUTDATED_ASSETS LIST**")
            self.AM_OutdatedAssets(saner_lib_obj)
            print("********************************************************")
            print("** COLLECT AM_Devices LIST**")
            self.AM_Devices(saner_lib_obj)
            print("********************************************************")
            print("** COLLECT DEVICE DISTRIBUTION LIST ** ")
            self.AM_Devices_Distribution(saner_lib_obj)
            print("********************************************************")
            print(" ** COLLECT OSlicense LIST  ** ")
            self.OSlicense(saner_lib_obj)
            print("********************************************************")
            print(" ** COLLECT APPlicense LIST  ** ")
            self.APPlicense(saner_lib_obj)
            print("********************************************************")
            print(" ** COLLECT HARDWARE_license LIST  ** ")
            self.HDlicense(saner_lib_obj)
            print("********************************************************")
            print(" ** COLLECT HARDWARE ASSETS _ DEVICE MANIFATURER DETAILS  ** ")
            self.HD_DeviceManufacturerBarChart(saner_lib_obj)
            print("********************************************************")
            print(" ** COLLECT HARDWARE ASSETS _ DeviceTypePieChart DETAILS  ** ")
            self.HD_DeviceTypePieChart(saner_lib_obj)
            print("********************************************************")
            print(" ** COMPARISION IS GOING ON BETWEEN NEW_DATA AND BASELINE_DATA ** ")
            print("********************************************************")
            self.compare()
            print(" ** COMPARISION IS ** DONE ** BETWEEN NEW_DATA AND BASELINE_DATA ** ")
            print("********************************************************")
            print("****************NEWLY CREATED TEMPORARY FILE DELETION ONGOING ******************************")
            if os.path.exists("AM_SOFTWARE_ASSETS_DATA.txt"):
                os.remove(str("AM_SOFTWARE_ASSETS_DATA.txt"))
            else:
                print("The file *---AM_SOFTWARE_ASSETS_DATA----*does not exist")

            if os.path.exists("RARELYUSED_ASSETS_DATA.txt"):
                os.remove(str("RARELYUSED_ASSETS_DATA.txt"))
            else:
                print("The file *------RARELYUSED_ASSETS_DATA.txt-----* does not exist")

            if os.path.exists("Blacklisted_Assets_DATA.txt"):
                os.remove(str("Blacklisted_Assets_DATA.txt"))
            else:
                print("The file *------Blacklisted_Assets_DATA.txt-----* does not exist")

            if os.path.exists("Outdated_Assets_DATA.txt"):
                os.remove(str("Outdated_Assets_DATA.txt"))
            else:
                print("The file *------Outdated_Assets_DATA.txt-----* does not exist")

            if os.path.exists("AM_Device_DATA.txt"):
                os.remove(str("AM_Device_DATA.txt"))
            else:
                print("The file *------AM_Device_DATA.txt-----* does not exist")

            if os.path.exists("AM_DEVICE_DESTIBULTION_FAMILY.txt"):
                os.remove(str("AM_DEVICE_DESTIBULTION_FAMILY.txt"))
            else:
                print("The file *------AM_DEVICE_DESTIBULTION_FAMILY.txt-----* does not exist")

            if os.path.exists("AM_OSlicense_DATA.txt"):
                os.remove(str("AM_OSlicense_DATA.txt"))
            else:
                print("The file *------AM_OSlicense_DATA.txt-----* does not exist")

            if os.path.exists("AM_APPlicense_DATA.txt"):
                os.remove(str("AM_APPlicense_DATA.txt"))
            else:
                print("The file *------AM_APPlicense_DATA.txt-----* does not exist")

            if os.path.exists("AM_HDlicense_DATA.txt"):
                os.remove(str("AM_HDlicense_DATA.txt"))
            else:
                print("The file *------AM_HDlicense_DATA.txt-----* does not exist")

            if os.path.exists("HD_DeviceManufacturer_DATA.txt"):
                os.remove(str("HD_DeviceManufacturer_DATA.txt"))
            else:
                print("The file *------HD_DeviceManufacturer_DATA.txt-----* does not exist")

            if os.path.exists("HD_DeviceTypeChart_DATA.txt"):
                os.remove(str("HD_DeviceTypeChart_DATA.txt"))
            else:
                print("The file *------HD_DeviceTypeChart_DATA.txt-----* does not exist")

            print("**************** TEMPORARY FILE's DELETION DONE ******************************")
            
            '''
#######################################################################################################
    def select_account(self,saner_lib_obj, account_id):
        params = {"forAccount": account_id}
        url = "/control.jsp?command=setAndOpenAccount"
        try:
            response = saner_lib_obj.sp_saner_get_page_info(url="/control.jsp?command=setAndOpenAccount",req_type="POST",post_data=params)
            if not response:
                logger.debug("[*] Unable to select the account : %s ", params)
            if response["status_code"] == 200:
                print("*** account Selection Was Successful ***")
                #device = input('Please Enter device name which you want to query the data : ')
            else:
                print("*** account Selection Was UN-Successful  ****** ")
        except Exception as msg:
            print("Exception Accoured : Something Went Wrong ---------------------------")
#######################################################################################################
    def sp_table_parser(self, html_content, table_id=None):
        # print('#***********GET ALL EM RELATED DETAILS FROM UI*******************#')
        try:
            soup = bs(html_content, 'html.parser')
            if table_id is not None:
                table = soup.find('table', id=table_id)
            else:
                table = soup.find('table')
            headings = [th.get_text().strip()
                        for th in table.find("thead").find_all("th")]
            ui_data = []
            for row in table.find_all("tr"):
                dataset = dict(zip(headings, (td.get_text() for td in row.find_all("td"))))
                ui_data.append(dataset)
            return ui_data

        except Exception as msg:
            print(msg)
            return

#######################################################################################################
    def AM_softwareAssets(self,saner_lib_obj):
        AM_SOFTWARE_ASSETS = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMcontrol.jsp?command=getallsoftwareassetswithscope&limit=-1&groups=null&publishers=null")
        AM_SOFTWARE_ASSETS=str(AM_SOFTWARE_ASSETS)
        AM_SOFTWARE_ASSETS_html_content=AM_SOFTWARE_ASSETS
        AM_SOFTWARE_ASSETS_DATA = self.sp_table_parser(html_content=AM_SOFTWARE_ASSETS_html_content, table_id='_assetInfoTable')
        with io.open("AM_SOFTWARE_ASSETS_DATA.txt", "w") as f:
            f.write(str(AM_SOFTWARE_ASSETS_DATA))
        AM_SOFTWARE_ASSETS_NAMES = []
        for info in AM_SOFTWARE_ASSETS_DATA:
            vname = info['Name']
            AM_SOFTWARE_ASSETS_NAMES.append(vname)
        print("SOFTWARE ASSETS NAMES COLLECTED FROM UI : ", AM_SOFTWARE_ASSETS_NAMES)
        print("SOFTWARE ASSETS COUNT COLLECTED FROM UI : ", len(AM_SOFTWARE_ASSETS_NAMES))

#######################################################################################################
    def AM_rarelyusedAssets(self,saner_lib_obj):
        RARELYUSED_ASSETS = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMcontrol.jsp?command=getrarelyusedassets&limit")
        RARELYUSED_ASSETS=str(RARELYUSED_ASSETS)
        RARELYUSED_ASSETS_html_content= RARELYUSED_ASSETS
        RARELYUSED_ASSETS_DATA = self.sp_table_parser(html_content=RARELYUSED_ASSETS_html_content, table_id='_ruAssetsTable')
        with io.open("RARELYUSED_ASSETS_DATA.txt", "w") as f:
            f.write(str(RARELYUSED_ASSETS_DATA))
        RARELYUSED_ASSETS_NAMES = []
        for info in  RARELYUSED_ASSETS_DATA:
            vname = info['Name']
            RARELYUSED_ASSETS_NAMES.append(vname)
        print("RARELYUSED_ASSETS_NAMES COLLECTED FROM UI : ", RARELYUSED_ASSETS_NAMES)
        print("RARELYUSED_ASSETS_NAMES COUNT COLLECTED FROM UI : ", len(RARELYUSED_ASSETS_NAMES))

 #######################################################################################################
    def AM_BlacklistedAssets(self, saner_lib_obj):
        Blacklisted_Assets = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMcontrol.jsp?command=getblacklistedassets&limit")
        Blacklisted_Assets = str(Blacklisted_Assets)
        Blacklisted_Assets_html_content = Blacklisted_Assets
        Blacklisted_Assets_DATA = self.sp_table_parser(html_content=Blacklisted_Assets_html_content,table_id='_blackListedAssetTable')
        with io.open("Blacklisted_Assets_DATA.txt", "w") as f:
            f.write(str(Blacklisted_Assets_DATA))
        Blacklisted_Assets_NAMES = []
        for info in Blacklisted_Assets_DATA:
            vname = info['Name']
            Blacklisted_Assets_NAMES.append(vname)
        print("Blacklisted_Assets_NAMES COLLECTED FROM UI : ", Blacklisted_Assets_NAMES)
        print("Blacklisted_Assets COUNT COLLECTED FROM UI : ", len(Blacklisted_Assets_NAMES))

#######################################################################################################

    def AM_OutdatedAssets(self, saner_lib_obj):
        Outdated_Assets = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMcontrol.jsp?command=getoutdatedapplications&limit")
        Outdated_Assets = str(Outdated_Assets)
        Outdated_Assets_html_content = Outdated_Assets
        Outdated_Assets_DATA = self.sp_table_parser(html_content=Outdated_Assets_html_content,table_id='_outdatedDeviceTable')
        with io.open("Outdated_Assets_DATA.txt", "w") as f:
            f.write(str(Outdated_Assets_DATA))
        Outdated_Assets_NAMES = []
        for info in Outdated_Assets_DATA:
            vname = info['Application']
            Outdated_Assets_NAMES.append(vname)
        print("OutdatedAssets FROM UI : ", Outdated_Assets_NAMES)
        print("OutdatedAssets COUNT COLLECTED FROM UI : ", len(Outdated_Assets_NAMES))

#######################################################################################################
    def AM_Devices(self, saner_lib_obj):
        AM_Device = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMcontrol.jsp?command=getdeviceinfo&limit")
        AM_Device = str(AM_Device)
        AM_Device_html_content = AM_Device
        AM_Device_DATA = self.sp_table_parser(html_content=AM_Device_html_content,table_id='_deviceInfoTable')
        with io.open("AM_Device_DATA.txt", "w") as f:
            f.write(str(AM_Device_DATA))
        AM_Device_NAMES = []
        for info in AM_Device_DATA:
            vname = info['Host Name']
            AM_Device_NAMES.append(vname)
        print("Devices NAMES COLLECTED FROM UI : ", AM_Device_NAMES)
        print("Devices COUNT COLLECTED FROM UI : ", len(AM_Device_NAMES))

#######################################################################################################
    def AM_Devices_Distribution(self, saner_lib_obj):
        AM_Device_Distribution = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMcontrol.jsp?command=getdevicesbasedonosfamily")
        AM_Device_Distribution = str(AM_Device_Distribution)
        AM_Device_Distribution_html_content = AM_Device_Distribution
        AM_Device_Distribution_DATA=re.findall(r'{[\s]*?"family":[\s\S]*?}[\s\S]*?][\s\s]*?}',AM_Device_Distribution_html_content)
        with io.open("AM_DEVICE_DESTIBULTION_FAMILY.txt","w")as f:
            f.write(str(AM_Device_Distribution_DATA))
        print("AM_DEVICE_DESTIBULTION_FAMILY COLLECTED FROM UI : ", AM_Device_Distribution_DATA)
        print("AM_DEVICE_DESTIBULTION_FAMILY COUNT COLLECTED FROM UI : ", len(AM_Device_Distribution_DATA))

#######################################################################################################
    def OSlicense(self, saner_lib_obj):
        AM_OSlicense = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMmanageAssets.jsp?loadOSLicenses=loadOSLicenses&limit")
        AM_OSlicense = str(AM_OSlicense)
        AM_OSlicense_html_content = AM_OSlicense
        AM_OSlicense_DATA = self.sp_table_parser(html_content=AM_OSlicense_html_content,table_id='amLicense')
        with io.open("AM_OSlicense_DATA.txt", "w") as f:
            f.write(str(AM_OSlicense_DATA))
        AM_OSlicense_NAMES = []
        for info in AM_OSlicense_DATA:
            vname = info['OS Name']
            AM_OSlicense_NAMES.append(vname)
        print("OSlicense_NAMES COLLECTED FROM UI : ", AM_OSlicense_NAMES)
        print("OSlicense_NAMES COUNT COLLECTED FROM UI : ", len(AM_OSlicense_NAMES))

#######################################################################################################
    def APPlicense(self, saner_lib_obj):
        AM_APPlicense = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMmanageAssets.jsp?loadApplicationLicenses=loadApplicationLicenses&limit")
        AM_APPlicense = str(AM_APPlicense)
        AM_APPlicense_html_content = AM_APPlicense
        AM_APPlicense_DATA = self.sp_table_parser(html_content=AM_APPlicense_html_content,table_id='amLicense')
        with io.open("AM_APPlicense_DATA.txt", "w") as f:
            f.write(str(AM_APPlicense_DATA))
        AM_APPlicense_NAMES = []
        for info in AM_APPlicense_DATA:
            vname = info['Application Name']
            AM_APPlicense_NAMES.append(vname)
        print("APPlicense NAMES COLLECTED FROM UI : ", AM_APPlicense_NAMES)
        print("APPlicense COUNT COLLECTED FROM UI : ", len(AM_APPlicense_NAMES))

#######################################################################################################
    def HDlicense(self, saner_lib_obj):
        AM_HDlicense = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMmanageAssets.jsp?loadHardwareLicenses=loadHarwareLicenses&limit")
        AM_HDlicense = str(AM_HDlicense)
        AM_HDlicense_html_content = AM_HDlicense
        AM_HDlicense_DATA = self.sp_table_parser(html_content=AM_HDlicense_html_content,table_id='amLicense')
        with io.open("AM_HDlicense_DATA.txt", "w") as f:
            f.write(str(AM_HDlicense_DATA))
        AM_HDlicense_NAMES = []
        for info in AM_HDlicense_DATA:
            vname = info['Manufacture']
            AM_HDlicense_NAMES.append(vname)
        print("HARDWARE_LICENSE COLLECTED FROM UI : ", AM_HDlicense_NAMES)
        print("HARDWARE LICENSE COUNT COLLECTED FROM UI : ", len(AM_HDlicense_NAMES))

#######################################################################################################
    def HD_DeviceManufacturerBarChart(self, saner_lib_obj):
        HD_DeviceManufacturer = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMcontrol.jsp?command=loadDeviceManufacturerBarChart")
        HD_DeviceManufacturer = str(HD_DeviceManufacturer)
        HD_DeviceManufacturer_html_content = HD_DeviceManufacturer
        HD_DeviceManufacturer_DATA=re.findall(r"content'[\s]*?:[\s]*?'Manufacturer[\s\S]*?\|\|\d+",HD_DeviceManufacturer_html_content)
        with io.open("HD_DeviceManufacturer_DATA.txt","w")as f:
            f.write(str(HD_DeviceManufacturer_DATA))
        print("HD_DeviceManufacturer_DATA COLLECTED FROM UI : ", HD_DeviceManufacturer_DATA)

#######################################################################################################
    def HD_DeviceTypePieChart(self, saner_lib_obj):
        HD_DeviceTypeChart = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMcontrol.jsp?command=loadDeviceTypePieChart")
        HD_DeviceTypeChart = str(HD_DeviceTypeChart)
        HD_DeviceTypeChart_html_content = HD_DeviceTypeChart
        HD_DeviceTypeChart_DATA = re.findall(r"'content'[\s\S]*?:[\s\S]*?\|\|\d+",HD_DeviceTypeChart_html_content)
        with io.open("HD_DeviceTypeChart_DATA.txt", "w")as f:
            f.write(str(HD_DeviceTypeChart_DATA))
        print("HD_DeviceTypePieChart_DATA COLLECTED FROM UI : ", HD_DeviceTypeChart_DATA)

#######################################################################################################
    def AM_Publishers(self, saner_lib_obj):
        AM_Publisher = saner_lib_obj.sp_saner_get_page_info(url="/modules/AM/AMcontrol.jsp?command=getvendorbasedassets&limit")
        print(AM_Publisher)
        AM_Publisher = str(AM_Publisher)
        AM_Publisher_html_content = AM_Publisher
        print("heyyyyyy : ", AM_Publisher_html_content)
        AM_Publisher_DATA = re.findall(r"'content'[\s\S]*?:[\s\S]*?\|\|\d+", AM_Publisher_html_content)
        with io.open("AM_Publisher_BASELINE_DATA.txt", "w")as f:
            f.write(str(AM_Publisher_DATA))
        print("AM_Publisher_DATA COLLECTED FROM UI : ", AM_Publisher_DATA)

#######################################################################################################
    def compare(self):
        l1 = ['AM_APPlicense_DATA.txt', 'AM_Device_DATA.txt','AM_DEVICE_DESTIBULTION_FAMILY.txt','AM_HDlicense_DATA.txt', 'AM_OSlicense_DATA.txt', 'AM_SOFTWARE_ASSETS_DATA.txt', 'Blacklisted_Assets_DATA.txt', 'Outdated_Assets_DATA.txt', 'RARELYUSED_ASSETS_DATA.txt','HD_DeviceManufacturer_DATA.txt','HD_DeviceTypeChart_DATA.txt']
        l2 = ['AM_APPlicense_BASELINE.txt', 'AM_Device_BASELINE.txt','AM_DEVICE_DESTIBULTION_FAMILY_BASELINE.txt', 'AM_HDlicense_BASELINE.txt', 'AM_OSlicense_BASELINE.txt', 'AM_SOFTWARE_ASSETSBASELINE.txt', 'Blacklisted_AssetsBASELINE.txt', 'Outdated_Assets_BASELINE.txt', 'RARELYUSED_ASSETSBASELINE.txt','HD_DeviceManufacturer_BASELINE_DATA.txt','HD_DeviceTypeChart_BASELINE_DATA.txt']
        for (a, b) in zip(l1, l2):
            print(a, b)
            f1 = open(a, "r")
            f2 = open(b, "r")
            count = 0
            for line1 in f1:
                for line2 in f2:
                    if line1 == line2:
                        pass
                    else:

                        print("######", a, "is NOT matching###### \n ", line1 + line2)
                        count = count + 1
                    break
            if count == 0:
                print("PASS :-------- ", a , " MATCHES WITH ", b ," ---------")
                print("************************************************************")
            f1.close()
            f2.close()

#######################################################################################################
if __name__=='__main__':
    am=AM()
    am.LOGIN()
    print("***** EXECUTION IS OVER PLEASE VERIFY THE OUTPUT.. ******")
#######################################################################################################
