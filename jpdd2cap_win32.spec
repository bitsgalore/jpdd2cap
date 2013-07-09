# -*- mode: python -*-
a = Analysis(['.\jpdd2cap\jpdd2cap.py'],
             pathex=['.\jpdd2cap'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\jpdd2cap', 'jpdd2cap.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries +
               [('./license/LICENSE.txt','LICENSE','DATA')],
               [('./example_files/balloon_ddr.jp2','./example_files/balloon_ddr.jp2','DATA')],
               [('./example_files/readme.txt','./example_files/readme.txt','DATA')],
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist_win32', 'jpdd2cap'))
