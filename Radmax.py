#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

'''
*Radmax Main Module*
'''
from Parameters4Radmax import *
from Parameters4Radmax import P4Radmax, LogWindow

try:
    import wx
    import wx.html
    import matplotlib
    import scipy
    import sys
    import numpy
    print('******************************')
    print('            RaDMax')
    print('         Version:%s' % (Application_version))
    print(' Last modification:%s' % (last_modification))
    print('******************************\n')
    if getattr(sys, 'frozen', False):
        print ("Versions of modules compile for this application:")
    else:
        print ("Cheking of the modules needed to work with RaDMax:")
        print ("Version founded on this computer:")
    print ("Python: %s" % (sys.version))
    print ("Matplotlib: %s" % (matplotlib.__version__))
    print ("Wxpython: %s" % (wx.__version__))
    print ("Scipy: %s" % (scipy.__version__))
    print ("Numpy: %s" % (numpy.__version__))
except ImportError:
    raise ImportError("WxPython, Matplotlib and scipy modules are required" +
                      "to run this program")
    exit()

from wx.lib.pubsub import pub
import wx.lib.agw.genericmessagedialog as GMD

from Icon4Radmax import NewP24, LoadP24, saveP24, saveasP24, shutdown24, logP32
from Icon4Radmax import prog_icon, About_icon_24, acceleration

from Graph4Radmax import GraphPanel
from Parameters_Panel import InitialDataPanel
from Fitting_Panel import FittingPanel
from OptionParam4Radmax import ParametersWindow
from GSAParam4Radmax import GSAParametersWindow

if 'phoenix' in wx.PlatformInfo:
    from wx.adv import AboutDialogInfo, AboutBox
else:
    from wx import AboutDialogInfo, AboutBox

"""Pubsub message"""
pubsub_Load = "LoadP"
pubsub_New = "NewP"
pubsub_LoadXRD = "LoadXRD"
pubsub_LoadStrain = "LoadStrain"
pubsub_LoadDW = "LoadDW"
pubsub_Save = "SaveP"
pubsub_Launch_GUI = "LaunchGUI"
pubsub_ChangeFrameTitle = "ChangeFrameTitle"
pubsub_Activate_Import = "ActivateImport"
pubsub_shortcut = "Shortcut"
pubsub_Hide_Show_Option = "HideShowOption"
pubsub_Hide_Show_GSA = "HideShowGSA"


# -----------------------------------------------------------------------------
class MainFrame(wx.Frame):
    """
    Main Frame launcher
    The aui manager module is used to build the main architecture
    """
    def __init__(self, parent, id=-1):
        pos = wx.DefaultPosition
#        print(wx.GetDisplaySize())  # returns a tuple
        size = (1120, 970)
        no_resize = wx.DEFAULT_FRAME_STYLE

        wx.Frame.__init__(self, None, wx.ID_ANY, Application_name, pos, size,
                          style=no_resize)
        wx.Frame.CenterOnScreen(self)
        self.Bind(wx.EVT_CLOSE, self.on_close)
