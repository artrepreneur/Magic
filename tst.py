import sys
import time
import subprocess
import platform
import os

'''
def ga():
    wallet_db = ''
    cmd = "touch .magic.cfg"
    result, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print(result, err) 
    if not err:
        print('res:', result)   

ga()


import time
from subprocess import Popen, PIPE, STDOUT
p = Popen("/usr/bin/google-authenticator", stdout=PIPE, stdin=PIPE, stderr=PIPE).communicate("n\nn")[0]
p = p.split("\n")
arr = p[6].replace(" ", "") + ',' + p[7].replace(" ", "")  + ',' + p[8].replace(" ", "")  + ',' + p[9].replace(" ", "")  + ',' + p[10].replace(" ", "")
out = p[3].split(":")[1].replace(" ", "") + '|' + arr + '|' + p[4].split("is")[1].replace(" ", "") 
print(out, "")

'''

def ping(host):
    res = False
    ping_param = "-n 1" if platform.system() == "Windows" else "-c 1"
    result = os.popen("ping " + ping_param + " " + host).read()
    if "ttl=" in str(result):
        res = True

    return res

print(ping("magicwallet.local"))