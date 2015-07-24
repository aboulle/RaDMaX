#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A_BOULLE & M_SOUILAH
# Version du : 22/06/2014

try:
    import wx, wx.html
except ImportError:
    raise ImportError, "The wxPython module is required to run this program"

from myIcon import NewP24, LoadP24, saveP24, saveasP24, shutdown24
from myIcon import parameters, bars_graph, prog_icon, About_icon

from Graph4Diff import RightGraph, Graph_window
from Parameters_Panel import InitialDataPanel
from Fitting_Panel import FittingPanel
from Parameters4Diff import *

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

#------------------------------------------------------------------------------
class MainFrame(wx.Frame):
    def __init__(self):
        pos=wx.DefaultPosition
        size = (1000, 900)
        wx.Frame.__init__(self, None, wx.ID_ANY, Application_name, pos, size)
        wx.Frame.CenterOnScreen(self)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.sb = wx.StatusBar(self, -1)
        self.sb.SetFieldsCount(3)
        self.SetStatusBar(self.sb)
        self.SetStatusWidths([-4, -1, -1])

#        self.SetIcon(prog_icon.GetIcon())

        self.m_menubar = wx.MenuBar()
        self.m_menufile = wx.Menu()
        self.NewP_ID = wx.ID_NEW
        self.LoadP_ID = wx.NewId()
        self.Load_XRD_ID = wx.NewId()
        self.Load_Strain_ID = wx.NewId()
        self.Load_DW_ID = wx.NewId()
        self.Save_ID = wx.NewId()
        self.SaveP_ID = wx.NewId()
        self.m_menunewproject = wx.MenuItem( self.m_menufile, self.NewP_ID, u"New Project"+ u"\t" + u"Ctrl+N", u"Begin a new project" , wx.ITEM_NORMAL )
        self.m_menunewproject.SetBitmap(wx.BitmapFromIcon(NewP24.GetIcon()))
        self.m_menufile.AppendItem( self.m_menunewproject )
        
        self.m_menuload = wx.MenuItem( self.m_menufile, self.LoadP_ID, u"Load Project"+ u"\t" + u"Ctrl+O", u"Load .ini file", wx.ITEM_NORMAL )
        self.m_menuload.SetBitmap(wx.BitmapFromIcon(LoadP24.GetIcon()))
        self.m_menufile.AppendItem( self.m_menuload )
        self.m_menufile.AppendSeparator()

        self.m_menuloadXRD = wx.MenuItem( self.m_menufile, self.Load_XRD_ID, u"Import XRD data"+ u"\t" + u"Alt-O", u"Import XRD data file", wx.ITEM_NORMAL )
#        self.m_menuloadXRD.SetBitmap(wx.BitmapFromIcon(NewP24.GetIcon()))
        self.m_menufile.AppendItem( self.m_menuloadXRD )
        
        self.m_menuloadStrain = wx.MenuItem( self.m_menufile, self.Load_Strain_ID, u"Import Strain", wx.EmptyString, wx.ITEM_NORMAL )
#        self.m_menuloadStrain.SetBitmap(wx.BitmapFromIcon(LoadP24.GetIcon()))
        self.m_menufile.AppendItem( self.m_menuloadStrain )
        self.m_menuloadStrain.Enable(False)

        self.m_menuloadDW = wx.MenuItem( self.m_menufile, self.Load_DW_ID, u"Import DW", wx.EmptyString, wx.ITEM_NORMAL )
