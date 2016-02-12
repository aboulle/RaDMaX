#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

from numpy import array, append, ones, zeros
from scipy.optimize import leastsq
from B_Splines import cubicSpline, constantSpline
from tools import f_pVoigt

dwp_pv_initial = [0.5, 0.2, 0.1, 0.1, 0.1, 0.1, 0.85]

# Debye-Waller Spline à N abscisses
def f_DW_spline3_smooth(alt, dwp,t):
	w_DW_free = dwp[:]
	w_DW = array([1.0,1.0,1.0])
	w_DW = append(w_DW,w_DW_free)
	N_abscisses = len(w_DW) - 3.
	z = alt * N_abscisses / t
	index = 0
	DW = ones(len(z))
	for i in z:
		DW[index] = cubicSpline(i,w_DW)
		index = index + 1
	return DW

def f_DW_spline3_smooth_lmfit(alt, pars, t):
    vals = pars.valuesdict()
    len_dwp = int(vals['nb_dwp_val'])
    dwp = []
    for ii in range(len_dwp):
        name = 'dwp_' + str(ii)
        dwp.append(vals[name])
    w_DW_free = dwp[:]
    w_DW = array([1.0,1.0,1.0])
    w_DW = append(w_DW,w_DW_free)
    N_abscisses = len(w_DW) - 3.
    z = alt * N_abscisses / t
    index = 0
    DW = ones(len(z))
    for i in z:
        DW[index] = cubicSpline(i,w_DW)
        index = index + 1
    return DW

def f_DW_spline3_abrupt(alt, dwp,t):
	w_DW = dwp[:]
	N_abscisses = len(w_DW) - 3.
	z = alt * N_abscisses / t
	index = 0
	DW = ones(len(z))
	for i in z:
		DW[index] = cubicSpline(i,w_DW)
		index = index + 1
	return DW	

def f_DW_histogram(alt, dwp,t):
	w_DW = dwp[:]
	N_abscisses = len(w_DW)
	z = alt * N_abscisses / t
	index = 0
	DW = ones(len(z))
	for i in z:
		DW[index] = constantSpline(i,w_DW)
		index = index + 1
	return DW	

def f_DW_pv(alt, pv_p, t):
    height = 1 - pv_p[0]
    loc = pv_p[1] * t
    fwhm1 = pv_p[2] * t
    fwhm2 = pv_p[3] * t
    eta1 = pv_p[4]
    eta2 = pv_p[5]
    bkg = 1 - pv_p[6]
    DW = zeros(len(alt))
    DW[(alt<=loc)] = 1. - f_pVoigt(alt[alt<=loc], [height, loc, fwhm1, eta1])
    DW[(alt>loc)] = 1. - ( f_pVoigt(alt[alt>loc], [height-bkg, loc, fwhm2, eta2]) + bkg)
    return DW

def f_DW_pv_lmfit(alt, pars, t):
    vals = pars.valuesdict()
    height = 1- vals['heigt_dw']
    loc = vals['loc_dw'] * t
    fwhm1 = vals['fwhm_1_dw'] * t
    fwhm2 = vals['fwhm_2_dw'] * t
    eta1 = vals['eta_1_dw']
    eta2 = vals['eta_2_dw']
    bkg = 1 - vals['bkg_dw']

    DW = zeros(len(alt))
    DW[(alt<=loc)] = 1. - f_pVoigt(alt[alt<=loc], [height, loc, fwhm1, eta1])
    DW[(alt>loc)] = 1. - ( f_pVoigt(alt[alt>loc], [height-bkg, loc, fwhm2, eta2]) + bkg)
    return DW

def f_DW(alt, dwp, t, choice): #DANS MENU DÉROULANT
    if choice == 0:
        DW = f_DW_spline3_smooth(alt, dwp, t)
#        DW = f_DW_spline3_smooth(alt, abs(dwp), t)
    elif choice == 1:
        DW = f_DW_spline3_abrupt(alt, dwp, t)
    elif choice == 2:
        DW = f_DW_pv(alt, dwp, t)
    elif choice == 3:
        DW = f_DW_histogram(alt, dwp, t)
    elif choice == 4:
        DW = f_DW_pv_lmfit(alt, dwp, t)
    elif choice == 5:
        DW = f_DW_spline3_smooth_lmfit(alt, dwp, t)
    return DW
 
def old2new_DW(alt, dwp, t, new_size, choice):
     dwp_guess = ones(new_size)
     dw_old = f_DW(alt, dwp, t, choice)
     def errfunc(dwp, alt, dw, t): return f_DW(alt, dwp, t, choice) - dw_old
     dwp_new, success = leastsq(errfunc, dwp_guess, args=(alt, dw_old, t))
     return dwp_new

def fit_input_DW(data, size, t, choice):
    def errfunc(dwp, x, y, choice):
	return f_DW(x, dwp, t, choice) - y
     
    depth = data[0]
    DW = data[1]

    if choice == 2:
        dwp = dwp_pv_initial
        t = depth.max()
    else:
        dwp = ones(size)

    height = t - depth
    
    dwp_fit, success = leastsq(errfunc, dwp, args=(height, DW, choice))

    return dwp_fit