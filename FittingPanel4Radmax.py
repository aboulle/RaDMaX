#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

# =============================================================================
# Radmax Fiting panel module
# =============================================================================

import wx
import wx.lib.agw.advancedsplash as AS
from wx.lib.pubsub import pub
import wx.lib.agw.genericmessagedialog as GMD
import wx.lib.scrolledpanel as scrolled

import Parameters4Radmax as p4R
from Parameters4Radmax import P4Rm
import Settings4Radmax as S4R
from Settings4Radmax import TextValidator, Sound_Launcher

from Fitting4Radmax import Fitting4Radmax, Fit_launcher
from Read4Radmax import SaveFile4Diff
from Calcul4Radmax import Calcul4Radmax
from Led4Radmax import LED
from DB4Radmax import DataBaseUse

from sys import platform as _platform
from random import randint
from numpy import column_stack

from Icon4Radmax import error_icon, ok_icon, stop_thread, stop_thread_morpheus

import logging
logger = logging.getLogger(__name__)

DIGIT_ONLY = 2

New_project_initial_data = {0: 10, 1: 1000, 2: 10}

pubsub_Load_project = "LoadProject"
pubsub_Read_field4Save = "ReadField4Save"
pubsub_Re_Read_field_paramters_panel = "ReReadParametersPanel"
pubsub_Draw_Fit_Live_XRD = "DrawFitLiveXRD"
pubsub_Update_Fit_Live = "UpdateFitLive"
pubsub_OnFit_Graph = "OnFitGraph"
pubsub_on_update_limit = "UpdateLimit"
pubsub_on_update_gauge = "UpdateGauge"
pubsub_changeColor_field4Save = "ChangeColorField4Save"
pubsub_Update_deformation_multiplicator_coef = "UpdateDefMultiplicatorCoef"
pubsub_gauge_to_zero = "Gauge2zero"
pubsub_update_sp_dwp_eta = "UpdatespdwpEta"
pubsub_Read_sp_dwp = "ReadSpDwp"
pubsub_on_refresh_GUI = "OnRefreshGUI"
pubsub_on_launch_thread = "OnLaunchThread"
pubsub_Draw_XRD = "DrawXRD"

pubsub_save_from_DB = "SaveFromDB"
pubsub_add_damaged_before_fit = "AddDamagedBeforeFit"
pubsub_adjust_nb_cycle = "AdjustNbCycle"


