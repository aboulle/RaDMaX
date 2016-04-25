#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

from Parameters4Radmax import *
from Icon4Radmax import prog_icon
from sys import platform as _platform

"""Pubsub message"""
pubsub_Hide_Show_GSA = "HideShowGSA"
pubsub_ModifyDLimits = "ModifyDeformationLimits"


# ------------------------------------------------------------------------------
class GSAParametersWindow(wx.Frame):
    def __init__(self, parent):
        pos = wx.DefaultPosition
        size = (350, 240)
        style = (wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX |
                 wx.CLIP_CHILDREN | wx.FRAME_FLOAT_ON_PARENT)
        wx.Frame.__init__(self, wx.GetApp().TopWindow, wx.ID_ANY,
                          Application_name + " - GSA Parameters",
                          pos, size, style)
        self.CenterOnParent()
        self.GetParent().Disable()
        self.Bind(wx.EVT_CLOSE, self.onOk)

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
                                    size=(200, 44))
        self.rb1 = wx.RadioButton(pnl, label=label_1, style=wx.RB_GROUP)
        self.rb2 = wx.RadioButton(pnl, label=label_2)
        self.rb3 = wx.RadioButton(pnl, label=label_3)

        self.rb1.Bind(wx.EVT_RADIOBUTTON, self.SetVal)
        self.rb2.Bind(wx.EVT_RADIOBUTTON, self.SetVal)
        self.rb3.Bind(wx.EVT_RADIOBUTTON, self.SetVal)
        self.state = [True, False, False]

        self.default_1_Id = wx.NewId()
        self.default_1 = wx.Button(pnl, id=self.default_1_Id,
                                   label="Ok")
        self.default_1.SetFont(font_update)
        self.default_1.Bind(wx.EVT_BUTTON, self.onOk)

        label_txt_b = wx.StaticText(pnl, -1, label="",
                                    size=(200, 22))

        mastersizer = wx.BoxSizer(wx.VERTICAL)
        mastersizer.Add(label_txt_a, 0, wx.ALL, 5)
        mastersizer.Add(self.rb1, 0, wx.ALL, 5)
        mastersizer.Add(self.rb2, 0, wx.ALL, 5)
        mastersizer.Add(self.rb3, 0, wx.ALL, 5)
        mastersizer.Add(label_txt_b, 0, wx.ALL, 5)
        mastersizer.Add(self.default_1, 0, wx.ALL, 5)

#        self.Bind(wx.EVT_SIZE, self.OnSize)
        pnl.SetSizer(mastersizer)
        pnl.Layout()
        pnl.Fit()

    def SetVal(self, event):
        self.state = []
        state1 = self.rb1.GetValue()
        state2 = self.rb2.GetValue()
        state3 = self.rb3.GetValue()
        self.state = [state1, state2, state3]

    def onOk(self, event):
        dlg = GMD.GenericMessageDialog(None, "Proceed to changes ?",
                                       "Attention", agwStyle=wx.OK |
                                       wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            pub.sendMessage(pubsub_ModifyDLimits, state=self.state)
        self.GetParent().Enable()
        pub.sendMessage(pubsub_Hide_Show_GSA, test=1)

#    def OnSize(self, event):
#        sizet = event.GetSize()
#        print ("%s, %s" % (sizet.width, sizet.height))
#        event.Skip()
