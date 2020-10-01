import paramiko

def ssh_2f(connection):
    password = connection.password
    fac_token = connection.fac_token
    hostname = connection.host
    port = connection.port

    # Handler for server questions
    def answer_handler(title, instructions, prompt_list):
        answers = {
          'password': password,
          'verification_code': fac_token
        }
        resp = []
        for prmpt in prompt_list:
            print('prmpt:', prmpt)
            prmpt_str = prmpt[0].lower().strip().replace(' ', '_').replace(':', '')
            print('prmpt_str:', prmpt_str, answers[prmpt_str])
            resp.append(answers[prmpt_str])
        return resp

    trans = paramiko.Transport((hostname, port))
    trans.use_compression()
    trans.set_keepalive(5)
    trans.connect()

    try:
        trans.auth_interactive_dumb(username, answer_handler)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh._transport = trans
        
        '''
        stdin, stdout, stderr = ssh.exec_command('ls')

        for line in stdout:
            print(line.strip('\n'))
        ssh.close()
        '''

        return ssh

    except Exception as exc:
        print('exception:', exc)
        trans.set_keepalive(0)

        if "Authentication failed" in str(exc):
            #token, ok = QtWidgets.QInputDialog.getText(window, '2FA', 'Enter your 2-factor authentication code:',QtWidgets.QLineEdit.Password)
            token = input("Enter your 2-factor authentication code:")
            token = token.strip()
            connection.fac_token = token
            return ssh_2f(connection.host, connection.port, connection.username, connection.password, connection.fac_token)
       
        elif "Bad authentication type" in str(exc):
            return connect_magic_wllt(connection)    


    #return trans

def connect_magic_wllt(conn):
    global CONNECTED, passphrase
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(conn.host, conn.port, conn.username, conn.password)
        print("Connected successfully.")
        CONNECTED = True
   
    except Exception as e:
        print("Couldn\'t connect with default password.", e,"\n")
        CONNECTED = False
        #passphrase, ok = QtWidgets.QInputDialog.getText(window, 'Wallet Passphrase', 'Enter wallet passphrase:',QtWidgets.QLineEdit.Password)
        passphrase = input("Enter your password:")
        passphrase = passphrase.strip()
        connection.password = passphrase

        try:    
            ssh = connect_magic_wllt(connection)
        except:
            ssh = "failed"   

        '''    
        if ok:
            passphrase = passphrase.strip()
            connection.password = passphrase
            ssh = connect_magic_wllt(connection)
        
        else:
            ssh = "failed"
        '''
    return ssh   

class connection:
   host = "magicwallet.local"
   port = 22
   username = "magic"
   password = "kashee"
   fac_token = ""


trans = ssh_2f(connection.host, connection.port, connection.username, connection.password, connection.fac_token)

'''
if not "Bad authentication type" and not "Authentication failed" in str(trans):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh._transport = trans
    stdin, stdout, stderr = ssh.exec_command('ls')

    for line in stdout:
        print(line.strip('\n'))
    ssh.close()
elif "Authentication failed" in str(trans):
    #token, ok = QtWidgets.QInputDialog.getText(window, '2FA', 'Enter your 2-factor authentication code:',QtWidgets.QLineEdit.Password)
    token = input("Enter your 2-factor authentication code:")
    token = token.strip()
    connection.fac_token = token
    trans = ssh_2f(connection.host, connection.port, connection.username, connection.password, connection.fac_token)

elif "Bad authentication type" in str(trans):
    connect_magic_wllt(connection)

'''