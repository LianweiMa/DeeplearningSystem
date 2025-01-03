# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.adv

import gettext
_ = gettext.gettext

###########################################################################
## Class mainWin
###########################################################################

class mainWin ( wx.Frame ):

    def __init__( self, parent ):

        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"许可证管理工具"), pos = wx.DefaultPosition, size = wx.Size( 500,370 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL )
        
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer = wx.BoxSizer( wx.HORIZONTAL )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        bSizer11 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, _(u"打开授权文件："), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )

        bSizer11.Add( self.m_staticText2, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        self.m_textCtrl_openFile = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        self.m_textCtrl_openFile.SetMinSize( wx.Size( 300,-1 ) )

        bSizer11.Add( self.m_textCtrl_openFile, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        self.m_button_openFile = wx.Button( self, wx.ID_ANY, _(u"浏览..."), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer11.Add( self.m_button_openFile, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


        bSizer1.Add( bSizer11, 1, wx.ALL|wx.EXPAND, 5 )

        bSizer111 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_textCtrl_LicenseText = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 500,120 ), wx.TE_MULTILINE )
        bSizer111.Add( self.m_textCtrl_LicenseText, 0, wx.ALL|wx.EXPAND, 5 )


        bSizer1.Add( bSizer111, 1, wx.EXPAND, 5 )

        sbSizer111 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"授权信息：") ), wx.VERTICAL )

        bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer11111 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText711 = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, _(u"软件版本："), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText711.Wrap( -1 )

        bSizer11111.Add( self.m_staticText711, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_textCtrl_softwareVersion = wx.TextCtrl( sbSizer111.GetStaticBox(), wx.ID_ANY, _(u"1.0"), wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
        bSizer11111.Add( self.m_textCtrl_softwareVersion, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        bSizer9.Add( bSizer11111, 1, 0, 5 )

        bSizer11112 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText73 = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, _(u"用户身份："), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText73.Wrap( -1 )

        bSizer11112.Add( self.m_staticText73, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_textCtrl_userID = wx.TextCtrl( sbSizer111.GetStaticBox(), wx.ID_ANY, _(u"malianwei"), wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
        bSizer11112.Add( self.m_textCtrl_userID, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        bSizer9.Add( bSizer11112, 1, 0, 5 )

        bSizer11113 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText731 = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, _(u"授权时间："), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText731.Wrap( -1 )

        bSizer11113.Add( self.m_staticText731, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_datePicker_expirationDate = wx.adv.DatePickerCtrl( sbSizer111.GetStaticBox(), wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.Size( 200,-1 ), wx.adv.DP_DEFAULT )
        bSizer11113.Add( self.m_datePicker_expirationDate, 0, wx.ALL, 5 )


        bSizer9.Add( bSizer11113, 1, wx.EXPAND, 5 )


        sbSizer111.Add( bSizer9, 1, wx.EXPAND, 5 )


        bSizer1.Add( sbSizer111, 1, wx.EXPAND, 5 )

        bSizer12 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, _(u"保存授权文件："), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )

        bSizer12.Add( self.m_staticText3, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        self.m_textCtrl_saveFile = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), wx.TE_READONLY )
        bSizer12.Add( self.m_textCtrl_saveFile, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        self.m_button_saveFile = wx.Button( self, wx.ID_ANY, _(u"浏览..."), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer12.Add( self.m_button_saveFile, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


        bSizer1.Add( bSizer12, 1, wx.ALL|wx.EXPAND, 5 )

        gSizer11 = wx.GridSizer( 0, 1, 0, 0 )

        self.m_button_process = wx.Button( self, wx.ID_ANY, _(u"生成授权"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer11.Add( self.m_button_process, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


        bSizer1.Add( gSizer11, 1, wx.ALL|wx.EXPAND, 5 )


        bSizer.Add( bSizer1, 1, wx.EXPAND, 5 )


        self.SetSizer( bSizer )
        self.Layout()
        self.m_statusBar1 = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_button_openFile.Bind( wx.EVT_BUTTON, self.m_button_openFileOnButtonClick )
        self.m_button_saveFile.Bind( wx.EVT_BUTTON, self.m_button_saveFileOnButtonClick )
        self.m_button_process.Bind( wx.EVT_BUTTON, self.m_button_processOnButtonClick )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def m_button_openFileOnButtonClick( self, event ):
         # 创建一个文件对话框
        dialog = wx.FileDialog(self, "Open file", wildcard="License files (*.lic)|*.lic",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        # 显示对话框并检查是否选择了文件
        if dialog.ShowModal() == wx.ID_OK:
            # 获取选择的文件路径
            path = dialog.GetPath()
            self.m_textCtrl_openFile.SetValue(path)
            self.m_statusBar1.SetStatusText(f'打开许可文件：{path}')

            import datetime,json
            from cryptography.fernet import Fernet

             # 从文件加载密钥
            with open('secret.key', 'rb') as key_file:
                key = key_file.read()           
            # 创建Fernet对象
            fernet = Fernet(key)

            with open(path, "rb") as f:
                encrypted_license = f.read()
                self.m_textCtrl_LicenseText.SetValue(encrypted_license)           
            license_json = fernet.decrypt(encrypted_license).decode()
            license_data = json.loads(license_json)
            software_version = license_data.get("software_version")
            self.m_textCtrl_softwareVersion.SetValue(software_version)
            user_id = license_data.get("user_id")
            self.m_textCtrl_userID.SetValue(user_id)
            expiration_date = license_data.get("expiration_date")
            print(expiration_date)
            expiration_date_datetime = datetime.datetime.strptime(expiration_date, "%Y-%m-%d")
            expiration_date_wxdatetime = wx.DateTime.FromDMY(expiration_date_datetime.day,expiration_date_datetime.month-1,expiration_date_datetime.year, 0,0,0,0)
            self.m_datePicker_expirationDate.SetValue(expiration_date_wxdatetime)
            features_allowed = license_data.get("features_allowed")
            # 在这里进行详细的验证，如检查版本、用户身份、期限和功能等
            if datetime.datetime.strptime(expiration_date, "%Y-%m-%d") < datetime.datetime.now():
                #frame = wx.Frame(None, title="提示")
                wx.MessageBox(f"许可截至：{expiration_date}！\n已过期，请联系技术人员！", "警告", wx.ICON_WARNING)        
        # 销毁对话框
        dialog.Destroy()

    def m_button_saveFileOnButtonClick( self, event ):
        # 创建一个文件对话框
        dialog = wx.FileDialog(self, "Save file", wildcard="License files (*.lic)|*.lic",
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        # 显示对话框并检查是否选择了文件
        if dialog.ShowModal() == wx.ID_OK:
            # 获取选择的文件路径
            path = dialog.GetPath()
            self.m_textCtrl_saveFile.SetValue(path)
            self.m_statusBar1.SetStatusText(f'保存许可文件：{path}')

    def m_button_processOnButtonClick( self, event ):
        import json
        from cryptography.fernet import Fernet

        key = Fernet.generate_key()
        # 保存密钥（这里只是示例，实际中应该使用更安全的存储方法）
        with open('secret.key', 'wb') as key_file:
            key_file.write(key)
            print(key)
        license_data = {
        "software_version": self.m_textCtrl_softwareVersion.GetValue(),
        "user_id": self.m_textCtrl_userID.GetValue(),
        "expiration_date": self.m_datePicker_expirationDate.GetValue().FormatISODate(),
        "features_allowed": ['features1','features2']
        }
        print(license_data["expiration_date"])
        license_json = json.dumps(license_data)
        f = Fernet(key)
        encrypted_license = f.encrypt(license_json.encode())
        self.m_textCtrl_LicenseText.SetValue(encrypted_license)
        with open(self.m_textCtrl_saveFile.GetValue(), "wb") as f:
            f.write(encrypted_license)
            self.m_statusBar1.SetStatusText(f'保存许可文件：{self.m_textCtrl_saveFile.GetValue()} 成功！')

#(datetime.datetime.now() + datetime.timedelta(days=int(self.m_textCtrl_expirationDate.GetValue()))).strftime("%Y - %m - %d")
