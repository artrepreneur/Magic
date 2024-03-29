# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.


from PyQt5 import QtWidgets, uic
from MainWindow import Ui_MainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from functools import partial
import os, sys, subprocess, json, threading, time, random, signal, traceback, re, psutil
import platform, transactions, estimate, ingest, signMultiSigTrans, sendMultiSigTrans, sendCombMultiSigTrans, fold, createWallet, getSeed, resync, peerinf
import balances, addresses, balanceAddresses, rpcworker, privkey, pubkey, password, wlltinf, send, time, datetime, genMultiSig, createMultiSigTrans, sendCombMultiSigTrans
from pixMp import *
from genAddress import *
from config import MIN_CONF, MAX_CONF
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
from shutil import copyfile
from pathlib import Path
from os import path
from rpcworker import progress_fn, thread_complete

# !!
import paramiko
from scp import SCPClient

CONNECTED = False
LOCAL_WALLET_PATH = "." 
REMOTE_WALLET_PATH = "Wallets" 
WALLET_NAME = "wallet.db"
WALLET_NAME_E = "wallet.db.gpg"
MAGIC_WALLET = False
WALLET_COPY = False
ssh = None
# !!

WAIT_SECONDS = 10
VERSION_NUM = "1.0.0"
AUTO_RESTART_WALLET = True
CREATE_NEW_WALLET = False
SHUTDOWN_CYCLE = False
WALLET_SYNCING = False
PKTD_SYNCING = False
COUNTER = 1 
FEE = ".00000001"
STATUS_INTERVAL = 10
passphrase = ''
passphrase_ok = False

# Password visiblity toggle
password_shown = False
ver_password_shown = False
old_password_shown = False
new_password_shown = False
v_password_shown = False
pwd_action = None
ver_pwd_action = None
pwd_vsbl_icon = None
pwd_invsbl_icon = None
pwd_old_action = None
pwd_new_action = None
pwd_ver_action = None

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

# Check if pkt wallet sync in progress
def pktwllt_synching(info):
    global WALLET_SYNCING
    if info != {}:
            status = (info["WalletStats"]["Syncing"])
            WALLET_SYNCING = bool(status)
            #print('WALLET_SYNCING',WALLET_SYNCING)
            return WALLET_SYNCING
    else:
        print('Unable to get wallet status.\n') 
        WALLET_SYNCING = False
        #print('WALLET_SYNCING',WALLET_SYNCING)
        return WALLET_SYNCING

# Check if pktd sync in progress
def pktd_synching(info):
    global PKTD_SYNCING
    if info != {}:
        status = (info["IsSyncing"]) 
        PKTD_SYNCING = bool(status)
        #print('PKTD_SYNCING',PKTD_SYNCING)
        return PKTD_SYNCING
    else:
        print('Unable to get pktd status.\n')
        PKTD_SYNCING = False
        #print('PKTD_SYNCING',PKTD_SYNCING)
        return PKTD_SYNCING

# Message box for wallet sync
def sync_msg(msg):
    sync_msg_box = QtWidgets.QMessageBox()
    sync_msg_box.setText(msg)
    sync_msg_box.setWindowTitle('Sync Info')
    sync_msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes)
    sync_ok_btn = sync_msg_box.button(QtWidgets.QMessageBox.Yes)
    sync_ok_btn.setText("Ok")
    sync_msg_box.exec()

# Add a new send recipient
class SendRcp(QtWidgets.QFrame):

    def __init__(self, obj_num, item, item_nm, *args, **kwargs):

        super(SendRcp, self).__init__(*args, **kwargs)
        self.obj_num = obj_num
        self.item = item
        self.name = item_nm
        self.setObjectName(self.name)
        self.setStyleSheet("background-color: rgb(228, 234, 235); margin-bottom: 0px; margin-right: 0px")
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.verticalLayout_21 = QtWidgets.QFormLayout(self)
        self.verticalLayout_21.setObjectName("verticalLayout_21")
        self.verticalLayout_21.setAlignment(Qt.AlignVCenter)
        self.label_9 = QtWidgets.QLabel(self)
        self.label_9.setStyleSheet("font: 75 15pt 'Gill Sans'; padding-bottom: 4px;")
        self.label_9.setObjectName("label_9")
        self.label_9.setText("Pay To:")
        self.label_9.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.lineEdit_6 = QtWidgets.QLineEdit(self)
        self.lineEdit_6.setMinimumSize(QSize(0, 35))
        self.lineEdit_6.setMaximumSize(QSize(16777215, 35))
        self.lineEdit_6.setStyleSheet("background-color: rgb(253, 253, 255); border: 1px solid rgb(210, 216, 216); border-radius: 4px;")
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_6.setToolTip("Enter Address of Payee")
        self.verticalLayout_21.addRow(self.label_9, self.lineEdit_6)
        self.verticalLayout_21.setFormAlignment(Qt.AlignLeft)
        self.verticalLayout_21.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        self.label_10 = QtWidgets.QLabel(self)
        self.label_10.setStyleSheet("font: 75 15pt 'Gill Sans';padding-bottom: 4px;")
        self.label_10.setObjectName("label_10")
        self.label_10.setText("Amount:")
        self.send_amt_input = QtWidgets.QLineEdit(self)
        self.send_amt_input.setMinimumSize(QSize(0, 35))
        self.send_amt_input.setMaximumSize(QSize(16777215, 35))
        self.send_amt_input.setStyleSheet("background-color: rgb(253, 253, 255); border: 1px solid rgb(210, 216, 216); border-radius: 4px;")
        self.send_amt_input.setToolTip("Enter Amount to Pay")
        self.send_amt_input.setObjectName("send_amt_input")
        self.verticalLayout_21.addRow(self.label_10, self.send_amt_input)

        self.frme = QtWidgets.QFrame(self)
        self.frme.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frme.setMinimumHeight(5)
        self.frme.setMaximumHeight(5)

        self.del_rcp_1 = QtWidgets.QPushButton(self)
        self.del_rcp_1.setObjectName("pushButton")
        self.del_rcp_1.setText("Delete Recipient")
        self.del_rcp_1.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
        self.del_rcp_1.setMinimumHeight(40)
        self.verticalLayout_21.addRow(self.frme, self.del_rcp_1)
        self.del_rcp_1.clicked.connect(self.del_clicked)

    def del_fields(self):
        self.lineEdit_6.clear()
        self.send_amt_input.clear()

    def del_clicked(self):

        self.lineEdit_6.clear()
        self.send_amt_input.clear() #sdfsd

        class_id = self.name.split('_')[0]
        chld_num = window.rcp_list.count() if (class_id == 'send') else window.rcp_list_2.count()

        if chld_num > 1 and class_id == 'send':
            window.rcp_list.removeItemWidget(self.item)
            window.rcp_list.takeItem(window.rcp_list.row(self.item))
            window.rcp_list.update()
            rcp_list_dict.pop(self.name)

            try:
                if pay_dict:
                    pay_dict.pop(self.lineEdit_6.text())
            except:
                print('unable to pop pay_dict', pay_dict)

        elif chld_num > 1 and class_id == 'multisig':
            window.rcp_list_2.removeItemWidget(self.item)
            window.rcp_list_2.takeItem(window.rcp_list_2.row(self.item))
            window.rcp_list_2.update()
            rcp_list_dict2.pop(self.name)

            try:
                if pay_dict2:
                    pay_dict2.pop(self.lineEdit_6.text())
            except:
                print('unable to pop pay_dict2', pay_dict2)


# Add a new public key entry field to multisig create
class PKLine(QtWidgets.QFrame):

    def __init__(self, obj_num, item, *args, **kwargs):

        super(PKLine, self).__init__(*args, **kwargs)
        self.item = item
        self.name = 'm_pkline_' + obj_num
        self.setObjectName(self.name)

        # New lineEdit
        self.pk_line = QtWidgets.QLineEdit(self)
        self.pk_line.setObjectName("pk_line_"+obj_num)
        self.pk_line.setStyleSheet("QLineEdit {background-color: rgb(253, 253, 255);}")
        self.pk_line.setMinimumHeight(40)

        # Del button
        self.del_btn = QtWidgets.QPushButton(self)
        self.del_btn.setObjectName("del_btn_"+obj_num)
        self.del_btn.setText("delete")
        self.del_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 16pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 16pt 'Futura'; background-color: #022D93; color: #FF6600;}")
        self.del_btn.setMinimumSize(60, 40)

        # Form layout
        self.form_layout = QtWidgets.QGridLayout(self)
        self.form_layout.addWidget(self.pk_line, 0, 0, 1, 1)
        self.form_layout.addWidget(self.del_btn, 0, 1, 1, 1)
        self.del_btn.clicked.connect(self.del_clicked)

    def del_clicked(self):
        chld_num = window.multisig_list.count()
        if chld_num > 1:
            if pk_list_dict:
                pk_list_dict.pop(self.name)
            window.multisig_list.removeItemWidget(self.item)
            window.multisig_list.takeItem(window.multisig_list.row(self.item))
            window.multisig_list.update()

class SideMenuBtn(QtWidgets.QPushButton):

    def __init__(self, obj_name, obj_text, icon_name, ttip, *args, **kwargs):
        super(SideMenuBtn, self).__init__(*args, **kwargs)
        self.text = obj_text
        self.name = obj_name
        self.icon_name = icon_name
        self.icon = icons[self.icon_name]
        self.ttip = ttip
        self.setText(self.text)
        self.setObjectName(self.name)
        self.setIcon(QIcon(self.icon))
        self.setIconSize(QSize(70,25))
        self.setStyleSheet("QPushButton#"+self.name+"{border-radius: 3px; border: 1px solid #D6E4FF; color: #D6E4FF; font: 57 20pt 'Futura'; text-align: left;} QToolTip { color: #000; background-color: #fff; border: none; }")
        self.setMaximumSize(QSize(16777215,50))
        self.setMinimumSize(QSize(16777215,50))
        self.setToolTip(_translate("MainWindow", self.ttip))

    def mousePressEvent(self, event):
        self.setText(self.text)
        self.setObjectName(self.name)
        self.alt_name = self.icon_name + '2'
        self.icon2 = icons[self.alt_name]
        self.setIcon(QIcon(self.icon2))
        self.setIconSize(QSize(70,25))
        self.setStyleSheet("QPushButton#"+self.name+" {border-radius: 3px; border: 1px solid #FF6600; color: #FF6600; font: 57 20pt 'Futura'; background-color: #022D93;  text-align: left;}  QToolTip { color: #000; background-color: #fff; border: none; }")
        self.setMaximumSize(QSize(16777215,50))
        self.setMinimumSize(QSize(16777215,50))

    def mouseReleaseEvent(self, event):
        self.setText(self.text)
        self.setObjectName(self.name)
        self.setIcon(QIcon(self.icon))
        self.setIconSize(QSize(70,25))
        self.setStyleSheet("QPushButton#"+self.name+" {border-radius: 3px; border: 1px solid #D6E4FF; color: #D6E4FF; font: 57 20pt 'Futura';  text-align: left;}  QToolTip { color: #000; background-color: #fff; border: none; }")
        self.setMaximumSize(QSize(16777215,50))
        self.setMinimumSize(QSize(16777215,50))
        side_menu_clicked(self)

def side_menu_clicked(btn):

    if btn.objectName().strip() == 'Balances':
        i = window.stackedWidget.indexOf(window.balance_page)
        show_balance()
        add_addresses(['balances'])
        window.stackedWidget.setCurrentIndex(i)

    elif btn.objectName().strip() == 'Send':
        window.label_6.clear()
        i = window.stackedWidget.indexOf(window.send_page)
        init_send_rcp()
        set_fee_est()
        window.stackedWidget.setCurrentIndex(i)

    elif btn.objectName().strip() == 'Magic':
        print("Detecting magic wallet...\n")
        dct_msg_box = QtWidgets.QMessageBox()
        dct_msg_box.setText("Attach your magic wallet and click \"Connect\" to connect it.\n")
        dct_msg_box.setInformativeText("If your wallet is attached to your computer, you may need to wait a minute and click the magic button again to connect to it.\n")
        dct_msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        dct_msg_btn = dct_msg_box.button(QtWidgets.QMessageBox.Ok)
        dct_msg_btn.setText("Connect")
        dct_msg_box.exec()
        detect_magic_wllt(QtWidgets)    

    elif btn.objectName().strip() == 'Receive':
        i = window.stackedWidget.indexOf(window.receive_page)
        window.receive_amt_line.clear()
        window.receive_hist_tree2.clear()
        window.msg_line.clear()
        window.label_26.clear()
        window.stackedWidget.setCurrentIndex(i)

    elif btn.objectName().strip() == 'Transactions':
        global iteration
        i = window.stackedWidget.indexOf(window.transactions_page)
        iteration = 0
        item_0 = QtWidgets.QTreeWidgetItem(window.transaction_hist_tree)
        font = QFont()
        font.setFamily("Gill Sans")
        font.setPointSize(15)
        item_0.setFont(0, font)

        if pktd_synching(wlltinf.get_inf(uname, pwd)):
            sync_msg("Transactions aren\'t available until wallet has completely sync\'d")
        else:
            get_transactions()
            window.stackedWidget.setCurrentIndex(i)


def get_transactions():
    global iteration

    try:
        transactions.history(uname, pwd, iteration, window, worker_state_active, threadpool)
        iteration += 1
    except:
        msg = "Unable to get transactions. \n\nHave any transactions been executed?"
        trns_msg_box = QtWidgets.QMessageBox()
        trns_msg_box.setWindowTitle("Transaction History Failed")
        trns_msg_box.setText(msg)
        trns_msg_box.exec()
        print('Unable to get transactions\n')

def show_balance():
    info = wlltinf.get_inf(uname, pwd)
    if pktd_synching(info): 
        sync_msg("Wallet daemon is currently syncing. Some features may not work until sync is complete.")
    elif pktwllt_synching(info):
        sync_msg('Wallet is currently synching to chain. Some balances may be inaccurate until chain sync\'s fully.')

    print("Getting balance...")
    window.balance_amount.clear()
    worker_state_active['GET_BALANCE'] = False
    total_balance = balances.get_balance_thd(uname, pwd, window, worker_state_active, threadpool)

def set_fee_est():
    global FEE
    estimate.fee(uname, pwd, window, FEE, worker_state_active, threadpool)

