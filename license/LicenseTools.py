from LicenseWin import mainWin
import wx
class MyApp(wx.App):
    def OnInit(self):
        frame = mainWin(None)
        # 创建窗口图标对象
        icon = wx.Icon('./res/license.ico', wx.BITMAP_TYPE_ICO) 
        # 设置窗口图标
        frame.SetIcon(icon)
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()