#        self.m_menuloadStrain.SetBitmap(wx.BitmapFromIcon(LoadP24.GetIcon()))
        self.m_menufile.AppendItem( self.m_menuloadDW )
        self.m_menuloadDW.Enable(False)
        self.m_menufile.AppendSeparator()

        self.m_menusave = wx.MenuItem( self.m_menufile, self.Save_ID, u"Save"+ u"\t" + u"Ctrl+S", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menusave.SetBitmap(wx.BitmapFromIcon(saveP24.GetIcon()))
        self.m_menufile.AppendItem( self.m_menusave )

        self.m_menusaveas = wx.MenuItem( self.m_menufile, self.SaveP_ID, u"Save As"+ u"\t" + u"Ctrl-Shift+S", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menusaveas.SetBitmap(wx.BitmapFromIcon(saveasP24.GetIcon()))
        self.m_menufile.AppendItem( self.m_menusaveas )

        self.m_menuexit = wx.MenuItem( self.m_menufile, wx.ID_EXIT, u"Exit"+ u"\t" + u"Alt-X", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuexit.SetBitmap(wx.BitmapFromIcon(shutdown24.GetIcon()))
        self.m_menufile.AppendItem( self.m_menuexit )

        self.m_menubar.Append( self.m_menufile, u"&File" ) 

        self.m_menuoptions = wx.Menu()
        self.m_menubar.Append( self.m_menuoptions, u"O&ptions" ) 

        self.m_menuhelp = wx.Menu()
        self.m_menuabout = wx.MenuItem( self.m_menuhelp, wx.ID_ABOUT, u"About..."+ u"\t" + u"F1", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuhelp.AppendItem( self.m_menuabout )

        self.m_menubar.Append( self.m_menuhelp, u"&Help" ) 

        self.SetMenuBar(self.m_menubar)
        
        self.Bind(wx.EVT_MENU, self.SetMenu)
        self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnAboutBox, id=wx.ID_ABOUT)

        pub.subscribe(self.OnChangeTitle, pubsub_ChangeFrameTitle)
        pub.subscribe(self.OnActivateImport, pubsub_Activate_Import)
        
        panel = MainPanel(self, self.sb)
        self.Show()
        pub.sendMessage(pubsub_Launch_GUI)

    def some_method(self, event):
        self.statusbar.SetStatusText('', 0)
        self.statusbar.SetStatusText('', 1)
        self.statusbar.SetStatusText('', 2)

    def OnActivateImport(self):
        self.m_menuloadStrain.Enable(True)
        self.m_menuloadStrain.SetHelp(u"Import Strain file")
        self.m_menuloadDW.Enable(True)
        self.m_menuloadDW.SetHelp( u"Import DW file")
       
    def SetMenu(self, event):
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
    
    def OnAboutBox(self, event):
        info = wx.AboutDialogInfo()
#        info.SetIcon(About_icon.GetIcon())
        info.SetName(Application_name)
        info.SetVersion('1.0')
        info.SetCopyright('(C) 2015 SPCTS')
        info.SetDescription(description)
        info.SetWebSite('http://www.unilim.fr/spcts/')
        info.AddDeveloper('Alexandre Boulle')
        info.AddDeveloper('Marc Souilah')
        wx.AboutBox(info)

    def OnChangeTitle(self, NewTitle):
        self.SetTitle(NewTitle)

    def OnClose(self, event):
        titlelabel = self.GetLabel().split(' - ')
        if len(titlelabel) > 1:
            if titlelabel[1] != "New Project":
                dlg = GMD.GenericMessageDialog(None, "Do you really want to close this application?",
                "Confirm Exit", agwStyle = wx.OK|wx.CANCEL|wx.ICON_QUESTION)
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_OK:
                    logger.log(logging.INFO, "End of the project\n")
                    sys.exit()
            else:
                dlg = GMD.GenericMessageDialog(None, "Project has not been saved\nDo you want to save it now ?",
                "Confirm Exit", agwStyle = wx.OK|wx.CANCEL|wx.ICON_QUESTION)
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
            dlg = GMD.GenericMessageDialog(None, "Do you really want to close this application?",
            "Confirm Exit", agwStyle = wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                logger.log(logging.INFO, "End of the project\n")
                sys.exit()            

#------------------------------------------------------------------------------
class MainPanel(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar
 
        self.panel1 = wx.Panel( self, wx.ID_ANY)
        self.aui_mgr = aui.AuiManager()
        self.aui_mgr.SetManagedWindow( self)

        ''' create the AUI Notebook  '''      
        self.notebook = AUINotebook(self, self.statusbar)

        ''' add notebook to AUI manager '''
        self.aui_mgr.AddPane( self.notebook, aui.AuiPaneInfo().Name( "notebook_content" ).
                             CenterPane().PaneBorder( False ).Position(1).MaximizeButton(False))

        all_panes = self.aui_mgr.GetAllPanes()
        '''Theme for Notebook
        aui.AuiDefaultTabArt(), aui.AuiSimpleTabArt(), aui.VC71TabArt()
        aui.FF2TabArt(), aui.VC8TabArt(), aui.ChromeTabArt()'''
        #for apply theme to all notebook
        for pane in all_panes :
            nb = pane.window
            tabArt = aui.ChromeTabArt()
            nb.SetArtProvider(tabArt)
            self._notebook_theme = 1
            nb.Refresh()
            nb.Update()

        self.aui_mgr.AddPane(GraphPanel(self, self.statusbar), aui.AuiPaneInfo().Name("Graph_Window").CenterPane().PaneBorder( False ).Position(1).MaximizeButton(False))
        self.aui_mgr.GetPane("notebook_content").dock_proportion = 70
        self.aui_mgr.GetPane("Graph_Window").dock_proportion = 90
        self.Layout()
        self.Centre( wx.BOTH )
        self.aui_mgr.Update()

#------------------------------------------------------------------------------
class AUINotebook(aui.AuiNotebook) :
    """ AUI Notebook class """
    def __init__(self, parent, statusbar) :
        aui.AuiNotebook.__init__( self, parent=parent)
        self.parent = parent
        self.statusbar = statusbar

        self.default_style = aui.AUI_NB_DEFAULT_STYLE & aui.AUI_NB_CLOSE_ON_ALL_TABS
        self.SetAGWWindowStyleFlag(self.default_style)
        
        """create the page windows as children of the notebook"""
        page1 = InitialDataPanel(self.parent, self.statusbar)
        page2 = FittingPanel(self.parent, self.statusbar)

        """add the pages to the notebook with the label to show on the tab"""
        self.AddPage(page1, "Initial Parameters")
        self.AddPage(page2, "Fitting window")

        self.SetCloseButton(page1, False)
        self.SetCloseButton(page2, False)

#------------------------------------------------------------------------------
class GraphPanel(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar

        vSplitter = wx.SplitterWindow(self)
        panelOne = Graph_window(vSplitter, self.statusbar)
        panelTwo = RightGraph(vSplitter, self.statusbar)
        vSplitter.SplitVertically(panelOne, panelTwo)
        vSplitter.SetSashGravity(0.5)       
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(vSplitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

#------------------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
