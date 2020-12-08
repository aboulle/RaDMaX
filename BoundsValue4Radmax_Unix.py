#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

import wx
sys.path.insert(0, './modules')
from pubsub import pub

import Parameters4Radmax as p4R
from Parameters4Radmax import P4Rm

from Icon4Radmax import prog_icon

from Calcul4Radmax import Calcul4Radmax
import wx.grid as Grid

from sys import platform as _platform

"""Pubsub message"""
pubsub_Hide_Show_data_coef = "HideShowDataCoef"
pubsub_Open_data_coef_Window = "OpenDataCoefWindow"

pubsub_Fill_List_coef = "FillListCoef"
pubsub_update_sp_dwp_eta = "UpdatespdwpEta"
asym_pv = ['heigt', 'loc', 'fwhm_1', 'fwhm_2', 'eta_1', 'eta_2', 'bkg']
coll = [0, 1, 3]


# -----------------------------------------------------------------------------
class DataTable(Grid.PyGridTableBase):
    def __init__(self):
        Grid.PyGridTableBase.__init__(self)

        self.colLabels = ['name', 'Strain', '', 'DW', '']
        self.dataTypes = [Grid.GRID_VALUE_STRING,
                          Grid.GRID_VALUE_FLOAT,
                          Grid.GRID_VALUE_BOOL,
                          Grid.GRID_VALUE_FLOAT,
                          Grid.GRID_VALUE_BOOL]

        self.data = []
        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.colLabels)

    def GetValue_(self, row, col):
        typename = self.GetTypeName(row, col)
        return self.GetValueAsCustom(row, col, typename)

    def GetValueAsCustom(self, row, col, typeName):
        return self.data[row][col]

    def GetValue(self, row, col):
        return self.data[row][col]

    def GetValueAsDouble(self, row, col):
        try:
            return self.data[row][col]
        except (IndexError, TypeError):
            print ('ggggg')
            pass

    def GetValueAsBool(self, row, col):
        return self.data[row][col]

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    def SetValue(self, row, col, value):
        typename = self.GetTypeName(row, col)
        return self.SetValueAsCustom(row, col, typename, value)
