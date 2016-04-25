#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

from Parameters4Radmax import *
from Icon4Radmax import prog_icon
from Read4Radmax import SaveFile4Diff
from sys import platform as _platform

"""Pubsub message"""
pubsub_Read_field = "ReadField"
pubsub_Save_Param_and_quit = "SaveParamAndQuit"
pubsub_Hide_Show_Option = "HideShowOption"


# -----------------------------------------------------------------------------
class ParametersWindow(wx.Frame):
    def __init__(self, parent):
        pos = wx.DefaultPosition
        size = (525, 488)
        style = (wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX |
                 wx.CLIP_CHILDREN | wx.FRAME_FLOAT_ON_PARENT)
        wx.Frame.__init__(self, wx.GetApp().TopWindow, wx.ID_ANY,
                          Application_name + " - Parameters", pos, size, style)
        self.CenterOnParent()
        self.GetParent().Disable()
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.SetIcon(prog_icon.GetIcon())

        self.aui_mgr = aui.AuiManager()
        self.aui_mgr.SetManagedWindow(self)

        self.notebook = AUINotebookParameters(self)

        self.aui_mgr.AddPane(self.notebook, aui.AuiPaneInfo().Center().
                             Name("notebook_content").PaneBorder(False).
                             Position(0).MaximizeButton(False).CenterPane().
                             MinSize((525, 100)))

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

        self.aui_mgr.AddPane(FitParametersPanel(self),
                             aui.AuiPaneInfo().Name("Fit Params").
                             CenterPane().PaneBorder(False).Bottom().
                             MaximizeButton(False).MinSize((525, 200)))

        self.aui_mgr.Update()
