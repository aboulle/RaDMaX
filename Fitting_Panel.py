#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

'''
*Radmax Fiting panel module*
'''

from threading import Thread, Event
from scipy.optimize import leastsq
from scipy import convolve
import wx.lib.agw.advancedsplash as AS

from Parameters4Radmax import *
#from Read4Radmax import LogSaver
try:
    import numba
    from def_XRD_jit import f_Refl_jit
except ImportError:
    pass
from def_XRD import f_Refl, f_ReflDict

from sim_anneal import SimAnneal
from sys import platform as _platform
from random import randint

from Icon4Radmax import error_icon, ok_icon, stop_thread, stop_thread_morpheus
from def_strain import f_strain
from def_DW import f_DW

New_project_initial_data = {0: 10, 1: 1000, 2: 10}

pubsub_Load_fitting_panel = "LoadFittingPanel"
pubsub_Read_field_paramters_panel = "ReadParametersPanel"
pubsub_Re_Read_field_paramters_panel = "ReReadParametersPanel"
pubsub_Refresh_fitting_panel = "RefreshFittingPanel"
pubsub_Draw_Fit_Live_XRD = "DrawFitLiveXRD"
pubsub_Draw_Fit_Live_Deformation = "DrawFitLiveDeformation"
pubsub_Update_Fit_Live = "UpdateFitLive"
pubsub_OnFit_Graph = "OnFitGraph"
pubsub_on_update_limit = "UpdateLimit"
pubsub_on_update_gauge = "UpdateGauge"
pubsub_Read_field4Save = "ReadField4Save"
pubsub_changeColor_field4Save = "on_change_color_field4Save"
pubsub_Update_deformation_multiplicator_coef = "UpdateDefMultiplicatorCoef"
pubsub_save_project_before_fit = "SaveProjectBeforeFit"
pubsub_gauge_to_zero = "gauge2zero"
pubsub_On_Limit_Before_Graph = "OnLimitBeforeGraph"
pubsub_Draw_XRD = "DrawXRD"
pubsub_Read_sp_dwp = "ReadSpDwp"
pubsub_Hide_Show_GSA = "HideShowGSA"
pubsub_ModifyDLimits = "ModifyDeformationLimits"

Live_COUNT = wx.NewEventType()
LiveLimitExceeded_COUNT = wx.NewEventType()
EVT_Live_COUNT = wx.PyEventBinder(Live_COUNT, 1)
EVT_LiveLimitExceeded_COUNT = wx.PyEventBinder(LiveLimitExceeded_COUNT, 1)


