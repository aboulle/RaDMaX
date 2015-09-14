#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A_BOULLE & M_SOUILAH

from Read4Radmax import ReadFile, SaveFile4Diff
from Parameters4Radmax import *
from def_strain import f_strain, old2new_strain, fit_input_strain
from def_DW import f_DW, old2new_DW, fit_input_DW
from def_XRD import f_Refl
from def_Fh import f_FH
from sys import platform as _platform

"""New Project initial data"""
New_project_initial = [1.48806, 0.013, 0.000001, 5e-6, 1, 1, 0, 0, 5.4135,\
5.4135, 5.4135, 90, 90, 90, 10, -3, 3.5, 10, 0, 4, 3500, 70]
New_project_initial_size = range(len(New_project_initial))
New_project_initial_data = dict(zip(New_project_initial_size, New_project_initial))

"""Pubsub message"""
pubsub_Load_fitting_panel = "LoadFittingPanel"
pubsub_Load = "LoadP"
pubsub_New = "NewP"
pubsub_LoadXRD = "LoadXRD"
pubsub_LoadStrain = "LoadStrain"
pubsub_LoadDW = "LoadDW"
pubsub_Save = "SaveP"
pubsub_Launch_GUI = "LaunchGUI"
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
pubsub_Update_deformation_multiplicator_coef = "UpdateDeformationMultiplicatorCoef"
pubsub_save_project_before_fit = "SaveProjectBeforeFit"
pubsub_gauge_to_zero = "Gauge2zero"
pubsub_shortcut = "Shortcut"
pubsub_On_Limit_Before_Graph = "OnLimitBeforeGraph"

