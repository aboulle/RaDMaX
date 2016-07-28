#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

import wx

from wx.lib.pubsub import pub
import wx.lib.agw.genericmessagedialog as GMD
import wx.lib.scrolledpanel as scrolled

from copy import deepcopy

import Parameters4Radmax as p4R
from Parameters4Radmax import P4Rm
from Settings4Radmax import TextValidator

from Image4Radmax import Scheme_SingleCrystal, Scheme_ThickFilm
from Image4Radmax import Scheme_ThickFilmAndSubstrate, Scheme_ThinFilm

from sys import platform as _platform

import logging
logger = logging.getLogger(__name__)

DIGIT_ONLY = 2

"""Pubsub message"""
pubsub_Load_project = "LoadProject"
pubsub_changeColor_field4Save = "ChangeColorField4Save"
pubsub_Read_field4Save = "ReadField4Save"
pubsub_Read_field4Fit = "ReadField4Fit"

pubsub_Re_Read_field_paramters_panel = "ReReadParametersPanel"
pubsub_update_crystal_list = "UpdateCrystalList"

New_project_initial = [1, 1, 1, 0, 0, 2, 5.4135, 5.4135, 5.4135, 90, 90, 90]


# ------------------------------------------------------------------------------
class SampleGeometry(scrolled.ScrolledPanel):
    """
    Initial Parameters main panel
    we built the all page in this module
    """
    def __init__(self, parent, statusbar):
        scrolled.ScrolledPanel.__init__(self, parent)
        self.statusbar = statusbar
        self.parent = parent

        size_value_hkl = (50, 22)
        size_value_lattice = (65, 22)

        if _platform == "linux" or _platform == "linux2":
            size_StaticBox = (500, 140)
            size_StaticBox_scheme = (505, 140)
            size_StaticBox_substrate = (950, 140)
            crystal_combobox = (110, -1)
            symmetry_combobox = (90, -1)
            font_Statictext = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_combobox = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 16
        elif _platform == "win32":
            size_StaticBox = (500, 200)
            size_StaticBox_scheme = (445, 450)
            size_StaticBox_substrate = (960, 140)
            crystal_combobox = (80, -1)
            symmetry_combobox = (80, -1)
            font_Statictext = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_combobox = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font = wx.Font(9, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 16
        elif _platform == 'darwin':
            size_StaticBox = (500, 140)
            size_StaticBox_scheme = (505, 140)
            size_StaticBox_substrate = (980, 140)
            crystal_combobox = (80, -1)
            symmetry_combobox = (80, -1)
            font_Statictext = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_combobox = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font = wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 18

        flagSizer = wx.ALL

        """master sizer for the whole panel"""
        self.mastersizer = wx.GridBagSizer(hgap=4, vgap=3)

        """
        Scheme part
        """
        Scheme_box = wx.StaticBox(self, -1, " Scheme ",
                                  size=size_StaticBox_scheme)
        Scheme_box.SetFont(font)
        Scheme_box_sizer = wx.StaticBoxSizer(Scheme_box, wx.VERTICAL)
        in_Scheme_box = wx.GridBagSizer(hgap=1, vgap=0)

        bmp = Scheme_SingleCrystal.GetBitmap()
        self.img = wx.StaticBitmap(self, -1, bmp)

        in_Scheme_box.Add(self.img, pos=(0, 0), flag=flagSizer)
        Scheme_box_sizer.Add(in_Scheme_box, 0, wx.ALL, 5)

        """
        Geometry part
        """
        Geometry_box = wx.StaticBox(self, -1, " Geometry ",
                                    size=size_StaticBox)
        Geometry_box.SetFont(font)
        Geometry_box_sizer = wx.StaticBoxSizer(Geometry_box, wx.VERTICAL)
        in_Geometry_box_sizer = wx.GridBagSizer(hgap=10, vgap=0)

        label_1 = "Default"
        label_2 = "Thin film"
        label_3 = "Thick film"
        label_4 = "Thick film + substrate"

        self.rb1 = wx.RadioButton(self, label=label_1, style=wx.RB_GROUP)
        self.rb2 = wx.RadioButton(self, label=label_2)
        self.rb3 = wx.RadioButton(self, label=label_3)
        self.rb4 = wx.RadioButton(self, label=label_4)

        self.rb1.Bind(wx.EVT_RADIOBUTTON, self.on_set_val)
        self.rb2.Bind(wx.EVT_RADIOBUTTON, self.on_set_val)
        self.rb3.Bind(wx.EVT_RADIOBUTTON, self.on_set_val)
        self.rb4.Bind(wx.EVT_RADIOBUTTON, self.on_set_val)
        self.state = [True, False, False, False]
        self.rb = [self.rb1, self.rb2, self.rb3, self.rb4]

        in_Geometry_box_sizer.Add(self.rb1, pos=(0, 0), flag=flagSizer)
        in_Geometry_box_sizer.Add(self.rb2, pos=(2, 0), flag=flagSizer)
        in_Geometry_box_sizer.Add(self.rb3, pos=(4, 0), flag=flagSizer)
        in_Geometry_box_sizer.Add(self.rb4, pos=(6, 0), flag=flagSizer)

        Geometry_box_sizer.Add(in_Geometry_box_sizer, 0, wx.ALL, 5)

        """
        Film thickness part
        """
        Thickness_box = wx.StaticBox(self, -1, " Film Thickness ",
                                     size=size_StaticBox)
        Thickness_box.SetFont(font)
        self.Thickness_box_sizer = wx.StaticBoxSizer(Thickness_box,
                                                     wx.VERTICAL)
        self.in_Thickness_box_sizer = wx.GridBagSizer(hgap=8, vgap=1)

        film_th_txt = wx.StaticText(self, -1, label=u'Film Thickness',
                                    size=(100, vStatictextsize))
        film_th_txt.SetFont(font_Statictext)
        self.film_th = wx.TextCtrl(self, size=size_value_hkl,
                                   validator=TextValidator(DIGIT_ONLY))
        self.film_th.SetFont(font_TextCtrl)

        self.dw_th_txt = wx.StaticText(self, -1, label=u'Film Dw',
                                       size=(100, vStatictextsize))
        self.dw_th_txt.SetFont(font_Statictext)
        self.dw_th = wx.TextCtrl(self, size=size_value_hkl,
                                 validator=TextValidator(DIGIT_ONLY))
        self.dw_th.SetFont(font_TextCtrl)
        self.dw_th.SetValue(str(1))

        self.in_Thickness_box_sizer.Add(film_th_txt, pos=(0, 0),
                                        flag=flagSizer)
        self.in_Thickness_box_sizer.Add(self.film_th, pos=(0, 1),
                                        flag=flagSizer)
        self.in_Thickness_box_sizer.Add(self.dw_th_txt, pos=(0, 4),
                                        flag=flagSizer)
        self.in_Thickness_box_sizer.Add(self.dw_th, pos=(0, 5),
                                        flag=flagSizer)
        self.Thickness_box_sizer.Add(self.in_Thickness_box_sizer, 0, wx.ALL, 5)

        """
        Substrate part
        """
        Substrate_box = wx.StaticBox(self, -1, " Substrate ",
                                     size=size_StaticBox_substrate)
        Substrate_box.SetFont(font)
        self.Substrate_box_sizer = wx.StaticBoxSizer(Substrate_box,
                                                     wx.VERTICAL)
        self.in_Substrate_box_sizer = wx.GridBagSizer(hgap=16, vgap=1)

        crystalname_txt = wx.StaticText(self, -1, label=u'Crystal',
                                        size=(45, vStatictextsize))
        crystalname_txt.SetFont(font_Statictext)
        self.crystal_choice = ["None"]
        self.cb_crystalname = wx.ComboBox(self, pos=(50, 30),
                                          choices=self.crystal_choice,
                                          style=wx.CB_READONLY,
                                          size=crystal_combobox)
        self.cb_crystalname.SetStringSelection(self.crystal_choice[0])
        self.cb_crystalname.SetFont(font_combobox)
        self.Bind(wx.EVT_COMBOBOX, self.on_change_substrate,
                  self.cb_crystalname)

        crystalsymmetry_txt = wx.StaticText(self, -1, label=u'Symmetry:',
                                            size=(65, vStatictextsize))
        crystalsymmetry_txt.SetFont(font_Statictext)
        self.symmetry_choice = ["cubic", "hexa", "tetra", "ortho", "rhombo",
                                "mono", "triclinic"]
        self.cb_crystalsymmetry = wx.ComboBox(self, pos=(50, 30),
                                              choices=self.symmetry_choice,
                                              style=wx.CB_READONLY,
                                              size=symmetry_combobox)
        self.cb_crystalsymmetry.SetStringSelection(self.symmetry_choice[0])
        self.cb_crystalsymmetry.SetFont(font_combobox)
        self.cb_crystalsymmetry.Bind(wx.EVT_COMBOBOX, self.on_select_symmetry)

        reflection_txt = wx.StaticText(self, -1, label=u'Reflection:',
                                       size=(70, vStatictextsize))
        reflection_txt.SetFont(font_Statictext)
        h_direction_txt = wx.StaticText(self, -1, label=u'h',
                                        size=(10, vStatictextsize))
        h_direction_txt.SetFont(font_Statictext)
        self.h_direction = wx.TextCtrl(self, size=size_value_hkl,
                                       validator=TextValidator(DIGIT_ONLY))
        self.h_direction.SetFont(font_TextCtrl)

        k_direction_txt = wx.StaticText(self, -1, label=u'k',
                                        size=(10, vStatictextsize))
        k_direction_txt.SetFont(font_Statictext)
        self.k_direction = wx.TextCtrl(self, size=size_value_hkl,
                                       validator=TextValidator(DIGIT_ONLY))
        self.k_direction.SetFont(font_TextCtrl)

        l_direction_txt = wx.StaticText(self, -1, label=u'l',
                                        size=(10, vStatictextsize))
        l_direction_txt.SetFont(font_Statictext)
        self.l_direction = wx.TextCtrl(self, size=size_value_hkl,
                                       validator=TextValidator(DIGIT_ONLY))
        self.l_direction.SetFont(font_TextCtrl)

        latticeparam_txt = wx.StaticText(self, -1,
                                         label=u'Lattice parameters (\u212B):',
                                         size=(135, vStatictextsize))
        latticeparam_txt.SetFont(font_Statictext)

        self.symmetry_txt_hide = wx.TextCtrl(self, size=(0, vStatictextsize))
        self.symmetry_txt_hide.Hide()

        a_param_txt = wx.StaticText(self, -1, label=u'a',
                                    size=(10, vStatictextsize))
        a_param_txt.SetFont(font_Statictext)
        self.a_param = wx.TextCtrl(self, size=size_value_lattice,
                                   validator=TextValidator(DIGIT_ONLY))
        self.a_param.SetFont(font_TextCtrl)

        b_param_txt = wx.StaticText(self, -1, label=u'b',
                                    size=(10, vStatictextsize))
        b_param_txt.SetFont(font_Statictext)
        self.b_param = wx.TextCtrl(self, size=size_value_lattice,
                                   validator=TextValidator(DIGIT_ONLY))
        self.b_param.SetFont(font_TextCtrl)

        c_param_txt = wx.StaticText(self, -1, label=u'c',
                                    size=(10, vStatictextsize))
        c_param_txt.SetFont(font_Statictext)
        self.c_param = wx.TextCtrl(self, size=size_value_lattice,
                                   validator=TextValidator(DIGIT_ONLY))
        self.c_param.SetFont(font_TextCtrl)

        alpha_param_txt = wx.StaticText(self, -1,
                                        label=u'\N{GREEK SMALL LETTER ALPHA}',
                                        size=(10, vStatictextsize))
        alpha_param_txt.SetFont(font_Statictext)
        self.alpha_param = wx.TextCtrl(self, size=size_value_lattice,
                                       validator=TextValidator(DIGIT_ONLY))
        self.alpha_param.SetFont(font_TextCtrl)

        beta_param_txt = wx.StaticText(self, -1,
                                       label=u'\N{GREEK SMALL LETTER BETA}',
                                       size=(10, vStatictextsize))
        beta_param_txt.SetFont(font_Statictext)
        self.beta_param = wx.TextCtrl(self, size=size_value_lattice,
                                      validator=TextValidator(DIGIT_ONLY))
        self.beta_param.SetFont(font_TextCtrl)

        gamma_param_txt = wx.StaticText(self, -1,
                                        label=u'\N{GREEK SMALL LETTER GAMMA}',
                                        size=(10, vStatictextsize))
        gamma_param_txt.SetFont(font_Statictext)
        self.gamma_param = wx.TextCtrl(self, size=size_value_lattice,
                                       validator=TextValidator(DIGIT_ONLY))
        self.gamma_param.SetFont(font_TextCtrl)

        self.in_Substrate_box_sizer.Add(crystalname_txt, pos=(0, 0),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.cb_crystalname, pos=(0, 1),
                                        span=(1, 3), flag=flagSizer)
        self.in_Substrate_box_sizer.Add(reflection_txt, pos=(1, 0),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(h_direction_txt, pos=(1, 1),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.h_direction, pos=(1, 2),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(k_direction_txt, pos=(1, 3),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.k_direction, pos=(1, 4),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(l_direction_txt, pos=(1, 5),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.l_direction, pos=(1, 6),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(latticeparam_txt, pos=(0, 5),
                                        span=(1, 4),
                                        flag=wx.ALL | wx.ALIGN_RIGHT |
                                        wx.ALIGN_CENTER_VERTICAL)
        self.in_Substrate_box_sizer.Add(a_param_txt, pos=(0, 9),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.a_param, pos=(0, 10),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(b_param_txt, pos=(0, 11),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.b_param, pos=(0, 12),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(c_param_txt, pos=(0, 13),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.c_param, pos=(0, 14),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(crystalsymmetry_txt, pos=(0, 15),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.cb_crystalsymmetry, pos=(1, 15),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.symmetry_txt_hide, pos=(0, 16),
                                        flag=flagSizer)

        self.in_Substrate_box_sizer.Add(alpha_param_txt, pos=(1, 9),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.alpha_param, pos=(1, 10),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(beta_param_txt, pos=(1, 11),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.beta_param, pos=(1, 12),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(gamma_param_txt, pos=(1, 13),
                                        flag=flagSizer)
        self.in_Substrate_box_sizer.Add(self.gamma_param, pos=(1, 14),
                                        flag=flagSizer)

        self.Substrate_box_sizer.Add(self.in_Substrate_box_sizer, 0, wx.ALL, 5)

        self.Textcontrol = [self.film_th, self.dw_th, self.h_direction,
                            self.k_direction, self.l_direction,
                            self.symmetry_txt_hide,
                            self.a_param, self.b_param, self.c_param,
                            self.alpha_param, self.beta_param,
                            self.gamma_param]

        Textcontrolen = range(len(self.Textcontrol))
        self.data_fields = dict(zip(Textcontrolen, self.Textcontrol))

        self.mastersizer.Add(Geometry_box_sizer, pos=(0, 0),
                             flag=flagSizer, border=5)
        self.mastersizer.Add(Scheme_box_sizer, pos=(0, 1), span=(2, 1),
                             flag=flagSizer, border=5)
        self.mastersizer.Add(self.Thickness_box_sizer, pos=(1, 0),
                             flag=flagSizer, border=5)
        self.mastersizer.Add(self.Substrate_box_sizer, pos=(2, 0), span=(0, 2),
                             flag=flagSizer, border=5)

        pub.subscribe(self.on_load, pubsub_Load_project)
        pub.subscribe(self.on_read_data_field, pubsub_Read_field4Save)
        pub.subscribe(self.on_read_data_field, pubsub_Read_field4Fit)
        pub.subscribe(self.on_apply_color_field,
                      pubsub_changeColor_field4Save)
        pub.subscribe(self.read_crystal_list, pubsub_update_crystal_list)

        self.SetSizer(self.mastersizer)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.mastersizer.Hide(self.Thickness_box_sizer)
        self.mastersizer.Hide(self.Substrate_box_sizer)

        self.read_crystal_list()

    def read_crystal_list(self):
        a = P4Rm()
        self.cb_crystalname.SetItems(a.crystal_list)
        self.cb_crystalname.SetStringSelection(a.crystal_list[0])

    def on_change_substrate(self, event):
        P4Rm.PathDict['substrate_name'] = event.GetString()

    def on_set_val(self, event):
        a = P4Rm()
        if not a.ParamDict['th'].any():
            return
        else:
            self.Freeze()
            self.state = []
            state1 = self.rb1.GetValue()
            state2 = self.rb2.GetValue()
            state3 = self.rb3.GetValue()
            state4 = self.rb4.GetValue()
            self.state = [state1, state2, state3, state4]
            P4Rm.AllDataDict['geometry'] = self.state.index(True)
            pub.sendMessage(pubsub_Re_Read_field_paramters_panel)
            self.Thaw()
            self.on_apply_rb()

    def on_apply_rb(self):
        self.Freeze()
        if self.state[0]:
            bmp = Scheme_SingleCrystal.GetBitmap()
        elif self.state[1]:
            bmp = Scheme_ThinFilm.GetBitmap()
        elif self.state[2]:
            bmp = Scheme_ThickFilm.GetBitmap()
        elif self.state[3]:
            bmp = Scheme_ThickFilmAndSubstrate.GetBitmap()
        self.img.SetBitmap(bmp)

        if self.state[2]:
            self.mastersizer.Show(self.Thickness_box_sizer)
            self.in_Thickness_box_sizer.Hide(self.dw_th_txt)
            self.in_Thickness_box_sizer.Hide(self.dw_th)
        else:
            self.mastersizer.Hide(self.Thickness_box_sizer)

        if self.state[3]:
            self.mastersizer.Show(self.Substrate_box_sizer)
            self.mastersizer.Show(self.Thickness_box_sizer)
        else:
            self.mastersizer.Hide(self.Substrate_box_sizer)
        self.Thaw()
        self.Refresh()

    def on_load(self, b=None):
        for ii in self.data_fields:
            self.data_fields[ii].Clear()
        if b == 1:
            for i in range(len(New_project_initial)):
                p_ = New_project_initial[i]
                self.data_fields[i].AppendText(str(p_))
        else:
            a = P4Rm()
            self.state = 4*[False]
            val = int(float(a.AllDataDict['geometry']))
            self.state[val] = True
            self.rb[val].SetValue(True)
            self.on_apply_rb()
            i = 0
            for k in p4R.SG_p[1:]:
                self.data_fields[i].AppendText(str(a.AllDataDict[k]))
                i += 1
            val = self.symmetry_choice[int(float(a.AllDataDict
                                       ['crystal_symmetry_s']))]
            self.cb_crystalsymmetry.SetStringSelection(val)
            self.on_select_symmetry(None, val)

            if a.PathDict['substrate_name'] in a.crystal_list:
                indexx = a.crystal_list.index(
                                           a.PathDict['substrate_name'])
                self.cb_crystalname.SetStringSelection(
                                           a.crystal_list[indexx])
                msg_ = "Config file successfully loaded"
                logger.log(logging.INFO, msg_)
            else:
                msg_ = ("You need to add the proper strcuture" +
                        "to continue")
                logger.log(logging.INFO, msg_)

    def on_select_symmetry(self, event=None, choice=None):
        """
        Symmetry combobox selection
        quite simple choice selection according to the symmetry condition
        """
        if choice is not None:
            i = choice
        else:
            i = event.GetString()

        cubique_text_state = ["Enable", "Disable", "Disable", "Disable",
                              "Disable", "Disable"]
        cubique_text_value = ["None", 0, 0, 90, 90, 90]

        hexa_text_state = ["Enable", "Disable", "Enable", "Disable", "Disable",
                           "Disable"]
        hexa_text_value = ["None", 0, "None", 90, 90, 120]

        tetra_text_state = ["Enable", "Disable", "Enable", "Disable",
                            "Disable", "Disable"]
        tetra_text_value = ["None", 0, "None", 90, 90, 90]

        ortho_text_state = ["Enable", "Enable", "Enable", "Disable", "Disable",
                            "Disable"]
        ortho_text_value = ["None", 0, "None", 90, 90, 90]

        rhombo_text_state = ["Enable", "Disable", "Disable", "Enable",
                             "Disable", "Disable"]
        rhombo_text_value = ["None", 0, 0, "None", 3, 3]

        mono_text_state = ["Enable", "Enable", "Enable", "Disable", "Enable",
                           "Disable"]
        mono_text_value = ["None", "None", "None", 90, "None", 90]

        tri_text_state = ["Enable", "Enable", "Enable", "Enable", "Enable",
                          "Enable"]
        tri_text_value = ["None", "None", "None", "None", "None", 90]

        if i == "cubic":
            temp_state = deepcopy(cubique_text_state)
            temp_value = deepcopy(cubique_text_value)
            self.symmetry_txt_hide.SetValue(str(0))
        elif i == "hexa":
            temp_state = deepcopy(hexa_text_state)
            temp_value = deepcopy(hexa_text_value)
            self.symmetry_txt_hide.SetValue(str(1))
        elif i == "tetra":
            temp_state = deepcopy(tetra_text_state)
            temp_value = deepcopy(tetra_text_value)
            self.symmetry_txt_hide.SetValue(str(2))
        elif i == "ortho":
            temp_state = deepcopy(ortho_text_state)
            temp_value = deepcopy(ortho_text_value)
            self.symmetry_txt_hide.SetValue(str(3))
        elif i == "rhombo":
            temp_state = deepcopy(rhombo_text_state)
            temp_value = deepcopy(rhombo_text_value)
            self.symmetry_txt_hide.SetValue(str(4))
        elif i == "mono":
            temp_state = deepcopy(mono_text_state)
            temp_value = deepcopy(mono_text_value)
            self.symmetry_txt_hide.SetValue(str(5))
        elif i == "triclinic":
            temp_state = deepcopy(tri_text_state)
            temp_value = deepcopy(tri_text_value)
            self.symmetry_txt_hide.SetValue(str(6))

        num = 6
        for i in range(6):
            if temp_state[i] == "Enable":
                self.data_fields[num+i].Enable()
            else:
                self.data_fields[num+i].Disable()
            if i in range(0, 3):
                if temp_value[i] != "None":
                    self.data_fields[num+i].SetValue(str(self.data_fields[num +
                                                     temp_value[i]].GetValue()))
            elif i in range(3, 6):
                if temp_value[i] != "None":
                    if temp_value[i] == 90 or temp_value[i] == 120:
                        self.data_fields[num+i].Clear()
                        self.data_fields[num+i].SetValue(str(temp_value[i]))
                    elif temp_value[i] == 3:
                        self.data_fields[num+i].Clear()
                        temp = str(self.data_fields[num +
                                   temp_value[i]].GetValue())
                        self.data_fields[num+i].SetValue(temp)

    def on_read_data_field(self, case=None):
        P4Rm.checkGeometryField = 0
        check_empty = self.on_search_empty_fields()
        if check_empty is True:
            data_float = self.is_data_float()
            if data_float is True:
                P4Rm.checkGeometryField = 1

    def on_apply_color_field(self, color):
        for ii in range(len(self.data_fields)):
            self.data_fields[ii].SetBackgroundColour(color)
        self.Refresh()
        wx.Yield()

    def on_search_empty_fields(self):
        """
        search for empty field
        """
        check_empty = True
        empty_fields = []
        for ii in range(len(self.data_fields)):
            empt = self.data_fields[ii]
            if empt.GetValue() == "":
                empty_fields.append(ii)
        if empty_fields != []:
            check_empty = False
            for ii in empty_fields:
                self.data_fields[ii].SetBackgroundColour('red')
            self.Refresh()
            msg = "Please, fill the red empty fields to continue"
            dlg = GMD.GenericMessageDialog(None, msg,
                                           "Attention", agwStyle=wx.OK |
                                           wx.ICON_INFORMATION)
            dlg.ShowModal()
            for ii in empty_fields:
                self.data_fields[ii].SetBackgroundColour('white')
            self.Refresh()
        return check_empty

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def is_data_float(self):
        IsFloat = []
        dataFloat = True
        ProjectFileData = []
        for i in range(len(self.data_fields)):
            ProjectFileData.append(self.data_fields[i].GetValue())
        for i in range(len(self.data_fields)):
            t = self.data_fields[i].GetValue()
            IsFloat.append(self.is_number(t))
        if False in IsFloat:
            dataFloat = False
            if self.not_a_float == 0:
                StringPosition = [i for i, x in enumerate(IsFloat)
                                  if x is False]
                for ii in StringPosition:
                    self.data_fields[ii].SetBackgroundColour('green')
                self.Refresh()
                msg_ = "Please, fill correctly the fields before to continue"
                dlg = GMD.GenericMessageDialog(None, msg_,
                                               "Attention",
                                               agwStyle=wx.OK |
                                               wx.ICON_INFORMATION)
                dlg.ShowModal()
                for ii in StringPosition:
                    self.data_fields[ii].SetBackgroundColour('white')
                self.Refresh()
        else:
            self.empty_field = 0
            self.parent.notebook.EnableTab(1, True)
            val = self.state.index(True)
            ProjectFileData.insert(0, val)
            P4Rm.PathDict['substrate_name'] = self.cb_crystalname.GetStringSelection()
            P4Rm.sample_geometry = [float(ii) for ii in ProjectFileData]
        return dataFloat
