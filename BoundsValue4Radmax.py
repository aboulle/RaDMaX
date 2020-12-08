#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

import sys
import wx

sys.path.insert(0, './modules')
from pubsub import pub

import Parameters4Radmax as p4R
from Parameters4Radmax import P4Rm

from Icon4Radmax import prog_icon, prog_icon_curve

from Calcul4Radmax import Calcul4Radmax

from ObjectListView import ObjectListView, ColumnDefn
from ObjectListView import EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_FINISHING

from sys import platform as _platform

"""Pubsub message"""
pubsub_Hide_Show_data_coef = "HideShowDataCoef"
pubsub_Open_data_coef_Window = "OpenDataCoefWindow"

pubsub_Fill_List_coef = "FillListCoef"
pubsub_update_sp_dwp_eta = "UpdatespdwpEta"

headercolumnname = ["name", "Strain", "state1", "DW", "state2"]
asym_pv = ['heigt', 'loc', 'fwhm_1', 'fwhm_2', 'eta_1', 'eta_2', 'bkg']


# -----------------------------------------------------------------------------
class CoefListData(object):
    def __init__(self, name, sp, state1, dwp, state2):
        """
        Constructor
        """
        self.name = name
        self.sp = sp
        self.state1 = state1
        self.dwp = dwp
        self.state2 = state2


# -----------------------------------------------------------------------------
class DataCoefPanel(wx.Frame):
    def __init__(self, parent):
        pos = wx.DefaultPosition
        size = (377, 282)
        if _platform == 'darwin':
            style = wx.DEFAULT_FRAME_STYLE
        else:
            style = (wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX |
                     wx.CLIP_CHILDREN | wx.FRAME_FLOAT_ON_PARENT)
        wx.Frame.__init__(self, wx.GetApp().TopWindow, wx.ID_ANY,
                          p4R.Application_name + " - Strain and DW Values",
                          pos, size, style)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.SetIcon(prog_icon.GetIcon())

        pnl = wx.Panel(self)

        def handleCellEditStarting(evt):
            currentCol = self.GetOLVColClicked(evt)
            if currentCol == 0:
                evt.Veto()

        def handleCellEditFinishing(evt):
            currentline = evt.rowIndex
            currentCol = self.GetOLVColClicked(evt)
            val = evt.cellValue
            self.update_param_dict(currentline, currentCol, val)

        self.list = ObjectListView(pnl, sortable=False,
                                   style=wx.LC_REPORT | wx.SUNKEN_BORDER,
                                   size=(450, 500))
        self.list.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK
        self.list.handleStandardKeys = False
        self.list.SetEmptyListMsg("This database has no rows")
        self.list.SetEmptyListMsgFont(wx.FFont(24, wx.DEFAULT,
                                               faceName="Tekton"))

        if _platform == "linux" or _platform == "linux2":
            self.width_name = 120
        else:
            self.width_name = 80
        self.width = 70
        self.widthCheck = 25
        self.col2checkstatus = {1: 0, 2: 0}

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnItemSelected, self.list)
        self.list.Bind(EVT_CELL_EDIT_STARTING, handleCellEditStarting)
        self.list.Bind(EVT_CELL_EDIT_FINISHING, handleCellEditFinishing)

        mastersizer = wx.BoxSizer(wx.HORIZONTAL)
        mastersizer.Add(self.list, 0,  wx.ALL | wx.EXPAND, 5)

        pub.subscribe(self.on_fill_list, pubsub_Fill_List_coef)
        pub.subscribe(self.on_open_window, pubsub_Open_data_coef_Window)

