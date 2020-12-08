#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

# =============================================================================
# Radmax Calcul module
# =============================================================================

import sys
import wx

sys.path.insert(0, './modules')
from pubsub import pub

import wx.lib.agw.genericmessagedialog as GMD

from copy import deepcopy

from scipy import arcsin, sin, in1d, around
import numpy as np
from numpy import arange, array, asarray
from collections import OrderedDict

import os
import Parameters4Radmax as p4R
from Parameters4Radmax import P4Rm

from Read4Radmax import ReadFile, SaveFile4Diff
from Def_Strain4Radmax import f_strain, old2new_strain, fit_input_strain
from Def_DW4Radmax import f_DW, old2new_DW, fit_input_DW
from Def_XRD4Radmax import f_Refl
from Def_Fh4Radmax import f_FH
from Tools4Radmax import f_dhkl_V

import logging
logger = logging.getLogger(__name__)

sp_pv_initial = [2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.05]
dwp_pv_initial = [0.5, 0.2, 0.1, 0.1, 0.1, 0.1, 0.85]

"""Pubsub message"""

pubsub_Load_project = "LoadProject"
pubsub_Read_field4Save = "ReadField4Save"
pubsub_ChangeFrameTitle = "ChangeFrameTitle"
pubsub_Activate_Import = "ActivateImport"
pubsub_OnFit_Graph = "OnFitGraph"
pubsub_gauge_to_zero = "Gauge2zero"

pubsub_change_basic_function = "ChangeBasicFunction"
pubsub_update_initial_panel = "UpdateInitialPanel"
pubsub_Draw_XRD = "DrawXRD"
pubsub_Draw_Strain = "DrawStrain"
pubsub_Draw_DW = "DrawDW"
pubsub_update_crystal_list = "UpdateCrystalList"
pubsub_test_some_field = "TestSomeField"
pubsub_update_sp_dwp_eta = "UpdatespdwpEta"

pubsub_change_update_btn_state = "ChangeUpdateButtonState"

pubsub_Fill_List_coef = "FillListCoef"


# ------------------------------------------------------------------------------
class Calcul4Radmax():

    def read_crystal_list(self):
        """
        Reading of the structures directory
        we list all the files present in this directory
        we get back the files name, sort them by name
        and used them in the crsytal combobox
        """
        if os.listdir(p4R.structures_name) != []:
            P4Rm.crystal_list = sorted(list(os.listdir(p4R.structures_name)))
        pub.sendMessage(pubsub_update_crystal_list)

    def on_load_project(self, paths):
        a = P4Rm()
        b = ReadFile()
        b.on_read_init_parameters(paths, p4R.ExperimentFile)
        datafromini = b.read_result_value()

        self.on_reset_deformation_multiplication()
        self.on_init_dictionnaries()

        P4Rm.ProjectFileData = datafromini[5:]

        i = 0
        for k in p4R.Exp_file_all_section:
            if k in p4R.Exp_read_only:
                P4Rm.AllDataDict[k] = float(datafromini[i])
            else:
                P4Rm.AllDataDict[k] = datafromini[i]
            i += 1

        i = 0
        for name in ['Compound_name', 'substrate_name', 'DW_file',
                     'Strain_file', 'XRD_file']:
            P4Rm.PathDict[name] = datafromini[i]
            i += 1

        P4Rm.DefaultDict['project_folder'] = os.path.split(paths)[0]
        P4Rm.PathDict['path2ini'] = os.path.split(paths)[0]
        P4Rm.PathDict['path2inicomplete'] = paths
        P4Rm.PathDict['namefromini'] = os.path.splitext(
                                           os.path.basename(paths))[0]
        self.on_update_config_file('project_folder')
        if a.ProjectFileData == []:
            msg_ = ("Please, pay attention to your input files," +
                    "there are some mistakes in the data")
            dlg = GMD.GenericMessageDialog(None, msg_, "Attention",
                                           agwStyle=wx.OK |
                                           wx.ICON_INFORMATION)
            dlg.ShowModal()
        else:
            P4Rm.PathDict['project_name'] = os.path.splitext(
                                                os.path.basename(paths))[0]

        success = self.on_read_initial_file()
        if success:
            self.on_load_and_read_data()

    def on_load_from_Database(self):
        a = P4Rm()
        P4Rm.FitDict['New&Load'] = 1
        self.on_reset_deformation_multiplication()
        self.on_calc_from_xrd()

        P4Rm.ParamDictbackup['dwp'] = deepcopy(a.ParamDict['dwp'])
        P4Rm.ParamDictbackup['sp'] = deepcopy(a.ParamDict['sp'])

        P4Rm.ParamDict['sp_abrupt'] = deepcopy(a.ParamDict['sp'])
        P4Rm.ParamDict['dwp_abrupt'] = deepcopy(a.ParamDict['dwp'])

        P4Rm.ParamDict['sp_smooth'] = deepcopy(a.ParamDict['sp'])
        P4Rm.ParamDict['dwp_smooth'] = deepcopy(a.ParamDict['dwp'])

        self.on_load_and_read_data()

    def on_load_and_read_data(self):
        a = P4Rm()
        pub.sendMessage(pubsub_Load_project)
        pub.sendMessage(pubsub_Read_field4Save)

        if (a.checkInitialField == 1 and a.checkGeometryField == 1 and
            a.checkFittingField == 1):
            P4Rm.allparameters = (a.initial_parameters +
                                  a.fitting_parameters +
                                  a.sample_geometry)
            i = 0
            for k in p4R.IP_p + p4R.F_p + p4R.SG_p:
                P4Rm.AllDataDict[k] = a.allparameters[i]
                i += 1

            pub.sendMessage(pubsub_test_some_field)

            P4Rm.ParamDict['slice_backup'] = (a.AllDataDict['number_slices'])
            P4Rm.ParamDict['damaged_value_backup'] = (a.AllDataDict['damaged_depth'])

            P4Rm.ParamDict['strain_basis_backup'] = a.AllDataDict['strain_basis_func']
            P4Rm.ParamDict['dw_basis_backup'] = a.AllDataDict['dw_basis_func']

            P4Rm.ParamDict['strain_sm_ab_bkp'] = a.AllDataDict['strain_basis_func']
            P4Rm.ParamDict['dw_sm_ab_bkp'] = a.AllDataDict['dw_basis_func']

            if a.PathDict['Compound_name'] in a.crystal_list:
                msg_ = "Config file successfully loaded"
                logger.log(logging.INFO, msg_)
            else:
                msg_ = ("You need to add the proper strcuture" +
                        "to continue")
                logger.log(logging.INFO, msg_)
            '''change name of the main title window'''

            self.on_init_sp_dwp()

            pub.sendMessage(pubsub_ChangeFrameTitle,
                            NewTitle=(p4R.Application_name +
                                      " - " +
                                      a.PathDict['project_name']))
            pub.sendMessage(pubsub_Activate_Import)
            pub.sendMessage(pubsub_OnFit_Graph, b=1)
            pub.sendMessage(pubsub_gauge_to_zero)
            self.on_reset_deformation_multiplication()
            self.on_calcul_parameters()

    def on_new_project(self):
        """
        Launch new project with default inital parameters
        all variables are initialized and graph are eventually removed
        """
        a = P4Rm()
        self.read_crystal_list()
