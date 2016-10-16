#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

# =============================================================================
# Radmax Cell Parameters module
# =============================================================================


import wx
import wx.lib.agw.aui as aui
import wx.lib.scrolledpanel as scrolled

from wx.lib.pubsub import pub
import wx.lib.agw.genericmessagedialog as GMD

from copy import deepcopy
from sys import platform as _platform

import Parameters4Radmax as p4R
from Parameters4Radmax import P4Rm
from Settings4Radmax import TextValidator

from Calcul4Radmax import Calcul4Radmax

import logging
logger = logging.getLogger(__name__)

DIGIT_ONLY = 2

"""New Project initial data"""
New_project_initial = [1.5406, 5e-6, 0.013, 0.013, 0.00001, 0.00001, 2,
                       1, 1, 0, 0, 5.4135, 5.4135, 5.4135, 90, 90, 90,
                       0, 10, 10, 3500, 70]
"""Pubsub message"""

pubsub_Load_project = "LoadProject"
pubsub_New = "NewP"

pubsub_ChangeFrameTitle = "ChangeFrameTitle"

pubsub_Read_field_paramters_panel = "ReadParametersPanel"
pubsub_Re_Read_field_paramters_panel = "ReReadParametersPanel"
pubsub_Update_Fit_Live = "UpdateFitLive"

pubsub_Read_field4Save = "ReadField4Save"
pubsub_changeColor_field4Save = "ChangeColorField4Save"
pubsub_shortcut = "Shortcut"
pubsub_On_Limit_Before_Graph = "OnLimitBeforeGraph"
pubsub_Update_Scale_Strain = "OnUpdateScaleStrain"
pubsub_Update_Scale_DW = "OnUpdateScaleDW"
pubsub_Read_sp_dwp = "ReadSpDwp"

pubsub_Read_field4Fit = "ReadField4Fit"
pubsub_Test_Model = "TestModel"
pubsub_change_basic_function = "ChangeBasicFunction"
pubsub_update_initial_panel = "UpdateInitialPanel"
pubsub_update_crystal_list = "UpdateCrystalList"
pubsub_test_some_field = "TestSomeField"
pubsub_change_update_btn_state = "ChangeUpdateButtonState"
pubsub_update_sp_dwp_eta = "UpdatespdwpEta"
pubsub_change_damaged_depth_color = "ChangeDamagedDepthColor"
pubsub_update_from_damaged = "UpdateFromDamaged"