#        self.Bind(wx.EVT_SIZE, self.OnSize)
        pnl.SetSizer(mastersizer)
        pnl.Layout()
        pnl.Fit()
        self.InitializeList()

    def on_open_window(self):
        self.CenterOnParent()

    def on_close(self, event):
        pub.sendMessage(pubsub_Hide_Show_data_coef, test=1)

    def InitializeList(self):
        temp = []
        ic_ = prog_icon_curve.GetBitmap()
        ImageIndex = self.list.AddImages(ic_)
        self.list.AddNamedImages("name", ic_)

        temp.append(ColumnDefn(headercolumnname[0], "center", self.width_name,
                               valueGetter=headercolumnname[0],
                               imageGetter=ImageIndex,
                               maximumWidth=self.width_name))
        temp.append(ColumnDefn(headercolumnname[1], "center", self.width,
                               valueGetter="sp",
                               maximumWidth=self.width,
                               checkStateGetter="state1"))
        temp.append(ColumnDefn(headercolumnname[3], "center", self.width,
                               valueGetter="dwp",
                               maximumWidth=self.width,
                               checkStateGetter="state2"))
        self.list.SetColumns(temp)

    def on_fill_list(self):
        a = P4Rm()
        self.Freeze()
        list_temp = []
        roundval = 3
        if a.AllDataDict['model'] == 2:
            for i in range(7):
                name = asym_pv[i]
                val_sp = str(round(a.ParamDict['sp'][i], roundval))
                val_dwp = str(round(a.ParamDict['dwp'][i], roundval))
                check_sp = a.ParamDict['state_sp'][i]
                check_dwp = a.ParamDict['state_dwp'][i]
                list_temp.append(CoefListData(name, val_sp, check_sp,
                                              val_dwp, check_dwp))
        else:
            len_sp = len(a.ParamDict['sp'])
            len_dwp = len(a.ParamDict['dwp'])
            if len_sp > len_dwp:
                num = len_sp
            else:
                num = len_dwp
            for i in range(num):
                if i < len_sp:
                    val_sp = str(round(a.ParamDict['sp'][i], roundval))
                    check_sp = a.ParamDict['state_sp'][i]
                else:
                    val_sp = ""
                    check_sp = True
                if i < len_dwp:
                    val_dwp = str(round(a.ParamDict['dwp'][i], roundval))
                    check_dwp = a.ParamDict['state_dwp'][i]
                else:
                    val_dwp = ""
                    check_dwp = True
                list_temp.append(CoefListData(i+1, val_sp, check_sp,
                                              val_dwp, check_dwp))
        self.list.SetObjects(list_temp)
        self.Thaw()

    def update_param_dict(self, currentline, currentCol, val):
        if currentCol == 1:
            P4Rm.ParamDict['sp'][currentline] = float(val)
        if currentCol == 2:
            P4Rm.ParamDict['dwp'][currentline] = float(val)
        self.read_and_update()

    def read_and_update(self):
        pub.sendMessage(pubsub_update_sp_dwp_eta)
        b = Calcul4Radmax()
        b.on_update()

    def OnItemSelected(self, event):
        if 'phoenix' in wx.PlatformInfo:
            currentline = event.Index
        else:
            currentline = event.m_itemIndex
        currentCol = self.GetOLVColClicked(event)
        if currentline == -1:
            self.Freeze()
            if currentCol == 1 or currentCol == 2:
                if self.col2checkstatus[currentCol] == 0:
                    val = False
                    self.col2checkstatus[currentCol] = 1
                else:
                    val = True
                    self.col2checkstatus[currentCol] = 0
                objects = self.list.GetObjects()
                if currentCol == 1:
                    for obj in objects:
                        obj.state1 = val
                elif currentCol == 2:
                    for obj in objects:
                        obj.state2 = val
                self.list.SetObjects(objects)
                self.list.RefreshObject(objects)
            self.Thaw()
        if currentCol == 1 or currentCol == 2:
            a = P4Rm()
            objects = self.list.GetObjects()
            len_sp = len(a.ParamDict['sp'])
            len_dwp = len(a.ParamDict['dwp'])
            check_sp = []
            check_dwp = []
            i = 0
            for obj in objects:
                if i < len_sp:
                    check_sp.append(obj.state1)
                if i < len_dwp:
                    check_dwp.append(obj.state2)
                i += 1
            P4Rm.ParamDict['state_sp'] = check_sp
            P4Rm.ParamDict['state_dwp'] = check_dwp

    def GetOLVColClicked(self, event):
        """
        DevPlayer@gmail.com  2011-01 Jan-13
        For use with a 3rd party module named ObjectListView
        used with wxPython.
        """

        spt = wx.GetMousePosition()
        fpt = self.list.ScreenToClient(spt)
        x, y = fpt
        last_col = 0
        for col in range(self.list.GetColumnCount()):
            col_width = self.list.GetColumnWidth(col)
            left_pxl_col = last_col
            right_pxl_col = last_col + col_width - 1

            if left_pxl_col <= x <= right_pxl_col:
                col_selected = col
                break
            col_selected = None
            last_col = last_col + col_width
        return col_selected

    def OnSize(self, event):
        sizet = event.GetSize()
        print ("%s, %s" % (sizet.width, sizet.height))
        event.Skip()
