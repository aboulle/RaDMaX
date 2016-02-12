#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

from numpy import array, append, ones, zeros
from scipy.optimize import leastsq
from B_Splines import cubicSpline, constantSpline
from tools import f_pVoigt

sp_pv_initial = [2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.05]

## Calcul de la déformation (Spline à N abscisses)
def f_strain_spline3_smooth(alt, sp,t):
    w_strain_free = sp[:]
    w_strain = array([0.0,0.0,0.0])
    w_strain = append(w_strain,w_strain_free)
    N_abscisses = len(w_strain) - 3.
    z = alt * N_abscisses / t
    index = 0
    strain = ones(len(z))
    for i in z:
        strain[index] = cubicSpline(i,w_strain) / 100. ## LES POIDS SONT EN %
        index = index + 1
    return strain

def f_strain_spline3_smooth_lmfit(alt, pars, t):
    vals = pars.valuesdict()
    len_sp = int(vals['nb_sp_val'])
    sp = []
    for ii in range(len_sp):
        name = 'sp_' + str(ii)
        sp.append(vals[name])
    w_strain_free = sp[:]
    w_strain = array([0.0,0.0,0.0])
    w_strain = append(w_strain,w_strain_free)
    N_abscisses = len(w_strain) - 3.
    z = alt * N_abscisses / t
    index = 0
    strain = ones(len(z))
    for i in z:
        strain[index] = cubicSpline(i,w_strain) / 100. ## LES POIDS SONT EN %
        index = index + 1
    return strain

def f_strain_spline3_abrupt(alt, sp,t):
    w_strain = sp[:]
    N_abscisses = len(w_strain) - 3.
    z = alt * N_abscisses / t
    index = 0
    strain = ones(len(z))
    for i in z:
        strain[index] = cubicSpline(i,w_strain) / 100. ## LES POIDS SONT EN %
        index = index + 1
    return strain

def f_strain_histogram(alt, sp,t):
    w_strain = sp[:]
    N_abscisses = len(w_strain)
    z = alt * N_abscisses / t
    index = 0
    strain = ones(len(z))
    for i in z:
        strain[index] = constantSpline(i,w_strain) / 100. ## LES POIDS SONT EN %
        index = index + 1
    return strain

def f_strain_pv(alt, pv_p, t):
    height = pv_p[0]
    loc = pv_p[1] * t
    fwhm1 = pv_p[2] * t
    fwhm2 = pv_p[3] * t
    eta1 = pv_p[4]
    eta2 = pv_p[5]
    bkg = pv_p[6]
    strain = zeros(len(alt))
    strain[(alt<=loc)] =  f_pVoigt(alt[alt<=loc], [height, loc, fwhm1, eta1]) / 100
    strain[(alt>loc)] = ( f_pVoigt(alt[alt>loc], [height-bkg, loc, fwhm2, eta2]) + bkg) / 100
    return strain

def f_strain_pv_lmfit(alt, pars, t):
    vals = pars.valuesdict()
    height = vals['heigt_strain']
    loc = vals['loc_strain'] * t
    fwhm1 = vals['fwhm_1_strain'] * t
    fwhm2 = vals['fwhm_2_strain'] * t
    eta1 = vals['eta_1_strain']
    eta2 = vals['eta_2_strain']
    bkg = vals['bkg_strain']
    strain = zeros(len(alt))
    strain[(alt<=loc)] =  f_pVoigt(alt[alt<=loc], [height, loc, fwhm1, eta1]) / 100
    strain[(alt>loc)] = ( f_pVoigt(alt[alt>loc], [height-bkg, loc, fwhm2, eta2]) + bkg) / 100
    return strain
	
def f_strain(alt, sp, t, choice):
    if choice == 0:
        strain = f_strain_spline3_smooth(alt, sp, t)
    elif choice == 1:
        strain = f_strain_spline3_abrupt(alt, sp, t)
    elif choice == 2:
        strain = f_strain_pv(alt, sp, t)
    elif choice == 3:
        strain = f_strain_histogram(alt, sp, t)
    elif choice == 4:
        strain = f_strain_pv_lmfit(alt, sp, t)
    elif choice == 5:
        strain = f_strain_spline3_smooth_lmfit(alt, sp, t)
    return strain
 
def old2new_strain(alt, sp, t, new_size, choice):
     sp_guess = ones(new_size)
     strain_old = f_strain(alt, sp, t, choice)
     def errfunc(sp, alt, strain, t): return f_strain(alt, sp, t, choice) - strain_old
     sp_new, success = leastsq(errfunc, sp_guess, args=(alt, strain_old, t))
     return sp_new   

def fit_input_strain(data, size, t, choice):
    def errfunc(sp, x, y, choice):
	return f_strain(x, sp, t, choice) - y

    depth = data[0]
    strain = data[1]

    if choice == 2:
        sp = sp_pv_initial
        t = depth.max()
    else:
        sp = ones(size)

    height = t - depth

    sp_fit, success = leastsq(errfunc, sp, args=(height, strain, choice))
    
    return sp_fit
    