#        self.data[row][col] = value

    def SetValueAsCustom(self, row, col, typeName, value):
        self.data[row][col] = value

    def SetValueAsDouble(self, row, col, value):
        self.data[row][col] = value

    def SetValueAsBool(self, row, col, value):
        self.data[row][col] = value

    # --------------------------------------------------
    # Some optional methods

    def SetDataTable(self, data):
        self.data = data

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]

    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)

    def ResetView(self, grid):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        grid.BeginBatch()

        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(),
             Grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
             Grid.GRIDTABLE_NOTIFY_ROWS_APPENDED)]:
            if new < current:
                msg = Grid.GridTableMessage(self, delmsg, new, current-new)
                self.GetView().ProcessTableMessage(msg)
            elif new > current:
                msg = Grid.GridTableMessage(self, addmsg, new-current)
                self.GetView().ProcessTableMessage(msg)
                msg = Grid.GridTableMessage(self,
                                            Grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
                grid.ProcessTableMessage(msg)

        grid.EndBatch()

        self._rows = self.GetNumberRows()

        # update the scrollbars and the displayed part of the grid
        grid.AdjustScrollbars()
        grid.Refresh()

    def UpdateValues(self, grid):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = Grid.GridTableMessage(self,
                                    Grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)
#        self._rows = self.GetNumberRows()
#        self._cols = self.GetNumberCols()
#        for row in range(self._rows):
#            for col in range(self._cols):
#                typ = self.GetTypeName(row, col)
#                if typ is Grid.GRID_VALUE_BOOL:
#                    if self.CanGetValueAs(row, col, typ):
#                        self.SetValueAsBool(self, row, col, value)
        grid.ForceRefresh()
        grid.Refresh()


# -----------------------------------------------------------------------------
class TableGrid(Grid.Grid):
    def __init__(self, parent):
        Grid.Grid.__init__(self, parent, -1)

        self._table = DataTable()

        self.SetTable(self._table, True)
        self.gridRowSize = 0
        self.firstLoop = 0

        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)

        self.Bind(Grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnLeftDClick)

    # I do this because I don't like the default behaviour of not starting the
    # cell editor on double clicks, but only a second click.
    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

    def DTable(self, arg):
        if self.gridRowSize is 0:
            self.gridRowSize = len(arg)
        self._table.SetDataTable(arg)
        self.Reset()

    def Update(self):
        self.UpdateValues()

    def Reset(self):
        self._table.ResetView(self)

    def UpdateValues(self):
        self._table.UpdateValues(self)

    def SetColor(self, num):
        if self.firstLoop is 0:
            for row in range(num):
                if row & 1:
                    attr = Grid.GridCellAttr()
                    attr.SetBackgroundColour(wx.Colour(255, 255, 204))
                    self.SetRowAttr(row, attr)
                    for col in coll:
                        attr = self.GetOrCreateCellAttr(row, col)
                        attr = attr.Clone()
                        attr.SetAlignment(wx.RIGHT, -1)
                        self.SetColAttr(col, attr)
            self.firstLoop = 1
            return
        if self.gridRowSize is num:
            for row in range(num):
                if row & 1:
                    attr = self.GetOrCreateCellAttr(row, 0)
                    attr = attr.Clone()
                    attr.SetBackgroundColour(wx.Colour(255, 255, 204))
                    self.SetRowAttr(row, attr)
                    for col in coll:
                        attr = self.GetOrCreateCellAttr(row, col)
                        attr = attr.Clone()
                        attr.SetAlignment(wx.RIGHT, -1)
                        self.SetColAttr(col, attr)
        else:
            for row in range(num):
                if row < self.gridRowSize:
                    if row & 1:
                        attr = self.GetOrCreateCellAttr(row, 0)
                        attr = attr.Clone()
                        attr.SetBackgroundColour(wx.Colour(255, 255, 204))
                        self.SetRowAttr(row, attr)
                        for col in coll:
                            attr = self.GetOrCreateCellAttr(row, col)
                            attr = attr.Clone()
                            attr.SetAlignment(wx.RIGHT, -1)
                            self.SetColAttr(col, attr)
                else:
                    if row & 1:
                        attr = Grid.GridCellAttr()
                        attr.SetBackgroundColour(wx.Colour(255, 255, 204))
                        self.SetRowAttr(row, attr)
                        for col in coll:
                            attr = self.GetOrCreateCellAttr(row, col)
                            attr = attr.Clone()
                            attr.SetAlignment(wx.RIGHT, -1)
                            self.SetColAttr(col, attr)
            self.gridRowSize = num
        self.ForceRefresh()
        self.Refresh()

    def GetValue(self, row, col):
        return self._table.GetValue_(row, col)

    def SetValue(self, row, col, val):
        self._table.SetValue(row, col, val)


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

        self.list = TableGrid(pnl)

        if _platform == "linux" or _platform == "linux2":
            self.width_name = 70
        else:
            self.width_name = 50
        self.width = 70
        self.widthCheck = 25
        self.col2checkstatus = {2: 0, 4: 0}

        self.Bind(Grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnItemSelected)
#        self.Bind(Grid.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(Grid.EVT_GRID_CELL_CHANGING, self.OnCellChanging)
        self.Bind(Grid.EVT_GRID_CELL_CHANGED, self.OnCellChanged)
        self.Bind(Grid.EVT_GRID_EDITOR_SHOWN, self.OnEditorHidden)
        self.Bind(Grid.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)

        mastersizer = wx.BoxSizer(wx.HORIZONTAL)
        mastersizer.Add(self.list, 0,  wx.EXPAND, 5)

        pub.subscribe(self.on_fill_list, pubsub_Fill_List_coef)
        pub.subscribe(self.on_open_window, pubsub_Open_data_coef_Window)

#        self.Bind(wx.EVT_SIZE, self.OnSize)
        pnl.SetSizer(mastersizer)
        pnl.Layout()
        pnl.Fit()

    def on_open_window(self):
        self.CenterOnParent()

    def on_close(self, event):
        pub.sendMessage(pubsub_Hide_Show_data_coef, test=1)

    def on_fill_list(self):
        a = P4Rm()
        list_temp = []
        roundval = 3
        if a.AllDataDict['model'] == 2:
            for i in range(7):
                name = asym_pv[i]
                val_sp = round(a.ParamDict['sp'][i], roundval)
                val_dwp = round(a.ParamDict['dwp'][i], roundval)
                check_sp = a.ParamDict['state_sp'][i]
                check_dwp = a.ParamDict['state_dwp'][i]
                list_temp.append([name, val_sp, check_sp,
                                  val_dwp, check_dwp])
        else:
            len_sp = len(a.ParamDict['sp'])
            len_dwp = len(a.ParamDict['dwp'])
            if len_sp > len_dwp:
                num = len_sp
            else:
                num = len_dwp
            for i in range(num):
                if i < len_sp:
                    val_sp = round(a.ParamDict['sp'][i], roundval)
                    check_sp = a.ParamDict['state_sp'][i]
                else:
                    val_sp = ""
                    check_sp = True
                if i < len_dwp:
                    val_dwp = round(a.ParamDict['dwp'][i], roundval)
                    check_dwp = a.ParamDict['state_dwp'][i]
                else:
                    val_dwp = ""
                    check_dwp = True
                list_temp.append([str(i+1), val_sp, check_sp, val_dwp, check_dwp])
        self.list.DTable(list_temp)
        self.list.SetColor(len(list_temp))
        for i in range(len(list_temp)):
            if i == 0:
                self.list.SetColSize(i, self.width_name)
            if i == 2 or i == 4:
                self.list.SetColSize(i, self.widthCheck)
            if i == 1 or i == 3:
                self.list.SetColSize(i, self.width)