# ------------------------------------------------------------------------------
class FittingPanel(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar
        self.parent = parent

        size_text = (55, 22)

        font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
        if _platform == "linux" or _platform == "linux2":
            font_Statictext = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_combobox = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            vStatictextsize = 16
        elif _platform == "win32":
            font_Statictext = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_combobox = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            vStatictextsize = 16
        elif _platform == 'darwin':
            font_Statictext = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_combobox = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            vStatictextsize = 18

        font_end_fit = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD,
                               False, u'Arial')
        size_StaticBox = (700, 140)

        """master sizer for the whole panel"""
        mainsizer = wx.GridBagSizer(hgap=0, vgap=1)
        topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.errorsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.centersizer = wx.BoxSizer(wx.VERTICAL)

        FitAlgo_choice = ["GSA", "leastsq"]
        self.ID_ComboStats = wx.NewId()
        FitAlgo_txt = wx.StaticText(self, -1, label=u'Fitting algorithm: ',
                                    size=(130, vStatictextsize))
        FitAlgo_txt.SetFont(font_Statictext)
        self.cb_FitAlgo = wx.ComboBox(self, id=self.ID_ComboStats,
                                      pos=(50, 30),
                                      choices=FitAlgo_choice,
                                      style=wx.CB_READONLY)
        self.cb_FitAlgo.SetStringSelection(FitAlgo_choice[0])
        self.Bind(wx.EVT_COMBOBOX, self.on_change_fit, self.cb_FitAlgo)
        self.cb_FitAlgo.SetFont(font_combobox)

        topsizer.Add(FitAlgo_txt, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        topsizer.Add(self.cb_FitAlgo, 0, wx.ALL, 5)

        """GSA options part"""
        GSA_options_box = wx.StaticBox(self, -1, " GSA options ",
                                       size=size_StaticBox)
        GSA_options_box.SetFont(font)
        self.GSA_options_box_sizer = wx.StaticBoxSizer(GSA_options_box,
                                                       wx.VERTICAL)
        in_GSA_options_box_sizer = wx.GridBagSizer(hgap=10, vgap=1)
        flagSizer = wx.ALL | wx.ALIGN_CENTER_VERTICAL

        temperature_txt = wx.StaticText(self, -1, label=u'Temperature (k)',
                                        size=(110, vStatictextsize))
        temperature_txt.SetFont(font_Statictext)
        self.temperature = wx.TextCtrl(self, size=size_text,
                                       validator=TextValidator(DIGIT_ONLY))
        self.temperature.SetFont(font_TextCtrl)

        cycle_number_txt = wx.StaticText(self, -1, label=u'Number of cycle',
                                         size=(110, vStatictextsize))
        cycle_number_txt.SetFont(font_Statictext)
        self.cycle_number = wx.TextCtrl(self, size=size_text,
                                        validator=TextValidator(DIGIT_ONLY))
        self.cycle_number.SetFont(font_TextCtrl)

        cooling_number_txt = wx.StaticText(self, -1,
                                           label=u'Number of cooling steps',
                                           size=(140, vStatictextsize))
        cooling_number_txt.SetFont(font_Statictext)
        self.cooling_number = wx.TextCtrl(self, size=size_text,
                                          validator=TextValidator(DIGIT_ONLY))
        self.cooling_number.SetFont(font_TextCtrl)

        in_GSA_options_box_sizer.Add(temperature_txt, pos=(0, 0),
                                     flag=flagSizer)
        in_GSA_options_box_sizer.Add(self.temperature, pos=(0, 1),
                                     flag=flagSizer)
        in_GSA_options_box_sizer.Add(cycle_number_txt, pos=(0, 2),
                                     flag=flagSizer)
        in_GSA_options_box_sizer.Add(self.cycle_number, pos=(0, 3),
                                     flag=flagSizer)
        in_GSA_options_box_sizer.Add(cooling_number_txt, pos=(0, 4),
                                     flag=flagSizer)
        in_GSA_options_box_sizer.Add(self.cooling_number, pos=(0, 5),
                                     flag=flagSizer)

        """Fit part"""
        Fit_box = wx.StaticBox(self, -1, " Fit ", size=size_StaticBox)
        Fit_box.SetFont(font)
        Fit_box_sizer = wx.StaticBoxSizer(Fit_box, wx.VERTICAL)
        in_Fit_box_sizer = wx.GridBagSizer(hgap=5, vgap=0)

        """GSA result part"""
        GSA_results_box = wx.StaticBox(self, -1, " GSA fit results ",
                                       size=size_StaticBox)
        GSA_results_box.SetFont(font)
        self.GSA_results_sizer = wx.StaticBoxSizer(GSA_results_box,
                                                   wx.VERTICAL)
        in_GSA_results_sizer = wx.GridBagSizer(hgap=2, vgap=0)

        """button part"""
        self.FitId = wx.NewId()
        self.StopFitId = wx.NewId()
        self.Restore_strain_Id = wx.NewId()
        self.Restore_dw_Id = wx.NewId()

        self.gauge = wx.Gauge(self, -1, size=(160, 25),
                              style=wx.ALL | wx.EXPAND)
        self.gauge.SetValue(0)
        Emin_txt = wx.StaticText(self, -1, label=u'Emin: ',
                                 size=(40, vStatictextsize))
        Emin_txt.SetFont(font_Statictext)
        self.Emin_change_txt = wx.StaticText(self, -1, label=u'',
                                             size=(50, vStatictextsize))
        self.Emin_change_txt.SetFont(font_TextCtrl)

        param_txt = wx.StaticText(self, -1, label=u'Minima: ',
                                  size=(60, vStatictextsize))
        param_txt.SetFont(font_Statictext)
        self.param_change_txt = wx.StaticText(self, -1, label=u'',
                                              size=(50, vStatictextsize))
        self.param_change_txt.SetFont(font_TextCtrl)

        name_limit = u'Limit Exceeded On Parameter: '
        self.on_limit_exceeded_txt = wx.StaticText(self, -1,
                                                   label=name_limit,
                                                   size=(190, vStatictextsize))
        self.on_limit_exceeded_txt.SetFont(font_Statictext)
        self.on_limit_exceeded = wx.StaticText(self, -1, label=u'',
                                               size=(50, vStatictextsize))
        self.on_limit_exceeded.SetFont(font_TextCtrl)

        self.fit_Btn = wx.Button(self, id=self.FitId, label="Fit!")
        self.fit_Btn.SetFont(font_update)
        self.fit_Btn.Bind(wx.EVT_BUTTON, self.on_launch_fit)
        self.stopfit_Btn = wx.Button(self, id=self.StopFitId,
                                     label="Stop fit!")
        self.stopfit_Btn.SetFont(font_update)
        self.stopfit_Btn.Bind(wx.EVT_BUTTON, self.on_stop_fit)
        self.stopfit_Btn.Disable()

        self.progressBar = wx.Gauge(self, -1, 50, (-20, 0), (100, 20))

        self.restore_strain_btn = wx.Button(self, id=self.Restore_strain_Id,
                                            label="Strain values",
                                            size=(120, 30))
        self.restore_strain_btn.SetFont(font_update)
        self.restore_dw_btn = wx.Button(self, id=self.Restore_dw_Id,
                                        label="DW values", size=(120, 30))
        self.restore_dw_btn.SetFont(font_update)
        self.restore_strain_btn.Bind(wx.EVT_BUTTON, self.on_restore)
        self.restore_dw_btn.Bind(wx.EVT_BUTTON, self.on_restore)

        in_Fit_box_sizer.Add(self.fit_Btn, pos=(0, 0), flag=flagSizer)
        in_Fit_box_sizer.Add(self.stopfit_Btn, pos=(0, 1), flag=flagSizer)
        in_Fit_box_sizer.Add(self.progressBar, pos=(0, 2),
                             flag=wx.EXPAND | wx.ALL)

        in_GSA_results_sizer.Add(self.gauge, pos=(0, 0),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(Emin_txt, pos=(0, 1),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(self.Emin_change_txt, pos=(0, 2),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(param_txt, pos=(0, 3),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(self.param_change_txt, pos=(0, 4),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(self.on_limit_exceeded_txt, pos=(0, 5),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(self.on_limit_exceeded, pos=(0, 6),
                                 flag=flagSizer)
#        'Emin = %4.3f' %E_min, '(',int(nb_minima), ')'

        """Restore part"""
        Restore_box = wx.StaticBox(self, -1, " Restore previous ",
                                   size=(300, 150))
        Restore_box.SetFont(font)
        self.Restore_box_sizer = wx.StaticBoxSizer(Restore_box, wx.VERTICAL)
        in_Restore_box_sizer = wx.GridBagSizer(hgap=0, vgap=1)

        in_Restore_box_sizer.Add(self.restore_strain_btn, pos=(0, 0))
        in_Restore_box_sizer.Add(self.restore_dw_btn, pos=(1, 0))

        self.Restore_box_sizer.Add(in_Restore_box_sizer, 0, wx.ALL, 5)

        self.png = wx.BitmapFromIcon(error_icon.GetIcon())
        self.information_icon = wx.StaticBitmap(self, -1, self.png, (10, 5),
                                                (self.png.GetWidth(),
                                                 self.png.GetHeight()))
        self.information_text = wx.StaticText(self, -1, label=u'',
                                              size=(150, 20))
        self.information_text.SetFont(font_end_fit)
        self.information_icon.Hide()

        self.residual_error_txt = wx.StaticText(self, -1,
                                                label=u'Residual error: ',
                                                size=(130, vStatictextsize))
        self.residual_error_txt.SetFont(font_end_fit)
        self.residual_error = wx.StaticText(self, -1, label=u'',
                                            size=(100, vStatictextsize))
        self.residual_error.SetFont(font_end_fit)
        self.residual_error_txt.Hide()
        self.errorsizer.Add(self.residual_error_txt, 0, wx.ALL, 5)
        self.errorsizer.Add(self.residual_error, 0, wx.ALL, 5)

        self.GSA_options_box_sizer.Add(in_GSA_options_box_sizer, 0, wx.ALL, 5)
        Fit_box_sizer.Add(in_Fit_box_sizer, 0, wx.ALL, 5)
        self.GSA_results_sizer.Add(in_GSA_results_sizer, 0, wx.ALL, 5)

        self.centersizer.Add(Fit_box_sizer, 0, wx.ALL & ~wx.TOP, 5)
        self.centersizer.Add(self.GSA_options_box_sizer, 0, wx.ALL, 5)
        self.centersizer.Add(self.GSA_results_sizer, 0, wx.ALL, 5)

        mainsizer.Add(topsizer, pos=(0, 0))
        mainsizer.Add(self.centersizer, pos=(1, 0), span=(3, 1))
        mainsizer.Add(self.Restore_box_sizer, pos=(1, 1), span=(1, 2))
        mainsizer.Add(self.information_icon, pos=(2, 1), flag=wx.ALL,
                      border=10)
        mainsizer.Add(self.information_text, pos=(2, 2), flag=wx.TOP,
                      border=15)
        mainsizer.Add(self.errorsizer, pos=(3, 1), span=(1, 2), flag=wx.TOP,
                      border=15)

        self.data_fields = {}
        self.data_fields[0] = self.temperature
        self.data_fields[1] = self.cycle_number
        self.data_fields[2] = self.cooling_number
        self.resultprojectfile = len(self.data_fields)*[1]
        self.resultprojectfile_backup = []
        self.test_limit = []
        self.fit_params = ""
        self.lmfit_install = False
        self.fitname = ""
        self.random_thread_image = 0

        self.worker_live = None
        self.begin_time = 0
        self.Bind(EVT_Live_COUNT, self.on_live)
        self.Bind(EVT_LiveLimitExceeded_COUNT, self.on_update_limit)

        pub.subscribe(self.on_load_project, pubsub_Load_fitting_panel)
        pub.subscribe(self.on_refresh_GUI_after_fit,
                      pubsub_Refresh_fitting_panel)
        pub.subscribe(self.on_update_gauge, pubsub_on_update_gauge)
        pub.subscribe(self.on_read_data_field, pubsub_Read_field4Save)
        pub.subscribe(self.on_change_color_field,
                      pubsub_changeColor_field4Save)
        pub.subscribe(self.gauge2zero, pubsub_gauge_to_zero)
        pub.subscribe(self.on_modify_deformation_limits, pubsub_ModifyDLimits)

        self.SetSizer(mainsizer)

    def on_change_fit(self, event):
        fitname = event.GetString()
        if fitname == 'GSA':
            self.centersizer.Show(self.GSA_results_sizer)
            self.centersizer.Show(self.GSA_options_box_sizer)
            self.Layout()
        else:
            self.centersizer.Hide(self.GSA_results_sizer)
            self.centersizer.Hide(self.GSA_options_box_sizer)
            self.Layout()
        self.Fit()

    def on_load_project(self, data=None, b=None):
        for ii in self.data_fields:
            self.data_fields[ii].Clear()
        if b == 1:
            for i in range(len(New_project_initial_data)):
                p_ = New_project_initial_data[i]
                self.data_fields[i].AppendText(str(p_))
                self.resultprojectfile_backup.append(p_)
        else:
            for i in range(len(data)):
                self.data_fields[i].AppendText(str(data[i]))
                self.resultprojectfile_backup.append(data[i])
        self.Fit()
        self.Layout()

    def onLaunchtest(self):
        a = P4Radmax()
        self.fitname = self.cb_FitAlgo.GetSelection()
        P4Radmax.allparameters = a.initial_parameters + a.fitting_parameters
        i = 0
        for k, v in a.DataDict.items():
            try:
                P4Radmax.DataDict[k] = a.allparameters[i]
                i += 1
            except (IndexError):
                break
        if self.fitname == 0:
            test_deformation_limit = self.on_test_data_before_fit()
        else:
            test_deformation_limit = True
        if test_deformation_limit is True:
            self.on_launch_thread()
        else:
            pub.sendMessage(pubsub_Hide_Show_GSA)

    def on_launch_thread(self):
        a = P4Radmax()
        if self.fitname == 0:
            logger.log(logging.INFO, "GSA Fit has been launched")
        else:
            logger.log(logging.INFO, "Leastsq Fit has been launched")

        P4Radmax.ParamDictbackup['sp'] = a.ParamDict['sp']
        P4Radmax.ParamDictbackup['dwp'] = a.ParamDict['dwp']
        msg_ = u"Fitting... Please Wait...This may take some time"
        self.statusbar.SetStatusText(msg_, 0)
        pub.sendMessage(pubsub_OnFit_Graph)
        P4Radmax.fitlive = 1
        self.gauge.SetValue(0)
        self.progressBar.Pulse()
        self.on_refresh_GUI_after_fit(0)
        sleep(0.3)
        self.random_thread_image = randint(0, 100)
        if self.fitname == 1:
            success = self.on_test_lmfit()
            if success is True:
                self.worker_live = Fit_launcher(self, 2, a.DataDict,
                                                self.fit_params)
            else:
                self.worker_live = Fit_launcher(self, 1, a.DataDict)
        else:
            self.worker_live = Fit_launcher(self, self.fitname, a.DataDict)

    def on_modify_deformation_limits(self, state):
        a = P4Radmax()
        case = state.index(True)
        if a.DataDict['model'] == 0. or a.DataDict['model'] == 1.:
            value = 0.1
            if case is 0:
                ''' Modify input'''
                i = 0
                for val_dwp, val_sp in zip(a.ParamDict['dwp'],
                                           a.ParamDict['sp']):
                    if val_dwp < a.DefaultDict['dw_min']:
                        val_ = a.DefaultDict['dw_min'] + value
                        P4Radmax.ParamDict['dwp'][i] = val_
                    elif val_dwp > a.DefaultDict['dw_max']:
                        val_ = a.DefaultDict['dw_max'] - value
                        P4Radmax.ParamDict['dwp'][i] = val_
                    if val_sp < a.DefaultDict['strain_min']:
                        val_ = a.DefaultDict['strain_min'] + value
                        P4Radmax.ParamDict['sp'][i] = val_
                    elif val_sp > a.DefaultDict['strain_max']:
                        val_ = a.DefaultDict['strain_max'] - value
                        P4Radmax.ParamDict['sp'][i] = val_
                    i += 1
                self.on_launch_thread()
            elif case is 1:
                ''' Modify limits '''
                roundval = 4
                t_min_dw = [False]*len(a.ParamDict['dwp'])
                t_max_dw = [False]*len(a.ParamDict['dwp'])
                t_min_sp = [False]*len(a.ParamDict['sp'])
                t_max_sp = [False]*len(a.ParamDict['sp'])
                i = 0
                for val_dwp, val_sp in zip(a.ParamDict['dwp'],
                                           a.ParamDict['sp']):
                    if val_dwp < a.DefaultDict['dw_min']:
                        t_min_dw[i] = True
                    elif val_dwp > a.DefaultDict['dw_max']:
                        t_max_dw[i] = True
                    if val_sp < a.DefaultDict['strain_min']:
                        t_min_sp[i] = True
                    elif val_sp > a.DefaultDict['strain_max']:
                        t_max_sp[i] = True
                    i += 1
                if True in t_min_dw:
                    round_ = round(min(a.ParamDict['dwp']) - value, roundval)
                    P4Radmax.DefaultDict['dw_min'] = round_
                elif True in t_max_dw:
                    round_ = round(max(a.ParamDict['dwp']) + value, roundval)
                    P4Radmax.DefaultDict['dw_max'] = round_
                if True in t_min_sp:
                    round_ = round(min(a.ParamDict['sp']) - value, roundval)
                    P4Radmax.DefaultDict['strain_min'] = round_
                if True in t_max_sp:
                    round_ = round(max(a.ParamDict['sp']) + value, roundval)
                    P4Radmax.DefaultDict['strain_max'] = round_
                self.on_launch_thread()
            elif case is 2:
                return 0

        elif a.DataDict['model'] == 2.:
            value = 0.5
            if case is 0:
                ''' Modify input'''
                i = 0
                ls_ = [0, 4, 5, 6]
                lse_ = [0, 2, 2, 4]
                ld_ = [x+6 for x in ls_]
                lde_ = [x+6 for x in lse_]
                for val_dwp, val_sp in zip(a.ParamDict['dwp'],
                                           a.ParamDict['sp']):
                    if i in ls_:
                        v_ = ls_.index(i)
                        ve_ = lse_[v_]
                        if val_sp < a.DefaultDict[GSAp_[ve_]]:
                            val_ = a.DefaultDict[GSAp_[ve_]] + value
                            P4Radmax.ParamDict['sp'][i] = val_
                        elif val_sp > a.DefaultDict[GSAp_[ve_ + 1]]:
                            val_ = a.DefaultDict[GSAp_[ve_ + 1]] - value
                            P4Radmax.ParamDict['sp'][i] = val_
                    else:
                        if val_sp < 0.:
                            val_ = value
                            P4Radmax.ParamDict['sp'][i] = val_
                        elif val_sp > 1.:
                            val_ = 1. - value
                            P4Radmax.ParamDict['sp'][i] = val_
                    j = i + 6
                    if j in ld_:
                        v_ = ld_.index(j)
                        ve_ = lde_[v_]
                        if val_dwp < a.DefaultDict[GSAp_[ve_]]:
                            val_ = a.DefaultDict[GSAp_[ve_]] + value
                            P4Radmax.ParamDict['dwp'][i] = val_
                        elif val_dwp > a.DefaultDict[GSAp_[ve_ + 1]]:
                            val_ = a.DefaultDict[GSAp_[ve_ + 1]] - value
                            P4Radmax.ParamDict['dwp'][i] = val_
                    else:
                        if val_dwp < 0.:
                            val_ = value
                            P4Radmax.ParamDict['dwp'][i] = val_
                        elif val_dwp > 1.:
                            val_ = 1. - value
                            P4Radmax.ParamDict['dwp'][i] = val_
                    i += 1
                self.on_launch_thread()
            elif case is 1:
                ''' Modify limits '''
                dict_min_ = ['strain_height_min', 'strain_eta_min',
                             'strain_eta_min', 'strain_bkg_min',
                             'dw_height_min', 'dw_eta_min', 'dw_eta_min',
                             'dw_bkg_min']
                dict_max_ = ['strain_height_max', 'strain_eta_max',
                             'strain_eta_max', 'strain_bkg_max',
                             'dw_height_max', 'dw_eta_max', 'dw_eta_max',
                             'dw_bkg_max']
                roundval = 4
                i = 0
                k = 0
                l = 0
                ls_ = [0, 4, 5, 6]
                lse_ = [0, 2, 2, 4]
                ld_ = [x+6 for x in ls_]
                lde_ = [x+6 for x in lse_]
                test_dw_min = [False]*len(ls_)
                test_dw_max = [False]*len(ls_)
                test_strain_min = [False]*len(ls_)
                test_strain_max = [False]*len(ls_)
                for val_dwp, val_sp in zip(a.ParamDict['dwp'],
                                           a.ParamDict['sp']):
                    if i in ls_:
                        v_ = ls_.index(i)
                        ve_ = lse_[v_]
                        if val_sp < a.DefaultDict[GSAp_[ve_]]:
                            test_strain_min[k] = True
                        elif val_sp > a.DefaultDict[GSAp_[ve_ + 1]]:
                            test_strain_max[k] = True
                        k += 1
                    j = i + 6
                    if j in ld_:
                        v_ = ld_.index(j)
                        ve_ = lde_[v_]
                        if val_dwp < a.DefaultDict[GSAp_[ve_]]:
                            test_dw_min[l] = True
                        elif val_dwp > a.DefaultDict[GSAp_[ve_ + 1]]:
                            test_dw_max[l] = True
                        l += 1
                    i += 1

                if True in test_strain_min:
                    for a_ in test_strain_min:
                        if a_ is True:
                            v_ = test_strain_min.index(True)
                            val_ = a.ParamDict['sp'][ls_[v_]] - value
                            round_ = round(val_, roundval)
                            index_ = dict_min_[v_]
                            P4Radmax.DefaultDict[index_] = round_
                elif True in test_strain_max:
                    for a_ in test_strain_max:
                        if a_ is True:
                            v_ = test_strain_max.index(True)
                            val_ = a.ParamDict['sp'][ls_[v_]] + value
                            round_ = round(val_, roundval)
                            index_ = dict_max_[v_]
                            P4Radmax.DefaultDict[index_] = round_
                if True in test_dw_min:
                    for a_ in test_dw_min:
                        if a_ is True:
                            v_ = test_dw_min.index(True)
                            val_ = a.ParamDict['dwp'][ls_[v_]] - value
                            round_ = round(val_, roundval)
                            index_ = dict_min_[v_ + 4]
                            P4Radmax.DefaultDict[index_] = round_
                elif True in test_dw_max:
                    for a_ in test_dw_max:
                        if a_ is True:
                            v_ = test_dw_max.index(True)
                            val_ = a.ParamDict['dwp'][ls_[v_]] + value
                            round_ = round(val_, roundval)
                            index_ = dict_max_[v_ + 4]
                            P4Radmax.DefaultDict[index_] = round_
                self.on_launch_thread()
            elif case is 2:
                return 0

    def on_test_data_before_fit(self):
        a = P4Radmax()
        P4Radmax.ParamDict['sp'] = np.asarray(a.ParamDict['sp'])
        P4Radmax.ParamDict['dwp'] = np.asarray(a.ParamDict['dwp'])
        if a.DataDict['model'] == 0. or a.DataDict['model'] == 1.:
            """ do not use the last value of strain because
            is out of the scope """
            test_dw = (all(a.ParamDict['dwp'] > a.DefaultDict['dw_min']) and
                       all(a.ParamDict['dwp'][:-1] < a.DefaultDict['dw_max']))
            test_strain = (all(a.ParamDict['sp'][:-1] >
                           a.DefaultDict['strain_min']) and
                           all(a.ParamDict['sp'] <
                               a.DefaultDict['strain_max']))
            if test_dw and test_strain:
                return True
            else:
                return False
        elif a.DataDict['model'] == 2.:
                i = 0
                ls_ = [0, 4, 5, 6]
                lse_ = [0, 2, 2, 4]
                ld_ = [x+6 for x in ls_]
                lde_ = [x+6 for x in lse_]
                test_dw = [False]*len(a.ParamDict['dwp'])
                test_strain = [False]*len(a.ParamDict['sp'])
                for val_dwp, val_sp in zip(a.ParamDict['dwp'],
                                           a.ParamDict['sp']):
                    if i in ls_:
                        v_ = ls_.index(i)
                        ve_ = lse_[v_]
                        if val_sp < a.DefaultDict[GSAp_[ve_]]:
                            test_strain[i] = True
                        elif val_sp > a.DefaultDict[GSAp_[ve_ + 1]]:
                            test_strain[i] = True
                    else:
                        if val_sp < 0.:
                            test_strain[i] = True
                        elif val_sp > 1.:
                            test_strain[i] = True
                    j = i + 6
                    if j in ld_:
                        v_ = ld_.index(j)
                        ve_ = lde_[v_]
                        if val_dwp < a.DefaultDict[GSAp_[ve_]]:
                            test_dw[i] = True
                        elif val_dwp > a.DefaultDict[GSAp_[ve_ + 1]]:
                            test_dw[i] = True
                    else:
                        if val_dwp < 0.:
                            test_dw[i] = True
                        elif val_dwp > 1.:
                            test_dw[i] = True
                    i += 1
                if (True in test_dw) or (True in test_strain):
                    return False
                else:
                    return True

    def on_test_lmfit(self):
        try:
            from lmfit import Parameters
        except (ImportError):
            raise (ImportError, "Please install Lmfit module to have better" +
                   "fit with constraint on eta value")
            return False
        else:
            a = P4Radmax()
            self.lmfit_install = True
            self.fit_params = Parameters()
            if a.DataDict['model'] == 2:
                self.fit_params.add('heigt_strain', value=a.ParamDict['sp'][0],
                                    min=a.DefaultDict['strain_height_min'],
                                    max=a.DefaultDict['strain_height_max'])
                self.fit_params.add('loc_strain', value=a.ParamDict['sp'][1],
                                    min=0.,
                                    max=1.)
                self.fit_params.add('fwhm_1_strain',
                                    value=a.ParamDict['sp'][2],
                                    min=0.,
                                    max=1.)
                self.fit_params.add('fwhm_2_strain',
                                    value=a.ParamDict['sp'][3],
                                    min=0.,
                                    max=1.)
                self.fit_params.add('strain_eta_1', value=a.ParamDict['sp'][4],
                                    min=a.DefaultDict['strain_eta_min'],
                                    max=a.DefaultDict['strain_eta_max'])
                self.fit_params.add('strain_eta_2', value=a.ParamDict['sp'][5],
                                    min=a.DefaultDict['strain_eta_min'],
                                    max=a.DefaultDict['strain_eta_max'])
                self.fit_params.add('bkg_strain', value=a.ParamDict['sp'][6],
                                    min=a.DefaultDict['strain_bkg_min'],
                                    max=a.DefaultDict['strain_bkg_max'])

                self.fit_params.add('heigt_dw', value=a.ParamDict['dwp'][0],
                                    min=a.DefaultDict['dw_height_min'],
                                    max=a.DefaultDict['dw_height_max'])
                self.fit_params.add('loc_dw', value=a.ParamDict['dwp'][1],
                                    min=0.,
                                    max=1.)
                self.fit_params.add('fwhm_1_dw', value=a.ParamDict['dwp'][2],
                                    min=0.,
                                    max=1.)
                self.fit_params.add('fwhm_2_dw', value=a.ParamDict['dwp'][3],
                                    min=0.,
                                    max=1.)
                self.fit_params.add('dw_eta_1', value=a.ParamDict['dwp'][4],
                                    min=a.DefaultDict['dw_eta_min'],
                                    max=a.DefaultDict['dw_eta_max'])
                self.fit_params.add('dw_eta_2', value=a.ParamDict['dwp'][5],
                                    min=a.DefaultDict['dw_eta_min'],
                                    max=a.DefaultDict['dw_eta_max'])
                self.fit_params.add('bkg_dw', value=a.ParamDict['dwp'][6],
                                    min=a.DefaultDict['dw_bkg_min'],
                                    max=a.DefaultDict['dw_bkg_max'])
            else:
                P4Radmax.name4lmfit = []
                for ii in range(len(a.ParamDict['sp'])):
                    name = 'sp_' + str(ii)
                    self.fit_params.add(name, value=a.ParamDict['sp'][ii],
                                        min=a.DefaultDict['strain_min'],
                                        max=a.DefaultDict['strain_max'])
                    P4Radmax.name4lmfit.append(name)
                self.fit_params.add('nb_sp_val',
                                    value=len(a.ParamDict['sp']), vary=False)
                for jj in range(len(a.ParamDict['dwp'])):
                    name = 'dwp_' + str(jj)
                    self.fit_params.add(name, value=a.ParamDict['dwp'][jj],
                                        min=a.DefaultDict['dw_min'],
                                        max=a.DefaultDict['dw_max'])
                    P4Radmax.name4lmfit.append(name)
                self.fit_params.add('nb_dwp_val',
                                    value=len(a.ParamDict['dwp']), vary=False)

            return True

    def on_read_data_from_lmfit(self):
        a = P4Radmax()
        result = P4Radmax.resultFit
        i = 0
        if a.DataDict['model'] == 2:
            for param in result.params.values():
                if i in range(1, 7):
                    P4Radmax.ParamDict['sp'][i] = param.value
                if i in range(7, 14):
                    P4Radmax.ParamDict['dwp'][i - 7] = param.value
                i += 1
        else:
            len_sp = int(result.params['nb_sp_val'])
            len_dwp = int(result.params['nb_dwp_val'])
            for ii in range(len_dwp):
                name = 'dwp_' + str(ii)
                P4Radmax.ParamDict['dwp'][ii] = result.params[name].value
            for jj in range(len_sp):
                name = 'sp_' + str(jj)
                P4Radmax.ParamDict['sp'][jj] = result.params[name].value

    def on_live(self, event):
        list4live = event.GetValue()
        stopFit = event.StopFit()
        if list4live[0] != []:
            pub.sendMessage(pubsub_Draw_Fit_Live_XRD, val=list4live[0])
        if list4live[1] is not None:
            pub.sendMessage(pubsub_on_update_gauge, val=list4live[1][2],
                            emin=list4live[1][0], param=int(list4live[1][1]))
        if list4live[2] is not None:
            pub.sendMessage(pubsub_Draw_Fit_Live_Deformation)
        if stopFit is not None:
            pub.sendMessage(pubsub_Refresh_fitting_panel, option=1,
                            case=stopFit)
            pub.sendMessage(pubsub_OnFit_Graph, b=1)

    def on_stop_fit(self, event):
        self.worker_live.stop()
        l_numb = [2, 24, 56, 89]
        if self.random_thread_image in l_numb:
            bmp = wx.BitmapFromIcon(stop_thread_morpheus.GetIcon())
        else:
            bmp = wx.BitmapFromIcon(stop_thread.GetIcon())
        shadow = wx.WHITE
        AS.AdvancedSplash(None, bitmap=bmp, timeout=2000,
                          agwStyle=AS.AS_TIMEOUT | AS.AS_CENTER_ON_PARENT,
                          shadowcolour=shadow)

    def on_restore(self, event):
        a = P4Radmax()
        widget = event.GetId()
        if widget == self.Restore_strain_Id:
            P4Radmax.ParamDict['sp'] = a.ParamDictbackup['sp']
            P4Radmax.ParamDict['strain_multiplication'] = 1.0
        elif widget == self.Restore_dw_Id:
            P4Radmax.ParamDict['dwp'] = a.ParamDictbackup['dwp']
            P4Radmax.ParamDict['DW_multiplication'] = 1.0
        pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)

    def on_refresh_GUI_after_fit(self, option, case=None):
        label = ""
        a = P4Radmax()
        if option == 0:
            self.parent.notebook.EnableTab(0, False)
            self.fit_Btn.Disable()
            self.stopfit_Btn.Enable()
            self.restore_strain_btn.Disable()
            self.restore_dw_btn.Disable()
            self.cb_FitAlgo.Disable()
            self.information_icon.Hide()
            self.information_text.SetLabel(u"")
            self.residual_error_txt.Hide()
            self.residual_error.SetLabel(u"")
        elif option == 1:
            a = P4Radmax()
            self.progressBar.SetValue(0)
            self.parent.notebook.EnableTab(0, True)
            self.fit_Btn.Enable()
            self.stopfit_Btn.Disable()
            self.restore_strain_btn.Enable()
            self.restore_dw_btn.Enable()
            self.cb_FitAlgo.Enable()
            P4Radmax.fitlive = 0
            P4Radmax.ParamDict['I_i'] = a.ParamDict['I_fit']
            y_cal = f_ReflDict(a.DataDict)
            y_cal = y_cal/y_cal.max() + a.DataDict['background']
            temp = ((log10(a.ParamDict['Iobs']) - log10(y_cal))**2).sum()
            P4Radmax.residual_error = temp / len(y_cal)
            error = round(a.residual_error, 4)
            if case == 0:
                self.png = wx.BitmapFromIcon(ok_icon.GetIcon())
                self.information_icon.SetBitmap(self.png)
                self.information_icon.Show()
                self.residual_error_txt.Show()
                self.residual_error.SetLabel(str(error))
                label = u"Fit ended normally"
                logger.log(logging.INFO, label)
                self.statusbar.SetStatusText(label, 0)
                self.gauge.SetValue(0)
                if self.lmfit_install is True:
                    self.on_read_data_from_lmfit()
                else:
                    t_ = a.par_fit[:int(a.DataDict['strain_basis_func'])]
                    P4Radmax.ParamDict['sp'] = t_
                    t_ = a.par_fit[-1*int(a.DataDict['dw_basis_func']):]
                    P4Radmax.ParamDict['dwp'] = t_
            elif case == 1:
                self.png = wx.BitmapFromIcon(error_icon.GetIcon())
                self.information_icon.SetBitmap(self.png)
                self.information_icon.Show()
                self.residual_error_txt.Show()
                self.residual_error.SetLabel(str(error))
                label = u"Fit aborted by user"
                logger.log(logging.WARNING, label)
                self.statusbar.SetStatusText(label, 0)
            if a.par_fit is not [] or self.lmfit_install is True:
                pub.sendMessage(pubsub_Draw_XRD)
                pub.sendMessage(pubsub_Update_deformation_multiplicator_coef)
                pub.sendMessage(pubsub_Read_sp_dwp)
                self.information_text.SetLabel(label)
                self.on_save_from_fit()
                self.Refresh()
        self.Refresh()
        self.Fit()
        self.Layout()

    def on_save_from_fit(self):
        a = P4Radmax()
        if a.PathDict['path2ini'] != '':
            path = a.PathDict['path2ini']
        else:
            path = a.PathDict['path2drx']
        try:
            header = ["2theta", "Iobs", "Icalc"]
            line = u'{:^12} {:^24} {:^12}'.format(*header)

            # -----------------------------------------------------------------
            name_ = (a.PathDict['namefromini'] + '_' +
                     output_name['out_strain_profile'])
            data_ = column_stack((a.ParamDict['depth'],
                                  a.ParamDict['strain_i']))
            savetxt(os.path.join(path, name_), data_, fmt='%10.8f')
            # -----------------------------------------------------------------
            name_ = (a.PathDict['namefromini'] + '_' +
                     output_name['out_dw_profile'])
            data_ = column_stack((a.ParamDict['depth'],
                                  a.ParamDict['DW_i']))
            savetxt(os.path.join(path, name_), data_, fmt='%10.8f')
            # -----------------------------------------------------------------
            if a.par_fit == []:
                # -------------------------------------------------------------
                name_ = (a.PathDict['namefromini'] + '_' +
                         output_name['out_strain'])
                data_ = a.ParamDict['sp']
                savetxt(os.path.join(path, name_),  data_, fmt='%10.8f')
                # -------------------------------------------------------------
                name_ = (a.PathDict['namefromini'] + '_' +
                         output_name['out_dw'])
                data_ = a.ParamDict['dwp']
                savetxt(os.path.join(path, name_), data_, fmt='%10.8f')
            else:
                # -------------------------------------------------------------
                name_ = (a.PathDict['namefromini'] + '_' +
                         output_name['out_strain'])
                data_ = a.par_fit[:int(a.DataDict['strain_basis_func'])]
                savetxt(os.path.join(path, name_), data_, fmt='%10.8f')
                # -------------------------------------------------------------
                name_ = (a.PathDict['namefromini'] + '_' +
                         output_name['out_dw'])
                data_ = a.par_fit[-1*int(a.DataDict['dw_basis_func']):]
                savetxt(os.path.join(path, name_), data_, fmt='%10.8f')
            # -----------------------------------------------------------------
            name_ = (a.PathDict['namefromini'] + '_' + output_name['out_XRD'])
            data_ = column_stack((a.ParamDict['th4live'], a.ParamDict['Iobs'],
                                  a.ParamDict['I_fit']))
            savetxt(os.path.join(path, ), data_, header=line,
                    fmt='{:^12}'.format('%3.8f'))
            # -----------------------------------------------------------------
            logger.log(logging.INFO, "Data have been saved successfully")
        except IOError:
            msg = "Impossible to save data to file, please check your path !!"
            logger.log(logging.WARNING, msg)

    def on_launch_fit(self, event):
        a = P4Radmax()
        if a.PathDict['namefromini'] != "":
            logger.log(logging.INFO, "Start Fit")
            check_empty = self.on_search_empty_fields()
            if check_empty is True:
                data_float = self.is_data_float()
                if data_float is True:
                    pub.sendMessage(pubsub_Read_field_paramters_panel,
                                    event=event)
                    if a.success4Fit == 0:
                        self.statusbar.SetStatusText(u"", 0)
                        self.onLaunchtest()
                    else:
                        self.parent.notebook.SetSelection(0)
                        pub.sendMessage(pubsub_Re_Read_field_paramters_panel,
                                        event=event)
                elif data_float is False:
                    text = u"Please, fill correctly the fields to continue"
                    self.statusbar.SetStatusText(text, 0)
                    logger.log(logging.WARNING, text)
            elif check_empty is False:
                text = u"Please, fill the red empty fields to continue"
                self.statusbar.SetStatusText(text, 0)
                logger.log(logging.WARNING, text)
        else:
            text = "Please, save the project before to continue"
            dlg = GMD.GenericMessageDialog(None, text,
                                           "Attention", agwStyle=wx.OK |
                                           wx.ICON_INFORMATION)
            dlg.ShowModal()
            pub.sendMessage(pubsub_save_project_before_fit,
                            event=event, case=1)

    def on_read_data_field(self):
        P4Radmax.checkDataField = 0
        check_empty = self.on_search_empty_fields()
        if check_empty is True:
            data_float = self.is_data_float()
            if data_float is True:
                P4Radmax.checkDataField = 1

    def on_change_color_field(self, case):
        if case == 0:
            for ii in range(len(self.data_fields)):
                self.data_fields[ii].SetBackgroundColour('#CCE5FF')
        elif case == 1:
            for ii in range(len(self.data_fields)):
                self.data_fields[ii].SetBackgroundColour('white')
        self.Refresh()
        wx.Yield()

    def on_search_empty_fields(self):
        """search for empty field"""
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
        for i in range(len(self.data_fields)):
            self.resultprojectfile[i] = self.data_fields[i].GetValue()
        for i in range(len(self.data_fields)):
            a = self.data_fields[i].GetValue()
            IsFloat.append(self.is_number(a))
        if False in IsFloat:
            dataFloat = False
            StringPosition = [i for i, x in enumerate(IsFloat) if x is False]
            for ii in StringPosition:
                self.data_fields[ii].SetBackgroundColour('green')
            self.Refresh()
            msg = "Please, fill correctly the fields to continue"
            dlg = GMD.GenericMessageDialog(None, msg,
                                           "Attention", agwStyle=wx.OK |
                                           wx.ICON_INFORMATION)
            dlg.ShowModal()
            for ii in StringPosition:
                self.data_fields[ii].SetBackgroundColour('white')
            self.Refresh()
        else:
            temp = [float(j) for j in self.resultprojectfile]
            P4Radmax.fitting_parameters = temp
        return dataFloat

    def on_update_gauge(self, val, emin, param):
        self.gauge.SetValue(val)
        self.Emin_change_txt.SetLabel('%4.3f' % emin)
        self.param_change_txt.SetLabel(str(param))

    def on_update_limit(self, event):
        val = event.GetValue()
        pub.sendMessage(pubsub_on_update_limit, val=val)

    def on_update_limit_value(self, val):
        if val != -1:
            self.on_limit_exceeded.SetLabel(str(val))
            self.on_limit_exceeded.SetForegroundColour('#FF0000')
        else:
            self.on_limit_exceeded.SetLabel("")
            self.on_limit_exceeded.SetForegroundColour('#000000')

    def gauge2zero(self):
        self.gauge.SetValue(0)
        self.information_icon.Hide()
        self.information_text.SetLabel(u"")


# -----------------------------------------------------------------------------
class LiveEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, value=None, data=None,
                 deformation=None, stopfit=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value
        self._data = data
        self._deformation = deformation
        self._stopfit = stopfit

    def GetValue(self):
        list4live = [self._value, self._data, self._deformation]
        return list4live

    def StopFit(self):
        return self._stopfit


# -----------------------------------------------------------------------------
class Liveon_limit_exceeded(wx.PyCommandEvent):
    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        return self._value


# -----------------------------------------------------------------------------
class Fit_launcher(Thread):
    def __init__(self, parent, choice, data, fit_params=None):
        Thread.__init__(self)
        self.parent = parent
        self.choice = choice
        self.data = data
        self.fit_params = fit_params
        self.need_abort = 0
        self.launch = 0
        self.count = 0
        self.leastsq_refresh = 0
        self.gsa_refresh = 0
        self.gauge_counter = 0
        self.const = 0
        self.pars_value = 0
        self.len_sp = 0
        self.len_dwp = 0
        self.gaugeUpdate = 0
        self._stop = Event()
        self.start()

    def init_array(self):
        a = P4Radmax()
        const_all = []
        const_all.append(self.data['wavelength'])
        const_all.append(self.data['damaged_depth'])
        const_all.append(a.ConstDict['phi'])
        const_all.append(a.ParamDict['b_S'])
        const_all.append(a.ParamDict['G'])
        const_all.append(a.ParamDict['thB_S'])
        const_all.append(a.ParamDict['t_l'])
        self.const = np.asarray(const_all, dtype=np.float64, order={'C'})
        self.len_sp = len(a.ParamDict['sp'])
        self.len_dwp = len(a.ParamDict['dwp'])
        self.gaugeUpdate = a.gaugeUpdate

    def on_limit_exceeded(self, val):
        if self.need_abort == 0:
            evt = Liveon_limit_exceeded(LiveLimitExceeded_COUNT, -1, val)
            wx.PostEvent(self.parent, evt)

    def per_iteration(self, pars, iter, resid, *args, **kws):
        if self.need_abort == 1:
            return True
        if iter < 3 or iter % 10 == 0:
            y_cal = self.residual_lmfit4iteration(pars)
            p = []
            if self.data['model'] == 2:
                for j in asym_pv_list:
                    p.append(pars[j].value)
            else:
                a = P4Radmax()
                for j in a.name4lmfit:
                    p.append(pars[j].value)
            P4Radmax.ParamDict['_fp_min'] = p
#            pub.sendMessage(pubsub_Draw_Fit_Live_XRD, val=y_cal)
#            pub.sendMessage(pubsub_Draw_Fit_Live_Deformation)
            deformation = [p]
            evt = LiveEvent(Live_COUNT, -1, y_cal, None, deformation)
            wx.PostEvent(self.parent, evt)
            sleep(0.5)

    def strain_DW(self, pars=None):
        a = P4Radmax()
        if pars is None:
            self.strain = f_strain(a.ParamDict['z'],
                                   a.ParamDict['_fp_min'][:self.len_sp:],
                                   self.data['damaged_depth'],
                                   a.splinenumber[0])
            self.DW = f_DW(a.ParamDict['z'],
                           a.ParamDict['_fp_min'][self.len_sp:self.len_sp +
                           self.len_dwp:],
                           self.data['damaged_depth'], a.splinenumber[1])
        else:
            if self.data['model'] == 0:
                spline_DW = 5
                spline_strain = 5
            elif self.data['model'] == 1:
                spline_DW = 5
                spline_strain = 5
            elif self.data['model'] == 2:
                spline_DW = 4
                spline_strain = 4
            self.pars4numba(pars)
            self.strain = f_strain(a.ParamDict['z'], self.pars_value,
                                   self.data['damaged_depth'], spline_strain)
            self.DW = f_DW(a.ParamDict['z'], self.pars_value,
                           self.data['damaged_depth'], spline_DW)
        self.strain.astype(np.float64)
        self.DW.astype(np.float64)

    def pars4numba(self, pars):
        vals = pars.valuesdict()
        const = []
        if self.data['model'] == 2:
            for name in asym_pv_list:
                const.append(vals[name])
        else:
            len_sp = int(vals['nb_sp_val'])
            len_dwp = int(vals['nb_dwp_val'])
            const.append(len_sp)
            const.append(len_dwp)
            for ii in range(len_sp):
                name = 'sp_' + str(ii)
                const.append(vals[name])
            for ii in range(len_dwp):
                name = 'dwp_' + str(ii)
                const.append(vals[name])
        self.pars_value = np.asarray(const, dtype=np.float64, order={'C'})

    def residual_lmfit4iteration(self, pars):
        a = P4Radmax()
        self.strain_DW(pars)
        res = f_Refl(self.strain, self.DW, a.ParamDict['FH'],
                     a.ParamDict['FmH'], a.ParamDict['F0'], a.ParamDict['th'],
                     self.const, len(a.ParamDict['z']),
                     self.data['number_slices'])
        y_cal = convolve(abs(res)**2, a.ParamDict['resol'], mode='same')
        y_cal = y_cal/y_cal.max() + self.data['background']
        return y_cal

    def residual_lmfit(self, pars, x, y):
        a = P4Radmax()
        self.strain_DW(pars)
        res = f_Refl(self.strain, self.DW, a.ParamDict['FH'],
                     a.ParamDict['FmH'], a.ParamDict['F0'], a.ParamDict['th'],
                     self.const, len(a.ParamDict['z']),
                     self.data['number_slices'])
        y_cal = convolve(abs(res)**2, a.ParamDict['resol'], mode='same')
        y_cal = y_cal/y_cal.max() + self.data['background']
        return (log10(y) - log10(y_cal))

    def residual_lmfit_jit(self, pars, x, y):
        a = P4Radmax()
        self.strain_DW(pars)
        res = np.zeros(a.ParamDict['th'].shape[0], dtype=np.complex128,
                       order={'C'})
        eta = np.zeros(a.ParamDict['th'].shape[0], dtype=np.complex128,
                       order={'C'})
        thb = np.zeros(len(a.ParamDict['z']), dtype=np.float64,
                       order={'C'})
        f_Refl_jit(self.strain, self.DW, a.ParamDict['FH'], a.ParamDict['FmH'],
                   a.ParamDict['F0'], a.ParamDict['th'], self.const,
                   len(a.ParamDict['z']), self.data['number_slices'],
                   res, eta, thb)
        y_cal = convolve(abs(res)**2, a.ParamDict['resol'], mode='same')
        y_cal = y_cal/y_cal.max() + self.data['background']
        return (log10(y) - log10(y_cal))

    def residual(self, p, y, x):
        P4Radmax.ParamDict['_fp_min'] = p
        y_cal = f_ReflDict(self.data)
        y_cal = y_cal/y_cal.max() + self.data['background']
        self.count = self.count + 1
        if self.count % self.leastsq_refresh == 0:
            deformation = [p]
            evt = LiveEvent(Live_COUNT, -1, y_cal, None, deformation)
            wx.PostEvent(self.parent, evt)
#            sleep(0.1)
        return (log10(y) - log10(y_cal))

    def residual_square(self, p, E_min, nb_minima, val4gauge):
        a = P4Radmax()
        P4Radmax.ParamDict['_fp_min'] = p
        self.strain_DW()
        res = f_Refl(self.strain, self.DW, a.ParamDict['FH'],
                     a.ParamDict['FmH'], a.ParamDict['F0'], a.ParamDict['th'],
                     self.const, len(a.ParamDict['z']),
                     self.data['number_slices'])
        y_cal = convolve(abs(res)**2, a.ParamDict['resol'], mode='same')
        y_cal = y_cal/y_cal.max() + self.data['background']
        y_obs = a.ParamDict['Iobs']
        gaugeUpdate = a.gaugeUpdate
        self.on_pass_data_to_thread(y_cal, p, E_min, nb_minima, val4gauge,
                                    gaugeUpdate)
        return ((log10(y_obs) - log10(y_cal))**2).sum() / len(y_cal)

    def residual_square_jit(self, p, E_min, nb_minima, val4gauge):
        a = P4Radmax()
        P4Radmax.ParamDict['_fp_min'] = p
        self.strain_DW()
        res = np.zeros(a.ParamDict['th'].shape[0], dtype=np.complex128,
                       order={'C'})
        eta = np.zeros(a.ParamDict['th'].shape[0], dtype=np.complex128,
                       order={'C'})
        thb = np.zeros(len(a.ParamDict['z']), dtype=np.float64,
                       order={'C'})

        f_Refl_jit(self.strain, self.DW, a.ParamDict['FH'], a.ParamDict['FmH'],
                   a.ParamDict['F0'], a.ParamDict['th'], self.const,
                   len(a.ParamDict['z']), self.data['number_slices'],
                   res, eta, thb)
        y_cal = convolve(abs(res)**2, a.ParamDict['resol'], mode='same')
        y_cal = y_cal/y_cal.max() + self.data['background']
        y_obs = a.ParamDict['Iobs']
        gaugeUpdate = a.gaugeUpdate
        self.on_pass_data_to_thread(y_cal, p, E_min, nb_minima, val4gauge,
                                    gaugeUpdate)
        return ((log10(y_obs) - log10(y_cal))**2).sum() / len(y_cal)

    def on_pass_data_to_thread(self, y_cal, p, E_min, nb_minima, val4gauge,
                               gaugeUpdate):
        self.count = self.count + 1
        if self.count == 1:
            data = [E_min, nb_minima, self.gauge_counter]
            evt = LiveEvent(Live_COUNT, -1, [])
            wx.PostEvent(self.parent, evt)
        if self.count % val4gauge == 0:
            self.gauge_counter += gaugeUpdate
            data = [E_min, nb_minima, self.gauge_counter]
            deformation = [p]
            evt = LiveEvent(Live_COUNT, -1, y_cal, data, deformation)
            wx.PostEvent(self.parent, evt)

    def run(self):
        a = P4Radmax()
        b = SimAnneal(self.parent)
        P4Radmax.par_fit = []
        P4Radmax.gsa_loop = 0
        self.leastsq_refresh = a.frequency_refresh_leastsq
        self.gsa_refresh = a.frequency_refresh_gsa
        evt = LiveEvent(Live_COUNT, -1, [])
        wx.PostEvent(self.parent, evt)
        self.init_array()

        if self.choice == 1 or self.choice == 2:
            if a.acc_choice is "Numpy":
                func = self.residual_lmfit
            else:
                func = self.residual_lmfit_jit
            if self.choice == 1:
                res = leastsq(func, a.ParamDict['par'],
                              args=(a.ParamDict['Iobs'], a.ParamDict['th']))
                P4Radmax.par_fit = res[0]
                P4Radmax.success = res[1]
            elif self.choice == 2:
                from lmfit import minimize
                maxfev_ = int(a.DefaultDict['maxfev'])*(len(self.fit_params)+1)
                P4Radmax.resultFit = minimize(func, self.fit_params,
                                              args=(a.ParamDict['th'],),
                                              iter_cb=self.per_iteration,
                                              scale_covar=True,
                                              kws={'y': a.ParamDict['Iobs']},
                                              maxfev=(maxfev_),
                                              ftol=a.DefaultDict['ftol'],
                                              xtol=a.DefaultDict['xtol'])
        elif self.choice == 0:
            if a.acc_choice is "Numpy":
                func = self.residual_square
            else:
                func = self.residual_square_jit
            P4Radmax.par_fit = b.gsa(func, self.on_limit_exceeded,
                                     self.data)

        if self.need_abort == 1:
            evt = LiveEvent(Live_COUNT, -1, [], None, None, 1)
            wx.PostEvent(self.parent, evt)
        else:
            evt = LiveEvent(Live_COUNT, -1, [], None, None, 0)
            wx.PostEvent(self.parent, evt)

    def stop(self):
        self._stop.set()
        P4Radmax.gsa_loop = 1
        self.need_abort = 1
        if self.choice == 1:
            evt = LiveEvent(Live_COUNT, -1, [], None, None, 1)
            wx.PostEvent(self.parent, evt)