#------------------------------------------------------------------------------
class InitialDataPanel(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar
        self.parent = parent
#        self.parent.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.OnPageChanged)
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)

        vStatictextsize = 16
        size_text = (85,22)
        size_value_hkl = (50,22)
        size_value_lattice = (65,22)
        size_damaged_depth = (110,22)
        
        font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
        font_update = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        if _platform == "linux" or _platform == "linux2":
            font_Statictext = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
            font_TextCtrl = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
            font_combobox = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
        elif _platform == "win32":
            info = wx.NativeFontInfo()
            info.SetFaceName("arial")
            info.SetPointSize(9)
            font_Statictext = wx.FontFromNativeInfoString(info.ToString())
            font_TextCtrl = wx.FontFromNativeInfoString(info.ToString())
            font_combobox = wx.FontFromNativeInfoString(info.ToString())
                
        size_StaticBox = (920, 140)

        """master sizer for the whole panel"""
        mastersizer = wx.BoxSizer(wx.VERTICAL)

        """Experiment part"""
        Experiment_box = wx.StaticBox(self, -1, " Experiment ", size=size_StaticBox)
        Experiment_box.SetFont(font)
        Experiment_box_sizer = wx.StaticBoxSizer(Experiment_box, wx.VERTICAL)
        in_Experiment_box_sizer = wx.GridBagSizer(hgap=10, vgap=0)
        flagSizer = wx.ALL|wx.ALIGN_CENTER_VERTICAL
        
        wavelength_txt = wx.StaticText(self, -1, label=u'Wavelength (\u212B)', size=(100,vStatictextsize))
        wavelength_txt.SetFont(font_Statictext)
        self.wavelength = wx.TextCtrl(self, size=size_text)
        self.wavelength.SetFont(font_TextCtrl)

        resolution_txt = wx.StaticText(self, -1, label=u'Resolution (°)', size=(90,vStatictextsize))
        resolution_txt.SetFont(font_Statictext)
        self.resolution = wx.TextCtrl(self, size=size_text)
        self.resolution.SetFont(font_TextCtrl)

        shape_txt = wx.StaticText(self, -1, label=u'Shape', size=(45,vStatictextsize))
        shape_txt.SetFont(font_Statictext)
        self.shape = wx.TextCtrl(self, size=size_text)
        self.shape.SetFont(font_TextCtrl)

        bckground_txt = wx.StaticText(self, -1, label=u'Background', size=(75,vStatictextsize))
        bckground_txt.SetFont(font_Statictext)
        self.bckground = wx.TextCtrl(self, size=size_text)
        self.bckground.SetFont(font_TextCtrl)
        
        in_Experiment_box_sizer.Add(wavelength_txt, pos=(0,0), flag=flagSizer)
        in_Experiment_box_sizer.Add(self.wavelength, pos=(0,1), flag=flagSizer)
        in_Experiment_box_sizer.Add(resolution_txt, pos=(0,2), flag=flagSizer)
        in_Experiment_box_sizer.Add(self.resolution, pos=(0,3), flag=flagSizer)
        in_Experiment_box_sizer.Add(shape_txt, pos=(0,4), flag=flagSizer)
        in_Experiment_box_sizer.Add(self.shape, pos=(0,5), flag=flagSizer)
        in_Experiment_box_sizer.Add(bckground_txt, pos=(0,6), flag=flagSizer)
        in_Experiment_box_sizer.Add(self.bckground, pos=(0,7), flag=flagSizer)
        
        Experiment_box_sizer.Add(in_Experiment_box_sizer, 0, wx.ALL, 5)
        
        """Material part"""
        Material_box = wx.StaticBox(self, -1, " Material ", size=size_StaticBox)
        Material_box.SetFont(font)
        Material_box_sizer = wx.StaticBoxSizer(Material_box, wx.VERTICAL)
        in_Material_box_sizer = wx.GridBagSizer(hgap=16, vgap=1)

        crystalname_txt = wx.StaticText(self, -1, label=u'Crystal', size=(45,vStatictextsize))
        crystalname_txt.SetFont(font_Statictext)
        self.crystal_choice = ["None"]
        self.cb_crystalname = wx.ComboBox(self, pos=(50, 30), choices=self.crystal_choice, style=wx.CB_READONLY, size=(80, 22))
        self.cb_crystalname.SetStringSelection(self.crystal_choice[0])
        self.cb_crystalname.SetFont(font_combobox)

        crystalsymmetry_txt = wx.StaticText(self, -1, label=u'Symmetry:', size=(65,vStatictextsize))
        crystalsymmetry_txt.SetFont(font_Statictext)
        self.symmetry_choice = ["cubic", "hexa", "tetra", "ortho", "rhombo", "mono", "triclinic"]
        self.cb_crystalsymmetry = wx.ComboBox(self, pos=(50, 30), choices=self.symmetry_choice, style=wx.CB_READONLY)
        self.cb_crystalsymmetry.SetStringSelection(self.symmetry_choice[0])
        self.cb_crystalsymmetry.SetFont(font_combobox)
        self.cb_crystalsymmetry.Bind(wx.EVT_COMBOBOX, self.OnSelectSymmetry)

        reflection_txt = wx.StaticText(self, -1, label=u'Reflection:', size=(65,vStatictextsize))
        reflection_txt.SetFont(font_Statictext)
        h_direction_txt = wx.StaticText(self, -1, label=u'h', size=(10,vStatictextsize))
        h_direction_txt.SetFont(font_Statictext)
        self.h_direction = wx.TextCtrl(self, size=size_value_hkl)
        self.h_direction.SetFont(font_TextCtrl)

        k_direction_txt = wx.StaticText(self, -1, label=u'k', size=(10,vStatictextsize))
        k_direction_txt.SetFont(font_Statictext)
        self.k_direction = wx.TextCtrl(self, size=size_value_hkl)
        self.k_direction.SetFont(font_TextCtrl)

        l_direction_txt = wx.StaticText(self, -1, label=u'l', size=(10,vStatictextsize))
        l_direction_txt.SetFont(font_Statictext)
        self.l_direction = wx.TextCtrl(self, size=size_value_hkl)
        self.l_direction.SetFont(font_TextCtrl)

        latticeparam_txt = wx.StaticText(self, -1, label=u'Lattice parameters (\u212B):', size=(135,vStatictextsize))
        latticeparam_txt.SetFont(font_Statictext)

        self.symmetry_txt_hide = wx.TextCtrl(self,size=(0,vStatictextsize))
        self.symmetry_txt_hide.Hide()

        a_param_txt = wx.StaticText(self, -1, label=u'a', size=(10,vStatictextsize))
        a_param_txt.SetFont(font_Statictext)
        self.a_param = wx.TextCtrl(self, size=size_value_lattice)
        self.a_param.SetFont(font_TextCtrl)

        b_param_txt = wx.StaticText(self, -1, label=u'b', size=(10,vStatictextsize))
        b_param_txt.SetFont(font_Statictext)
        self.b_param = wx.TextCtrl(self, size=size_value_lattice)
        self.b_param.SetFont(font_TextCtrl)

        c_param_txt = wx.StaticText(self, -1, label=u'c', size=(10,vStatictextsize))
        c_param_txt.SetFont(font_Statictext)
        self.c_param = wx.TextCtrl(self, size=size_value_lattice)
        self.c_param.SetFont(font_TextCtrl)

        alpha_param_txt = wx.StaticText(self, -1, label=u'\N{GREEK SMALL LETTER ALPHA}', size=(10,vStatictextsize))
        alpha_param_txt.SetFont(font_Statictext)
        self.alpha_param = wx.TextCtrl(self, size=size_value_lattice)
        self.alpha_param.SetFont(font_TextCtrl)

        beta_param_txt = wx.StaticText(self, -1, label=u'\N{GREEK SMALL LETTER BETA}', size=(10,vStatictextsize))
        beta_param_txt.SetFont(font_Statictext)
        self.beta_param = wx.TextCtrl(self, size=size_value_lattice)
        self.beta_param.SetFont(font_TextCtrl)

        gamma_param_txt = wx.StaticText(self, -1, label=u'\N{GREEK SMALL LETTER GAMMA}', size=(10,vStatictextsize))
        gamma_param_txt.SetFont(font_Statictext)
        self.gamma_param = wx.TextCtrl(self, size=size_value_lattice)
        self.gamma_param.SetFont(font_TextCtrl)

        in_Material_box_sizer.Add(crystalname_txt, pos=(0,0), flag=flagSizer)
        in_Material_box_sizer.Add(self.cb_crystalname, pos=(0,1), span=(1,2), flag=flagSizer)
        in_Material_box_sizer.Add(reflection_txt, pos=(1,0), flag=flagSizer)
        in_Material_box_sizer.Add(h_direction_txt, pos=(1,1), flag=flagSizer)
        in_Material_box_sizer.Add(self.h_direction, pos=(1,2), flag=flagSizer)
        in_Material_box_sizer.Add(k_direction_txt, pos=(1,3), flag=flagSizer)
        in_Material_box_sizer.Add(self.k_direction, pos=(1,4), flag=flagSizer)
        in_Material_box_sizer.Add(l_direction_txt, pos=(1,5), flag=flagSizer)
        in_Material_box_sizer.Add(self.l_direction, pos=(1,6), flag=flagSizer)

        in_Material_box_sizer.Add(latticeparam_txt, pos=(0,5), span=(1,4), flag=wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        in_Material_box_sizer.Add(a_param_txt, pos=(0,9), flag=flagSizer)
        in_Material_box_sizer.Add(self.a_param, pos=(0,10), flag=flagSizer)
        in_Material_box_sizer.Add(b_param_txt, pos=(0,11), flag=flagSizer)
        in_Material_box_sizer.Add(self.b_param, pos=(0,12), flag=flagSizer)
        in_Material_box_sizer.Add(c_param_txt, pos=(0,13), flag=flagSizer)
        in_Material_box_sizer.Add(self.c_param, pos=(0,14), flag=flagSizer)

        in_Material_box_sizer.Add(crystalsymmetry_txt, pos=(0,15), flag=flagSizer)
        in_Material_box_sizer.Add(self.cb_crystalsymmetry, pos=(1,15), flag=flagSizer)    
        in_Material_box_sizer.Add(self.symmetry_txt_hide, pos=(0,16), flag=flagSizer)

        in_Material_box_sizer.Add(alpha_param_txt, pos=(1,9), flag=flagSizer)
        in_Material_box_sizer.Add(self.alpha_param, pos=(1,10), flag=flagSizer)
        in_Material_box_sizer.Add(beta_param_txt, pos=(1,11), flag=flagSizer)
        in_Material_box_sizer.Add(self.beta_param, pos=(1,12), flag=flagSizer)
        in_Material_box_sizer.Add(gamma_param_txt, pos=(1,13), flag=flagSizer)
        in_Material_box_sizer.Add(self.gamma_param, pos=(1,14), flag=flagSizer)

        Material_box_sizer.Add(in_Material_box_sizer, 0, wx.ALL, 5)

        """Strain and Debye Waller part"""
        Strain_DW_box = wx.StaticBox(self, -1, " Strain and Debye-Waller ", size=size_StaticBox)
        Strain_DW_box.SetFont(font)
        Strain_DW_box_sizer = wx.StaticBoxSizer(Strain_DW_box, wx.VERTICAL)
        in_Strain_DW_box_sizer = wx.GridBagSizer(hgap=10, vgap=1)

        Strain_DW_choice = ["B-splines smooth", "B-splines abrupt", "B-splines histogram"]
        strainname_txt = wx.StaticText(self, -1, label=u'Strain: model', size=(85,vStatictextsize))
        strainname_txt.SetFont(font_Statictext)
        self.cb_strainname = wx.ComboBox(self, pos=(50, 30), choices=Strain_DW_choice, style=wx.CB_READONLY)
        self.cb_strainname.SetStringSelection(Strain_DW_choice[0])
        self.cb_strainname.SetFont(font_combobox)
        
        dwname_txt = wx.StaticText(self, -1, label=u'DW: model', size=(75,vStatictextsize))
        dwname_txt.SetFont(font_Statictext)
        self.cb_dwname = wx.ComboBox(self, pos=(50, 30), choices=Strain_DW_choice, style=wx.CB_READONLY)
        self.cb_dwname.SetStringSelection(Strain_DW_choice[0])
        self.cb_dwname.SetFont(font_combobox)
        
        self.StrainBfunction_ID = wx.NewId()
        self.dwBfunction_ID = wx.NewId()
       
        StrainBfunction_txt = wx.StaticText(self, id=self.StrainBfunction_ID, label=u'Basis functions', size=(95,vStatictextsize))
        StrainBfunction_txt.SetFont(font_Statictext)
        self.StrainBfunction = wx.TextCtrl(self, size=size_value_lattice)
        self.StrainBfunction.SetFont(font_TextCtrl)

        dwBfunction_txt = wx.StaticText(self, id=self.dwBfunction_ID, label=u'Basis functions', size=(95,vStatictextsize))
        dwBfunction_txt.SetFont(font_Statictext)
        self.dwBfunction_choice = [""]
        self.dwBfunction = wx.ComboBox(self, pos=(50, 30), choices=self.dwBfunction_choice, style=wx.CB_READONLY, size=(65, 22))
        self.dwBfunction.SetStringSelection(self.dwBfunction_choice[0])
        self.dwBfunction.SetFont(font_combobox)
        
        self.dwBfunction.Bind(wx.EVT_COMBOBOX, self.OnChangeDW)
        
        self.dwBfunction_hide = wx.TextCtrl(self,size=(0,vStatictextsize))
        self.dwBfunction_hide.Hide()
        
        dwMinMax_txt = wx.StaticText(self, -1, label=u'Min./ Max.', size=(70,vStatictextsize))
        dwMinMax_txt.SetFont(font_Statictext)
        self.dwMin = wx.TextCtrl(self, size=size_value_lattice)
        self.dwMax = wx.TextCtrl(self, size=size_value_lattice)
        self.dwMin.SetFont(font_TextCtrl)
        self.dwMax.SetFont(font_TextCtrl)

        StrainMinMax_txt = wx.StaticText(self, -1, label=u'Min./ Max.', size=(70,vStatictextsize))
        StrainMinMax_txt.SetFont(font_Statictext)
        self.StrainMin = wx.TextCtrl(self, size=size_value_lattice)
        self.StrainMax = wx.TextCtrl(self, size=size_value_lattice)
        self.StrainMin.SetFont(font_TextCtrl)
        self.StrainMax.SetFont(font_TextCtrl)
        
        damaged_depth_txt = wx.StaticText(self, -1, label=u'Damaged depth (\u212B)', size=(115,vStatictextsize))
        damaged_depth_txt.SetFont(font_Statictext)
        self.damaged_depth = wx.TextCtrl(self, size=size_damaged_depth)
        self.damaged_depth.SetFont(font_TextCtrl)

        Nb_slice_txt = wx.StaticText(self, -1, label=u'Number of slices (for XRD computation)', size=(260,vStatictextsize))
        Nb_slice_txt.SetFont(font_Statictext)
        self.Nb_slice = wx.TextCtrl(self, size=size_damaged_depth)
        self.Nb_slice.SetFont(font_TextCtrl)

        self.m_strain_ID = wx.NewId()
        self.m_DW_ID = wx.NewId()
        DW_horizontal_ctrl_txt = wx.StaticText(self, -1, label=u'Scale', size=(40,vStatictextsize))
        self.DW_horizontal_ctrl = wx.StaticText(self, -1, label=u'', size=(35,vStatictextsize))
        self.DW_horizontal_ctrl.SetFont(font_Statictext)
        self.DW_horizontal_ctrl.SetLabel('1.00')

        strain_horizontal_ctrl_txt = wx.StaticText(self, -1, label=u'Scale', size=(40,vStatictextsize))
        self.strain_horizontal_ctrl = wx.StaticText(self, -1, label=u'', size=(35,vStatictextsize))
        self.strain_horizontal_ctrl.SetFont(font_Statictext)
        self.strain_horizontal_ctrl.SetLabel('1.00')
        
        in_Strain_DW_box_sizer.Add(strainname_txt, pos=(0,0), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.cb_strainname, pos=(0,1), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(dwname_txt, pos=(1,0), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.cb_dwname, pos=(1,1), flag=flagSizer)
        
        in_Strain_DW_box_sizer.Add(StrainBfunction_txt, pos=(0,3), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.StrainBfunction, pos=(0,4), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(dwBfunction_txt, pos=(1,3), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.dwBfunction, pos=(1,4), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.dwBfunction_hide, pos=(1,5), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(StrainMinMax_txt, pos=(0,6), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.StrainMin, pos=(0,7), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.StrainMax, pos=(0,8), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(strain_horizontal_ctrl_txt, pos=(0,9), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.strain_horizontal_ctrl, pos=(0,10), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(dwMinMax_txt, pos=(1,6), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.dwMin, pos=(1,7), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.dwMax, pos=(1,8), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(DW_horizontal_ctrl_txt, pos=(1,9), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.DW_horizontal_ctrl, pos=(1,10), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(damaged_depth_txt, pos=(2,0), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(self.damaged_depth, pos=(2,1), flag=flagSizer)
        in_Strain_DW_box_sizer.Add(Nb_slice_txt, pos=(2,3), span=(1,4), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        in_Strain_DW_box_sizer.Add(self.Nb_slice, pos=(2,7), span=(1,2), flag=flagSizer)
        
        Strain_DW_box_sizer.Add(in_Strain_DW_box_sizer, 0, wx.ALL, 5)
        
        self.updateId = wx.NewId()
        self.update_Btn = wx.Button(self, id=self.updateId, label="Update")
        self.update_Btn.SetFont(font_update)
        self.update_Btn.Bind(wx.EVT_BUTTON, self.onUpdate)
        self.update_Btn.SetFocus()

        self.Textcontrol = [self.wavelength, self.resolution, self.shape, self.bckground,
                            self.h_direction, self.k_direction, self.l_direction, self.symmetry_txt_hide,
                            self.a_param, self.b_param, self.c_param, self.alpha_param, self.beta_param,
                            self.gamma_param, self.StrainBfunction, self.StrainMin, self.StrainMax,
                            self.dwBfunction_hide, self.dwMin, self.dwMax, self.damaged_depth, self.Nb_slice]
        Textcontrolen = range(len(self.Textcontrol))
        self.data_fields = dict(zip(Textcontrolen,self.Textcontrol))
        self.data_fields_dict = []
        self.folder_paths_dict = []
        self.par4diff = []
        self.resultprojectfile = (len(Initial_data_key) + header_project)*[1]
        self.data_paths_dict = dict(zip(NamePath_panel_keys, self.resultprojectfile[:4]))
        self.resultprojectfile_backup = []

        self.directory_path = ""
        self.project_name = "" 
        self.XRD_path = ""
        self.Strain_path = ""
        self.DW_path = ""
        self.loadproject = ""
        
        self.load_data = 0
        self.data_change = 0
        self.empty_field = 0
        self.not_a_float = 0
        self.spline_strain = ""
        self.spline_DW = ""

                
        mastersizer.Add(Experiment_box_sizer, 0, wx.ALL, 5)
        mastersizer.Add(Material_box_sizer, 0, wx.ALL, 5)
        mastersizer.Add(Strain_DW_box_sizer, 0, wx.ALL, 5)
        mastersizer.Add(self.update_Btn, 0, wx.ALL, 5)
        
        pub.subscribe(self.onLoadProject, pubsub_Load)
        pub.subscribe(self.onNewProject, pubsub_New)
        pub.subscribe(self.onLoadXRD, pubsub_LoadXRD)
        pub.subscribe(self.onLoadStrain, pubsub_LoadStrain)
        pub.subscribe(self.onLoadDW, pubsub_LoadDW)
        pub.subscribe(self.OnLaunchCalc4Fit, pubsub_Read_field_paramters_panel)   
        pub.subscribe(self.onUpdate, pubsub_Re_Read_field_paramters_panel)
        pub.subscribe(self.onUpdateFromDragAndDrop, pubsub_Update_Fit_Live)
        pub.subscribe(self.onSaveProject, pubsub_Save)
        pub.subscribe(self.onSaveProject, pubsub_save_project_before_fit)
        pub.subscribe(self.Reset_Deformation_Multiplication, pubsub_Update_deformation_multiplicator_coef)
        pub.subscribe(self.onNewProject, pubsub_Launch_GUI)
        pub.subscribe(self.f_strain_DW, pubsub_Draw_Fit_Live_Deformation)
        pub.subscribe(self.KeyPressed, pubsub_shortcut)
        pub.subscribe(self.LimitReach, pubsub_On_Limit_Before_Graph)
        
        b = ReadFile(self)
        b.Read_init_Parameters(os.path.join(current_dir, filename + '.ini'), ConfigFile)
        config_File_extraction = b.read_result_value()
        self.folder_paths_dict = dict(zip(Folder_paths_key, config_File_extraction[2:]))
        
        self.SetSizer(mastersizer)
        self.ReadCrystalList()
        

    def KeyPressed(self, event, case):
        if case == 0:
            self.onUpdate(event)
        elif case == 1:
            if self.project_name != "":
                a = P4Diff()
                for ii in self.data_fields:
                    self.data_fields[ii].Clear()
                paths = a.path2inicomplete
                self.onReadDataLoaded(event, paths)
                logger.log(logging.INFO, "File has been reloaded by shortcut")

    def OnChangeDW(self, event):
        self.dwBfunction_hide.SetValue(event.GetString())

    def ReadCrystalList(self):
        if os.listdir(structures_name) != []:
            self.crystal_choice = sorted(list(os.listdir(structures_name)))
            self.cb_crystalname.SetItems(self.crystal_choice)
            self.cb_crystalname.SetStringSelection(self.crystal_choice[0])
    
    def OnSelectSymmetry(self, event, choice=None):
        if choice != None:
            i = choice
        else:
            i = event.GetString()
            
        cubique_text_state = ["Enable", "Disable", "Disable", "Disable", "Disable", "Disable"]
        cubique_text_value = ["None", 0, 0, 90, 90, 90]

        hexa_text_state = ["Enable", "Disable", "Enable", "Disable", "Disable", "Disable"]
        hexa_text_value = ["None", 0, "None", 90, 90, 120]

        tetra_text_state = ["Enable", "Disable", "Enable", "Disable", "Disable", "Disable"]
        tetra_text_value = ["None", 0, "None", 90, 90, 90]

        ortho_text_state = ["Enable", "Enable", "Enable", "Disable", "Disable", "Disable"]
        ortho_text_value = ["None", 0, "None", 90, 90, 90]

        rhombo_text_state = ["Enable", "Disable", "Disable", "Enable", "Disable", "Disable"]
        rhombo_text_value = ["None", 0, 0, "None", 3, 3]

        mono_text_state = ["Enable", "Enable", "Enable", "Disable", "Enable", "Disable"]
        mono_text_value = ["None", "None", "None", 90, "None", 90]

        tri_text_state = ["Enable", "Enable", "Enable", "Enable", "Enable", "Enable"]
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
                    self.data_fields[8+i].SetValue(str(self.data_fields[8 + temp_value[i]].GetValue()))
            elif i in range(3, 6):
                if temp_value[i] != "None":
                    if temp_value[i] == 90 or temp_value[i] == 120:
                        self.data_fields[8+i].Clear()
                        self.data_fields[8+i].SetValue(str(temp_value[i]))
                    elif temp_value[i] == 3:
                        self.data_fields[8+i].Clear()
                        self.data_fields[8+i].SetValue(str(self.data_fields[8 + temp_value[i]].GetValue()))

    def onNewProject(self, event=None):
        a = P4Diff()
        self.Reset_Deformation_Multiplication()
        for ii in self.data_fields:
            self.data_fields[ii].Clear()
        for i in range(len(self.data_fields)):
            self.data_fields[i].AppendText(str(New_project_initial_data[i]))
            self.resultprojectfile_backup.append(New_project_initial_data[i])
        
        success = self.ReadDataField()
        if success == True:
            pub.sendMessage(pubsub_ChangeFrameTitle, NewTitle=Application_name + " - " + 'New Project')
            self.statusbar.SetStatusText(u"", 0)
            P4Diff.namefromini = ""

            self.par4diff = dict(zip(Parameters_panel_keys,a.initial_parameters))
    
            val = self.symmetry_choice[int(float(self.par4diff['crystal_symmetry']))]
            self.cb_crystalsymmetry.SetStringSelection(val)
            self.OnSelectSymmetry(event, val)
    
            P4Diff.slice_backup = self.par4diff['number_slices']
            P4Diff.strain_basis_backup = self.par4diff['strain_basis_func']
            P4Diff.dw_basis_backup = self.par4diff['dw_basis_func']
            P4Diff.damaged_value_backup = self.par4diff['damaged_depth']
            
            self.dwBfunction_choice = [str(a.strain_basis_backup)]
            self.dwBfunction.SetItems(self.dwBfunction_choice)
            self.dwBfunction.SetStringSelection(self.dwBfunction_choice[0])
            self.cb_crystalname.SetStringSelection(self.crystal_choice[0])
            
            P4Diff.t_l = self.par4diff['damaged_depth']/self.par4diff['number_slices'] ## épaisseur d'une lamelle
            P4Diff.z = arange(self.par4diff['number_slices']+1) * a.t_l ## hauteur
            P4Diff.depth = self.par4diff['damaged_depth']-a.z
            P4Diff.Iobs = []
            P4Diff.Ical = []
            P4Diff.sp = int(self.par4diff['strain_basis_func'])*[1]
            P4Diff.dwp = int(self.par4diff['dw_basis_func'])*[1]
            P4Diff.sp = np.array(a.sp)
            P4Diff.dwp = np.array(a.dwp)
            pub.sendMessage(pubsub_Load_fitting_panel, data=None, b=1)
            pub.sendMessage(pubsub_Draw_XRD, b=2)
            pub.sendMessage(pubsub_Activate_Import)
            self.Calc_Strain()
            self.Calc_DW()
            spline_strain = self.cb_strainname.GetSelection()
            spline_DW = self.cb_dwname.GetSelection()
            nb_slice, dw_func = self.OnChangeBasisFunction(self.par4diff['strain_basis_func'], self.par4diff['dw_basis_func'], \
                                                            spline_strain, spline_DW, self.par4diff['number_slices'])
            
            self.data_paths_dict['Compound_name'] = self.cb_crystalname.GetStringSelection()
            self.data_paths_dict['DW_file'] = ""
            self.data_paths_dict['Strain_file'] = ""
            self.data_paths_dict['XRD_file'] = ""
            pub.sendMessage(pubsub_gauge_to_zero)
            self.update_Btn.SetFocus()

            self.Fit()  
            self.Layout()
        
    def onLoadXRD(self, event):
        a = P4Diff()
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
            P4Diff.path2drx = paths[0] 
            self.data_paths_dict['XRD_file'] = paths[0]
            self.onUpdateConfigFile('XRD_file')
            dlg.Destroy()
            try:
                """READING XRD FILE"""
                self.Reset_Deformation_Multiplication()
                b.read_xrd_file(paths[0])                
                P4Diff.Iobs = a.data_xrd[1]
                P4Diff.Iobs = a.Iobs / a.Iobs.max()
                P4Diff.Iobs_backup = a.Iobs
                P4Diff.th = (a.data_xrd[0])*pi/360.
                P4Diff.th_backup = (a.data_xrd[0])*pi/360.
                P4Diff.th4live = 2*a.th*180/pi
                pub.sendMessage(pubsub_Draw_XRD, b=1)
            except TypeError:
                logger.log(logging.WARNING, "!!! Please check your input file !!!")

    def onLoadStrain(self, event):
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
            self.onUpdateConfigFile('Strain_file')
            dlg.Destroy()
            try:
                self.Calc_Strain(paths, 0)
            except TypeError:
                logger.log(logging.WARNING, "!!! Please check your input file !!!")

    def onLoadDW(self, event):
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
            self.onUpdateConfigFile('DW_file')
            dlg.Destroy()
            try:
                self.Calc_DW(paths, 0)
            except TypeError:
                logger.log(logging.WARNING, "!!! Please check your input file !!!")

    def Calc_DW(self, paths=None, choice=None):
        a = P4Diff()
        b = ReadFile(self)
        spline_DW = self.cb_dwname.GetSelection()
        if choice == 0:
            data = b.read_dw_xy_file(paths[0])
            P4Diff.dwp = fit_input_DW(data, self.par4diff['dw_basis_func'],self.par4diff['damaged_depth'], spline_DW)
        P4Diff.dwp_backup = a.dwp
        P4Diff.dw_basis_backup = float(self.par4diff['dw_basis_func'])
        P4Diff.DW_i = f_DW(a.z, a.dwp, self.par4diff['damaged_depth'], spline_DW)
        t = self.par4diff['damaged_depth']
        P4Diff.x_dwp = t - linspace(1, len(a.dwp), len(a.dwp))*t / (len(a.dwp))
        shifted_dwp = append(array([1.]),a.dwp[:-1:])
        P4Diff.scale_dw = shifted_dwp /a.DW_i[ in1d(around(a.depth, decimals=3),  around(a.x_dwp, decimals=3))]
        P4Diff.scale_dw[a.scale_dw==0] = 1.
        P4Diff.DW_shifted = shifted_dwp/a.scale_dw
        if choice == 0:
            self.Save_Deformation('DW_file', 'DW', a.dwp)
        pub.sendMessage(pubsub_Draw_DW)

    def Calc_Strain(self, paths=None, choice=None):
        a = P4Diff()
        b = ReadFile(self)
        spline_strain = self.cb_strainname.GetSelection()
        if choice == 0:
            data = b.read_strain_xy_file(paths[0])
            P4Diff.sp = fit_input_strain(data, self.par4diff['strain_basis_func'],self.par4diff['damaged_depth'], spline_strain)
        P4Diff.sp_backup = a.sp
        P4Diff.strain_basis_backup = float(self.par4diff['strain_basis_func'])
        P4Diff.strain_i = f_strain(a.z, a.sp, self.par4diff['damaged_depth'], spline_strain)
        t = self.par4diff['damaged_depth']
        P4Diff.x_sp = t - linspace(1, len(a.sp), len(a.sp))*t / (len(a.sp))
        shifted_sp = append(array([0.]),a.sp[:-1:])
        
        P4Diff.scale_strain = shifted_sp /a.strain_i[ in1d(around(a.depth, decimals=3),  around(a.x_sp,decimals=3))]
        P4Diff.scale_strain[a.scale_strain==0] = 1. #avoids div by 0 error
        P4Diff.strain_shifted = shifted_sp*100./a.scale_strain  
        if choice == 0:
            self.Save_Deformation('Strain_file', 'strain', a.sp)
        pub.sendMessage(pubsub_Draw_Strain)

    def onLoadProject(self, event):
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
            self.onUpdateConfigFile('project_file')
            dlg.Destroy()
            self.onReadDataLoaded(event, paths[0])

    def onReadDataLoaded(self, event, paths):
            a = P4Diff()
            b = ReadFile(self)
            b.Read_init_Parameters(paths, ConfigDataFile)
            self.resultprojectfile = b.read_result_value()
            
            P4Diff.path2ini = os.path.split(paths)[0]
            P4Diff.path2inicomplete = paths
            P4Diff.namefromini = os.path.splitext(os.path.basename(paths))[0]
            if self.resultprojectfile == []:
                dlg = GMD.GenericMessageDialog(None, "Please, pay attention to your input files, there are some mistakes in the data",
                "Attention", agwStyle = wx.OK|wx.ICON_INFORMATION)
                dlg.ShowModal()
            else:
                self.project_name = os.path.splitext(os.path.basename(paths))[0]
                self.resultprojectfile_backup = []
                for i in range(len(self.data_fields)):
                    self.data_fields[i].AppendText(str(self.resultprojectfile[i + header_project]))
                    self.resultprojectfile_backup.append(self.resultprojectfile[i + header_project])

                success = self.ReadDataField()
                if success == True:                
                    self.par4diff = dict(zip(Parameters_panel_keys,self.resultprojectfile[4:]))
                    
                    '''create dictionnary of datafields to use name instead index'''
                    self.data_paths_dict = dict(zip(NamePath_panel_keys, self.resultprojectfile[:4]))
                    val = self.symmetry_choice[int(float(self.par4diff['crystal_symmetry']))]
                    self.cb_crystalsymmetry.SetStringSelection(val)
                    self.OnSelectSymmetry(event, val)
    
                    P4Diff.slice_backup = self.par4diff['number_slices']
                    P4Diff.strain_basis_backup = self.par4diff['strain_basis_func']
                    P4Diff.dw_basis_backup = self.par4diff['dw_basis_func']
                    P4Diff.damaged_value_backup = self.par4diff['damaged_depth']
                    
                    self.dwBfunction_choice = [a.strain_basis_backup]
                    self.dwBfunction.SetItems(self.dwBfunction_choice)
                    self.dwBfunction.SetStringSelection(self.dwBfunction_choice[0])
                    
                    if self.data_paths_dict['Compound_name'] in self.crystal_choice:
                        indexx = self.crystal_choice.index(self.data_paths_dict['Compound_name'])
                        self.cb_crystalname.SetStringSelection(self.crystal_choice[indexx])
                        logger.log(logging.INFO, "Config file successfully loaded")
                    else:
                        logger.log(logging.INFO, "You need to add the proper strcuture to continue")
                    '''change name of the main title window'''
                    pub.sendMessage(pubsub_ChangeFrameTitle, NewTitle=Application_name + " - " + str(self.project_name))
                    pub.sendMessage(pubsub_Load_fitting_panel, data=self.resultprojectfile[-6:])
                    pub.sendMessage(pubsub_Activate_Import)
                    pub.sendMessage(pubsub_OnFit_Graph, b=1)
                    pub.sendMessage(pubsub_gauge_to_zero)
                    self.update_Btn.SetFocus()
                    self.load_data = 1
                    self.OnLaunchCalc()

    def onUpdateConfigFile(self, folder):
        a = SaveFile4Diff(self)
        a.update_Config_File(os.path.join(current_dir, filename + '.ini'), self.folder_paths_dict[folder], folder)

    def Save_Deformation(self, case, name, data, supp=None):
        if self.project_name == "":
            path = os.path.join(self.folder_paths_dict[case], 'temp_' + '_input_' + name + '_coeff.txt') 
        else:
            path = os.path.join(self.folder_paths_dict['Save_as_file'], self.project_name + '_input_' + name + '_coeff.txt')                
            if supp == 1:
                path2remove = os.path.join(self.folder_paths_dict[case], 'temp_' + '_input_' + name + '_coeff.txt')
                if os.path.isfile(path2remove):
                    os.remove(path2remove)
        self.data_paths_dict[case] = path
        savetxt(path, data , fmt='%10.8f')

    def onSaveProject(self, event, case):
        a = P4Diff()
        if self.project_name == "":
            case = 1
        wildcard = "data file (*.ini)|*.ini|" \
                "All files (*.*)|*.*"
        textmessage = "Save file as ..."
        check = self.ReadDataField(0)
        if check == True and a.checkDataField == 1:
            if  self.data_paths_dict['DW_file'] != "" or self.data_paths_dict['Strain_file'] != ""\
            or self.data_paths_dict['XRD_file'] != "":
                if case == 1:
                    dlg = wx.FileDialog(self, message=textmessage,
                                        defaultDir=self.folder_paths_dict['Save_as_file'], defaultFile="",
                                        wildcard=wildcard, style=wx.SAVE)
                    if dlg.ShowModal() == wx.ID_OK:
                        paths = dlg.GetPaths()
                        self.folder_paths_dict['Save_as_file'] = os.path.split(paths[0])[0]
                        self.onUpdateConfigFile('Save_as_file')
                        dlg.Destroy()
                        P4Diff.path2ini = os.path.split(paths[0])[0]
                        if _platform == "linux" or _platform == "linux2":
                            P4Diff.path2inicomplete = paths[0] + '.ini'
                        elif _platform == "win32":
                            P4Diff.path2inicomplete = paths[0]
                        P4Diff.namefromini = os.path.splitext(os.path.basename(paths[0]))[0]
                        self.project_name = a.namefromini
                    else:
                        return
                b = SaveFile4Diff(self)
                P4Diff.allparameters = a.initial_parameters + a.fitting_parameters
                self.Save_Deformation('Strain_file', 'strain', a.sp, 1)
                self.Save_Deformation('DW_file', 'DW', a.dwp, 1)
                name = self.cb_crystalname.GetStringSelection()
                forsave = [name, self.data_paths_dict['DW_file'], self.data_paths_dict['Strain_file'],\
                self.data_paths_dict['XRD_file']]
                b.save_project(forsave, case)
                for ii in range(len(self.data_fields)):
                    self.data_fields[ii].SetBackgroundColour('#CCE5FF')
                pub.sendMessage(pubsub_changeColor_field4Save, case=0)
                self.Refresh()
                wx.Yield()
                sleep(0.8)
                logger.log(logging.INFO, "Data have been saved to " + str(a.path2inicomplete))
                for ii in range(len(self.data_fields)):
                    self.data_fields[ii].SetBackgroundColour('white')
                pub.sendMessage(pubsub_changeColor_field4Save, case=1)
                self.Refresh()
                wx.Yield()
                self.statusbar.SetStatusText(u"Data have been saved to " + str(a.path2inicomplete), 0)
                pub.sendMessage(pubsub_ChangeFrameTitle, NewTitle=Application_name + " - " + a.namefromini)
            else:
                dlg = GMD.GenericMessageDialog(None, "There is no data to save",
                    "Attention", agwStyle = wx.OK|wx.ICON_INFORMATION)
                dlg.ShowModal()
#                dlg = GMD.GenericMessageDialog(None, "Do you really want to close this application?",
#                "Confirm Exit", agwStyle = wx.OK|wx.CANCEL|wx.ICON_QUESTION)
#                result = dlg.ShowModal()
#                dlg.Destroy()
#                if result == wx.ID_OK:
#                    logger.log(logging.INFO, "End of the project\n")
#                    sys.exit()


    def ReadDataField(self, case=None):
        logger.log(logging.INFO, "Test if fields are full and contains float")
        check_empty = self.search4emptyfields()
        if check_empty == True:
            data_float = self.IsDataFloat()
            if data_float == True:
                logger.log(logging.INFO, "Test pass successfully")
                if case == 0:
                    pub.sendMessage(pubsub_Read_field4Save)
                return True
            else:
                logger.log(logging.WARNING, "There are some problem in the data")
                return False
                           
    def OnLaunchCalc(self):
        success = self.Read_Initial_File()
        if success == True:
            self.empty_field = 0
            self.calculsupplementaryparameters()
            self.Fit()  
            self.Layout()

    def OnLaunchCalc4Fit(self, event):
        a = P4Diff()
        if a.Iobs == [] or a.sp == [] or a.dwp == []:
            return
        else:
            self.empty_field = 1
            self.not_a_float = 1
            check_empty = self.search4emptyfields()
            if check_empty == True:
                data_float = self.IsDataFloat()
                if data_float == True:
                    self.empty_field = 0
                    self.calculsupplementaryparameters()
                    self.Fit()  
                    self.Layout()
                    P4Diff.success4Fit = 0
                else:
                    P4Diff.success4Fit = 1
            else:
                P4Diff.success4Fit = 1
            self.empty_field = 0
            self.not_a_float = 0

    def LimitReach(self, limit):
        limit_list = [15,16,18,19]
        for i in range(len(limit)):
            if limit[i] == False:
                self.data_fields[limit_list[i]].SetBackgroundColour('yellow')
                self.Refresh() 
        dlg = GMD.GenericMessageDialog(None, u"Deformation values are off limits\n" + \
        u"Please check the yellow field before launching the fit",
                "Attention", agwStyle = wx.OK|wx.ICON_INFORMATION|wx.CENTRE)
        dlg.ShowModal()
        for i in range(len(limit)):
            if limit[i] == False:
                self.data_fields[limit_list[i]].SetBackgroundColour('white')
                self.Refresh()                 
        
    def Read_Initial_File(self):
        a = P4Diff()
        b = ReadFile(self)
        if (os.path.exists(self.data_paths_dict['DW_file']) and os.path.exists(self.data_paths_dict['Strain_file'])\
            and os.path.exists(self.data_paths_dict['XRD_file'])) == True:
            try:
                """READING DW FILE"""
                b.read_dw_file(self.data_paths_dict['DW_file'])
                """READING Strain FILE"""
                b.read_strain_file(self.data_paths_dict['Strain_file'])
                """READING XRD FILE"""
                b.read_xrd_file(self.data_paths_dict['XRD_file'])
                P4Diff.Iobs = a.data_xrd[1]
                P4Diff.Iobs = a.Iobs / a.Iobs.max()
                P4Diff.Iobs_backup = a.Iobs
                P4Diff.th = (a.data_xrd[0])*pi/360.
                P4Diff.th_backup = (a.data_xrd[0])*pi/360.
                P4Diff.th4live = 2*a.th*180/pi
                P4Diff.dwp_backup = a.dwp
                P4Diff.sp_backup = a.sp
            except TypeError:
                logger.log(logging.WARNING, "!!! Please check your input file !!!")
            else:
                return True
        else:
            dlg = GMD.GenericMessageDialog(None, "Please, check that the input files really exists",
            "Attention", agwStyle = wx.OK|wx.ICON_INFORMATION)
            dlg.ShowModal()
            return False

    def onUpdate(self, event):
        self.empty_field = 0
        self.not_a_float = 0
        val = self.cb_crystalsymmetry.GetStringSelection()
        self.OnSelectSymmetry(event, val)
        check_empty = self.search4emptyfields()
        if check_empty == True:
            data_float = self.IsDataFloat()
            if data_float == True:
                a = P4Diff()
                if a.Iobs == [] or a.sp == [] or a.dwp == []:
                    return
                else:
                    self.empty_field = 0
                    self.calculsupplementaryparameters()
                    self.Fit()  
                    self.Layout()
                    P4Diff.success4Fit = 0
                    self.statusbar.SetStatusText(u"", 0)
                    pub.sendMessage(pubsub_gauge_to_zero)
            else:
                P4Diff.success4Fit = 1
        else:
            P4Diff.success4Fit = 1
        self.empty_field = 0
        self.not_a_float = 0

    def onUpdateFromDragAndDrop(self):
        self.empty_field = 0
        self.not_a_float = 0
        check_empty = self.search4emptyfields()
        if check_empty == True:
            data_float = self.IsDataFloat()
            if data_float == True:
                a = P4Diff()
                if a.Iobs == [] or a.sp == [] or a.dwp == []:
                    return
                else:
                    self.empty_field = 0
                    self.calculsupplementaryparameters()
                    self.Fit()  
                    self.Layout()
                    P4Diff.success4Fit = 0
            else:
                P4Diff.success4Fit = 1
        else:
            P4Diff.success4Fit = 1
        self.empty_field = 0
        self.not_a_float = 0

    def onUpdateBasis(self):
        self.StrainBfunction.GetValue()
        self.dwBfunction.GetValue()

    def calculsupplementaryparameters(self):
        a = P4Diff()
        name = self.cb_crystalname.GetStringSelection()
        self.spline_strain = self.cb_strainname.GetSelection()
        self.spline_DW = self.cb_dwname.GetSelection()
        temp = [self.spline_strain, self.spline_DW]
        P4Diff.splinenumber = temp
        self.par4diff = dict(zip(Parameters_panel_keys,a.initial_parameters))
        nb_slice, dw_func = self.OnChangeBasisFunction(self.par4diff['strain_basis_func'], self.par4diff['dw_basis_func'], \
                                                        self.spline_strain, self.spline_DW, self.par4diff['number_slices'])
        self.par4diff['dw_basis_func'] = dw_func
        self.par4diff['number_slices'] = nb_slice
        if name != []:
            P4Diff.par = np.concatenate((a.sp,a.dwp),axis=0)
            P4Diff.resol = f_pVoigt(a.th, [1, (a.th.min()+a.th.max())/2 ,\
                        self.par4diff['resolution']*pi/180, self.par4diff['shape']])
            
            P4Diff.d, P4Diff.Vol = f_dhkl_V(self.par4diff['h'],self.par4diff['k'],self.par4diff['l'],\
                                self.par4diff['a'], self.par4diff['b'],self.par4diff['c'],\
                                self.par4diff['alpha'], self.par4diff['beta'], self.par4diff['gamma']) ## CUBIQUE / FAUDRA METTRE UNE FORMULE GENERALE ICI
            
            P4Diff.G = a.re * self.par4diff['wavelength'] * self.par4diff['wavelength'] / (pi * a.Vol) ## Gamma : conversion Facteur Structure -> -(Polarisabilité)
            P4Diff.thB_S  = arcsin(self.par4diff['wavelength'] / (2*a.d))
            P4Diff.g0 = sin(a.thB_S - a.phi) ## gamma 0
            P4Diff.gH = -sin(a.thB_S + a.phi) ## gamma H
            P4Diff.b_S = a.g0 / a.gH
            P4Diff.t_l = self.par4diff['damaged_depth']/self.par4diff['number_slices'] ## épaisseur d'une lamelle
            P4Diff.z = arange(self.par4diff['number_slices']+1) * a.t_l ## hauteur
            P4Diff.FH, P4Diff.FmH, P4Diff.F0 = f_FH(self.par4diff['h'],self.par4diff['k'],\
                                self.par4diff['l'],self.par4diff['wavelength'],a.thB_S,a.z, name)
                                
            P4Diff.Ical = f_Refl(self.par4diff) ## évaluation RAPIDE
            
            P4Diff.I_i = a.Ical/a.Ical.max() + self.par4diff['background']
            P4Diff.depth = self.par4diff['damaged_depth']-a.z
                        
            P4Diff.DW_i = f_DW(a.z, a.dwp, self.par4diff['damaged_depth'], self.spline_DW)
            P4Diff.strain_i = f_strain(a.z, a.sp, self.par4diff['damaged_depth'], self.spline_strain)

            t = self.par4diff['damaged_depth']
            P4Diff.x_sp = t - linspace(1, len(a.sp), len(a.sp))*t / (len(a.sp))  # generate depth (x axis) for the strain basis function
            P4Diff.x_dwp = t - linspace(1, len(a.dwp), len(a.dwp))*t / (len(a.dwp))
            
            self.Shifted_and_draw_curves()
        else:
            logger.log(logging.WARNING, "check if the structure file really exists")

    def f_strain_DW(self):
        a = P4Diff()
        
        P4Diff.sp = a._fp_min[:int(self.par4diff['strain_basis_func'])]
        P4Diff.dwp = a._fp_min[-1*int(self.par4diff['dw_basis_func']):]
        
        P4Diff.DW_i = f_DW(a.z, a.dwp, self.par4diff['damaged_depth'], self.spline_DW)
        P4Diff.strain_i = f_strain(a.z, a.sp, self.par4diff['damaged_depth'], self.spline_strain)

        t = self.par4diff['damaged_depth']
        P4Diff.x_sp = t - linspace(1, len(a.sp), len(a.sp))*t / (len(a.sp))  # generate depth (x axis) for the strain basis function
        P4Diff.x_dwp = t - linspace(1, len(a.dwp), len(a.dwp))*t / (len(a.dwp))
        
        self.Shifted_and_draw_curves()

    def Shifted_and_draw_curves(self):
        a = P4Diff()
        
        shifted_sp = append(array([0.]),a.sp[:-1:]) # shifts the array so as to set center ofl each Bspline on the maximum
        shifted_dwp = append(array([1.]),a.dwp[:-1:])
#        print 'shifted_sp.shape', shifted_sp.shape
#        print 'a.strain_i[ in1d(a.depth,  a.x_sp)].shape', a.strain_i[ in1d(around(a.depth, decimals=3),  around(a.x_sp,decimals=3))].shape
#        print 'a.x_sp.shape', a.x_sp.shape

        P4Diff.scale_strain = shifted_sp /a.strain_i[ in1d(around(a.depth, decimals=3),  around(a.x_sp,decimals=3))]
        P4Diff.scale_strain[a.scale_strain==0] = 1. #avoids div by 0 error
        P4Diff.scale_dw = shifted_dwp /a.DW_i[ in1d(around(a.depth, decimals=3),  around(a.x_dwp, decimals=3))]
        P4Diff.scale_dw[a.scale_dw==0] = 1.

        P4Diff.DW_shifted = shifted_dwp/a.scale_dw
        P4Diff.strain_shifted = shifted_sp*100./a.scale_strain
        P4Diff.stain_out_save = a.sp[-1]
        P4Diff.dw_out_save = a.dwp[-1]
        
        self.DW_horizontal_ctrl.SetLabel(str(a.DW_multiplication))
        self.strain_horizontal_ctrl.SetLabel(str(a.strain_multiplication))

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
                dlg = GMD.GenericMessageDialog(None, "Please, fill the red empty fields before to continue",
                "Attention", agwStyle = wx.OK|wx.ICON_INFORMATION)
                dlg.ShowModal()
                self.empty_field = 1
                for ii in empty_fields:
                    self.data_fields[ii].SetBackgroundColour('white')
                self.Refresh()            
        return check_empty        

    def Is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    def IsDataFloat(self):
        IsFloat = []
        dataFloat = True
        for i in range(len(Parameters_panel_keys)):
            self.resultprojectfile[i+header_project] = self.data_fields[i].GetValue()
        for i in range(len(Parameters_panel_keys)):
            a = self.data_fields[i].GetValue()
#            print i, a 
            IsFloat.append(self.Is_number(a))
        if False in IsFloat:
            dataFloat = False
            if self.not_a_float == 0:
                StringPosition = [i for i,x in enumerate(IsFloat) if x == False]
                for ii in StringPosition:
                    self.data_fields[ii].SetBackgroundColour('green')
                self.Refresh() 
                dlg = GMD.GenericMessageDialog(None, "Please, fill correctly the fields before to continue",
                "Attention", agwStyle = wx.OK|wx.ICON_INFORMATION)
                dlg.ShowModal()
                
                for ii in StringPosition:
                    self.data_fields[ii].SetBackgroundColour('white')
                self.Refresh()
        else:
            self.empty_field = 0
            self.parent.notebook.EnableTab(1, True)
#            print 'Nb_slice_combo', self.Nb_slice_combo.GetValue()
            temp = [float(ii) for ii in self.resultprojectfile[4:-6:]]
            P4Diff.initial_parameters = temp
#            print temp
        return dataFloat
        
    def Reset_Deformation_Multiplication(self):
        a = P4Diff()
        P4Diff.strain_multiplication = 1.0
        P4Diff.DW_multiplication = 1.0
        self.DW_horizontal_ctrl.SetLabel(str(a.DW_multiplication))
        self.strain_horizontal_ctrl.SetLabel(str(a.strain_multiplication))

    def OnChangeBasisFunction(self, strain, dw, spline_strain, spline_DW, slice_):
        a = P4Diff()
        strain_change = 0
        dw_change = 0
        slice_change = 0
        if  strain != float(a.strain_basis_backup):
            P4Diff.strain_basis_backup = strain
            strain_change = 1
        if  dw != a.dw_basis_backup:
            P4Diff.dw_basis_backup = dw
            dw_change = 1
        if slice_ != float(a.slice_backup):
            P4Diff.slice_backup = slice_
            slice_change = 1
        if strain_change == 1 or dw_change == 1 or slice_change == 1:
            self.par4diff['damaged_depth'], self.par4diff['number_slices'] = self.find_nearest_Damaged_depth(self.par4diff['damaged_depth'],\
                                                                                                    self.par4diff['number_slices'], strain)
            slice_val = self.par4diff['number_slices']
            damaged_val = self.par4diff['damaged_depth']
            dw = self.find_nearest_dw(self.par4diff['number_slices'], dw, strain, strain_change, dw_change, slice_change)
            self.damaged_depth.SetValue(str(damaged_val))
            self.dwBfunction.SetValue(str(dw))
            P4Diff.t_l = damaged_val/slice_val
            P4Diff.z = arange(slice_val+1) * a.t_l
            P4Diff.dwp = old2new_DW(a.z, a.dwp, damaged_val, dw, spline_DW)
            P4Diff.sp = old2new_strain(a.z, a.sp, damaged_val, strain, spline_strain)
            P4Diff.dwp_backup = deepcopy(a.dwp)
            P4Diff.sp_backup = deepcopy(a.sp)
            self.Layout()
            self.Nb_slice.SetValue(str(slice_val))
            return slice_val, dw
        else:
            slice_val = int(float(self.Nb_slice.GetValue()))
            return slice_val, dw

    def find_nearest_Damaged_depth(self, damaged, N, Nstrain):
        if damaged%Nstrain != 0:
            damaged = round(damaged/Nstrain)*Nstrain
        if N/Nstrain != 0:
            N = round(N/Nstrain)*Nstrain
        return damaged, N

    def find_nearest(self, array, value):
        array = [int(a) for a in array]
        array = np.array(array)
        idx = (np.abs(array-value)).argmin()
        return idx

    def find_nearest_dw(self, N, Ndw, Nstrain, strain_change, dw_change, slice_change):
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
            
    def OnSelectNbSlice(self, event):
        self.Nb_slice_hide.SetValue(str(event.GetString())) 
                 
    def OnPageChanged(self, event):
        self.Fit()  
        self.Layout()
        self.update_Btn.SetFocus()
        if self.load_data == 1:
            self.onUpdate(event)
            if self.empty_field == 1:
                event.Veto()
                self.parent.notebook.EnableTab(1, False)
                self.Fit()  
                self.Layout()