#        self.on_reset_deformation_multiplication()

        pub.sendMessage(pubsub_Load_project, b=1)

        P4Rm.xrd_graph_loaded = 0
        self.on_init_dictionnaries()
                        
        pub.sendMessage(pubsub_Read_field4Save)

        if (a.checkInitialField == 1 and a.checkGeometryField == 1 and
            a.checkFittingField == 1):
            P4Rm.allparameters = (a.initial_parameters +
                                  a.fitting_parameters +
                                  a.sample_geometry)
            i = 0
            for k in p4R.IP_p + p4R.F_p + p4R.SG_p:
                P4Rm.AllDataDict[k] = a.allparameters[i]
                i += 1

            P4Rm.ParamDict['slice_backup'] = a.AllDataDict['number_slices']
            P4Rm.ParamDict['strain_basis_backup'] = (a.AllDataDict['strain_basis_func'])
            P4Rm.ParamDict['dw_basis_backup'] = a.AllDataDict['dw_basis_func']

            P4Rm.ParamDict['strain_sm_ab_bkp'] = a.AllDataDict['strain_basis_func']
            P4Rm.ParamDict['dw_sm_ab_bkp'] = a.AllDataDict['dw_basis_func']

            P4Rm.ParamDict['damaged_value_backup'] = (a.AllDataDict['damaged_depth'])
                                                          
            P4Rm.ParamDict['t_l'] = (a.AllDataDict['damaged_depth'] /
                                         a.AllDataDict['number_slices'])
            P4Rm.ParamDict['z'] = (arange(a.AllDataDict['number_slices']+1) *
                                       a.ParamDict['t_l'])
            P4Rm.ParamDict['depth'] = (a.AllDataDict['damaged_depth'] -
                                           a.ParamDict['z'])
            P4Rm.ParamDict['sp'] = int(a.AllDataDict['strain_basis_func'])*[1]
            P4Rm.ParamDict['dwp'] = int(a.AllDataDict['dw_basis_func'])*[1]
            P4Rm.ParamDict['sp_abrupt'] = int(a.AllDataDict['strain_basis_func'])*[1]
            P4Rm.ParamDict['dwp_abrupt'] = int(a.AllDataDict['dw_basis_func'])*[1]
            
            P4Rm.ParamDict['sp_smooth'] = int(a.AllDataDict['strain_basis_func'])*[1]
            P4Rm.ParamDict['dwp_smooth'] = int(a.AllDataDict['dw_basis_func'])*[1]

            funky = 2  # pseudo-voigt
            P4Rm.AllDataDict['function_profile'] = funky
            P4Rm.ParamDict['func_profile'] = p4R.FitFunction_choice[funky]

            self.on_init_sp_dwp()

            pub.sendMessage(pubsub_Draw_XRD, b=2)
            pub.sendMessage(pubsub_Activate_Import)

            self.calc_strain()
            self.calc_DW()
            spline_strain = a.spline_strain
            spline_DW = a.spline_DW
            nb_slice, dw_func = self.OnChangeBasisFunction(
                                a.AllDataDict['strain_basis_func'],
                                a.AllDataDict['dw_basis_func'],
                                spline_strain, spline_DW,
                                a.AllDataDict['number_slices'])

            self.on_reset_deformation_multiplication()
            self.on_copy_default2_alldata()
            new_name = p4R.Application_name + " - " + 'New Project'

            pub.sendMessage(pubsub_ChangeFrameTitle, NewTitle=new_name)
            pub.sendMessage(pubsub_OnFit_Graph)
            pub.sendMessage(pubsub_gauge_to_zero)

    def on_init_sp_dwp(self):
        a = P4Rm()
        P4Rm.ParamDict['sp_pv'] = sp_pv_initial
        P4Rm.ParamDict['dwp_pv'] = dwp_pv_initial

        P4Rm.ParamDict['state_sp'] = len(a.ParamDict['sp'])*[True]
        P4Rm.ParamDict['state_dwp'] = len(a.ParamDict['dwp'])*[True]

    def on_init_dictionnaries(self):
        ncolumnParam = len(p4R.Params4Radmax)*[""]
        ncolumnPath = len(p4R.Path4Radmax)*[""]
        ncolumnAllData = len(p4R.Exp_file_all_section)*[""]
        ncolumnFit = len(p4R.FitData)*[0, 0, 0, "", False, "",
                                       "", "", None, "", 1]
        P4Rm.AllDataDict = OrderedDict(zip(p4R.Exp_file_all_section, ncolumnAllData))
        P4Rm.ParamDict = OrderedDict(zip(p4R.Params4Radmax, ncolumnParam))
        P4Rm.PathDict = OrderedDict(zip(p4R.Path4Radmax, ncolumnPath))
        P4Rm.FitDict = OrderedDict(zip(p4R.FitData, ncolumnFit))

    def on_copy_default2_alldata(self):
        a = P4Rm()
        for k in p4R.Exp_read_only:
            P4Rm.AllDataDict[k] = a.DefaultDict[k]

    def on_test_substrate(self):
        a = P4Rm()
        if a.AllDataDict['film_thick'] < a.AllDataDict['damaged_depth']:
            P4Rm.AllDataDict['film_thick'] = a.AllDataDict['damaged_depth'] + 1
            P4Rm.FitDict['New&Load'] = 1
            pub.sendMessage(pubsub_Load_project)
        if a.AllDataDict['dw_thick'] not in [0, 1]:
            P4Rm.AllDataDict['dw_thick'] = 1
            P4Rm.FitDict['New&Load'] = 1
            pub.sendMessage(pubsub_Load_project)

    def on_update_config_file(self, name_key):
        a = P4Rm()
        b = SaveFile4Diff()
        name = p4R.filename + '.ini'
        b.on_update_config_file(os.path.join(p4R.current_dir, name),
                                a.DefaultDict[name_key], name_key)

    def on_launch_calc(self):
        success = self.on_read_initial_file()
        if success:
            self.on_calcul_parameters()

    def on_read_initial_file(self):
        a = P4Rm()
        b = ReadFile()
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
                self.on_calc_from_xrd()

                P4Rm.ParamDictbackup['dwp'] = a.ParamDict['dwp']
                P4Rm.ParamDictbackup['sp'] = a.ParamDict['sp']

                P4Rm.ParamDict['sp_abrupt'] = a.ParamDict['sp']
                P4Rm.ParamDict['dwp_abrupt'] = a.ParamDict['dwp']

                P4Rm.ParamDict['sp_smooth'] = a.ParamDict['sp']
                P4Rm.ParamDict['dwp_smooth'] = a.ParamDict['dwp']

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

    def on_calc_from_xrd(self):
        a = P4Rm()
        P4Rm.ParamDict['Iobs'] = a.ParamDict['data_xrd'][1]
        minval = np.min(a.ParamDict['Iobs'][np.nonzero(a.ParamDict['Iobs'])])
        P4Rm.ParamDict['Iobs'][a.ParamDict['Iobs'] == 0] = minval
        P4Rm.ParamDict['Iobs'] = a.ParamDict['Iobs'] / a.ParamDict['Iobs'].max()
        P4Rm.ParamDict['th'] = ((a.ParamDict['data_xrd'][0]) *
                                np.pi/360.)
        P4Rm.ParamDict['th4live'] = 2*a.ParamDict['th']*180/np.pi

        P4Rm.ParamDictbackup['Iobs'] = a.ParamDict['Iobs']
        P4Rm.ParamDictbackup['th'] = a.ParamDict['th']
        P4Rm.xrd_graph_loaded = 1
        pub.sendMessage(pubsub_change_update_btn_state)

    def on_make_param_func(self):
        a = P4Rm()
        func = a.ParamDict['func_profile']
        fwhml = a.AllDataDict['width_left']*np.pi/180
        fwhmr = a.AllDataDict['width_right']*np.pi/180
        etal = a.AllDataDict['shape_left']
        etar = a.AllDataDict['shape_right']
        b_bell = a.AllDataDict['b_bell']
        pos = (a.ParamDict['th'].min() + a.ParamDict['th'].max())/2
        if func.__name__ == "f_Gauss" or func.__name__ == "f_Lorentz":
            param_func = [1, pos, fwhml]
        elif func.__name__ == "f_pVoigt":
            param_func = [1, pos, fwhml, etal]
        elif func.__name__ == "f_gbell":
            param_func = [1, pos, fwhml, b_bell]
        elif func.__name__ == "f_splitpV":
            param_func = [1, pos, fwhml, fwhmr, etal, etar]
        P4Rm.ParamDict['param_func_profile'] = param_func

    def on_calcul_parameters(self):
        a = P4Rm()
        name = a.PathDict['Compound_name']
        name_s = a.PathDict['substrate_name']

        self.on_test_substrate()

        spline_strain = a.spline_strain
        spline_DW = a.spline_DW
        temp = [spline_strain, spline_DW]
        P4Rm.splinenumber = temp

        if a.AllDataDict['model'] != 2:
            nb_slice, dw_func = self.OnChangeBasisFunction(
                                a.AllDataDict['strain_basis_func'],
                                a.AllDataDict['dw_basis_func'],
                                spline_strain, spline_DW,
                                a.AllDataDict['number_slices'])
            a.AllDataDict['dw_basis_func'] = dw_func
            a.AllDataDict['number_slices'] = nb_slice

        if name != []:
            self.on_make_param_func()
            P4Rm.ParamDict['par'] = np.concatenate((a.ParamDict['sp'],
                                                    a.ParamDict['dwp']),
                                                   axis=0)
            x_ = a.ParamDict['th']
            param = a.ParamDict['param_func_profile']
            P4Rm.ParamDict['resol'] = a.ParamDict['func_profile'](x_, param)

            P4Rm.ParamDict['t_l'] = (a.AllDataDict['damaged_depth'] /
                                     a.AllDataDict['number_slices'])
            P4Rm.ParamDict['z'] = (arange(a.AllDataDict['number_slices']+1) *
                                   a.ParamDict['t_l'])