# Append addresses to list
def add_addresses(type):

    for item in type:
        if item == "balances" or item == "all":
            if WALLET_SYNCING:
                sync_msg('Wallet is synching, balances will take a while to return.')
            elif PKTD_SYNCING:     
                sync_msg('Wallet is synching, balances will take a while to return.')
            # Add loading message
            load_label= QtWidgets.QLabel()
            load_label.setStyleSheet("font: 15pt \'Gill Sans\'; padding-bottom: 4px; text-align: center;")
            load_label.setText("Addresses loading please wait...")
            load_label.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            balanceAddresses.get_addresses(uname, pwd, window, item, worker_state_active, threadpool)

        elif item == "addresses":
            addresses.get_addresses(uname, pwd, window, item, worker_state_active, threadpool)

def get_priv_key(address, passphrase):
    # Get private key
    privkey.get_key(uname, pwd, address, passphrase, window, worker_state_active, threadpool)

def get_pub_key(address):
    # Get private key
    pubkey.get_key(uname, pwd, address, window, worker_state_active, threadpool)

# !!
def change_pass(old_pass, new_pass):

    # Attempt to change password.
    global passphrase
    passphrase = ""
    success = False

    if path.exists(get_correct_path(".magic.cfg")):

        if not (MAGIC_WALLET and CONNECTED and ssh):

            # Ask user to attach and connect to wallet before attempting to change password
            pwd_chg_msg_box = QtWidgets.QMessageBox()
            pwd_chg_msg = 'It seems you own a magic wallet. Make sure it\'s attached and click the "Magic" button connect it.'
            pwd_chg_msg_box.setText(pwd_chg_msg)            
            pwd_chg_msg_box.exec()

        else:
            if not (old_pass == new_pass):
                print("About to change local password... \n")
                password.change(uname, pwd, old_pass, new_pass, window, worker_state_active, threadpool, True)
                print("Changed wallet password... \n")
            
            res = change_mgk_passphrase(new_pass, ssh)
            
            if res:
                print("Changed magic password... \n")
                passphrase = new_pass
                success = True

    else:
        password.change(uname, pwd, old_pass, new_pass, window, worker_state_active, threadpool, False)
        passphrase = new_pass
        success = True

    return success    

# Additional customizations
def add_custom_styles():
    global pwd_action, ver_pwd_action, pwd_vsbl_icon, pwd_invsbl_icon, pwd_old_action, pwd_new_action, pwd_ver_action

    window.label_25.setPixmap(QPixmap(resource_path('img/app_icon.png')))
 
    # Password visiblity toggle
    pwd_vsbl_icon = QIcon(QPixmap(resource_path('img/glyphicons_051_eye_open.png')))
    pwd_invsbl_icon = QIcon(QPixmap(resource_path('img/glyphicons_052_eye_close.png')))
    pwd_action = window.lineEdit_2.addAction(pwd_vsbl_icon, QtWidgets.QLineEdit.TrailingPosition)
    ver_pwd_action = window.lineEdit_11.addAction(pwd_vsbl_icon, QtWidgets.QLineEdit.TrailingPosition)
    pwd_old_action = window.lineEdit_10.addAction(pwd_vsbl_icon, QtWidgets.QLineEdit.TrailingPosition)
    pwd_new_action = window.lineEdit_4.addAction(pwd_vsbl_icon, QtWidgets.QLineEdit.TrailingPosition)
    pwd_ver_action = window.lineEdit_5.addAction(pwd_vsbl_icon, QtWidgets.QLineEdit.TrailingPosition)

    # Frame customizations
    window.send_exec_group.setStyleSheet("QGroupBox#send_exec_group {border-radius: 5px; background-color: rgb(228, 234, 235);}")
    window.send_exec_group.setMinimumHeight(73)
    window.send_exec_group.setMaximumHeight(73)

    # Button cusomizations
    window.clear_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.clear_btn.setMinimumSize(50, 40)

    window.fold_btn_1.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.fold_btn_1.setMinimumSize(80, 40)

    #window.fold_again_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    #window.fold_again_btn.setMinimumSize(80, 40)

    window.snd_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.snd_btn.setMinimumSize(50, 40)

    window.add_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.add_btn.setMinimumSize(50, 40)

    window.multi_clear_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_clear_btn.setMinimumSize(50, 40)

    window.fee_est2_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.fee_est2_btn.setMinimumSize(100, 40)

    window.fee_est_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.fee_est_btn.setMinimumSize(100, 40)

    window.import_keys_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.import_keys_btn.setMinimumSize(80, 40)

    window.multi_add_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_add_btn.setMinimumSize(50, 40)

    window.multi_create_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_create_btn.setMinimumSize(50, 40)

    window.multi_sign_btn2.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_sign_btn2.setMinimumSize(50, 40)

    window.multi_sign_btn3.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_sign_btn3.setMinimumSize(50, 40)

    window.multi_sign_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_sign_btn.setMinimumSize(160, 40)

    window.import_trans_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.import_trans_btn.setMinimumSize(160, 40)

    window.multi_send_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_send_btn.setMinimumSize(160, 40)

    window.combine_trans_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.combine_trans_btn.setMinimumSize(180, 40)

    window.add_trns_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.add_trns_btn.setMinimumSize(180, 40)

    window.comb_clear_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.comb_clear_btn.setMinimumSize(180, 40)

    window.combine_send_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.combine_send_btn.setMinimumSize(180, 40)

    window.rtr_pubk_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.rtr_pubk_btn.setFixedSize(180, 40)

    window.rtr_prvk_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.rtr_prvk_btn.setFixedSize(180, 40)

    window.file_loc_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.file_loc_btn.setFixedSize(100, 40)

    window.multi_create_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_create_btn.setMinimumSize(100, 40)

    window.address_gen_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.address_gen_btn.setFixedSize(100, 40)

    window.multi_qr_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_qr_btn.setFixedSize(100, 40)

    window.address_gen_btn2.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.address_gen_btn2.setMinimumHeight(40)

    window.all_addr_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.all_addr_btn.setMinimumHeight(40)

    window.bal_addr_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.bal_addr_btn.setMinimumHeight(40)

    window.receive_rqst_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.receive_rqst_btn.setFixedSize(200, 40)

    window.multisig_gen_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multisig_gen_btn.setFixedSize(100, 40)

    window.add_multisig_pk_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.add_multisig_pk_btn.setFixedSize(140, 40)

    window.pwd_ok_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.pwd_ok_btn.setMinimumSize(50, 40)

    window.pwd_cancel_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.pwd_cancel_btn.setMinimumSize(50, 40)

    window.sign_dec_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.sign_dec_btn.setMinimumSize(50, 40)

    window.sign_enc_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.sign_enc_btn.setMinimumSize(50, 40)

    window.load_trns_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.load_trns_btn.setFixedSize(100, 40)

    window.wllt_cr8_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.wllt_cr8_btn.setFixedSize(120, 40)

    window.passphrase_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.passphrase_btn.setFixedSize(120, 40)

    window.seed_next_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.seed_next_btn.setMinimumSize(150, 40)

    window.no_seed_next_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.no_seed_next_btn.setMinimumSize(150, 40)

    window.open_wllt_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.open_wllt_btn.setFixedSize(100, 40)

    window.recalc_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.recalc_btn.setFixedSize(100, 25)



# Listen for static buttons
def button_listeners():
    window.snd_btn.clicked.connect(btn_released)
    window.clear_btn.clicked.connect(btn_released)
    window.multi_clear_btn.clicked.connect(btn_released)
    window.fee_est2_btn.clicked.connect(btn_released)
    window.fee_est_btn.clicked.connect(btn_released)
    window.add_btn.clicked.connect(btn_released)
    window.add_multisig_pk_btn.clicked.connect(btn_released)
    window.multi_add_btn.clicked.connect(btn_released)
    window.address_gen_btn.clicked.connect(btn_released)
    window.address_gen_btn2.clicked.connect(btn_released)
    window.all_addr_btn.clicked.connect(btn_released)
    window.bal_addr_btn.clicked.connect(btn_released)
    window.multi_create_btn.clicked.connect(btn_released)
    window.multi_sign_btn2.clicked.connect(btn_released)
    window.multi_sign_btn3.clicked.connect(btn_released)
    window.import_trans_btn.clicked.connect(btn_released)
    window.combine_trans_btn.clicked.connect(btn_released)
    window.combine_send_btn.clicked.connect(btn_released)
    window.multi_sign_btn.clicked.connect(btn_released)
    window.add_trns_btn.clicked.connect(btn_released)
    window.comb_clear_btn.clicked.connect(btn_released)
    window.fold_btn_1.clicked.connect(btn_released)
    #window.fold_again_btn.clicked.connect(btn_released)
    window.multi_send_btn.clicked.connect(btn_released)
    window.rtr_prvk_btn.clicked.connect(btn_released)
    window.rtr_pubk_btn.clicked.connect(btn_released)
    window.pwd_cancel_btn.clicked.connect(btn_released)
    window.pwd_ok_btn.clicked.connect(btn_released)
    window.load_trns_btn.clicked.connect(btn_released)
    window.import_keys_btn.clicked.connect(btn_released)
    window.receive_rqst_btn.clicked.connect(btn_released)
    window.multisig_gen_btn.clicked.connect(btn_released)
    window.multi_qr_btn.clicked.connect(btn_released)
    window.wllt_cr8_btn.clicked.connect(btn_released)
    window.passphrase_btn.clicked.connect(btn_released)
    window.seed_next_btn.clicked.connect(btn_released)
    window.no_seed_next_btn.clicked.connect(btn_released)
    window.open_wllt_btn.clicked.connect(btn_released)
    window.recalc_btn.clicked.connect(btn_released)
    


# Menu listeners
def menubar_listeners():
    window.actionAddress_2.triggered.connect(menubar_released)
    window.actionMultiSig_Address.triggered.connect(menubar_released)
    window.actionCreate_Transaction.triggered.connect(menubar_released)
    window.actionPassword.triggered.connect(menubar_released)
    window.actionPay_to_Many.triggered.connect(menubar_released)
    window.actionSign_Verify_Message.triggered.connect(menubar_released)
    window.actionCombine_Multisig_Transactions.triggered.connect(menubar_released)
    window.actionExport_Private_Key.triggered.connect(menubar_released)
    window.actionImport_Keys.triggered.connect(menubar_released)
    window.actionDelete.triggered.connect(menubar_released)
    window.actionInformation_2.triggered.connect(menubar_released)
    window.actionGet_Public_Key.triggered.connect(menubar_released)
    window.actionEncrypt_Decrypt_Message.triggered.connect(menubar_released)
    window.actionSave.triggered.connect(menubar_released)
    window.actionGet_Private_Key.triggered.connect(menubar_released)
    window.actionSeed.triggered.connect(menubar_released)
    window.actionFrom_Text_2.triggered.connect(menubar_released)
    window.actionFrom_QR_Code.triggered.connect(menubar_released)
    window.actionFold_Address.triggered.connect(menubar_released)
    window.actionWebsite.triggered.connect(menubar_released)
    window.actionManual_Resync.triggered.connect(menubar_released)
    app.aboutToQuit.connect(quit_app)
    pwd_action.triggered.connect(on_toggle_password_action)
    ver_pwd_action.triggered.connect(on_toggle_ver_password_action)
    pwd_old_action.triggered.connect(on_toggle_old_password_action)
    pwd_new_action.triggered.connect(on_toggle_new_password_action)
    pwd_ver_action.triggered.connect(on_toggle_v_password_action)


def on_toggle_password_action(self):
    global password_shown

    if not password_shown:
        window.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Normal)
        password_shown = True
        pwd_action.setIcon(pwd_invsbl_icon)
    else:
        window.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        password_shown = False
        pwd_action.setIcon(pwd_vsbl_icon)

def on_toggle_ver_password_action(self):
    global ver_password_shown
    
    if not ver_password_shown:
        window.lineEdit_11.setEchoMode(QtWidgets.QLineEdit.Normal)
        ver_password_shown = True
        ver_pwd_action.setIcon(pwd_invsbl_icon)
    else:
        window.lineEdit_11.setEchoMode(QtWidgets.QLineEdit.Password)
        ver_password_shown = False
        ver_pwd_action.setIcon(pwd_vsbl_icon)

def on_toggle_old_password_action(self):
    global old_password_shown
    
    if not old_password_shown:
        window.lineEdit_10.setEchoMode(QtWidgets.QLineEdit.Normal)
        old_password_shown = True
        pwd_old_action.setIcon(pwd_invsbl_icon)
    else:
        window.lineEdit_10.setEchoMode(QtWidgets.QLineEdit.Password)
        old_password_shown = False
        pwd_old_action.setIcon(pwd_vsbl_icon)

def on_toggle_new_password_action(self):
    global new_password_shown
    print("toggle new", new_password_shown)
    if not new_password_shown:
        window.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.Normal)
        new_password_shown = True
        pwd_new_action.setIcon(pwd_invsbl_icon)
    else:
        window.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.Password)
        new_password_shown = False
        pwd_new_action.setIcon(pwd_vsbl_icon)

def on_toggle_v_password_action(self):
    global v_password_shown
    
    if not v_password_shown:
        window.lineEdit_5.setEchoMode(QtWidgets.QLineEdit.Normal)
        v_password_shown = True
        pwd_ver_action.setIcon(pwd_invsbl_icon)
    else:
        window.lineEdit_5.setEchoMode(QtWidgets.QLineEdit.Password)
        v_password_shown = False
        pwd_ver_action.setIcon(pwd_vsbl_icon)

class CustomInputDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(CustomInputDialog, self).__init__(*args, **kwargs)
        
        self.pass_shown = False 
        self.passphrase = None
        self.type = type
        self.label = QtWidgets.QLabel(self)
        
        '''
        if SHUTDOWN_CYCLE:
            self.label.setText("Backing up your wallet...\n\nPlease enter your wallet passphrase:")
        else:
            self.label.setText("Please enter your wallet passphrase:")
        '''
        
        self.label.setText("Please enter your wallet passphrase:")    
        self.label.setStyleSheet("font: 14pt Bold 'Gill Sans'")
        self.setWindowTitle("Wallet Passphrase")
        
        self.line = QtWidgets.QLineEdit(self)
        self.line_action = self.line.addAction(pwd_vsbl_icon, QtWidgets.QLineEdit.TrailingPosition)
        self.line.setEchoMode(QtWidgets.QLineEdit.Password)
        self.line.setFixedWidth(200)
        
        self.cncl_btn = QtWidgets.QPushButton(self)
        self.cncl_btn.setObjectName("cncl_btn")
        self.cncl_btn.setText("Cancel")
        self.cncl_btn.setFixedWidth(80)
        
        self.ok_btn = QtWidgets.QPushButton(self)
        self.ok_btn.setObjectName("ok_btn")
        self.ok_btn.setText("Ok")
        self.ok_btn.setDefault(True)
        self.ok_btn.setFixedWidth(80)
        
        self.form_layout = QtWidgets.QGridLayout(self)
        self.form_layout.addWidget(self.label, 0, 0, 1, 1)
        self.form_layout.addWidget(self.line, 1, 0, 1, 1)
        
        self.frame = QtWidgets.QFrame(self)
        self.sub_form_layout  = QtWidgets.QGridLayout(self.frame)
        self.sub_form_layout.addWidget(self.cncl_btn, 0, 0, 1, 1)
        self.sub_form_layout.addWidget(self.ok_btn, 0, 1, 1, 1)
        self.form_layout.addWidget(self.frame, 2, 0, 1, 1)
        
        # Actions
        self.cncl_btn.clicked.connect(self.cncl_clicked)
        self.ok_btn.clicked.connect(self.ok_clicked)
        self.line_action.triggered.connect(self.toggle_clicked)
					
    def cncl_clicked(self):
        self.passphrase = None
        self.close()
        
    def ok_clicked(self):
        passphrase = self.line.text()
        self.passphrase = passphrase
        self.close()
        
    def toggle_clicked(self):
        if not self.pass_shown:
            self.line.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.pass_shown = True
            self.line_action.setIcon(pwd_invsbl_icon)
        else:
            self.line.setEchoMode(QtWidgets.QLineEdit.Password)
            self.pass_shown = False
            self.line_action.setIcon(pwd_vsbl_icon)
					
