#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

'''
*Radmax Initial Parameters module*
'''

from Read4Radmax import ReadFile, SaveFile4Diff
from Parameters4Radmax import *
from def_strain import f_strain, old2new_strain, fit_input_strain
from def_DW import f_DW, old2new_DW, fit_input_DW
from def_XRD import f_ReflDict
from def_Fh import f_FH
from sys import platform as _platform

ALPHA_ONLY = 1
DIGIT_ONLY = 2

"""New Project initial data"""
New_project_initial = [1.48806, 0.013, 0.000001, 5e-6, 1, 1, 0, 0, 5.4135,
                       5.4135, 5.4135, 90, 90, 90, 0, 10, 10, 3500, 70]
sp_pv_initial = [2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.05]
dwp_pv_initial = [0.5, 0.2, 0.1, 0.1, 0.1, 0.1, 0.85]
New_project_initial_size = range(len(New_project_initial))
New_project_initial_data = dict(zip(New_project_initial_size,
                                    New_project_initial))

"""Pubsub message"""
pubsub_Launch_GUI = "LaunchGUI"

pubsub_Load_fitting_panel = "LoadFittingPanel"
pubsub_Load = "LoadP"
pubsub_New = "NewP"
pubsub_LoadXRD = "LoadXRD"
pubsub_LoadStrain = "LoadStrain"
pubsub_LoadDW = "LoadDW"
pubsub_Save = "SaveP"
pubsub_ChangeFrameTitle = "ChangeFrameTitle"
pubsub_Draw_XRD = "DrawXRD"
pubsub_Draw_Strain = "DrawStrain"
pubsub_Draw_DW = "DrawDW"
pubsub_Read_field_paramters_panel = "ReadParametersPanel"
pubsub_Re_Read_field_paramters_panel = "ReReadParametersPanel"
pubsub_notebook_selection = "NotebookSelection"
pubsub_Activate_Import = "ActivateImport"
pubsub_Update_Fit_Live = "UpdateFitLive"
pubsub_OnFit_Graph = "OnFitGraph"
pubsub_Draw_Fit_Live_Deformation = "DrawFitLiveDeformation"
pubsub_Read_field4Save = "ReadField4Save"
pubsub_changeColor_field4Save = "ChangeColorField4Save"
pubsub_Update_deformation_multiplicator_coef = "UpdateDefMultiplicatorCoef"
pubsub_save_project_before_fit = "SaveProjectBeforeFit"
pubsub_gauge_to_zero = "Gauge2zero"
pubsub_shortcut = "Shortcut"
pubsub_On_Limit_Before_Graph = "OnLimitBeforeGraph"
pubsub_Update_Scale_Strain = "on_update_scaleStrain"
pubsub_Update_Scale_DW = "on_update_scaleDW"
pubsub_Permute_Graph = "PermuteGrpah"
pubsub_Read_sp_dwp = "ReadSpDwp"


# ------------------------------------------------------------------------------
class InitialDataPanel(wx.Panel):
    """
    Initial Parameters main panel
    we built the all page in this module
    """
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar
        self.parent = parent