# =============================================================================
# Material Data
# =============================================================================
            P4Rm.ParamDict['d'], P4Rm.ParamDict['Vol'] = f_dhkl_V(
                                        a.AllDataDict['h'], a.AllDataDict['k'],
                                        a.AllDataDict['l'], a.AllDataDict['a'],
                                        a.AllDataDict['b'], a.AllDataDict['c'],
                                        a.AllDataDict['alpha'],
                                        a.AllDataDict['beta'],
                                        a.AllDataDict['gamma'])
            temp_1 = (a.ConstDict['re'] * a.AllDataDict['wavelength'] *
                      a.AllDataDict['wavelength'])
            P4Rm.ParamDict['G'] = temp_1 / (np.pi * a.ParamDict['Vol'])
            temp_2 = arcsin(a.AllDataDict['wavelength'] / (2*a.ParamDict['d']))
            P4Rm.ParamDict['thB_S'] = temp_2
            temp_3 = a.ConstDict['phi']
            P4Rm.ParamDict['g0'] = sin(a.ParamDict['thB_S'] - temp_3)
            P4Rm.ParamDict['gH'] = -sin(a.ParamDict['thB_S'] + temp_3)
            P4Rm.ParamDict['b_S'] = a.ParamDict['g0'] / a.ParamDict['gH']
            temp_4 = f_FH(a.AllDataDict['h'], a.AllDataDict['k'],
                          a.AllDataDict['l'], a.AllDataDict['wavelength'],
                          a.ParamDict['thB_S'], a.ParamDict['z'], name)
            P4Rm.ParamDict['FH'] = temp_4[0]
            P4Rm.ParamDict['FmH'] = temp_4[1]
            P4Rm.ParamDict['F0'] = temp_4[2]