def get_pass():
        global passphrase, passphrase_ok

        passphrase = ""
        ok = passphrase_ok
        dialog = CustomInputDialog()
        dialog.exec()
        passphrase = dialog.passphrase

        if passphrase and not passphrase_ok:
            # see if passphrase is valid, we are using the same passphrase for the wallet. 
            try:
                cmd = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet walletpassphrase " + passphrase + ' 1000'
                result, err = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                result = result.decode('utf-8')
                err = err.decode('utf-8')
                
                if not err:
                    ok = True
                    passphrase_ok = ok

                    try:
                        lock = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet walletlock"
                        result_lock, err_lock = subprocess.Popen(resource_path(lock), shell=True, stdout=subprocess.PIPE).communicate()
                    except:
                        print("Wallet lock failed.\n")
                else:
                    passphrase = ""
                    bad_pass()  

            except:
                print("Passphrase failed.\n")
                passphrase = ""
                bad_pass()
        elif passphrase and passphrase_ok:
            ok = passphrase_ok
        else:
            passphrase = ""
            ok = False
            passphrase_ok = ok

        return passphrase, ok

def bad_pass():
    pwd_msg = "The password you entered is incorrect."
    pwd_msg_box = QtWidgets.QMessageBox()
    pwd_msg_box.setText(pwd_msg)
    pwd_msg_box.exec()  

# Quit app
def quit_app():
    global SHUTDOWN_CYCLE
    SHUTDOWN_CYCLE = True
    exit_handler()


