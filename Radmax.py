#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

# =============================================================================
# Radmax Main Module
# =============================================================================


# =============================================================================
# The files are provided "as is" without warranty or support of any kind
# =============================================================================

import os
import sys
from sys import platform as _platform

import Parameters4Radmax as p4R
from Parameters4Radmax import P4Rm

try:
    import wx
    from distutils.version import LooseVersion
    vers = wx.__version__
    if LooseVersion(vers) < LooseVersion("3.0.2.0"):
        if _platform == "linux" or _platform == "linux2":
            pass
        else:
            print("You are using wxPython version number %s" % vers)
            print("To run, RaDMaX needs wxPython version 3.0.2.0 or higher")
            sys.exit()
except ImportError:
    raise ImportError("WxPython module is required to run this program")
    sys.exit()

try:
    import wx
    import wx.html
    import matplotlib
    import scipy
    import numpy
    sys.path.insert(0, './modules')
    import ObjectListView as OLV
    import sqlalchemy
    from pubsub import pub
    print('**********************************')
    print('             RaDMaX')
    print('         Version:%s' % p4R.version)
    print(' Last modification date: %s' % p4R.last_modification)
    print('***********************************\n')
    if getattr(sys, 'frozen', False):
        print ("Versions of modules compiled for this application:")
    else:
        print ("Checking the modules needed to work with RaDMaX:")
        print ("Version found on this computer:")
    print ("Python: %s" % sys.version)
    print ("Wxpython: %s" % wx.__version__)
    print ("Matplotlib: %s" % matplotlib.__version__)
    print ("Scipy: %s" % scipy.__version__)
    print ("Numpy: %s" % numpy.__version__)
    print ("ObjectListView: %s" % OLV.__version__)
    print ("Sqlalchemy: %s" % sqlalchemy.__version__)
except ImportError:
    raise ImportError("Matplotlib, scipy and numpy modules are required" +
                      "to run this program")
    sys.exit()

import wx.lib.agw.aui as aui

import wx.lib.agw.genericmessagedialog as GMD

from sys import platform as _platform

from Icon4Radmax import NewP24, LoadP24, saveP24, saveasP24, shutdown24, logP32
from Icon4Radmax import prog_icon, About_icon_24

from random import randint
import logging

from Graph4Radmax import GraphPanel
from ExpPanel4Radmax import InitialDataPanel
from SampleGeometry4Radmax import SampleGeometry
from FittingPanel4Radmax import FittingPanel
from OptionParam4Radmax import ParametersWindow
from LimitPanel4Radmax import GSAParametersWindow
from Color4Radmax import ColorWindow
from FitReport4Radmax import FitReportWindow
from Calcul4Radmax import Calcul4Radmax
from Read4Radmax import SaveFile4Diff
from DB4Radmax import DataBasePanel, DataBaseManagement

from Settings4Radmax import LogSaver, LogWindow
from Settings4Radmax import Sound_Launcher

if _platform == 'darwin' or _platform == "linux" or _platform == "linux2":
    from BoundsValue4Radmax_Unix import DataCoefPanel
elif _platform == "win32":
    from BoundsValue4Radmax import DataCoefPanel
    """Necessaire avec PyInstaller sous windows
    sinon l'executable ne se lance pas """
    if getattr(sys, 'frozen', False):
        import FileDialog

LogSaver()

logger = logging.getLogger(__name__)

if 'phoenix' in wx.PlatformInfo:
    from wx.adv import AboutDialogInfo, AboutBox
else:
    from wx import AboutDialogInfo, AboutBox

"""Pubsub message"""
pubsub_Save = "SaveP"
pubsub_ChangeFrameTitle = "ChangeFrameTitle"

pubsub_Activate_Import = "ActivateImport"
pubsub_shortcut = "Shortcut"

pubsub_Hide_Show_Option = "HideShowOption"
pubsub_Open_Option_Window = "OpenOptionWindow"
pubsub_Fill_List_coef = "FillListCoef"


pubsub_Hide_Show_GSA = "HideShowGSA"
pubsub_Open_GSA_Window = "OpenGSAWindow"

pubsub_Hide_Show_Color = "HideShowColor"
pubsub_Open_Color_Window = "OpenColorWindow"

