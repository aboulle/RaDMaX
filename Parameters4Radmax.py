#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

# =============================================================================
# Radmax Parameters module
# =============================================================================


import os
import sys
from os.path import abspath
from sys import platform as _platform

from collections import OrderedDict

Application_name = "RaDMaX"
filename = "Radmax"
Application_version = "2.3.0.0"
last_modification = "29/07/2016"
log_filename = "activity"
ExperimentFile = 'ExperimentFile'
RadmaxFile = 'RadmaxFile'
Database_name = 'RadmaxDB'

description = ("RaDMaX: Radiation Damage in Materials analyzed with X-ray" +
               "diffraction")
licence = ("RaDMaX is distributed freely under the CeCILL license" +
           "(see LICENSE.txt and COPYRIGHT.txt).")
copyright_ = "(C) 2016 SPCTS"
website_ = "http://www.unilim.fr/spcts/"

output_name = {'out_strain': 'output_strain_coeff.txt',
               'out_dw': 'output_DW_coeff.txt',
               'out_strain_profile': 'output_strain.txt',
               'out_dw_profile': 'output_DW.txt',
               'in_strain': 'input_strain_coeff.txt',
               'in_dw': 'input_DW_coeff.txt', 'out_XRD': 'out_XRD_fit.txt'}

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    if _platform == 'darwin':
        application_path = os.path.dirname(sys.argv[0])
        path = os.path.split(application_path)
        path_temp = os.path.split(path[0])
        current_dir = os.path.dirname(abspath(path_temp[0]))
    elif _platform == 'win32':
        application_path = os.path.dirname(sys.executable)
        config_path = os.path.join(application_path, filename)
        current_dir = os.path.dirname(abspath(config_path))
else:
    # we are running in a normal Python environment
    application_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(application_path, filename)
    current_dir = os.path.dirname(abspath(config_path))

structures_name = os.path.join(current_dir, 'structures')
struc_factors = os.path.join(current_dir, 'f0f1f2')
log_file_path = os.path.join(current_dir, log_filename + ".log")
music_path = os.path.join(current_dir, 'modules', 'Sounds')
database_path = os.path.join(current_dir, 'database')


"""
Definition of the variable name used in the program
They are called by all the modules
"""
dlg_size = (700, 300)

database_dict = ['engine', 'session', 'Name', 'choice_state', 'choice_combo',
                 'date_1', 'date_2']

FitAlgo_choice = ["GSA", "leastsq"]
FitSuccess = ["Success", "Aborted"]

FitParamDefault = {'strain_eta_min': -0.5, 'strain_eta_max': 1.5,
                   'dw_eta_min': -0.5, 'dw_eta_max': 1.5, 'dw_height_min': 0.,
                   'dw_height_max': 1., 'strain_height_min': 0.,
                   'strain_height_max': 1., 'dw_bkg_min': 0., 'dw_bkg_max': 1.,
                   'strain_bkg_min': 0., 'strain_bkg_max': 1.,
                   'strain_min': 0., 'strain_max': 1., 'dw_min': 0.,
                   'dw_max': 1., 'qa': 0.99, 'qv': 2.6, 'qt': 1.001,
                   'xtol': 1.e-7, 'ftol': 1.e-7, 'maxfev': 2000,
                   'c_strain': '#00aa00', 'c_dw': '#ff0000',
                   'c_data': '#8080ff', 'c_fit': '#00e6e6',
                   'c_fit_live': '#ff0000', 'l_strain': 'dotted',
                   'l_dw': 'dashed', 'l_data': 'solid',
                   'l_fit': 'solid', 'l_fit_live': 'solid',
                   'use_database': 'False'}

DefaultParam4Radmax = ['project_folder', 'DW_folder', 'Strain_folder',
                       'XRD_folder', 'Save_as_folder',
                       'strain_eta_min', 'strain_eta_max', 'dw_eta_min',
                       'dw_eta_max', 'strain_height_min',
                       'strain_height_max', 'dw_height_min', 'dw_height_max',
                       'strain_bkg_min', 'strain_bkg_max', 'dw_bkg_min',
                       'dw_bkg_max', 'strain_min', 'strain_max', 'dw_min',
                       'dw_max', 'qa', 'qv', 'qt', 'xtol', 'ftol', 'maxfev',
                       'c_strain', 'c_dw', 'c_data', 'c_fit', 'c_fit_live',
                       'l_strain', 'l_dw', 'l_data', 'l_fit', 'l_fit_live',
                       'use_database']


value4rounddamaged = int(200)

