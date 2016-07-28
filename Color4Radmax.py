#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

import wx
from wx.lib.pubsub import pub
import wx.lib.agw.genericmessagedialog as GMD

import Parameters4Radmax as p4R
from Parameters4Radmax import P4Rm

from Icon4Radmax import prog_icon
from Read4Radmax import SaveFile4Diff

import os
from sys import platform as _platform
import wx.lib.colourselect as csel

if 'phoenix' in wx.PlatformInfo:
    from wx.adv import OwnerDrawnComboBox
    cbFlags = wx.adv
else:
    from wx.combo import OwnerDrawnComboBox
    cbFlags = wx.combo

"""Pubsub message"""
pubsub_Hide_Show_Color = "HideShowColor"
pubsub_Open_Color_Window = "OpenColorWindow"
pubsub_Graph_change_color_style = "RGraphChangeColorStyle"

pubsub_Re_Read_field_paramters_panel = "ReReadParametersPanel"

penStyles = [
    "Solid",
    "Dash",
    "Dot",
    "Dot Dash",
    "Transparent",
    ]


# ------------------------------------------------------------------------------
class ColorWindow(wx.Frame):
    def __init__(self, parent):
        pos = wx.DefaultPosition
        size = (365, 304)
        style = (wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX |
                 wx.CLIP_CHILDREN | wx.FRAME_FLOAT_ON_PARENT)
        wx.Frame.__init__(self, wx.GetApp().TopWindow, wx.ID_ANY,
                          p4R.Application_name + " - Graph Style",
                          pos, size, style)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.SetIcon(prog_icon.GetIcon())
        if _platform == "linux" or _platform == "linux2":
            font_update = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        elif _platform == "win32":
            font_update = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        elif _platform == 'darwin':
            font_update = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.lines_names = ['solid', 'dashed', 'dashdot', 'dotted', 'None']
        pnl = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.buttonRefs = []

        colorlinesizer = wx.FlexGridSizer(cols=5)

        vStatictextsize = 16
        size_text = (50, vStatictextsize)
        graph = wx.StaticText(pnl, -1, "Graph", size=size_text)
        l1 = wx.StaticLine(pnl, size=(3, 20), style=wx.LI_VERTICAL)
        l2 = wx.StaticLine(pnl, size=(3, 20), style=wx.LI_VERTICAL)
        t1 = wx.StaticText(pnl, -1, "Colors")
        t2 = wx.StaticText(pnl, -1, "Style")
        graph.SetFont(font_update)
        l1.SetFont(font_update)
        l2.SetFont(font_update)
        t1.SetFont(font_update)
        t2.SetFont(font_update)
        colorlinesizer.AddMany([
            (graph, 0, wx.ALL | wx.ALIGN_CENTER, 3),
            (l1, 0, wx.ALL | wx.ALL, 3),
            (t1, 0, wx.ALL | wx.ALIGN_CENTER, 3),
            (l2, 0, wx.ALL | wx.ALL, 3),
            (t2, 0, wx.ALL | wx.ALIGN_CENTER, 3),
            ])

        self.buttonRefs = []  # for saving references to buttons
        self.list_ = ['Strain', 'DW', 'XRD Data', 'Fit', 'Fit Live']
        a = P4Rm()
        size_button = (60, 20)
        for i in range(len(self.list_)):
            key_c = p4R.s_radmax_7[i]
            key_l = p4R.s_radmax_7[i + len(self.list_)]
            color = a.DefaultDict[key_c]
            line = a.DefaultDict[key_l]
            name = self.list_[i]
            graph = wx.StaticText(pnl, -1, name, size=size_text)
            b1 = csel.ColourSelect(pnl, -1, "", color, size=size_button)
            l1 = wx.StaticLine(pnl, size=(3, 20), style=wx.LI_VERTICAL)
            l2 = wx.StaticLine(pnl, size=(3, 20), style=wx.LI_VERTICAL)
            pscb = PenStyleComboBox(pnl, choices=penStyles,
                                    style=wx.CB_READONLY, pos=(20, 40),
                                    size=(120, -1), name=name)
            pscb.SetSelection(self.lines_names.index(line))

            self.buttonRefs.append((name, b1, pscb))
            colorlinesizer.AddMany([
                (graph, 0, wx.ALL | wx.ALIGN_CENTER, 3),
                (l1, 0, wx.ALL | wx.ALL, 3),
                (b1, 0, wx.ALL, 3),
                (l2, 0, wx.ALL | wx.ALL, 3),
                (pscb, 0, wx.ALL, 3),
                ])

        self.b = wx.Button(pnl, -1, "Apply")
        self.b.SetFont(font_update)
        self.Bind(wx.EVT_BUTTON, self.on_apply_color, id=self.b.GetId())

        self.default_1_Id = wx.NewId()
        self.default_1 = wx.Button(pnl, id=self.default_1_Id,
                                   label="Set as Default")
        self.default_1.SetFont(font_update)
        self.default_1.Bind(wx.EVT_BUTTON, self.on_save_data)

        buttonSizer = wx.FlexGridSizer(cols=2)
        buttonSizer.Add(self.b, 0, wx.ALL, 3)
        buttonSizer.Add(self.default_1, 0, wx.ALL, 3)

        mainSizer.Add(colorlinesizer, 0, wx.ALL, 3)
        mainSizer.Add(buttonSizer, 0, wx.ALL, 3)

        pub.subscribe(self.on_open_window, pubsub_Open_Color_Window)
