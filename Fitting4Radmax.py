#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

# =============================================================================
# Fitting Module
# =============================================================================


import wx
from wx.lib.pubsub import pub

import Parameters4Radmax as p4R
from Parameters4Radmax import P4Rm
import Settings4Radmax as S4R

from Calcul4Radmax import Calcul4Radmax

from threading import Thread, Event
from scipy.optimize import leastsq
from scipy import convolve, in1d, log10

from time import sleep

import numpy as np
from numpy import around, array, arange, asarray

from Def_XRD4Radmax import f_Refl, f_Refl_fit

from GSA4Radmax import gsa

from Def_Strain4Radmax import f_strain
from Def_DW4Radmax import f_DW

import logging

logger = logging.getLogger(__name__)

"""Pubsub message"""

pubsub_Read_field4Save = "ReadField4Save"
pubsub_OnFit_Graph = "OnFitGraph"

pubsub_on_refresh_GUI = "OnRefreshGUI"
pubsub_Hide_Show_GSA = "HideShowGSA"
pubsub_on_launch_thread = "OnLaunchThread"

pubsub_save_project_before_fit = "SaveProjectBeforeFit"
pubsub_adjust_nb_cycle = "AdjustNbCycle"


# -----------------------------------------------------------------------------
class Fitting4Radmax():
    def on_launch_fit(self):
        a = P4Rm()
        b = Calcul4Radmax()
        b.on_update()
        pub.sendMessage(pubsub_Read_field4Save)

        if a.PathDict['namefromini'] != "":
            logger.log(logging.INFO, "Start Fit")
            if (a.checkInitialField is 1 and a.checkGeometryField is 1 and
                        a.checkFittingField is 1):
                P4Rm.allparameters = (a.initial_parameters +
                                      a.fitting_parameters +
                                      a.sample_geometry)
                i = 0
                for k in p4R.IP_p + p4R.F_p + p4R.SG_p:
                    P4Rm.AllDataDict[k] = a.allparameters[i]
                    i += 1
                if a.AllDataDict['nb_cycle_max'] < a.AllDataDict['nb_palier']:
                    P4Rm.AllDataDict['nb_cycle_max'] = a.AllDataDict['nb_palier']
                    pub.sendMessage(pubsub_adjust_nb_cycle)
                self.onLaunchtest()
            else:
                return
        else:
            pub.sendMessage(pubsub_save_project_before_fit, case=2)

    def onLaunchtest(self):
        test_deformation_limit = self.on_test_data_before_fit()
        if test_deformation_limit is True:
            self.on_launch_thread()
        else:
            pub.sendMessage(pubsub_Hide_Show_GSA)

    def on_test_data_before_fit(self):
        a = P4Rm()
        P4Rm.ParamDict['sp'] = np.asarray(a.ParamDict['sp'])
        P4Rm.ParamDict['dwp'] = np.asarray(a.ParamDict['dwp'])
        if a.AllDataDict['model'] == 0. or a.AllDataDict['model'] == 1.:
            """ do not use the last value of strain because
            is out of the scope """
            test_dw = (all(a.ParamDict['dwp'] > a.AllDataDict['dw_min']) and
                       all(a.ParamDict['dwp'][:-1] < a.AllDataDict['dw_max']))
            test_strain = (all(a.ParamDict['sp'][:-1] >
                               a.AllDataDict['strain_min']) and
                           all(a.ParamDict['sp'] <
                               a.AllDataDict['strain_max']))
            if test_dw and test_strain:
                return True
            else:
                return False
        elif a.AllDataDict['model'] == 2.:
            i = 0
            ls_ = [0, 4, 5, 6]
            lse_ = [0, 2, 2, 4]
            ld_ = [x + 6 for x in ls_]
            lde_ = [x + 6 for x in lse_]
            test_dw = [False] * len(a.ParamDict['dwp'])
            test_strain = [False] * len(a.ParamDict['sp'])
            for val_dwp, val_sp in zip(a.ParamDict['dwp'],
                                       a.ParamDict['sp']):
                if i in ls_:
                    v_ = ls_.index(i)
                    ve_ = lse_[v_]
                    if val_sp < a.AllDataDict[p4R.GSAp_[ve_]]:
                        test_strain[i] = True
                    elif val_sp > a.AllDataDict[p4R.GSAp_[ve_ + 1]]:
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
                    if val_dwp < a.AllDataDict[p4R.GSAp_[ve_]]:
                        test_dw[i] = True
                    elif val_dwp > a.AllDataDict[p4R.GSAp_[ve_ + 1]]:
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

    def on_launch_thread(self):
        a = P4Rm()
        if a.fit_type == 0:
            logger.log(logging.INFO, "GSA Fit has been launched")
        else:
            logger.log(logging.INFO, "Leastsq Fit has been launched")

        P4Rm.fitlive = 1
        P4Rm.ParamDictbackup['sp'] = a.ParamDict['sp']
        P4Rm.ParamDictbackup['dwp'] = a.ParamDict['dwp']
        P4Rm.ParamDictbackup['I_i'] = a.ParamDict['I_i']
        pub.sendMessage(pubsub_OnFit_Graph)
        pub.sendMessage(pubsub_on_refresh_GUI, option=0, case=0)
        sleep(0.3)
        pub.sendMessage(pubsub_on_launch_thread)

    def on_stop_fit(self):
        P4Rm.FitDict['worker_live'].stop()

    def on_fit_ending(self, case):
        a = P4Rm()
        P4Rm.ParamDict['I_i'] = a.ParamDict['I_fit']
        y_cal = f_Refl(a.AllDataDict['geometry'])
        y_cal = y_cal / y_cal.max() + a.AllDataDict['background']
        temp = ((log10(a.ParamDict['Iobs']) - log10(y_cal)) ** 2).sum()
        P4Rm.residual_error = temp / len(y_cal)

        if a.fit_type == 0:
            t_ = a.par_fit[:int(a.AllDataDict['strain_basis_func'])]
            P4Rm.ParamDict['sp'] = t_
            t_ = a.par_fit[-1 * int(a.AllDataDict['dw_basis_func']):]
            P4Rm.ParamDict['dwp'] = t_
        else:
            if a.lmfit_install:
                self.on_read_data_from_lmfit()
            else:
                t_ = a.par_fit[:int(a.AllDataDict['strain_basis_func'])]
                P4Rm.ParamDict['sp'] = t_
                t_ = a.par_fit[-1 * int(a.AllDataDict['dw_basis_func']):]
                P4Rm.ParamDict['dwp'] = t_

    def on_modify_deformation_limits(self, state):
        a = P4Rm()
        case = state.index(True)
        if a.AllDataDict['model'] == 0. or a.AllDataDict['model'] == 1.:
            value = 0.1
            if case is 0:
                ''' Modify input'''
                i = 0
                for val_dwp, val_sp in zip(a.ParamDict['dwp'],
                                           a.ParamDict['sp']):
                    if val_dwp < a.AllDataDict['dw_min']:
                        val_ = a.AllDataDict['dw_min'] + value
                        P4Rm.ParamDict['dwp'][i] = val_
                    elif val_dwp > a.AllDataDict['dw_max']:
                        val_ = a.AllDataDict['dw_max'] - value
                        P4Rm.ParamDict['dwp'][i] = val_
                    if val_sp < a.AllDataDict['strain_min']:
                        val_ = a.AllDataDict['strain_min'] + value
                        P4Rm.ParamDict['sp'][i] = val_
                    elif val_sp > a.AllDataDict['strain_max']:
                        val_ = a.AllDataDict['strain_max'] - value
                        P4Rm.ParamDict['sp'][i] = val_
                    i += 1
                self.on_launch_thread()
            elif case is 1:
                ''' Modify limits '''
                roundval = 4
                t_min_dw = [False] * len(a.ParamDict['dwp'])
                t_max_dw = [False] * len(a.ParamDict['dwp'])
                t_min_sp = [False] * len(a.ParamDict['sp'])
                t_max_sp = [False] * len(a.ParamDict['sp'])
                i = 0
                for val_dwp, val_sp in zip(a.ParamDict['dwp'],
                                           a.ParamDict['sp']):
                    if val_dwp < a.AllDataDict['dw_min']:
                        t_min_dw[i] = True
                    elif val_dwp > a.AllDataDict['dw_max']:
                        t_max_dw[i] = True
                    if val_sp < a.AllDataDict['strain_min']:
                        t_min_sp[i] = True
                    elif val_sp > a.AllDataDict['strain_max']:
                        t_max_sp[i] = True
                    i += 1
                if True in t_min_dw:
                    round_ = round(min(a.ParamDict['dwp']) - value, roundval)
                    P4Rm.AllDataDict['dw_min'] = round_
                elif True in t_max_dw:
                    round_ = round(max(a.ParamDict['dwp']) + value, roundval)
                    P4Rm.AllDataDict['dw_max'] = round_
                if True in t_min_sp:
                    round_ = round(min(a.ParamDict['sp']) - value, roundval)
                    P4Rm.AllDataDict['strain_min'] = round_
                if True in t_max_sp:
                    round_ = round(max(a.ParamDict['sp']) + value, roundval)
                    P4Rm.AllDataDict['strain_max'] = round_
                self.on_launch_thread()
            elif case is 2:
                return 0

        elif a.AllDataDict['model'] == 2.:
            value = 0.5
            if case is 0:
                ''' Modify input'''
                i = 0
                ls_ = [0, 4, 5, 6]
                lse_ = [0, 2, 2, 4]
                ld_ = [x + 6 for x in ls_]
                lde_ = [x + 6 for x in lse_]
                for val_dwp, val_sp in zip(a.ParamDict['dwp'],
                                           a.ParamDict['sp']):
                    if i in ls_:
                        v_ = ls_.index(i)
                        ve_ = lse_[v_]
                        if val_sp < a.AllDataDict[p4R.GSAp_[ve_]]:
                            val_ = a.AllDataDict[p4R.GSAp_[ve_]] + value
                            P4Rm.ParamDict['sp'][i] = val_
                        elif val_sp > a.AllDataDict[p4R.GSAp_[ve_ + 1]]:
                            val_ = a.AllDataDict[p4R.GSAp_[ve_ + 1]] - value
                            P4Rm.ParamDict['sp'][i] = val_
                    else:
                        if val_sp < 0.:
                            val_ = value
                            P4Rm.ParamDict['sp'][i] = val_
                        elif val_sp > 1.:
                            val_ = 1. - value
                            P4Rm.ParamDict['sp'][i] = val_
                    j = i + 6
                    if j in ld_:
                        v_ = ld_.index(j)
                        ve_ = lde_[v_]
                        if val_dwp < a.AllDataDict[p4R.GSAp_[ve_]]:
                            val_ = a.AllDataDict[p4R.GSAp_[ve_]] + value
                            P4Rm.ParamDict['dwp'][i] = val_
                        elif val_dwp > a.AllDataDict[p4R.GSAp_[ve_ + 1]]:
                            val_ = a.AllDataDict[p4R.GSAp_[ve_ + 1]] - value
                            P4Rm.ParamDict['dwp'][i] = val_
                    else:
                        if val_dwp < 0.:
                            val_ = value
                            P4Rm.ParamDict['dwp'][i] = val_
                        elif val_dwp > 1.:
                            val_ = 1. - value
                            P4Rm.ParamDict['dwp'][i] = val_
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
                ld_ = [x + 6 for x in ls_]
                lde_ = [x + 6 for x in lse_]
                test_dw_min = [False] * len(ls_)
                test_dw_max = [False] * len(ls_)
                test_strain_min = [False] * len(ls_)
                test_strain_max = [False] * len(ls_)
                for val_dwp, val_sp in zip(a.ParamDict['dwp'],
                                           a.ParamDict['sp']):
                    if i in ls_:
                        v_ = ls_.index(i)
                        ve_ = lse_[v_]
                        if val_sp < a.AllDataDict[p4R.GSAp_[ve_]]:
                            test_strain_min[k] = True
                        elif val_sp > a.AllDataDict[p4R.GSAp_[ve_ + 1]]:
                            test_strain_max[k] = True
                        k += 1
                    j = i + 6
                    if j in ld_:
                        v_ = ld_.index(j)
                        ve_ = lde_[v_]
                        if val_dwp < a.AllDataDict[p4R.GSAp_[ve_]]:
                            test_dw_min[l] = True
                        elif val_dwp > a.AllDataDict[p4R.GSAp_[ve_ + 1]]:
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
                            P4Rm.AllDataDict[index_] = round_
                elif True in test_strain_max:
                    for a_ in test_strain_max:
                        if a_ is True:
                            v_ = test_strain_max.index(True)
                            val_ = a.ParamDict['sp'][ls_[v_]] + value
                            round_ = round(val_, roundval)
                            index_ = dict_max_[v_]
                            P4Rm.AllDataDict[index_] = round_
                if True in test_dw_min:
                    for a_ in test_dw_min:
                        if a_ is True:
                            v_ = test_dw_min.index(True)
                            val_ = a.ParamDict['dwp'][ls_[v_]] - value
                            round_ = round(val_, roundval)
                            index_ = dict_min_[v_ + 4]
                            P4Rm.AllDataDict[index_] = round_
                elif True in test_dw_max:
                    for a_ in test_dw_max:
                        if a_ is True:
                            v_ = test_dw_max.index(True)
                            val_ = a.ParamDict['dwp'][ls_[v_]] + value
                            round_ = round(val_, roundval)
                            index_ = dict_max_[v_ + 4]
                            P4Rm.AllDataDict[index_] = round_
                self.on_launch_thread()
            elif case is 2:
                return 0

    def on_test_lmfit(self):
        a = P4Rm()
        if not a.lmfit_install:
            return False
        else:
            from lmfit import Parameters
            fit_params = Parameters()
            if a.AllDataDict['model'] == 2:
                fit_params.add('heigt_strain', value=a.ParamDict['sp'][0],
                               min=a.AllDataDict['strain_height_min'],
                               max=a.AllDataDict['strain_height_max'],
                               vary=a.ParamDict['state_sp'][0])
                fit_params.add('loc_strain', value=a.ParamDict['sp'][1],
                               min=0.,
                               max=1.,
                               vary=a.ParamDict['state_sp'][1])
                fit_params.add('fwhm_1_strain', value=a.ParamDict['sp'][2],
                               min=0.,
                               max=1.,
                               vary=a.ParamDict['state_sp'][2])
                fit_params.add('fwhm_2_strain', value=a.ParamDict['sp'][3],
                               min=0.,
                               max=1.,
                               vary=a.ParamDict['state_sp'][3])
                fit_params.add('strain_eta_1', value=a.ParamDict['sp'][4],
                               min=a.AllDataDict['strain_eta_min'],
                               max=a.AllDataDict['strain_eta_max'],
                               vary=a.ParamDict['state_sp'][4])
                fit_params.add('strain_eta_2', value=a.ParamDict['sp'][5],
                               min=a.AllDataDict['strain_eta_min'],
                               max=a.AllDataDict['strain_eta_max'],
                               vary=a.ParamDict['state_sp'][5])
                fit_params.add('bkg_strain', value=a.ParamDict['sp'][6],
                               min=a.AllDataDict['strain_bkg_min'],
                               max=a.AllDataDict['strain_bkg_max'],
                               vary=a.ParamDict['state_sp'][6])

                fit_params.add('heigt_dw', value=a.ParamDict['dwp'][0],
                               min=a.AllDataDict['dw_height_min'],
                               max=a.AllDataDict['dw_height_max'],
                               vary=a.ParamDict['state_sp'][0])
                fit_params.add('loc_dw', value=a.ParamDict['dwp'][1],
                               min=0.,
                               max=1.,
                               vary=a.ParamDict['state_dwp'][1])
                fit_params.add('fwhm_1_dw', value=a.ParamDict['dwp'][2],
                               min=0.,
                               max=1.,
                               vary=a.ParamDict['state_dwp'][2])
                fit_params.add('fwhm_2_dw', value=a.ParamDict['dwp'][3],
                               min=0.,
                               max=1.,
                               vary=a.ParamDict['state_dwp'][3])
                fit_params.add('dw_eta_1', value=a.ParamDict['dwp'][4],
                               min=a.AllDataDict['dw_eta_min'],
                               max=a.AllDataDict['dw_eta_max'],
                               vary=a.ParamDict['state_dwp'][4])
                fit_params.add('dw_eta_2', value=a.ParamDict['dwp'][5],
                               min=a.AllDataDict['dw_eta_min'],
                               max=a.AllDataDict['dw_eta_max'],
                               vary=a.ParamDict['state_dwp'][5])
                fit_params.add('bkg_dw', value=a.ParamDict['dwp'][6],
                               min=a.AllDataDict['dw_bkg_min'],
                               max=a.AllDataDict['dw_bkg_max'],
                               vary=a.ParamDict['state_dwp'][6])
            else:
                P4Rm.name4lmfit = []
                for ii in range(len(a.ParamDict['sp'])):
                    name = 'sp_' + str(ii)
                    fit_params.add(name, value=a.ParamDict['sp'][ii],
                                   min=a.AllDataDict['strain_min'],
                                   max=a.AllDataDict['strain_max'],
                                   vary=a.ParamDict['state_sp'][ii])
                    P4Rm.name4lmfit.append(name)
                fit_params.add('nb_sp_val', value=len(a.ParamDict['sp']),
                               vary=False)
                for jj in range(len(a.ParamDict['dwp'])):
                    name = 'dwp_' + str(jj)
                    fit_params.add(name, value=a.ParamDict['dwp'][jj],
                                   min=a.AllDataDict['dw_min'],
                                   max=a.AllDataDict['dw_max'],
                                   vary=a.ParamDict['state_dwp'][jj])
                    P4Rm.name4lmfit.append(name)
                fit_params.add('nb_dwp_val', value=len(a.ParamDict['dwp']),
                               vary=False)
            P4Rm.FitDict['fit_params'] = fit_params
            return True

    def on_read_data_from_lmfit(self):
        a = P4Rm()
        from lmfit import fit_report
        result = P4Rm.resultFit
        data = []
        data.append(result.success)
        data.append(result.lmdif_message)
        data.append(result.ier)
        data.append(fit_report(result))
        P4Rm.FitDict['Leastsq_report'] = data
        i = 0
        if a.AllDataDict['model'] == 2:
            for param in result.params.values():
                if i in range(1, 7):
                    P4Rm.ParamDict['sp'][i] = param.value
                if i in range(7, 14):
                    P4Rm.ParamDict['dwp'][i - 7] = param.value
                i += 1
        else:
            len_sp = int(result.params['nb_sp_val'])
            len_dwp = int(result.params['nb_dwp_val'])
            for ii in range(len_dwp):
                name = 'dwp_' + str(ii)
                P4Rm.ParamDict['dwp'][ii] = result.params[name].value
            for jj in range(len_sp):
                name = 'sp_' + str(jj)
                P4Rm.ParamDict['sp'][jj] = result.params[name].value