asym_pv_list = ['heigt_strain', 'loc_strain', 'fwhm_1_strain', 'fwhm_2_strain',
                'strain_eta_1', 'strain_eta_2', 'bkg_strain', 'heigt_dw',
                'loc_dw', 'fwhm_1_dw', 'fwhm_2_dw', 'dw_eta_1', 'dw_eta_2',
                'bkg_dw']

GSAp_ = ['strain_height_min', 'strain_height_max', 'strain_eta_min',
         'strain_eta_max', 'strain_bkg_min', 'strain_bkg_max',
         'dw_height_min', 'dw_height_max', 'dw_eta_min', 'dw_eta_max',
         'dw_bkg_min', 'dw_bkg_max']

Params4Radmax = ['sp', 'dwp', 'sp_pv', 'dwp_pv', 'sp_smooth', 'dwp_smooth',
                 'sp_abrupt', 'dwp_abrupt', 'data_xrd', 'x_sp', 'x_dwp',
                 'Iobs', 'Ical', 'I_i', 'I_fit', '_fp_min',
                 'th', 'th4live', 'damaged_value_backup',
                 't_l', 'z', 'depth', 'thB_S', 'g0', 'gH', 'b_S', 'd',
                 'G', 'FH', 'FmH', 'F0', 'Vol', 'DW_multiplication',
                 'strain_multiplication', 'strain_basis_backup',
                 'dw_basis_backup', 'strain_sm_ab_bkp', 'dw_sm_ab_bkp',
                 'scale_strain', 'scale_dw', 'strain_i',
                 'strain_shifted', 'DW_i', 'DW_shifted', 'par', 'resol',
                 'stain_out', 'dw_out', 'thB_S_s', 'g0_s', 'gH_s', 'b_S_s',
                 'd_s', 'G_s', 'FH_s', 'FmH_s', 'F0_s', 'Vol_s',
                 'state_sp', 'state_dwp']

Bsplinesave = ['smooth', 'abrupt', 'pv']
Strain_DW_choice = ["B-splines smooth", "B-splines abrupt", "Asymmetric pv"]
sample_geometry = ["Default", "Thin film", "Thick film",
                   "Thick film + substrate"]


# Initial Parameters panel
IP_p = ['wavelength', 'resolution', 'shape', 'background', 'h', 'k', 'l',
        'crystal_symmetry', 'a', 'b', 'c', 'alpha', 'beta', 'gamma', 'model',
        'strain_basis_func', 'dw_basis_func', 'damaged_depth', 'number_slices']

# Sample Geometry panel
SG_p = ['geometry', 'film_thick', 'dw_thick', 'h_s', 'k_s', 'l_s',
        'crystal_symmetry_s', 'a_s', 'b_s', 'c_s',
        'alpha_s', 'beta_s', 'gamma_s']

# Fitting panel
F_p = ['tmax', 'nb_cycle_max', 'nb_palier']

# All Path
Path4Radmax = ['project_name', 'path2ini', 'path2inicomplete', 'path2drx',
               'namefromini', 'name4lmfit', 'Compound_name', 'substrate_name',
               'DW_file', 'Strain_file', 'XRD_file']

FitData = ['checkFittingField', 'checkGeometryField', 'checkInitialField',
           'fit_type', 'lmfit_install', 'fit_params', 'spline_strain',
           'spline_DW', 'worker_live', 'Leastsq_report', 'New&Load', 'list4DW']

# =============================================================================
# experimental file.ini section
# =============================================================================
Exp_file_section = ['Crystal', 'Data files', 'Experiment', 'Material',
                    'Strain and DW', 'GSA options', 'Bspline Bounds',
                    'PV Bounds', 'GSA expert', 'Leastsq parameters',
                    'Sample Geometry', 'Substrate']
s_crystal = ['crystal_name', 'substrate_name']
s_data_file = ['input_dw', 'input_strain', 'xrd_data']
s_experiment = ['wavelength', 'resolution', 'shape', 'background']
s_material = ['h', 'k', 'l', 'crystal_symmetry', 'a', 'b', 'c',
              'alpha', 'beta', 'gamma']
s_strain_DW = ['model', 'strain_basis_func', 'dw_basis_func',
               'damaged_depth', 'number_slices']
s_GSA_options = ['tmax', 'nb_cycle_max', 'nb_palier']
s_bsplines = ['strain_min', 'strain_max', 'dw_min', 'dw_max']
s_pv = ['strain_eta_min', 'strain_eta_max', 'dw_eta_min',
        'dw_eta_max', 'strain_height_min',
        'strain_height_max', 'dw_height_min', 'dw_height_max',
        'strain_bkg_min', 'strain_bkg_max', 'dw_bkg_min',
        'dw_bkg_max']