pubsub_Hide_Show_FitReport = "HideShowFitReport"
pubsub_Open_FitReport_Window = "OpenFitReportWindow"

pubsub_Hide_Show_data_coef = "HideShowDataCoef"
pubsub_Open_data_coef_Window = "OpenDataCoefWindow"

pubsub_enable_dis_database = "EnableDisableDatabase"
pubsub_save_from_DB = "SaveFromDB"

pubsub_save_project_before_fit = "SaveProjectBeforeFit"
pubsub_add_damaged_before_fit = "AddDamagedBeforeFit"
pubsub_show_panel = "ShowPanel"
pubsub_change_damaged_depth_color = "ChangeDamagedDepthColor"


# -----------------------------------------------------------------------------
class MainFrame(wx.Frame):
    """
    Main Frame launcher
    The aui manager module is used to build the main architecture
    """
    def __init__(self, parent):
        pos = wx.DefaultPosition
        screen_size = wx.GetDisplaySize()
        if screen_size[1] <= 1000:
            size = (1000, 900)
        else:
            size = (1180, 1035)
        no_resize = wx.DEFAULT_FRAME_STYLE

        wx.Frame.__init__(self, None, wx.ID_ANY, p4R.Application_name,
                          pos, size, style=no_resize)
        wx.Frame.CenterOnScreen(self)
        self.Bind(wx.EVT_CLOSE, self.on_close)