# -----------------------------------------------------------------------------
class InitialDataPanel(scrolled.ScrolledPanel):
    """
    Initial Parameters main panel
    we built the all page in this module
    """
    def __init__(self, parent, statusbar):
        scrolled.ScrolledPanel.__init__(self, parent)
        self.statusbar = statusbar
        self.parent = parent
        self.parent.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING,
                         self.on_page_changed)

        size_text = (85, 22)
        size_value_hkl = (50, 22)
        size_value_lattice = (65, 22)
        size_damaged_depth = (110, 22)
        size_scale = (50, 22)

        if _platform == "linux" or _platform == "linux2":
            size_StaticBox = (950, 140)
            crystal_combobox = (110, -1)
            function_combobox = (130, -1)
            symmetry_combobox = (90, -1)
            size_lattp = 150
            size_damdept = 130
            size_noslice = 110
            font_Statictext = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_combobox = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_scale = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font_update = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 16
        elif _platform == "win32":
            size_StaticBox = (960, 140)
            crystal_combobox = (80, -1)
            function_combobox = (100, -1)
            symmetry_combobox = (80, -1)
            size_lattp = 135
            size_damdept = 115
            size_noslice = 95
            font_Statictext = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_combobox = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_scale = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font_update = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(9, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 16
        elif _platform == 'darwin':
            size_StaticBox = (980, 140)
            crystal_combobox = (80, -1)
            function_combobox = (130, -1)
            symmetry_combobox = (80, -1)
            size_lattp = 150
            size_damdept = 130
            size_noslice = 110
            font_Statictext = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_combobox = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_scale = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font_update = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            font = wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.BOLD)
            vStatictextsize = 18

        flagSizer = wx.ALL | wx.ALIGN_CENTER_VERTICAL

        """master sizer for the whole panel"""
        mastersizer = wx.BoxSizer(wx.VERTICAL)

        """Experiment part"""
        Experiment_box = wx.StaticBox(self, -1, " Experiment ",
                                      size=size_StaticBox)
        Experiment_box.SetFont(font)
        Experiment_box_sizer = wx.StaticBoxSizer(Experiment_box, wx.VERTICAL)
        in_Experiment_box_sizer = wx.GridBagSizer(hgap=10, vgap=0)

        wavelength_txt = wx.StaticText(self, -1, label=u'Wavelength (\u212B)',
                                       size=(100, vStatictextsize))
        wavelength_txt.SetFont(font_Statictext)
        self.wavelength = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                      size=size_text,
                                      validator=TextValidator(DIGIT_ONLY))
        self.wavelength.SetFont(font_TextCtrl)

        bckground_txt = wx.StaticText(self, -1, label=u'Background',
                                      size=(75, vStatictextsize))
        bckground_txt.SetFont(font_Statictext)
        self.bckground = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                     size=size_text,
                                     validator=TextValidator(DIGIT_ONLY))
        self.bckground.SetFont(font_TextCtrl)

        fitfunction_txt = wx.StaticText(self, -1, label=u'Resolution function',
                                        size=(110, vStatictextsize))
        fitfunction_txt.SetFont(font_Statictext)
        self.cb_fitfunction = wx.ComboBox(self, pos=(50, 30),
                                          choices=p4R.FitFunction,
                                          style=wx.CB_READONLY,
                                          size=function_combobox)
        self.cb_fitfunction.SetStringSelection(p4R.FitFunction[2])
        self.cb_fitfunction.SetFont(font_combobox)
        self.Bind(wx.EVT_COMBOBOX, self.on_change_function,
                  self.cb_fitfunction)

        """parametre FWHM=Resolution"""
        self.fwhml_txt = wx.StaticText(self, -1, label=u'Width (°)',
                                       size=(80, vStatictextsize))
        self.fwhml_txt.SetFont(font_Statictext)
        self.fwhml = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                 size=size_text,
                                 validator=TextValidator(DIGIT_ONLY))
        self.fwhml.SetFont(font_TextCtrl)

        self.fwhmr_txt = wx.StaticText(self, -1, label=u'Width right (°)',
                                       size=(80, vStatictextsize))
        self.fwhmr_txt.SetFont(font_Statictext)
        self.fwhmr = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                 size=size_text,
                                 validator=TextValidator(DIGIT_ONLY))
        self.fwhmr.SetFont(font_TextCtrl)

        """parametre eta=shape"""
        self.shapel_txt = wx.StaticText(self, -1, label=u'Shape',
                                        size=(80, vStatictextsize))
        self.shapel_txt.SetFont(font_Statictext)
        self.shapel = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                  size=size_text,
                                  validator=TextValidator(DIGIT_ONLY))
        self.shapel.SetFont(font_TextCtrl)

        self.shaper_txt = wx.StaticText(self, -1, label=u'Shape right',
                                        size=(80, vStatictextsize))
        self.shaper_txt.SetFont(font_Statictext)
        self.shaper = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                  size=size_text,
                                  validator=TextValidator(DIGIT_ONLY))
        self.shaper.SetFont(font_TextCtrl)

        self.b_bell_txt = wx.StaticText(self, -1, label=u'b',
                                        size=(45, vStatictextsize))
        self.b_bell_txt.SetFont(font_Statictext)
        self.b_bell = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                  size=size_text,
                                  validator=TextValidator(DIGIT_ONLY))
        self.b_bell.SetFont(font_TextCtrl)

        in_Experiment_box_sizer.Add(wavelength_txt, pos=(0, 0),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.wavelength, pos=(0, 1),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(bckground_txt, pos=(1, 0),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.bckground, pos=(1, 1),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(fitfunction_txt, pos=(0, 2),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.cb_fitfunction, pos=(0, 3),
                                    flag=flagSizer)
        """resolution = FWHM droit et gauche"""
        in_Experiment_box_sizer.Add(self.fwhml_txt, pos=(0, 4),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.fwhml, pos=(0, 5),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.fwhmr_txt, pos=(1, 4),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.fwhmr, pos=(1, 5),
                                    flag=flagSizer)
        """shape = eta droit et gauche"""
        in_Experiment_box_sizer.Add(self.shapel_txt, pos=(0, 6),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.shapel, pos=(0, 7),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.shaper_txt, pos=(1, 6),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.shaper, pos=(1, 7),
                                    flag=flagSizer)
        """b = b fonction gBell"""
        in_Experiment_box_sizer.Add(self.b_bell_txt, pos=(0, 8),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.b_bell, pos=(0, 9),
                                    flag=flagSizer)

        Experiment_box_sizer.Add(in_Experiment_box_sizer, 0, wx.ALL, 5)

        self.func_list = [self.fwhml_txt, self.fwhml,
                          self.fwhmr_txt, self.fwhmr,
                          self.shapel_txt, self.shapel,
                          self.shaper_txt, self.shaper,
                          self.b_bell_txt, self.b_bell
                          ]
        self.b_bell.AppendText(str(p4R.FitFunction_value['b_func']))
        self.fwhmr.AppendText(str(p4R.FitFunction_value['resolr']))
        self.shaper.AppendText(str(p4R.FitFunction_value['shaper']))
        P4Rm.ParamDict['b_func'] = p4R.FitFunction_value['b_func']
        P4Rm.ParamDict['resolr'] = p4R.FitFunction_value['resolr']
        P4Rm.ParamDict['shaper'] = p4R.FitFunction_value['shaper']

        l = ["S", "S", "H", "H", "S", "S", "H", "H", "H", "H"]
        for i in range(len(self.func_list)):
            if l[i] is "S":
                self.func_list[i].Show()
            elif l[i] is "H":
                self.func_list[i].Hide()
        funky = p4R.FitFunction.index("Pseudo-Voigt")
        P4Rm.ParamDict['func_profile'] = p4R.FitFunction_choice[funky]

        """Material part"""
        Material_box = wx.StaticBox(self, -1, " Material ",
                                    size=size_StaticBox)
        Material_box.SetFont(font)
        Material_box_sizer = wx.StaticBoxSizer(Material_box, wx.VERTICAL)
        in_Material_box_sizer = wx.GridBagSizer(hgap=16, vgap=1)

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
        self.Bind(wx.EVT_COMBOBOX, self.on_change_material,
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
        self.h_direction = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                       size=size_value_hkl,
                                       validator=TextValidator(DIGIT_ONLY))
        self.h_direction.SetFont(font_TextCtrl)

        k_direction_txt = wx.StaticText(self, -1, label=u'k',
                                        size=(10, vStatictextsize))
        k_direction_txt.SetFont(font_Statictext)
        self.k_direction = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                       size=size_value_hkl,
                                       validator=TextValidator(DIGIT_ONLY))
        self.k_direction.SetFont(font_TextCtrl)

        l_direction_txt = wx.StaticText(self, -1, label=u'l',
                                        size=(10, vStatictextsize))
        l_direction_txt.SetFont(font_Statictext)
        self.l_direction = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                       size=size_value_hkl,
                                       validator=TextValidator(DIGIT_ONLY))
        self.l_direction.SetFont(font_TextCtrl)

        latticeparam_txt = wx.StaticText(self, -1,
                                         label=u'Lattice parameters (\u212B):',
                                         size=(size_lattp, vStatictextsize))
        latticeparam_txt.SetFont(font_Statictext)

        self.symmetry_txt_hide = wx.TextCtrl(self, size=(0, vStatictextsize))
        self.symmetry_txt_hide.Hide()

        a_param_txt = wx.StaticText(self, -1, label=u'a',
                                    size=(10, vStatictextsize))
        a_param_txt.SetFont(font_Statictext)
        self.a_param = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                   size=size_value_lattice,
                                   validator=TextValidator(DIGIT_ONLY))
        self.a_param.SetFont(font_TextCtrl)

        b_param_txt = wx.StaticText(self, -1, label=u'b',
                                    size=(10, vStatictextsize))
        b_param_txt.SetFont(font_Statictext)
        self.b_param = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                   size=size_value_lattice,
                                   validator=TextValidator(DIGIT_ONLY))
        self.b_param.SetFont(font_TextCtrl)

        c_param_txt = wx.StaticText(self, -1, label=u'c',
                                    size=(10, vStatictextsize))
        c_param_txt.SetFont(font_Statictext)
        self.c_param = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                   size=size_value_lattice,
                                   validator=TextValidator(DIGIT_ONLY))
        self.c_param.SetFont(font_TextCtrl)

        alpha_param_txt = wx.StaticText(self, -1,
                                        label=u'\N{GREEK SMALL LETTER ALPHA}',
                                        size=(10, vStatictextsize))
        alpha_param_txt.SetFont(font_Statictext)
        self.alpha_param = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                       size=size_value_lattice,
                                       validator=TextValidator(DIGIT_ONLY))
        self.alpha_param.SetFont(font_TextCtrl)

        beta_param_txt = wx.StaticText(self, -1,
                                       label=u'\N{GREEK SMALL LETTER BETA}',
                                       size=(10, vStatictextsize))
        beta_param_txt.SetFont(font_Statictext)
        self.beta_param = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                      size=size_value_lattice,
                                      validator=TextValidator(DIGIT_ONLY))
        self.beta_param.SetFont(font_TextCtrl)

        gamma_param_txt = wx.StaticText(self, -1,
                                        label=u'\N{GREEK SMALL LETTER GAMMA}',
                                        size=(10, vStatictextsize))
        gamma_param_txt.SetFont(font_Statictext)
        self.gamma_param = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                       size=size_value_lattice,
                                       validator=TextValidator(DIGIT_ONLY))
        self.gamma_param.SetFont(font_TextCtrl)

        in_Material_box_sizer.Add(crystalname_txt, pos=(0, 0), flag=flagSizer)
        in_Material_box_sizer.Add(self.cb_crystalname, pos=(0, 1), span=(1, 3),
                                  flag=flagSizer)
        in_Material_box_sizer.Add(reflection_txt, pos=(1, 0), flag=flagSizer)
        in_Material_box_sizer.Add(h_direction_txt, pos=(1, 1), flag=flagSizer)
        in_Material_box_sizer.Add(self.h_direction, pos=(1, 2), flag=flagSizer)
        in_Material_box_sizer.Add(k_direction_txt, pos=(1, 3), flag=flagSizer)
        in_Material_box_sizer.Add(self.k_direction, pos=(1, 4), flag=flagSizer)
        in_Material_box_sizer.Add(l_direction_txt, pos=(1, 5), flag=flagSizer)
        in_Material_box_sizer.Add(self.l_direction, pos=(1, 6), flag=flagSizer)

        in_Material_box_sizer.Add(latticeparam_txt, pos=(0, 5), span=(1, 4),
                                  flag=wx.ALL | wx.ALIGN_RIGHT |
                                  wx.ALIGN_CENTER_VERTICAL)
        in_Material_box_sizer.Add(a_param_txt, pos=(0, 9), flag=flagSizer)
        in_Material_box_sizer.Add(self.a_param, pos=(0, 10), flag=flagSizer)
        in_Material_box_sizer.Add(b_param_txt, pos=(0, 11), flag=flagSizer)
        in_Material_box_sizer.Add(self.b_param, pos=(0, 12), flag=flagSizer)
        in_Material_box_sizer.Add(c_param_txt, pos=(0, 13), flag=flagSizer)
        in_Material_box_sizer.Add(self.c_param, pos=(0, 14), flag=flagSizer)

        in_Material_box_sizer.Add(crystalsymmetry_txt, pos=(0, 15),
                                  flag=flagSizer)
        in_Material_box_sizer.Add(self.cb_crystalsymmetry, pos=(1, 15),
                                  flag=flagSizer)
        in_Material_box_sizer.Add(self.symmetry_txt_hide, pos=(0, 16),
                                  flag=flagSizer)

        in_Material_box_sizer.Add(alpha_param_txt, pos=(1, 9),
                                  flag=flagSizer)
        in_Material_box_sizer.Add(self.alpha_param, pos=(1, 10),
                                  flag=flagSizer)
        in_Material_box_sizer.Add(beta_param_txt, pos=(1, 11),
                                  flag=flagSizer)
        in_Material_box_sizer.Add(self.beta_param, pos=(1, 12),
                                  flag=flagSizer)
        in_Material_box_sizer.Add(gamma_param_txt, pos=(1, 13),
                                  flag=flagSizer)
        in_Material_box_sizer.Add(self.gamma_param, pos=(1, 14),
                                  flag=flagSizer)

        Material_box_sizer.Add(in_Material_box_sizer, 0, wx.ALL, 5)

        """Strain and Debye Waller part"""
        Strain_DW_box = wx.StaticBox(self, -1, " Strain and Debye-Waller ",
                                     size=size_StaticBox)
        Strain_DW_box.SetFont(font)
        Strain_DW_box_sizer = wx.StaticBoxSizer(Strain_DW_box, wx.VERTICAL)
        in_Strain_DW_box_sizer = wx.GridBagSizer(hgap=10, vgap=1)

        self.Strainname_ID = wx.NewId()
        self.dwname_ID = wx.NewId()

        self.modelChoice = wx.TextCtrl(self, size=(0, vStatictextsize),
                                       validator=TextValidator(DIGIT_ONLY))
        self.modelChoice.Hide()
        self.modelCalc = 0

        strainname_txt = wx.StaticText(self, self.Strainname_ID,
                                       label=u'Strain: model',
                                       size=(85, vStatictextsize))
        strainname_txt.SetFont(font_Statictext)
        self.cb_strainname = wx.ComboBox(self, pos=(50, 30),
                                         choices=p4R.Strain_DW_choice,
                                         style=wx.CB_READONLY)
        self.cb_strainname.SetStringSelection(p4R.Strain_DW_choice[0])
        self.cb_strainname.SetFont(font_combobox)

        dwname_txt = wx.StaticText(self, self.dwname_ID, label=u'DW: model',
                                   size=(75, vStatictextsize))
        dwname_txt.SetFont(font_Statictext)
        self.cb_dwname = wx.ComboBox(self, pos=(50, 30),
                                     choices=p4R.Strain_DW_choice,
                                     style=wx.CB_READONLY)
        self.cb_dwname.SetStringSelection(p4R.Strain_DW_choice[0])
        self.cb_dwname.SetFont(font_combobox)

        self.cb_strainname.Bind(wx.EVT_COMBOBOX, self.on_select_strain_Dw_name)
        self.cb_dwname.Bind(wx.EVT_COMBOBOX, self.on_select_strain_Dw_name)

        self.StrainBfunction_ID = wx.NewId()
        self.dwBfunction_ID = wx.NewId()

        StrainBfunction_txt = wx.StaticText(self, id=self.StrainBfunction_ID,
                                            label=u'Basis functions',
                                            size=(95, vStatictextsize))
        StrainBfunction_txt.SetFont(font_Statictext)
        self.StrainBfunction = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                           size=size_value_lattice,
                                           validator=TextValidator(DIGIT_ONLY))
        self.StrainBfunction.SetFont(font_TextCtrl)

        dwBfunction_txt = wx.StaticText(self, id=self.dwBfunction_ID,
                                        label=u'Basis functions',
                                        size=(95, vStatictextsize))
        dwBfunction_txt.SetFont(font_Statictext)
        self.dwBfunction_choice = [""]
        self.dwBfunction = wx.ComboBox(self, pos=(50, 30),
                                       choices=self.dwBfunction_choice,
                                       style=wx.CB_READONLY, size=(65, -1))
        self.dwBfunction.SetStringSelection(self.dwBfunction_choice[0])
        self.dwBfunction.SetFont(font_combobox)

        self.dwBfunction.Bind(wx.EVT_COMBOBOX, self.on_change_DW)

        self.dwBfunction_hide = wx.TextCtrl(self, size=(0, vStatictextsize),
                                            validator=TextValidator(
                                                      DIGIT_ONLY))
        self.dwBfunction_hide.Hide()

        damaged_depth_txt = wx.StaticText(self, -1,
                                          label=u'Damaged depth (\u212B)',
                                          size=(size_damdept, vStatictextsize))
        damaged_depth_txt.SetFont(font_Statictext)
        self.damaged_depth = myTextCtrl(self, -1, size=size_damaged_depth)
        self.damaged_depth.SetFont(font_TextCtrl)

        Nb_slice_txt = wx.StaticText(self, -1,
                                     label=u'Number of slices',
                                     size=(size_noslice, vStatictextsize))
        Nb_slice_txt.SetFont(font_Statictext)
        self.Nb_slice = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER,
                                    size=size_value_lattice,
                                    validator=TextValidator(DIGIT_ONLY))
        self.Nb_slice.SetFont(font_TextCtrl)

        self.m_strain_ID = wx.NewId()
        self.m_DW_ID = wx.NewId()

        self.scale_strain_Btn = wx.Button(self, id=self.m_strain_ID,
                                          label=u'Scale',
                                          size=size_scale, style=wx.NO_BORDER)
        self.scale_strain_Btn.SetFont(font_scale)
        self.scale_strain_Btn.Bind(wx.EVT_BUTTON, self.on_update_scale)
        self.strain_horizontal_ctrl = wx.TextCtrl(self, size=size_scale,
                                                  validator=TextValidator(
                                                            DIGIT_ONLY))
        self.strain_horizontal_ctrl.SetFont(font_TextCtrl)
        self.strain_horizontal_ctrl.SetValue(str(1))

        self.scale_DW_Btn = wx.Button(self, id=self.m_DW_ID, label=u'Scale',
                                      size=size_scale, style=wx.NO_BORDER)
        self.scale_DW_Btn.SetFont(font_scale)
        self.scale_DW_Btn.Bind(wx.EVT_BUTTON, self.on_update_scale)
        self.DW_horizontal_ctrl = wx.TextCtrl(self, size=size_scale,
                                              validator=TextValidator(
                                                        DIGIT_ONLY))
        self.DW_horizontal_ctrl.SetFont(font_TextCtrl)
        self.DW_horizontal_ctrl.SetValue(str(1))

        self.eta_strain_1 = wx.TextCtrl(self, size=size_scale,
                                        validator=TextValidator(DIGIT_ONLY))
        self.eta_strain_1.SetFont(font_TextCtrl)
        self.eta_strain_1.SetValue(str(0.5))

        self.eta_strain_2 = wx.TextCtrl(self, size=size_scale,
                                        validator=TextValidator(DIGIT_ONLY))
        self.eta_strain_2.SetFont(font_TextCtrl)
        self.eta_strain_2.SetValue(str(0.5))

        self.eta_dw_1 = wx.TextCtrl(self, size=size_scale,
                                    validator=TextValidator(DIGIT_ONLY))
        self.eta_dw_1.SetFont(font_TextCtrl)
        self.eta_dw_1.SetValue(str(0.5))

        self.eta_dw_2 = wx.TextCtrl(self, size=size_scale,
                                    validator=TextValidator(DIGIT_ONLY))
        self.eta_dw_2.SetFont(font_TextCtrl)
        self.eta_dw_2.SetValue(str(0.5))

        self.eta_txt_label = u'Eta1/Eta2 parameters'
        self.eta_txt = wx.StaticText(self, -1, label=self.eta_txt_label,
                                     size=(130, vStatictextsize))
        self.eta_txt.SetFont(font_Statictext)

        in_Strain_DW_box_sizer.Add(strainname_txt, pos=(0, 0),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.cb_strainname, pos=(0, 1),
                                   flag=flagSizer)

        in_Strain_DW_box_sizer.Add(StrainBfunction_txt, pos=(0, 2),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.StrainBfunction, pos=(0, 3),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.scale_strain_Btn, pos=(0, 4),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.strain_horizontal_ctrl, pos=(0, 5),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.eta_txt, pos=(0, 6), span=(1, 2),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.eta_strain_1, pos=(0, 9),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.eta_strain_2, pos=(0, 10),
                                   flag=flagSizer)

        in_Strain_DW_box_sizer.Add(dwname_txt, pos=(1, 0),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.cb_dwname, pos=(1, 1),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(dwBfunction_txt, pos=(1, 2),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.dwBfunction, pos=(1, 3),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.dwBfunction_hide, pos=(1, 11),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.scale_DW_Btn, pos=(1, 4),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.DW_horizontal_ctrl, pos=(1, 5),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.eta_dw_1, pos=(1, 9),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.eta_dw_2, pos=(1, 10),
                                   flag=flagSizer)

        in_Strain_DW_box_sizer.Add(damaged_depth_txt, pos=(2, 0),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.damaged_depth, pos=(2, 1),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(Nb_slice_txt, pos=(2, 2),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.Nb_slice, pos=(2, 3),
                                   flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.modelChoice, pos=(2, 10),
                                   flag=flagSizer)

        Strain_DW_box_sizer.Add(in_Strain_DW_box_sizer, 0, wx.ALL, 5)

        self.updateId = wx.NewId()
        self.update_Btn = wx.Button(self, id=self.updateId, label="Update")
        self.update_Btn.SetFont(font_update)
        self.update_Btn.Bind(wx.EVT_BUTTON, self.on_update)
        self.update_Btn.Disable()
        self.update_Btn.SetFocus()

        self.Textcontrolhide = [self.eta_strain_1, self.eta_strain_2,
                                self.eta_dw_1, self.eta_dw_2]
        for i in range(len(self.Textcontrolhide)):
            self.Textcontrolhide[i].Show(False)
        self.eta_txt.SetLabelText("")

        self.Textcontrol = [self.wavelength, self.bckground,
                            self.fwhml, self.fwhmr,
                            self.shapel, self.shaper, self.b_bell,
                            self.h_direction, self.k_direction,
                            self.l_direction, self.symmetry_txt_hide,
                            self.a_param, self.b_param, self.c_param,
                            self.alpha_param, self.beta_param,
                            self.gamma_param, self.modelChoice,
                            self.StrainBfunction, self.dwBfunction_hide,
                            self.damaged_depth, self.Nb_slice]

        Textcontrolen = range(len(self.Textcontrol))
        self.data_fields = dict(zip(Textcontrolen, self.Textcontrol))

        for name in self.Textcontrol:
            self.Bind(wx.EVT_TEXT_ENTER, self.on_press_enter, name)

        for num in range(len(self.func_list)):
            if num & 1:
                name = self.func_list[num]
                self.Bind(wx.EVT_TEXT_ENTER, self.on_press_enter, name)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_press_enter)

        self.paramcell = [self.a_param, self.b_param, self.c_param,
                          self.alpha_param, self.beta_param,
                          self.gamma_param]

        self.load_data = 0
        self.load_init = 0
        self.data_change = 0
        self.empty_field = 0
        self.not_a_float = 0
        self.spline_strain = ""
        self.spline_DW = ""

        mastersizer.Add(Experiment_box_sizer, 0, wx.ALL, 5)
        mastersizer.Add(Material_box_sizer, 0, wx.ALL, 5)
        mastersizer.Add(Strain_DW_box_sizer, 0, wx.ALL, 5)
        mastersizer.Add(self.update_Btn, 0, wx.ALL, 5)

        pub.subscribe(self.on_load, pubsub_Load_project)
        pub.subscribe(self.on_new_project, pubsub_New)
        pub.subscribe(self.on_update, pubsub_Re_Read_field_paramters_panel)
        pub.subscribe(self.on_update, pubsub_Update_Fit_Live)
        pub.subscribe(self.read_crystal_list, pubsub_update_crystal_list)
        pub.subscribe(self.key_pressed, pubsub_shortcut)
        pub.subscribe(self.on_test_model, pubsub_Test_Model)
        pub.subscribe(self.on_read_data_field, pubsub_Read_field4Fit)
        pub.subscribe(self.OnChangeBasisFunction_, pubsub_change_basic_function)
        pub.subscribe(self.on_read_data_field, pubsub_Read_field4Save)
        pub.subscribe(self.on_update_panel, pubsub_update_initial_panel)
        pub.subscribe(self.on_test_some_field, pubsub_test_some_field)
        pub.subscribe(self.on_change_update_button_state, pubsub_change_update_btn_state)
        pub.subscribe(self.on_update_sp_DW, pubsub_update_sp_dwp_eta)
        pub.subscribe(self.on_launch_calc4Fit, pubsub_Read_field_paramters_panel)
        pub.subscribe(self.on_read_sp_DW, pubsub_Read_sp_dwp)
        pub.subscribe(self.on_apply_color_field, pubsub_changeColor_field4Save)
        pub.subscribe(self.on_change_color_damaged_depth, pubsub_change_damaged_depth_color)
        pub.subscribe(self.on_update, pubsub_update_from_damaged)

        self.SetSizer(mastersizer)
        self.SetAutoLayout(1)
        self.SetupScrolling()

    def on_page_changed(self, event):
        self.update_Btn.SetFocus()

    def on_press_enter(self, event):
        self.on_update()
        event.Skip()

    def on_new_project(self):
        a = P4Rm()
        val = self.symmetry_choice[int(float(a.AllDataDict
                                   ['crystal_symmetry']))]
        self.cb_crystalsymmetry.SetStringSelection(val)
        self.on_select_symmetry(None, val)

        self.cb_strainname.SetSelection(0)
        self.cb_dwname.SetSelection(0)
        self.on_hide_show_eta(False)
        self.update_Btn.Disable()
        self.load_data = 0
        self.statusbar.SetStatusText(u"", 0)

        pub.sendMessage(pubsub_ChangeFrameTitle,
                        NewTitle=p4R.Application_name + " - " + 'New Project')
        self.update_Btn.SetFocus()
        self.Fit()
        self.Layout()

    def on_load(self, b=None):
        a = P4Rm()
        for ii in self.data_fields:
            self.data_fields[ii].Clear()
        if b == 1:
            for i in range(len(New_project_initial)):
                p_ = New_project_initial[i]
                self.data_fields[i].AppendText(str(p_))
        else:
            i = 0
            for k in p4R.IP_p:
                self.data_fields[i].AppendText(str(a.AllDataDict[k]))
                i += 1

            val = self.symmetry_choice[int(float(a.AllDataDict
                                           ['crystal_symmetry']))]
            self.cb_crystalsymmetry.SetStringSelection(val)
            self.on_select_symmetry(None, val)

            self.modelCalc = a.AllDataDict['model']
            self.cb_strainname.SetSelection(int(float(a.AllDataDict['model'])))
            self.cb_dwname.SetSelection(int(float(a.AllDataDict['model'])))

            self.dwBfunction.SetItems(self.dwBfunction_choice)
            self.dwBfunction.SetStringSelection(self.dwBfunction_choice[0])

            indexx = a.crystal_list.index(a.PathDict['Compound_name'])
            self.cb_crystalname.SetStringSelection(a.crystal_list[indexx])


            funky = int(float(a.AllDataDict['function_profile']))
            self.cb_fitfunction.SetStringSelection(p4R.FitFunction[funky])
            self.on_change_function(None, p4R.FitFunction[funky])
            P4Rm.ParamDict['func_profile'] = p4R.FitFunction_choice[funky]

            self.on_update_sp_DW()
            self.update_Btn.Enable()
            self.update_Btn.SetFocus()
            self.load_data = 1
            self.load_init = 1

    def on_change_update_button_state(self):
        self.update_Btn.Enable()
        self.update_Btn.SetFocus()
        self.load_data = 1
        self.load_init = 1

    def on_test_some_field(self):
        self.on_test_model()
        self.on_check_data_value()

    def on_update(self, event=None):
        a = P4Rm()
        try:
            if not a.ParamDict['th'].any():
                return
            else:
                sym_name = self.cb_crystalsymmetry.GetStringSelection()
                sym_num = self.symmetry_choice.index(sym_name)
                P4Rm.AllDataDict['crystal_symmetry'] = int(sym_num)
                b = Calcul4Radmax()
                b.on_update()
        except AttributeError:
            pass

    def on_update_panel(self):
        a = P4Rm()
        self.DW_horizontal_ctrl.SetLabel(str(a.ParamDict['DW_multiplication']))
        self.strain_horizontal_ctrl.SetLabel(str(a.ParamDict['strain_multiplication']))

    def on_change_material(self, event):
        P4Rm.PathDict['Compound_name'] = event.GetString()
        self.on_update(event)

    def on_change_DW(self, event):
        self.dwBfunction_hide.SetValue(event.GetString())
        self.on_update(event)

    def read_crystal_list(self):
        a = P4Rm()
        self.cb_crystalname.SetItems(a.crystal_list)
        self.cb_crystalname.SetStringSelection(a.crystal_list[0])

    def OnChangeBasisFunction_(self, tmp):
        self.dwBfunction.SetItems(tmp[0])
        self.damaged_depth.SetValue(str(tmp[2]))
        self.dwBfunction.SetValue(str(tmp[3]))
        self.Nb_slice.SetValue(str(tmp[4]))
        val = float(self.StrainBfunction.GetValue())
        P4Rm.AllDataDict['strain_basis_func'] = int(val)
        self.dwBfunction_hide.SetValue(str(tmp[3]))
        P4Rm.AllDataDict['dw_basis_func'] = int(tmp[3])

    def on_change_function(self, event=None, choice=None):
        a = P4Rm()
        if choice is not None:
            func = choice
            funky = p4R.FitFunction.index(func)
        else:
            func = event.GetString()
            funky = p4R.FitFunction.index(func)
        if func == "Gaussian" or func == "Lorentzian":
            l = ["S", "S", "H", "H", "H", "H", "H", "H", "H", "H"]
        elif func == "Pseudo-Voigt":
            l = ["S", "S", "H", "H", "S", "S", "H", "H", "H", "H"]
        elif func == "Generalized bell":
            l = ["S", "S", "H", "H", "H", "H", "H", "H", "S", "S"]
            self.b_bell.SetValue(str(a.AllDataDict['b_bell']))
        elif func == "Split-PV":
            l = ["S", "S", "S", "S", "S", "S", "S", "S", "H", "H"]
            self.fwhmr.SetValue(str(a.AllDataDict['width_right']))
            self.shaper.SetValue(str(a.AllDataDict['shape_right']))
        for i in range(len(self.func_list)):
            if l[i] is "S":
                self.func_list[i].Show()
            elif l[i] is "H":
                self.func_list[i].Hide()
        if func == "Split-PV":
            self.fwhml_txt.SetLabel(u'Width left (°)')
            self.shapel_txt.SetLabel(u'Shape left')
        else:
            self.fwhml_txt.SetLabel(u'Width (°)')
            self.shapel_txt.SetLabel(u'Shape')
        P4Rm.AllDataDict['function_profile'] = funky
        P4Rm.ParamDict['func_profile'] = p4R.FitFunction_choice[funky]
        self.Layout()
#        wx.Yield()
        if choice is None:
            self.on_update(event)

    def key_pressed(self, event, case):
        """
        ctrl+U update bouton
        ctrl+I recharge le dernier projet
        """
        a = P4Rm()
        if case == 0:
            self.on_update(event)
        elif case == 1:
            if a.PathDict['project_name'] != "":
                paths = a.PathDict['path2inicomplete']
                b = Calcul4Radmax()
                b.on_load_project(paths)
                logger.log(logging.INFO, "File has been reloaded by shortcut")

    def on_select_symmetry(self, event=None, choice=None):
        """
        Symmetry combobox selection
        choice selection according to the symmetry condition
        E=Enable, D=Disable
        """
        if choice is not None:
            i = choice
        else:
            i = event.GetString()

        cubique_text_state = ["E", "D", "D", "D", "D", "D"]
        cubique_text_value = ["None", 0, 0, 90, 90, 90]

        hexa_text_state = ["E", "D", "E", "D", "D", "D"]
        hexa_text_value = ["None", 0, "None", 90, 90, 120]

        tetra_text_state = ["E", "D", "E", "D", "D", "D"]
        tetra_text_value = ["None", 0, "None", 90, 90, 90]

        ortho_text_state = ["E", "E", "E", "D", "D", "D"]
        ortho_text_value = ["None", 0, "None", 90, 90, 90]

        rhombo_text_state = ["E", "D", "D", "E", "D", "D"]
        rhombo_text_value = ["None", 0, 0, "None", 3, 3]

        mono_text_state = ["E", "E", "E", "D", "E", "D"]
        mono_text_value = ["None", "None", "None", 90, "None", 90]

        tri_text_state = ["E", "E", "E", "E", "E", "E"]
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

        for i in range(6):
            if temp_state[i] == "E":
                self.paramcell[i].Enable()
            else:
                self.paramcell[i].Disable()
            if i in range(0, 3):
                if temp_value[i] != "None":
                    val = self.paramcell[temp_value[i]].GetValue()
                    self.paramcell[i].SetValue(str(val))
            elif i in range(3, 6):
                if temp_value[i] != "None":
                    if temp_value[i] == 90 or temp_value[i] == 120:
                        self.paramcell[i].Clear()
                        self.paramcell[i].SetValue(str(temp_value[i]))
                    elif temp_value[i] == 3:
                        self.paramcell[i].Clear()
                        temp = str(self.paramcell[temp_value[i]].GetValue())
                        self.paramcell[i].SetValue(temp)

    def on_read_data_field(self, case=None):
        """
        lecture des champs
        test si float
        """
        P4Rm.checkInitialField = 0
        check_empty = self.on_search_empty_fields()
        if check_empty is True:
            data_float = self.is_data_float()
            if data_float is True:
                P4Rm.checkInitialField = 1

    def on_apply_color_field(self, color):
        """
        permet de changer la couleur des champs lors du lancement du fit
        bleu: sauvegarde des données
        wx.NullColour= si white alors le textctrl scintille apres à chaque
        update
        """
        if color == (255, 255, 255):
            color = wx.NullColour
        for ii in range(len(self.data_fields)):
            self.data_fields[ii].SetBackgroundColour(color)
        self.Refresh()

    def on_change_color_damaged_depth(self, color):
        self.damaged_depth.SetBorderColour(color)
        self.Refresh()

    def on_check_data_value(self):
        """
        Check if some data are not off limit for the program
        """
        a = P4Rm()
        if a.AllDataDict['width_left'] == 0:
            P4Rm.AllDataDict['width_left'] = 1e-4
            self.data_fields[1].Clear()
            self.data_fields[1].AppendText(str(a.AllDataDict['width_left']))
        if a.AllDataDict['shape_left'] <= 0:
            P4Rm.AllDataDict['shape_left'] = 1e-5
            self.data_fields[2].Clear()
            self.data_fields[2].AppendText(str(a.AllDataDict['shape_left']))
        elif a.AllDataDict['shape_left'] > 1:
            P4Rm.AllDataDict['shape_left'] = 1
            self.data_fields[2].Clear()
            self.data_fields[2].AppendText(str(a.AllDataDict['shape_left']))
        else:
            return
        self.Refresh()

    def on_launch_calc4Fit(self, event):
        a = P4Rm()
        if (a.ParamDict['Iobs'] == [] or
           a.ParamDict['sp'] == [] or
           a.ParamDict['dwp'] == []):
            return
        else:
            self.empty_field = 1
            self.not_a_float = 1
            check_empty = self.search4emptyfields()
            if check_empty:
                data_float = self.is_data_float()
                if data_float:
                    self.empty_field = 0
                    self.on_calcul_parameters()
                    self.Fit()
                    self.Layout()
                    P4Rm.success4Fit = 0
                else:
                    P4Rm.success4Fit = 1
            else:
                P4Rm.success4Fit = 1
            self.empty_field = 0
            self.not_a_float = 0

    def on_update_scale(self, event):
        widget = event.GetId()
        if widget == self.m_strain_ID:
            pub.sendMessage(pubsub_Update_Scale_Strain, event=event,
                            val=float(self.strain_horizontal_ctrl.GetValue()))
        elif widget == self.m_DW_ID:
            pub.sendMessage(pubsub_Update_Scale_DW, event=event,
                            val=float(self.DW_horizontal_ctrl.GetValue()))

    def on_select_strain_Dw_name(self, event):
        a = P4Rm()
        bsplinename = event.GetString()
        self.modelCalc = p4R.Strain_DW_choice.index(bsplinename)
        self.modelChoice.Clear()
        self.modelChoice.AppendText(str(self.modelCalc))
        t = int(a.AllDataDict['model'])
        P4Rm.AllDataDict['model'] = self.modelCalc

        if bsplinename == "Asymmetric pv":
            self.on_hide_show_eta(True)
            self.StrainBfunction.Disable()
            self.cb_strainname.SetSelection(2)
            self.cb_dwname.SetSelection(2)
            P4Rm.ParamDict['strain_sm_ab_bkp'] = a.AllDataDict['strain_basis_func']
            P4Rm.ParamDict['dw_sm_ab_bkp'] = a.AllDataDict['dw_basis_func']
            P4Rm.ParamDict['sp_' + p4R.Bsplinesave[t]] = a.ParamDict['sp']
            P4Rm.ParamDict['dwp_' + p4R.Bsplinesave[t]] = a.ParamDict['dwp']
            P4Rm.ParamDict['sp'] = a.ParamDict['sp_pv']
            P4Rm.ParamDict['dwp'] = a.ParamDict['dwp_pv']
            P4Rm.ParamDict['state_sp'] = 7*[True]
            P4Rm.ParamDict['state_dwp'] = 7*[True]

        else:
            self.on_hide_show_eta(False)
            self.StrainBfunction.Enable()
            self.cb_strainname.SetSelection(0)
            self.cb_dwname.SetSelection(0)
            if bsplinename == "B-splines smooth":
                P4Rm.ParamDict['sp_' + p4R.Bsplinesave[t]] = a.ParamDict['sp']
                P4Rm.ParamDict['dwp_' + p4R.Bsplinesave[t]] = a.ParamDict['dwp']
                P4Rm.ParamDict['sp'] = a.ParamDict['sp_smooth']
                P4Rm.ParamDict['dwp'] = a.ParamDict['dwp_smooth']
            elif bsplinename == "B-splines abrupt":
                P4Rm.ParamDict['sp_' + p4R.Bsplinesave[t]] = a.ParamDict['sp']
                P4Rm.ParamDict['dwp_' + p4R.Bsplinesave[t]] = a.ParamDict['dwp']
                P4Rm.ParamDict['sp'] = a.ParamDict['sp_abrupt']
                P4Rm.ParamDict['dwp'] = a.ParamDict['dwp_abrupt']
            P4Rm.FitDict['New&Load'] = 1
            P4Rm.AllDataDict['strain_basis_func'] = a.ParamDict['strain_sm_ab_bkp']
            P4Rm.AllDataDict['dw_basis_func'] = a.ParamDict['dw_sm_ab_bkp']

            P4Rm.ParamDict['state_sp'] = len(a.ParamDict['sp'])*[True]
            P4Rm.ParamDict['state_dwp'] = len(a.ParamDict['dwp'])*[True]

        self.StrainBfunction.SetValue(str(a.AllDataDict['strain_basis_func']))
        self.dwBfunction_hide.SetValue(str(a.AllDataDict['dw_basis_func']))
        self.on_test_model()
        self.on_update(event)

    def on_hide_show_eta(self, state):
        for i in range(len(self.Textcontrolhide)):
            self.Textcontrolhide[i].Show(state)
        if state:
            self.eta_txt.SetLabelText(self.eta_txt_label)
        else:
            self.eta_txt.SetLabelText("")
        self.Layout()

    def on_update_sp_DW(self):
        a = P4Rm()        
        for i in range(len(self.Textcontrolhide)):
            self.Textcontrolhide[i].Clear()
        roundval = 3
        self.eta_strain_1.AppendText(str(round(a.ParamDict['sp'][4],
                                               roundval)))
        self.eta_strain_2.AppendText(str(round(a.ParamDict['sp'][5],
                                               roundval)))
        self.eta_dw_1.AppendText(str(round(a.ParamDict['dwp'][4],
                                           roundval)))
        self.eta_dw_2.AppendText(str(round(a.ParamDict['dwp'][5],
                                           roundval)))

    def on_read_sp_DW(self):
        a = P4Rm()
        P4Rm.ParamDict['sp'][4] = self.eta_strain_1.GetValue()
        P4Rm.ParamDict['sp'][5] = self.eta_strain_2.GetValue()
        P4Rm.ParamDict['dwp'][4] = self.eta_dw_1.GetValue()
        P4Rm.ParamDict['dwp'][5] = self.eta_dw_2.GetValue()
        P4Rm.ParamDict['sp'] = [float(r) for r in a.ParamDict['sp']]
        P4Rm.ParamDict['dwp'] = [float(r) for r in a.ParamDict['dwp']]

    def on_test_model(self):
        val = 7.0
        model = int(float(self.modelChoice.GetValue()))
        if model == 2:
            self.on_hide_show_eta(True)
            P4Rm.AllDataDict['strain_basis_func'] = val
            P4Rm.AllDataDict['dw_basis_func'] = val
            self.StrainBfunction.Clear()
            self.StrainBfunction.AppendText(str(val))
            self.StrainBfunction.Disable()
            self.dwBfunction_hide.Clear()
            self.dwBfunction_hide.AppendText(str(val))
            temp = [str(val)]
            self.dwBfunction.SetItems(temp)
            self.dwBfunction.SetStringSelection(temp[0])

            self.cb_strainname.SetSelection(2)
            self.cb_dwname.SetSelection(2)
            P4Rm.modelPv = True
            self.on_read_sp_DW()
        else:
            self.on_hide_show_eta(False)
            self.StrainBfunction.Enable()
            self.cb_strainname.SetSelection(model)
            self.cb_dwname.SetSelection(model)
            P4Rm.modelPv = False

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
            color = (255, 0, 0)
            for ii in empty_fields:
                self.data_fields[ii].SetBackgroundColour('red')
            self.Refresh()
            msg = "Please, fill the red empty fields to continue"
            dlg = GMD.GenericMessageDialog(None, msg,
                                           "Attention", agwStyle=wx.OK |
                                           wx.ICON_INFORMATION)
            dlg.ShowModal()
            color = wx.NullColour
            for ii in empty_fields:
                self.data_fields[ii].SetBackgroundColour(color)
            self.Refresh()
        return check_empty

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def is_data_float(self):
        a = P4Rm()
        IsFloat = []
        dataFloat = True
        P4Rm.ProjectFileData = []
        for i in range(len(self.data_fields)):
            P4Rm.ProjectFileData.append(self.data_fields[i].GetValue())
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
            P4Rm.initial_parameters = [float(ii) for ii in a.ProjectFileData]
            P4Rm.PathDict['Compound_name'] = self.cb_crystalname.GetStringSelection()
            P4Rm.spline_strain = self.cb_strainname.GetSelection()
            P4Rm.spline_DW = self.cb_dwname.GetSelection()
        return dataFloat


# -----------------------------------------------------------------------------
class myTextCtrl(wx.Panel):
    def __init__(self, parent, id, size):
        wx.Panel.__init__(self, parent, id=-1)
        self.ed = wx.TextCtrl(self, -1, "",
                              style=wx.TE_PROCESS_ENTER | wx.NO_BORDER,
                              size=size,
                              validator=TextValidator(DIGIT_ONLY))
        self.Bind(wx.EVT_TEXT_ENTER, self.on_press_enter, self.ed)
        self.change_color_border = False
        self.color = wx.Colour(255, 255, 255)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def on_press_enter(self, event):
        pub.sendMessage(pubsub_update_from_damaged)

    def OnSize(self, event):
        size = event.GetSize()
        self.ed.SetPosition((1, 1))
        self.ed.SetSize((size.x-2, size.y-2))
        event.Skip()

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        pen = wx.Pen(self.color, 10, wx.SOLID)
        pen.SetJoin(wx.JOIN_MITER)
        dc.SetBackground(wx.Brush(self.color, style=wx.BRUSHSTYLE_SOLID))
        dc.SetPen(pen)
        dc.Clear()

    def SetBackgroundColour(self, cor):
        self.ed.SetBackgroundColour(cor)

    def SetForegroundColour(self, cor):
        self.ed.SetForegroundColour(cor)

    def SetBorderColour(self, color):
        self.color = color
        self.Refresh()

    def SetFont(self, font):
        self.ed.SetFont(font)

    def Clear(self):
        self.ed.Clear()

    def AppendText(self, val):
        self.ed.AppendText(val)

    def GetValue(self):
        return self.ed.GetValue()

    def SetValue(self, val):
        self.ed.SetValue(val)
