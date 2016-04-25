#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

'''
*Radmax parameters module*
'''

try:
    import wx
    import wx.html
except ImportError:
    raise ImportError("The wxPython module is required to run this program")

from inspect import getsourcefile
from os.path import abspath
import os
import sys
from sys import exit
from sys import platform as _platform
import string

from Icon4Radmax import prog_icon

import wx.lib.agw.aui as aui
from wx.lib.pubsub import pub
import wx.lib.agw.multidirdialog as MDD
import wx.lib.agw.genericmessagedialog as GMD
import wx.lib.agw.floatspin as FS

from time import time, sleep
import logging
import numpy as np

from copy import deepcopy

from math import ceil

from tools import *

from collections import OrderedDict

from logging.handlers import RotatingFileHandler
logger = logging.getLogger(__name__)

LEVELS = [
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL
]

Application_name = "RaDMaX"
filename = "Radmax"
Application_version = "2.0.0.0"
last_modification = "25/04/2016"
log_filename = "activity"
ConfigDataFile = 'ConfigDataFile'
ConfigFile = 'ConfigFile'

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


"""
Definition of the variable name used in the program
They are call for all the different module
"""

FitParamDefault = {'strain_eta_min': -0.5, 'strain_eta_max': 1.5,
                   'dw_eta_min': -0.5, 'dw_eta_max': 1.5, 'dw_height_min': 0.,
                   'dw_height_max': 1., 'strain_height_min': 0.,
                   'strain_height_max': 1., 'dw_bkg_min': 0., 'dw_bkg_max': 1.,
                   'strain_bkg_min': 0., 'strain_bkg_max': 1.,
                   'strain_min': 0., 'strain_max': 1., 'dw_min': 0.,
                   'dw_max': 1., 'qa': 0.99, 'qv': 2.6, 'qt': 1.001,
                   'xtol': 1.e-7, 'ftol': 1.e-7, 'maxfev': 2000}

Folder_paths_key = ['project_file', 'DW_file', 'Strain_file', 'XRD_file',
                    'Save_as_file']

DefaultParam4Radmax = ['project_file', 'DW_file', 'Strain_file', 'XRD_file',
                       'Save_as_file', 'strain_eta_min', 'strain_eta_max',
                       'dw_eta_min', 'dw_eta_max', 'strain_height_min',
                       'strain_height_max', 'dw_height_min', 'dw_height_max',
                       'strain_bkg_min', 'strain_bkg_max', 'dw_bkg_min',
                       'dw_bkg_max', 'strain_min', 'strain_max', 'dw_min',
                       'dw_max', 'qa', 'qv', 'qt', 'xtol', 'ftol', 'maxfev']

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
                 'G', 'FH', 'FmH', 'F0', 'DW_multiplication',
                 'strain_multiplication', 'strain_basis', 'dw_basis',
                 'scale_strain', 'scale_dw', 'strain_i', 'strain_shifted',
                 'DW_i', 'DW_shifted', 'par', 'resol', 'stain_out', 'dw_out']

Bsplinesave = ['smooth', 'abrupt', 'pv']

Data4Radmax = ['wavelength', 'resolution', 'shape', 'background', 'h', 'k',
               'l', 'crystal_symmetry', 'a', 'b', 'c', 'alpha', 'beta',
               'gamma', 'model', 'strain_basis_func', 'dw_basis_func',
               'damaged_depth', 'number_slices', 'tmax', 'nb_cycle_max',
               'nb_palier']

Path4Radmax = ['project_name', 'path2ini', 'path2inicomplete', 'path2drx',
               'namefromini', 'name4lmfit', 'Compound_name', 'DW_file',
               'Strain_file', 'XRD_file']


# definition of the exact structure of the config file
Config_DataFile_section = ['Crystal', 'Data files', 'Experiment', 'Material',
                           'Strain and DW', 'GSA options', 'Bspline Bounds',
                           'PV Bounds', 'GSA expert', 'Leastsq parameters']