# ------------------------------------------------------------------------------
class FittingPanel(scrolled.ScrolledPanel):
    def __init__(self, parent, statusbar):
        scrolled.ScrolledPanel.__init__(self, parent)
        self.statusbar = statusbar
        self.parent = parent

        size_text = (55, 22)

        font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
        if _platform == "linux" or _platform == "linux2":
            size_nocool = 160
            size_limitexceed = 110
            font_Statictext = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_combobox = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            vStatictextsize = 16
        elif _platform == "win32":
            size_nocool = 140
            size_limitexceed = 110
            font_Statictext = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                      False, u'Arial')
            font_TextCtrl = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_combobox = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                                    False, u'Arial')
            font_update = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            vStatictextsize = 16
        elif _platform == 'darwin':
            size_nocool = 160
            size_limitexceed = 110
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

        self.ID_ComboStats = wx.NewId()
        FitAlgo_txt = wx.StaticText(self, -1, label=u'Fitting algorithm: ',
                                    size=(130, vStatictextsize))
        FitAlgo_txt.SetFont(font_Statictext)
        self.cb_FitAlgo = wx.ComboBox(self, id=self.ID_ComboStats,
                                      pos=(50, 30),
                                      choices=p4R.FitAlgo_choice,
                                      style=wx.CB_READONLY)
        self.cb_FitAlgo.SetStringSelection(p4R.FitAlgo_choice[0])
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
                                           size=(size_nocool, vStatictextsize))
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

        name_limit = u'Limit Exceeded: '
        self.on_limit_exceeded_txt = wx.StaticText(self, -1,
                                                   label=name_limit,
                                                   size=(size_limitexceed,
                                                         vStatictextsize))
        self.on_limit_exceeded_txt.SetFont(font_Statictext)

        self.led = LED(self)

        live_Nb_cycle_txt = wx.StaticText(self, -1, label=u'Current cycle: ',
                                          size=(95, vStatictextsize))
        live_Nb_cycle_txt.SetFont(font_Statictext)
        self.live_Nb_cycle = wx.StaticText(self, -1, label=u'',
                                           size=(50, vStatictextsize))
        self.live_Nb_cycle.SetFont(font_TextCtrl)

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

        in_GSA_results_sizer.Add(Emin_txt, pos=(0, 0),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(self.Emin_change_txt, pos=(0, 1),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(param_txt, pos=(0, 2),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(self.param_change_txt, pos=(0, 3),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(self.on_limit_exceeded_txt, pos=(0, 4),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(self.led, pos=(0, 5),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(live_Nb_cycle_txt, pos=(0, 8),
                                 flag=flagSizer)
        in_GSA_results_sizer.Add(self.live_Nb_cycle, pos=(0, 9),
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

        self.png = error_icon.GetBitmap()
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

        self.Textcontrol = [self.temperature, self.cycle_number,
                            self.cooling_number]
        Textcontrolen = range(len(self.Textcontrol))
        self.data_fields = dict(zip(Textcontrolen, self.Textcontrol))

        self.resultprojectfile = len(self.data_fields)*[1]

        self.random_thread_image = 0
        self.random_music = 0

        self.Bind(S4R.EVT_Live_COUNT, self.on_live)
        self.Bind(S4R.EVT_LiveLimitExceeded_COUNT, self.on_update_limit)
        self.Bind(S4R.EVT_Live_count_NbCycle, self.on_update_nb_cycle)

        pub.subscribe(self.on_load_project, pubsub_Load_project)
        pub.subscribe(self.on_refresh_GUI, pubsub_on_refresh_GUI)
        pub.subscribe(self.on_launch_thread, pubsub_on_launch_thread)
        pub.subscribe(self.on_update_gauge, pubsub_on_update_gauge)
        pub.subscribe(self.on_read_data_field, pubsub_Read_field4Save)
        pub.subscribe(self.on_apply_color_field, pubsub_changeColor_field4Save)
        pub.subscribe(self.gauge2zero, pubsub_gauge_to_zero)
        pub.subscribe(self.on_adjust_nb_cycle, pubsub_adjust_nb_cycle)

        self.SetupScrolling()
        self.SetAutoLayout(1)
        self.SetSizer(mainsizer)

    def on_change_fit(self, event):
        """
        Fit selection GSA ou Leastsq
        """
        fitname = event.GetString()
        if fitname == 'GSA':
            self.centersizer.Show(self.GSA_results_sizer)
            self.centersizer.Show(self.GSA_options_box_sizer)
        else:
            self.centersizer.Hide(self.GSA_results_sizer)
            self.centersizer.Hide(self.GSA_options_box_sizer)
        self.Refresh()

    def on_load_project(self, b=None):
        """
        chargement des données provenant du fichier .ini
        """
        for ii in self.data_fields:
            self.data_fields[ii].Clear()
        if b == 1:
            for i in range(len(New_project_initial_data)):
                p_ = New_project_initial_data[i]
                self.data_fields[i].AppendText(str(p_))
        else:
            a = P4Rm()
            i = 0
            for k in p4R.F_p:
                self.data_fields[i].AppendText(str(a.AllDataDict[k]))
                i += 1
        self.Refresh()

    def on_read_data_field(self, case=None):
        """
        lecture des champs
        test si float
        """
        P4Rm.checkFittingField = 0
        check_empty = self.on_search_empty_fields()
        if check_empty is True:
            data_float = self.is_data_float()
            if data_float is True:
                P4Rm.checkFittingField = 1

    def on_apply_color_field(self, color):
        """
        permet de changer la couleur des champs lors du lancement du fit
        vert: champ vide
        rouge: pas un nombre (redondant avec le validator)
        bleu: sauvegarde des données
        """
        for ii in range(len(self.data_fields)):
            self.data_fields[ii].SetBackgroundColour(color)
        self.Refresh()
        wx.Yield()

    def on_launch_fit(self, event):
        """
        lancement du fit.
        test de la valeur damaged_depth, si celle-ci est nulle alors
        un pop up s'ouvre pour demander à l'utilisateur de mettre une
        valeur non nulle.
        """
        a = P4Rm()
        if a.AllDataDict['damaged_depth'] == 0:
            pub.sendMessage(pubsub_add_damaged_before_fit)
        else:
            if not a.ParamDict['th'].any():
                return
            else:
                b = Fitting4Radmax()
                P4Rm.fit_type = self.cb_FitAlgo.GetSelection()
                b.on_launch_fit()

    def on_adjust_nb_cycle(self):
        """
        mise à jour du champ nb_cycle_max.
        la valeur doit etre égale ou superieur
        à la valeur de nb_palier.
        Si inferieur la valeur est égale à celle contenu dans nb_palier
        """
        a = P4Rm()
        self.cycle_number.Clear()
        self.cycle_number.AppendText(str(a.AllDataDict['nb_cycle_max']))
        self.Refresh()

    def on_launch_thread(self):
        """
        lancement du thread du fit
        """
        a = P4Rm()
        b = Fitting4Radmax()
        if a.fit_type == 1:
            success = b.on_test_lmfit()
            if success is True:
                P4Rm.FitDict['worker_live'] = Fit_launcher(self, 2)
            else:
                P4Rm.FitDict['worker_live'] = Fit_launcher(self, 1)
        else:
            P4Rm.FitDict['worker_live'] = Fit_launcher(self, 0)

    def on_refresh_GUI(self, option, case=None):
        """
        rafraichissement de l'IU avant et après le fit
        """
        label = ""
        a = P4Rm()
        c = Fitting4Radmax()
        d = DataBaseUse()
        if option == 0:
            self.on_disenable_notebook(False)
            msg_ = u"Fitting... Please Wait...This may take some time"
            self.statusbar.SetStatusText(msg_, 0)
            self.progressBar.Pulse()
            self.fit_Btn.Disable()
            self.stopfit_Btn.Enable()
            self.restore_strain_btn.Disable()
            self.restore_dw_btn.Disable()
            self.cb_FitAlgo.Disable()
            self.information_icon.Hide()
            self.information_text.SetLabel(u"")
            self.residual_error_txt.Hide()
            self.residual_error.SetLabel(u"")
            self.random_thread_image = randint(0, 100)
            self.random_music = randint(0, 200)
        elif option == 1:
            P4Rm.fitlive = 0
            self.progressBar.SetValue(0)
            self.on_disenable_notebook(True)
            self.fit_Btn.Enable()
            self.stopfit_Btn.Disable()
            self.restore_strain_btn.Enable()
            self.restore_dw_btn.Enable()
            self.cb_FitAlgo.Enable()
            c.on_fit_ending(case)
            error = round(a.residual_error, 4)
            led_work = self.led
            led_work.SetState(0)
            if case == 0:
                png = ok_icon.GetBitmap()
                label = u"Fit ended normally"
            elif case == 1:
                png = error_icon.GetBitmap()
                label = u"Fit aborted by user"
            self.on_finish_fit(png, error, label)
            self.information_text.SetLabel(label)
            self.on_save_data()
            pub.sendMessage(pubsub_Draw_XRD)
            pub.sendMessage(pubsub_OnFit_Graph, b=1)
            pub.sendMessage(pubsub_Update_deformation_multiplicator_coef)
            pub.sendMessage(pubsub_update_sp_dwp_eta)
            pub.sendMessage(pubsub_Read_sp_dwp)
            Sound_Launcher(self, case, self.random_music)
            if a.DefaultDict['use_database'] is True:
                d.on_fill_database_and_list(case)
            if not a.lmfit_install:
                pub.sendMessage(pubsub_Update_Fit_Live)

    def on_finish_fit(self, png, error, label):
        """
        Affichage de l'image et du texte de fin de fit
        Fit ended normally
        Fit aborted by user
        ecriture dans le fichier log
        """
        self.information_icon.SetBitmap(png)
        self.information_icon.Show()
        self.residual_error_txt.Show()
        self.residual_error.SetLabel(str(error))
        self.statusbar.SetStatusText(label, 0)
        logger.log(logging.INFO, label)
        self.Refresh()
        self.SetAutoLayout(1)
        self.Layout()

    def on_save_data(self):
        """
        sauvegarde des données des champs
        lecture des champs
        """
        a = P4Rm()
        b = SaveFile4Diff()
        if a.pathfromDB == 1:
            pub.sendMessage(pubsub_save_from_DB, case=1)
            P4Rm.pathfromDB = 0
        b.on_save_from_fit()

    def on_disenable_notebook(self, case):
        """
        Active et deactive les onglets en fonction des besoins du fit
        """
        a = P4Rm()
        self.parent.notebook.EnableTab(0, case)
        self.parent.notebook.EnableTab(1, case)
        if self.parent.notebook.GetPageCount() > 3:
            if a.DefaultDict['use_database'] is True:
                self.parent.notebook.EnableTab(3, case)
                self.parent.notebook.EnableTab(4, case)
            else:
                self.parent.notebook.EnableTab(3, False)
                self.parent.notebook.EnableTab(4, False)

    def on_live(self, event):
        """
        recupere les données provenant du thread du fit et
        mise à jour des champs et des graphs
        """
        list4live = event.GetValue()
        stopFit = event.StopFit()
        if list4live[0] != []:
            pub.sendMessage(pubsub_Draw_Fit_Live_XRD, val=list4live[0])
        if list4live[1] is not None:
            pub.sendMessage(pubsub_on_update_gauge, emin=list4live[1][0],
                            param=int(list4live[1][1]))
        if list4live[2] is not None:
            b = Calcul4Radmax()
            b.f_strain_DW()
        if stopFit is not None:
            self.on_refresh_GUI(1, stopFit)
            pub.sendMessage(pubsub_OnFit_Graph, b=1)

    def on_stop_fit(self, event):
        """
        A la fin du fit permet d'afficher le pop image soit l'icone du prog
        soit morpheus_matrix de manière aléatoire
        """
        b = Fitting4Radmax()
        l_numb = [2, 24, 56, 89]
        if self.random_thread_image in l_numb:
            bmp = stop_thread_morpheus.GetBitmap()
        else:
            bmp = stop_thread.GetBitmap()
        shadow = wx.WHITE
        AS.AdvancedSplash(None, bitmap=bmp, timeout=2000,
                          agwStyle=AS.AS_TIMEOUT | AS.AS_CENTER_ON_PARENT,
                          shadowcolour=shadow)
        b.on_stop_fit()

    def on_restore(self, event):
        """
        Permet de recuperer les valeurs d'avant le fit avec les boutons restore
        """
        a = P4Rm()
        widget = event.GetId()
        if widget == self.Restore_strain_Id:
            P4Rm.ParamDict['sp'] = a.ParamDictbackup['sp']
            P4Rm.ParamDict['strain_multiplication'] = 1.0
        elif widget == self.Restore_dw_Id:
            P4Rm.ParamDict['dwp'] = a.ParamDictbackup['dwp']
            P4Rm.ParamDict['DW_multiplication'] = 1.0
        pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)

    def on_update_gauge(self, emin, param):
        self.Emin_change_txt.SetLabel('%4.3f' % emin)
        self.param_change_txt.SetLabel(str(param))

    def on_update_limit(self, event):
        """
        controle du bouton led qui change de couleur en rouge lorsqu'un
        parametre depasse la limite
        """
        val = event.GetValue()
        if val != -1:
            led_work = self.led
            led_work.SetState(1)
        else:
            led_work = self.led
            led_work.SetState(0)
        pub.sendMessage(pubsub_on_update_limit, val=val)

    def on_update_nb_cycle(self, event):
        """
        Mise à jour du nombre de cycle effectué
        """
        val = event.GetValue()
        self.live_Nb_cycle.SetLabel(str(val))

    def gauge2zero(self):
        """
        remise à zero des objets de suivi du fit
        """
        self.information_icon.Hide()
        self.information_text.SetLabel("")
        self.residual_error_txt.Hide()
        self.residual_error.SetLabel("")
        self.Refresh()

    def on_search_empty_fields(self):
        """
        Verification des champs, recherche des champs vide
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
        """
        test si la valeur du champ est bien un float
        """
        try:
            float(s)
            return True
        except ValueError:
            return False

    def is_data_float(self):
        """
        test si la valeur du champ est bien un float
        ecrit les données dans P4Rm.fitting_parameters
        """
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
            P4Rm.fitting_parameters = temp
        return dataFloat