# Handler for menu item click
def btn_released(self):
    global FEE, passphrase

    clicked_widget = window.sender()
    #print('pressed button:', clicked_widget.objectName())

    if clicked_widget.objectName() == 'add_multisig_pk_btn':
        #print('add new pk line here')
        if window.multisig_list.count() < 12:
            item_num = window.multisig_list.count() + 1
            item_line_N = QtWidgets.QListWidgetItem(window.multisig_list)
            item_line_N.setSizeHint(QSize(window.multisig_list.width() - 30, 60))
            window.multisig_list.addItem(item_line_N)
            item_nm = "m_pkline_"+ str(item_num)
            vars()[item_nm] = PKLine(str(item_num), item_line_N)
            window.multisig_list.setItemWidget(item_line_N, vars()[item_nm])
            pk_list_dict[item_nm] = vars()[item_nm]

    elif clicked_widget.objectName() == 'multisig_gen_btn':
        global pk_arr, pk_count
        pk_arr = []
        for val in list(pk_list_dict.values()):
            itm = val.pk_line.text().strip()
            if itm:
                pk_arr.append(itm)

        pk_count = int(window.sig_box.currentText())
        msg_box_16 = QtWidgets.QMessageBox()
        print('Key count:', len(pk_arr), pk_count)
        if len(pk_arr) >= pk_count:
            print("Correct number of public keys entered.")

            for i, item in enumerate(pk_arr):
                if not item:
                    msg = "All public keys must be valid. Delete any extra input fields you don't need."
                    msg_box_16.setText(msg)
                    msg_box_16.exec()
                    return

            #Get passphrase
            if passphrase == '':
                passphrase, ok = get_pass()
            else:
                ok = True

            if ok:
                msg = "Create new multisig address?"
                msg_box_16.setText(msg)
                msg_box_16.exec()
                genMultiSig.create(uname, pwd, window, pk_count, pk_arr, passphrase, worker_state_active, threadpool)
        else:
            msg = "Incorrect number of public keys."
            msg_box_16.setText(msg)
            msg_box_16.exec()
            print("Incorrect number of public keys.")

    elif clicked_widget.objectName() == 'add_trns_btn':
        import_qr2()

    elif clicked_widget.objectName() == 'comb_clear_btn':
        clear_comb()

    elif clicked_widget.objectName() == 'clear_btn':
        clear_send_rcp()

    elif clicked_widget.objectName() == 'multi_clear_btn':
        clear_multi_rcp()

    elif clicked_widget.objectName() == 'fee_est_btn':
        set_fee_est()

    elif clicked_widget.objectName() == 'fee_est2_btn':
        set_fee_est()

    elif clicked_widget.objectName() == 'wllt_cr8_btn':
        window.lineEdit_2.clear()
        window.lineEdit_11.clear()
        i = window.stackedWidget.indexOf(window.wllt_pwd_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_widget.objectName() == 'passphrase_btn':
        global wllt_pass
        wllt_pass = window.lineEdit_2.text().strip()
        wllt_pass_conf = window.lineEdit_11.text().strip()

        if not (wllt_pass or wllt_pass_conf):
            wllt_pass = ''
            wll_pass_conf = ''
            msg_box_24 = QtWidgets.QMessageBox()
            msg_box_24.setText('You must enter both a password and a confirmation.')
            msg_box_24.exec()
            return

        if wllt_pass == wllt_pass_conf:
            msg = ''
            if len(wllt_pass) < 8:
                msg = "Make sure your password is at least 8 letters"
            elif re.search('[0-9]',wllt_pass) is None:
                msg = "Make sure your password has a number in it"
            elif re.search('[A-Z]',wllt_pass) is None:
                msg = "Make sure your password has a capital letter in it"
            if msg:
                msg_box_24 = QtWidgets.QMessageBox()
                msg_box_24.setText(msg)
                msg_box_24.exec()
                return

            window.imprt_seed_txt.clear()
            window.old_pass_line.clear()
            i = window.stackedWidget.indexOf(window.imprt_seed_page)
            window.stackedWidget.setCurrentIndex(i)
            imp_msg_box = QtWidgets.QMessageBox()
            text = "Select \"Continue Without Seed\" if you are not importing a previous wallet seed."
            imp_msg_box.setText(text)
            imp_msg_box.setWindowTitle("Notification")
            ret = imp_msg_box.exec()

        else:
            wllt_pass = ''
            wll_pass_conf = ''
            msg_box_24 = QtWidgets.QMessageBox()
            msg_box_24.setText('Password and password confirmation do not match.')
            msg_box_24.exec()

    elif clicked_widget.objectName() == 'no_seed_next_btn':
        try:
            pp = wllt_pass
            window.seed_txt.clear()
            seed = createWallet.execute(uname,pwd, pp)["seed"]
            window.seed_txt.setText(seed)
            i = window.stackedWidget.indexOf(window.wllt_done_page)
            window.stackedWidget.setCurrentIndex(i)
        except:
            seed_msg_box = QtWidgets.QMessageBox()
            seed_msg_box.setText('Your wallet could not be created. Verify seed and/or old password.')
            seed_msg_box.exec()

    elif clicked_widget.objectName() == 'seed_next_btn':
        pp = wllt_pass
        seed_entry = window.imprt_seed_txt.toPlainText().strip()
        old_pass_line = window.old_pass_line.text().strip()

        if not old_pass_line:
            seed_msg_box = QtWidgets.QMessageBox()
            seed_msg_box.setText('You failed to enter your old password.')
            seed_msg_box.exec()
            return
        try:
            seed = createWallet.seed_execute(uname, pwd, pp, old_pass_line, seed_entry)["seed"]
            if not seed:
                seed_msg_box = QtWidgets.QMessageBox()
                seed_msg_box.setText('Your wallet could not be created. Verify seed and/or old password.')
                seed_msg_box.exec()
            else:
                window.seed_txt.setText(seed)
                i = window.stackedWidget.indexOf(window.wllt_done_page)
                window.stackedWidget.setCurrentIndex(i)
        except:
            seed_msg_box = QtWidgets.QMessageBox()
            seed_msg_box.setText('Your wallet could not be created. Verify seed and/or old password.')
            seed_msg_box.exec()
      

    elif clicked_widget.objectName() == 'recalc_btn':
        if pktwllt_synching(wlltinf.get_inf(uname, pwd)):
            window.balance_amount.setText(_translate("MainWindow", "Wallet Syncing..."))
        else:
            show_balance()

    elif clicked_widget.objectName() == 'open_wllt_btn':
        start_wallet_thread()
        window.menubar.setEnabled(True)
        #window.resize(1030, 800)
        window.menu_frame.show()
        window.frame_4.show()
        window.balance_tree.clear()
        i = window.stackedWidget.indexOf(window.balance_page)
        window.stackedWidget.setCurrentIndex(i)
        show_balance()
        add_addresses(['balances'])
        add_addresses(['addresses'])

    #elif clicked_widget.fold_again_btn.objectName() == 'fold_again_btn':
    #    i = window.stackedWidget.indexOf(window.fold_page_1)
    #    window.stackedWidget.setCurrentIndex(i)

    elif clicked_widget.objectName() == 'fold_btn_1':
        window.label_77.clear()
        fr = window.fld_frm_box.currentText()
        to = window.fld_to_box.currentText()
       
        # Handle empty addresses
        if fr == '':
            # Select a fold address.
            msg_box_26= QtWidgets.QMessageBox()
            msg_box_26.setText('You must select an address to fold from.')
            msg_box_26.exec()
            return 

        elif to == '':
            # If you have no fold addresses, click here to generate one.
            msg_box_26= QtWidgets.QMessageBox()
            msg_box_26.setText('You must select an address to fold to. Do you wish to create a new fold address?')
            msg_box_26.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            msg_box_26.setDefaultButton(QtWidgets.QMessageBox.Yes)
            snd_yes_btn = msg_box_26.button(QtWidgets.QMessageBox.Yes)
            snd_no_btn = msg_box_26.button(QtWidgets.QMessageBox.No)
            msg_box_26.exec()
            if msg_box_26.clickedButton() == snd_yes_btn:
                window.address_gen_btn2.click()
            return

        if pktwllt_synching(wlltinf.get_inf(uname, pwd)):
            msg_box_26= QtWidgets.QMessageBox()
            msg_box_26.setText('Wallet is syncing, unable to fold at this time.')
            msg_box_26.exec()
            return
        if passphrase == '':
            passphrase, ok = get_pass()
        else:
            ok = True

        if ok:
            #Get passphrase
            fold.execute(uname, pwd, window, worker_state_active, threadpool, passphrase, fr, to)
            msg_box_26= QtWidgets.QMessageBox()
            msg_box_26.setText('Wallet is currently folding. You may need to fold multiple times if your entire balance is not folded.')
            msg_box_26.exec()
        else:
            msg_box_18= QtWidgets.QMessageBox()
            msg_box_18.setText('You must enter your wallet passphase to submit transaction')
            msg_box_18.exec()

    elif clicked_widget.objectName() == 'add_btn':
        global rcp_list_dict, pay_dict

        if rcp_list_dict:
            last_key = list(rcp_list_dict.keys())[-1]
            last_item_num = last_key.split('_')[-1]
            item_num = int(last_item_num) + 1

        else:
            item_num = window.rcp_list.count() + 1

        item_line_N = QtWidgets.QListWidgetItem(window.rcp_list)
        item_line_N.setSizeHint(QSize((window.rcp_list.width() - 30), window.rcp_list.height()))
        window.rcp_list.addItem(item_line_N)
        item_nm = "send_rcp_"+ str(item_num)
        vars()[item_nm] = SendRcp(str(item_num), item_line_N, item_nm)
        window.rcp_list.setItemWidget(item_line_N, vars()[item_nm])
        rcp_list_dict[item_nm] = vars()[item_nm]
        window.rcp_list.setCurrentRow(int(window.rcp_list.count()))
        window.rcp_list.repaint()

    elif clicked_widget.objectName() == 'multi_add_btn':
        global rcp_list_dict2, pay_dict2

        if rcp_list_dict2:
            last_key = list(rcp_list_dict2.keys())[-1]
            last_item_num = last_key.split('_')[-1]
            item_num = int(last_item_num) + 1

        else:
            item_num = window.rcp_list_2.count() + 1

        item_num = window.rcp_list_2.count() + 1
        item_line_N = QtWidgets.QListWidgetItem(window.rcp_list_2)
        item_line_N.setSizeHint(QSize((window.rcp_list_2.width() - 30), window.rcp_list_2.height()))
        window.rcp_list_2.addItem(item_line_N)
        item_nm = "multisig_rcp_"+ str(item_num)
        vars()[item_nm] = SendRcp(str(item_num), item_line_N, item_nm)
        window.rcp_list_2.setItemWidget(item_line_N, vars()[item_nm])
        window.rcp_list_2.repaint()
        rcp_list_dict2[item_nm] = vars()[item_nm]

        #for i in rcp_list_dict2:
        #    print('payto:', rcp_list_dict2[i].lineEdit_6.text().strip())
        #    print('amt:', rcp_list_dict2[i].send_amt_input.text().strip())

    elif clicked_widget.objectName() == 'multi_qr_btn':

        # pop up with QR pk_arr
        pks = '| '.join(pk_arr)
        qr_text = 'qr_type: MULTI_QR, public_keys: '+ pks +' , m: '+str(pk_count)

        # Write QR
        qr_c = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )

        qr_c.add_data(qr_text)
        qr_c.make(fit=True)

        img = qr_c.make_image(fill_color="black", back_color="white")

        fn = "addmultiqr.png"
        img.save(resource_path("QRCodes/"+fn))

        # Show QR
        msg_box_25 = QtWidgets.QMessageBox()
        msg_box_25.setIconPixmap(QPixmap(resource_path("QRCodes/"+fn)))
        msg_box_25.setInformativeText('Scan QR code here.')
        msg_box_25.setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
        ret = msg_box_25.exec()

        # Save QR elsewhere for convenient sharing.
        if ret == QtWidgets.QMessageBox.Save:
            dir = QDir.homePath()
            dlg = QtWidgets.QFileDialog()
            dlg.setDefaultSuffix(".padding")
            filename = (dlg.getSaveFileName(None, "Save QR", dir + "/" + fn, "*.png"))[0]
            if filename:
                img.save(resource_path(filename))

        elif ret == QtWidgets.QMessageBox.Cancel:
            return

    elif clicked_widget.objectName() == 'receive_rqst_btn':
        pay_to_addr = str(window.pay_to_combo_box.currentText())
        amt = window.receive_amt_line.text()

        try:
            amt = float(amt)
        except:
            window.receive_amt_line.clear()
            window.receive_amt_line.setPlaceholderText('Input must be a number value.')
            return

        amt = str(amt)
        pay_msg = window.msg_line.text()

        dt= str(datetime.datetime.now()).split('.')[0]

        if pay_to_addr[0] == 'P':
            qr_text = 'qr_type: MULTI_PAY_REQUEST, date: '+ dt +',pay_to: ' + pay_to_addr +',amount: ' + amt + ',comment: ' + pay_msg
        else:
            qr_text = 'qr_type: PAY_REQUEST, date: '+ dt +',pay_to: ' + pay_to_addr +',amount: ' + amt + ',comment: ' + pay_msg

        # Write QR
        qr_c = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_c.add_data(qr_text)
        qr_c.make(fit=True)

        img = qr_c.make_image(fill_color="black", back_color="white")

        #img = qrcode.make(qr_text)
        fn = "requests.png"
        img.save(resource_path("QRCodes/"+fn))

        # Show QR
        msg_box_15 = QtWidgets.QMessageBox()
        msg_box_15.setIconPixmap(QPixmap(resource_path("QRCodes/"+fn)))
        msg_box_15.setInformativeText('Scan QR code here.')
        msg_box_15.setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
        ret = msg_box_15.exec()

        # Save QR elsewhere for convenient sharing.
        if ret == QtWidgets.QMessageBox.Save:
            dir = QDir.homePath()
            dlg = QtWidgets.QFileDialog()
            dlg.setDefaultSuffix(".padding")
            filename = (dlg.getSaveFileName(None, "Save QR", dir + "/" + fn, "*.png"))[0]
            if filename:
                img.save(resource_path(filename))

        elif ret == QtWidgets.QMessageBox.Cancel:
            return

        window.label_26.setText(_translate("MainWindow","Share the QR code you saved with the party you are requesting payment from."))
        window.label_26.setStyleSheet("font: 15pt 'Gill Sans'")

    elif clicked_widget.objectName() == 'address_gen_btn':
        if not pktwllt_synching(wlltinf.get_inf(uname, pwd)) == "True" or worker_state_active['FOLD_WALLET']:
            get_new_address(uname, pwd, window, worker_state_active, threadpool)
        else:
            msg = 'Wallet is syncing, this will not work until sync is complete.'
            sync_msg(msg)

    elif clicked_widget.objectName() == 'pwd_cancel_btn':
        window.lineEdit_4.clear()
        window.lineEdit_5.clear()
        window.lineEdit_10.clear()

    elif clicked_widget.objectName() == 'pwd_ok_btn':
        old_pass = window.lineEdit_10.text().strip()
        new_pass = window.lineEdit_4.text().strip()
        new_pass_cfm = window.lineEdit_5.text().strip()

        if old_pass.isalnum() and new_pass.isalnum() and new_pass_cfm.isalnum():

            if new_pass_cfm != new_pass:
                msg_box_12 = QtWidgets.QMessageBox()
                msg_box_12.setText('Make sure your new password matches your password confirmation.')
                msg_box_12.exec()
            else:
                if worker_state_active['PASS_CHNG'] == False:
                    print('attempt to change old_pass password')
                    change_pass(old_pass, new_pass)
                    
        else:
            msg_box_12 = QtWidgets.QMessageBox()
            msg_box_12.setText('Make sure your passwords are alphanumeric.')
            msg_box_12.exec()

    elif clicked_widget.objectName() == 'address_gen_btn2':
        window.address_line.clear()
        i = window.stackedWidget.indexOf(window.address_create_page)
        window.stackedWidget.setCurrentIndex(i)
        inf_msg_box = QtWidgets.QMessageBox()
        inf_msg_box.setText('Just click generate to create an address.')
        inf_msg_box.exec()

    elif clicked_widget.objectName() == 'all_addr_btn' and not worker_state_active['GET_ADDRESS']:
        window.balance_tree.clear()
        item_1 = QtWidgets.QTreeWidgetItem(window.balance_tree)
        window.balance_tree.topLevelItem(0).setText(0, _translate("MainWindow", "Loading..."))
        i = window.stackedWidget.indexOf(window.balance_page)
        window.stackedWidget.setCurrentIndex(i)
        add_addresses(['all'])

    elif clicked_widget.objectName() == 'bal_addr_btn' and not worker_state_active['GET_ADDRESS']:
        window.balance_tree.clear()
        item_1 = QtWidgets.QTreeWidgetItem(window.balance_tree)
        window.balance_tree.topLevelItem(0).setText(0, _translate("MainWindow", "Loading..."))
        add_addresses(['balances'])

    elif clicked_widget.objectName() == 'multi_create_btn':
        global multisig_trans
        window.label_65.clear()
        pay_dict2 = {}
        address = str(window.comboBox_2.currentText())
        FEE = window.lineEdit_3.text()
        is_valid = True
        for i in rcp_list_dict2:
            pay_to = rcp_list_dict2[i].lineEdit_6.text().strip()
            amt = rcp_list_dict2[i].send_amt_input.text().strip()
            amt_isnum = False

            if pay_to == address:
                msg_box_17 = QtWidgets.QMessageBox()
                msg_box_17.setText('Cannot submit transaction. Payee and payer must be different.')
                msg_box_17.exec()
                is_valid = False
                return

            try:
                amt = float(amt)
                amt_isnum = True

            except:
                amt_isnum = False

            if amt_isnum and pay_to.isalnum():
                pay_dict2[pay_to] = amt

            else:
                msg_box_17 = QtWidgets.QMessageBox()
                msg_box_17.setText('Cannot submit transaction. Make sure all payees have a valid address and amount.')
                msg_box_17.exec()
                is_valid = False
                return

        if len(rcp_list_dict2) > 0:

            #Get passphrase
            if passphrase == '':
                passphrase, ok = get_pass()
            else:
                ok = True

            if ok:
                result = createMultiSigTrans.create(uname, pwd, amt, address, pay_dict2, FEE, passphrase, window)
                err_result = str(result).split(':')[0]
                if err_result == "Error":
                    msg_box_18 = QtWidgets.QMessageBox()
                    msg_box_18.setText(result)
                    msg_box_18.exec()
                else:
                    window.multi_sign_btn2.setEnabled(True)
                    #QR gen
                    global multisig_trans
                    multisig_trans = str(result)
                    trans_len = len(bytes.fromhex(result.strip()))

                    if trans_len <= 1276:
                        qr_text = 'qr_type: MULTISIG_TRANS, transactions:' + multisig_trans.strip('\n')
                        qr_c = qrcode.QRCode(
                            version=25,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=4,
                        )
                        qr_c.add_data(qr_text)
                        qr_c.make(fit=True)

                        img = qr_c.make_image(fill_color="black", back_color="white")
                        #img = qrcode.make(qr_text)
                        fn = "multitrans.png"
                        img.save(resource_path("QRCodes/"+fn))
                        msg_box = QtWidgets.QMessageBox()
                        msg_box.setText('Scan QR code here, or use "Show Details" to copy transaction.')
                        qr = QPixmap(resource_path("QRCodes/"+fn))
                        msg_box.setIconPixmap(qr.scaled(QSize(400,400), Qt.KeepAspectRatio))
                        msg_box.setDetailedText(str(result))
                        msg_box.setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
                        ret = msg_box.exec()

                        if ret == QtWidgets.QMessageBox.Save:
                            try:
                                dir = QDir.homePath()
                                dlg = QtWidgets.QFileDialog()
                                dlg.setDefaultSuffix(".padding")
                                filename = (dlg.getSaveFileName(None, "Save QR", dir + "/" + fn,"", " (.png)"))[0]

                                if filename:
                                    img.save(resource_path(filename))
                            except:
                                return

                        elif ret == QtWidgets.QMessageBox.Cancel:
                            return
                    else:
                        i = window.stackedWidget.indexOf(window.raw_multi_trans_page)
                        window.stackedWidget.setCurrentIndex(i)
                        window.raw_mult_trans.clear()
                        window.raw_mult_trans.setText(multisig_trans)

            else:
                msg_box_18= QtWidgets.QMessageBox()
                msg_box_18.setText('You must enter your wallet passphase to submit transaction')
                msg_box_18.exec()

    elif clicked_widget.objectName() == 'import_trans_btn':
        import_qr()

    elif clicked_widget.objectName() == 'multi_sign_btn':
        raw_trans = (str(window.trans_text.toPlainText())).strip()
        
        if passphrase == '':
            passphrase, ok = get_pass()
        else:
            ok = True

        if ok:
            result = signMultiSigTrans.create(uname, pwd, raw_trans, passphrase, window)
            err_result = str(result).split(':')[0]

            if err_result == "Error":
                msg_box_19 = QtWidgets.QMessageBox()
                msg_box_19.setText(result)
                msg_box_19.exec()
            else:
                window.signed_text.setText(result)
                signed_multisig_trans = str(result)
                qr_text = 'qr_type: SIGNED_MULTISIG_TRANS, transactions: ' + signed_multisig_trans
                #print('qr_text', qr_text)
                try:
                    trans_len = len(bytes.fromhex(signed_multisig_trans))
                    if trans_len <= 1276:
                        qr_c = qrcode.QRCode(
                            version=25,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=4,
                        )
                        qr_c.add_data(qr_text)
                        qr_c.make(fit=True)

                        img = qr_c.make_image(fill_color="black", back_color="white")

                        #img = qrcode.make(qr_text)
                        fn = "signed-multitrans.png"
                        img.save(resource_path("QRCodes/"+fn))
                        msg_box_20 = QtWidgets.QMessageBox()
                        msg_box_20.setText('Scan QR code here, or use "Show Details" to copy transaction.')
                        qr = QPixmap(resource_path("QRCodes/"+fn))
                        msg_box_20.setIconPixmap(qr.scaled(QSize(400,400), Qt.KeepAspectRatio))
                        msg_box_20.setDetailedText(str(result))
                        msg_box_20.setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
                        ret = msg_box_20.exec()

                        if ret == QtWidgets.QMessageBox.Save:
                            dir = QDir.homePath()
                            dlg = QtWidgets.QFileDialog()
                            dlg.setDefaultSuffix(".padding")
                            filename = (dlg.getSaveFileName(None, "Save QR", dir + "/" + fn, "*.png"))[0]

                            if filename:
                                img.save(resource_path(filename))

                        elif ret == QtWidgets.QMessageBox.Cancel:
                            return
                except:
                    return

        else:
            msg_box_19 = QtWidgets.QMessageBox()
            msg_box_19.setText('You must enter your wallet passphase to submit transaction')
            msg_box_19.exec()

    elif (clicked_widget.objectName() == 'multi_sign_btn2') or (clicked_widget.objectName() == 'multi_sign_btn3'):
        i = window.stackedWidget.indexOf(window.load_sign_verify_page)
        window.stackedWidget.setCurrentIndex(i)

        try:
            window.trans_text.clear()
            window.signed_text.clear()
            window.signed_text.repaint()
            window.label_66.clear()
            window.trans_text.setText(multisig_trans)
            window.trans_text.repaint()
            window.trans_text.setPlaceholderText("Use import button to import multisig transactions here, or copy and paste them in.")
            msg_box_2 = QtWidgets.QMessageBox()
            msg_box_2.setText('Your multisig transaction has been auto-populated here. Just click sign to sign the transaction.')
            msg_box_2.exec()
        except:
            window.trans_text.setPlaceholderText("Could not auto-populate multisig transaction. You must create a transaction first. If a transaction was created, use import button to load it.")#Use import transaction from menu or paste raw transaction here.

    elif clicked_widget.objectName() == 'multi_send_btn':

        #required_sigs = True
        msg_box_3 = QtWidgets.QMessageBox()
        msg_box_3.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        snd_yes_btn = msg_box_3.button(QtWidgets.QMessageBox.Yes)
        snd_no_btn = msg_box_3.button(QtWidgets.QMessageBox.No)
        raw_trans = (str(window.signed_text.toPlainText())).strip()
        result = sendMultiSigTrans.create(uname, pwd, FEE, raw_trans, window)
        err_result = str(result["result"]).split(':')[0]

        if err_result == "Error":
            msg_box_19 = QtWidgets.QMessageBox()
            msg_box_19.setText(result["result"])
            msg_box_19.exec()

        elif err_result == "Cancel":
            return

        else:
            i = window.stackedWidget.indexOf(window.sent_page)
            window.stackedWidget.setCurrentIndex(i)
            window.lineEdit_7.setText(result["result"])
            window.textEdit_4.setText(result["details"])

    elif clicked_widget.objectName() == 'snd_btn':
        global pay_dict

        if not worker_state_active['FOLD_WALLET']:
           
            #Get passphrase
            if passphrase == '':
                passphrase, ok = get_pass()
            else:
                ok = True

            if ok:

                pay_dict = {}
                address = str(window.pay_from_combo_box.currentText())
                msg_box_3d = QtWidgets.QMessageBox()
                is_valid = True
                for i in rcp_list_dict:
                    pay_to = rcp_list_dict[i].lineEdit_6.text().strip()
                    amt = rcp_list_dict[i].send_amt_input.text().strip()


                    if pay_to == address:
                        msg_box_3d.setText('Cannot submit transaction. Payee and payer must be different.')
                        msg_box_3d.exec()
                        is_valid = False
                        return


                    amt_isnum = False
                    try:
                        amt = float(amt)
                        amt_isnum = True
                    except:
                        amt_isnum = True

                    if amt_isnum and pay_to.isalnum():
                        pay_dict[pay_to] = amt

                    else:
                        msg_box_3d.setText('Cannot submit transaction. Make sure all payees have a valid address and amount.')
                        msg_box_3d.exec()
                        is_valid = False
                        return

                if is_valid:
                    msg_box_3b = QtWidgets.QMessageBox()
                    msg_box_3b.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
                    msg_box_3b.setDefaultButton(QtWidgets.QMessageBox.Yes)
                    snd_yes_btn = msg_box_3b.button(QtWidgets.QMessageBox.Yes)
                    snd_no_btn = msg_box_3b.button(QtWidgets.QMessageBox.No)
                    msg_box_3b.setText('Are you sure you \nwish to send?')
                    msg_box_3b.exec()

                    if msg_box_3b.clickedButton() == snd_yes_btn:
                        send.execute2(uname, pwd, address, passphrase, pay_dict, window, worker_state_active)
                        
            else:
                msg_box_3a = QtWidgets.QMessageBox()
                msg_box_3a.setText('You must enter your wallet passphase to submit transaction')
                msg_box_3a.exec()

    elif clicked_widget.objectName() == 'import_keys_btn':
        txt = window.import_text.toPlainText()
        keys = txt.replace('\n',' ').split()

        if passphrase == '':
            passphrase, ok = get_pass()
        else:
            ok = True

        if ok:
            ingest.all_keys(uname, pwd, keys, passphrase, window, worker_state_active, threadpool)

    elif clicked_widget.objectName() == 'send_comb_btn':
        msg_box_3b = QtWidgets.QMessageBox()
        msg_box_3b.setText('You do not have the required number of signatures to submit this transaction.')
        msg_box_3b.exec()

    elif clicked_widget.objectName() == 'rtr_prvk_btn':
        address = str(window.comboBox_5.currentText())
     
        if passphrase == '':
            passphrase, ok = get_pass()
        else:
            ok = True

        if ok:

            if address[0] == 'P':
                msg_box_10 = QtWidgets.QMessageBox()
                msg_box_10.setText("Can't retrieve private key for multisig address.")
                msg_box_10.exec()
                return

            if address.isalnum() and passphrase.isalnum():
                get_priv_key(address, passphrase)
            else:
                msg_box_10 = QtWidgets.QMessageBox()
                msg_box_10.setText('Make sure to select and address and enter your wallet passphrase to retrieve your private key.')
                msg_box_10.exec()

    elif clicked_widget.objectName() == 'rtr_pubk_btn':
        address = str(window.addr_combo.currentText())
        if address[0] == 'P':
            msg_box_11 = QtWidgets.QMessageBox()
            msg_box_11.setText("Can't retrieve public key for multisig address.")
            msg_box_11.exec()
            return
        if address.isalnum():
            get_pub_key(address)
        else:
            msg_box_11 = QtWidgets.QMessageBox()
            msg_box_11.setText('Make sure to select and address  to retrieve your public key.')
            msg_box_11.exec()

    elif clicked_widget.objectName() == 'combine_trans_btn':
        signed_trans_list = window.add_trans_txt.toPlainText()
        signed_trans_arr = signed_trans_list.split('\n')
        signed_trans_arr = [item for item in signed_trans_arr if item!='']
        result = "Unable to combine transactions."#combineSigned.combine(uname, pwd, window, signed_trans_arr)
        multi_comb_trans = str(result)
        window.combine_trans_txt.setText(multi_comb_trans)
        window.combine_trans_txt.repaint()

        try:
            trans_len = len(bytes.fromhex(result))
            qr_text = 'qr_type: COMBINED_MULTISIG_TRANS, transactions: ' + multi_comb_trans
            if trans_len <= 1276:
                qr_c = qrcode.QRCode(
                    version=25,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr_c.add_data(qr_text)
                qr_c.make(fit=True)

                img = qr_c.make_image(fill_color="black", back_color="white")
                #img = qrcode.make(qr_text)

                fn = "combined-multitrans.png"
                img.save(resource_path("QRCodes/"+fn))
                msg_box_22 = QtWidgets.QMessageBox()
                msg_box_22.setText('Scan QR code here, or use "Show Details" to copy the combined multisig transaction.')
                qr = QPixmap(resource_path("QRCodes/"+fn))
                msg_box_22.setIconPixmap(qr.scaled(QSize(400,400), Qt.KeepAspectRatio))
                msg_box_22.setDetailedText(str(multi_comb_trans))
                msg_box_22.setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
                ret = msg_box_22.exec()

                try:
                    if ret == QtWidgets.QMessageBox.Save:
                        dir = QDir.homePath()
                        dlg = QtWidgets.QFileDialog()
                        dlg.setDefaultSuffix(".padding")
                        filename = (dlg.getSaveFileName(None, "Save QR", dir + "/" + fn, "*.png"))[0]

                        if filename:
                            img.save(resource_path(filename))

                    elif ret == QtWidgets.QMessageBox.Cancel:
                        return

                except:
                    print("QR operation failed")
        except:
            return

    elif clicked_widget.objectName() == 'combine_send_btn':
        window.label_69.clear()
        if not worker_state_active['FOLD_WALLET']:
            try:
                multi_comb_trans = window.combine_trans_txt.toPlainText()
                result = sendCombMultiSigTrans.create(uname, pwd, FEE, multi_comb_trans, window)
                err_result = str(result["result"]).split(':')[0]

                if err_result == "Error":
                    msg_box_22 = QtWidgets.QMessageBox()
                    msg_box_22.setText(result["result"])
                    msg_box_22.exec()

                elif err_result == "Cancel":
                    return

                else:
                    i = window.stackedWidget.indexOf(window.sent_page)
                    window.stackedWidget.setCurrentIndex(i)
                    window.lineEdit_7.setText(result["result"])
                    window.textEdit_4.setText(result["details"])
            except:
                msg_box_22 = QtWidgets.QMessageBox()
                msg_box_22.setText("Transaction send failed. Check that all necessary signatures have been combined.")
                msg_box_22.exec()
                window.label_69.setText("Transaction send failed. Check that all necessary signatures have been combined.")

    elif clicked_widget.objectName() == 'load_trns_btn' and not worker_state_active['TRANS']:
        get_transactions()
        #msg_box_27 = QtWidgets.QMessageBox()
        #msg_box_27.setText("Loading...")
        #msg_box_27.exec()


def menubar_released(self):
    global FEE, passphrase
    clicked_item = window.sender().objectName()
    #print('pressed menubar item', clicked_item)
    if clicked_item == 'actionAddress_2':
        window.address_line.clear()
        #window.pubkey_line.clear()
        i = window.stackedWidget.indexOf(window.address_create_page)
        window.stackedWidget.setCurrentIndex(i)
        inf_msg_box = QtWidgets.QMessageBox()
        inf_msg_box.setText('Just click generate to create an address.')
        inf_msg_box.exec()

    elif clicked_item == 'actionMultiSig_Address':
        i = window.stackedWidget.indexOf(window.multisig_create_page)
        init_multisig()
        window.stackedWidget.setCurrentIndex(i)
        msg_box_8 = QtWidgets.QMessageBox()
        msg_box_8.setText('Select "Add Public Key" to add more signatures to your multisig address.')
        msg_box_8.exec()

    elif clicked_item == 'actionCreate_Transaction':
        init_multi_rcp()
        set_fee_est()
        window.label_55.setText("Generate a raw multisig transaction here.")
        window.label_65.clear()
        window.multi_sign_btn2.setEnabled(False)
        i = window.stackedWidget.indexOf(window.multisig_send_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionPassword':
        window.lineEdit_10.clear()
        window.lineEdit_4.clear()
        window.lineEdit_5.clear()
        i = window.stackedWidget.indexOf(window.password_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionSave':
        wallet_file = str(wallet_db)
        save_dir = QDir.homePath()
        name = "wallet.db"
        dlg = QtWidgets.QFileDialog()
        dlg.setDefaultSuffix(".db")
        filename = str(dlg.getSaveFileName(None, "save file", save_dir + "/" + name,"", "DB (.db)")[0])

        try:
            copyfile(wallet_file, filename)
        except:
            print('Wallet file could not be copied.')


    elif clicked_item == 'actionDelete':
        wallet_file = wallet_db

        if wallet_file != '':
            msg_box_5 = QtWidgets.QMessageBox()
            text = 'Are you sure you wish to delete this wallet?\n'# + wallet_file
            msg_box_5.setText(text)
            msg_box_5.setWindowTitle("Delete Wallet")
            del_yes = QtWidgets.QMessageBox.Yes
            del_no = QtWidgets.QMessageBox.No
            msg_box_5.setStandardButtons(del_yes | del_no)
            msg_box_5.setDefaultButton(del_yes)
            ret = msg_box_5.exec()
            del_msg_box = QtWidgets.QMessageBox()
            del_msg_box.setWindowTitle("Wallet Delete Status")
            success = False

            if (ret == QtWidgets.QMessageBox.Yes):
                print("Deleting wallet.")
                success = True
                try:
                    os.remove(wallet_file)
                    msg = "Wallet Deleted. \n\nDo you wish to set up a new wallet?"
                    cont_yes = QtWidgets.QMessageBox.Yes
                    cont_no = QtWidgets.QMessageBox.No
                    del_msg_box.setStandardButtons(cont_yes | cont_no)
                    del_msg_box.setDefaultButton(cont_yes)
                except:
                    msg = "Wallet not deleted."
                    print(msg)

            elif (ret == QtWidgets.QMessageBox.No):
                msg = "Wallet not deleted."
                print(msg)

            del_msg_box.setText(msg)
            cont = del_msg_box.exec()

            if cont == QtWidgets.QMessageBox.Yes and success:
                # Kill wallet, then restart it
                global AUTO_RESTART_WALLET
                if os_sys == 'Linux' or os_sys == 'Darwin':
                    try:
                        subprocess.call(['pkill', 'SIGINT', 'wallet'], shell=False)
                        AUTO_RESTART_WALLET = True
                    except:
                        sys.exit()

                elif os_sys == 'Windows':
                    try:
                        os.system("taskkill /f /im  wallet.exe")
                        AUTO_RESTART_WALLET = True
                    except:
                        sys.exit()

                window.menu_frame.hide()
                window.menubar.setEnabled(False)
                i = window.stackedWidget.indexOf(window.new_wallet_page)
                window.stackedWidget.setCurrentIndex(i)

            elif cont == QtWidgets.QMessageBox.No and success:
                exit_handler()
                sys.exit()

    elif clicked_item == 'actionPay_to_Many':
        window.label_6.clear()
        i = window.stackedWidget.indexOf(window.send_page)
        window.stackedWidget.setCurrentIndex(i)
        msg_box_1 = QtWidgets.QMessageBox()
        msg_box_1.setText('Select "Add Recipients" below to pay to multiple addresses.')
        msg_box_1.exec()

    elif clicked_item == 'actionFrom_Text_2':
        window.trans_text.clear()
        window.signed_text.clear()
        window.label_66.clear()
        i = window.stackedWidget.indexOf(window.load_sign_verify_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionFrom_QR_Code':
        import_qr()

    elif clicked_item == 'actionFold_Address':
        window.label_77.clear()
        i = window.stackedWidget.indexOf(window.fold_page_1)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionWebsite':
        url = QUrl('https://github.com/artrepreneur/PKT-Cash-Wallet')
        if not QDesktopServices.openUrl(url):
            QMessageBox.warning(self, 'Open Url', 'Could not open url')
    
    elif clicked_item == 'actionManual_Resync':
        sync_msg("Wallet Resync Starting. This could take a while.")
        resync.execute(uname, pwd, window, worker_state_active, threadpool)

    elif clicked_item == 'actionSeed':
        if passphrase == '':
            passphrase, ok = get_pass()
        else:
            ok = True

        if ok:
            try:
                window.seed_txt_2.clear()
                seed = getSeed.execute(uname, pwd, passphrase, window, worker_state_active) #, threadpool
                if seed:
                    window.seed_txt_2.setText(seed)
                    i = window.stackedWidget.indexOf(window.get_seed_page)
                    window.stackedWidget.setCurrentIndex(i)

            except:
                print('Wrong wallet passphrase entered.')
                msg_box_13 = QtWidgets.QMessageBox()
                msg_box_13.setText('Wrong wallet passphrase entered.')
                msg_box_13.exec()


    elif clicked_item == 'actionSign_Verify_Message' or clicked_item == 'actionCreate_Transaction':
        i = window.stackedWidget.indexOf(window.load_sign_verify_page)
        window.trans_text.clear()
        window.signed_text.clear()
        window.label_66.clear()
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionCombine_Multisig_Transactions':
        i = window.stackedWidget.indexOf(window.combine_multi_page)
        window.add_trans_txt.clear()
        window.combine_trans_txt.clear()
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionExport_Private_Key':
        i = window.stackedWidget.indexOf(window.export_keys_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionImport_Keys':
        i = window.stackedWidget.indexOf(window.import_page)
        window.import_text.clear()
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionInformation_2':

        info = wlltinf.get_inf(uname, pwd)
        if info:
            try:
                window.ver.setText(VERSION_NUM)
                window.blks.setText(str(info["CurrentHeight"]))
                window.dsync.setText(str(info["IsSyncing"]))
                window.isync.setText(str(info["WalletStats"]["Syncing"]))
                window.bstp.setText(str(info["CurrentBlockTimestamp"]))
                window.bhsh.setText(str(info["CurrentBlockHash"]))
            except:
                print('Unable to get wallet info\n')
        else:
            msg_box_14 = QtWidgets.QMessageBox()
            msg_box_14.setText('Your wallet information could not be retrieved. Please wait for wallet to sync and retry.')
            msg_box_14.exec()

        i = window.stackedWidget.indexOf(window.information_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionGet_Public_Key':
        i = window.stackedWidget.indexOf(window.pubkey_page)
        window.pk_line.clear()
        window.stackedWidget.setCurrentIndex(i)
        #window.addr_combo.addItems(['Loading addresses ...'])

    elif clicked_item == 'actionGet_Private_Key':
        i = window.stackedWidget.indexOf(window.privkey_page)
        #window.lineEdit_9.clear()
        window.lineEdit_8.clear()
        window.stackedWidget.setCurrentIndex(i)
        #window.comboBox_5.addItems(['Loading addresses ...'])

    elif clicked_item == 'actionEncrypt_Decrypt_Message':
        i = window.stackedWidget.indexOf(window.enc_msg_page)
        window.textEdit_2.clear()
        window.textEdit_3.clear()
        window.stackedWidget.setCurrentIndex(i)

def import_qr2():
    dir = QDir.homePath()
    dlg2 = QtWidgets.QFileDialog()
    filename = dlg2.getOpenFileName(None, _translate("MainWindow","Open QR"), dir + "/", "*.png")

    try:
        qr_dict = {}
        qr_data = str((decode(Image.open(filename[0]))[0].data).decode('utf-8')).split(',')

        for i, item in enumerate(qr_data):
            item_list = item.split(':')
            key = item_list[0].strip()
            val = item_list[1].strip()
            qr_dict[key] = val

        if qr_dict['qr_type'] == 'SIGNED_MULTISIG_TRANS':
            window.combine_trans_txt.clear()
            i = window.stackedWidget.indexOf(window.combine_multi_page)
            window.stackedWidget.setCurrentIndex(i)
            transactions = qr_dict['transactions']
            window.add_trans_txt.append(transactions+'\n\n')
        elif qr_dict['qr_type'] == 'COMBINED_MULTISIG_TRANS':
            window.combine_trans_txt.clear()
            i = window.stackedWidget.indexOf(window.combine_multi_page)
            window.stackedWidget.setCurrentIndex(i)
            transactions = qr_dict['transactions']
            window.combine_trans_txt.setText(transactions)

    except:
        print("Unable to retrieve QR File")
        window.add_trans_txt.setPlaceholderText("QR not a valid signed multisig transaction.")

    return

def import_qr():
    dir = QDir.homePath()
    dlg2 = QtWidgets.QFileDialog()
    filename = dlg2.getOpenFileName(None, _translate("MainWindow","Open QR"), dir + "/", "*.png")
    try:
        qr_dict = {}
        qr_data = str((decode(Image.open(filename[0]))[0].data).decode('utf-8')).split(',')
        for i, item in enumerate(qr_data):
            item_list = item.split(':')
            key = item_list[0].strip()
            val = item_list[1].strip()
            qr_dict[key] = val

        if qr_dict['qr_type'] == 'PAY_REQUEST':
            window.label_6.clear()
            i = window.stackedWidget.indexOf(window.send_page)
            window.stackedWidget.setCurrentIndex(i)
            init_send_rcp()
            pay_to = list(rcp_list_dict.values())[0].lineEdit_6.setText(qr_dict['pay_to'])
            amt = list(rcp_list_dict.values())[0].send_amt_input.setText(qr_dict['amount'])

        elif qr_dict['qr_type'] == 'MULTI_PAY_REQUEST':
            window.label_65.clear()
            i = window.stackedWidget.indexOf(window.multisig_send_page)
            window.stackedWidget.setCurrentIndex(i)
            init_multi_rcp()
            pay_to = list(rcp_list_dict2.values())[0].lineEdit_6.setText(qr_dict['pay_to'])
            amt = list(rcp_list_dict2.values())[0].send_amt_input.setText(qr_dict['amount'])

        elif qr_dict['qr_type'] == 'MULTISIG_TRANS':
            window.trans_text.clear()
            window.signed_text.clear()
            window.label_66.clear()
            i = window.stackedWidget.indexOf(window.load_sign_verify_page)
            window.stackedWidget.setCurrentIndex(i)
            transactions = qr_dict['transactions']
            window.trans_text.setText(transactions)

        elif qr_dict['qr_type'] == 'SIGNED_MULTISIG_TRANS':
            window.trans_text.clear()
            window.signed_text.clear()
            window.label_66.clear()
            i = window.stackedWidget.indexOf(window.load_sign_verify_page)
            window.stackedWidget.setCurrentIndex(i)
            transactions = qr_dict['transactions']
            window.signed_text.setText(transactions)

        elif qr_dict['qr_type'] == 'COMBINED_MULTISIG_TRANS':
            window.combine_trans_txt.clear()
            i = window.stackedWidget.indexOf(window.combine_multi_page)
            window.stackedWidget.setCurrentIndex(i)
            transactions = qr_dict['transactions']
            window.combine_trans_txt.setText(transactions)

        elif qr_dict['qr_type'] == 'MULTI_QR':
            public_keys = qr_dict['public_keys'].split('|')
            m = qr_dict['m']
            window.multisig_list.clear()

            for i in range(len(public_keys)):
                item_line_x = QtWidgets.QListWidgetItem(window.multisig_list)
                item_line_x.setSizeHint(QSize(window.multisig_list.width() - 30, 60))
                window.multisig_list.addItem(item_line_x)
                item_nm = "m_pkline_"+ str(i+1)
                vars()[item_nm] = PKLine(str(i+1), item_line_x)
                window.multisig_list.setItemWidget(item_line_x, vars()[item_nm])
                pk_list_dict[item_nm] = vars()[item_nm]
                (pk_list_dict[item_nm]).pk_line.setText(public_keys[i])
            window.sig_box.setCurrentText(str(m))
            i = window.stackedWidget.indexOf(window.multisig_create_page)
            window.stackedWidget.setCurrentIndex(i)

    except:
        print("Unable to retrieve QR File")

    return


# Check if procs are running     
def chk_live_proc():
    proc_array = []
    print('Checking live processes, if any...\n')
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        #print('PROCS:', proc)
        if proc.info['name']=='wallet':
            proc_array.append('wallet')
        if proc.info['name']=='pktd':
            proc_array.append('pktd')
    return proc_array

def kill_procs(procs):
    global os_sys
    os_sys = platform.system()
    print('Trying to kill procs\n')
    if len(procs) > 0:
        if not SHUTDOWN_CYCLE: # At start up
            msg_box_X = QtWidgets.QMessageBox()
            proc_text = ('a ' + procs[0]) if len(procs) == 1 else ('a ' + procs[0] + ' and a '+ procs[1]) 
            text = 'You are running ' + proc_text + ' instance. Would you like to kill all instances?'
            msg_box_X.setText(text)
            msg_box_X.setWindowTitle("Kill Daemon")
            kill_yes = QtWidgets.QMessageBox.Yes
            kill_no = QtWidgets.QMessageBox.No
            msg_box_X.setStandardButtons(kill_yes | kill_no)
            msg_box_X.setDefaultButton(kill_yes)
            ret = msg_box_X.exec()

            if (ret == QtWidgets.QMessageBox.Yes):
                print('Restarting daemons...\n')
                kill_it()
            else:
               print('Quitting application...\n')
               sys.exit()

        else: # At shutdown
            if WALLET_COPY:
                msg_box_X = QtWidgets.QMessageBox()
                msg_box_X.setWindowTitle("Shutdown Delay")
                msg_box_X.setText("Can't shutdown, wallet still copying to magic stick.")
                ret = msg_box_X.exec()
                print("Magic wallet still copying, can't shutdown just yet.")
                
                i = 0
                while WALLET_COPY and not i == 20:
                    time.sleep(10)
                    i += 1
            
            kill_it()
            print('About to exit...\n')
            sys.exit()
             
                    
# !!
def kill_it():
    global AUTO_RESTART_WALLET, WALLET_COPY, ssh, passphrase_ok
    
    try:
        AUTO_RESTART_WALLET = False

        if os_sys == 'Linux' or os_sys == 'Darwin':
            subprocess.call(['pkill', 'SIGINT', 'wallet'], shell=False)
            subprocess.call(['pkill', 'SIGINT', 'pktd'], shell=False)

        elif os_sys == 'Windows':
            os.system("taskkill /f /im  wallet.exe")
            os.system("taskkill /f /im  pktd.exe")
                
        try:     
            if MAGIC_WALLET: 

                mgk_msg_box5 = QtWidgets.QMessageBox()
                mgk_msg_box5.setText("Do you wish to back up your wallet to your device?\n")
                mgk_msg_box5.setWindowTitle("Back Up Wallet")
                mgk_msg_box5.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
                ret = mgk_msg_box5.exec()

                if ret == QtWidgets.QMessageBox.Yes:    
                    print("Backing up Magic Wallet...\n")
                    
                    if passphrase == '':
                        passphrase_ok = True
                        set_passphrase()

                    WALLET_COPY = True
                    print("Reconnecting to magic wallet...\n")
                    ssh = ssh_2fa(connection)
                    res = put_magic_wllt(ssh, passphrase)
                    WALLET_COPY = False

                    # Delete local wallet?
                    mgk_msg_box6 = QtWidgets.QMessageBox()
                    mgk_msg_box6.setText("Do you wish to only store your wallet on your magic wallet device?\n")
                    mgk_msg_box6.setInformativeText("NOTE: Selecting yes means the only copy of you wallet will be on your device, and not on your desktop.")
                    mgk_msg_box6.setWindowTitle("Secure Wallet")
                    mgk_msg_box6.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
                    ret2 = mgk_msg_box6.exec()

                    if ret2 == QtWidgets.QMessageBox.Yes:
                        os.remove(wallet_file)
                else:
                    print("Sleeping another 10 seconds to be sure of graceful shutdown...\n")
                    time.sleep(10)
            else:
                print("Sleeping another 10 seconds to be sure of graceful shutdown...\n")
                time.sleep(10)    
        except:
            print("Unable to connect to magic wallet. \n")     
        
        return  

    except:
        print('Failed to clean up.')    


# Cleanup on exit
def exit_handler():
    print("Cleaning up...\n")       
    procs = chk_live_proc()
    if procs:
        kill_procs(procs)
    

def restart(proc):
    global COUNTER
    COUNTER = 0
    print('Process:', proc)
    rst_msg_box = QtWidgets.QMessageBox()
    if proc == "pktwallet":
        process = "PKT wallet"
    else:
        process = "PKT daemon"
    msg = process + ' has died, would you like to restart it?'
    rst_msg_box.setText(msg)
    rst_msg_box.setWindowTitle('Process Restart')
    rst_msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
    rst_ok_btn = rst_msg_box.button(QtWidgets.QMessageBox.Yes)
    rst_ok_btn.setText("Ok")
    ret = rst_msg_box.exec()

    if ret == QtWidgets.QMessageBox.Yes:
        try:
            if proc == "pktwallet":
                start_wallet_thread()
            else:
                start_pktd_thread()
                
        except:
            print("Process could not be restarted.")
            sys.exit()

    elif ret == QtWidgets.QMessageBox.Cancel:
        sys.exit()


# Thread PKT wallet
def start_wallet_thread():
    pktwallet_cmd_result = inv_pktwllt()
    worker = Worker(pktwllt_worker, pktwallet_cmd_result)
    worker.signals.result.connect(pktwllt_dead)
    threadpool.start(worker)

def pktwllt_dead():
    print('Wallet died\n')
    window.label_103.setPixmap(QPixmap(resource_path('img/red_btn.png')))
    window.label_106.setText('0%')
    if not SHUTDOWN_CYCLE:
        if not AUTO_RESTART_WALLET and wallet_db != '':
            restart('pktwallet')
        else:
            start_wallet_thread()
    
# Thread PKT Daemon
def start_pktd_thread():
    pktd_cmd_result = inv_pktd()
    worker = Worker(pktd_worker, pktd_cmd_result)
    worker.signals.result.connect(pktd_dead)
    threadpool.start(worker)

def get_correct_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def inv_pktd():
    global pktd_pid, pktd_cmd_result
    p = path.exists(get_correct_path("bin/pktd"))
    if p:
        print('Invoking PKTD...\n')
        pktd_cmd = "bin/pktd -u "+uname+" -P " +pwd+ " --txindex --addrindex"
        pktd_cmd_result = subprocess.Popen(resource_path(pktd_cmd), shell=True, stdout=subprocess.PIPE)
        pktd_pid = pktd_cmd_result.pid + 1
        return pktd_cmd_result
    else:
        sys.exit()    


def pktd_worker(pktd_cmd_result, progress_callback):
    print('Running PKTD Worker...\n')
    while (pktd_cmd_result.poll() is None or int(pktd_cmd_result.poll()) > 0) and not SHUTDOWN_CYCLE:
        output = str((pktd_cmd_result.stdout.readline()).decode('utf-8'))
        print('PKTD Output:', output)
    return

def pktd_dead():
    print('Daemon died \n')
    window.label_100.setPixmap(QPixmap(resource_path('img/red_btn.png'))) 
    window.label_105.setText('0%')
    if not SHUTDOWN_CYCLE:
        restart('pktd')

def inv_pktwllt():
    p = path.exists(get_correct_path("bin/wallet"))
    if p:
        print('Invoking PKT Wallet...\n')
        global pktwallet_pid, pktwallet_cmd_result
        pktwallet_cmd_result = subprocess.Popen([resource_path('bin/wallet'), '-u', uname, '-P', pwd, '--userpc', '--usespv'],  shell=False, stdout=subprocess.PIPE)
        pktwallet_pid = pktwallet_cmd_result.pid + 1
        pktwllt_stdout = str((pktwallet_cmd_result.stdout.readline()).decode('utf-8'))
        status = ''
    else:
        sys.exit()    

    # Loop until wallet successfully opens.
    while not ('Opened wallet' in status) and (pktwallet_cmd_result.poll() is None):
        pktwllt_stdout = str((pktwallet_cmd_result.stdout.readline()).decode('utf-8'))
        print('pktwllt_stdout:',pktwllt_stdout)
        if pktwllt_stdout:
            status = pktwllt_stdout   
    return pktwallet_cmd_result

def pktwllt_worker(pktwallet_cmd_result, progress_callback):
    print('Running PKT Wallet Worker...\n')

    # Watch the wallet to ensure it stays open.
    while True:
        output = str((pktwallet_cmd_result.stdout.readline()).decode('utf-8'))
        print('Wallet Output:', output)
        if not pktwallet_cmd_result.poll() is None or output =='' or SHUTDOWN_CYCLE:
            break    
    return

def start_daemon(uname, pwd):
    global pktd_pid, pktwallet_pid
    pktd_pid = 0
    pktwallet_pid = 0
    if wallet_db != '' and path.exists(wallet_db):
      
        try:
            start_pktd_thread()
            start_wallet_thread()
        except:
            print('Failed to invoke daemon.')
            exit_handler()
            sys.exit()

    else:
        try:
            global CREATE_NEW_WALLET
            print('Creating a new wallet...')
            CREATE_NEW_WALLET = True
            start_pktd_thread()
            window.menu_frame.hide()
            window.frame_4.hide()
            window.menubar.setEnabled(False)
            i = window.stackedWidget.indexOf(window.new_wallet_page)
            window.stackedWidget.setCurrentIndex(i)

        except:
            print('Failed to invoke pktd daemon.')
            exit_handler()
            sys.exit()

def make_executable():
    print('Checking permissions...\n')
    if not os.access("./bin/pktd", os.X_OK):
        result = subprocess.Popen('chmod 755 bin/*',shell=True, stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
        return
    else:
        return 

def check_status():
    worker = Worker(get_status)
    worker.signals.result.connect(status_dead)
    threadpool.start(worker)

def get_status(progress_callback):
    global COUNTER
    while True:
        if COUNTER % STATUS_INTERVAL == 0:
            status_light()
        else:
            COUNTER +=1
        if SHUTDOWN_CYCLE:
            break    
        time.sleep(1)
    return        

def status_dead():
    print("Status light loop died \n")

def status_light():
    global COUNTER
    COUNTER = 1
    pktd_pct = '0.0%'
    wllt_pct = '0.0%'
    #print('Checking status...')
    
    info = wlltinf.get_inf(uname, pwd)
    w_sync = pktwllt_synching(info)
    p_sync = pktd_synching(info)

    if not p_sync: # synched
        pktd_pct='100.0%'
        #print('pktd synced', pktd_pct)

    else: # not synched
        peerinfo = (peerinf.get_inf(uname, pwd))
        #print('peerinfo:', peerinfo)

        if len(peerinfo)>0:
            peerinfo = peerinfo[0]
            strt_height = peerinfo['startingheight']
            curr_height_1 = peerinfo['currentheight']
            print('Current Height', curr_height_1, 'Start Height:', strt_height)
            pct_d = round((curr_height_1 / strt_height ) * 100,1)
            pktd_pct = str(pct_d) + '%'
            print('PKTD PCT:', pktd_pct, '\n')
            #if pktd_pct=='100.0%':
            #    pktd_pct = '0.0%'

        else: # no data for peerinfo
            pktd_pct = '0.0%'             

    if not w_sync: # synched
        wllt_pct='100.0%'

    else: # not synched
        curr_height_2 = int(info['CurrentHeight'])
        bnd_height = int(info['BackendHeight'])
        print('Current Height', curr_height_2, 'Back End Height:', bnd_height)
        curr_height_2 = bnd_height if curr_height_2 > bnd_height else curr_height_2
        pct_w = round((curr_height_2 / bnd_height ) * 100,1)
        if pct_w > 100:
            pct_w = 100
        wllt_pct = str(pct_w) + '%'
        print('Wallet PCT:', wllt_pct)    
        #if wllt_pct=='100.0%':
        #    wllt_pct = '0.0%'    

    #print('Wallet Sync:', w_sync, 'Wallet Percent:',wllt_pct)
    #print('PKTD Sync:', p_sync, 'PKTD Percent:',  pktd_pct, '\n')

    window.label_105.setText(pktd_pct)
    window.label_106.setText(wllt_pct)
    window.label_103.setPixmap(QPixmap(resource_path('img/grn_btn.png'))) if (not w_sync and wllt_pct=='100.0%') else window.label_103.setPixmap(QPixmap(resource_path('img/ylw_btn.png')))   
    window.label_100.setPixmap(QPixmap(resource_path('img/grn_btn.png'))) if (not p_sync and pktd_pct=='100.0%') else window.label_100.setPixmap(QPixmap(resource_path('img/ylw_btn.png')))                                  

def get_wallet_db():
    wallet_db = ''
    get_db_cmd = "bin/getwalletdb"
    get_db_result = (subprocess.Popen(resource_path(get_db_cmd), shell=True, stdout=subprocess.PIPE).communicate()[0]).decode("utf-8")
    print('get_db_result:', get_db_result) 
    if get_db_result.strip() != "Path not found":    
        wallet_db = get_db_result.strip('\n')+'/wallet.db'
        print('Wallet location:', wallet_db)
    else:
        wallet_db = ''
    return wallet_db    

def clear_send_rcp():
    global rcp_list_dict, pay_dict

    keys = list(rcp_list_dict.keys())
    for key in keys:
        rcp_list_dict[key].del_clicked()

    # still clear last remaining fields here.
    if (rcp_list_dict):
        item = list(rcp_list_dict.values())[0]
        item.del_fields()

        # Clear out dict's
        pay_dict = {}

def clear_comb():
    window.add_trans_txt.clear()
    window.add_trans_txt.repaint()
    window.combine_trans_txt.clear()
    window.combine_trans_txt.repaint()
    window.add_trans_txt.setPlaceholderText("Use import button to import signed transactions here, or copy and paste them in.")
    i = window.stackedWidget.indexOf(window.combine_multi_page)
    window.stackedWidget.setCurrentIndex(i)

def clear_multi_rcp():
    global rcp_list_dict2, pay_dict2

    keys = list(rcp_list_dict2.keys())
    for key in keys:
        rcp_list_dict2[key].del_clicked()

    # still clear last remaining fields here.
    if (rcp_list_dict2):
        item = list(rcp_list_dict2.values())[0]
        item.del_fields()

        # Clear out dict's
        pay_dict = {}


def init_send_rcp():
    global rcp_list_dict, pay_dict
    window.rcp_list.clear()
    rcp_list_dict = {} # reset
    pay_dict = {}
    window.rcp_list.setAutoScrollMargin(5)
    window.rcp_list.setStyleSheet("margin: 0px")
    item_line_y = QtWidgets.QListWidgetItem(window.rcp_list)
    item_line_y.setSizeHint(QSize((window.rcp_list.width() - 30), window.rcp_list.height()))
    window.rcp_list.addItem(item_line_y)
    item_nm = "send_rcp_"+ str(1)
    vars()[item_nm] = SendRcp(str(1), item_line_y, item_nm)
    window.rcp_list.setItemWidget(item_line_y, vars()[item_nm])
    rcp_list_dict[item_nm] = vars()[item_nm]

def init_multi_rcp():
    global rcp_list_dict2, pay_dict2
    rcp_list_dict2 = {}
    pay_dict2 = {}
    window.rcp_list_2.clear()
    window.rcp_list_2.setAutoScrollMargin(5)
    item_line_z = QtWidgets.QListWidgetItem(window.rcp_list_2)
    item_line_z.setSizeHint(QSize((window.rcp_list_2.width() - 30), window.rcp_list_2.height()))
    window.rcp_list_2.addItem(item_line_z)
    item_nm = "multisig_rcp_"+ str(1)
    vars()[item_nm] = SendRcp(str(1), item_line_z, item_nm)
    window.rcp_list_2.setItemWidget(item_line_z, vars()[item_nm])
    rcp_list_dict2[item_nm] = vars()[item_nm]

def init_multisig():
    global pk_list_dict
    pk_list_dict = {}
    window.label_13.clear()
    window.label_13.setText("To create a multi signature address, enter the public keys of all the participants. Maximum of 12 allowed.")
    window.multisig_list.clear()
    for i in range(3):
        item_line_x = QtWidgets.QListWidgetItem(window.multisig_list)
        item_line_x.setSizeHint(QSize(window.multisig_list.width() - 30, 60))
        window.multisig_list.addItem(item_line_x)
        item_nm = "m_pkline_"+ str(i+1)
        vars()[item_nm] = PKLine(str(i+1), item_line_x)
        window.multisig_list.setItemWidget(item_line_x, vars()[item_nm])
        pk_list_dict[item_nm] = vars()[item_nm]

def add_mgk_btn():
    grid.addWidget(mgk_btn, 4, 0)
    window.frame_3.setMinimumHeight(300)
    window.frame.setMaximumHeight(250)

def init_side_menu():
    global mgk_btn, grid

    balance_btn = SideMenuBtn('Balances', ' Balances', 'pixmap_balance_btn', 'View Your Balances')
    send_btn = SideMenuBtn('Send', 'Send', 'pixmap_send_btn', 'Send PKT Cash')
    receive_btn = SideMenuBtn('Receive', 'Receive', 'pixmap_receive_btn', 'Receive PKT Cash')
    transaction_btn = SideMenuBtn('Transactions', '  Transactions', 'pixmap_transaction_btn', 'View Transaction History')
    mgk_btn = SideMenuBtn('Magic', '   Magic', 'pixmap_magic_btn', 'Connect Magic')
    grid = QtWidgets.QGridLayout(window.frame_3)
    grid.addWidget(balance_btn, 0, 0)
    grid.addWidget(send_btn, 1, 0)
    grid.addWidget(receive_btn, 2, 0)
    grid.addWidget(transaction_btn, 3, 0)
    grid.setSpacing(0)

    conn = ping(connection.host)
    print("***conn", connection.host, conn, path.exists(get_correct_path(".magic.cfg")), "\n")
    
    try:  
        if conn or path.exists(get_correct_path(".magic.cfg")):
            add_mgk_btn()
    except:
        print("Magic wallet not connected \n")   

    grid.setContentsMargins(0,0,0,0)
    window.frame_3.setLayout(grid)

def deactivate():
    window.receive_groupBox_2.hide()
    window.comboBox_3.hide()
    window.label_41.hide()
    window.multi_add_btn.hide()
    window.multi_clear_btn.hide()
    window.add_btn.hide()
    window.trns_status.hide()
    window.multi_amt_frame.setEnabled(False)
    window.label_9.setText('Enter Your Payee Below')
    window.label_17.setText('Enter Your Payee Below')
    window.actionPay_to_Many.setVisible(False)
    window.actionEncrypt_Decrypt_Message.setVisible(False)
    window.actionCombine_Multisig_Transactions.setVisible(False)

    # Fee related buttons
    window.fee_est2_btn.hide()
    window.fee_est_btn.hide()
    window.frame_2.hide()
    window.lineEdit_6.hide()

def init_size():
    window.setMinimumSize(1300, 800)
    #window.transaction_hist_tree.setStyleSheet("QTreeView::item { padding: 5px; background-color: rgb(201, 207, 207)}")
    window.stackedWidget.setCurrentIndex(0)
    window.balance_tree.header().setMinimumHeight(40)
    window.transaction_hist_tree.header().setMinimumHeight(40)
    window.receive_hist_tree2.header().setMinimumHeight(40)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# !! --

class connection:
    host = "magicwallet.local"
    port = 22
    username = "magic"
    password = "magicuser"
    fac_token = ""

def request_frm_bck_up():
    mgk_msg_box4 = QtWidgets.QMessageBox()
    mgk_msg_box4.setText("Do you wish to retrieve your wallet from your magic stick?\nIf so, click \"yes\"")
    mgk_msg_box4.setWindowTitle("Retrieve Wallet")
    mgk_msg_box4.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
    ret = mgk_msg_box4.exec()

    if ret == QtWidgets.QMessageBox.Yes:
        return True
    else:
        return False 

def get_magic_wllt(ssh, passphrase):
    global WALLET_COPY, AUTO_RESTART_WALLET, LOCAL_WALLET_PATH, progress_bar

    try:
           
        LOCAL_WALLET_PATH = wallet_db.strip('wallet.db')
        progress_bar = Pbar("get")
        progress_bar.exec()

        result = "Successfully retrieved wallet from device."

    except Exception as e:
        print("Couldn\'t copy wallet from back up:", e)
        result = "Failed to retrieve wallet from device."
        sys.exit() 

    print("about to close ssh")
    #ssh.close()
    print("closed ssh")
    print(result)

    #Restart wallet 
    os_sys = platform.system()
    
    if not SHUTDOWN_CYCLE:

            try:
                if os_sys == 'Linux' or os_sys == 'Darwin':
                    subprocess.call(['pkill', 'SIGINT', 'wallet'], shell=False)
                elif os_sys == 'Windows':
                    os.system("taskkill /f /im  wallet.exe")    
                AUTO_RESTART_WALLET = True
                
            except:
                sys.exit()
    WALLET_COPY = False   
    return result 


class Pbar(QtWidgets.QDialog):
  
    def __init__(self, type, *args, **kwargs):
        super(Pbar, self).__init__(*args, **kwargs)

        
        self.type = type
        self.label = QtWidgets.QLabel(self)
        self.label.setStyleSheet("font: 14pt Bold 'Gill Sans'")
        self.label.move(45,20)

        # Progress bar
        self.prog = QtWidgets.QProgressBar(self)
        self.prog.setGeometry(20, 50, 300, 50)
        self.prog.setMaximum(100)

        # Close button
        self.button = QtWidgets.QPushButton("Close", self)
        self.button.move(135, 90)
        self.button.setEnabled(False)
        self.button.clicked.connect(self.close_it)
     
        if self.type =="put":
            self.setWindowTitle("Backing Up Wallet")
            self.label.setText("Copying local wallet to magic wallet...")
        else:
            self.setWindowTitle("Retrieving Wallet")
            self.label.setText("Copying magic wallet to local wallet...")    
        
        self.show()
 
        self.scp = SCPClient(ssh.get_transport(), progress=self.progress)
        
        if self.type =="put":
            self.scp.put(f"{wallet_db}", REMOTE_WALLET_PATH)
        else:
            self.scp.get(REMOTE_WALLET_PATH + "/" + WALLET_NAME, LOCAL_WALLET_PATH)
        
    def progress(self, filename, size, sent):
        count = float(sent)/float(size)*100
        self.prog.setValue(count)
        QtWidgets.QApplication.processEvents()
        sys.stdout.write("%s's progress: %.2f%%   \r" % (f"{filename.decode('utf-8')}", count ))
      
        if count==100 and self:
            print("about to close scp")
            self.button.setEnabled(True)
            QtWidgets.QApplication.processEvents()

    def reset(self):
        self.prog.setValue(0)
        QtWidgets.QApplication.processEvents()

    def close_it(self):
        self.close()
        self.reject()      

def put_magic_wllt(ssh, passphrase):
    global WALLET_COPY, wallet_db, progress_bar
    result = ""

    # Check if local wallet exists
    if path.exists(wallet_db):

        try:
            progress_bar = Pbar("put")
            progress_bar.exec()

        except Exception as e:
            print("Couldn\'t connect, connection error:", e)
            result = "Failed to copy wallet to device"
    else:
        result = "Couldn\'t find local wallet.db file, exiting..."        

    WALLET_COPY = False     
    #ssh.close()
    print(result)
    return result
    
    return

# Does wallet.db exist on magic wallet? If so it's a first connect
def first_connect(ssh):
    cmd = "ls "+ REMOTE_WALLET_PATH +"/"+ WALLET_NAME +">> /dev/null 2>&1 && echo yes || echo no | tr -d '\n'"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    lines = stdout.readlines()
    if len(lines) > 1: 
        for line in lines:
            if "Too many logins" in lines:
                mgk_msg_box2 = QtWidgets.QMessageBox()
                mgk_msg_box2.setText("Too many logins on magic stick. If you are not logged into your stick through another ssh then your wallet has been compromised.")
                mgk_msg_box2.setWindowTitle("Magic Wallet Connection Denied")
                ret = mgk_msg_box2.exec()
                print('Too many logins on magic stick. If you are not logged into your stick through ssh then your wallet has been compromised.')
                sys.exit()
    else:
        line = lines[0]

        if line == 'yes':
            print('Wallet found on magic stick.\n')
            print('Lines:',lines) 
            return False

        elif line == 'no':
            print('No wallet found on magic stick.\n')
            # Check if a magic_cfg exists
            p = path.exists(get_correct_path(".magic.cfg"))
           
            if p:
                return False
            else:   
                return True

# Get the passphrase from the user.
def set_passphrase():
    global passphrase
    passphrase, ok = get_pass()
    passphrase = passphrase.strip()
    return passphrase


# Change password on magic wallet
def change_mgk_passphrase(passphrase, ssh):
    #command = "echo 'magic:"+passphrase+"' | sudo chpasswd "
    command = "python /home/magic/.chg_pwd.py " + passphrase
    stdin, stdout, stderr = ssh.exec_command(command)
    success = False
    lines = str((stdout.readlines())[0]).rstrip()

    if lines=="None":
        success = True
    else:
        print("Error changing password\n")
        success = False
    
    return success

# Setup 2fa on magic wallet
def setup_2fa(ssh):
    print("In setup_2fa...\n")
    success = False
    cmd_1 = "python /home/magic/.auth.py"
    stdin, stdout, stderr = ssh.exec_command(cmd_1)
    remote_res = stdout.readlines()[0] #.split('\n')
    print("Remote Res in 2fa:", remote_res)
    arr = (remote_res.split(",")[0]).split("|") 

    if len(arr) > 0: #and not stderr:
        success = True
        secret = arr[0].replace("('","")
        emer_scratch_codes = arr[1].split(";")
        ver_code = arr[2].replace("'", "")
        print("secret:", secret, "\nemer_scratch_codes:", emer_scratch_codes, "\nver_code:", ver_code, "\n")        
        
        # display QR for authy, and display emergency scratch codes.
        qr_text = 'otpauth://hotp/magic@magicwallet?secret=ELIUHFTUQICYEQBDOBG25QMWNE&issuer=magicwallet'
        
        # Write QR
        qr_c = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )

        qr_c.add_data(qr_text)
        qr_c.make(fit=True)

        img = qr_c.make_image(fill_color="black", back_color="white")

        fn = "2fa.png"
        img.save(resource_path("QRCodes/"+fn))

        # Show QR
        msg_box_QR = QtWidgets.QMessageBox()
        msg_box_QR.setIconPixmap(QPixmap(resource_path("QRCodes/"+fn)))
        msg_box_QR.setInformativeText('Scan QR code here.')
        ret = msg_box_QR.exec()

        # Delete
        os.remove(resource_path("QRCodes/"+fn)) 

        # Activate 2fa
        cmd_2 = "/home/magic/.activ8.sh"
        stdin, stdout, stderr = ssh.exec_command(cmd_2)
        remote_res = stdout.readlines()[0]
        if "Activating 2FA" in remote_res:
            print("Activated\n")
        print("***stdin, stdout, stderr", stdin, stdout, stderr, remote_res)  

    return success

def touch_config():
    # Touch local config
    print("Touching config file.\n")
    cmd = "touch .magic.cfg"
    result, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    result = result.decode('utf-8')
    err = err.decode('utf-8')

    if err:
        print(err,"\n")

def rem_config():
    print("Revoking config file.\n")
    cmd = "rm -rf ./.magic.cfg"
    result, err = (subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
    result = result.decode('utf-8')
    err = err.decode('utf-8')

    if err:
        print(err,"\n")

def start_magic_thread(ssh):
    global passphrase, WALLET_COPY
    WALLET_COPY = True
    success = magic_link(ssh, fc, passphrase)
    magic_complete(success)

# Compare file epoch timestamps
def compare_ts(file_1, file_2):
    if file_1 > file_2:
        return True 
    else:
        return False      


def magic_link(ssh, fc, passphrase): #, progress_callback):
    success = False
    res = ""

    if MAGIC_WALLET and CONNECTED and ssh:

        # If not shutdown_cycle
        if not SHUTDOWN_CYCLE:

            # On a first connect we just copy the local wallet to remote storage.
            if fc or path.exists(get_correct_path(".magic.cfg")):
                res = put_magic_wllt(ssh, passphrase)
            elif wallet_db == '':
                # no local wallet present, copy over the remote wallet
                res = get_magic_wllt(ssh, passphrase)
            else:
                # Let's check the timestamps of both (local/remote) and see which is newer, if remote is newer copy that 
                try:
                    cmd_1 = "date -r "+REMOTE_WALLET_PATH +"/"+ WALLET_NAME+" +%s"
                    stdin, stdout, stderr = ssh.exec_command(cmd_1)
                    remote_dt = str(stdout.readlines()[0]).split('\n')[0]

                    if remote_dt:
                        cmd_2 = "date -r '"+wallet_db+"' +%s"
                        local_dt, err = (subprocess.Popen(cmd_2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                        local_dt = local_dt.decode('utf-8')
                        err = err.decode('utf-8')

                        if not err:
                            
                            if int(remote_dt) > int(local_dt): 
                                print("Retrieving wallet from magic stick...\n")
                                res = get_magic_wllt(ssh, passphrase)
                            else:
                                print("Remote wallet not more recent than local wallet...\n")    
                        else:
                            print("No local wallet available.", err)
                            res = get_magic_wllt(ssh, passphrase)


                except Exception as exc:
                    res = "Failed"
                    print("Failed to retrieve wallet. Either a bad connection or an existing session is blocking connection.", exc)
                    
        else: 
            # Copy local wallet to remote
            res = put_magic_wllt(ssh, passphrase)

        if "Successfully" in res:
            success = True
        
        print("In magic link, RES:", res)
        return success            

# Sync is compelte
def magic_complete(success):
    global WALLET_COPY, AUTO_RESTART_WALLET
    print("In magic_complete, \"success\"", success)
    if success:
        print("Magic wallet sync process complete.")
    else:
        print("Magic wallet sync process failed.")
    AUTO_RESTART_WALLET = True    
    WALLET_COPY = False
    print("In magic wallet, \"WALLET_COPY:\"", WALLET_COPY)

# Connect to magic wallet once 2fa is setup    
def ssh_2fa(conn):
    global CONNECTED, passphrase, ssh

    password = passphrase if not passphrase =='' else conn.password
    fac_token = conn.fac_token
    hostname = conn.host
    port = conn.port
    username = conn.username    
    prmpt_str =""

    # Handler for server questions
    def answer_handler(title, instructions, prompt_list):
        answers = {
          'password': password,
          'verification_code': fac_token
        }

        resp = []
        for prmpt in prompt_list:
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
        CONNECTED = True  
        return ssh

    except Exception as exc:
        CONNECTED = False
        print('Exception:', exc)
        trans.set_keepalive(0)

        # Default failed
        if "Authentication failed" in str(exc):
            
            # Assume not first connect and collect all data required for 2fa
            if passphrase == "" or passphrase == "magicuser": 
                passphrase, ok = get_pass() 
            else:
                ok = True      

            if ok:
                passphrase = passphrase.strip()
                conn.password = passphrase
                
                if SHUTDOWN_CYCLE:
                    token, ok = QtWidgets.QInputDialog.getText(window, '2FA', 'Backing up your wallet...\n\nEnter your 2-factor authentication code:',QtWidgets.QLineEdit.Password)
                    
                else:
                    token, ok = QtWidgets.QInputDialog.getText(window, '2FA', 'Enter your 2-factor authentication code:',QtWidgets.QLineEdit.Password)
                
                if ok:
                    token = token.strip()
                    conn.fac_token = token
                    return ssh_2fa(conn)
                else:
                    ssh = "failed"
                    return ssh   
            
            else:
                ssh = "failed"
                return ssh

        # Authentication code failed.    
        elif "Bad authentication type" in str(exc):
            print("In bad authentication type...\n")
            token, ok = QtWidgets.QInputDialog.getText(window, '2FA', 'Enter your 2-factor authentication code:',QtWidgets.QLineEdit.Password)
                
            if ok:
                print("OK is true")
                token = token.strip()
                conn.fac_token = token
                return ssh_2fa(conn)
            else:
                print("Canceled back up...\n")
                ssh = "failed"
                return ssh

        else:
            print("Already connected to device, only one session allowed.\n")
            ssh = "failed"
            return ssh

# Connects to magic wallet in the default case, ie. no 2fa setup yet
def connect_magic_wllt(conn):
    global CONNECTED, passphrase
    
    print("In connect_magic_wllt... \n")
    if passphrase:
        conn.password = passphrase

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(conn.host, conn.port, conn.username, conn.password)
        print("Connected successfully.\n")
        CONNECTED = True
   
    except Exception as e:
        if conn.password == "magicuser":
            print("Couldn\'t connect with default password.", e,"\n")
        else: 
            print("Couldn\'t connect with password:", conn.password, e, "\n")

        CONNECTED = False
        passphrase, ok = get_pass()

        if ok:
            passphrase = passphrase.strip()
            conn.password = passphrase
            ssh = connect_magic_wllt(conn)
        else:
            ssh = "failed"

    return ssh        

# Is magic wallet attached?
def ping(host):
    res = False
    ping_param = "-n 1" if platform.system() == "Windows" else "-c 1"
    result = os.popen("ping " + ping_param + " " + host).read()
    print("result", result)
    if "ttl=" in str(result):
        res = True
    return res

def detect_magic_wllt(QtWidgets):
    global passphrase, MAGIC_WALLET, ssh, fc
    success = False
    # See if device attached
    conn = connection()

    try: 
        result = ping(conn.host)
    except:
        print("Magic wallet not connected...")

    mgk_msg_box = QtWidgets.QMessageBox()

    # If magic wallet is attached
    if result:
        MAGIC_WALLET = True
        p = path.exists(get_correct_path(".magic.cfg")) # Look for magic.cfg
        
        # If the config file doesn't exist we can't say for sure that this wallet has been setup yet
        if not p:
            print("Config file not present.\n")
            
            mgk_msg_box.setText("Have you already set up your magic wallet?")
            mgk_msg_box.setWindowTitle("Setup")
            mgk_msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            mgk_msg_box.setDefaultButton(QtWidgets.QMessageBox.Yes)
            ret = mgk_msg_box.exec()  

            if ret == QtWidgets.QMessageBox.Yes: # Config file is missing
                # We're fully  configured
                touch_config()
                success = True
                
            else:
                # Not configured,  wallet isn't setup
                ssh = connect_magic_wllt(conn) #Connect simplistically with the default password
                print("In detect magic wallet, ssh:", ssh)

                if not ssh == "failed": # we're connected
                    
                    fc = first_connect(ssh) # Check if first time connecting
                    
                    # On first connect set the magic passphrase, and local passphrase to be the same thing
                    if fc:
                        print("First time connecting. Setting new PWD and Backing up local wallet to magic stick...\n")
                        mgk_msg_box.setText("First time connecting.")
                        mgk_msg_box.setInformativeText("Setting new PWD and Backing up local wallet to magic stick. Click \"OK\" to continue.")
                        mgk_msg_box.setWindowTitle("First Connect")  
                        touch_config()

                        #set new passphrase
                        if not passphrase:
                            passphrase = set_passphrase()

                        res = change_pass(passphrase, passphrase) # Changing both passwords in one shot
                        print("Change password result:", res, "\n")

                        #set up 2fa
                        if res:
                            print("Setting up 2FA...\n")
                            res2 = setup_2fa(ssh)
                            
                            if res2: 
                                   
                                # Logout, so we can test the 2fa login    
                                ssh.close()  
 
                                success = True
                            
                            else:
                                rem_config()            
                        else: # it failed, revoke config
                            rem_config()

                else: # Connection failed, maybe wallet is partially set up. Lets ask user for wallet passphrase
                    conn_retry_msg()   
        else:
            # Config exists
            touch_config()
            success = True

        # Assume we are configured now so log back in
        if success:
            ssh = ssh_2fa(conn)
        
            # If the login succeeded
            if not ssh == "failed":
                fc = first_connect(ssh)
                #mgk_msg_box = QtWidgets.QMessageBox()
                mgk_msg_box.setText("Magic Wallet connected. Would you like to sync it?")
                mgk_msg_box.setWindowTitle("Connect Magic Wallet")
                mgk_msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
                mgk_msg_box.setDefaultButton(QtWidgets.QMessageBox.Yes)
                ret = mgk_msg_box.exec()

                # Start sync in separate thread
                if ret == QtWidgets.QMessageBox.Yes:
                    start_magic_thread(ssh)

    # If wallet isn't attached
    elif not result and MAGIC_WALLET:
        #mgk_msg_box = QtWidgets.QMessageBox()
        mgk_msg_box.setText("Magic Wallet not attached.")
        mgk_msg_box.setWindowTitle("Not Attached")            

def conn_retry_msg():
    mgk_msg_box2 = QtWidgets.QMessageBox()
    mgk_msg_box2.setText("Wallet failed to connect. Let\'s try that again.")
    mgk_msg_box2.setWindowTitle("Not Connected")  
        
# !! --

# ----- MAIN -----
if __name__ == "__main__":

    _translate = QCoreApplication.translate
    iteration = 0
    wallet_db = get_wallet_db()

    worker_state_active = {
        'GET_ADDRESS':False,
        'GET_BALANCE': False,
        'GET_NEW_ADDRESS': False,
        'GET_PRIV_KEY': False,
        'GET_PUB_KEY': False,
        'PASS_CHNG': False,
        'TRANS': False,
        'EST': False,
        'SEND_PAY': False,
        'IMP_PRIV_KEY': False,
        'GET_MULTI_ADDR': False,
        'FOLD_WALLET': False,
        'GET_SEED': False,
        'RESYNC': False
    }

    # Randomized Auth
    uname = str(random.getrandbits(128))
    pwd = str(random.getrandbits(128))

    # Set up app
    app = QtWidgets.QApplication(sys.argv)
    icons = set_pixmaps()
    window = MainWindow()
    window.raise_() #added for pyinstaller only, else menubar fails

    # check perms
    make_executable()

    # Shutdown any other instances
    exit_handler()

    # Size the app
    init_size()

    # Add multisig pubkeys lines
    init_multisig()

    # Add initial send recipient form - normal transaction
    init_send_rcp()

    # Add initial send recipient form - multisig transaction
    init_multi_rcp()

    # Add side menu buttons
    init_side_menu()

    # Temporarily deactivated for later version, or future deprecation
    deactivate()

    # Set up threadpool
    threadpool = QThreadPool()

    # Fire up daemon and wallet backend
    print('Starting Daemon ...\n')
    start_daemon(uname, pwd) 
    
    if not CREATE_NEW_WALLET:
        # Add balances
        print('Getting Balance ...')
        show_balance()

        # Add address balances and addresses
        print('Getting Address Balances ...')
        add_addresses(['balances'])
        add_addresses(['addresses'])

    # Styling
    add_custom_styles()

    # Listeners
    button_listeners()
    menubar_listeners()
    window.show()
    check_status()
    #detect_magic_wllt(QtWidgets)
    app.exec()
