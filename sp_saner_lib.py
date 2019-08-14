#!/usr/bin/python
"""
Saner HTTPS Based Library
"""
###############################################################################
# 
# Authors:
# Veerendra GG <veerendragg@secpod.com>
#
# Date: 20/11/2018
# Date: 21/11/2018 - Implemented Logger Mechanism to log file as well as console by omitting print
# Date: 22/11/2018 - Improved logger setup

# Authors:
# Bharath Kumar K P <bharathkp@secpod.com>
# Date: 11/06/2019 - Implemented post request changes, required to get csrf token to send post requests
# Date: 13/6/2019 - Added two new functions in order to check the header sent and to decide whether to get token or not
# Date: 18/6/2019 - Created a table parser, to fetch the table details from a html page, taking the table-id,
# Date: 24/6/2019 - Create a new function to enable the threat feed of the account, by accepting the session object of the account
# if table-id  is not given, then give the data of the first table in the page
#
# Version 1.0 - Requirement python 3.0
#
# Copyright:
# Copyright (c) 2018 SecPod , http://www.secpod.com
#
###############################################################################

import sys
import requests
import logging.config
import os
import json
from bs4 import BeautifulSoup as bs

#import sp_utils

## Check for proper required python version
req_version = (3, 0)
cur_version = sys.version_info
if cur_version < req_version:
    print("[-] Python 3.x is required to run this framework...")
    sys.exit()

###########################################################################