# =============================================================================
# Substrate Data
# =============================================================================
            P4Rm.ParamDict['d_s'], P4Rm.ParamDict['Vol_s'] = f_dhkl_V(
                                        a.AllDataDict['h_s'],
                                        a.AllDataDict['k_s'],
                                        a.AllDataDict['l_s'],
                                        a.AllDataDict['a_s'],
                                        a.AllDataDict['b_s'],
                                        a.AllDataDict['c_s'],
                                        a.AllDataDict['alpha_s'],
                                        a.AllDataDict['beta_s'],
                                        a.AllDataDict['gamma_s'])
            temp_1 = (a.ConstDict['re'] * a.AllDataDict['wavelength'] *
                      a.AllDataDict['wavelength'])
            P4Rm.ParamDict['G_s'] = temp_1 / (np.pi * a.ParamDict['Vol_s'])
            temp_2 = arcsin(a.AllDataDict['wavelength'] /
                            (2*a.ParamDict['d_s']))
            P4Rm.ParamDict['thB_S_s'] = temp_2
            temp_3 = a.ConstDict['phi_s']
            P4Rm.ParamDict['g0_s'] = sin(a.ParamDict['thB_S_s'] - temp_3)
            P4Rm.ParamDict['gH_s'] = -sin(a.ParamDict['thB_S_s'] + temp_3)
            P4Rm.ParamDict['b_S_s'] = a.ParamDict['g0_s'] / a.ParamDict['gH_s']
            temp_4 = f_FH(a.AllDataDict['h_s'], a.AllDataDict['k_s'],
                          a.AllDataDict['l_s'],
                          a.AllDataDict['wavelength'],
                          a.ParamDict['thB_S_s'],
                          a.ParamDict['z'], name_s)
            P4Rm.ParamDict['FH_s'] = temp_4[0]
            P4Rm.ParamDict['FmH_s'] = temp_4[1]
            P4Rm.ParamDict['F0_s'] = temp_4[2]