structure_Crystal = ['crystal_name']
structure_Data_filename = ['input_dw', 'input_strain', 'xrd_data']
structure_Experiment = ['wavelength', 'resolution', 'shape', 'background']
structure_Material = ['h', 'k', 'l', 'crystal_symmetry', 'a', 'b', 'c',
                      'alpha', 'beta', 'gamma']
structure_Strain_and_DW = ['model', 'strain_basis_func', 'dw_basis_func',
                           'damaged_depth', 'number_slices']
structure_GSA_options = ['tmax', 'nb_cycle_max', 'nb_palier']
structure_Adv_GSA_options = ['qa', 'qv', 'qt']


Config_File_section = ['RaDMax', 'Folder Paths', 'PV Bounds', 'Bspline Bounds',
                       'GSA expert', 'Leastsq parameters']
Config_File_section_1 = ['version', 'last_modification']
Config_File_section_2 = ['project_file', 'dw_file', 'strain_file', 'xrd_file',
                         'save_as_file']
Config_File_section_3 = ['strain_eta_min', 'strain_eta_max', 'dw_eta_min',
                         'dw_eta_max', 'strain_height_min',
                         'strain_height_max', 'dw_height_min', 'dw_height_max',
                         'strain_bkg_min', 'strain_bkg_max', 'dw_bkg_min',
                         'dw_bkg_max']
Config_File_section_4 = ['strain_min', 'strain_max', 'dw_min', 'dw_max']
Config_File_section_5 = ['qa', 'qv', 'qt']
Config_File_section_6 = ['xtol', 'ftol', 'maxfev']

All_DataFile4Radmax = (structure_Crystal + structure_Data_filename +
                       structure_Experiment + structure_Material +
                       structure_Strain_and_DW + structure_GSA_options +
                       Config_File_section_4 + Config_File_section_3 +
                       Config_File_section_5 + Config_File_section_6)

"""Read and create config file"""
Config_File_all_section = (Config_File_section_1 + Config_File_section_2 +
                           Config_File_section_3 + Config_File_section_4 +
                           Config_File_section_5 + Config_File_section_6)


Config_DataFile_all_section = (structure_Crystal + structure_Data_filename +
                               structure_Experiment +
                               structure_Material +
                               structure_Strain_and_DW +
                               structure_GSA_options +
                               Config_File_section_4 +
                               Config_File_section_3 +
                               Config_File_section_5 +
                               Config_File_section_6)

ALPHA_ONLY = 1
DIGIT_ONLY = 2


# -----------------------------------------------------------------------------
class P4Radmax():
    """
    Parameters4Diff:
    All the variable passed and shared along the different module
    """

    """Parameters Panel"""
    ncolumnParam = len(Params4Radmax)*[""]
    ncolumnPath = len(Path4Radmax)*[""]
    ncolumnData = len(Data4Radmax)*[""]
    ncolumnDefault = len(DefaultParam4Radmax)*[""]
    ncolumnAllData = len(All_DataFile4Radmax)*[""]

    AllDataDict = OrderedDict(zip(All_DataFile4Radmax, ncolumnAllData))
    ParamDict = OrderedDict(zip(Params4Radmax, ncolumnParam))
    PathDict = OrderedDict(zip(Path4Radmax, ncolumnPath))
    DataDict = OrderedDict(zip(Data4Radmax, ncolumnData))
    DefaultDict = OrderedDict(zip(DefaultParam4Radmax, ncolumnDefault))

    ConstDict = {'re': 2.818*10**-5, 'phi': 0, 'jump_scale': 0.00001}

    ParamDict['DW_multiplication'] = 1
    ParamDict['strain_multiplication'] = 1

    ParamDictbackup = OrderedDict(zip(Params4Radmax, ncolumnParam))

    Paramwindowtest = {'FitParametersPanel': "", 'PseudoVoigtPanel': "",
                       'BsplinePanel': ""}

    ProjectFileData = []
    initial_parameters = []
    fitting_parameters = []
    limit_GSA = []

    log_window_status = ""
    logfile_Radmax_path = ""
    logfile_currentP_path = ""

    Option_window_status = ""

    gsa_loop = 0
    success4Fit = 0
    fitlive = 0
    frequency_refresh_leastsq = 50
    frequency_refresh_gsa = 30
    gaugeUpdate = 0
    residual_error = 0

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
    slice_backup = ""
    par_fit = []
    success = []
    resultFit = ""

    checkDataField = 0
    modelPv = ""
    acc_choice = ""
    old_file_version = ""