# =============================================================================
# Thread part
# =============================================================================
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
class Live_NbCycle(wx.PyCommandEvent):
    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        return self._value


# -----------------------------------------------------------------------------
class Fit_launcher(Thread):
    def __init__(self, parent, choice=None):
        Thread.__init__(self)
        self.parent = parent
        self.choice = choice
        self.need_abort = 0
        self.launch = 0
        self.count = 0
        self.gauge_counter = 0
        self.const = 0
        self.pars_value = 0
        self.len_sp = 0
        self.len_dwp = 0
        self.Data4f_Refl = []
        self._stop = Event()
        self.start()
        self.ii = 1

    def init_array(self):
        a = P4Rm()
        const_all = []
        const_all.append(a.AllDataDict['wavelength'])
        const_all.append(a.AllDataDict['damaged_depth'])
        const_all.append(a.AllDataDict['number_slices'])

        const_all.append(a.ConstDict['phi'])
        const_all.append(a.ParamDict['t_l'])
        const_all.append(a.ParamDict['b_S'])
        const_all.append(a.ParamDict['thB_S'])
        const_all.append(a.ParamDict['G'])
        const_all.append(a.ParamDict['F0'])
        const_all.append(a.ParamDict['FH'])
        const_all.append(a.ParamDict['FmH'])

        const_all.append(a.ParamDict['b_S_s'])
        const_all.append(a.ParamDict['thB_S_s'])
        const_all.append(a.ParamDict['G_s'])
        const_all.append(a.ParamDict['F0_s'])
        const_all.append(a.ParamDict['FH_s'])
        const_all.append(a.ParamDict['FmH_s'])
        const_all.append(a.AllDataDict['film_thick'])
        const_all.append(a.AllDataDict['dw_thick'])

        const_all.append(a.ParamDict['th'])
        const_all.append(len(a.ParamDict['z']))

        self.const = const_all
        self.len_sp = len(a.ParamDict['sp'])
        self.len_dwp = len(a.ParamDict['dwp'])

    def on_limit_exceeded(self, val):
        if self.need_abort == 0:
            evt = Liveon_limit_exceeded(S4R.LiveLimitExceeded_COUNT, -1, val)
            wx.PostEvent(self.parent, evt)

    def on_count_cycles(self, val):
        evt = Live_NbCycle(S4R.Live_count_NbCycle, -1, val)
        wx.PostEvent(self.parent, evt)

    def per_iteration(self, pars, iter, resid, *args, **kws):
        a = P4Rm()
        if self.need_abort == 1:
            return True
        if iter < 3 or iter % 10 == 0:
            y_cal = self.residual_lmfit4iteration(pars)
            p = []
            if a.AllDataDict['model'] == 2:
                for j in p4R.asym_pv_list:
                    p.append(pars[j].value)
            else:
                for j in a.name4lmfit:
                    p.append(pars[j].value)
            P4Rm.ParamDict['_fp_min'] = p
            deformation = [p]
            self.f_strain_DW()
            sleep(0.5)
            evt = LiveEvent(S4R.Live_COUNT, -1, y_cal, None, deformation)
            wx.PostEvent(self.parent, evt)
            sleep(0.5)

    def strain_DW(self, pars=None):
        a = P4Rm()
        self.Data4f_Refl = []
        if pars is None:
            strain = f_strain(a.ParamDict['z'],
                              a.ParamDict['_fp_min'][:self.len_sp:],
                              a.AllDataDict['damaged_depth'],
                              a.splinenumber[0])
            DW = f_DW(a.ParamDict['z'],
                      a.ParamDict['_fp_min'][self.len_sp:self.len_sp +
                      self.len_dwp:],
                      a.AllDataDict['damaged_depth'], a.splinenumber[1])
        else:
            if a.AllDataDict['model'] == 0:
                spline_DW = 5
                spline_strain = 5
            elif a.AllDataDict['model'] == 1:
                spline_DW = 6
                spline_strain = 6
            elif a.AllDataDict['model'] == 2:
                spline_DW = 4
                spline_strain = 4
            self.pars4numba(pars)
            strain = f_strain(a.ParamDict['z'], self.pars_value,
                              a.AllDataDict['damaged_depth'], spline_strain)
            DW = f_DW(a.ParamDict['z'], self.pars_value,
                      a.AllDataDict['damaged_depth'], spline_DW)
        strain.astype(np.float64)
        DW.astype(np.float64)
        self.Data4f_Refl.append(strain)
        self.Data4f_Refl.append(DW)
        self.Data4f_Refl.append(self.const)

    def residual_lmfit4iteration(self, pars):
        a = P4Rm()
        res = f_Refl_fit(a.AllDataDict['geometry'], self.Data4f_Refl)
        y_cal = convolve(abs(res) ** 2, a.ParamDict['resol'], mode='same')
        y_cal = y_cal / y_cal.max() + a.AllDataDict['background']
        return y_cal

    def residual_lmfit(self, pars, x, y):
        a = P4Rm()
        self.strain_DW(pars)
        res = f_Refl_fit(a.AllDataDict['geometry'], self.Data4f_Refl)
        y_cal = convolve(abs(res) ** 2, a.ParamDict['resol'], mode='same')
        y_cal = y_cal / y_cal.max() + a.AllDataDict['background']
        return (log10(y) - log10(y_cal))

    def residual_leastsq(self, p, y, x):
        a = P4Rm()
        P4Rm.ParamDict['_fp_min'] = p
        self.strain_DW()
        res = f_Refl_fit(a.AllDataDict['geometry'], self.Data4f_Refl)
        y_cal = convolve(abs(res) ** 2, a.ParamDict['resol'], mode='same')
        y_cal = y_cal / y_cal.max() + a.AllDataDict['background']
        self.count += 1
        if self.count % 50 == 0:
            self.f_strain_DW()
            sleep(0.2)
            deformation = [p]
            evt = LiveEvent(S4R.Live_COUNT, -1, y_cal, None, deformation)
            wx.PostEvent(self.parent, evt)
        if self.need_abort == 1:
            return (log10(y_cal) - log10(y_cal))
        else:
            return (log10(y) - log10(y_cal))

    def residual_square(self, p, E_min, nb_minima):
        a = P4Rm()
        P4Rm.ParamDict['_fp_min'] = p
        self.strain_DW()
        res = f_Refl_fit(a.AllDataDict['geometry'], self.Data4f_Refl)
        y_cal = convolve(abs(res) ** 2, a.ParamDict['resol'], mode='same')
        y_cal = y_cal / y_cal.max() + a.AllDataDict['background']
        y_obs = a.ParamDict['Iobs']
        self.on_pass_data_to_thread(y_cal, p, E_min, nb_minima)
        return ((log10(y_obs) - log10(y_cal)) ** 2).sum() / len(y_cal)

    def pars4numba(self, pars):
        a = P4Rm()
        vals = pars.valuesdict()
        const = []
        if a.AllDataDict['model'] == 2:
            for name in p4R.asym_pv_list:
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

    def on_pass_data_to_thread(self, y_cal, p, E_min, nb_minima):
        self.count += 1
        if self.count == 1:
            self.f_strain_DW()
            sleep(0.5)
            evt = LiveEvent(S4R.Live_COUNT, -1, [])
            wx.PostEvent(self.parent, evt)
            sleep(0.2)
        elif self.count % 10 == 0:
            self.f_strain_DW()
            sleep(0.5)
            data = [E_min, nb_minima]
            deformation = [p]
            evt = LiveEvent(S4R.Live_COUNT, -1, y_cal, data, deformation)
            wx.PostEvent(self.parent, evt)
            sleep(0.2)

    def run(self):
        a = P4Rm()
        P4Rm.par_fit = []
        P4Rm.gsa_loop = 0
        evt = LiveEvent(S4R.Live_COUNT, -1, [])
        wx.PostEvent(self.parent, evt)
        self.init_array()

        if self.choice == 1 or self.choice == 2:
            if a.lmfit_install:
                func = self.residual_lmfit
            else:
                func = self.residual_leastsq
            if self.choice == 1:
                P4Rm.par_fit, P4Rm.success = leastsq(func, a.ParamDict['par'],
                                                     args=(a.ParamDict['Iobs'],
                                                           a.ParamDict['th']))
            elif self.choice == 2:
                from lmfit import minimize
                maxfev_ = int(a.AllDataDict['maxfev']) * (len(a.FitDict['fit_params']) + 1)
                P4Rm.resultFit = minimize(func, a.FitDict['fit_params'],
                                          args=(a.ParamDict['th'],),
                                          iter_cb=self.per_iteration,
                                          scale_covar=True,
                                          kws={'y': a.ParamDict['Iobs']},
                                          maxfev=(maxfev_),
                                          ftol=a.AllDataDict['ftol'],
                                          xtol=a.AllDataDict['xtol'])
        elif self.choice == 0:
            func = self.residual_square
            P4Rm.par_fit = gsa(func, self.on_limit_exceeded,
                               self.on_count_cycles, a.AllDataDict)
        if self.need_abort == 1:
            evt = LiveEvent(S4R.Live_COUNT, -1, [], None, None, 1)
            wx.PostEvent(self.parent, evt)
            self.need_abort = 0
        else:
            evt = LiveEvent(S4R.Live_COUNT, -1, [], None, None, 0)
            wx.PostEvent(self.parent, evt)

    def stop(self):
        self._stop.set()
        P4Rm.gsa_loop = 1
        self.need_abort = 1

    def f_strain_DW(self):
        a = P4Rm()
        P4Rm.ParamDict['sp'] = a.ParamDict['_fp_min'][:int(a.AllDataDict['strain_basis_func'])]
        P4Rm.ParamDict['dwp'] = a.ParamDict['_fp_min'][-1 * int(a.AllDataDict['dw_basis_func']):]

        P4Rm.ParamDict['DW_i'] = f_DW(
            a.ParamDict['z'], a.ParamDict['dwp'],
            a.AllDataDict['damaged_depth'],
            a.AllDataDict['model'])
        P4Rm.ParamDict['strain_i'] = f_strain(
            a.ParamDict['z'], a.ParamDict['sp'],
            a.AllDataDict['damaged_depth'],
            a.AllDataDict['model'])

        t = a.AllDataDict['damaged_depth']
        self.on_shifted_sp_curves(t)
        self.on_shifted_dwp_curves(t)

    def on_shifted_dwp_curves(self, t):
        a = P4Rm()
        if a.AllDataDict['model'] == 0:
            temp_1 = arange(2, len(a.ParamDict['dwp']) + 1)
            temp_2 = temp_1 * t / (len(a.ParamDict['dwp']))
            P4Rm.ParamDict['x_dwp'] = t - temp_2
            shifted_dwp = a.ParamDict['dwp'][:-1:]
            temp_3 = in1d(around(a.ParamDict['depth'], decimals=3),
                          around(a.ParamDict['x_dwp'], decimals=3))
            temp_4 = a.ParamDict['DW_i'][temp_3]
            P4Rm.ParamDict['scale_dw'] = shifted_dwp / temp_4
            P4Rm.ParamDict['scale_dw'][a.ParamDict['scale_dw'] == 0] = 1.

            P4Rm.ParamDict['DW_shifted'] = shifted_dwp / a.ParamDict['scale_dw']
            P4Rm.ParamDict['dw_out'] = a.ParamDict['dwp'][-1]

        elif a.AllDataDict['model'] == 1:
            temp_1 = arange(0, len(a.ParamDict['dwp']) + 1 - 3)
            temp_2 = temp_1 * t / (len(a.ParamDict['dwp']) - 3)
            P4Rm.ParamDict['x_dwp'] = t - temp_2
            shifted_dwp = a.ParamDict['dwp'][1:-1:]
            temp_3 = in1d(around(a.ParamDict['depth'], decimals=3),
                          around(a.ParamDict['x_dwp'], decimals=3))
            temp_4 = a.ParamDict['DW_i'][temp_3]
            P4Rm.ParamDict['scale_dw'] = shifted_dwp / temp_4
            P4Rm.ParamDict['scale_dw'][a.ParamDict['scale_dw'] == 0] = 1.

            P4Rm.ParamDict['DW_shifted'] = shifted_dwp / a.ParamDict['scale_dw']
            temp_5 = array([a.ParamDict['dwp'][0], a.ParamDict['dwp'][-1]])
            P4Rm.ParamDict['dw_out'] = temp_5

        elif a.AllDataDict['model'] == 2:
            x_dw_temp = []
            x_dw_temp.append(t * (1 - a.ParamDict['dwp'][1]))
            x_dw_temp.append(t * (1 - a.ParamDict['dwp'][1] +
                                  a.ParamDict['dwp'][2] / 2))
            x_dw_temp.append(t * (1 - a.ParamDict['dwp'][1] -
                                  a.ParamDict['dwp'][3] / 2))
            x_dw_temp.append(t * 0.05)
            P4Rm.ParamDict['x_dwp'] = x_dw_temp

            y_dw_temp = []
            y_dw_temp.append(a.ParamDict['dwp'][0])
            y_dw_temp.append(1. - (1 - a.ParamDict['dwp'][0]) / 2)
            y_dw_temp.append(1. - (1 - a.ParamDict['dwp'][0]) / 2 -
                             (1 - a.ParamDict['dwp'][6]) / 2)
            y_dw_temp.append(a.ParamDict['dwp'][6])
            P4Rm.ParamDict['DW_shifted'] = y_dw_temp

    def on_shifted_sp_curves(self, t):
        a = P4Rm()
        if a.AllDataDict['model'] == 0:
            temp_1 = arange(2, len(a.ParamDict['sp']) + 1)
            temp_2 = temp_1 * t / (len(a.ParamDict['sp']))
            P4Rm.ParamDict['x_sp'] = t - temp_2
            shifted_sp = a.ParamDict['sp'][:-1:]
            temp_3 = in1d(around(a.ParamDict['depth'], decimals=3),
                          around(a.ParamDict['x_sp'], decimals=3))
            temp_4 = a.ParamDict['strain_i'][temp_3]
            P4Rm.ParamDict['scale_strain'] = shifted_sp / temp_4
            P4Rm.ParamDict['scale_strain'][a.ParamDict['scale_strain'] == 0] = 1.
            P4Rm.ParamDict['strain_shifted'] = asarray(shifted_sp) * 100. / a.ParamDict['scale_strain']
            P4Rm.ParamDict['stain_out'] = a.ParamDict['sp'][-1]

        elif a.AllDataDict['model'] == 1:
            temp_1 = arange(0, len(a.ParamDict['sp']) + 1 - 3)
            temp_2 = temp_1 * t / (len(a.ParamDict['sp']) - 3)
            P4Rm.ParamDict['x_sp'] = t - temp_2
            shifted_sp = a.ParamDict['sp'][1:-1:]
            temp_3 = in1d(around(a.ParamDict['depth'], decimals=3),
                          around(a.ParamDict['x_sp'], decimals=3))
            temp_4 = a.ParamDict['strain_i'][temp_3]
            P4Rm.ParamDict['scale_strain'] = shifted_sp / temp_4
            P4Rm.ParamDict['scale_strain'][a.ParamDict['scale_strain'] == 0] = 1.

            P4Rm.ParamDict['strain_shifted'] = asarray(shifted_sp) * 100. / a.ParamDict['scale_strain']
            temp_5 = array([a.ParamDict['sp'][0], a.ParamDict['sp'][-1]])
            P4Rm.ParamDict['stain_out'] = temp_5

        elif a.AllDataDict['model'] == 2:
            x_sp_temp = []
            x_sp_temp.append(t * (1 - a.ParamDict['sp'][1]))
            x_sp_temp.append(t * (1 - a.ParamDict['sp'][1] +
                                  a.ParamDict['sp'][2] / 2))
            x_sp_temp.append(t * (1 - a.ParamDict['sp'][1] -
                                  a.ParamDict['sp'][3] / 2))
            x_sp_temp.append(t * 0.05)
            P4Rm.ParamDict['x_sp'] = x_sp_temp

            y_sp_temp = []
            y_sp_temp.append(a.ParamDict['sp'][0])
            y_sp_temp.append(a.ParamDict['sp'][0] / 2)
            y_sp_temp.append(a.ParamDict['sp'][0] / 2 + a.ParamDict['sp'][6] / 2)
            y_sp_temp.append(a.ParamDict['sp'][6])
            P4Rm.ParamDict['strain_shifted'] = y_sp_temp
