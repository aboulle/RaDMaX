#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A_BOULLE & M_SOUILAH

from numpy import array, append, ones
from scipy.optimize import leastsq
from B_Splines import cubicSpline, constantSpline

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

	
def f_strain(alt, sp, t, choice):
    if choice == 0:
        strain = f_strain_spline3_smooth(alt, sp, t)
    elif choice == 1:
        strain = f_strain_spline3_abrupt(alt, sp, t)
    elif choice == 2:
        strain = f_strain_histogram(alt, sp, t)
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
    height = t - depth
    
    sp = ones(size)
    sp_fit, success = leastsq(errfunc, sp, args=(height, strain, choice))
    
    return sp_fit
    
