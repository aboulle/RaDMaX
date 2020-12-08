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

from Icon4Radmax import prog_icon

from sys import platform as _platform

"""Pubsub message"""
pubsub_Hide_Show_FitReport = "HideShowFitReport"
pubsub_Open_FitReport_Window = "OpenFitReportWindow"


# ------------------------------------------------------------------------------
class FitReportWindow(wx.Frame):
    def __init__(self, parent):
        pos = wx.DefaultPosition
        size = (615, 527)
        style = (wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX |
                 wx.CLIP_CHILDREN | wx.FRAME_FLOAT_ON_PARENT)
        wx.Frame.__init__(self, wx.GetApp().TopWindow, wx.ID_ANY,
                          p4R.Application_name + " - Fitting report",
                          pos, size, style)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.SetIcon(prog_icon.GetIcon())
        if _platform == "linux" or _platform == "linux2":
            font_update = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font_title = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        elif _platform == "win32":
            font_update = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font_title = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        elif _platform == 'darwin':
            font_update = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font_title = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        flagSizer = wx.ALIGN_CENTER | wx.LEFT

        pnl = wx.Panel(self)
        self.mastersizer = wx.GridBagSizer(hgap=4, vgap=3)

        label_0 = "Lmfit Leastsq fit report"
        label_txt = wx.StaticText(pnl, -1, label=label_0,
                                  size=(230, 44))
        label_txt.SetFont(font_title)

        self.label_1_a = "Success"
        self.label_1_a_txt = wx.StaticText(pnl, -1, label=self.label_1_a,
                                           size=(80, 44))
        self.label_1_a_txt.SetFont(font_update)
        l1 = wx.StaticLine(pnl, size=(3, 20), style=wx.LI_VERTICAL)

        self.label_1_b_txt = wx.StaticText(pnl, -1, label="",
                                           size=(250, 44))

        self.label_2_a = "Message"
        self.label_2_a_txt = wx.StaticText(pnl, -1, label=self.label_2_a,
                                           size=(80, 44))
        self.label_2_a_txt.SetFont(font_update)
        l2 = wx.StaticLine(pnl, size=(3, 20), style=wx.LI_VERTICAL)

        self.label_2_b_txt = wx.StaticText(pnl, -1, label="",
                                           size=(250, 44))

        self.label_3_a = "Ier"
        self.label_3_a_txt = wx.StaticText(pnl, -1, label=self.label_3_a,
                                           size=(80, 44))
        self.label_3_a_txt.SetFont(font_update)
        l3 = wx.StaticLine(pnl, size=(3, 20), style=wx.LI_VERTICAL)

        self.label_3_b_txt = wx.StaticText(pnl, -1, label="",
                                           size=(250, 44))

        l4 = wx.StaticLine(pnl, size=(3, 20), style=wx.LI_VERTICAL)
        label_3_c = "1, 2, 3 or 4, the solution was found"
        self.label_3_c_txt = wx.StaticText(pnl, -1, label=label_3_c,
                                           size=(250, 44))

        self._logFileContents = wx.TextCtrl(pnl, wx.ID_ANY, size=(600, 300),
                                            style=wx.TE_MULTILINE |
                                            wx.TE_READONLY | wx.VSCROLL)

        self.Textcontrol = [self.label_1_b_txt, self.label_2_b_txt,
                            self.label_3_b_txt]

        self.mastersizer.Add(label_txt, pos=(0, 1), span=(1, 2),
                             flag=wx.ALIGN_LEFT, border=5)
        self.mastersizer.Add(self.label_1_a_txt, pos=(1, 0),
                             flag=flagSizer, border=10)
        self.mastersizer.Add(l1, pos=(1, 1))
        self.mastersizer.Add(self.label_1_b_txt, pos=(1, 2),
                             flag=flagSizer)

        self.mastersizer.Add(self.label_2_a_txt, pos=(2, 0),
                             flag=flagSizer, border=10)
        self.mastersizer.Add(l2, pos=(2, 1))
        self.mastersizer.Add(self.label_2_b_txt, pos=(2, 2), span=(1, 2),
                             flag=flagSizer)

        self.mastersizer.Add(self.label_3_a_txt, pos=(3, 0),
                             flag=flagSizer, border=10)
        self.mastersizer.Add(l3, pos=(3, 1))
        self.mastersizer.Add(self.label_3_b_txt, pos=(3, 2),
                             flag=flagSizer)
        self.mastersizer.Add(l4, pos=(3, 3))
        self.mastersizer.Add(self.label_3_c_txt, pos=(3, 4),
                             flag=flagSizer)
        self.mastersizer.Add(self._logFileContents, pos=(4, 0), span=(1, 5),
                             flag=flagSizer)

        pub.subscribe(self.on_open_window, pubsub_Open_FitReport_Window)
        pub.subscribe(self.on_fill_report, pubsub_Open_FitReport_Window)
#        self.Bind(wx.EVT_SIZE, self.OnSize)
        pnl.SetSizer(self.mastersizer)
        pnl.Layout()
        pnl.Fit()

    def on_open_window(self):
        self.CenterOnParent()
        self.GetParent().Disable()

    def on_fill_report(self):
        a = P4Rm()
        data = a.FitDict['Leastsq_report']
        if data is not "":
            for i in range(3):
                self.Textcontrol[i].SetLabel(str(data[i]))
            self._logFileContents.SetValue(data[-1])
            self.Refresh()

    def on_close(self, event):
        self.GetParent().Enable()
        pub.sendMessage(pubsub_Hide_Show_FitReport, test=1)

    def OnSize(self, event):
        sizet = event.GetSize()
        print ("%s, %s" % (sizet.width, sizet.height))
        event.Skip()
