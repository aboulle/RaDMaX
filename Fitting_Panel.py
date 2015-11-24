#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

'''
*Radmax Fiting panel module*
'''

from  threading import Thread, Event
from scipy.optimize import leastsq

from Read4Radmax import LogSaver
from Parameters4Radmax import *
from def_XRD import f_Refl
from sim_anneal import SimAnneal
from sys import platform as _platform
from time import sleep
from Icon4Radmax import error_icon, ok_icon

New_project_initial_data = {0:10, 1:1000, 2:10, 3:0.99, 4:2.6, 5:1.001}

pubsub_Load_fitting_panel = "LoadFittingPanel"
pubsub_Read_field_paramters_panel = "ReadParametersPanel"
pubsub_Re_Read_field_paramters_panel = "ReReadParametersPanel"
pubsub_Refresh_fitting_panel = "RefreshFittingPanel"
pubsub_Draw_Fit_Live_XRD = "DrawFitLiveXRD"
pubsub_Draw_Fit_Live_Deformation = "DrawFitLiveDeformation"
pubsub_Update_Fit_Live = "UpdateFitLive"
pubsub_OnFit_Graph = "OnFitGraph"
pubsub_Update_Limit = "UpdateLimit"
pubsub_Update_Gauge = "UpdateGauge"
pubsub_Read_field4Save = "ReadField4Save"
pubsub_changeColor_field4Save = "ChangeColorField4Save"
pubsub_Update_deformation_multiplicator_coef = "UpdateDeformationMultiplicatorCoef"
pubsub_save_project_before_fit = "SaveProjectBeforeFit"
pubsub_gauge_to_zero = "Gauge2zero"
pubsub_On_Limit_Before_Graph = "OnLimitBeforeGraph"
pubsub_Draw_XRD = "DrawXRD"

Live_COUNT = wx.NewEventType()
LiveLimitExceeded_COUNT = wx.NewEventType()
EVT_Live_COUNT = wx.PyEventBinder(Live_COUNT, 1)
EVT_LiveLimitExceeded_COUNT = wx.PyEventBinder(LiveLimitExceeded_COUNT, 1)

