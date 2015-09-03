#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A_BOULLE & M_SOUILAH

from numpy import array, append, ones
from scipy.optimize import leastsq
from B_Splines import cubicSpline, constantSpline

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

def f_DW(alt, dwp, t, choice): #DANS MENU DÉROULANT
    if choice == 0:
        DW = f_DW_spline3_smooth(alt, abs(dwp), t)
    elif choice == 1:
        DW = f_DW_spline3_abrupt(alt, dwp, t)
    elif choice == 2:
        DW = f_DW_histogram(alt, dwp, t)
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
    height = t - depth
    
    dwp = ones(size)
    dwp_fit, success = leastsq(errfunc, dwp, args=(height, DW, choice))

    return dwp_fit