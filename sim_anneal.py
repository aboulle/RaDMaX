#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

import scipy.stats as stats
from scipy import rand
from pylab import normal

from Parameters4Radmax import *
from def_XRD import f_ReflDict
from numpy import append, ones, zeros, linspace, log10


# ------------------------------------------------------------------------------
class SimAnneal(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.Fit()

    def temp_sch_stepped(self, cycle, Tmax, qv, nb_palier):
        nb_cycle_max = len(cycle)
        palier = nb_cycle_max / nb_palier
        T = ones(len(cycle))*Tmax

        for iteration in cycle:
            index = iteration - 1
            if ((index) % palier == 0.):
                last_success = iteration-1
                T[index] = (Tmax*((2**(qv-1.))-1.) /
                            (((1.+iteration)**(qv-1.)) - 1.))
            else:
                T[index] = T[last_success]
        return T

    def temp_sch(self, cycle, Tmax, qv):
        T = ones(len(cycle))*Tmax
        for iteration in cycle:
            index = iteration - 1
            T[index] = (Tmax*((2**(qv-1.))-1.) /
                        (((1.+iteration)**(qv-1.)) - 1.))
        return T

    def accept_prob(self, Delta_E, T, qa):
        if (qa <= 1):
            if ((1. + ((qa-1.)*Delta_E/T)) <= 0.):
                return 0.
            elif (Delta_E < 0):
                return 1
            else:
                return ((1. + ((qa-1.)*Delta_E/T))**(1./(1.-qa)))
        else:
            if (Delta_E < 0):
                return 1
            else:
                return ((1. + ((qa-1.)*Delta_E/T))**(1./(1.-qa)))

    def tsallis_rv(self, qv, Tqv, D):
        p = (3.-qv)/(2*(qv-1))
        s = ((2.*(qv-1))**0.5) / (Tqv**(1./(3-qv)))
        rv = zeros(D, dtype=float)
        x = normal(0, 1, D)
        u = stats.gamma.rvs(p, loc=0., scale=1., size=1)
        y = s*(u**0.5)
        rv[:] = x[:]/y
        return rv

    def tronque(self, fp_t, limits):
        for ii in range(len(fp_t)):
            if (fp_t[ii] <= limits[2*ii]):
                fp_t[ii] = limits[2*ii]
            if (fp_t[ii] >= limits[(2*ii)+1]):
                fp_t[ii] = limits[(2*ii)+1]
        return fp_t

    def randomize_old_FONCTIONNE(self, qv, T, D, fp_0, scale, limits):
        sum1 = 0
        depassements = zeros(D, dtype=float)
        fp_t = fp_0[:]
        while (sum1 != len(fp_0)):
            for ii in range(len(fp_t)):
                sum2 = 0
                while (sum2 != 1):
                    delta_fp = self.tsallis_rv(qv, T, 1)[0] * scale[ii]
                    fp_t[ii] = (fp_0[ii] + delta_fp)
                    if (fp_t[ii] >= limits[2*ii] and
                       fp_t[ii] <= limits[2*ii+1]):
                        sum1 += 1
                        sum2 = 1
                    else:
                        depassements[ii] = 1
                        print('DEPASSEMENT SUR LE PARAMETRE', ii, fp_t[ii],
                              scale[ii])
                        fp_t[ii] = fp_0[ii]
        print(delta_fp)
        return fp_t, depassements

    def randomize(self, LimitExceeded, qv, T, D, fp_0, scale, limits):
        depassements = zeros(D, dtype=float)
        fp_t = zeros(len(fp_0))
        fp_t[:] = fp_0[:]
        for ii in range(len(fp_t)):
            delta_fp = self.tsallis_rv(qv, T, 1)[0] * scale[ii]
            fp_t[ii] = (fp_0[ii] + delta_fp)
            LimitExceeded(-1)
            while ((fp_t[ii] < limits[2*ii]) or (fp_t[ii] > limits[2*ii+1])):
                LimitExceeded(ii)
                depassements[ii] = 1
                fp_t[ii] = fp_0[ii]
                delta_fp = self.tsallis_rv(qv, T, 1)[0] * scale[ii]
                fp_t[ii] = (fp_0[ii] + delta_fp)
        return fp_t, depassements

    def residual_square(self, p, data):
        a = P4Radmax()
        P4Radmax.ParamDict['_fp_min'] = p
        y_cal = f_ReflDict(data)
        y_cal = y_cal/y_cal.max() + data['background']
        temp = ((log10(a.ParamDict['Iobs']) - log10(y_cal))**2).sum()
        return temp / len(y_cal)

    def gsa(self, energy, LimitExceeded, data, args=()):
        a = P4Radmax()
        par_scale = ones(len(a.ParamDict['par']))*a.ConstDict['jump_scale']
        sp_limits = zeros(2*len(a.ParamDict['sp']))
        dwp_limits = zeros(2*len(a.ParamDict['dwp']))

        if a.DataDict['model'] == 0. or a.DataDict['model'] == 1.:        
            sp_limits[0:(2*len(a.ParamDict['sp']))-1:2] = a.DefaultDict['strain_min']
            sp_limits[1:(2*len(a.ParamDict['sp'])):2] = a.DefaultDict['strain_max']
    
            dwp_limits[0:(2*len(a.ParamDict['dwp']))-1:2] = a.DefaultDict['dw_min']
            dwp_limits[1:(2*len(a.ParamDict['dwp'])):2] = a.DefaultDict['dw_max']
        elif a.DataDict['model'] == 2.:
            sp_limits[0] = a.DefaultDict['strain_height_min']
            sp_limits[1] = a.DefaultDict['strain_height_max']
            sp_limits[2] = 0.
            sp_limits[3] = 1.
            sp_limits[4] = 0.
            sp_limits[5] = 1.
            sp_limits[6] = 0.
            sp_limits[7] = 1.
            sp_limits[8] = a.DefaultDict['strain_eta_min']
            sp_limits[9] = a.DefaultDict['strain_eta_max']
            sp_limits[10] = a.DefaultDict['strain_eta_min']
            sp_limits[11] = a.DefaultDict['strain_eta_max']
            sp_limits[12] = a.DefaultDict['strain_bkg_min']
            sp_limits[13] = a.DefaultDict['strain_bkg_max']

            dwp_limits[0] = a.DefaultDict['dw_height_min']
            dwp_limits[1] = a.DefaultDict['dw_height_max']
            dwp_limits[2] = 0.
            dwp_limits[3] = 1.
            dwp_limits[4] = 0.
            dwp_limits[5] = 1.
            dwp_limits[6] = 0.
            dwp_limits[7] = 1.
            dwp_limits[8] = a.DefaultDict['dw_eta_min']
            dwp_limits[9] = a.DefaultDict['dw_eta_max']
            dwp_limits[10] = a.DefaultDict['dw_eta_min']
            dwp_limits[11] = a.DefaultDict['dw_eta_max']
            dwp_limits[12] = a.DefaultDict['dw_bkg_min']
            dwp_limits[13] = a.DefaultDict['dw_bkg_max']
        par_limits = append(sp_limits, dwp_limits)
        fp = a.ParamDict['par']
        qa_var = a.DefaultDict['qa']

        if type(args) != type(()):
            args = (args,)

        P4Radmax.ParamDict['_fp_min'] = fp
        fp_0 = zeros(len(fp))
        fp_min = zeros(len(fp))
        fp_t = zeros(len(fp))
        fp_0[:] = fp[:]
        fp_min[:] = fp[:]
        fp_t[:] = fp[:]
        E_0 = self.residual_square(fp, data)
        E_min = E_0
        E_t = E_0
        nb_rejet = 0
        nb_minima = 0
        tmax = data['tmax']/1000
#        nombre de paramètres
        D = len(fp)
        depassements = zeros(D, dtype=float)
#        définition du tableau de cycle
        cycle = linspace(1, data['nb_cycle_max'], data['nb_cycle_max'])
        cycle = [int(ii) for ii in cycle]
        cycle = np.asarray(cycle, dtype=np.int32)
    #    evolution_E = zeros(nb_cycle_max, dtype = float)
    #    evolution_Jump = zeros(nb_cycle_max)
    #    evolution_Param = zeros((nb_cycle_max, D), dtype = float)
    #    evolution_Depass = zeros((nb_cycle_max, D), dtype = float)
    #    définition du tableau de refroidissement
    #    temperature = temp_sch(cycle, Tmax, qt)
        temperature = self.temp_sch_stepped(cycle, tmax, a.DefaultDict['qt'],
                                            data['nb_palier'])
        val4gauge = int(cycle[-1])/20
        if int(cycle[-1]) <= 100:
            val4gaugetemp = int(cycle[-1])/5
            P4Radmax.gaugeUpdate = 100/5
        elif 100 < int(cycle[-1]) <= 1000:
            val4gaugetemp = int(cycle[-1])/40
            P4Radmax.gaugeUpdate = 100/40
        elif 1000 < int(cycle[-1]) <= 10000:
            val4gaugetemp = int(cycle[-1])/100
            P4Radmax.gaugeUpdate = 100/100
        if type(val4gaugetemp) != int:
            val4gauge = ceil(val4gaugetemp)
        else:
            val4gauge = val4gaugetemp
    #   début de la boucle de recuit
        for iteration in cycle:
            if a.gsa_loop == 1:
                break
            elif a.gsa_loop == 0:
                index = iteration - 1
#            lecture de la tempétature
                T = temperature[index]
#        randomisation des paramètres
                fp_t, depassements = self.randomize(LimitExceeded,
                                                    a.DefaultDict['qv'],
                                                    T, D, fp_0, par_scale,
                                                    par_limits)
#        calcul de l'énergie du nouvel état
#                print ("loop= ", iteration)
                E_t = energy(fp_t, E_min, nb_minima, val4gauge)
        #        evolution_E[index] = E_0
        #        evolution_Param[index,:] = fp_0[:]
        #        evolution_Depass[index, :] = multiply(depassements[:],fp_0[:])
#        test : si l'energie a baissé, garde les nouveaux paramètres et défini
#        une nouvelle énergie de référence
                if (E_t <= E_0):
                    nb_rejet = 0
                    fp_0 = fp_t[:]
                    E_0 = E_t
        #            evolution_Jump[index] = -1
        #            evolution_E[index] = E_0
        #            evolution_Param[index,:] = fp_0[:]
                    if (E_t <= E_min):
                        nb_minima += 1.
                        fp_min = fp_t[:]
                        E_min = E_t
                else:
                    Delta_E = E_t - E_0
                    qa_var = qa_var - 0.85*iteration
                    Pqa = self.accept_prob(Delta_E, T, qa_var)
                    alea = rand()
                    if (alea < Pqa):
                        nb_rejet = 0
                        fp_0 = fp_t[:]
                        E_0 = E_t
        #                evolution_Jump[index] = 1
        #                evolution_Param[index,:] = fp_0[:]
                    else:
                        nb_rejet += 1
        return fp_min