#        self.list.ForceRefresh()

    def read_and_update(self):
        pub.sendMessage(pubsub_update_sp_dwp_eta)
        b = Calcul4Radmax()
        b.on_update()

    def OnEditorHidden(self, event):
        currentCol = event.GetCol()
        if currentCol == 0:
            event.Veto()
            return

    def OnCellChanging(self, event):
        currentline = event.GetRow()
        currentCol = event.GetCol()
        if currentCol is 2:
            if self.list.GetValue(currentline, currentCol):
                P4Rm.ParamDict['state_sp'][currentline] = True
            else:
                P4Rm.ParamDict['state_sp'][currentline] = False
            self.list.Update()
        elif currentCol is 4:
            if self.list.GetValue(currentline, currentCol):
                P4Rm.ParamDict['state_dwp'][currentline] = True
            else:
                P4Rm.ParamDict['state_dwp'][currentline] = False
            self.list.Update()
        event.Skip()

    def OnCellChanged(self, event):
        currentline = event.GetRow()
        currentCol = event.GetCol()
        if currentCol is 1:
            P4Rm.ParamDict['sp'][currentline] = float(self.list.GetValue(currentline, currentCol))
            self.list.Update()
            self.read_and_update()
        elif currentCol is 3:
            P4Rm.ParamDict['dwp'][currentline] = float(self.list.GetValue(currentline, currentCol))            
            self.list.Update()
            self.read_and_update()
        elif currentCol is 2:
            if self.list.GetValue(currentline, currentCol):
                P4Rm.ParamDict['state_sp'][currentline] = True
            else:
                P4Rm.ParamDict['state_sp'][currentline] = False
            self.list.Update()
            self.read_check()
        elif currentCol is 4:
            if self.list.GetValue(currentline, currentCol):
                P4Rm.ParamDict['state_dwp'][currentline] = True
            else:
                P4Rm.ParamDict['state_dwp'][currentline] = False
            self.list.Update()
            self.read_check()
        event.Skip()

    def OnItemSelected(self, event):
        currentline = event.GetRow()
        currentCol = event.GetCol()
        if currentline == -1:
            if currentCol is 2 or currentCol is 4:
                if self.col2checkstatus[currentCol] == 0:
                    val = False
                    self.col2checkstatus[currentCol] = 1
                else:
                    val = True
                    self.col2checkstatus[currentCol] = 0
                self.read_check_all(currentCol, val)
        event.Skip()

    def read_check_all(self, currentCol, val):
        a = P4Rm()
        if currentCol is 2:
            sp_line = len(a.ParamDict['sp'])
            for currentline in range(sp_line):
                self.list.SetValue(currentline, 2, val)
        elif currentCol is 4:
            dwp_line = len(a.ParamDict['dwp'])
            for currentline in range(dwp_line):
                self.list.SetValue(currentline, 4, val)
        self.list.Update()
        self.read_check()

    def read_check(self):
        a = P4Rm()
        sp_line = len(a.ParamDict['sp'])
        dwp_line = len(a.ParamDict['dwp'])
        for currentline in range(sp_line):
            temp = self.list.GetValue(currentline, 2)
            if temp:
                P4Rm.ParamDict['state_sp'][currentline] = True
            else:
                P4Rm.ParamDict['state_sp'][currentline] = False
        for currentline in range(dwp_line):
            temp = self.list.GetValue(currentline, 4)
            if temp:
                P4Rm.ParamDict['state_dwp'][currentline] = True
            else:
                P4Rm.ParamDict['state_dwp'][currentline] = False

    def OnSize(self, event):
        sizet = event.GetSize()
        print ("%s, %s" % (sizet.width, sizet.height))
        event.Skip()
