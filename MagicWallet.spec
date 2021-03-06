# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

a = Analysis(['MagicWallet.py'],
            binaries=[
               ('build/deps/libzbar.dylib', '.'),
               ('build/deps/jpeg/9d/lib/libjpeg.9.dylib','.')
             ],
             datas=[('QRCodes', 'QRCodes')],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [('img/glyphicons_325_wallet_blk@2x.png', 'img/glyphicons_325_wallet_blk@2x.png', 'DATA'),
         ('img/glyphicons_325_wallet_blk_alt@2x.png', 'img/glyphicons_325_wallet_blk_alt@2x.png', 'DATA'),
         ('img/glyphicons_325_wallet@2x.png', 'img/glyphicons_325_wallet@2x.png', 'DATA'),
         ('img/glyphicons_325_wallet_alt@2x.png', 'img/glyphicons_325_wallet_alt@2x.png', 'DATA'),
         ('img/glyphicons_222_share@2x.png', 'img/glyphicons_222_share@2x.png', 'DATA'),
         ('img/glyphicons_222_share_alt@2x.png', 'img/glyphicons_222_share_alt@2x.png', 'DATA'),
         ('img/glyphicons_221_unshare@2x.png', 'img/glyphicons_221_unshare@2x.png', 'DATA'),
         ('img/glyphicons_221_unshare_alt@2x.png', 'img/glyphicons_221_unshare_alt@2x.png', 'DATA'),
         ('img/glyphicons_457_transfer@2x.png', 'img/glyphicons_457_transfer@2x.png', 'DATA'),
         ('img/glyphicons_457_transfer_alt@2x.png', 'img/glyphicons_457_transfer_alt@2x.png', 'DATA'),
         ('img/app_icon.png', 'img/app_icon.png', 'DATA'),
         ('img/Magic.iconset/icon_1024x1024@2x.png','img/Magic.iconset/icon_1024x1024@2x.png', 'DATA'),
         ('MultisigData/mdata.json', 'MultisigData/mdata.json', 'DATA'),
         ('bin/pktd', 'bin/pktd', 'DATA'),
         ('bin/btcctl', 'bin/btcctl', 'DATA'),
         ('bin/wallet', 'bin/wallet', 'DATA'),
         ('img/glyphicons_325_wallet_blk_alt@2x.png', 'img/glyphicons_325_wallet_blk_alt@2x.png', 'DATA')]


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

if sys.platform == 'darwin':
     exe = EXE(pyz,
               a.scripts,
               a.binaries,
               a.zipfiles,
               a.datas,
               name='MagicWallet',
               debug=True,
               strip=False,
               upx=True,
               runtime_tmpdir=None,
               console=True,
               icon='img/Magic.icns')

# Package the executable file into .app if on OS X
if sys.platform == 'darwin':
      app = BUNDLE(exe,
                   name='MagicWallet.app',
                   info_plist={
                     'NSHighResolutionCapable': 'True',
                     'LSBackgroundOnly': '1',
                     'LSBackgroundOnly': 'False'
                   },
                   icon='img/Magic.icns')

coll = COLLECT(exe,
             a.binaries,
             a.zipfiles,
             a.datas,
             strip=False,
             upx=True,
             upx_exclude=[],
             name='MagicWallet')