#        self.Bind(wx.EVT_SIZE, self.on_size)

        import locale
        locale.setlocale(locale.LC_ALL, 'en_US')
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)

        self.sb = wx.StatusBar(self, -1)
        self.sb.SetFieldsCount(3)
        self.SetStatusBar(self.sb)
        self.SetStatusWidths([-4, -1, -1])

        self.SetIcon(prog_icon.GetIcon())

        self.m_menubar = wx.MenuBar()

        n_menu_value = 1
        self.NewP_ID = n_menu_value
        n_menu_value += 1
        self.LoadP_ID = n_menu_value
        n_menu_value += 1
        self.Load_XRD_ID = n_menu_value
        n_menu_value += 1
        self.Load_Strain_ID = n_menu_value
        n_menu_value += 1
        self.Load_DW_ID = n_menu_value
        n_menu_value += 1
        self.Export_data_ID = n_menu_value
        n_menu_value += 1
        self.Save_ID = n_menu_value
        n_menu_value += 1
        self.SaveP_ID = n_menu_value
        n_menu_value += 1
        self.log_ID = n_menu_value
        n_menu_value += 1
        self.paramoption_ID = n_menu_value
        n_menu_value += 1
        self.spdwpvalues_ID = n_menu_value
        n_menu_value += 1
        self.fitreport_ID = n_menu_value
        n_menu_value += 1
        self.colorwindow_ID = n_menu_value
        n_menu_value += 1
        self.Update = n_menu_value
        n_menu_value += 1
        self.Reloadini = n_menu_value
        n_menu_value += 1
        self.About = n_menu_value
        n_menu_value += 1
        self.Exit = n_menu_value

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

        self.m_menuloadDW = wx.MenuItem(self.m_menufile, self.Load_DW_ID,
                                        u"Import DW", wx.EmptyString,
                                        wx.ITEM_NORMAL)

        self.m_menuexportData = wx.MenuItem(self.m_menufile,
                                            self.Export_data_ID,
                                            u"Export Strain - DW - XRD fit",
                                            wx.EmptyString, wx.ITEM_NORMAL)

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

        self.m_menubar.Append(self.m_menuoptions, u"O&ptions")
        self.m_menulog = wx.MenuItem(self.m_menuoptions, self.log_ID,
                                     u"Log file", u"Open log file",
                                     wx.ITEM_NORMAL)
        self.m_menulog.SetBitmap(logP32.GetBitmap())
        text_ = u"Open Color and style graph window"
        self.m_menucolor = wx.MenuItem(self.m_menuoptions, self.colorwindow_ID,
                                       u"Graph Style", text_,
                                       wx.ITEM_NORMAL)

        n_menu_value += 1
        self.HideShowDatabase = n_menu_value
        self.m_menuhide_show_database = wx.MenuItem(self.m_menufile,
                                                    self.HideShowDatabase,
                                                    u"Use Database",
                                                    wx.EmptyString,
                                                    wx.ITEM_CHECK)

        """Fit menu"""
        self.m_menufit = wx.Menu()

        self.m_menubar.Append(self.m_menufit, u"F&it")
        self.m_menu_fit = wx.MenuItem(self.m_menufit, self.paramoption_ID,
                                      u"Fitting options",
                                      u"Open Parameters window",
                                      wx.ITEM_NORMAL)

        self.m_menu_strain_dw = wx.MenuItem(self.m_menufit,
                                            self.spdwpvalues_ID,
                                            (u"Strain and DW Values" +
                                             u"\t" + u"Ctrl+G"),
                                            u"Open Strain & DW Values window",
                                            wx.ITEM_NORMAL)

        self.m_menu_report_fit = wx.MenuItem(self.m_menufit, self.fitreport_ID,
                                             (u"Fitting report" +
                                              u"\t" + u"Ctrl+R"),
                                             u"Open Lmfit report window",
                                             wx.ITEM_NORMAL)

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
            self.m_menufile.Append(self.m_menuexportData)
            self.m_menufile.AppendSeparator()
            self.m_menufile.Append(self.m_menusave)
            self.m_menufile.Append(self.m_menusaveas)
            self.m_menufile.Append(self.m_menuexit)

            self.m_menuoptions.Append(self.m_menulog)
            self.m_menuoptions.Append(self.m_menuhide_show_database)
            self.m_menuoptions.Append(self.m_menucolor)

            self.m_menufit.Append(self.m_menu_fit)
            self.m_menufit.Append(self.m_menu_strain_dw)
            self.m_menufit.Append(self.m_menu_report_fit)
            self.m_menuhelp.Append(self.m_menuabout)
        else:
            self.m_menufile.AppendItem(self.m_menunewproject)
            self.m_menufile.AppendItem(self.m_menuload)
            self.m_menufile.AppendSeparator()
            self.m_menufile.AppendItem(self.m_menuloadXRD)
            self.m_menufile.AppendItem(self.m_menuloadStrain)
            self.m_menufile.AppendItem(self.m_menuloadDW)
            self.m_menufile.AppendSeparator()
            self.m_menufile.AppendItem(self.m_menuexportData)
            self.m_menufile.AppendSeparator()
            self.m_menufile.AppendItem(self.m_menusave)
            self.m_menufile.AppendItem(self.m_menusaveas)
            self.m_menufile.AppendItem(self.m_menuexit)

            self.m_menuoptions.AppendItem(self.m_menulog)
            self.m_menuoptions.AppendItem(self.m_menuhide_show_database)
            self.m_menuoptions.AppendItem(self.m_menucolor)

            self.m_menufit.AppendItem(self.m_menu_fit)
            self.m_menufit.AppendItem(self.m_menu_strain_dw)
            self.m_menufit.AppendItem(self.m_menu_report_fit)
            self.m_menuhelp.AppendItem(self.m_menuabout)

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
        self.frame_Fit_Report_window = None
        self.frame_GSA_window = None
        self.frame_color_window = None
        self.frame_data_coef_window = None

        self.Fit_Param_window_launch = 0
        self.Fit_Report_window_launch = 0
        self.GSA_window_launch = 0
        self.color_window_launch = 0
        self.data_coef_window_launch = 0

        try:
            import lmfit
            vers = lmfit.__version__
            if LooseVersion(vers) < LooseVersion("0.9.0"):
                print("\nYou are using Lmfit version number %s" % vers)
                print("To run, RaDMaX needs Lmfit version 0.9.0 or higher")
                print("Please, install a new Lmfit version to be able" +
                      " to use it with RaDMaX")
                print("Lmfit will not be used in this session\n")
                P4Rm.lmfit_install = False
            else:
                print ("Lmfit: %s" % (lmfit.__version__))
                P4Rm.lmfit_install = True
        except ImportError:
            print ("\nLmfit module is recommanded but not mandatory")

        pub.subscribe(self.on_change_title,
                      pubsub_ChangeFrameTitle)
        pub.subscribe(self.on_activate_import,
                      pubsub_Activate_Import)
        pub.subscribe(self.on_display_option_window,
                      pubsub_Hide_Show_Option)
        pub.subscribe(self.on_display_GSA_window,
                      pubsub_Hide_Show_GSA)
        pub.subscribe(self.on_display_Color_window,
                      pubsub_Hide_Show_Color)
        pub.subscribe(self.on_display_fit_report_window,
                      pubsub_Hide_Show_FitReport)
        pub.subscribe(self.on_display_data_coef_window,
                      pubsub_Hide_Show_data_coef)
        pub.subscribe(self.on_save,
                      pubsub_save_from_DB)
        pub.subscribe(self.on_save_before_fit,
                      pubsub_save_project_before_fit)
        pub.subscribe(self.on_add_damaged,
                      pubsub_add_damaged_before_fit)

        from Read4Radmax import ReadFile
        b = ReadFile()
        b.on_read_init_parameters(os.path.join(p4R.current_dir,
                                               p4R.filename + '.ini'),
                                  p4R.RadmaxFile)
        config_File_extraction = b.read_result_value()

        i = 2
        a = P4Rm()
        for k,v in a.DefaultDict.items():
            P4Rm.DefaultDict[k] = config_File_extraction[i]
            i += 1
        for k, v in p4R.FitParamDefault.items():
            if k == 'maxfev':
                P4Rm.DefaultDict[k] = int(float(a.DefaultDict[k]))
            elif k in p4R.s_radmax_7:
                P4Rm.DefaultDict[k] = a.DefaultDict[k]
            elif k in p4R.s_radmax_8:
                if a.DefaultDict[k] == 'True':
                    P4Rm.DefaultDict[k] = True
                else:
                    P4Rm.DefaultDict[k] = False
            else:
                P4Rm.DefaultDict[k] = float(a.DefaultDict[k])
        if os.listdir(p4R.structures_name):
            P4Rm.crystal_list = sorted(list(os.listdir(p4R.structures_name)))

        if a.DefaultDict['use_database']:
            self.m_menuhide_show_database.Check(True)
        else:
            self.m_menuhide_show_database.Check(False)

        load_random_voice = randint(0, 3)
        Sound_Launcher(self, 2, load_random_voice)

        MainPanel(self, self.sb)
        self.Show()

    def on_size(self, event):
        sizet = event.GetSize()
        print ("%s, %s" % (sizet.width, sizet.height))
        event.Skip()

    def some_method(self):
        self.sb.SetStatusText('', 0)
        self.sb.SetStatusText('', 1)
        self.sb.SetStatusText('', 2)

    def on_activate_import(self):
        self.m_menuloadStrain.Enable(True)
        self.m_menuloadStrain.SetHelp(u"Import Strain file")
        self.m_menuloadDW.Enable(True)
        self.m_menuloadDW.SetHelp(u"Import DW file")

    def set_menu_all(self, event):
        widget = event.GetId()
        if widget == self.NewP_ID:
            self.on_new_project()
        elif widget == self.LoadP_ID:
            self.on_load_project()
        elif widget == self.Load_XRD_ID:
            self.on_load_XRD()
        elif widget == self.Load_Strain_ID:
            self.on_load_strain()
        elif widget == self.Load_DW_ID:
            self.on_load_DW()
        elif widget == self.Export_data_ID:
            self.on_export_data()
        elif widget == self.Save_ID:
            self.on_save(0)
        elif widget == self.SaveP_ID:
            self.on_save(1)
        elif widget == self.log_ID:
            self.on_display_log_file()
        elif widget == self.HideShowDatabase:
            if self.m_menuhide_show_database.IsChecked():
                pub.sendMessage(pubsub_enable_dis_database, case=0)
                P4Rm.DefaultDict['use_database'] = True
            else:
                pub.sendMessage(pubsub_enable_dis_database, case=1)
                P4Rm.DefaultDict['use_database'] = False
            b = SaveFile4Diff()
            path_ = os.path.join(p4R.current_dir, p4R.filename + '.ini')
            b.on_update_config_file_parameters(path_)
        elif widget == self.paramoption_ID:
            self.on_display_option_window()
        elif widget == self.fitreport_ID:
            self.on_display_fit_report_window()
        elif widget == self.colorwindow_ID:
            self.on_display_Color_window()
        elif widget == self.spdwpvalues_ID:
            self.on_display_data_coef_window()
        elif widget == self.Update:
            pub.sendMessage(pubsub_shortcut, event=event, case=0)
        elif widget == self.Reloadini:
            pub.sendMessage(pubsub_shortcut, event=event, case=1)

    def on_new_project(self):
        b = Calcul4Radmax()
        b.on_new_project()

    def on_calc_dialog_pos(self, dlg_size):
        originx, originy = self.GetPosition()
        sizex, sizey = self.GetSize()
        posx = int(originx + sizex/2 - dlg_size[0]/2)
        posy = int(originy + sizey/2 - dlg_size[1]/2)
        return (posx, posy)

    def on_load_project(self):
        """
        Loading of project with '.ini' extension,
        format created for the RaDMax application
        """
        a = P4Rm()
        wildcard = "text file (*.ini)|*.ini|" \
                   "All files (*.*)|*.*"
        dlgpos = self.on_calc_dialog_pos(p4R.dlg_size)
        dlg = wx.FileDialog(
            self, message="Select ini file",
            defaultDir=a.DefaultDict['project_folder'],
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
            )
        dlg.SetSize(p4R.dlg_size)
        dlg.SetPosition(dlgpos)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            dlg.Destroy()
            P4Rm.pathfromDB = 0
            self.some_method()
            b = Calcul4Radmax()
            b.on_load_project(paths[0])

    def on_load_XRD(self):
        """
        Loading and extracting XRD data file with no default extension,
        but needed a two columns format file
        """
        a = P4Rm()
        wildcard = "All files (*.*)|*.*"
        dlgpos = self.on_calc_dialog_pos(p4R.dlg_size)
        dlg = wx.FileDialog(
            self, message="Import XRD file",
            defaultDir=a.DefaultDict['XRD_folder'],
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
            )
        dlg.SetSize(p4R.dlg_size)
        dlg.SetPosition(dlgpos)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            dlg.Destroy()
            b = Calcul4Radmax()
            b.calc_XRD(paths)

    def on_load_strain(self):
        """
        Loading of Strain data file with no default extension,
        but needed a two columns format file
        """
        a = P4Rm()
        wildcard = "All files (*.*)|*.*"
        dlgpos = self.on_calc_dialog_pos(p4R.dlg_size)
        dlg = wx.FileDialog(
            self, message="Import Strain file",
            defaultDir=a.DefaultDict['Strain_folder'],
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
            )
        dlg.SetSize(p4R.dlg_size)
        dlg.SetPosition(dlgpos)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            dlg.Destroy()
            b = Calcul4Radmax()
            b.calc_strain(paths, 0)

    def on_load_DW(self):
        """
        Loading of DW data file with no default extension,
        but needed a two columns format file
        """
        a = P4Rm()
        wildcard = "All files (*.*)|*.*"
        dlgpos = self.on_calc_dialog_pos(p4R.dlg_size)
        dlg = wx.FileDialog(
            self, message="Import DW file",
            defaultDir=a.DefaultDict['DW_folder'],
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
            )
        dlg.SetSize(p4R.dlg_size)
        dlg.SetPosition(dlgpos)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            dlg.Destroy()
            b = Calcul4Radmax()
            b.calc_DW(paths, 0)

    def on_export_data(self):
        """
        Manual export data to file containing Strain, Dw and XRD fit
        """
        a = P4Rm()
        b = SaveFile4Diff()
        if a.PathDict['project_name'] == "":
            return
        else:
            b.on_export_data()

    def on_save(self, case):
        """
        Saving project, save or save as depending of the action
        """
        a = P4Rm()
        b = SaveFile4Diff()
        if a.PathDict['project_name'] == "":
            case = 1
        wildcard = "data file (*.ini)|*.ini|" \
                   "All files (*.*)|*.*"
        textmessage = "Save file as ..."
        if case == 1:
            defaultdir_ = a.DefaultDict['Save_as_folder']
            dlgpos = self.on_calc_dialog_pos(p4R.dlg_size)
            dlg = wx.FileDialog(self, message=textmessage,
                                defaultDir=defaultdir_, defaultFile="",
                                wildcard=wildcard, style=wx.FD_SAVE)
            dlg.SetSize(p4R.dlg_size)
            dlg.SetPosition(dlgpos)
            if dlg.ShowModal() == wx.ID_OK:
                paths = dlg.GetPaths()
                b.on_save_project(case, paths)
            else:
                return
        else:
            b.on_save_project(case)

    def on_save_before_fit(self):
        text = "Please, save the project to continue"
        dlg = GMD.GenericMessageDialog(None, text,
                                       "Attention", agwStyle=wx.OK |
                                       wx.ICON_INFORMATION)
        dlg.ShowModal()
        if dlg.ShowModal() == wx.ID_OK:
            self.on_save(1)

    def on_add_damaged(self):
        pub.sendMessage(pubsub_show_panel)
        color = (255, 0, 0)
        pub.sendMessage(pubsub_change_damaged_depth_color, color=color)
        text = "Please, add some damaged to fit the data"
        dlg = GMD.GenericMessageDialog(None, text,
                                       "Attention", agwStyle=wx.OK |
                                       wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        color = (255, 255, 255)
        pub.sendMessage(pubsub_change_damaged_depth_color, color=color)

    def on_about_box(self, event):
        info = AboutDialogInfo()
        info.SetName(p4R.Application_name)
        info.SetVersion(p4R.Application_version)
        info.SetCopyright(p4R.copyright_)
        info.SetDescription(p4R.description)
        info.SetWebSite(p4R.website_)
        info.AddDeveloper('Alexandre Boulle')
        info.AddDeveloper('Marc Souilah')
        info.SetLicence(p4R.licence)
        AboutBox(info)

    def on_change_title(self, NewTitle):
        """
        Change title when create a new project
        """
        self.SetTitle(NewTitle)

    def on_display_log_file(self):
        """
        Open Log file
        """
        if P4Rm.log_window_status is False:
            LogWindow().Show()
            P4Rm.log_window_status = True

    def on_display_option_window(self, test=None):
        """
        Open Parameters window
        """
        if test is None:
            if self.Fit_Param_window_launch == 0:
                self.Fit_Param_window_launch = 1
                self.frame_Fit_Param_window = ParametersWindow(self)
                self.frame_Fit_Param_window.Show()
            else:
                self.frame_Fit_Param_window.Show()
            pub.sendMessage(pubsub_Open_Option_Window)
        elif test == 1:
            self.frame_Fit_Param_window.Hide()
            self.SetFocus()

    def on_display_fit_report_window(self, test=None):
        """
        Open Fit Report window
        """
        if test is None:
            if self.Fit_Report_window_launch == 0:
                self.Fit_Report_window_launch = 1
                self.frame_Fit_Report_window = FitReportWindow(self)
                self.frame_Fit_Report_window.Show()
            else:
                self.frame_Fit_Report_window.Show()
            pub.sendMessage(pubsub_Open_FitReport_Window)
        elif test == 1:
            self.frame_Fit_Report_window.Hide()
            self.SetFocus()

    def on_display_GSA_window(self, test=None):
        """
        Open GSA Parameters window
        """
        if test is None:
            if self.GSA_window_launch == 0:
                self.GSA_window_launch = 1
                self.frame_GSA_window = GSAParametersWindow(self)
                self.frame_GSA_window.Show()
            else:
                self.frame_GSA_window.Show()
            pub.sendMessage(pubsub_Open_GSA_Window)
        else:
            self.frame_GSA_window.Hide()
            self.SetFocus()

    def on_display_Color_window(self, test=None):
        """
        Open Graph option window
        """
        if test is None:
            if self.color_window_launch == 0:
                self.color_window_launch = 1
                self.frame_color_window = ColorWindow(self)
                self.frame_color_window.Show()
            else:
                self.frame_color_window.Show()
            pub.sendMessage(pubsub_Open_Color_Window)
        else:
            self.frame_color_window.Hide()
            self.SetFocus()

    def on_display_data_coef_window(self, test=None):
        """
        Open sp dwp coefficients value window
        """
        if test is None:
            if self.data_coef_window_launch == 0:
                self.data_coef_window_launch = 1
                self.frame_data_coef_window = DataCoefPanel(self)
                self.frame_data_coef_window.Show()
            else:
                self.frame_data_coef_window.Show()
            pub.sendMessage(pubsub_Open_data_coef_Window)
            pub.sendMessage(pubsub_Fill_List_coef)
        else:
            self.frame_data_coef_window.Hide()
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
                    sys.exit()
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
                    sys.exit()
                else:
                    logger.log(logging.INFO, "Project not saved")
                    logger.log(logging.INFO, "End of the project\n")
                    sys.exit()
        else:
            _msg = "Do you really want to close this application?"
            dlg = GMD.GenericMessageDialog(None, _msg, "Confirm Exit",
                                           agwStyle=wx.OK | wx.CANCEL |
                                           wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                logger.log(logging.INFO, "End of the project\n")
                sys.exit()


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
                             Position(1))

        all_panes = self.aui_mgr.GetAllPanes()
        '''
        Theme for Notebook
        aui.AuiDefaultTabArt(), aui.AuiSimpleTabArt(), aui.VC71TabArt()
        aui.FF2TabArt(), aui.VC8TabArt(), aui.ChromeTabArt()
        '''
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
                             CenterPane().PaneBorder(False).Position(1))
        self.aui_mgr.GetPane("notebook_content").dock_proportion = 75
        self.aui_mgr.GetPane("Graph_Window").dock_proportion = 100
        screen_size = wx.GetDisplaySize()
        if screen_size[1] >= 1000:
            self.parent.SetSizeHints(minW=1180, minH=1035)
        self.Layout()
        self.Fit()
        self.Centre(wx.BOTH)
        self.aui_mgr.Update()
        P4Rm.log_window_status = False

        pub.subscribe(self.OnAddDelete, pubsub_enable_dis_database)
        pub.subscribe(self.on_show_panel, pubsub_show_panel)

        a = P4Rm()
        if a.DefaultDict['use_database'] is True:
            self.OnAddDelete(0)
        else:
            self.OnAddDelete(1)

        b = Calcul4Radmax()
        b.on_new_project()

    def OnAddDelete(self, case):
        if case == 0:
            if not _platform == 'darwin':
                self.Freeze()
                page4 = DataBasePanel(self.parent, self.statusbar)
                page5 = DataBaseManagement(self.parent, self.statusbar)
                self.notebook.AddPage(page4, "DataBase")
                self.notebook.AddPage(page5, "DataBase Management")
                self.notebook.SetCloseButton(3, False)
                self.notebook.SetCloseButton(4, False)
                self.Thaw()
            else:
                self.notebook.EnableTab(3, True)
                self.notebook.EnableTab(4, True)
        elif case == 1:
            if not _platform == 'darwin':
                if self.notebook.GetPageCount() > 3:
                    self.Freeze()
                    page4 = DataBasePanel(self.parent, self.statusbar)
                    page5 = DataBaseManagement(self.parent, self.statusbar)
                    self.notebook.DeletePage(3)
                    self.notebook.DeletePage(3)
                    self.Thaw()
            else:
                self.notebook.EnableTab(3, False)
                self.notebook.EnableTab(4, False)

    def on_show_panel(self):
        self.notebook.SetSelection(0)


