#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

from numpy import array, append, ones, zeros, exp, log
from scipy.optimize import leastsq
from B_Splines import constantSpline

dwp_pv_initial = [0.5, 0.2, 0.1, 0.1, 0.1, 0.1, 0.85]


def bSpline3(z):
    if z <= 0:
        return 0
    elif z <= 1:
        return (z**3)/6
    elif z <= 2:
        return (2./3) + z * (-2 + z*(2 - z/2))
    elif z <= 3:
        return (-22./3) + z * (10 + z*(-4 + z/2))
    elif z <= 4:
        return (32./3) + z * (-8 + z*(2 - z/6))
    else:
        return 0


def cubicSpline(z, w):
    somme = 0
    index = 0
    for poids in w:
        somme = somme + poids * bSpline3(z-index+3)
        index = index + 1
    return somme


def f_pVoigt(x, pv_p):
    max_ = pv_p[0]
    pos = pv_p[1]
    FWHM = pv_p[2]
    eta = pv_p[3]
    gauss = max_ * exp(-log(2.) * ((x-pos)/(0.5*FWHM))**2)
    lorentz = max_ / (1. + ((x - pos)/(0.5*FWHM))**2)
    return eta*lorentz + (1-eta)*gauss


def f_DW_spline3_smooth(alt, dwp, t):
    w_DW_free = dwp[:]
    w_DW = array([1.0, 1.0, 1.0])
    w_DW = append(w_DW, w_DW_free)
    N_abscisses = len(w_DW) - 3.
    z = alt * N_abscisses / t
    index = 0
    DW = ones(len(z))
    for i in z:
        DW[index] = cubicSpline(i, w_DW)
        index = index + 1
    return DW


def f_DW_spline3_smooth_lmfit(alt, pars, t):
    w_DW_free = pars[-int(pars[1]):]
    w_DW = array([1.0, 1.0, 1.0])
    w_DW = append(w_DW, w_DW_free)
    N_abscisses = len(w_DW) - 3.
    z = alt * N_abscisses / t
    index = 0
    DW = ones(len(z))
    for i in z:
        DW[index] = cubicSpline(i, w_DW)
        index = index + 1
    return DW


def f_DW_spline3_abrupt(alt, dwp, t):
    w_DW = dwp[:]
    N_abscisses = len(w_DW) - 3.
    z = alt * N_abscisses / t
    index = 0
    DW = ones(len(z))
    for i in z:
        DW[index] = cubicSpline(i, w_DW)
        index = index + 1
    return DW


def f_DW_histogram(alt, dwp, t):
    w_DW = dwp[:]
    N_abscisses = len(w_DW)
    z = alt * N_abscisses / t
    index = 0
    DW = ones(len(z))
    for i in z:
        DW[index] = constantSpline(i, w_DW)
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
    DW[(alt <= loc)] = (1. -
                        f_pVoigt(alt[alt <= loc], [height, loc, fwhm1, eta1]))
    DW[(alt > loc)] = (1. -
                       (f_pVoigt(alt[alt > loc],
                                 [height-bkg, loc, fwhm2, eta2]) + bkg))
    return DW


def f_DW_pv_lmfit(alt, pars, t):
    height = 1 - pars[7]
    loc = pars[8] * t
    fwhm1 = pars[9] * t
    fwhm2 = pars[10] * t
    eta1 = pars[11]
    eta2 = pars[12]
    bkg = 1 - pars[13]

    DW = zeros(len(alt))
    DW[(alt <= loc)] = (1. -
                        f_pVoigt(alt[alt <= loc], [height, loc, fwhm1, eta1]))
    DW[(alt > loc)] = (1. -
                       (f_pVoigt(alt[alt > loc],
                                 [height-bkg, loc, fwhm2, eta2]) + bkg))
    return DW


def f_DW(alt, dwp, t, choice):
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
    def errfunc(dwp, x, y, choice): return f_DW(x, dwp, t, choice) - y

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