#------------------------------------------------------------------------------
class FittingPanel(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar
        self.parent = parent

        size_text = (55,22)
        
        font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
        if _platform == "linux" or _platform == "linux2":
            font_Statictext = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
            font_TextCtrl = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
            font_combobox = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
            font_update = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            vStatictextsize = 16
        elif _platform == "win32":
            font_Statictext = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
            font_TextCtrl = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
            font_combobox = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
            font_update = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            vStatictextsize = 16
        elif _platform == 'darwin':
            font_Statictext = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
            font_TextCtrl = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
            font_combobox = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Arial')
            font_update = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            vStatictextsize = 18

        font_end_fit = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, u'Arial')        
        size_StaticBox = (700, 140)

        """master sizer for the whole panel"""
        mainsizer = wx.GridBagSizer(hgap=0, vgap=1)
        topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.errorsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.centersizer = wx.BoxSizer(wx.VERTICAL)


        FitAlgo_choice = ["GSA", "leastsq"]
        self.ID_ComboStats = wx.NewId()
        FitAlgo_txt = wx.StaticText(self, -1, label=u'Fitting algorithm: ', size=(130,vStatictextsize))
        FitAlgo_txt.SetFont(font_Statictext)
        self.cb_FitAlgo = wx.ComboBox(self, id=self.ID_ComboStats, pos=(50, 30), choices=FitAlgo_choice, style=wx.CB_READONLY)
        self.cb_FitAlgo.SetStringSelection(FitAlgo_choice[0])
        self.Bind(wx.EVT_COMBOBOX, self.onChangeFit, self.cb_FitAlgo)
        self.cb_FitAlgo.SetFont(font_combobox)
        
        topsizer.Add(FitAlgo_txt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        topsizer.Add(self.cb_FitAlgo, 0, wx.ALL, 5)

        """GSA options part"""
        GSA_options_box = wx.StaticBox(self, -1, " GSA options ", size=size_StaticBox)
        GSA_options_box.SetFont(font)
        self.GSA_options_box_sizer = wx.StaticBoxSizer(GSA_options_box, wx.VERTICAL)
        in_GSA_options_box_sizer = wx.GridBagSizer(hgap=10, vgap=1)
        flagSizer = wx.ALL|wx.ALIGN_CENTER_VERTICAL 
        
        temperature_txt = wx.StaticText(self, -1, label=u'Temperature (k)', size=(110,vStatictextsize))
        temperature_txt.SetFont(font_Statictext)
        self.temperature = wx.TextCtrl(self, size=size_text, validator = TextValidator(DIGIT_ONLY))
        self.temperature.SetFont(font_TextCtrl)

        cycle_number_txt = wx.StaticText(self, -1, label=u'Number of cycle', size=(110,vStatictextsize))
        cycle_number_txt.SetFont(font_Statictext)
        self.cycle_number = wx.TextCtrl(self, size=size_text, validator = TextValidator(DIGIT_ONLY))
        self.cycle_number.SetFont(font_TextCtrl)

        cooling_number_txt = wx.StaticText(self, -1, label=u'Number of cooling steps', size=(140,vStatictextsize))
        cooling_number_txt.SetFont(font_Statictext)
        self.cooling_number = wx.TextCtrl(self, size=size_text, validator = TextValidator(DIGIT_ONLY))
        self.cooling_number.SetFont(font_TextCtrl)
        
        in_GSA_options_box_sizer.Add(temperature_txt, pos=(0,0), flag=flagSizer)
        in_GSA_options_box_sizer.Add(self.temperature, pos=(0,1), flag=flagSizer)
        in_GSA_options_box_sizer.Add(cycle_number_txt, pos=(0,2), flag=flagSizer)
        in_GSA_options_box_sizer.Add(self.cycle_number, pos=(0,3), flag=flagSizer)
        in_GSA_options_box_sizer.Add(cooling_number_txt, pos=(0,4), flag=flagSizer)
        in_GSA_options_box_sizer.Add(self.cooling_number, pos=(0,5), flag=flagSizer)

        """Advanced GSA options part"""
        AGSA_options_box = wx.StaticBox(self, -1, " Advanced GSA options (expert users only) ", size=size_StaticBox)
        AGSA_options_box.SetFont(font)
        self.AGSA_options_box_sizer = wx.StaticBoxSizer(AGSA_options_box, wx.VERTICAL)
        in_AGSA_options_box_sizer = wx.GridBagSizer(hgap=10, vgap=0)
        
        qa_txt = wx.StaticText(self, -1, label=u'qa', size=(20,vStatictextsize))
        cooling_number_txt.SetFont(font_Statictext)
        self.qa = wx.TextCtrl(self, size=size_text, validator = TextValidator(DIGIT_ONLY))
        self.qa.SetFont(font_TextCtrl)

        qv_txt = wx.StaticText(self, -1, label=u'qv', size=(20,vStatictextsize))
        qv_txt.SetFont(font_Statictext)
        self.qv = wx.TextCtrl(self, size=size_text, validator = TextValidator(DIGIT_ONLY))
        self.qv.SetFont(font_TextCtrl)

        qt_txt = wx.StaticText(self, -1, label=u'qt', size=(20,vStatictextsize))
        qt_txt.SetFont(font_Statictext)
        self.qt = wx.TextCtrl(self, size=size_text, validator = TextValidator(DIGIT_ONLY))
        self.qt.SetFont(font_TextCtrl)
        
        in_AGSA_options_box_sizer.Add(qa_txt, pos=(0,0), flag=flagSizer)
        in_AGSA_options_box_sizer.Add(self.qa, pos=(0,1), flag=flagSizer)
        in_AGSA_options_box_sizer.Add(qv_txt, pos=(0,2), flag=flagSizer)
        in_AGSA_options_box_sizer.Add(self.qv, pos=(0,3), flag=flagSizer)
        in_AGSA_options_box_sizer.Add(qt_txt, pos=(0,4), flag=flagSizer)
        in_AGSA_options_box_sizer.Add(self.qt, pos=(0,5), flag=flagSizer)

        """Fit part"""
        Fit_box = wx.StaticBox(self, -1, " Fit ", size=size_StaticBox)
        Fit_box.SetFont(font)
        Fit_box_sizer = wx.StaticBoxSizer(Fit_box, wx.VERTICAL)
        in_Fit_box_sizer = wx.GridBagSizer(hgap=5, vgap=0)

        """GSA result part"""
        GSA_results_box = wx.StaticBox(self, -1, " GSA fit results ", size=size_StaticBox)
        GSA_results_box.SetFont(font)
        self.GSA_results_sizer = wx.StaticBoxSizer(GSA_results_box, wx.VERTICAL)
        in_GSA_results_sizer = wx.GridBagSizer(hgap=2, vgap=0)

        """button part"""
        self.FitId = wx.NewId()
        self.StopFitId = wx.NewId()
        self.Restore_strain_Id = wx.NewId()
        self.Restore_dw_Id = wx.NewId()

        self.gauge = wx.Gauge(self, -1, size=(160, 25), style=wx.ALL|wx.EXPAND)
        self.gauge.SetValue(0)
        Emin_txt = wx.StaticText(self, -1, label=u'Emin: ', size=(40,vStatictextsize))
        Emin_txt.SetFont(font_Statictext)
        self.Emin_change_txt = wx.StaticText(self, -1, label=u'', size=(50,vStatictextsize))
        self.Emin_change_txt.SetFont(font_TextCtrl)
        
        param_txt = wx.StaticText(self, -1, label=u'Minima: ', size=(60,vStatictextsize))
        param_txt.SetFont(font_Statictext)
        self.param_change_txt = wx.StaticText(self, -1, label=u'', size=(50,vStatictextsize))
        self.param_change_txt.SetFont(font_TextCtrl)

        self.limitexceeded_txt = wx.StaticText(self, -1, label=u'Limit Exceeded On Parameter: ', size=(190,vStatictextsize))
        self.limitexceeded_txt.SetFont(font_Statictext)
        self.limitexceeded = wx.StaticText(self, -1, label=u'', size=(50,vStatictextsize))
        self.limitexceeded.SetFont(font_TextCtrl)
        
        self.fit_Btn = wx.Button(self, id=self.FitId, label="Fit!")
        self.fit_Btn.SetFont(font_update)
        self.fit_Btn.Bind(wx.EVT_BUTTON, self.onLaunchFit)
        self.stopfit_Btn = wx.Button(self, id=self.StopFitId, label="Stop fit!")
        self.stopfit_Btn.SetFont(font_update)
        self.stopfit_Btn.Bind(wx.EVT_BUTTON, self.onStopFit)
        self.stopfit_Btn.Disable()
        
        self.restore_strain_btn = wx.Button(self, id=self.Restore_strain_Id, label="Strain values", size=(120, 30))
        self.restore_strain_btn.SetFont(font_update)
        self.restore_dw_btn = wx.Button(self, id=self.Restore_dw_Id, label="DW values", size=(120, 30))
        self.restore_dw_btn.SetFont(font_update)
        self.restore_strain_btn.Bind(wx.EVT_BUTTON, self.onRestore)
        self.restore_dw_btn.Bind(wx.EVT_BUTTON, self.onRestore)
        
        in_Fit_box_sizer.Add(self.fit_Btn, pos=(0,0), flag=flagSizer)
        in_Fit_box_sizer.Add(self.stopfit_Btn, pos=(0,1), flag=flagSizer)

        in_GSA_results_sizer.Add(self.gauge, pos=(0,0), flag=flagSizer)
        in_GSA_results_sizer.Add(Emin_txt, pos=(0,1), flag=flagSizer)
        in_GSA_results_sizer.Add(self.Emin_change_txt, pos=(0,2), flag=flagSizer)
        in_GSA_results_sizer.Add(param_txt, pos=(0,3), flag=flagSizer)
        in_GSA_results_sizer.Add(self.param_change_txt, pos=(0,4), flag=flagSizer)
        in_GSA_results_sizer.Add(self.limitexceeded_txt, pos=(0,5), flag=flagSizer)
        in_GSA_results_sizer.Add(self.limitexceeded, pos=(0,6), flag=flagSizer)
#        'Emin = %4.3f' %E_min, '(',int(nb_minima), ')'
        
        """Restore part"""
        Restore_box = wx.StaticBox(self, -1, " Restore previous ", size=(300, 150))
        Restore_box.SetFont(font)
        self.Restore_box_sizer = wx.StaticBoxSizer(Restore_box, wx.VERTICAL)
        in_Restore_box_sizer = wx.GridBagSizer(hgap=0, vgap=1)
        
        in_Restore_box_sizer.Add(self.restore_strain_btn, pos=(0,0))
        in_Restore_box_sizer.Add(self.restore_dw_btn, pos=(1,0))

        self.Restore_box_sizer.Add(in_Restore_box_sizer, 0, wx.ALL, 5)

        self.png = wx.BitmapFromIcon(error_icon.GetIcon())
        self.information_icon = wx.StaticBitmap(self, -1, self.png, (10, 5), (self.png.GetWidth(), self.png.GetHeight()))
        self.information_text = wx.StaticText(self, -1, label=u'', size=(150,20))
        self.information_text.SetFont(font_end_fit)
        self.information_icon.Hide()

        self.residual_error_txt = wx.StaticText(self, -1, label=u'Residual error: ', size=(130,vStatictextsize))
        self.residual_error_txt.SetFont(font_end_fit)
        self.residual_error = wx.StaticText(self, -1, label=u'', size=(100,vStatictextsize))
        self.residual_error.SetFont(font_end_fit)
        self.residual_error_txt.Hide()
        self.errorsizer.Add(self.residual_error_txt, 0, wx.ALL, 5)
        self.errorsizer.Add(self.residual_error, 0, wx.ALL, 5)
        
        self.GSA_options_box_sizer.Add(in_GSA_options_box_sizer, 0, wx.ALL, 5)
        self.AGSA_options_box_sizer.Add(in_AGSA_options_box_sizer, 0, wx.ALL, 5)
        Fit_box_sizer.Add(in_Fit_box_sizer, 0, wx.ALL, 5)
        self.GSA_results_sizer.Add(in_GSA_results_sizer, 0, wx.ALL, 5)
        
        self.centersizer.Add(Fit_box_sizer, 0, wx.ALL & ~wx.TOP, 5)
        self.centersizer.Add(self.GSA_options_box_sizer, 0, wx.ALL, 5)
        self.centersizer.Add(self.AGSA_options_box_sizer, 0, wx.ALL, 5)
        self.centersizer.Add(self.GSA_results_sizer, 0, wx.ALL, 5)
        
        mainsizer.Add(topsizer, pos=(0,0))
        mainsizer.Add(self.centersizer, pos=(1,0), span=(3,1))
        mainsizer.Add(self.Restore_box_sizer, pos=(1,1), span=(1,2))
        mainsizer.Add(self.information_icon, pos=(2,1), flag=wx.ALL, border=10)
        mainsizer.Add(self.information_text, pos=(2,2), flag=wx.TOP, border=15)
        mainsizer.Add(self.errorsizer, pos=(3,1), span=(1,2), flag=wx.TOP, border=15)        
#        mainsizer.Add(self.residual_error_txt, pos=(3,1), span=(1,2), flag=wx.TOP, border=10)
#        mainsizer.Add(self.residual_error, pos=(3,3), flag=wx.TOP, border=10)
        
        
        self.data_fields = {}
        self.data_fields[0] = self.temperature
        self.data_fields[1] = self.cycle_number
        self.data_fields[2] = self.cooling_number
        self.data_fields[3] = self.qa
        self.data_fields[4] = self.qv
        self.data_fields[5] = self.qt
        self.resultprojectfile = len(Fitting_panel_keys)*[1]
        self.resultprojectfile_backup = []
        self.test_limit = []
        
        self.worker_live = None        
        self.par4diff = []
        self.Bind(EVT_Live_COUNT, self.OnLive)
        self.Bind(EVT_LiveLimitExceeded_COUNT, self.Update_Limit)
        
       
        pub.subscribe(self.onLoadProject, pubsub_Load_fitting_panel)
        pub.subscribe(self.RefreshAfterFit, pubsub_Refresh_fitting_panel)
#        pub.subscribe(self.Update_Limit, pubsub_Update_Limit)
        pub.subscribe(self.Update_Gauge, pubsub_Update_Gauge)
        pub.subscribe(self.ReadDataField, pubsub_Read_field4Save)
        pub.subscribe(self.ChangeColorField, pubsub_changeColor_field4Save)
        pub.subscribe(self.Gauge2zero, pubsub_gauge_to_zero)
        
        self.SetSizer(mainsizer)

    def onChangeFit(self, event):
        fitname = event.GetString()
        if fitname == 'GSA':
            self.centersizer.Show(self.GSA_results_sizer)
            self.centersizer.Show(self.GSA_options_box_sizer)
            self.centersizer.Show(self.AGSA_options_box_sizer)
            self.Layout()
        else:
            self.centersizer.Hide(self.GSA_results_sizer)          
            self.centersizer.Hide(self.GSA_options_box_sizer)
            self.centersizer.Hide(self.AGSA_options_box_sizer)
            self.Layout()
        self.Fit()

    def onLoadProject(self, data=None, b=None):
        for ii in self.data_fields:
            self.data_fields[ii].Clear()
        if b == 1:
            for i in range(len(New_project_initial_data)):
                self.data_fields[i].AppendText(str(New_project_initial_data[i]))
                self.resultprojectfile_backup.append(New_project_initial_data[i])
        else:
            for i in range(len(data)):
                self.data_fields[i].AppendText(str(data[i]))
                self.resultprojectfile_backup.append(data[i])
        self.Fit()  
        self.Layout()
        
    def onLaunchthread(self):
        a = P4Diff()
        fitname = self.cb_FitAlgo.GetSelection()
        P4Diff.allparameters = a.initial_parameters + a.fitting_parameters
        self.par4diff = dict(zip(Initial_data_key,a.allparameters))
        if fitname == 0:
            test_deformation_limit = self.onTestDataBeforeFit()
        else:
            test_deformation_limit = True
        if test_deformation_limit == True:
            if fitname == 0:
                logger.log(logging.INFO, "GSA Fit has been launched")
            else:
                logger.log(logging.INFO, "Leastsq Fit has been launched")
            self.RefreshAfterFit(0)
            P4Diff.sp_backup = a.sp
            P4Diff.dwp_backup = a.dwp 
            self.statusbar.SetStatusText(u"Fitting... Please Wait...This may take some time", 0)
            self.Refresh()  
            pub.sendMessage(pubsub_OnFit_Graph)
            P4Diff.fitlive = 1
            self.gauge.SetValue(0)
            self.worker_live = Fit_launcher(self, fitname, self.par4diff)
        else:
            self.parent.notebook.SetSelection(0)
            pub.sendMessage(pubsub_On_Limit_Before_Graph, limit=self.test_limit)

    def onTestDataBeforeFit(self):
        a = P4Diff()
        """ do not use the last value of strain because ou of the scope """
        test_dw = (a.dwp > self.par4diff['min_dw']).all() and (a.dwp[:-1] < self.par4diff['max_dw']).all()
        test_strain = (a.sp[:-1] > self.par4diff['min_strain']).all() and (a.sp < self.par4diff['max_strain']).all()
        if test_dw and test_strain == True:
            return True
        else:
            self.test_limit = []
            self.test_limit.append((a.sp[:-1] > self.par4diff['min_strain']).all())
            self.test_limit.append((a.sp < self.par4diff['max_strain']).all())
            self.test_limit.append((a.dwp > self.par4diff['min_dw']).all())
            self.test_limit.append((a.dwp[:-1] < self.par4diff['max_dw']).all())
            return False            
        
    def OnLive(self, event):
        list4live = event.GetValue()
        stopFit = event.StopFit()
        if list4live[0] != []:
            pub.sendMessage(pubsub_Draw_Fit_Live_XRD, val=list4live[0])
        if list4live[1] != None:
            pub.sendMessage(pubsub_Update_Gauge, val=list4live[1][2], emin=list4live[1][0], param=int(list4live[1][1]))
        if list4live[2] != None:
            pub.sendMessage(pubsub_Draw_Fit_Live_Deformation)
        if stopFit != None:
            pub.sendMessage(pubsub_Refresh_fitting_panel, option=1, case=stopFit)
            pub.sendMessage(pubsub_OnFit_Graph, b=1)
        
    def onStopFit(self, event):
        self.worker_live.stop()
        busy = wx.BusyInfo("One moment please, waiting for threads to die...")
        sleep(2)
        wx.Yield()

    def onRestore(self, event):
        a = P4Diff()
        widget = event.GetId()
        if widget == self.Restore_strain_Id:
            P4Diff.sp = a.sp_backup
            P4Diff.strain_multiplication = 1.0
        elif widget == self.Restore_dw_Id:
            P4Diff.dwp = a.dwp_backup
            P4Diff.DW_multiplication = 1.0
        pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)

    def RefreshAfterFit(self, option, case=None):
        label = ""
        a = P4Diff()
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
            a = P4Diff()
            self.parent.notebook.EnableTab(0, True)
            self.fit_Btn.Enable()
            self.stopfit_Btn.Disable()
            self.restore_strain_btn.Enable()
            self.restore_dw_btn.Enable()
            self.cb_FitAlgo.Enable()
            P4Diff.fitlive = 0
            P4Diff.I_i = a.I_fit
            y_cal = f_Refl(self.par4diff)
            y_cal = y_cal/y_cal.max() + self.par4diff['background']
            P4Diff.residual_error = ((log10(a.Iobs) - log10(y_cal))**2).sum() / len(y_cal)
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
                P4Diff.sp = a.par_fit[:int(self.par4diff['strain_basis_func'])]
                P4Diff.dwp = a.par_fit[-1*int(self.par4diff['dw_basis_func']):]
            elif case == 1:
                self.png = wx.BitmapFromIcon(error_icon.GetIcon())
                self.information_icon.SetBitmap(self.png)
                self.information_icon.Show()
                self.residual_error_txt.Show()
                self.residual_error.SetLabel(str(error))
                label = u"Fit aborted by user"
                logger.log(logging.WARNING, label)
                self.statusbar.SetStatusText(label, 0)    
            if a.par_fit != []:
