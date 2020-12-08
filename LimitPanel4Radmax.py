#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

import sys
import wx

sys.path.insert(0, './modules')
from pubsub import pub

import Parameters4Radmax as p4R

from Icon4Radmax import prog_icon
from Fitting4Radmax import Fitting4Radmax

from sys import platform as _platform

"""Pubsub message"""
pubsub_Hide_Show_GSA = "HideShowGSA"
pubsub_Open_GSA_Window = "OpenGSAWindow"


# -----------------------------------------------------------------------------
class GSAParametersWindow(wx.Frame):
    def __init__(self, parent):
        pos = wx.DefaultPosition
        size = (377, 282)
        style = (wx.SYSTEM_MENU | wx.CAPTION |
                 wx.CLIP_CHILDREN | wx.FRAME_FLOAT_ON_PARENT)
        wx.Frame.__init__(self, wx.GetApp().TopWindow, wx.ID_ANY,
                          p4R.Application_name + " - Fit Parameters",
                          pos, size, style)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.SetIcon(prog_icon.GetIcon())
        if _platform == "linux" or _platform == "linux2":
            font_update = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        elif _platform == "win32":
            font_update = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        elif _platform == 'darwin':
            font_update = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        pnl = wx.Panel(self)
        label_0 = (u"Input parameters are off limits\n" +
                   u"Please choose your action:")
        label_1 = "Modify input ?"
        label_2 = "Modify limits ?"
        label_3 = "Obi-Wan Kenobi"

        label_txt_a = wx.StaticText(pnl, -1, label=label_0,
                                    size=(250, 44))
        self.rb1 = wx.RadioButton(pnl, label=label_1, style=wx.RB_GROUP)
        self.rb2 = wx.RadioButton(pnl, label=label_2)
        self.rb3 = wx.RadioButton(pnl, label=label_3)

        self.rb1.Bind(wx.EVT_RADIOBUTTON, self.on_set_val)
        self.rb2.Bind(wx.EVT_RADIOBUTTON, self.on_set_val)
        self.rb3.Bind(wx.EVT_RADIOBUTTON, self.on_set_val)
        self.state = [True, False, False]

        self.ok_1_Id = wx.NewId()
        self.cancel_1_Id = wx.NewId()
        self.ok_1 = wx.Button(pnl, id=self.ok_1_Id, label="Ok")
        self.ok_1.SetFont(font_update)
        self.ok_1.Bind(wx.EVT_BUTTON, self.on_ok)

        self.cancel_1 = wx.Button(pnl, id=self.cancel_1_Id, label="Cancel")
        self.cancel_1.SetFont(font_update)
        self.cancel_1.Bind(wx.EVT_BUTTON, self.on_close)

        label_txt_b = wx.StaticText(pnl, -1, label="",
                                    size=(200, 22))

        mastersizer = wx.BoxSizer(wx.VERTICAL)
        horizsizer = wx.BoxSizer(wx.HORIZONTAL)
        mastersizer.Add(label_txt_a, 0, wx.ALL, 5)
        mastersizer.Add(self.rb1, 0, wx.ALL, 5)
        mastersizer.Add(self.rb2, 0, wx.ALL, 5)
        mastersizer.Add(self.rb3, 0, wx.ALL, 5)
        mastersizer.Add(label_txt_b, 0, wx.ALL, 5)
        horizsizer.Add(self.ok_1, 0, wx.ALL, 5)
        horizsizer.Add(self.cancel_1, 0, wx.ALL, 5)
        mastersizer.Add(horizsizer, 0, wx.ALL, 5)

        pub.subscribe(self.on_open_window, pubsub_Open_GSA_Window)
#        self.Bind(wx.EVT_SIZE, self.OnSize)
        pnl.SetSizer(mastersizer)
        pnl.Layout()
        pnl.Fit()

    def on_open_window(self):
        self.CenterOnParent()
        self.GetParent().Disable()

    def on_set_val(self, event):
        self.state = []
        state1 = self.rb1.GetValue()
        state2 = self.rb2.GetValue()
        state3 = self.rb3.GetValue()
        self.state = [state1, state2, state3]

    def on_ok(self, event):
        b = Fitting4Radmax()
        b.on_modify_deformation_limits(self.state)
        self.GetParent().Enable()
        pub.sendMessage(pubsub_Hide_Show_GSA, test=1)

    def on_close(self, event):
        self.GetParent().Enable()
        pub.sendMessage(pubsub_Hide_Show_GSA, test=1)

#    def OnSize(self, event):
#        sizet = event.GetSize()
#        print ("%s, %s" % (sizet.width, sizet.height))
#        event.Skip()