class SPSanerLibFunctions:
    """
    sp_saner Library
    """

    ###########################################################################

    def _setup_logger(self, logger):
        """
        Setup Logger
        """

        ## Logger filename
        logger_conf_filename = "sp_logger.conf"
        logger_level = logging.DEBUG  # OR Change to "logging.DEBUG" for debug mode

        self.logger = None

        try:
            ## Setup logger
            if not logger:
                if os.path.exists(logger_conf_filename):
                    logging.config.fileConfig(logger_conf_filename)
                    self.logger = logging.getLogger("SPLogger")
                    self.logger.debug("[+] SPLogger logger setup done")
                else:
                    self.logger = logging.basicConfig(level=logger_level)
                    self.logger.debug("[+] Default logger Setup done")
            else:
                self.logger = logger
                self.logger.debug("[+] Reusing existing logger")

        except Exception as msg:
            print("[-] Exception during logger initialisation : ", msg)
            print("[-] Required '%s' proper logger configuration file" % logger_conf_filename)
            sys.exit(0)

    ###########################################################################

    def __init__(self, sp_saner_ip, ssl_verify=True, logger=None):
        """
        Constructor
        """

        ## Setup Logger
        self._setup_logger(logger)

        if not sp_saner_ip:
            self.logger.info("[-] Saner IP is not mentioned.")
            sys.exit()

        self.user_agent = "Mozilla/5.0"

        self.headers = {'User-Agent': 'Mozilla/5.0'}

        ## Set SSL Versification should be done or not ?
        if ssl_verify not in [True, False]:
            self.ssl_verify = True
        else:
            self.ssl_verify = ssl_verify

        ## Supress SSL warning
        if not self.ssl_verify:
            ## Disable warning message "InsecureRequestWarning: Unverified HTTPS request is being made"
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

        self.logger.debug("[+] SSL Verify : %s " % self.ssl_verify)

        ## Create Utils Class Object
        #self.sp_utils = sp_utils.SPUtils(self.logger)

        ## sp_saner Session Object
        self.sp_saner_session_obj = None

        self.sp_saner_base_url = "https://%s" % sp_saner_ip.strip()

        self.logger.debug("[+] Saner base URL : %s" % self.sp_saner_base_url)

    ###########################################################################

    def __del__(self):
        """
        Destructor
        """

        self.logger.debug("[+] Inside Saner library function destructor")

        ## Logout
        if self.sp_saner_session_obj:
            self.sp_saner_logout()

    ###########################################################################

    def sp_saner_login(self, username, passwd):
        """
        Login to Saner using given auth and return session object
        """

        self.logger.debug("[+] Saner login with user : %s" % username)

        if not (username and passwd):
            self.logger.info("ERROR: Please verify URL=%s, User=%s and "
                             "Pass=%s" % (self.sp_saner_base_url, username, passwd))
            return False

        username = username.strip()
        login_url = self.sp_saner_base_url + "/control.jsp"

        post_data = {
                        "command": "login",
                        "username": username,
                        "password": passwd
        }

        self.logger.debug("[+] Creating Saner login session")

        self.sp_saner_session_obj = requests.Session()     
        response = self.sp_saner_session_obj.post(login_url, data=post_data,
                                                  headers=self.headers,
                                                  verify=self.ssl_verify,
                                                  allow_redirects=True)

        if type(response.content) != str:
            content = response.content.decode()
        else:
            content = response.content

        if "Limit on number of users reached." in content:
            self.logger.info("[-] Login Failed: Limit on number of users reached.")
            ## clear session and cookies
            self.sp_saner_session_obj.close()
            self.sp_saner_session_obj = None
            return None

        if ">Sign out<" not in content:
            self.logger.info("[-] User (%s) Login Failed, Please verify username and pasword" % username)
            ## clear session and cookies
            self.sp_saner_session_obj.close()
            self.sp_saner_session_obj = None
            return None

        self.logger.info("[+] User (%s) Logged in Successfully" % username)

        return self.sp_saner_session_obj

    ###########################################################################

    def sp_saner_logout(self):
        """
        sp_saner logout function
        """

        self.logger.debug("[+] Logging out and clearing session")

        logout_success = False

        if not self.sp_saner_session_obj:
            self.logger.info("[-] No Session exists for logout.")
            return logout_success

        logout_url = self.sp_saner_base_url + "/control.jsp?command=logout&_msp@@Name=true"

        self.logger.debug("[+] Calling Saner logout : %s " % logout_url)

        ## Call logout page
        response = self.sp_saner_session_obj.get(logout_url, verify=self.ssl_verify, headers=self.headers)

        if type(response.content) != str:
            content = response.content.decode()
        else:
            content = response.content

        if "User logged out" in content:
            self.logger.info("[+] User Logged out Successfully")
            logout_success = True

            ## clear session and cookies
            self.sp_saner_session_obj.close()
            self.sp_saner_session_obj = None
        else:
            self.logger.info("[-] User Logout Failed")

        return logout_success

    ###########################################################################

    def sp_saner_get_mve_basic_info_by_mve_id(self, mve_id):

        basic_mve_info = ""

        if not mve_id:
            return basic_mve_info

        mve_url = "/modules/VM/VMcontrol.jsp?command=getformatteddocumentformve&mveId=" + mve_id

        response = self.sp_saner_get_page_info(mve_url)
        if not response:
            self.logger.info("[-] Failed to get basic mve info for mve id : %s " % mve_url)
            self.logger.debug("[-] Response : %s " % response)
            return basic_mve_info

        self.logger.debug("[*] Response Status code : %s", response['status_code'])

        ## Return page content
        basic_mve_info = response['content']

        return basic_mve_info

    ###########################################################################

    def sp_saner_get_session_headers(self):
        token_res = self.sp_saner_get_page_info_afterheadercheck(url="/JavaScriptServlet",
                                                                          headers={"FETCH-CSRF-TOKEN": "1"},
                                                                          req_type="POST")
        #print(token_res)

        token = token_res['content'].split(':')
        #print('Token : %s' % token)

        h2 = {token[0]: token[1]}
        h12 = {"X-Requested-With": "XMLHttpRequest", token[0]: token[1]}
        #print("values of h12 in first function is", h12)
        return h12

    def sp_saner_get_page_info(self, url="", sp_saner_session_obj=None,
                               req_type="GET", headers=None,
                               post_data=None):

        #print("we reached here --------------------")
        try:
            #print("we reached here --------------------try")
            print(type(headers))
            #abc = isinstance(headers, None)
            if headers is not None:
                if 'SANER-TOKEN' in headers():
                    #print("---------:::::::::******", headers)
                    self.sp_saner_get_page_info_afterheadercheck(self, url, sp_saner_session_obj, req_type, headers, post_data)
                    #print("**********************************")
                else:
                    h12 = self.sp_saner_get_session_headers()
                    #print("values of h12 in calling function is", h12)

                    response = self.sp_saner_get_page_info_afterheadercheck(url,
                                                                            headers=h12,
                                                                            req_type="POST", post_data=post_data)
                    #print(response)
                    #print("we reached here --------------------2")
                    return response
            else:
                #print("we reached the else part successfully")
                h12 = self.sp_saner_get_session_headers()
                #print("values of h12 in calling function is", h12)

                response = self.sp_saner_get_page_info_afterheadercheck(url,
                                                                headers=h12,
                                                                req_type="POST", post_data=post_data)
                #print(response)
                #print("we reached here --------------------2")
                return response
        except Exception as msg:
            self.logger.info("[-] ERROR: While Send Receive Request : %s " % url)
            self.logger.debug("[-] EXCEPTION: Message : %s " % msg)
            print("[-] EXCEPTION: Message : %s " % msg)
            return {}

    def sp_saner_get_page_info_afterheadercheck(self, url="", sp_saner_session_obj=None,
                               req_type="GET", headers=None,
                               post_data=None):
        """
        Returns dictonay with headers, content, status_code, ok along
        with response object
        """

        try:

            self.logger.debug("[+] Getting Saner info for a given URL")

            response_dict = {}
            response = {}

            if not url:
                self.logger.info("[-] You missed to pass URL.")
                return response_dict

            url = self.sp_saner_base_url + url

            self.logger.debug("[+] Getting info Saner info from URL : %s " % url)

            if not sp_saner_session_obj:
                if self.sp_saner_session_obj:
                    sp_saner_session_obj = self.sp_saner_session_obj
                else:
                    self.logger.info("[-] No session established.")
                    return response_dict

            if req_type.upper() not in ["GET", "POST"]:
                self.logger.info("[-] Invalid request type : %s " % req_type)
                return response_dict

            ## Add user agent as Mozilla to avoid web sites blocking python agent request.
            if not headers:
                headers = self.headers

            ## Several website block, if user agent if python.
            elif 'User-Agent' not in headers.keys():
                headers['User-Agent'] = self.headers['User-Agent']

            if not post_data:
                post_data = {}

            self.logger.debug("[*] Sending '%s' request to (%s) URL" % (req_type.upper(), url))

            self.logger.debug("[*] Headers : %s " % headers)


            try:
                #print("-------------godfklsjdklfdk------", headers)

                ## Send GET request
                if req_type.upper() == "GET":
                    response = sp_saner_session_obj.get(url, headers=headers, verify=self.ssl_verify)

                ## Send POST request
                if req_type.upper() == "POST":
                    if post_data:
                        self.logger.debug("[*] Post Data : %s " % post_data)
                        response = sp_saner_session_obj.post(url, headers=headers,
                                                             data=post_data,
                                                             verify=self.ssl_verify,
                                                             allow_redirects=True)
                    else:
                        response = sp_saner_session_obj.post(url, headers=headers,
                                                             verify=self.ssl_verify,
                                                             allow_redirects=True)

            except sp_saner_session_obj.exceptions.ConnectionError:
                self.logger.info("[-] Connection refused for (%s) URL " % url)

            if type(response.content) != str:
                content = response.content.decode()
            else:
                content = response.content

            self.logger.debug("[+] Formatting response as per need")

            ## Send dict with specific content
            if response and response.status_code:
                response_dict.update({"headers": response.headers,
                                      "content": content,
                                      "status_code": response.status_code,
                                      "ok": response.ok,
                                      "res_object": response})
            else:
                self.logger.info("[-] ERROR: Didn't get proper response status code : %s " % response)
            #print("---------------returning safely")
            return response_dict

        except Exception as msg:
            self.logger.info("[-] ERROR: While Send Receive Request : %s " % url)
            self.logger.debug("[-] EXCEPTION: Message : %s " % msg)
            return {}

    ###########################################################################

    def sp_table_parser(self, html_content, table_id=None):
        #print("\n entered the parser")
        try:
            #convert the html content into a proper format to parse
            soup = bs(html_content, 'html.parser')
            #print("\n entered the try block after soup command")

            #check whether the table_id is present in the calling function and fetch the table based on id, else fetch the first table
            if table_id is not None:
                table = soup.find('table', id=table_id)
            else:
                table = soup.find('table')

            #print(table)
            #Get the table headers in the table fetched
            headings = [th.get_text().strip() for th in table.find("tr").find_all("th")]
            datasets = []

            #Form a list of dictionaries, by matching the table headers with appropriate data belonging to that from the table
            for row in table.find_all("tr")[1:]:
                dataset = dict(zip(headings, (td.get_text() for td in row.find_all("td"))))
                datasets.append(dataset)
            #print(datasets)
            return datasets
        except Exception as msg:
            self.logger.info("[-] ERROR: While fetching tables ")
            self.logger.debug("[-] EXCEPTION: Message : %s " % msg)
            return {}

      #################################################################################
    def enable_threat_feed(self, sp_saner_session_obj=None):
        """
        Reading URLs from a file
        """

        f = open('results/url_status.txt', 'a')
        url_now = "/modules/EDR/EDRcontrol.jsp?command=enablefeed&feedName=SecPod Default"
        print("Checking it now in the eablethreatfeed \n\n\n")
        try:
            response = self.sp_saner_get_page_info(url_now, sp_saner_session_obj)
            print("Successfully got threatfeed \n\n\n")
            print(response)

            ## Checking if response data
            if not response:
                self.logger.debug("[*] Unable to contact  the URL : %s " % url_now)

            if response["status_code"] == 200:
                f.write("%s:Ok: %s\n" % (response["status_code"], url_now))
            else:
                f.write("%s:Check: %s\n" % (response["status_code"], url_now))
            return response

        except Exception as msg:
            f.write("500:Fail: %s\n" % url_now)
        f.close()