#        self.Bind(wx.EVT_SIZE, self.OnSize)
        pnl.SetSizer(mainSizer)
        pnl.Layout()
        pnl.Fit()

    def on_open_window(self):
        self.CenterOnParent()
        self.GetParent().Disable()

    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

    def on_apply_color(self, event):
        res_c = []
        res_l = []
        for name, color, line in self.buttonRefs:
            c1 = color.GetValue()
            l1 = line.GetValue()
            tmp = self.lines_names[penStyles.index(l1)]
            try:
                res_c.append(self.rgb_to_hex(c1.Get()))
                res_l.append(tmp)
            except (AttributeError):
                res_c.append(c1)
                res_l.append(tmp)
        for i in range(len(self.list_)):
            key_c = p4R.s_radmax_7[i]
            key_l = p4R.s_radmax_7[i + len(self.list_)]
            P4Rm.DefaultDict[key_c] = res_c[i]
            P4Rm.DefaultDict[key_l] = res_l[i]
        pub.sendMessage(pubsub_Graph_change_color_style)
        pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)
#        pub.sendMessage(pubsub_redraw_Graph_change_color)

    def on_save_data(self, event):
        _msg = "Save data as default ?\n" + \
               "This change will be applied for all fit !!\n\n"
        dlg = GMD.GenericMessageDialog(None, _msg,
                                       "Attention", agwStyle=wx.OK |
                                       wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.on_apply_color(event)
            b = SaveFile4Diff()
            name = p4R.filename + '.ini'
            b.on_update_config_file_parameters(os.path.join(p4R.current_dir,
                                                            name))
            event.Skip()

    def on_close(self, event):
        self.GetParent().Enable()
        pub.sendMessage(pubsub_Hide_Show_Color, test=1)

    def OnSize(self, event):
        sizet = event.GetSize()
        print ("%s, %s" % (sizet.width, sizet.height))
        event.Skip()


# -----------------------------------------------------------------------------
class PenStyleComboBox(OwnerDrawnComboBox):

    # Overridden from OwnerDrawnComboBox, called to draw each
    # item in the list
    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            # painting the control, but there is no valid item selected yet
            return

        r = wx.Rect(*rect)  # make a copy
        r.Deflate(3, 5)

        penStyle = wx.SOLID
        if item == 1:
            penStyle = wx.LONG_DASH
        elif item == 2:
            penStyle = wx.DOT
        elif item == 3:
            penStyle = wx.DOT_DASH
        elif item == 4:
            penStyle = wx.TRANSPARENT

        pen = wx.Pen(dc.GetTextForeground(), 3, penStyle)
        dc.SetPen(pen)

        if flags & wx.combo.ODCB_PAINTING_CONTROL:
            # for painting the control itself
            dc.DrawLine(r.x+5, r.y+r.height/2, r.x+r.width - 5, r.y+r.height/2)

        else:
            # for painting the items in the popup
            dc.DrawText(self.GetString(item),
                        r.x + 3,
                        (r.y + 0) + ((r.height/2) - dc.GetCharHeight())/2)
            dc.DrawLine(r.x+5, r.y+((r.height/4)*3)+1, r.x+r.width - 5,
                        r.y+((r.height/4)*3)+1)

    # Overridden from OwnerDrawnComboBox, called for drawing the
    # background area of each item.
    def OnDrawBackground(self, dc, rect, item, flags):
        # If the item is selected, or its item # iseven, or we are painting the
        # combo control itself, then use the default rendering.
        if (item & 1 == 0 or flags & (wx.combo.ODCB_PAINTING_CONTROL |
                                      wx.combo.ODCB_PAINTING_SELECTED)):
            wx.combo.OwnerDrawnComboBox.OnDrawBackground(self, dc, rect,
                                                         item, flags)
            return

        # Otherwise, draw every other background with different colour.
        bgCol = wx.Colour(240, 240, 250)
        dc.SetBrush(wx.Brush(bgCol))
        dc.SetPen(wx.Pen(bgCol))
        dc.DrawRectangleRect(rect)

    # Overridden from OwnerDrawnComboBox, should return the height
    # needed to display an item in the popup, or -1 for default
    def OnMeasureItem(self, item):
        # Simply demonstrate the ability to have variable-height items
        if item & 1:
            return 36
        else:
            return 24

    # Overridden from OwnerDrawnComboBox.  Callback for item width, or
    # -1 for default/undetermined
    def OnMeasureItemWidth(self, item):
        return -1  # default - will be measured from text width
