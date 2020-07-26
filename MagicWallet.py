# note hashin scp and paramiko to both requirements.txt
import paramiko
from scp import SCPClient

# Make sure PKTWallet.py have these integrated, via hashin
import os.path 
from os import path

import time
import subprocess
import sys

# Add all of these
CONNECTED = False
LOCAL_WALLET_PATH = "." # This is set by get_wallet_db on integration 
REMOTE_WALLET_PATH = "Wallets" # This is static 
WALLET_NAME = "wallet.db"
WALLET_NAME_E = "wallet.db.gpg"
MAGIC_WALLET = True


class connection:
    host = "raspberrypi.local"
    port = 22
    username = "magic"
    password = "redman3" #redman2

def connect_magic_wllt(conn):
    global CONNECTED, passphrase
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(conn.host, conn.port, conn.username, conn.password)
        print("Connected successfully!", ssh)
        passphrase = conn.password
        CONNECTED = True

    except Exception as e:
        print("Couldn\'t connect, connection error:", e)
        CONNECTED = False
        #print("Failed to connect to device")
        passphrase = input("Enter your password:")
        passphrase = passphrase.strip()
        conn.password = passphrase
        print('CONN PWD:', conn.password)
        ssh = connect_magic_wllt(conn)
    
    return ssh

def request_frm_bck_up():
    retrieve = input("Do you wish to retrieve your wallet from your magic stick? (y/n)")
    if retrieve == 'y':
        return True
    else: 
        return False

def get_magic_wllt(ssh, passphrase):
        
    if request_frm_bck_up():
    
        command = "gpg --batch --passphrase passphrase --decrypt "+ WALLET_NAME_E +" | cat " + WALLET_NAME

        try:
            #stdin, stdout, stderr = ssh.exec_command(command)
            #lines = stdout.readlines()
            #if lines:
            #    print('lines:',lines)

            scp = SCPClient(ssh.get_transport())
            scp.get(REMOTE_WALLET_PATH + "/" + WALLET_NAME, LOCAL_WALLET_PATH)
            scp.close()
            result = "Successfully retrieved wallet from device."

        except Exception as e:
            print("Couldn\'t connect, connection error:", e)
            result = "Failed to retrieve wallet from device."
            sys.exit() # Quit
        
    ssh.close()
    print(result) 
    return result 

def progress(filename, size, sent):
    sys.stdout.write("%s's progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )

def progress4(filename, size, sent, peername):
    sys.stdout.write("(%s:%s) %s's progress: %.2f%%   \r" % (peername[0], peername[1], filename, float(sent)/float(size)*100) )

def put_magic_wllt(ssh, passphrase):
    print("LOCAL_WALLET_PATH", LOCAL_WALLET_PATH)

    # Check if local wallet exists
    if path.exists(LOCAL_WALLET_PATH): # replace with get_wallet_db()
        command = "gpg -c --batch --no-symkey-cache --compress-algo none --passphrase "+ passphrase + " " + REMOTE_WALLET_PATH + "/" + WALLET_NAME

        try:
            scp = SCPClient(ssh.get_transport(), progress4=progress4)
            scp.put(f"{get_wallet_db()}", REMOTE_WALLET_PATH)

            # Encrypt it
            #stdin, stdout, stderr = ssh.exec_command(command)
            #lines = stdout.readlines()
            #if lines:
            #    print('Lines:',lines)
            
            result = "Copied local wallet to device\n"

        except Exception as e:
            print("Couldn\'t connect, connection error:", e)
            result = "Failed to copy wallet to device"
    else:
        result = "Couldn\'t find local wallet.db file, exiting..."        
    scp.close()    
    ssh.close()
    print(result)
    return result

def first_connect(ssh):
    cmd = "ls -al "+ REMOTE_WALLET_PATH +"/"+ WALLET_NAME +">> /dev/null 2>&1 && echo yes || echo no | tr -d '\n'"
    print('CMD', cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    lines = stdout.readlines()
    print('LS result:', lines)

    if len(lines) > 1: 
        for line in lines:
            if "Too many logins" in line:
                print('Too many logins on magic stick. If you are not logged into your stick through ssh then your wallet has been compromised.')
                sys.exit()
    else:
        line = lines[0]
        print('LIne', line)
        if line == 'yes':
            print('Wallet found on magic stick.')
            print('Lines:',lines)
            return False
        elif line == 'no':
            print('No wallet found on magic stick.')
            return True


def get_wallet_db():
    wallet_db = ''
    get_db_cmd = "bin/getwalletdb"
    get_db_result = (subprocess.Popen(get_db_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]).decode("utf-8")
    print('get_db_result:', get_db_result) 
    if get_db_result.strip() != "Path not found":    
        wallet_db = get_db_result.strip('\n')+'/wallet.db'
        print('Wallet location:', wallet_db)
    else:
        wallet_db = ''
    print('wallet_db', wallet_db)        
    return wallet_db   

def get_passphrase():
    passphrase = input('Enter new wallet passphrase:')
    passphrase = passphrase.strip()
    return passphrase

def set_new_passphrase(passphrase, ssh):
    command = "echo \'magic:"+passphrase+"\' | sudo chpasswd"
    stdin, stdout, stderr = ssh.exec_command(command)
    lines = stdout.readlines()
    if lines:
        print('Lines:',lines)

# ----- MAIN -----
if __name__ == "__main__":

    global passphrase
    LOCAL_WALLET_PATH = get_wallet_db()

    # On Startup
    conn = connection()
    ssh = connect_magic_wllt(conn)

    print('MW', MAGIC_WALLET, 'CONNECTED', CONNECTED, 'ssh', ssh)
    if MAGIC_WALLET and CONNECTED and ssh:

        # On first connection 
        if first_connect(ssh):
            # Copy local wallet to remote
            print("First time connecting. Setting new PWD and Backing up local wallet to magic stick...")

            #set new passphrase
            passphrase = get_passphrase()
            set_new_passphrase(passphrase, ssh)
            put_magic_wllt(ssh, passphrase )
        else:
            # Copy remote wallet to local, Assumes remote wallet is more up to date.
            print("Retrieving wallet from magic stick...")    
            get_magic_wllt(ssh, passphrase)

    print("sleeping before shutdown...")
    time.sleep(10)

    # On Shutdown cycle
    ssh = connect_magic_wllt(conn)
    if MAGIC_WALLET and CONNECTED and ssh:
        # Copy local wallet to remote
        put_magic_wllt(ssh, passphrase)