#                pub.sendMessage(pubsub_Update_Fit_Live)
                pub.sendMessage(pubsub_Draw_XRD)
                pub.sendMessage(pubsub_Update_deformation_multiplicator_coef)
                self.information_text.SetLabel(label)
                self.OnSavefromFit()
                self.Refresh()  
        self.Refresh()  
        self.Fit()
        self.Layout()

    def OnSavefromFit(self):
        a = P4Diff()
        if a.path2ini != '':
            path = a.path2ini
        else:
            path = a.path2drx
        try:
            header = ["2theta", "Iobs", "Icalc"]
            line = u'{:^12} {:^24} {:^12}'.format(*header)
            savetxt(os.path.join(path, a.namefromini + '_' + output_name['out_strain_profile']), column_stack((a.depth, a.strain_i)), fmt='%10.8f')
            savetxt(os.path.join(path, a.namefromini + '_' + output_name['out_dw_profile']), column_stack((a.depth, a.DW_i)), fmt='%10.8f')
            savetxt(os.path.join(path, a.namefromini + '_' + output_name['out_strain']),a.par_fit[:int(self.par4diff['strain_basis_func'])] , fmt='%10.8f')
            savetxt(os.path.join(path, a.namefromini + '_' + output_name['out_dw']), a.par_fit[-1*int(self.par4diff['dw_basis_func']):], fmt='%10.8f')
            savetxt(os.path.join(path, a.namefromini + '_' + output_name['out_XRD']),\
                    column_stack((a.th4live, a.Iobs, a.I_fit)), header=line, fmt='{:^12}'.format('%3.8f'))
            logger.log(logging.INFO, "Data have been saved successfully")
        except IOError:
            logger.log(logging.WARNING, "Impossible to save data to file, please check your path !!")

    def onLaunchFit(self, event):
        a = P4Diff()
        if a.namefromini != "":
            logger.log(logging.INFO, "Start Fit")
            check_empty = self.search4emptyfields()
            if check_empty == True:
                data_float = self.IsDataFloat()
                if data_float == True:
                    pub.sendMessage(pubsub_Read_field_paramters_panel, event=event)
                    if a.success4Fit == 0:
                        self.statusbar.SetStatusText(u"", 0)
                        self.onLaunchthread()
                    else:
                        self.parent.notebook.SetSelection(0)
                        pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)
                elif data_float == False:
                    text = u"Please, fill correctly the fields before to continue"
                    self.statusbar.SetStatusText(text, 0)
                    logger.log(logging.WARNING, text)
            elif check_empty == False:
                text = u"Please, fill the red empty fields before to continue" 
                self.statusbar.SetStatusText(text, 0)
                logger.log(logging.WARNING, text)
        else:
            dlg = GMD.GenericMessageDialog(None, "Please, save the project before to continue",
            "Attention", agwStyle = wx.OK|wx.ICON_INFORMATION)
            dlg.ShowModal()
            pub.sendMessage(pubsub_save_project_before_fit, event=event, case=1)

    def ReadDataField(self):
        P4Diff.checkDataField = 0
        check_empty = self.search4emptyfields()
        if check_empty == True:
            data_float = self.IsDataFloat()
            if data_float == True:
                P4Diff.checkDataField = 1

    def ChangeColorField(self, case):
        if case == 0:
            for ii in range(len(self.data_fields)):
                self.data_fields[ii].SetBackgroundColour('#CCE5FF')
        elif case == 1:
            for ii in range(len(self.data_fields)):
                self.data_fields[ii].SetBackgroundColour('white')
        self.Refresh()
        wx.Yield()

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
            for ii in empty_fields:
                self.data_fields[ii].SetBackgroundColour('red')
            self.Refresh() 
            dlg = GMD.GenericMessageDialog(None, "Please, fill the red empty fields before to continue",
            "Attention", agwStyle = wx.OK|wx.ICON_INFORMATION)
            dlg.ShowModal()
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
        for i in range(len(self.data_fields)):
            self.resultprojectfile[i] = self.data_fields[i].GetValue()
        for i in range(len(Fitting_panel_keys)):
            a = self.data_fields[i].GetValue()