# -----------------------------------------------------------------------------
class LogWindow(wx.Frame):
    """
    Creation of the log window
    we use the 'log_window_status' variable to ensure that only one instance of
    the window in launch at one time
    """
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, Application_name +
                          " - log window")
        wx.Frame.CenterOnScreen(self)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.SetIcon(prog_icon.GetIcon())
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._logFileContents = wx.TextCtrl(self, wx.ID_ANY, size=(600, 300),
                                            style=wx.TE_MULTILINE |
                                            wx.TE_READONLY | wx.VSCROLL)

        self.updateButton = wx.Button(self, wx.ID_ANY, label="Update")

        sizer.Add(self._logFileContents, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.updateButton, 0, wx.ALL | wx.EXPAND, 5)
        self.Bind(wx.EVT_BUTTON, self.on_update, self.updateButton)
        self.SetSizer(sizer)
        self.update()
        self.Layout()
        self.Fit()

    def update(self):
        with open(log_file_path, "r") as f:
            self._logFileContents.SetValue(f.read())

    def on_update(self, event):
        self.update()

    def onClose(self, event):
        P4Radmax.log_window_status = False
        self.Destroy()


# -----------------------------------------------------------------------------
class LogSaver(wx.Panel):
    """
    class used all along the modules to record the information available
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY)
        self.Fit()

        # création de l'objet logger qui va nous servir à écrire dans les logs
        logger = logging.getLogger()
        # on met le niveau du logger à DEBUG, comme ça il écrit tout
        logger.setLevel(logging.DEBUG)

        # création d'un formateur qui va ajouter le temps, le niveau
        # de chaque message quand on écrira un message dans le log
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s ::' +
                                      '%(message)s')
        # création d'un handler qui va rediriger une écriture du log vers
        # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
        file_handler = RotatingFileHandler(log_file_path, 'a', 1000000, 1)
        # on lui met le niveau sur DEBUG,
#        on lui dit qu'il doit utiliser le formateur
        # créé précédement et on ajoute ce handler au logger
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


# -----------------------------------------------------------------------------
class WxTextCtrlHandler(logging.Handler):
    """
    Redirect the logger to a wxPython textCtrl
    """
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        s = self.format(record) + '\n'
        wx.CallAfter(self.ctrl.WriteText, s)


# -----------------------------------------------------------------------------
class TextValidator(wx.PyValidator):
    """
    Used to test in the character enter in the textctrl are the one desired
    (letters, digits or punctuations)
    """
    def __init__(self, flag=None, pyVar=None):
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return TextValidator(self.flag)

    def Validate_Point_Coma(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        temp = []
        for x in val:
            if x == '.' or x == ',':
                temp.append(True)
            else:
                temp.append(False)
        if True in temp:
            return True
        else:
            return False

    def Validate_Sign(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        temp = []
        for x in val:
            if x == '-':
                temp.append(True)
            else:
                temp.append(False)
        if True in temp:
            return True
        else:
            return False

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if self.flag == ALPHA_ONLY and chr(key) in string.letters:
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in string.digits:
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in "eE":
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in ".,":
            test = self.Validate_Point_Coma(self)
            if test is False:
                event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in "-":
            test = self.Validate_Sign(self)
            if test is False:
                event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()
        return