#        self.Bind(wx.EVT_SIZE, self.on_size)

        self.sb = wx.StatusBar(self, -1)
        self.sb.SetFieldsCount(3)
        self.SetStatusBar(self.sb)
        self.SetStatusWidths([-4, -1, -1])

        self.SetIcon(prog_icon.GetIcon())

        self.m_menubar = wx.MenuBar()

        self.NewP_ID = wx.ID_NEW
        self.LoadP_ID = wx.NewId()
        self.Load_XRD_ID = wx.NewId()
        self.Load_Strain_ID = wx.NewId()
        self.Load_DW_ID = wx.NewId()
        self.Save_ID = wx.NewId()
        self.SaveP_ID = wx.NewId()
        self.log_ID = wx.NewId()
        self.paramoption_ID = wx.NewId()
        self.Update = wx.NewId()
        self.Reloadini = wx.NewId()
        self.About = wx.NewId()
        self.Exit = wx.NewId()

        """File menu"""
        self.m_menufile = wx.Menu()
        self.m_menunewproject = wx.MenuItem(self.m_menufile, self.NewP_ID,
                                            u"New Project" + u"\t" + u"Ctrl+N",
                                            u"Begin a new project",
                                            wx.ITEM_NORMAL)
        self.m_menunewproject.SetBitmap(NewP24.GetBitmap())

        self.m_menuload = wx.MenuItem(self.m_menufile, self.LoadP_ID,
                                      u"Load Project" + u"\t" + u"Ctrl+O",
                                      u"Load .ini file", wx.ITEM_NORMAL)
        self.m_menuload.SetBitmap(LoadP24.GetBitmap())

        self.m_menuloadXRD = wx.MenuItem(self.m_menufile, self.Load_XRD_ID,
                                         u"Import XRD data" + u"\t" + u"Alt-O",
                                         u"Import XRD data file",
                                         wx.ITEM_NORMAL)

        self.m_menuloadStrain = wx.MenuItem(self.m_menufile,
                                            self.Load_Strain_ID,
                                            u"Import Strain", wx.EmptyString,
                                            wx.ITEM_NORMAL)
        self.m_menuloadStrain.Enable(False)

        self.m_menuloadDW = wx.MenuItem(self.m_menufile, self.Load_DW_ID,
                                        u"Import DW", wx.EmptyString,
                                        wx.ITEM_NORMAL)
        self.m_menuloadDW.Enable(False)

        self.m_menusave = wx.MenuItem(self.m_menufile, self.Save_ID, u"Save" +
                                      u"\t" + u"Ctrl+S", wx.EmptyString,
                                      wx.ITEM_NORMAL)
        self.m_menusave.SetBitmap(saveP24.GetBitmap())

        self.m_menusaveas = wx.MenuItem(self.m_menufile, self.SaveP_ID,
                                        u"Save As" + u"\t" + u"Ctrl-Shift+S",
                                        wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menusaveas.SetBitmap(saveasP24.GetBitmap())

        self.m_menuexit = wx.MenuItem(self.m_menufile, self.Exit, u"Exit" +
                                      u"\t" + u"Alt-X", wx.EmptyString,
                                      wx.ITEM_NORMAL)
        self.m_menuexit.SetBitmap(shutdown24.GetBitmap())

        self.m_menubar.Append(self.m_menufile, u"&File")

        """Option menu"""
        self.m_menuoptions = wx.Menu()
        choose_acc = wx.Menu()

        self.m_menubar.Append(self.m_menuoptions, u"O&ptions")
        self.m_menulog = wx.MenuItem(self.m_menuoptions, self.log_ID,
                                     u"Log file", u"Open log file",
                                     wx.ITEM_NORMAL)
        self.m_menulog.SetBitmap(logP32.GetBitmap())

        """Fit menu"""
        self.m_menufit = wx.Menu()
        choose_acc = wx.Menu()

        self.m_menubar.Append(self.m_menufit, u"F&it")
        self.m_menu_fit = wx.MenuItem(self.m_menufit, self.paramoption_ID,
                                      u"Fit Parameters",
                                      u"Open Parameters window",
                                      wx.ITEM_NORMAL)

        self.acc_numpy_Id = wx.NewId()
        self.acc_numba_Id = wx.NewId()
        self.menuoptionsId = wx.NewId()
        self.acc_icon_ID = wx.NewId()
        self.m_menuacc = wx.MenuItem(self.m_menufit, self.acc_icon_ID,
                                     u"Fit Acceleration", u"",
                                     wx.ITEM_NORMAL)
        self.m_menuacc.SetBitmap(acceleration.GetBitmap())
        self.acc_numpy = choose_acc.AppendRadioItem(self.acc_numpy_Id,
                                                    "Numpy", "")
        self.acc_numba = choose_acc.AppendRadioItem(self.acc_numba_Id,
                                                    "Numba", "")
        choose_acc.Check(self.acc_numpy_Id, True)
        P4Radmax.acc_choice = "Numpy"


        """About menu"""
        self.m_menuhelp = wx.Menu()
        self.m_menuabout = wx.MenuItem(self.m_menuhelp, self.About, u"About." +
                                       u"\t" + u"Alt-L", wx.EmptyString,
                                       wx.ITEM_NORMAL)
        self.m_menuabout.SetBitmap(About_icon_24.GetBitmap())

        self.m_menubar.Append(self.m_menuhelp, u"&Help")

        if 'phoenix' in wx.PlatformInfo:
            self.m_menufile.Append(self.m_menunewproject)
            self.m_menufile.Append(self.m_menuload)
            self.m_menufile.AppendSeparator()
            self.m_menufile.Append(self.m_menuloadXRD)
            self.m_menufile.Append(self.m_menuloadStrain)
            self.m_menufile.Append(self.m_menuloadDW)
            self.m_menufile.AppendSeparator()
            self.m_menufile.Append(self.m_menusave)
            self.m_menufile.Append(self.m_menusaveas)
            self.m_menufile.Append(self.m_menuexit)
            self.m_menuoptions.Append(self.m_menulog)
            self.m_menufit.Append(self.m_menu_fit)
            self.m_menufit.AppendSeparator()
            self.m_menufit.Append(self.m_menuacc)
            self.m_menuhelp.Append(self.m_menuabout)
            self.m_menufit.Append(self.menuoptionsId, "&Choice", choose_acc)
        else:
            self.m_menufile.AppendItem(self.m_menunewproject)
            self.m_menufile.AppendItem(self.m_menuload)
            self.m_menufile.AppendSeparator()
            self.m_menufile.AppendItem(self.m_menuloadXRD)
            self.m_menufile.AppendItem(self.m_menuloadStrain)
            self.m_menufile.AppendItem(self.m_menuloadDW)
            self.m_menufile.AppendSeparator()
            self.m_menufile.AppendItem(self.m_menusave)
            self.m_menufile.AppendItem(self.m_menusaveas)
            self.m_menufile.AppendItem(self.m_menuexit)
            self.m_menuoptions.AppendItem(self.m_menulog)
            self.m_menufit.AppendItem(self.m_menu_fit)
            self.m_menufit.AppendSeparator()
            self.m_menufit.AppendItem(self.m_menuacc)
            self.m_menuhelp.AppendItem(self.m_menuabout)
            self.m_menufit.AppendMenu(self.menuoptionsId, "&Choice",
                                      choose_acc)

        self.SetMenuBar(self.m_menubar)

        self.Bind(wx.EVT_MENU, self.set_menu_all)
        self.Bind(wx.EVT_MENU, self.on_close, id=self.Exit)
        self.Bind(wx.EVT_MENU, self.on_about_box, id=self.About)
#        ----------------------------------------------------------------------
#        Definition of shortcut used in RaDMax:
#        ctrl+U emulate the update button
#        ctrl+I reload the last open project
        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('U'),
                                               self.Update),
                                              (wx.ACCEL_CTRL, ord('I'),
                                               self.Reloadini)])
        self.SetAcceleratorTable(self.accel_tbl)

        self.frame_Fit_Param_window = None
        self.frame_GSA_window = None

        try:
            import lmfit
            print ("Lmfit: %s" % (lmfit.__version__))
        except ImportError:
            print ("\nLmfit module is recommanded but not mandatory")

        try:
            import numba
            print ("Numba: %s" % (numba.__version__))
        except ImportError:
            self.m_menufit.Enable(self.menuoptionsId, False)

        pub.subscribe(self.on_change_title, pubsub_ChangeFrameTitle)
        pub.subscribe(self.on_activate_import, pubsub_Activate_Import)
        pub.subscribe(self.on_display_option_window, pubsub_Hide_Show_Option)
        pub.subscribe(self.on_display_GSA_window, pubsub_Hide_Show_GSA)

        MainPanel(self, self.sb)

        self.Show()

    def on_size(self, event):
        sizet = event.GetSize()
        print ("%s, %s" % (sizet.width, sizet.height))
        event.Skip()

    def some_method(self, event):
        self.statusbar.SetStatusText('', 0)
        self.statusbar.SetStatusText('', 1)
        self.statusbar.SetStatusText('', 2)

    def on_activate_import(self):
        self.m_menuloadStrain.Enable(True)
        self.m_menuloadStrain.SetHelp(u"Import Strain file")
        self.m_menuloadDW.Enable(True)
        self.m_menuloadDW.SetHelp(u"Import DW file")

    def set_menu_all(self, event):
        widget = event.GetId()
        if widget == self.NewP_ID:
            pub.sendMessage(pubsub_New, event=event)
        elif widget == self.LoadP_ID:
            pub.sendMessage(pubsub_Load, event=event)
        elif widget == self.Load_XRD_ID:
            pub.sendMessage(pubsub_LoadXRD, event=event)
        elif widget == self.Load_Strain_ID:
            pub.sendMessage(pubsub_LoadStrain, event=event)
        elif widget == self.Load_DW_ID:
            pub.sendMessage(pubsub_LoadDW, event=event)
        elif widget == self.Save_ID:
            pub.sendMessage(pubsub_Save, event=event, case=0)
        elif widget == self.SaveP_ID:
            pub.sendMessage(pubsub_Save, event=event, case=1)
        elif widget == self.log_ID:
            self.on_display_log_file()
        elif widget == self.paramoption_ID:
            self.on_display_option_window()
        elif widget == self.Update:
            pub.sendMessage(pubsub_shortcut, event=event, case=0)
        elif widget == self.Reloadini:
            pub.sendMessage(pubsub_shortcut, event=event, case=1)
        elif (widget == self.acc_numpy_Id) or (widget == self.acc_numba_Id):
            if self.acc_numpy.IsChecked():
                P4Radmax.acc_choice = "Numpy"
            elif self.acc_numba.IsChecked():
                P4Radmax.acc_choice = "Numba"

    def on_about_box(self, event):
        info = AboutDialogInfo()
        info.SetName(Application_name)
        info.SetVersion(str(Application_version))
        info.SetCopyright(copyright_)
        info.SetDescription(description)
        info.SetWebSite(website_)
        info.AddDeveloper('Alexandre Boulle')
        info.AddDeveloper('Marc Souilah')
        info.SetLicence(licence)
        AboutBox(info)

    def on_change_title(self, NewTitle):
        """Change title when create a new project"""
        self.SetTitle(NewTitle)

    def on_display_log_file(self):
        """Open Log file"""
        if P4Radmax.log_window_status is False:
            LogWindow().Show()
            P4Radmax.log_window_status = True

    def on_display_option_window(self, test=None):
        """Open Parameters window"""
        if test is None:
            self.frame_Fit_Param_window = ParametersWindow(self)
            self.frame_Fit_Param_window.Show()
        else:
            self.frame_Fit_Param_window.Hide()
            self.SetFocus()

    def on_display_GSA_window(self, test=None):
        """Open GSA Parameters window"""
        if test is None:
            self.frame_GSA_window = GSAParametersWindow(self)
            self.frame_GSA_window.Show()
        else:
            self.frame_GSA_window.Hide()
            self.SetFocus()

    def on_close(self, event):
        titlelabel = self.GetLabel().split(' - ')
        if len(titlelabel) > 1:
            if titlelabel[1] != "New Project":
                _msg = "Do you really want to close this application?"
                dlg = GMD.GenericMessageDialog(None, _msg, "Confirm Exit",
                                               agwStyle=wx.OK | wx.CANCEL |
                                               wx.ICON_QUESTION)
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_OK:
                    logger.log(logging.INFO, "End of the project\n")
                    exit()
            else:
                _msg = ("Project has not been saved\n" +
                        "Do you want to save it now ?")
                dlg = GMD.GenericMessageDialog(None, _msg, "Confirm Exit",
                                               agwStyle=wx.OK | wx.CANCEL |
                                               wx.ICON_QUESTION)
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_OK:
                    logger.log(logging.INFO, "Saving on going project")
                    pub.sendMessage(pubsub_Save, event=event, case=1)
                    logger.log(logging.INFO, "End of the project\n")
                    exit()
                else:
                    logger.log(logging.INFO, "Project not saved")
                    logger.log(logging.INFO, "End of the project\n")
                    exit()
        else:
            _msg = "Do you really want to close this application?"
            dlg = GMD.GenericMessageDialog(None, _msg, "Confirm Exit",
                                           agwStyle=wx.OK | wx.CANCEL |
                                           wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                logger.log(logging.INFO, "End of the project\n")
                exit()


# -----------------------------------------------------------------------------
class MainPanel(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar
        self.parent = parent

        self.aui_mgr = aui.AuiManager()
        self.aui_mgr.SetManagedWindow(self)

        ''' create the AUI Notebook  '''
        self.notebook = AUINotebook(self, self.statusbar)

        ''' add notebook to AUI manager '''
        self.aui_mgr.AddPane(self.notebook, aui.AuiPaneInfo().CenterPane().
                             Name("notebook_content").PaneBorder(False).
                             Position(1).MaximizeButton(False))

        all_panes = self.aui_mgr.GetAllPanes()
        '''Theme for Notebook
        aui.AuiDefaultTabArt(), aui.AuiSimpleTabArt(), aui.VC71TabArt()
        aui.FF2TabArt(), aui.VC8TabArt(), aui.ChromeTabArt()'''
        # for apply theme to all notebook
        for pane in all_panes:
            nb = pane.window
            tabArt = aui.ChromeTabArt()
            nb.SetArtProvider(tabArt)
            self._notebook_theme = 1
            nb.Refresh()
            nb.Update()

        self.aui_mgr.AddPane(GraphPanel(self, self.statusbar),
                             aui.AuiPaneInfo().Name("Graph_Window").
                             CenterPane().PaneBorder(False).Position(1).
                             MaximizeButton(False))
        self.aui_mgr.GetPane("notebook_content").dock_proportion = 70
        self.aui_mgr.GetPane("Graph_Window").dock_proportion = 100
        self.Layout()
        self.parent.SetSizeHints(minW=1120, minH=970)
        self.Fit()
        self.Centre(wx.BOTH)
        self.aui_mgr.Update()
        P4Radmax.logfile_Radmax_path = current_dir
        P4Radmax.log_window_status = False
        P4Radmax.Option_window_status = False
        LogSaver(self)
        pub.sendMessage(pubsub_Launch_GUI)


# -----------------------------------------------------------------------------
class AUINotebook(aui.AuiNotebook):
    """ AUI Notebook class """
    def __init__(self, parent, statusbar):
        aui.AuiNotebook.__init__(self, parent=parent)
        self.parent = parent
        self.statusbar = statusbar

        self.default_style = (aui.AUI_NB_CLOSE_ON_ALL_TABS)
        self.SetAGWWindowStyleFlag(self.default_style)

        """create the page windows as children of the notebook"""
        page1 = InitialDataPanel(self.parent, self.statusbar)
        page2 = FittingPanel(self.parent, self.statusbar)

        """add the pages to the notebook with the label to show on the tab"""
        self.AddPage(page1, "Initial Parameters")
        self.AddPage(page2, "Fitting window")

        self.SetCloseButton(0, False)
        self.SetCloseButton(1, False)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(0)
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()