#            print i, a 
            IsFloat.append(self.Is_number(a))
        if False in IsFloat:
            dataFloat = False
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
            temp = [float(j) for j in self.resultprojectfile]
            P4Diff.fitting_parameters = temp
        return dataFloat

    def Update_Gauge(self, val, emin, param):
        self.gauge.SetValue(val)
        self.Emin_change_txt.SetLabel('%4.3f' %emin)
        self.param_change_txt.SetLabel(str(param))

    def Update_Limit(self, event):
        val = event.GetValue()
        pub.sendMessage(pubsub_Update_Limit, val=val)

    def Update_Limit_value(self, val):
        if val != -1:
            self.limitexceeded.SetLabel(str(val))
            self.limitexceeded.SetForegroundColour('#FF0000')
        else:
            self.limitexceeded.SetLabel("")
            self.limitexceeded.SetForegroundColour('#000000')
        
    def Gauge2zero(self):
        self.gauge.SetValue(0)
        self.information_icon.Hide()
        self.information_text.SetLabel(u"")


#------------------------------------------------------------------------------
class LiveEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, value=None, data=None, deformation=None, stopfit=None):
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

#------------------------------------------------------------------------------
class LiveLimitExceeded(wx.PyCommandEvent):
    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        return self._value

       
#------------------------------------------------------------------------------
class Fit_launcher(Thread):
    def __init__(self, parent, choice, data):
        Thread.__init__(self)
        self.parent = parent
        self.choice = choice
        self.data = data
        self.need_abort = 0
        self.launch = 0
        self.count = 0
        self.leastsq_refresh = 0
        self.gsa_refresh = 0
        self.gauge_counter = 0
        self._stop = Event()
        self.start()

    def LimitExceeded(self, val):
        if self.need_abort == 0:
            evt = LiveLimitExceeded(LiveLimitExceeded_COUNT, -1, val)
            wx.PostEvent(self.parent, evt)

    def residual(self, p, y, x):
        P4Diff._fp_min = p
        y_cal = f_Refl(self.data)
        y_cal = y_cal/y_cal.max() + self.data['background']
        self.count = self.count + 1
        if self.count % self.leastsq_refresh == 0:
            deformation = [p]
            evt = LiveEvent(Live_COUNT, -1, y_cal, None, deformation)
            wx.PostEvent(self.parent, evt)
            sleep(0.5)
        return (log10(y) - log10(y_cal))

    def residual_square(self, p, E_min, nb_minima, val4gauge):
        a = P4Diff()
        P4Diff._fp_min = p
        y_cal = f_Refl(self.data)
        y_cal = y_cal/y_cal.max() + self.data['background']
        self.count = self.count + 1
        if self.count == 1:
            data = [E_min, nb_minima, self.gauge_counter]
            evt = LiveEvent(Live_COUNT, -1, [])
            wx.PostEvent(self.parent, evt)
        if self.count % val4gauge == 0:
            self.gauge_counter += a.gaugeUpdate
            data = [E_min, nb_minima, self.gauge_counter]
            deformation = [p]
            evt = LiveEvent(Live_COUNT, -1, y_cal, data, deformation)
            wx.PostEvent(self.parent, evt)
        return ((log10(a.Iobs) - log10(y_cal))**2).sum() / len(y_cal)

    def run(self):
        a = P4Diff()
        b = SimAnneal(self.parent)
        P4Diff.par_fit = []
        P4Diff.gsa_loop = 0
        self.leastsq_refresh = a.frequency_refresh_leastsq
        self.gsa_refresh = a.frequency_refresh_gsa
        evt = LiveEvent(Live_COUNT, -1, [])
        wx.PostEvent(self.parent, evt)

        if self.choice == 1:
            P4Diff.par_fit, P4Diff.success = leastsq(self.residual, a.par, args = (a.Iobs, a.th))
        elif self.choice == 0:
            P4Diff.par_fit = b.gsa(self.residual_square, self.LimitExceeded, self.data)

        if self.need_abort == 1:
            evt = LiveEvent(Live_COUNT, -1, [], None, None, 1)
            wx.PostEvent(self.parent, evt)
        else:
            evt = LiveEvent(Live_COUNT, -1, [], None, None, 0)
            wx.PostEvent(self.parent, evt)
    
    def stop(self):
        self._stop.set()
        P4Diff.gsa_loop = 1
        self.need_abort = 1
        if self.choice == 1:
            evt = LiveEvent(Live_COUNT, -1, [], None, None, 1)
            wx.PostEvent(self.parent, evt)