s_GSA_expert = ['qa', 'qv', 'qt']
s_leastsq = ['xtol', 'ftol', 'maxfev']
s_geometry = ['geometry', 'film_thick', 'dw_thick']
s_substrate = ['h_s', 'k_s', 'l_s', 'crystal_symmetry_s', 'a_s', 'b_s', 'c_s',
               'alpha_s', 'beta_s', 'gamma_s']

Exp_file_all_section = (s_crystal + s_data_file + s_experiment + s_material +
                        s_strain_DW + s_GSA_options + s_bsplines + s_pv +
                        s_GSA_expert + s_leastsq + s_geometry + s_substrate)

# read from experiment file without check if value is a number or not
Exp_read_only = s_bsplines + s_pv + s_GSA_expert + s_leastsq

# =============================================================================
# Radmax.ini section
# =============================================================================
Radmax_File_section = ['RaDMax', 'Folder Paths', 'PV Bounds', 'Bspline Bounds',
                       'GSA expert', 'Leastsq parameters', 'Graph Options',
                       'Database']
s_radmax_1 = ['version', 'last_modification']
s_radmax_2 = ['project_file', 'dw_file', 'strain_file', 'xrd_file',
              'save_as_file']
s_radmax_3 = ['strain_eta_min', 'strain_eta_max', 'dw_eta_min',
              'dw_eta_max', 'strain_height_min',
              'strain_height_max', 'dw_height_min', 'dw_height_max',
              'strain_bkg_min', 'strain_bkg_max', 'dw_bkg_min',
              'dw_bkg_max']
s_radmax_4 = ['strain_min', 'strain_max', 'dw_min', 'dw_max']
s_radmax_5 = ['qa', 'qv', 'qt']
s_radmax_6 = ['xtol', 'ftol', 'maxfev']
s_radmax_7 = ['c_strain', 'c_dw', 'c_data', 'c_fit', 'c_fit_live',
              'l_strain', 'l_dw', 'l_data', 'l_fit', 'l_fit_live']
s_radmax_8 = ['use_database']

Radmax_all_section = (s_radmax_1 + s_radmax_2 + s_radmax_3 + s_radmax_4 +
                      s_radmax_5 + s_radmax_6 + s_radmax_7 + s_radmax_8)


# -----------------------------------------------------------------------------
class P4Rm():
    """
    Parameters4Diff:
    All the variable passed and shared along the different module
    """

    """Parameters Panel"""
    ncolumnParam = len(Params4Radmax)*[""]
    ncolumnPath = len(Path4Radmax)*[""]
    ncolumnDefault = len(DefaultParam4Radmax)*[""]
    ncolumnAllData = len(Exp_file_all_section)*[""]
    ncolumnFit = len(FitData)*[0, 0, 0, "", False, "", "", "", None, "", 1]
    ncolumnDB = len(database_dict)*[None]

    AllDataDict = OrderedDict(zip(Exp_file_all_section, ncolumnAllData))
    ParamDict = OrderedDict(zip(Params4Radmax, ncolumnParam))
    PathDict = OrderedDict(zip(Path4Radmax, ncolumnPath))
    DefaultDict = OrderedDict(zip(DefaultParam4Radmax, ncolumnDefault))
    FitDict = OrderedDict(zip(FitData, ncolumnFit))

    ConstDict = {'re': 2.818*10**-5, 'phi': 0, 'phi_s': 0,
                 'jump_scale': 0.00001}

    ParamDict['DW_multiplication'] = 1
    ParamDict['strain_multiplication'] = 1

    ParamDictbackup = OrderedDict(zip(Params4Radmax, ncolumnParam))

    Paramwindowtest = {'FitParametersPanel': "", 'PseudoVoigtPanel': "",
                       'BsplinePanel': ""}

    DBDict = OrderedDict(zip(database_dict, ncolumnDB))

    ProjectFileData = []
    initial_parameters = []
    fitting_parameters = []
    sample_geometry = []

    checkFittingField = 0
    checkGeometryField = 0
    checkInitialField = 0
    fit_type = ""
    lmfit_install = False
    fit_params = ""

    crystal_list = ""

    spline_strain = ""
    spline_DW = ""

    log_window_status = ""

    gsa_loop = 0
    fitlive = 0
    residual_error = 0

    xrd_graph_loaded = 0

    zoomOn = 0

    from_Calc_Strain = 0
    from_Calc_DW = 0

    DragDrop_Strain_x = []
    DragDrop_Strain_y = []
    DragDrop_DW_x = []
    DragDrop_DW_y = []

    allparameters = []
    allparameters4save = []

    splinenumber = []
    par_fit = []
    success = []
    resultFit = ""
    success4Fit = 0
    modelPv = ""
    pathfromDB = 0