#       self.parent.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.on_page_changed)
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)

        size_text = (85, 22)
        size_value_hkl = (50, 22)
        size_value_lattice = (65, 22)
        size_damaged_depth = (110, 22)
        size_scale = (50, 22)

        if _platform == "linux" or _platform == "linux2":
            size_StaticBox = (950, 140)
            crystal_combobox = (110, -1)
            symmetry_combobox = (90, -1)
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
            symmetry_combobox = (80, -1)
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
            symmetry_combobox = (80, -1)
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
        self.wavelength = wx.TextCtrl(self, size=size_text,
                                      validator=TextValidator(DIGIT_ONLY))
        self.wavelength.SetFont(font_TextCtrl)

        resolution_txt = wx.StaticText(self, -1, label=u'Resolution (°)',
                                       size=(90, vStatictextsize))
        resolution_txt.SetFont(font_Statictext)
        self.resolution = wx.TextCtrl(self, size=size_text,
                                      validator=TextValidator(DIGIT_ONLY))
        self.resolution.SetFont(font_TextCtrl)

        shape_txt = wx.StaticText(self, -1, label=u'Shape',
                                  size=(45, vStatictextsize))
        shape_txt.SetFont(font_Statictext)
        self.shape = wx.TextCtrl(self, size=size_text,
                                 validator=TextValidator(DIGIT_ONLY))
        self.shape.SetFont(font_TextCtrl)

        bckground_txt = wx.StaticText(self, -1, label=u'Background',
                                      size=(75, vStatictextsize))
        bckground_txt.SetFont(font_Statictext)
        self.bckground = wx.TextCtrl(self, size=size_text,
                                     validator=TextValidator(DIGIT_ONLY))
        self.bckground.SetFont(font_TextCtrl)

        in_Experiment_box_sizer.Add(wavelength_txt, pos=(0, 0),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.wavelength, pos=(0, 1),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(resolution_txt, pos=(0, 2),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.resolution, pos=(0, 3),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(shape_txt, pos=(0, 4),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.shape, pos=(0, 5),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(bckground_txt, pos=(0, 6),
                                    flag=flagSizer)
        in_Experiment_box_sizer.Add(self.bckground, pos=(0, 7),
                                    flag=flagSizer)

        Experiment_box_sizer.Add(in_Experiment_box_sizer, 0, wx.ALL, 5)

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
#        style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE|wx.TE_PROCESS_ENTER

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
                                       size=(65, vStatictextsize))
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

        self.Strain_DW_choice = ["B-splines smooth", "B-splines abrupt",
                                 "Asymmetric pv"]
#        self.modelChoice = 0:"B-splines smooth", 1:"B-splines abrupt",
#                                 2:"B-splines pv", 3:"B-splines histogram"

        strainname_txt = wx.StaticText(self, self.Strainname_ID,
                                       label=u'Strain: model',
                                       size=(85, vStatictextsize))
        strainname_txt.SetFont(font_Statictext)
        self.cb_strainname = wx.ComboBox(self, pos=(50, 30),
                                         choices=self.Strain_DW_choice,
                                         style=wx.CB_READONLY)
        self.cb_strainname.SetStringSelection(self.Strain_DW_choice[0])
        self.cb_strainname.SetFont(font_combobox)

        dwname_txt = wx.StaticText(self, self.dwname_ID, label=u'DW: model',
                                   size=(75, vStatictextsize))
        dwname_txt.SetFont(font_Statictext)
        self.cb_dwname = wx.ComboBox(self, pos=(50, 30),
                                     choices=self.Strain_DW_choice,
                                     style=wx.CB_READONLY)
        self.cb_dwname.SetStringSelection(self.Strain_DW_choice[0])
        self.cb_dwname.SetFont(font_combobox)

        self.cb_strainname.Bind(wx.EVT_COMBOBOX, self.on_select_strain_Dw_name)
        self.cb_dwname.Bind(wx.EVT_COMBOBOX, self.on_select_strain_Dw_name)

        self.StrainBfunction_ID = wx.NewId()
        self.dwBfunction_ID = wx.NewId()

        StrainBfunction_txt = wx.StaticText(self, id=self.StrainBfunction_ID,
                                            label=u'Basis functions',
                                            size=(95, vStatictextsize))
        StrainBfunction_txt.SetFont(font_Statictext)
        self.StrainBfunction = wx.TextCtrl(self, size=size_value_lattice,
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
                                          size=(115, vStatictextsize))
        damaged_depth_txt.SetFont(font_Statictext)
        self.damaged_depth = wx.TextCtrl(self, size=size_damaged_depth,
                                         validator=TextValidator(DIGIT_ONLY))
        self.damaged_depth.SetFont(font_TextCtrl)

        Nb_slice_txt = wx.StaticText(self, -1,
                                     label=u'Number of slices',
                                     size=(95, vStatictextsize))
        Nb_slice_txt.SetFont(font_Statictext)
        self.Nb_slice = wx.TextCtrl(self, size=size_value_lattice,
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
        self.update_Btn.SetFocus()

        self.Textcontrolhide = [self.eta_strain_1, self.eta_strain_2,
                                self.eta_dw_1, self.eta_dw_2]
        for i in range(len(self.Textcontrolhide)):
            self.Textcontrolhide[i].Show(False)
        self.eta_txt.SetLabelText("")

        self.Textcontrol = [self.wavelength, self.resolution, self.shape,
                            self.bckground, self.h_direction, self.k_direction,
                            self.l_direction, self.symmetry_txt_hide,
                            self.a_param, self.b_param, self.c_param,
                            self.alpha_param, self.beta_param,
                            self.gamma_param, self.modelChoice,
                            self.StrainBfunction, self.dwBfunction_hide,
                            self.damaged_depth, self.Nb_slice]

        Textcontrolen = range(len(self.Textcontrol))
        self.data_fields = dict(zip(Textcontrolen, self.Textcontrol))
        self.data_fields_dict = []
        self.folder_paths_dict = []

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

        pub.subscribe(self.on_load_project, pubsub_Load)
        pub.subscribe(self.on_new_project, pubsub_New)
        pub.subscribe(self.on_load_XRD, pubsub_LoadXRD)
        pub.subscribe(self.on_load_strain, pubsub_LoadStrain)
        pub.subscribe(self.on_load_DW, pubsub_LoadDW)
        pub.subscribe(self.on_launch_calc4Fit,
                      pubsub_Read_field_paramters_panel)
        pub.subscribe(self.on_update, pubsub_Re_Read_field_paramters_panel)
        pub.subscribe(self.on_update_from_drag_and_drop,
                      pubsub_Update_Fit_Live)
        pub.subscribe(self.on_save_project, pubsub_Save)
        pub.subscribe(self.on_save_project, pubsub_save_project_before_fit)
        pub.subscribe(self.on_reset_deformation_multiplication,
                      pubsub_Update_deformation_multiplicator_coef)
        pub.subscribe(self.initialization, pubsub_Launch_GUI)
        pub.subscribe(self.f_strain_DW, pubsub_Draw_Fit_Live_Deformation)
        pub.subscribe(self.key_pressed, pubsub_shortcut)
        pub.subscribe(self.limit_reach, pubsub_On_Limit_Before_Graph)
        pub.subscribe(self.on_read_sp_DW, pubsub_Read_sp_dwp)

        self.SetSizer(mastersizer)

    def initialization(self):
        b = ReadFile(self)
        b.on_read_init_parameters(os.path.join(current_dir, filename + '.ini'),
                                  ConfigFile)
        config_File_extraction = b.read_result_value()

        self.folder_paths_dict = dict(zip(Folder_paths_key,
                                          config_File_extraction[2:]))
        i = 2
        a = P4Radmax()
        for k, v in a.DefaultDict.items():
            P4Radmax.DefaultDict[k] = config_File_extraction[i]
            i += 1
        for k, v in FitParamDefault.items():
            if k == 'maxfev':
                P4Radmax.DefaultDict[k] = int(float(a.DefaultDict[k]))
            else:
                P4Radmax.DefaultDict[k] = float(a.DefaultDict[k])
        self.read_crystal_list()
        self.on_new_project()

    def key_pressed(self, event, case):
        """ctrl+U emulate the update button
        ctrl+I reload the last open project"""
        a = P4Radmax()
        if case == 0:
            self.on_update(event)
        elif case == 1:
            if a.PathDict['project_name'] != "":
                a = P4Radmax()
                for ii in self.data_fields:
                    self.data_fields[ii].Clear()
                paths = a.PathDict['path2inicomplete']
                self.on_reset_deformation_multiplication()
                self.on_read_data_loaded(event, paths)
                logger.log(logging.INFO, "File has been reloaded by shortcut")

    def on_change_DW(self, event):
        self.dwBfunction_hide.SetValue(event.GetString())

    def read_crystal_list(self):
        """
        Reading of the structures directory
        we list all the files present in this directory
        we get back the files name, sort them by name
        and used them in the crsytal combobox
        """
        if os.listdir(structures_name) != []:
            self.crystal_choice = sorted(list(os.listdir(structures_name)))
            self.cb_crystalname.SetItems(self.crystal_choice)
            self.cb_crystalname.SetStringSelection(self.crystal_choice[0])

    def on_select_symmetry(self, event, choice=None):
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

        for i in range(6):
            if temp_state[i] == "Enable":
                self.data_fields[8+i].Enable()
            else:
                self.data_fields[8+i].Disable()
            if i in range(0, 3):
                if temp_value[i] != "None":
                    self.data_fields[8+i].SetValue(str(self.data_fields[8 +
                                                   temp_value[i]].GetValue()))
            elif i in range(3, 6):
                if temp_value[i] != "None":
                    if temp_value[i] == 90 or temp_value[i] == 120:
                        self.data_fields[8+i].Clear()
                        self.data_fields[8+i].SetValue(str(temp_value[i]))
                    elif temp_value[i] == 3:
                        self.data_fields[8+i].Clear()
                        temp = str(self.data_fields[8 +
                                   temp_value[i]].GetValue())
                        self.data_fields[8+i].SetValue(temp)

    def on_new_project(self, event=None):
        """
        Launch new project with default inital parameters
        all variables are initialized and graph are eventually removed
        """
        a = P4Radmax()
        self.on_reset_deformation_multiplication()
        for ii in self.data_fields:
            self.data_fields[ii].Clear()
        for i in range(len(self.data_fields)):
            self.data_fields[i].AppendText(str(New_project_initial_data[i]))

        self.cb_strainname.SetSelection(0)
        self.cb_dwname.SetSelection(0)
        self.on_hide_show_eta(False)

        success = self.on_read_data_field()
        if success:
            pub.sendMessage(pubsub_ChangeFrameTitle,
                            NewTitle=Application_name + " - " + 'New Project')
            self.statusbar.SetStatusText(u"", 0)
            i = 0
            for k, v in a.DataDict.items():
                try:
                    P4Radmax.DataDict[k] = a.initial_parameters[i]
                    i += 1
                except (IndexError):
                    break

            val = self.symmetry_choice[int(float(a.DataDict
                                       ['crystal_symmetry']))]
            self.cb_crystalsymmetry.SetStringSelection(val)
            self.on_select_symmetry(event, val)

            P4Radmax.ParamDict['slice_backup'] = a.DataDict['number_slices']
            P4Radmax.ParamDict['strain_basis'] = (a.DataDict
                                                  ['strain_basis_func'])
            P4Radmax.ParamDict['dw_basis'] = a.DataDict['dw_basis_func']
            P4Radmax.ParamDict['damaged_value_backup'] = (a.DataDict
                                                          ['damaged_depth'])

            self.dwBfunction_choice = [str(a.ParamDict['strain_basis'])]
            self.dwBfunction.SetItems(self.dwBfunction_choice)
            self.dwBfunction.SetStringSelection(self.dwBfunction_choice[0])
            self.cb_crystalname.SetStringSelection(self.crystal_choice[0])

            P4Radmax.ParamDict['t_l'] = (a.DataDict['damaged_depth'] /
                                         a.DataDict['number_slices'])
            P4Radmax.ParamDict['z'] = (arange(a.DataDict['number_slices']+1) *
                                       a.ParamDict['t_l'])
            P4Radmax.ParamDict['depth'] = (a.DataDict['damaged_depth'] -
                                           a.ParamDict['z'])
            P4Radmax.ParamDict['sp'] = int(a.DataDict
                                           ['strain_basis_func'])*[1]
            P4Radmax.ParamDict['dwp'] = int(a.DataDict['dw_basis_func'])*[1]
            P4Radmax.ParamDict['sp_abrupt'] = int(a.DataDict
                                                  ['strain_basis_func'])*[1]
            P4Radmax.ParamDict['dwp_abrupt'] = int(a.DataDict
                                                   ['dw_basis_func'])*[1]
            P4Radmax.ParamDict['sp_pv'] = sp_pv_initial
            P4Radmax.ParamDict['dwp_pv'] = dwp_pv_initial
            P4Radmax.ParamDict['sp_bspline'] = a.ParamDict['sp']
            P4Radmax.ParamDict['dwp_bspline'] = a.ParamDict['dwp']

            pub.sendMessage(pubsub_Load_fitting_panel, data=None, b=1)
            pub.sendMessage(pubsub_Draw_XRD, b=2)
            pub.sendMessage(pubsub_Activate_Import)
            self.calc_strain()
            self.calc_DW()
            spline_strain = self.cb_strainname.GetSelection()
            spline_DW = self.cb_dwname.GetSelection()
            nb_slice, dw_func = self.OnChangeBasisFunction(
                                a.DataDict['strain_basis_func'],
                                a.DataDict['dw_basis_func'],
                                spline_strain, spline_DW,
                                a.DataDict['number_slices'])

            P4Radmax.PathDict['Compound_name'] = (self.cb_crystalname.
                                                  GetStringSelection())

            pub.sendMessage(pubsub_gauge_to_zero)
            self.update_Btn.SetFocus()
            self.Fit()
            self.Layout()

    def on_load_XRD(self, event):
        """
        Loading and extracting of XRD data file with no default extension,
        but needed a two columns format file
        """
        a = P4Radmax()
        b = ReadFile(self)
        wildcard = "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Select one file",
            defaultDir=self.folder_paths_dict['XRD_file'],
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.folder_paths_dict['XRD_file'] = os.path.split(paths[0])[0]
            P4Radmax.PathDict['path2drx'] = paths[0]
            P4Radmax.PathDict['XRD_file'] = paths[0]
            self.on_on_update_config_file('XRD_file')
            dlg.Destroy()
            try:
                """READING XRD FILE"""
                self.on_reset_deformation_multiplication()
                b.read_xrd_file(paths[0])
                P4Radmax.ParamDict['Iobs'] = a.ParamDict['data_xrd'][1]
                minval = np.min(a.Iobs[np.nonzero(a.Iobs)])
                P4Radmax.ParamDict['Iobs'][a.Iobs == 0] = minval
                P4Radmax.ParamDict['Iobs'] = a.Iobs / a.Iobs.max()
                P4Radmax.ParamDict['th'] = ((a.ParamDict['data_xrd'][0]) *
                                            np.pi/360.)
                P4Radmax.ParamDict['th4live'] = 2*a.ParamDict['th']*180/np.pi

                P4Radmax.ParamDictbackup['Iobs'] = a.ParamDict['Iobs']
                P4Radmax.ParamDictbackup['th'] = ParamDict['th']

                pub.sendMessage(pubsub_Draw_XRD, b=1)
            except TypeError:
                logger.log(logging.WARNING, "!Please check your input file!")

    def on_load_strain(self, event):
        """
        Loading of Strain data file with no default extension,
        but needed a two columns format file
        """
        wildcard = "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Import Strain file",
            defaultDir=self.folder_paths_dict['Strain_file'],
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.folder_paths_dict['Strain_file'] = os.path.split(paths[0])[0]
            self.on_on_update_config_file('Strain_file')
            dlg.Destroy()
            try:
                self.calc_strain(paths, 0)
            except TypeError:
                logger.log(logging.WARNING, "!Please check your input file!")

    def on_load_DW(self, event):
        """
        Loading of DW data file with no default extension,
        but needed a two columns format file
        """
        wildcard = "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Import DW file",
            defaultDir=self.folder_paths_dict['DW_file'],
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.folder_paths_dict['DW_file'] = os.path.split(paths[0])[0]
            self.on_on_update_config_file('DW_file')
            dlg.Destroy()
            try:
                self.calc_DW(paths, 0)
            except TypeError:
                logger.log(logging.WARNING, "!Please check your input file!")

    def calc_strain(self, paths=None, choice=None):
        """
        Reading and calcul Strain coefficient
        """
        a = P4Radmax()
        b = ReadFile(self)
        spline_strain = self.cb_strainname.GetSelection()
        if choice == 0:
            data = b.read_strain_xy_file(paths[0])
            if spline_strain == 2:
                t = data[0].max()
                P4Radmax.ParamDict['t_l'] = t/a.DataDict['number_slices']
                P4Radmax.ParamDict['z'] = (arange(a.DataDict['number_slices'] +
                                           1) * a.ParamDict['t_l'])
                P4Radmax.ParamDict['depth'] = t - a.ParamDict['z']
            else:
                t = a.DataDict['damaged_depth']
            P4Radmax.ParamDict['sp'] = fit_input_strain(
                                        data, a.DataDict['strain_basis_func'],
                                        a.DataDict['damaged_depth'],
                                        spline_strain)
        else:
            t = a.DataDict['damaged_depth']
        P4Radmax.ParamDictbackup['sp'] = a.ParamDict['sp']
        P4Radmax.ParamDict['strain_basis'] = float(a.DataDict
                                                   ['strain_basis_func'])
        P4Radmax.ParamDict['strain_i'] = f_strain(
                                         a.ParamDict['z'], a.ParamDict['sp'],
                                         t, spline_strain)
        self.on_shifted_sp_curves(t)
        P4Radmax.from_calc_strain = 1
        self.draw_curves()
        if choice == 0:
            self.save_deformation('Strain_file', 'strain', a.ParamDict['sp'])
            self.save_deformation('Strain_file', 'strain', a.sp)

    def calc_DW(self, paths=None, choice=None):
        """
        Reading and calcul DW coefficient
        """
        a = P4Radmax()
        b = ReadFile(self)
        spline_DW = self.cb_dwname.GetSelection()
        if choice == 0:
            data = b.read_dw_xy_file(paths[0])
            if spline_DW == 2:
                t = data[0].max()
                P4Radmax.ParamDict['t_l'] = t/a.DataDict['number_slices']
                P4Radmax.ParamDict['z'] = (arange(a.DataDict['number_slices'] +
                                           1) * a.ParamDict['t_l'])
                P4Radmax.ParamDict['depth'] = t - a.ParamDict['z']
            else:
                t = a.DataDict['damaged_depth']
            P4Radmax.ParamDict['dwp'] = fit_input_DW(
                                        data, a.DataDict['dw_basis_func'],
                                        a.DataDict['damaged_depth'], spline_DW)
        else:
            t = a.DataDict['damaged_depth']
        P4Radmax.ParamDictbackup['dwp'] = a.ParamDict['dwp']
        P4Radmax.ParamDict['dw_basis'] = float(a.DataDict['strain_basis_func'])
        P4Radmax.ParamDict['DW_i'] = f_strain(
                                     a.ParamDict['z'], a.ParamDict['dwp'],
                                     t, spline_DW)
        self.on_shifted_dwp_curves(t)
        P4Radmax.from_calc_DW = 1
        self.draw_curves()
        if choice == 0:
            self.save_deformation('DW_file', 'DW', a.ParamDict['dwp'])
            self.save_deformation('DW_file', 'DW', a.dwp)

    def on_load_project(self, event):
        """
        Loading of project with '.ini' extension,
        format created for the RaDMax application
        """
        wildcard = "text file (*.ini)|*.ini|" \
                   "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Select ini file",
            defaultDir=self.folder_paths_dict['project_file'],
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            for ii in self.data_fields:
                self.data_fields[ii].Clear()
            paths = dlg.GetPaths()
            self.folder_paths_dict['project_file'] = os.path.split(paths[0])[0]
            self.on_on_update_config_file('project_file')
            dlg.Destroy()
            self.on_read_data_loaded(event, paths[0])

    def on_read_data_loaded(self, event, paths):
            a = P4Radmax()
            b = ReadFile(self)
            b.on_read_init_parameters(paths, ConfigDataFile)
            datafromini = b.read_result_value()
            P4Radmax.ProjectFileData = datafromini[4:]
            i = 0
            for k, v in a.AllDataDict.items():
                try:
                    P4Radmax.AllDataDict[k] = datafromini[i]
                    i += 1
                except (IndexError):
                    break
            i = 0
            for name in ['Compound_name', 'DW_file', 'Strain_file',
                         'XRD_file']:
                P4Radmax.PathDict[name] = datafromini[i]
                i += 1

            P4Radmax.PathDict['path2ini'] = os.path.split(paths)[0]
            P4Radmax.PathDict['path2inicomplete'] = paths
            P4Radmax.PathDict['namefromini'] = os.path.splitext(
                                               os.path.basename(paths))[0]
            if a.ProjectFileData == []:
                msg_ = ("Please, pay attention to your input files," +
                        "there are some mistakes in the data")
                dlg = GMD.GenericMessageDialog(None, msg_, "Attention",
                                               agwStyle=wx.OK |
                                               wx.ICON_INFORMATION)
                dlg.ShowModal()
            else:
                P4Radmax.PathDict['project_name'] = os.path.splitext(
                                                    os.path.basename(paths))[0]
                for i in range(len(self.data_fields)):
                    self.data_fields[i].AppendText(str(a.ProjectFileData[i]))

                success = self.on_read_data_field()
                if success:
                    i = 0
                    for k, v in a.DataDict.items():
                        try:
                            P4Radmax.DataDict[k] = a.initial_parameters[i]
                            i += 1
                        except (IndexError):
                            break

                    val = self.symmetry_choice[int(float(a.DataDict
                                                   ['crystal_symmetry']))]
                    self.cb_crystalsymmetry.SetStringSelection(val)
                    self.on_select_symmetry(event, val)

                    P4Radmax.ParamDict['slice_backup'] = (a.DataDict
                                                          ['number_slices'])
                    P4Radmax.ParamDict['damaged_value_backup'] = (a.DataDict['damaged_depth'])

                    self.modelCalc = a.DataDict['model']
                    P4Radmax.ParamDict['strain_basis'] = a.DataDict['strain_basis_func']
                    P4Radmax.ParamDict['dw_basis'] = a.DataDict['dw_basis_func']

                    self.dwBfunction_choice = [str(
                                                  a.ParamDict['strain_basis'])]
                    self.dwBfunction.SetItems(self.dwBfunction_choice)
                    self.dwBfunction.SetStringSelection(
                                                    self.dwBfunction_choice[0])

                    if a.PathDict['Compound_name'] in self.crystal_choice:
                        indexx = self.crystal_choice.index(
                                                   a.PathDict['Compound_name'])
                        self.cb_crystalname.SetStringSelection(
                                                   self.crystal_choice[indexx])
                        msg_ = "Config file successfully loaded"
                        logger.log(logging.INFO, msg_)
                    else:
                        msg_ = ("You need to add the proper strcuture" +
                                "to continue")
                        logger.log(logging.INFO, msg_)
                    '''change name of the main title window'''
                    P4Radmax.ParamDict['sp_pv'] = sp_pv_initial
                    P4Radmax.ParamDict['dwp_pv'] = dwp_pv_initial

                    data4Fitting = []
                    data4Fitting.append(a.AllDataDict['tmax'])
                    data4Fitting.append(a.AllDataDict['nb_cycle_max'])
                    data4Fitting.append(a.AllDataDict['nb_palier'])

                    pub.sendMessage(pubsub_ChangeFrameTitle,
                                    NewTitle=(Application_name +
                                              " - " +
                                              a.PathDict['project_name']))
                    pub.sendMessage(pubsub_Load_fitting_panel,
                                    data=data4Fitting)
                    pub.sendMessage(pubsub_Activate_Import)
                    pub.sendMessage(pubsub_OnFit_Graph, b=1)
                    pub.sendMessage(pubsub_gauge_to_zero)

                    self.update_Btn.SetFocus()
                    self.load_data = 1
                    self.load_init = 1
                    self.populate_default_dict()
                    self.on_launch_calc()

    def populate_default_dict(self):
        a = P4Radmax()
        for k, v in FitParamDefault.items():
            try:
                P4Radmax.DefaultDict[k] = float(a.AllDataDict[k])
            except (IndexError):
                break

    def on_on_update_config_file(self, folder):
        a = SaveFile4Diff(self)
        a.on_update_config_file(os.path.join(current_dir, filename + '.ini'),
                             self.folder_paths_dict[folder], folder)

    def save_deformation(self, case, name, data, supp=None):
        a = P4Radmax()
        if a.PathDict['project_name'] == "":
            name_ = 'temp_' + '_input_' + name + '_coeff.txt'
            path = os.path.join(self.folder_paths_dict[case], name_)
        else:
            name_ = (a.PathDict['project_name'] + '_input_' +
                     name + '_coeff.txt')
            path = os.path.join(self.folder_paths_dict['Save_as_file'], name_)
            if supp == 1:
                name_ = 'temp_' + '_input_' + name + '_coeff.txt'
                path2remove = os.path.join(self.folder_paths_dict[case], name_)
                if os.path.isfile(path2remove):
                    os.remove(path2remove)
        P4Radmax.PathDict[case] = path
        savetxt(path, data, fmt='%10.8f')

    def on_save_project(self, event, case):
        """
        Saving project, save or save as depending of the action
        """
        a = P4Radmax()
        if a.PathDict['project_name'] == "":
            case = 1
        wildcard = "data file (*.ini)|*.ini|" \
                   "All files (*.*)|*.*"
        textmessage = "Save file as ..."
        check = self.on_read_data_field(0)
        if check is True and a.checkDataField is 1:
            if (a.PathDict['DW_file'] is not "" or
               a.PathDict['Strain_file'] is not "" or
               a.PathDict['XRD_file'] is not ""):
                if case is 1:
                    defaultdir_ = self.folder_paths_dict['Save_as_file']
                    dlg = wx.FileDialog(self, message=textmessage,
                                        defaultDir=defaultdir_, defaultFile="",
                                        wildcard=wildcard, style=wx.SAVE)
                    if dlg.ShowModal() == wx.ID_OK:
                        paths = dlg.GetPaths()
                        self.folder_paths_dict['Save_as_file'] = os.path.split(paths[0])[0]
                        self.on_on_update_config_file('Save_as_file')
                        dlg.Destroy()
                        P4Radmax.PathDict['path2ini'] = os.path.split(paths[0])[0]
                        if _platform == "linux" or _platform == "linux2":
                            P4Radmax.PathDict['path2inicomplete'] = paths[0] + '.ini'
                        elif _platform == "win32":
                            P4Radmax.PathDict['path2inicomplete'] = paths[0]
                        P4Radmax.PathDict['namefromini'] = os.path.splitext(os.path.basename(paths[0]))[0]
                        P4Radmax.PathDict['project_name'] = a.PathDict['namefromini']
                    else:
                        return
                b = SaveFile4Diff(self)
                P4Radmax.allparameters = (a.initial_parameters +
                                          a.fitting_parameters)
                self.save_deformation('Strain_file', 'strain',
                                      a.ParamDict['sp'], 1)
                self.save_deformation('DW_file', 'DW', a.ParamDict['dwp'], 1)
                P4Radmax.AllDataDict['crystal_name'] = self.cb_crystalname.GetStringSelection()
                P4Radmax.AllDataDict['input_dw'] = a.PathDict['DW_file']
                P4Radmax.AllDataDict['input_strain'] = a.PathDict['Strain_file']
                P4Radmax.AllDataDict['xrd_data'] = a.PathDict['XRD_file']
                i = 0
                for name in Data4Radmax:
                    P4Radmax.AllDataDict[name] = a.allparameters[i]
                    i += 1
                for name in DefaultParam4Radmax[5:]:
                    P4Radmax.AllDataDict[name] = a.DefaultDict[name]
                b.save_project(case)
                for ii in range(len(self.data_fields)):
                    self.data_fields[ii].SetBackgroundColour('#CCE5FF')
                pub.sendMessage(pubsub_changeColor_field4Save, case=0)
                self.Refresh()
                wx.Yield()
                sleep(0.8)
                msg_ = ("Data have been saved to " +
                        a.PathDict['path2inicomplete'])
                logger.log(logging.INFO, msg_)
                for ii in range(len(self.data_fields)):
                    self.data_fields[ii].SetBackgroundColour('white')
                pub.sendMessage(pubsub_changeColor_field4Save, case=1)
                self.Refresh()
                wx.Yield()
                msg_ = (u"Data have been saved to " +
                        str(a.PathDict['path2inicomplete']))
                self.statusbar.SetStatusText(msg_, 0)
                pub.sendMessage(pubsub_ChangeFrameTitle,
                                NewTitle=Application_name + " - " +
                                a.PathDict['namefromini'])
            else:
                msg_ = "There is no data to save"
                dlg = GMD.GenericMessageDialog(None, msg_,
                                               "Attention", agwStyle=wx.OK |
                                               wx.ICON_INFORMATION)
                dlg.ShowModal()

    def on_read_data_field(self, case=None):
        msg_ = "Test if fields are full and contains float"
        logger.log(logging.INFO, msg_)
        check_empty = self.search4emptyfields()
        if check_empty is True:
            data_float = self.is_data_float()
            if data_float:
                msg_ = "Test pass successfully"
                logger.log(logging.INFO, msg_)
                if case is 0:
                    pub.sendMessage(pubsub_Read_field4Save)
                return True
            else:
                msg_ = "There are some problem in the data"
                logger.log(logging.WARNING, msg_)
                return False

    def on_check_data_value(self):
        """
        Check if some data are not off limit for the program
        """
        a = P4Radmax()
        if a.DataDict['resolution'] == 0:
            a.DataDict['resolution'] = 1e-4
            self.data_fields[1].Clear()
            self.data_fields[1].AppendText(str(a.DataDict['resolution']))
        if a.DataDict['shape'] <= 0:
            a.DataDict['shape'] = 1e-5
            self.data_fields[2].Clear()
            self.data_fields[2].AppendText(str(a.DataDict['shape']))
        if a.DataDict['shape'] > 1:
            a.DataDict['shape'] = 1
            self.data_fields[2].Clear()
            self.data_fields[2].AppendText(str(a.DataDict['shape']))

    def on_launch_calc(self):
        success = self.on_read_initial_file()
        if success:
            self.empty_field = 0
            self.on_calcul_parameters()
            self.Fit()
            self.Layout()

    def on_launch_calc4Fit(self, event):
        a = P4Radmax()
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
                    P4Radmax.success4Fit = 0
                else:
                    P4Radmax.success4Fit = 1
            else:
                P4Radmax.success4Fit = 1
            self.empty_field = 0
            self.not_a_float = 0

    def limit_reach(self, limit):
        limit_list = [16, 17, 19, 20]
        for i in range(len(limit)):
            if limit[i] == False:
                self.data_fields[limit_list[i]].SetBackgroundColour('yellow')
                self.Refresh()
        msg_ = (u"Deformation values are off limits\n" +
                "Please check the yellow field before launching the fit")
        dlg = GMD.GenericMessageDialog(None, msg_, "Attention",
                                       agwStyle=wx.OK | wx.ICON_INFORMATION |
                                       wx.CENTRE)
        dlg.ShowModal()
        for i in range(len(limit)):
            if limit[i] == False:
                self.data_fields[limit_list[i]].SetBackgroundColour('white')
                self.Refresh()

    def on_read_initial_file(self):
        a = P4Radmax()
        b = ReadFile(self)
        if (os.path.exists(a.PathDict['DW_file']) and
           os.path.exists(a.PathDict['Strain_file']) and
           os.path.exists(a.PathDict['XRD_file'])) is True:
            try:
                """READING DW FILE"""
                b.read_dw_file(a.PathDict['DW_file'])
                """READING Strain FILE"""
                b.read_strain_file(a.PathDict['Strain_file'])
                """READING XRD FILE"""
                b.read_xrd_file(a.PathDict['XRD_file'])

                P4Radmax.ParamDict['Iobs'] = a.ParamDict['data_xrd'][1]
                minval = np.min(a.ParamDict['Iobs'][np.nonzero(
                                                    a.ParamDict['Iobs'])])
                P4Radmax.ParamDict['Iobs'][a.ParamDict['Iobs'] == 0] = minval
                P4Radmax.ParamDict['Iobs'] = (a.ParamDict['Iobs'] /
                                              a.ParamDict['Iobs'].max())
                P4Radmax.ParamDictbackup['Iobs'] = a.ParamDict['Iobs']
                P4Radmax.ParamDict['th'] = ((a.ParamDict['data_xrd'][0]) *
                                            np.pi/360.)
                temp = a.ParamDict['data_xrd'][0]
                P4Radmax.ParamDictbackup['th'] = temp*np.pi/360.
                P4Radmax.ParamDict['th4live'] = 2*a.ParamDict['th']*180/np.pi
                P4Radmax.ParamDictbackup['dwp'] = a.ParamDict['dwp']
                P4Radmax.ParamDictbackup['sp'] = a.ParamDict['sp']
                P4Radmax.ParamDict['sp_abrupt'] = a.ParamDict['sp']
                P4Radmax.ParamDict['dwp_abrupt'] = a.ParamDict['dwp']
            except TypeError:
                logger.log(logging.WARNING, "!Please check your input file!")
            else:
                return True
        else:
            msg_ = "Please, check that the input files really exists"
            dlg = GMD.GenericMessageDialog(None, msg_,
                                           "Attention", agwStyle=wx.OK |
                                           wx.ICON_INFORMATION)
            dlg.ShowModal()
            return False

    def on_update(self, event):
        self.empty_field = 0
        self.not_a_float = 0
        val = self.cb_crystalsymmetry.GetStringSelection()
        self.on_select_symmetry(event, val)
        check_empty = self.search4emptyfields()
        if check_empty:
            data_float = self.is_data_float()
            if data_float:
                a = P4Radmax()
                if (a.ParamDict['Iobs'] == [] or
                   a.ParamDict['sp'] == [] or
                   a.ParamDict['dwp'] == []):
                    return
                else:
                    self.empty_field = 0
                    self.on_calcul_parameters()
                    self.Fit()
                    self.Layout()
                    P4Radmax.success4Fit = 0
                    self.statusbar.SetStatusText(u"", 0)
                    pub.sendMessage(pubsub_gauge_to_zero)
            else:
                P4Radmax.success4Fit = 1
        else:
            P4Radmax.success4Fit = 1
        self.empty_field = 0
        self.not_a_float = 0

    def on_update_from_drag_and_drop(self):
        self.empty_field = 0
        self.not_a_float = 0
        check_empty = self.search4emptyfields()
        if check_empty:
            data_float = self.is_data_float()
            if data_float:
                a = P4Radmax()
                if (a.ParamDict['Iobs'] == [] or
                   a.ParamDict['sp'] == [] or
                   a.ParamDict['dwp'] == []):
                    return
                else:
                    self.empty_field = 0
                    self.on_calcul_parameters()
                    self.Fit()
                    self.Layout()
                    P4Radmax.success4Fit = 0
            else:
                P4Radmax.success4Fit = 1
        else:
            P4Radmax.success4Fit = 1
        self.empty_field = 0
        self.not_a_float = 0

    def on_update_basis(self):
        self.StrainBfunction.GetValue()
        self.dwBfunction.GetValue()

    def on_update_scale(self, event):
        widget = event.GetId()
        if widget == self.m_strain_ID:
            pub.sendMessage(pubsub_Update_Scale_Strain, event=event,
                            val=float(self.strain_horizontal_ctrl.GetValue()))
        elif widget == self.m_DW_ID:
            pub.sendMessage(pubsub_Update_Scale_DW, event=event,
                            val=float(self.DW_horizontal_ctrl.GetValue()))

    def on_select_strain_Dw_name(self, event):
        a = P4Radmax()
        bsplinename = event.GetString()
        self.modelCalc = self.Strain_DW_choice.index(bsplinename)
        self.modelChoice.Clear()
        self.modelChoice.AppendText(str(self.modelCalc))
        t = int(a.DataDict['model'])
        P4Radmax.DataDict['model'] = self.modelCalc
        if bsplinename == "Asymmetric pv":
            self.on_hide_show_eta(True)
            self.cb_strainname.SetSelection(2)
            self.cb_dwname.SetSelection(2)
            self.StrainBfunction.Disable()
            P4Radmax.ParamDict['sp_' + Bsplinesave[t]] = a.ParamDict['sp']
            P4Radmax.ParamDict['dwp_' + Bsplinesave[t]] = a.ParamDict['dwp']

            P4Radmax.ParamDict['sp'] = a.ParamDict['sp_pv']
            P4Radmax.ParamDict['dwp'] = a.ParamDict['dwp_pv']
            self.on_test_model()
            pub.sendMessage(pubsub_Permute_Graph, choice=1)
        else:
            self.on_hide_show_eta(False)
            self.StrainBfunction.Enable()
            self.cb_strainname.SetSelection(0)
            self.cb_dwname.SetSelection(0)
            if bsplinename == "B-splines smooth":
                P4Radmax.ParamDict['sp_' + Bsplinesave[t]] = a.ParamDict['sp']
                P4Radmax.ParamDict['dwp_' + Bsplinesave[t]] = a.ParamDict['dwp']
                P4Radmax.ParamDict['sp'] = a.ParamDict['sp_smooth']
                P4Radmax.ParamDict['dwp'] = a.ParamDict['dwp_smooth']
            elif bsplinename == "B-splines abrupt":
                P4Radmax.ParamDict['sp_' + Bsplinesave[t]] = a.ParamDict['sp']
                P4Radmax.ParamDict['dwp_' + Bsplinesave[t]] = a.ParamDict['dwp']
                P4Radmax.ParamDict['sp'] = a.ParamDict['sp_abrupt']
                P4Radmax.ParamDict['dwp'] = a.ParamDict['dwp_abrupt']
            self.on_test_model()
            pub.sendMessage(pubsub_Permute_Graph, choice=0)

    def on_hide_show_eta(self, state):
        for i in range(len(self.Textcontrolhide)):
            self.Textcontrolhide[i].Show(state)
        if state:
            self.eta_txt.SetLabelText(self.eta_txt_label)
        else:
            self.eta_txt.SetLabelText("")
        self.Layout()

    def on_read_sp_DW(self):
        a = P4Radmax()
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
        self.load_init = 0

    def on_update_sp_DW(self):
        a = P4Radmax()
        P4Radmax.ParamDict['sp'][4] = self.eta_strain_1.GetValue()
        P4Radmax.ParamDict['sp'][5] = self.eta_strain_2.GetValue()
        P4Radmax.ParamDict['dwp'][4] = self.eta_dw_1.GetValue()
        P4Radmax.ParamDict['dwp'][5] = self.eta_dw_2.GetValue()
        P4Radmax.ParamDict['sp'] = [float(r) for r in a.ParamDict['sp']]
        P4Radmax.ParamDict['dwp'] = [float(r) for r in a.ParamDict['dwp']]

    def on_test_model(self):
        a = P4Radmax()
        val = 7.0
        if a.DataDict['model'] == 2:
            self.on_hide_show_eta(True)
            a.DataDict['strain_basis_func'] = val
            a.DataDict['dw_basis_func'] = val
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
            P4Radmax.modelPv = True
            if self.load_init == 1:
                self.on_read_sp_DW()
            else:
                self.on_update_sp_DW()
        else:
            self.on_hide_show_eta(False)
            self.StrainBfunction.Enable()
            self.cb_strainname.SetSelection(a.DataDict['model'])
            self.cb_dwname.SetSelection(a.DataDict['model'])
            P4Radmax.modelPv = False

    def on_calcul_parameters(self):
        a = P4Radmax()
        name = self.cb_crystalname.GetStringSelection()
        i = 0
        for k, v in a.DataDict.items():
            try:
                P4Radmax.DataDict[k] = a.initial_parameters[i]
                i += 1
            except (IndexError):
                break
        self.on_test_model()
        self.on_check_data_value()
        self.spline_strain = self.cb_strainname.GetSelection()
        self.spline_DW = self.cb_dwname.GetSelection()
        temp = [self.spline_strain, self.spline_DW]
        P4Radmax.splinenumber = temp

        if a.DataDict['model'] != 2:
            nb_slice, dw_func = self.OnChangeBasisFunction(
                                a.DataDict['strain_basis_func'],
                                a.DataDict['dw_basis_func'],
                                self.spline_strain, self.spline_DW,
                                a.DataDict['number_slices'])
            a.DataDict['dw_basis_func'] = dw_func
            a.DataDict['number_slices'] = nb_slice

        if name != []:
            P4Radmax.ParamDict['par'] = np.concatenate((a.ParamDict['sp'],
                                                       a.ParamDict['dwp']),
                                                       axis=0)
            P4Radmax.ParamDict['resol'] = f_pVoigt(
                                          a.ParamDict['th'],
                                          [1, (a.ParamDict['th'].min() +
                                           a.ParamDict['th'].max())/2,
                                           a.DataDict['resolution']*np.pi/180,
                                           a.DataDict['shape']])

            P4Radmax.ParamDict['d'], P4Radmax.ParamDict['Vol'] = f_dhkl_V(
                                        a.DataDict['h'], a.DataDict['k'],
                                        a.DataDict['l'], a.DataDict['a'],
                                        a.DataDict['b'], a.DataDict['c'],
                                        a.DataDict['alpha'],
                                        a.DataDict['beta'],
                                        a.DataDict['gamma'])
            temp_1 = (a.ConstDict['re'] * a.DataDict['wavelength'] *
                      a.DataDict['wavelength'])
            P4Radmax.ParamDict['G'] = temp_1 / (np.pi * a.ParamDict['Vol'])
            temp_2 = arcsin(a.DataDict['wavelength'] / (2*a.ParamDict['d']))
            P4Radmax.ParamDict['thB_S'] = temp_2
            temp_3 = a.ConstDict['phi']
            P4Radmax.ParamDict['g0'] = sin(a.ParamDict['thB_S'] - temp_3)
            P4Radmax.ParamDict['gH'] = -sin(a.ParamDict['thB_S'] + temp_3)
            P4Radmax.ParamDict['b_S'] = a.ParamDict['g0'] / a.ParamDict['gH']
            P4Radmax.ParamDict['t_l'] = (a.DataDict['damaged_depth'] /
                                         a.DataDict['number_slices'])
            P4Radmax.ParamDict['z'] = (arange(a.DataDict['number_slices']+1) *
                                       a.ParamDict['t_l'])
            temp_4 = f_FH(a.DataDict['h'], a.DataDict['k'], a.DataDict['l'],
                          a.DataDict['wavelength'], a.ParamDict['thB_S'],
                          a.ParamDict['z'], name)
            P4Radmax.ParamDict['FH'] = temp_4[0]
            P4Radmax.ParamDict['FmH'] = temp_4[1]
            P4Radmax.ParamDict['F0'] = temp_4[2]

            P4Radmax.ParamDict['Ical'] = f_ReflDict(a.DataDict)

            P4Radmax.ParamDict['I_i'] = (a.ParamDict['Ical'] /
                                         a.ParamDict['Ical'].max() +
                                         a.DataDict['background'])
            P4Radmax.ParamDict['depth'] = (a.DataDict['damaged_depth'] -
                                           a.ParamDict['z'])

            P4Radmax.ParamDict['DW_i'] = f_DW(
                                         a.ParamDict['z'],
                                         a.ParamDict['dwp'],
                                         a.DataDict['damaged_depth'],
                                         self.spline_DW)
            P4Radmax.ParamDict['strain_i'] = f_strain(
                                             a.ParamDict['z'],
                                             a.ParamDict['sp'],
                                             a.DataDict['damaged_depth'],
                                             self.spline_strain)
            t = a.DataDict['damaged_depth']

            self.on_shifted_sp_curves(t)
            self.on_shifted_dwp_curves(t)
            self.draw_curves()
        else:
            msg_ = "check if the structure file really exists"
            logger.log(logging.WARNING, msg_)

    def f_strain_DW(self):
        a = P4Radmax()
        P4Radmax.ParamDict['sp'] = a.ParamDict['_fp_min'][:int(a.DataDict['strain_basis_func'])]
        P4Radmax.ParamDict['dwp'] = a.ParamDict['_fp_min'][-1*int(a.DataDict['dw_basis_func']):]

        P4Radmax.ParamDict['DW_i'] = f_DW(
                                     a.ParamDict['z'], a.ParamDict['dwp'],
                                     a.DataDict['damaged_depth'],
                                     self.spline_DW)
        P4Radmax.ParamDict['strain_i'] = f_strain(
                                         a.ParamDict['z'], a.ParamDict['sp'],
                                         a.DataDict['damaged_depth'],
                                         self.spline_strain)

        t = a.DataDict['damaged_depth']
        self.on_shifted_sp_curves(t)
        self.on_shifted_dwp_curves(t)
        self.draw_curves()

    def on_shifted_dwp_curves(self, t):
        a = P4Radmax()
        if a.DataDict['model'] == 2:
            x_dw_temp = []
            x_dw_temp.append(t*(1-a.ParamDict['dwp'][1]))
            x_dw_temp.append(t*(1-a.ParamDict['dwp'][1] +
                             a.ParamDict['dwp'][2]/2))
            x_dw_temp.append(t*(1-a.ParamDict['dwp'][1] -
                             a.ParamDict['dwp'][3]/2))
            x_dw_temp.append(t*0.05)
            P4Radmax.ParamDict['x_dwp'] = x_dw_temp

            y_dw_temp = []
            y_dw_temp.append(a.ParamDict['dwp'][0])
            y_dw_temp.append(1. - (1-a.ParamDict['dwp'][0])/2)
            y_dw_temp.append(1. - (1-a.ParamDict['dwp'][0])/2 -
                             (1-a.ParamDict['dwp'][6])/2)
            y_dw_temp.append(a.ParamDict['dwp'][6])
            P4Radmax.ParamDict['DW_shifted'] = y_dw_temp

            self.DW_horizontal_ctrl.SetLabel(str(a.DW_multiplication))
        else:
            temp_1 = linspace(1, len(a.ParamDict['dwp']),
                              len(a.ParamDict['dwp']))
            temp_2 = temp_1 * t / (len(a.ParamDict['dwp']))
            P4Radmax.ParamDict['x_dwp'] = t - temp_2
            shifted_dwp = append(array([1.]), a.ParamDict['dwp'][:-1:])

            temp_3 = in1d(around(a.ParamDict['depth'], decimals=3),
                          around(a.ParamDict['x_dwp'], decimals=3))
            temp_4 = a.ParamDict['DW_i'][temp_3]
            P4Radmax.ParamDict['scale_dw'] = shifted_dwp / temp_4
            P4Radmax.ParamDict['scale_dw'][a.ParamDict['scale_dw'] == 0] = 1.

            P4Radmax.ParamDict['DW_shifted'] = shifted_dwp/a.ParamDict['scale_dw']
            P4Radmax.ParamDict['dw_out'] = a.ParamDict['dwp'][-1]

            self.DW_horizontal_ctrl.SetLabel(str(a.DW_multiplication))

    def on_shifted_sp_curves(self, t):
        a = P4Radmax()

        if a.DataDict['model'] == 2:
            x_sp_temp = []
            x_sp_temp.append(t*(1-a.ParamDict['sp'][1]))
            x_sp_temp.append(t*(1-a.ParamDict['sp'][1] +
                             a.ParamDict['sp'][2]/2))
            x_sp_temp.append(t*(1-a.ParamDict['sp'][1] -
                             a.ParamDict['sp'][3]/2))
            x_sp_temp.append(t*0.05)
            P4Radmax.ParamDict['x_sp'] = x_sp_temp

            y_sp_temp = []
            y_sp_temp.append(a.ParamDict['sp'][0])
            y_sp_temp.append(a.ParamDict['sp'][0]/2)
            y_sp_temp.append(a.ParamDict['sp'][0]/2 + a.ParamDict['sp'][6]/2)
            y_sp_temp.append(a.ParamDict['sp'][6])
            P4Radmax.ParamDict['strain_shifted'] = y_sp_temp

            self.strain_horizontal_ctrl.SetLabel(str(a.strain_multiplication))
        else:
            temp_1 = linspace(1, len(a.ParamDict['sp']),
                              len(a.ParamDict['sp']))
            temp_2 = temp_1 * t / (len(a.ParamDict['sp']))
            P4Radmax.ParamDict['x_sp'] = t - temp_2
            shifted_sp = append(array([0.]), a.ParamDict['sp'][:-1:])

            temp_3 = in1d(around(a.ParamDict['depth'], decimals=3),
                          around(a.ParamDict['x_sp'], decimals=3))
            temp_4 = a.ParamDict['strain_i'][temp_3]
            P4Radmax.ParamDict['scale_strain'] = shifted_sp / temp_4
            P4Radmax.ParamDict['scale_strain'][a.ParamDict['scale_strain'] == 0] = 1.

            P4Radmax.ParamDict['strain_shifted'] = shifted_sp*100./a.ParamDict['scale_strain']
            P4Radmax.ParamDict['stain_out'] = a.ParamDict['sp'][-1]

            self.strain_horizontal_ctrl.SetLabel(str(a.strain_multiplication))

    def draw_curves(self):
        a = P4Radmax()
        if a.from_calc_strain == 1:
            P4Radmax.from_calc_strain = 0
            pub.sendMessage(pubsub_Draw_Strain)
        elif a.from_calc_DW == 1:
            P4Radmax.from_calc_DW = 0
            pub.sendMessage(pubsub_Draw_DW)
        else:
            if a.fitlive == 1:
                pub.sendMessage(pubsub_Draw_Strain)
                pub.sendMessage(pubsub_Draw_DW)
            else:
                pub.sendMessage(pubsub_Draw_XRD)
                pub.sendMessage(pubsub_Draw_Strain)
                pub.sendMessage(pubsub_Draw_DW)

    def search4emptyfields(self):
        """search for empty field"""
        check_empty = True
        empty_fields = []
        for ii in range(len(self.data_fields)):
            empt = self.data_fields[ii]
            if empt.GetValue() == "":
                empty_fields.append(ii)
        if empty_fields != []:
            check_empty = False
            if self.empty_field == 0:
                for ii in empty_fields:
                    self.data_fields[ii].SetBackgroundColour('red')
                self.Refresh()
                msg_ = "Please, fill the red empty fields before to continue"
                dlg = GMD.GenericMessageDialog(None, msg_,
                                               "Attention",
                                               agwStyle=wx.OK |
                                               wx.ICON_INFORMATION)
                dlg.ShowModal()
                self.empty_field = 1
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
        a = P4Radmax()
        IsFloat = []
        dataFloat = True
        P4Radmax.ProjectFileData = []
        for i in range(len(self.data_fields)):
            P4Radmax.ProjectFileData.append(self.data_fields[i].GetValue())
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
            P4Radmax.initial_parameters = [float(ii) for ii in
                                           a.ProjectFileData]
        return dataFloat

    def on_reset_deformation_multiplication(self):
        a = P4Radmax()
        P4Radmax.strain_multiplication = 1.0
        P4Radmax.DW_multiplication = 1.0
        self.DW_horizontal_ctrl.SetLabel(str(a.DW_multiplication))
        self.strain_horizontal_ctrl.SetLabel(str(a.strain_multiplication))

    def OnChangeBasisFunction(self, strain, dw, spline_strain,
                              spline_DW, slice_):
        a = P4Radmax()
        strain_change = 0
        dw_change = 0
        slice_change = 0
        if strain != float(a.ParamDict['strain_basis']):
            P4Radmax.ParamDict['strain_basis'] = strain
            strain_change = 1
        if dw != a.ParamDict['dw_basis']:
            P4Radmax.ParamDict['dw_basis'] = dw
            dw_change = 1
        if slice_ != float(a.ParamDict['slice_backup']):
            P4Radmax.slice_backup = slice_
            slice_change = 1

        if strain_change == 1 or dw_change == 1 or slice_change == 1:
            temp = self.find_nearest_damaged_depth(a.DataDict['damaged_depth'],
                                                   a.DataDict['number_slices'],
                                                   strain)
            a.DataDict['damaged_depth'] = temp[0]
            a.DataDict['number_slices'] = temp[1]
            slice_val = a.DataDict['number_slices']
            damaged_val = a.DataDict['damaged_depth']
            dw = self.find_nearest_dw(a.DataDict['number_slices'], dw, strain,
                                      strain_change, dw_change, slice_change)
            self.damaged_depth.SetValue(str(damaged_val))
            self.dwBfunction.SetValue(str(dw))
            P4Radmax.ParamDict['t_l'] = damaged_val/slice_val
            P4Radmax.ParamDict['z'] = arange(slice_val+1) * a.ParamDict['t_l']
            P4Radmax.ParamDict['dwp'] = old2new_DW(a.ParamDict['z'],
                                                   a.ParamDict['dwp'],
                                                   damaged_val, dw, spline_DW)
            P4Radmax.ParamDict['sp'] = old2new_strain(a.ParamDict['z'],
                                                      a.ParamDict['sp'],
                                                      damaged_val, strain,
                                                      spline_strain)
            P4Radmax.ParamDictbackup['dwp'] = deepcopy(a.ParamDict['dwp'])
            P4Radmax.ParamDictbackup['sp'] = deepcopy(a.ParamDict['sp'])

            self.Layout()
            self.Nb_slice.SetValue(str(slice_val))
            return slice_val, dw
        else:
            slice_val = int(float(self.Nb_slice.GetValue()))
            return slice_val, dw

    def find_nearest_damaged_depth(self, damaged, N, Nstrain):
        if damaged % Nstrain != 0:
            damaged = round(damaged/Nstrain)*Nstrain
        if N/Nstrain != 0:
            N = round(N/Nstrain)*Nstrain
        return damaged, N

    def find_nearest(self, array, value):
        array = [int(a) for a in array]
        array = np.array(array)
        idx = (np.abs(array-value)).argmin()
        return idx

    def find_nearest_dw(self, N, Ndw, Nstrain, strain_change, dw_change,
                        slice_change):
        temp = []
        for i in range(5, 30):
            if N % i == 0:
                temp.append(str(i))
        self.dwBfunction.SetItems(temp)
        if strain_change == 1:
            index = self.find_nearest(temp, int(Nstrain))
            self.dwBfunction.SetStringSelection(temp[index])
            self.dwBfunction_hide.SetValue(str(Nstrain))
            val = int(temp[index])
        elif slice_change == 1:
            index = self.find_nearest(temp, int(Ndw))
            self.dwBfunction.SetStringSelection(temp[index])
            val = int(temp[index])
        elif dw_change == 1:
            index = self.dwBfunction_hide.GetValue()
            val = int(float(index))
        return val

    def on_page_changed(self, event):
        self.Fit()
        self.Layout()
        self.update_Btn.SetFocus()
        if self.load_data == 1:
            self.on_update(event)
            if self.empty_field == 1:
                event.Veto()
                self.parent.notebook.EnableTab(1, False)
                self.Fit()
                self.Layout()
