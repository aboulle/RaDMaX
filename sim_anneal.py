#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A_BOULLE & M_SOUILAH

import scipy.stats as stats
from scipy import rand
from pylab import normal

from Parameters4Radmax import *
from def_XRD import f_Refl
from numpy import append, ones, zeros, linspace, log10

#------------------------------------------------------------------------------
class SimAnneal(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.Fit()

    def temp_sch_stepped(self, cycle, Tmax, qv, nb_palier):
    	nb_cycle_max = len(cycle)
    	palier = nb_cycle_max / nb_palier
    	T = ones(len(cycle))*Tmax
    ##	last_success = 0
    	for iteration in cycle:
    		index = iteration - 1.
    		if ((index)%palier == 0.):
    			last_success = iteration-1
    			T[index] = Tmax*((2**(qv-1.))-1.) / (((1.+iteration)**(qv-1.)) - 1.)
    		else :
    			T[index] = T[last_success]
    	return T
    	
    def temp_sch(self, cycle, Tmax, qv):
    	T = ones(len(cycle))*Tmax
    	for iteration in cycle:
    		index = iteration - 1.
    		T[index] = Tmax*((2**(qv-1.))-1.) / (((1.+iteration)**(qv-1.)) - 1.)
    	return T
    
    def accept_prob(self, Delta_E, T, qa):
    	if (qa <= 1):
    		if ( (1. + ((qa-1.)*Delta_E/T)) <= 0.):
    			return 0.
    		elif (Delta_E < 0):
    			return 1
    		else:
    			return ((1. + ((qa-1.)*Delta_E/T) )**(1./(1.-qa)))
    	else :
    		if (Delta_E < 0):
    			return 1
    		else:
    			return ((1. + ((qa-1.)*Delta_E/T) )**(1./(1.-qa)))
    
    
    def tsallis_rv(self, qv, Tqv, D):
    	p = (3.-qv)/(2*(qv-1))
    	s = ((2.*(qv-1))**0.5) / (Tqv**(1./(3-qv)))
    	rv = zeros(D, dtype = float)
    	x = normal(0,1,D)
    	u = stats.gamma.rvs(p, loc = 0., scale = 1., size = 1)
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
    	sum = 0
    	depassements = zeros(D, dtype = float)
    	fp_t = fp_0[:]
    	while (sum != len(fp_0)):
    ##		delta_fp = divide(self.tsallis_rv(qv, T, D), scale)
    		for ii in range(len(fp_t)):
    			sum2 = 0
    			while (sum2 != 1):
    				delta_fp = self.tsallis_rv(qv, T, 1)[0] * scale[ii]
    				fp_t[ii] = (fp_0[ii] + delta_fp)
    				if (fp_t[ii]>=limits[2*ii]) and (fp_t[ii]<=limits[2*ii+1]):
    					sum +=1
    					sum2 = 1
    				else:
    					depassements[ii] = 1
    					print('DEPASSEMENT SUR LE PARAMETRE', ii, fp_t[ii], scale[ii])
    					fp_t[ii] = fp_0[ii]
    ##					pause = raw_input()
    	print(delta_fp)
    	return fp_t, depassements
    
    def randomize(self, LimitExceeded, qv, T, D, fp_0, scale, limits): 
        depassements = zeros(D, dtype = float)
        fp_t = zeros(len(fp_0))
        fp_t[:] = fp_0[:]
        for ii in range(len(fp_t)):
            delta_fp = self.tsallis_rv(qv, T, 1)[0] * scale[ii]
            fp_t[ii] = (fp_0[ii] + delta_fp)
            LimitExceeded(-1)
            while ((fp_t[ii]<limits[2*ii]) or (fp_t[ii]>limits[2*ii+1])):
    #            print('************ LIMIT EXCEEDED ON PARAMETER', ii, '************')
                LimitExceeded(ii)
                depassements[ii] = 1
                fp_t[ii] = fp_0[ii]
                delta_fp = self.tsallis_rv(qv, T, 1)[0] * scale[ii]
                fp_t[ii] = (fp_0[ii] + delta_fp)
        return fp_t, depassements
       
    
    def residual_square(self, p, data):
        a = P4Diff()
        P4Diff._fp_min = p
        y_cal = f_Refl(data)
        y_cal = y_cal/y_cal.max() + data['background']
        return ((log10(a.Iobs) - log10(y_cal))**2).sum() / len(y_cal)
    
    def gsa(self, energy, LimitExceeded, data, args = ()):
        a = P4Diff()
        par_scale = ones(len(a.par))*a.jump_scale
        sp_limits = zeros(2*len(a.sp))
        sp_limits[0:(2*len(a.sp))-1:2] = data['min_strain']
        sp_limits[1:(2*len(a.sp)):2] = data['max_strain']
        dwp_limits = zeros(2*len(a.dwp))
        dwp_limits[0:(2*len(a.dwp))-1:2] = data['min_dw']
        dwp_limits[1:(2*len(a.dwp)):2] = data['max_dw']
        par_limits = append(sp_limits, dwp_limits)
        fp = a.par
    
        if type(args) != type(()): args = (args,)
    ## initialisation des parametres min et 0
        P4Diff._fp_min = fp
        fp_0 = zeros(len(fp))
        fp_min = zeros(len(fp))
        fp_t = zeros(len(fp))
        fp_0[:] = fp[:]
        fp_min[:] = fp[:]
        fp_t[:] = fp[:]
        E_0 = self.residual_square(fp, data)
        E_min = E_0
        E_t = E_0
        cycle_min = 1.
        nb_rejet = 0
        nb_minima = 0
        tmax = data['tmax']/1000
    ## nombre de paramètres
        D = len(fp)
        depassements = zeros(D, dtype = float)
    ## définition du tableau de cycle
        cycle = linspace(1, data['nb_cycle_max'], data['nb_cycle_max'])
    #    evolution_E = zeros(nb_cycle_max, dtype = float)
    #    evolution_Jump = zeros(nb_cycle_max)
    #    evolution_Param = zeros((nb_cycle_max, D), dtype = float)
    #    evolution_Depass = zeros((nb_cycle_max, D), dtype = float)
    ## définition du tableau de refroidissement
    ##	temperature = temp_sch(cycle, Tmax, qt)
        temperature = self.temp_sch_stepped(cycle, tmax, data['qt'], data['nb_palier'])
        val4gauge = int(cycle[-1])/20
        if int(cycle[-1]) <= 100:
            val4gaugetemp = int(cycle[-1])/5
            P4Diff.gaugeUpdate = 100/5
        elif  100 < int(cycle[-1]) <= 1000:
            val4gaugetemp = int(cycle[-1])/20
            P4Diff.gaugeUpdate = 100/20
        elif  1000 < int(cycle[-1]) <= 10000:
            val4gaugetemp = int(cycle[-1])/100
            P4Diff.gaugeUpdate = 100/100
        if type(val4gaugetemp) != int:
            val4gauge = ceil(val4gaugetemp)
        else:
            val4gauge = val4gaugetemp
                        
    ## début de la boucle de recuit
        for iteration in cycle:
            if a.gsa_loop == 1:
    #            pub.sendMessage(pubsub_Update_Gauge, val=0, emin=E_min, param=int(nb_minima))
                break
            elif a.gsa_loop == 0:
                index = iteration - 1
        ## lecture de la tempétature
                T = temperature[index]
        ## randomisation des paramètres
                fp_t, depassements = self.randomize(LimitExceeded, data['qv'], T, D, fp_0, par_scale, par_limits)
        ## calcul de l'énergie du nouvel état
                E_t = energy(fp_t, E_min, nb_minima, val4gauge)
        #        evolution_E[index] = E_0
        #        evolution_Param[index,:] = fp_0[:]
        #        evolution_Depass[index, :] = multiply(depassements[:],fp_0[:])
        ## test : si l'energie a baissé, garde les nouveaux paramètres et défini une nouvelle énergie de référence
                if (E_t <= E_0):
        #            print iteration, '(',nb_minima, 'minimum )', 'E0 = %4.3f' %E_0 , 'Emin = %4.3f' %E_min, 'T = %4.3f' %T, "DOWN"
    #                print(iteration, 'Emin = %4.3f' %E_min, '(',int(nb_minima), ')')
                    nb_rejet = 0
                    fp_0 = fp_t[:]
                    E_0 = E_t
        #            evolution_Jump[index] = -1
        #            evolution_E[index] = E_0
        #            evolution_Param[index,:] = fp_0[:]
        			## de plus, si cette energie est la plus faible rencontrée, défini de nouveau minima
                    if (E_t <= E_min):
                        nb_minima += 1.
                        fp_min = fp_t[:]
                        E_min = E_t
                        cycle_min = iteration
                else:
        ## sinon, si l'énergie a augementée, accepte le changemet que si random < Prob
                    Delta_E = E_t - E_0
                    data['qa'] = data['qa'] - 0.85*iteration
                    Pqa = self.accept_prob(Delta_E, T, data['qa'])
                    alea = rand()
                    if (alea < Pqa):
                        nb_rejet = 0
        #                print iteration, '(',nb_minima, 'minimum )', 'E0 = %4.3f' %E_0, 'Emin = %4.3f' %E_min, 'T = %4.3f' %T, "UP"
    #                    print(iteration, 'Emin = %4.3f' %E_min, '(',int(nb_minima), ')')                
                        fp_0 = fp_t[:]
                        E_0 = E_t
        #                evolution_Jump[index] = 1
        #                evolution_Param[index,:] = fp_0[:]
                    else:
                        nb_rejet +=1
        #                print iteration, '(',nb_minima, 'minimum )', 'E0 = %4.3f' %E_0, 'Emin = %4.3f' %E_min, 'T = %4.3f' %T, "REJECTED"
    #            if iteration == 1:
    #                print(iteration, 'Emin = %4.3f' %E_min, '(',int(nb_minima), ')')
    #                pub.sendMessage(pubsub_Update_Gauge, val=0, emin=E_min, param=int(nb_minima))
    #            if iteration % val4gauge == 0:
    ##                print(iteration, 'Emin = %4.3f' %E_min, '(',int(nb_minima), ')')
    #                gauge_counter += 5
    #                pub.sendMessage(pubsub_Update_Gauge, val=gauge_counter, emin=E_min, param=int(nb_minima))
        #    export = column_stack((cycle,evolution_E, temperature, evolution_Jump))
        #    export_param = column_stack((cycle, evolution_Param))
        #    export_depass = column_stack((cycle, evolution_Depass))
        #    savetxt("gsa_output.txt", export, fmt = '%10.8f')
        #    savetxt("gsa_param_output.txt", export_param, fmt = '%10.8f')
        #    savetxt("gsa_depass_output.txt", export_depass, fmt = '%10.8f')
        #    print 'Energie initiale =',  evolution_E[0]
        #    print 'Energie minimale =',  E_min, 'atteinte en', cycle_min, 'cycles'
        #    print 'paramètres', fp_min
        #    print 'dépassements totaux', depassements
        return fp_min
    
    