#        self.Bind(wx.EVT_SIZE, self.OnSize)
        pub.subscribe(self.onCloseAfterSaving, pubsub_Save_Param_and_quit)
        self.Layout()

    def onClose(self, event):
        dlg = GMD.GenericMessageDialog(None, "Save changes ?",
                                       "Attention", agwStyle=wx.OK |
                                       wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            pub.sendMessage(pubsub_Read_field)
            a = P4Radmax()
            if False not in a.Paramwindowtest:
                P4Radmax.Option_window_status = False
        else:
            P4Radmax.Option_window_status = False
        self.GetParent().Enable()
        pub.sendMessage(pubsub_Hide_Show_Option, test=1)

    def onCloseAfterSaving(self):
        self.GetParent().Enable()
        pub.sendMessage(pubsub_Hide_Show_Option, test=1)

#    def OnSize(self, event):
#        sizet = event.GetSize()
#        print ("%s, %s" % (sizet.width, sizet.height))
#        event.Skip()


# ------------------------------------------------------------------------------
class AUINotebookParameters(aui.AuiNotebook):
    """ AUI Notebook class """
    def __init__(self, parent):
        aui.AuiNotebook.__init__(self, parent=parent)
        self.parent = parent

        self.default_style = (aui.AUI_NB_DEFAULT_STYLE &
                              aui.AUI_NB_CLOSE_ON_ALL_TABS)
        self.SetAGWWindowStyleFlag(self.default_style)

        """create the page windows as children of the notebook"""
        page1 = BsplinePanel(self)
        page2 = PseudoVoigtPanel(self)

        """add the pages to the notebook with the label to show on the tab"""
        self.AddPage(page1, "Bspline")
        self.AddPage(page2, "PseudoVoigt")

        self.SetCloseButton(page1, False)
        self.SetCloseButton(page2, False)


# -----------------------------------------------------------------------------
class BsplinePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        if _platform == "linux" or _platform == "linux2":
            size_StaticBox = (950, 140)
            font_Statictext = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 16
        elif _platform == "win32":
            size_StaticBox = (960, 140)
            font_Statictext = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(9, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 16
        elif _platform == 'darwin':
            size_StaticBox = (980, 140)
            font_Statictext = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 18

        size_text = (95, 22)
        flagSizer = wx.ALL | wx.ALIGN_CENTER

        Fit_box = wx.StaticBox(self, -1, " Bounds ",
                               size=size_StaticBox)
        Fit_box.SetFont(font)
        Fit_box_sizer = wx.StaticBoxSizer(Fit_box, wx.VERTICAL)
        in_Fit_box_sizer = wx.GridBagSizer(hgap=10, vgap=0)

        Strain_txt = wx.StaticText(self, -1, label=u'Strain',
                                   size=(45, vStatictextsize))
        Strain_txt.SetFont(font_update)
        Dwp_txt = wx.StaticText(self, -1, label=u'Dwp',
                                size=(45, vStatictextsize))
        Dwp_txt.SetFont(font_update)

        Min_txt = wx.StaticText(self, -1, label=u'Min',
                                size=(45, vStatictextsize))
        Min_txt.SetFont(font_Statictext)
        Max_txt = wx.StaticText(self, -1, label=u'Max',
                                size=(45, vStatictextsize))
        Max_txt.SetFont(font_Statictext)

        self.Min_strain = wx.TextCtrl(self, size=size_text,
                                      validator=TextValidator(DIGIT_ONLY))
        self.Min_strain.SetFont(font_TextCtrl)

        self.Max_strain = wx.TextCtrl(self, size=size_text,
                                      validator=TextValidator(DIGIT_ONLY))
        self.Max_strain.SetFont(font_TextCtrl)

        self.Min_dw = wx.TextCtrl(self, size=size_text,
                                  validator=TextValidator(DIGIT_ONLY))
        self.Min_dw.SetFont(font_TextCtrl)

        self.Max_dw = wx.TextCtrl(self, size=size_text,
                                  validator=TextValidator(DIGIT_ONLY))
        self.Max_dw.SetFont(font_TextCtrl)

        in_Fit_box_sizer.Add(Strain_txt, pos=(0, 0), flag=flagSizer)
        in_Fit_box_sizer.Add(Dwp_txt, pos=(0, 2), flag=flagSizer)
        in_Fit_box_sizer.Add(Min_txt, pos=(1, 1), flag=flagSizer)
        in_Fit_box_sizer.Add(Max_txt, pos=(2, 1), flag=flagSizer)

        in_Fit_box_sizer.Add(self.Min_strain, pos=(1, 0), flag=flagSizer)
        in_Fit_box_sizer.Add(self.Max_strain, pos=(2, 0), flag=flagSizer)

        in_Fit_box_sizer.Add(self.Min_dw, pos=(1, 2), flag=flagSizer)
        in_Fit_box_sizer.Add(self.Max_dw, pos=(2, 2), flag=flagSizer)

        Fit_box_sizer.Add(in_Fit_box_sizer, 0, wx.ALL, 5)

        mastersizer = wx.BoxSizer(wx.VERTICAL)
        mastersizer.Add(Fit_box_sizer, 0, wx.ALL, 5)

        pub.subscribe(self.onReadField, pubsub_Read_field)

        self.Textcontrol = [self.Min_strain, self.Max_strain, self.Min_dw,
                            self.Max_dw]
        self.SetSizer(mastersizer)
        self.Layout()
        self.Fit()
        self.onFillTextCtrl()

    def onFillTextCtrl(self):
        a = P4Radmax()
        i = 0
        for k in DefaultParam4Radmax[17:21]:
            self.Textcontrol[i].AppendText(str(a.DefaultDict[k]))
            i += 1

    def onReadField(self):
        success = self.IsDataFloat()
        if success:
            P4Radmax.Paramwindowtest['BsplinePanel'] = True

    def Is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def IsDataFloat(self):
        IsFloat = []
        dataFloat = True
        for i in range(len(self.Textcontrol)):
            IsFloat.append(self.Is_number(self.Textcontrol[i].GetValue()))
        if False in IsFloat:
            dataFloat = False
            StringPosition = [i for i, x in enumerate(IsFloat) if x is False]
            for ii in StringPosition:
                self.Textcontrol[ii].SetBackgroundColour('green')
            self.Refresh()
            _msg = "Please, fill correctly the fields before to continue"
            dlg = GMD.GenericMessageDialog(None, _msg, "Attention",
                                           agwStyle=wx.OK |
                                           wx.ICON_INFORMATION)
            dlg.ShowModal()
            for ii in StringPosition:
                self.Textcontrol[ii].SetBackgroundColour('white')
            self.Refresh()
        else:
            i = 0
            for k in DefaultParam4Radmax[17:21]:
                val = self.Textcontrol[i].GetValue()
                P4Radmax.DefaultDict[k] = float(val)
                i += 1
        return dataFloat


# -----------------------------------------------------------------------------
class PseudoVoigtPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        if _platform == "linux" or _platform == "linux2":
            size_StaticBox = (950, 140)
            font_Statictext = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 16
            hStatictextsize = 60
        elif _platform == "win32":
            size_StaticBox = (960, 140)
            font_Statictext = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(9, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 16
            hStatictextsize = 60
        elif _platform == 'darwin':
            size_StaticBox = (980, 140)
            font_Statictext = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 18
            hStatictextsize = 60

        size_text = (95, 22)
        flagSizer = wx.ALL | wx.ALIGN_CENTER

        Fit_box = wx.StaticBox(self, -1, " Bounds ",
                               size=size_StaticBox)
        Fit_box.SetFont(font)
        Fit_box_sizer = wx.StaticBoxSizer(Fit_box, wx.VERTICAL)
        in_Fit_box_sizer = wx.GridBagSizer(hgap=10, vgap=0)

        Strain_txt = wx.StaticText(self, -1, label=u'Strain',
                                   size=(45, vStatictextsize))
        Strain_txt.SetFont(font_update)

        Dwp_txt = wx.StaticText(self, -1, label=u'Dwp',
                                size=(45, vStatictextsize))
        Dwp_txt.SetFont(font_update)

        Eta1_txt = wx.StaticText(self, -1, label=u'Eta min',
                                 size=(hStatictextsize, vStatictextsize))
        Eta1_txt.SetFont(font_Statictext)
        Eta2_txt = wx.StaticText(self, -1, label=u'Eta max',
                                 size=(hStatictextsize, vStatictextsize))
        Eta2_txt.SetFont(font_Statictext)
        fwhm1_txt = wx.StaticText(self, -1, label=u'height min',
                                  size=(hStatictextsize, vStatictextsize))
        fwhm1_txt.SetFont(font_Statictext)
        fwhm2_txt = wx.StaticText(self, -1, label=u'height max',
                                  size=(hStatictextsize, vStatictextsize))
        fwhm2_txt.SetFont(font_Statictext)
        pos1_txt = wx.StaticText(self, -1, label=u'bkg min',
                                 size=(hStatictextsize, vStatictextsize))
        pos1_txt.SetFont(font_Statictext)
        pos2_txt = wx.StaticText(self, -1, label=u'bkg max',
                                 size=(hStatictextsize, vStatictextsize))
        pos2_txt.SetFont(font_Statictext)

        ''' sp part '''
        self.Eta1_strain = wx.TextCtrl(self, size=size_text,
                                       validator=TextValidator(DIGIT_ONLY))
        self.Eta1_strain.SetFont(font_TextCtrl)

        self.Eta2_strain = wx.TextCtrl(self, size=size_text,
                                       validator=TextValidator(DIGIT_ONLY))
        self.Eta2_strain.SetFont(font_TextCtrl)

        self.fwhm1_strain = wx.TextCtrl(self, size=size_text,
                                        validator=TextValidator(DIGIT_ONLY))
        self.fwhm1_strain.SetFont(font_TextCtrl)

        self.fwhm2_strain = wx.TextCtrl(self, size=size_text,
                                        validator=TextValidator(DIGIT_ONLY))
        self.fwhm2_strain.SetFont(font_TextCtrl)

        self.pos1_strain = wx.TextCtrl(self, size=size_text,
                                       validator=TextValidator(DIGIT_ONLY))
        self.pos1_strain.SetFont(font_TextCtrl)

        self.pos2_strain = wx.TextCtrl(self, size=size_text,
                                       validator=TextValidator(DIGIT_ONLY))
        self.pos2_strain.SetFont(font_TextCtrl)

        ''' dwp part '''
        self.Eta1_dw = wx.TextCtrl(self, size=size_text,
                                   validator=TextValidator(DIGIT_ONLY))
        self.Eta1_dw.SetFont(font_TextCtrl)

        self.Eta2_dw = wx.TextCtrl(self, size=size_text,
                                   validator=TextValidator(DIGIT_ONLY))
        self.Eta2_dw.SetFont(font_TextCtrl)

        self.fwhm1_dw = wx.TextCtrl(self, size=size_text,
                                    validator=TextValidator(DIGIT_ONLY))
        self.fwhm1_dw.SetFont(font_TextCtrl)

        self.fwhm2_dw = wx.TextCtrl(self, size=size_text,
                                    validator=TextValidator(DIGIT_ONLY))
        self.fwhm2_dw.SetFont(font_TextCtrl)

        self.pos1_dw = wx.TextCtrl(self, size=size_text,
                                   validator=TextValidator(DIGIT_ONLY))
        self.pos1_dw.SetFont(font_TextCtrl)

        self.pos2_dw = wx.TextCtrl(self, size=size_text,
                                   validator=TextValidator(DIGIT_ONLY))
        self.pos2_dw.SetFont(font_TextCtrl)

        in_Fit_box_sizer.Add(Strain_txt, pos=(0, 0), flag=flagSizer)
        in_Fit_box_sizer.Add(Dwp_txt, pos=(0, 2), flag=flagSizer)
        in_Fit_box_sizer.Add(Eta1_txt, pos=(1, 1), flag=flagSizer)
        in_Fit_box_sizer.Add(Eta2_txt, pos=(2, 1), flag=flagSizer)
        in_Fit_box_sizer.Add(fwhm1_txt, pos=(3, 1), flag=flagSizer)
        in_Fit_box_sizer.Add(fwhm2_txt, pos=(4, 1), flag=flagSizer)
        in_Fit_box_sizer.Add(pos1_txt, pos=(5, 1), flag=flagSizer)
        in_Fit_box_sizer.Add(pos2_txt, pos=(6, 1), flag=flagSizer)

        in_Fit_box_sizer.Add(self.Eta1_strain, pos=(1, 0), flag=flagSizer)
        in_Fit_box_sizer.Add(self.Eta2_strain, pos=(2, 0), flag=flagSizer)
        in_Fit_box_sizer.Add(self.fwhm1_strain, pos=(3, 0), flag=flagSizer)
        in_Fit_box_sizer.Add(self.fwhm2_strain, pos=(4, 0), flag=flagSizer)
        in_Fit_box_sizer.Add(self.pos1_strain, pos=(5, 0), flag=flagSizer)
        in_Fit_box_sizer.Add(self.pos2_strain, pos=(6, 0), flag=flagSizer)

        in_Fit_box_sizer.Add(self.Eta1_dw, pos=(1, 2), flag=flagSizer)
        in_Fit_box_sizer.Add(self.Eta2_dw, pos=(2, 2), flag=flagSizer)
        in_Fit_box_sizer.Add(self.fwhm1_dw, pos=(3, 2), flag=flagSizer)
        in_Fit_box_sizer.Add(self.fwhm2_dw, pos=(4, 2), flag=flagSizer)
        in_Fit_box_sizer.Add(self.pos1_dw, pos=(5, 2), flag=flagSizer)
        in_Fit_box_sizer.Add(self.pos2_dw, pos=(6, 2), flag=flagSizer)

        Fit_box_sizer.Add(in_Fit_box_sizer, 0, wx.ALL, 5)

        mastersizer = wx.BoxSizer(wx.VERTICAL)
        mastersizer.Add(Fit_box_sizer, 0, wx.ALL, 5)

        pub.subscribe(self.onReadField, pubsub_Read_field)

        self.Textcontrol = [self.Eta1_strain, self.Eta2_strain, self.Eta1_dw,
                            self.Eta2_dw, self.fwhm1_strain, self.fwhm2_strain,
                            self.fwhm1_dw, self.fwhm2_dw, self.pos1_strain,
                            self.pos2_strain, self.pos1_dw, self.pos2_dw]

        self.SetSizer(mastersizer)
        self.Layout()
        self.Fit()
        self.onFillTextCtrl()

    def onFillTextCtrl(self):
        a = P4Radmax()
        i = 0
        for k in DefaultParam4Radmax[5:17]:
            self.Textcontrol[i].AppendText(str(a.DefaultDict[k]))
            i += 1

    def onReadField(self):
        success = self.IsDataFloat()
        if success:
            P4Radmax.Paramwindowtest['PseudoVoigtPanel'] = True

    def Is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def IsDataFloat(self):
        IsFloat = []
        dataFloat = True
        for i in range(len(self.Textcontrol)):
            IsFloat.append(self.Is_number(self.Textcontrol[i].GetValue()))
        if False in IsFloat:
            dataFloat = False
            StringPosition = [i for i, x in enumerate(IsFloat) if x is False]
            for ii in StringPosition:
                self.Textcontrol[ii].SetBackgroundColour('green')
            self.Refresh()
            _msg = "Please, fill correctly the fields before to continue"
            dlg = GMD.GenericMessageDialog(None, _msg, "Attention",
                                           agwStyle=wx.OK |
                                           wx.ICON_INFORMATION)
            dlg.ShowModal()
            for ii in StringPosition:
                self.Textcontrol[ii].SetBackgroundColour('white')
            self.Refresh()
        else:
            i = 0
            for k in DefaultParam4Radmax[5:17]:
                val = self.Textcontrol[i].GetValue()
                P4Radmax.DefaultDict[k] = float(val)
                i += 1
        return dataFloat


# -----------------------------------------------------------------------------
class FitParametersPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        if _platform == "linux" or _platform == "linux2":
            size_StaticBox = (950, 140)
            font_Statictext = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 16
        elif _platform == "win32":
            size_StaticBox = (960, 140)
            font_Statictext = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(9, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 16
        elif _platform == 'darwin':
            size_StaticBox = (980, 140)
            font_Statictext = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 18

        size_text = (95, 22)
        flagSizer = wx.ALL | wx.ALIGN_CENTER_VERTICAL

        """Advanced GSA options part"""
        _msg = " Advanced GSA options (expert users only) "
        AGSA_options_box = wx.StaticBox(self, -1, _msg, size=size_StaticBox)
        AGSA_options_box.SetFont(font)
        AGSA_options_box_sizer = wx.StaticBoxSizer(AGSA_options_box,
                                                   wx.VERTICAL)
        in_AGSA_options_box_sizer = wx.GridBagSizer(hgap=10, vgap=0)

        qa_txt = wx.StaticText(self, -1, label=u'qa',
                               size=(20, vStatictextsize))
        self.qa = wx.TextCtrl(self, size=size_text,
                              validator=TextValidator(DIGIT_ONLY))
        self.qa.SetFont(font_TextCtrl)

        qv_txt = wx.StaticText(self, -1, label=u'qv',
                               size=(20, vStatictextsize))
        qv_txt.SetFont(font_Statictext)
        self.qv = wx.TextCtrl(self, size=size_text,
                              validator=TextValidator(DIGIT_ONLY))
        self.qv.SetFont(font_TextCtrl)

        qt_txt = wx.StaticText(self, -1, label=u'qt',
                               size=(20, vStatictextsize))
        qt_txt.SetFont(font_Statictext)
        self.qt = wx.TextCtrl(self, size=size_text,
                              validator=TextValidator(DIGIT_ONLY))
        self.qt.SetFont(font_TextCtrl)

        in_AGSA_options_box_sizer.Add(qa_txt, pos=(0, 0), flag=flagSizer)
        in_AGSA_options_box_sizer.Add(self.qa, pos=(0, 1), flag=flagSizer)
        in_AGSA_options_box_sizer.Add(qv_txt, pos=(0, 2), flag=flagSizer)
        in_AGSA_options_box_sizer.Add(self.qv, pos=(0, 3), flag=flagSizer)
        in_AGSA_options_box_sizer.Add(qt_txt, pos=(0, 4), flag=flagSizer)
        in_AGSA_options_box_sizer.Add(self.qt, pos=(0, 5), flag=flagSizer)

        AGSA_options_box_sizer.Add(in_AGSA_options_box_sizer, 0, wx.ALL, 5)

        Leastsq_box = wx.StaticBox(self, -1, " Leastsq parameters ",
                                   size=size_StaticBox)
        Leastsq_box.SetFont(font)
        Leastsq_box_sizer = wx.StaticBoxSizer(Leastsq_box, wx.VERTICAL)
        in_Leastsq_box_sizer = wx.GridBagSizer(hgap=10, vgap=0)

        xtol_txt = wx.StaticText(self, -1, label=u'xtol',
                                 size=(45, vStatictextsize))
        xtol_txt.SetFont(font_Statictext)
        self.xtol = wx.TextCtrl(self, size=size_text,
                                validator=TextValidator(DIGIT_ONLY))
        self.xtol.SetFont(font_TextCtrl)

        ftol_txt = wx.StaticText(self, -1, label=u'ftol',
                                 size=(45, vStatictextsize))
        ftol_txt.SetFont(font_Statictext)
        self.ftol = wx.TextCtrl(self, size=size_text,
                                validator=TextValidator(DIGIT_ONLY))
        self.ftol.SetFont(font_TextCtrl)

        maxfev_txt = wx.StaticText(self, -1, label=u'maxfev',
                                   size=(45, vStatictextsize))
        maxfev_txt.SetFont(font_Statictext)
        self.maxfev = wx.TextCtrl(self, size=size_text,
                                  validator=TextValidator(DIGIT_ONLY))
        self.maxfev.SetFont(font_TextCtrl)

        in_Leastsq_box_sizer.Add(xtol_txt, pos=(0, 0), flag=flagSizer)
        in_Leastsq_box_sizer.Add(self.xtol, pos=(0, 1), flag=flagSizer)
        in_Leastsq_box_sizer.Add(ftol_txt, pos=(0, 2), flag=flagSizer)
        in_Leastsq_box_sizer.Add(self.ftol, pos=(0, 3), flag=flagSizer)
        in_Leastsq_box_sizer.Add(maxfev_txt, pos=(0, 4), flag=flagSizer)
        in_Leastsq_box_sizer.Add(self.maxfev, pos=(0, 5), flag=flagSizer)

        Leastsq_box_sizer.Add(in_Leastsq_box_sizer, 0, wx.ALL, 5)

        self.default_1_Id = wx.NewId()
        self.default_1 = wx.Button(self, id=self.default_1_Id,
                                   label="Set as Default")
        self.default_1.SetFont(font_update)
        self.default_1.Bind(wx.EVT_BUTTON, self.onSaveData)

        mastersizer = wx.BoxSizer(wx.VERTICAL)
        mastersizer.Add(Leastsq_box_sizer, 0, wx.ALL, 5)
        mastersizer.Add(AGSA_options_box_sizer, 0, wx.ALL, 5)
        mastersizer.Add(self.default_1, 0, wx.ALL, 5)

        pub.subscribe(self.onReadField, pubsub_Read_field)

        self.TextcontrolGSA = [self.qa, self.qv, self.qt]
        self.TextcontrolLeastsq = [self.xtol, self.ftol, self.maxfev]
        self.all_textControl = self.TextcontrolGSA + self.TextcontrolLeastsq

        self.SetSizer(mastersizer)
        self.Layout()
        self.Fit()
        self.onFillTextCtrl()

    def onFillTextCtrl(self):
        a = P4Radmax()
        i = 0
        for k in DefaultParam4Radmax[21:24]:
            self.TextcontrolGSA[i].AppendText(str(a.DefaultDict[k]))
            i += 1
        i = 0
        for k in DefaultParam4Radmax[24:]:
            self.TextcontrolLeastsq[i].AppendText(str(a.DefaultDict[k]))
            i += 1

    def onSaveData(self, event):
        _msg = "Save data as default ?\n" + \
               "This change will be applied for all fit !!\n\n"
        dlg = GMD.GenericMessageDialog(None, _msg,
                                       "Attention", agwStyle=wx.OK |
                                       wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            pub.sendMessage(pubsub_Read_field)
            success = self.IsDataFloat()
            if success:
                a = P4Radmax()
                P4Radmax.Paramwindowtest['FitParametersPanel'] = True
                if False not in a.Paramwindowtest:
                    a = SaveFile4Diff(self)
                    a.update_Config_File_Parameters(os.path.join(current_dir,
                                                    filename + '.ini'))
                    P4Radmax.Paramwindowtest['FitParametersPanel'] = True
                    pub.sendMessage(pubsub_Save_Param_and_quit)

    def onReadField(self):
        success = self.IsDataFloat()
        if success:
            P4Radmax.Paramwindowtest['FitParametersPanel'] = True

    def Is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def IsDataFloat(self):
        IsFloat = []
        dataFloat = True
        for i in range(len(self.all_textControl)):
            IsFloat.append(self.Is_number(self.all_textControl[i].GetValue()))
        if False in IsFloat:
            dataFloat = False
            StringPosition = [i for i, x in enumerate(IsFloat) if x is False]
            for ii in StringPosition:
                self.all_textControl[ii].SetBackgroundColour('green')
            self.Refresh()
            _msg = "Please, fill correctly the fields before to continue"
            dlg = GMD.GenericMessageDialog(None, _msg, "Attention",
                                           agwStyle=wx.OK |
                                           wx.ICON_INFORMATION)
            dlg.ShowModal()
            for ii in StringPosition:
                self.all_textControl[ii].SetBackgroundColour('white')
            self.Refresh()
        else:
            i = 0
            for k in DefaultParam4Radmax[21:24]:
                val = self.TextcontrolGSA[i].GetValue()
                P4Radmax.DefaultDict[k] = float(val)
                i += 1
            i = 0
            for k in DefaultParam4Radmax[24:]:
                val = self.TextcontrolLeastsq[i].GetValue()
                if k == 'maxfev':
                    P4Radmax.DefaultDict[k] = int(float(val))
                else:
                    P4Radmax.DefaultDict[k] = float(val)
                i += 1
        return dataFloat