# =============================================================================
            P4Rm.ParamDict['Ical'] = f_Refl(a.AllDataDict['geometry'])

            P4Rm.ParamDict['I_i'] = (a.ParamDict['Ical'] /
                                     a.ParamDict['Ical'].max() +
                                     a.AllDataDict['background'])
            P4Rm.ParamDict['depth'] = (a.AllDataDict['damaged_depth'] -
                                       a.ParamDict['z'])

            P4Rm.ParamDict['DW_i'] = f_DW(
                                         a.ParamDict['z'],
                                         a.ParamDict['dwp'],
                                         a.AllDataDict['damaged_depth'],
                                         spline_DW)
            P4Rm.ParamDict['strain_i'] = f_strain(
                                             a.ParamDict['z'],
                                             a.ParamDict['sp'],
                                             a.AllDataDict['damaged_depth'],
                                             spline_strain)
            t = a.AllDataDict['damaged_depth']

            if a.AllDataDict['damaged_depth'] > 0:
                self.on_shifted_sp_curves(t)
                self.on_shifted_dwp_curves(t)
            self.draw_curves()
        else:
            msg_ = "check if the structure file really exists"
            logger.log(logging.WARNING, msg_)

    def f_strain_DW(self):
        a = P4Rm()
        P4Rm.ParamDict['sp'] = a.ParamDict['_fp_min'][:int(a.AllDataDict['strain_basis_func'])]
        P4Rm.ParamDict['dwp'] = a.ParamDict['_fp_min'][-1*int(a.AllDataDict['dw_basis_func']):]

        P4Rm.ParamDict['DW_i'] = f_DW(
                                     a.ParamDict['z'], a.ParamDict['dwp'],
                                     a.AllDataDict['damaged_depth'],
                                     a.spline_DW)
        P4Rm.ParamDict['strain_i'] = f_strain(
                                         a.ParamDict['z'], a.ParamDict['sp'],
                                         a.AllDataDict['damaged_depth'],
                                         a.spline_strain)

        t = a.AllDataDict['damaged_depth']
        self.on_shifted_sp_curves(t)
        self.on_shifted_dwp_curves(t)
        self.draw_curves()

    def on_shifted_dwp_curves(self, t):
        a = P4Rm()
        if a.AllDataDict['model'] == 0:
            temp_1 = arange(2, len(a.ParamDict['dwp'])+1)
            temp_2 = temp_1 * t / (len(a.ParamDict['dwp']))
            P4Rm.ParamDict['x_dwp'] = t - temp_2
            shifted_dwp = a.ParamDict['dwp'][:-1:]
            temp_3 = in1d(around(a.ParamDict['depth'], decimals=3),
                          around(a.ParamDict['x_dwp'], decimals=3))
            temp_4 = a.ParamDict['DW_i'][temp_3]
            P4Rm.ParamDict['scale_dw'] = shifted_dwp / temp_4
            P4Rm.ParamDict['scale_dw'][a.ParamDict['scale_dw'] == 0] = 1.

            P4Rm.ParamDict['DW_shifted'] = shifted_dwp/a.ParamDict['scale_dw']
            P4Rm.ParamDict['dw_out'] = a.ParamDict['dwp'][-1]

        elif a.AllDataDict['model'] == 1:
            temp_1 = arange(0, len(a.ParamDict['dwp'])+1-3)
            temp_2 = temp_1 * t / (len(a.ParamDict['dwp'])-3)
            P4Rm.ParamDict['x_dwp'] = t - temp_2
            shifted_dwp = a.ParamDict['dwp'][1:-1:]
            temp_3 = in1d(around(a.ParamDict['depth'], decimals=3),
                          around(a.ParamDict['x_dwp'], decimals=3))
            temp_4 = a.ParamDict['DW_i'][temp_3]
            P4Rm.ParamDict['scale_dw'] = shifted_dwp / temp_4
            P4Rm.ParamDict['scale_dw'][a.ParamDict['scale_dw'] == 0] = 1.

            P4Rm.ParamDict['DW_shifted'] = shifted_dwp/a.ParamDict['scale_dw']
            temp_5 = array([a.ParamDict['dwp'][0], a.ParamDict['dwp'][-1]])
            P4Rm.ParamDict['dw_out'] = temp_5

        elif a.AllDataDict['model'] == 2:
            x_dw_temp = []
            x_dw_temp.append(t*(1-a.ParamDict['dwp'][1]))
            x_dw_temp.append(t*(1-a.ParamDict['dwp'][1] +
                             a.ParamDict['dwp'][2]/2))
            x_dw_temp.append(t*(1-a.ParamDict['dwp'][1] -
                             a.ParamDict['dwp'][3]/2))
            x_dw_temp.append(t*0.05)
            P4Rm.ParamDict['x_dwp'] = x_dw_temp

            y_dw_temp = []
            y_dw_temp.append(a.ParamDict['dwp'][0])
            y_dw_temp.append(1. - (1-a.ParamDict['dwp'][0])/2)
            y_dw_temp.append(1. - (1-a.ParamDict['dwp'][0])/2 -
                             (1-a.ParamDict['dwp'][6])/2)
            y_dw_temp.append(a.ParamDict['dwp'][6])
            P4Rm.ParamDict['DW_shifted'] = y_dw_temp

    def on_shifted_sp_curves(self, t):
        a = P4Rm()
        if a.AllDataDict['model'] == 0:
            temp_1 = arange(2, len(a.ParamDict['sp'])+1)
            temp_2 = temp_1 * t / (len(a.ParamDict['sp']))
            P4Rm.ParamDict['x_sp'] = t - temp_2
            shifted_sp = a.ParamDict['sp'][:-1:]
            temp_3 = in1d(around(a.ParamDict['depth'], decimals=3),
                          around(a.ParamDict['x_sp'], decimals=3))
            temp_4 = a.ParamDict['strain_i'][temp_3]
            P4Rm.ParamDict['scale_strain'] = shifted_sp / temp_4
            P4Rm.ParamDict['scale_strain'][a.ParamDict['scale_strain'] == 0] = 1.
            P4Rm.ParamDict['strain_shifted'] = asarray(shifted_sp)*100./a.ParamDict['scale_strain']
            P4Rm.ParamDict['stain_out'] = a.ParamDict['sp'][-1]

        elif a.AllDataDict['model'] == 1:
            temp_1 = arange(0, len(a.ParamDict['sp'])+1-3)
            temp_2 = temp_1 * t / (len(a.ParamDict['sp'])-3)
            P4Rm.ParamDict['x_sp'] = t - temp_2
            shifted_sp = a.ParamDict['sp'][1:-1:]
            temp_3 = in1d(around(a.ParamDict['depth'], decimals=3),
                          around(a.ParamDict['x_sp'], decimals=3))
            temp_4 = a.ParamDict['strain_i'][temp_3]
            P4Rm.ParamDict['scale_strain'] = shifted_sp / temp_4
            P4Rm.ParamDict['scale_strain'][a.ParamDict['scale_strain'] == 0] = 1.

            P4Rm.ParamDict['strain_shifted'] = asarray(shifted_sp)*100./a.ParamDict['scale_strain']
            temp_5 = array([a.ParamDict['sp'][0], a.ParamDict['sp'][-1]])
            P4Rm.ParamDict['stain_out'] = temp_5

        elif a.AllDataDict['model'] == 2:
            x_sp_temp = []
            x_sp_temp.append(t*(1-a.ParamDict['sp'][1]))
            x_sp_temp.append(t*(1-a.ParamDict['sp'][1] +
                             a.ParamDict['sp'][2]/2))
            x_sp_temp.append(t*(1-a.ParamDict['sp'][1] -
                             a.ParamDict['sp'][3]/2))
            x_sp_temp.append(t*0.05)
            P4Rm.ParamDict['x_sp'] = x_sp_temp

            y_sp_temp = []
            y_sp_temp.append(a.ParamDict['sp'][0])
            y_sp_temp.append(a.ParamDict['sp'][0]/2)
            y_sp_temp.append(a.ParamDict['sp'][0]/2 + a.ParamDict['sp'][6]/2)
            y_sp_temp.append(a.ParamDict['sp'][6])
            P4Rm.ParamDict['strain_shifted'] = y_sp_temp


    def draw_curves(self):
        a = P4Rm()
        pub.sendMessage(pubsub_update_initial_panel)
        if a.from_calc_strain == 1:
            P4Rm.from_calc_strain = 0
            pub.sendMessage(pubsub_Draw_Strain)
        elif a.from_calc_DW == 1:
            P4Rm.from_calc_DW = 0
            pub.sendMessage(pubsub_Draw_DW)
        else:
            if a.fitlive == 1:
                pub.sendMessage(pubsub_Draw_Strain)
                pub.sendMessage(pubsub_Draw_DW)
                pub.sendMessage(pubsub_Fill_List_coef)
            else:
                pub.sendMessage(pubsub_Draw_XRD)
                pub.sendMessage(pubsub_Draw_Strain)
                pub.sendMessage(pubsub_Draw_DW)
                pub.sendMessage(pubsub_Fill_List_coef)

    def calc_XRD(self, paths):
        """
        Loading and extracting of XRD data file with no default extension,
        but needed a two columns format file
        """
        b = ReadFile()
        P4Rm.DefaultDict['XRD_folder'] = os.path.split(paths[0])[0]
        P4Rm.PathDict['XRD_file'] = paths[0]
        self.on_update_config_file('XRD_folder')
        try:
            """READING XRD FILE"""
            b.read_xrd_file(paths[0])
            self.on_calc_from_xrd()
            pub.sendMessage(pubsub_Draw_XRD, b=1)
        except TypeError:
            logger.log(logging.WARNING, "!Please check your input file!")

    def calc_strain(self, paths=None, choice=None):
        """
        Reading and calcul Strain coefficient
        """
        if paths:
            P4Rm.DefaultDict['Strain_folder'] = os.path.split(paths[0])[0]
            self.on_update_config_file('Strain_folder')
        a = P4Rm()
        b = ReadFile()
        c = SaveFile4Diff()
        spline_strain = a.spline_strain
        if choice == 0:
            data = b.read_strain_xy_file(paths[0])
            if spline_strain == 2:
                t = data[0].max()
                P4Rm.ParamDict['t_l'] = t/a.AllDataDict['number_slices']
                P4Rm.ParamDict['z'] = (arange(a.AllDataDict['number_slices'] +
                                       1) * a.ParamDict['t_l'])
                P4Rm.ParamDict['depth'] = t - a.ParamDict['z']
            else:
                t = a.AllDataDict['damaged_depth']
            P4Rm.ParamDict['sp'] = fit_input_strain(data,
                                                    a.AllDataDict['strain_basis_func'],
                                                    a.AllDataDict['damaged_depth'],
                                                    spline_strain)
        else:
            t = a.AllDataDict['damaged_depth']
        P4Rm.ParamDictbackup['sp'] = a.ParamDict['sp']
        P4Rm.ParamDict['strain_basis'] = float(a.AllDataDict['strain_basis_func'])
        P4Rm.ParamDict['strain_i'] = f_strain(a.ParamDict['z'],
                                              a.ParamDict['sp'],
                                              t, spline_strain)
        self.on_shifted_sp_curves(t)
        P4Rm.from_calc_strain = 1
        self.draw_curves()
        if choice == 0:
            c.save_deformation('Strain_file', 'strain', a.ParamDict['sp'])

    def calc_DW(self, paths=None, choice=None):
        """
        Reading and calcul DW coefficient
        """
        if paths:
            P4Rm.DefaultDict['DW_folder'] = os.path.split(paths[0])[0]
            self.on_update_config_file('DW_folder')
        a = P4Rm()
        b = ReadFile()
        c = SaveFile4Diff()
        spline_DW = a.spline_DW
        if choice == 0:
            data = b.read_dw_xy_file(paths[0])
            if spline_DW == 2:
                t = data[0].max()
                P4Rm.ParamDict['t_l'] = t/a.AllDataDict['number_slices']
                P4Rm.ParamDict['z'] = (arange(a.AllDataDict['number_slices'] +
                                       1) * a.ParamDict['t_l'])
                P4Rm.ParamDict['depth'] = t - a.ParamDict['z']
            else:
                t = a.AllDataDict['damaged_depth']
            P4Rm.ParamDict['dwp'] = fit_input_DW(data,
                                                 a.AllDataDict['dw_basis_func'],
                                                 a.AllDataDict['damaged_depth'],
                                                 spline_DW)
        else:
            t = a.AllDataDict['damaged_depth']
        P4Rm.ParamDictbackup['dwp'] = a.ParamDict['dwp']
        P4Rm.ParamDict['dw_basis'] = float(a.AllDataDict['strain_basis_func'])
        P4Rm.ParamDict['DW_i'] = f_strain(a.ParamDict['z'],
                                          a.ParamDict['dwp'],
                                          t, spline_DW)
        self.on_shifted_dwp_curves(t)
        P4Rm.from_calc_DW = 1
        self.draw_curves()
        if choice == 0:
            c.save_deformation('DW_file', 'DW', a.ParamDict['dwp'])

    def OnChangeBasisFunction(self, strain, dw, spline_strain,
                              spline_DW, slice_):
        a = P4Rm()
        strain_change = 0
        dw_change = 0
        slice_change = 0
        if strain != float(a.ParamDict['strain_basis_backup']):
            P4Rm.ParamDict['strain_basis_backup'] = strain
            P4Rm.ParamDict['state_sp'] = int(strain)*[True]
            strain_change = 1
        if dw != a.ParamDict['dw_basis_backup']:
            P4Rm.ParamDict['dw_basis_backup'] = dw
            dw_change = 1
        if slice_ != float(a.ParamDict['slice_backup']):
            P4Rm.ParamDict['slice_backup'] = slice_
            slice_change = 1
        if a.FitDict['New&Load'] == 1:
            dw_change = 1

        if strain_change == 1 or dw_change == 1 or slice_change == 1:
            temp = self.find_nearest_damaged_depth(a.AllDataDict['damaged_depth'],
                                                   a.AllDataDict['number_slices'],
                                                   strain)
            P4Rm.AllDataDict['damaged_depth'] = temp[0]
            P4Rm.AllDataDict['number_slices'] = temp[1]
            damaged_val = temp[0]
            slice_val = temp[1]
            dw, index, list_ = self.find_nearest_dw(a.AllDataDict['number_slices'],
                                                    dw, strain, strain_change,
                                                    dw_change, slice_change)
            P4Rm.ParamDict['t_l'] = damaged_val/slice_val
            P4Rm.ParamDict['z'] = arange(slice_val+1) * a.ParamDict['t_l']
            P4Rm.ParamDict['dwp'] = old2new_DW(a.ParamDict['z'],
                                               a.ParamDict['dwp'],
                                               damaged_val, dw, spline_DW)
            P4Rm.ParamDict['sp'] = old2new_strain(a.ParamDict['z'],
                                                  a.ParamDict['sp'],
                                                  damaged_val, strain,
                                                  spline_strain)
            P4Rm.ParamDictbackup['dwp'] = deepcopy(a.ParamDict['dwp'])
            P4Rm.ParamDictbackup['sp'] = deepcopy(a.ParamDict['sp'])
            P4Rm.FitDict['New&Load'] = 0
            P4Rm.FitDict['list4DW'] = list_
            tmp = []
            tmp.append(list_)
            tmp.append(index)
            tmp.append(damaged_val)
            tmp.append(dw)
            tmp.append(slice_val)
            P4Rm.ParamDict['state_dwp'] = dw*[True]

            pub.sendMessage(pubsub_change_basic_function, tmp=tmp)
            return slice_val, dw
        else:
            slice_val = int(a.AllDataDict['number_slices'])
            return slice_val, dw

    def find_nearest_damaged_depth(self, damaged, N, Nstrain):
        a = P4Rm()
        if a.AllDataDict['model'] == 0:
            if damaged % Nstrain != 0:
                damaged = round(damaged/Nstrain)*Nstrain
            if N/Nstrain != 0:
                N = round(N/Nstrain)*Nstrain
        elif a.AllDataDict['model'] == 1:
            Nstrain = Nstrain - 3
            if damaged % Nstrain != 0:
                damaged = round(damaged/Nstrain)*Nstrain
            if N/Nstrain != 0:
                N = round(N/Nstrain)*Nstrain
        return damaged, N

    def find_nearest(self, ar, value):
        ar_ = [int(a) for a in ar]
        ar_ = np.array(ar_)
        idx = (np.abs(ar_-value)).argmin()
        return idx

    def find_nearest_dw(self, N, Ndw, Nstrain, strain_change, dw_change,
                        slice_change):
        a = P4Rm()
        temp = []
        if a.AllDataDict['model'] == 0:
            for i in range(5, int(float(Nstrain)) + 1):
                if N % i == 0:
                    temp.append(str(i))
            if strain_change == 1:
                index = int(self.find_nearest(temp, int(Nstrain)))
                P4Rm.AllDataDict['dw_basis_func'] = Nstrain
                val = int(temp[index])
            elif slice_change == 1:
                index = int(self.find_nearest(temp, int(Ndw)))
                val = int(temp[index])
            elif dw_change == 1:
                index = int(a.AllDataDict['dw_basis_func'])
                val = int(float(index))
        elif a.AllDataDict['model'] == 1:
            val = int(float(Nstrain))
            temp.append(str(val))
            index = 1
        return val, index, temp

    def on_reset_deformation_multiplication(self):
        P4Rm.ParamDict['DW_multiplication'] = 1.0
        P4Rm.ParamDict['strain_multiplication'] = 1.0
        pub.sendMessage(pubsub_update_initial_panel)

    def on_update(self):
        a = P4Rm()

        pub.sendMessage(pubsub_Read_field4Save)

        if (a.checkInitialField == 1 and a.checkGeometryField == 1 and
            a.checkFittingField == 1):
            P4Rm.allparameters = (a.initial_parameters +
                                  a.fitting_parameters +
                                  a.sample_geometry)
            i = 0
            for k in p4R.IP_p + p4R.F_p + p4R.SG_p:
                P4Rm.AllDataDict[k] = a.allparameters[i]
                i += 1
            pub.sendMessage(pubsub_test_some_field)

            if (a.ParamDict['Iobs'] == [] or
               a.ParamDict['sp'] == [] or
               a.ParamDict['dwp'] == []):
                return
            else:
                self.on_calcul_parameters()
                if a.AllDataDict['model'] == 2:
                    pub.sendMessage(pubsub_update_sp_dwp_eta)
                P4Rm.success4Fit = 0
        else:
            P4Rm.success4Fit = 1