# -----------------------------------------------------------------------------
class AUINotebook(aui.AuiNotebook):
    """
    AUI Notebook class
    """
    def __init__(self, parent, statusbar):
        aui.AuiNotebook.__init__(self, parent=parent)
        self.parent = parent
        self.statusbar = statusbar

        self.default_style = (aui.AUI_NB_CLOSE_ON_ALL_TABS)
        self.SetAGWWindowStyleFlag(self.default_style)

        """create the page windows as children of the notebook"""
        page1 = InitialDataPanel(self.parent, self.statusbar)
        page2 = SampleGeometry(self.parent, self.statusbar)
        page3 = FittingPanel(self.parent, self.statusbar)

        """add the pages to the notebook with the label to show on the tab"""
        self.AddPage(page1, "Initial Parameters")
        self.AddPage(page2, "Sample Geometry")
        self.AddPage(page3, "Fitting window")

        self.SetCloseButton(0, False)
        self.SetCloseButton(1, False)
        self.SetCloseButton(2, False)

        if _platform == 'darwin':
            page4 = DataBasePanel(self.parent, self.statusbar)
            page5 = DataBaseManagement(self.parent, self.statusbar)
            self.AddPage(page4, "DataBase")
            self.AddPage(page5, "DataBase Management")
            self.SetCloseButton(3, False)
            self.SetCloseButton(4, False)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(0)
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()
