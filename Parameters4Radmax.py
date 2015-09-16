#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A_BOULLE & M_SOUILAH

try:
    import wx, wx.html
except ImportError:
    raise ImportError, "The wxPython module is required to run this program"

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

from logging.handlers import RotatingFileHandler
logger = logging.getLogger(__name__)

LEVELS = [
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL
]
NamePath_panel_keys = ['Compound_name', 'DW_file', 'Strain_file', 'XRD_file']
Parameters_panel_keys = ['wavelength', 'resolution', 'shape', 'background', 'h', 'k', 'l',\
'crystal_symmetry', 'a', 'b', 'c', 'alpha', 'beta', 'gamma', 'strain_basis_func', 'min_strain',\
'max_strain', 'dw_basis_func', 'min_dw', 'max_dw', 'damaged_depth', 'number_slices']
Fitting_panel_keys = ['tmax', 'nb_cycle_max', 'nb_palier', 'qa', 'qv', 'qt']
Initial_data_key = Parameters_panel_keys + Fitting_panel_keys 
Folder_paths_key = ['project_file', 'DW_file', 'Strain_file', 'XRD_file', 'Save_as_file']
init_parameters = [1] * len(Initial_data_key)
value4rounddamaged = int(200)
header_project = 4

Application_name = "RaDMaX"
filename = "Radmax"
Application_version = 1.4
last_modification = "16/09/2015"
log_filename = "activity"
ConfigDataFile = 'ConfigDataFile'
ConfigFile = 'ConfigFile'

description = """RaDMaX: Radiation Damage in Materials analyzed with X-ray diffraction"""
licence = "RaDMaX is distributed freely under the CeCILL license (see LICENSE.txt and COPYRIGHT.txt)."

output_name = {'out_strain':'output_strain_coeff.txt', 'out_dw':'output_DW_coeff.txt', 'out_strain_profile':'output_strain.txt',\
            'out_dw_profile':'output_DW.txt', 'in_strain':'input_strain_coeff.txt', 'in_dw':'input_DW_coeff.txt', 'out_XRD':'out_XRD_fit.txt',}

current_dir = os.path.dirname(os.path.realpath(filename))
structures_name = os.path.join(current_dir, 'structures')
struc_factors = os.path.join(current_dir, 'f0f1f2')
log_file_path = os.path.join(current_dir, log_filename + ".log")

#------------------------------------------------------------------------------
class LogWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, Application_name + " log window")
        wx.Frame.CenterOnScreen(self)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.SetIcon(prog_icon.GetIcon())
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._logFileContents = wx.TextCtrl(self, wx.ID_ANY, size=(600,300),
                          style = wx.TE_MULTILINE|wx.TE_READONLY|wx.VSCROLL)


        self.updateButton = wx.Button(self,wx.ID_ANY,label="Update")
        
        sizer.Add(self._logFileContents,1,wx.ALL|wx.EXPAND,5)
        sizer.Add(self.updateButton,0,wx.ALL|wx.EXPAND,5)
        self.Bind(wx.EVT_BUTTON,self.on_update,self.updateButton)
        self.SetSizer(sizer)
        self.update()
        self.Layout()
        self.Fit()
        
    def update(self):
        with open(log_file_path,"r") as f:
            self._logFileContents.SetValue(f.read())
            
    def on_update(self,event):
        self.update()
    
    def onClose(self, event):
        P4Diff.log_window_status = False
        self.Destroy()

#------------------------------------------------------------------------------
class LogSaver(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY)
        self.Fit()

        # création de l'objet logger qui va nous servir à écrire dans les logs
        logger = logging.getLogger()
        # on met le niveau du logger à DEBUG, comme ça il écrit tout
        logger.setLevel(logging.DEBUG)
         
        # création d'un formateur qui va ajouter le temps, le niveau
        # de chaque message quand on écrira un message dans le log
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        # création d'un handler qui va rediriger une écriture du log vers
        # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
        file_handler = RotatingFileHandler(log_file_path, 'a', 1000000, 1)
        # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
        # créé précédement et on ajoute ce handler au logger
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

#------------------------------------------------------------------------------
class WxTextCtrlHandler(logging.Handler):
    """ Redirect the logger to a wxPython textCtrl """
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        s = self.format(record) + '\n'
        wx.CallAfter(self.ctrl.WriteText, s)

#------------------------------------------------------------------------------
class P4Diff():
    """Parameters4Diff"""
    log_window_status = ""
    logfile_Radmax_path = ""
    logfile_currentP_path = ""
    re = 2.818*10**-5 ## rayon classique de l'électron
    phi = 0. ## angle d'asymétrie LAISSER COMME ÇA POUR L'INSTANT
    jump_scale = 0.00001
    gsa_loop = 0
    success4Fit = 0
    fitlive = 0
    frequency_refresh_leastsq = 50
    frequency_refresh_gsa = 30
    gaugeUpdate = 0
    
    zoomOn = 0

    DragDrop_Strain_x = []
    DragDrop_Strain_y = []
    DragDrop_DW_x = []
    DragDrop_DW_y = []
    data_xrd = []
    sp = []
    dwp = []   
    sp_backup = []
    dwp_backup = []   
    x_sp = []
    x_dwp = []
    Iobs = []
    Iobs_backup = []
    Ical = []
    I_i = []
    I_fit = []
    _fp_min = []
    th = []
    th_backup = []
    th4live = []
    par = []
    resol = []
    z = []
    G = []
    FH = []
    FmH = []
    F0 = []
    depth = []
    DW_i = []
    DW_shifted = []
    DW_multiplication = 1.00
    strain_i = []
    strain_shifted = []
    strain_multiplication = 1.00
    strain_basis_backup = ""
    dw_basis_backup = ""
    scale_strain = []
    scale_dw = []
    stain_out_save = 0
    dw_out_save = 0
    d = ""
    Vol = ""
    thB_S = ""
    g0 = ""
    gH = ""
    b_S = ""
    t_l = ""
    allparameters = []
    allparameters4save = []
    initial_parameters = []
    fitting_parameters = []
    splinenumber = []
    slice_backup = ""
    par_fit = []
    success = []
    path2ini = ""
    path2drx = ""
    path2inicomplete = ""
    namefromini = ""
    checkDataField = 0
    