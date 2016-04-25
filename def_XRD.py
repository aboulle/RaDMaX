#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

from def_strain import f_strain
from def_DW import f_DW
from Parameters4Radmax import P4Radmax
from scipy import tan, exp, sin, pi, convolve, sqrt
from tools import signe

'''
Calcul de la réflectivité dynamique
'''


def f_Refl(strain, DW, FH, FmH, F0, th, const_all, z, number_slices):
    wl = const_all[0]
    phi = const_all[2]
    b_S = const_all[3]
    G = const_all[4]
    thB_S = const_all[5]
    t_l = const_all[6]
    N = number_slices

    thB = thB_S - strain * tan(thB_S)  # angle de Bragg dans chaque lamelle
    eta = ((-b_S*(th-thB_S)*sin(2*thB_S) - 0.5*G*F0[0]*(1-b_S)) /
           ((abs(b_S)**0.5) * G * (FH[0]*FmH[0])**0.5))
    res = (eta - signe(eta.real)*((eta*eta - 1)**0.5)) * (FH[0] / FmH[0])**0.5

    n = 1
    while (n <= N):
        g0 = sin(thB[n] - phi)  # gamma 0
        gH = -sin(thB[n] + phi)  # gamma H
        b = g0 / gH
        T = (pi * G * ((FH[n] * FmH[n])**0.5) * t_l * DW[n] /
             (wl * (abs(g0 * gH)**0.5)))
        eta = ((-b*(th-thB[n])*sin(2*thB_S) - 0.5*G*F0[n]*(1-b)) /
               ((abs(b)**0.5) * G * DW[n] * (FH[n]*FmH[n])**0.5))
        S1 = (res - eta + sqrt(eta*eta-1))*exp(-1j*T*sqrt(eta*eta-1))
        S2 = (res - eta - sqrt(eta*eta-1))*exp(1j*T*sqrt(eta*eta-1))
        res = ((eta + (sqrt(eta*eta-1)) * ((S1+S2)/(S1-S2))) *
               sqrt(FH[n] / FmH[n]))
        n += 1
    return res


def f_ReflDict(data):
    a = P4Radmax()
    G = a.ParamDict['G']
    thB_S = a.ParamDict['thB_S']
    wl = data['wavelength']
    t = data['damaged_depth']
    N = data['number_slices']
    resol = a.ParamDict['resol']
    b_S = a.ParamDict['b_S']
    phi = a.ConstDict['phi']
    t_l = a.ParamDict['t_l']
    z = a.ParamDict['z']
    FH = a.ParamDict['FH']
    FmH = a.ParamDict['FmH']
    F0 = a.ParamDict['F0']
    sp = a.ParamDict['sp']
    dwp = a.ParamDict['dwp']
    th = a.ParamDict['th']
    spline_DW = a.splinenumber[1]
    spline_strain = a.splinenumber[0]
    param = a.ParamDict['par']

    if a.fitlive == 1:
        param = a.ParamDict['_fp_min']

    strain = f_strain(z, param[:len(sp):], t, spline_strain)
    DW = f_DW(z, param[len(sp):len(sp)+len(dwp):], t, spline_DW)

    thB = thB_S - strain * tan(thB_S)  # angle de Bragg dans chaque lamelle
    eta = ((-b_S*(th-thB_S)*sin(2*thB_S) - 0.5*G*F0[0]*(1-b_S)) /
           ((abs(b_S)**0.5) * G * (FH[0]*FmH[0])**0.5))
    res = (eta - signe(eta.real)*((eta*eta - 1)**0.5)) * (FH[0] / FmH[0])**0.5

    n = 1
    while (n <= N):
        g0 = sin(thB[n] - phi)  # gamma 0
        gH = -sin(thB[n] + phi)  # gamma H
        b = g0 / gH
        T = (pi * G * ((FH[n] * FmH[n])**0.5) * t_l * DW[n] /
             (wl * (abs(g0 * gH)**0.5)))
        eta = ((-b*(th-thB[n])*sin(2*thB_S) - 0.5*G*F0[n]*(1-b)) /
               ((abs(b)**0.5) * G * DW[n] * (FH[n]*FmH[n])**0.5))
        S1 = (res - eta + sqrt(eta*eta-1))*exp(-1j*T*sqrt(eta*eta-1))
        S2 = (res - eta - sqrt(eta*eta-1))*exp(1j*T*sqrt(eta*eta-1))
        res = ((eta + (sqrt(eta*eta-1)) * ((S1+S2)/(S1-S2))) *
               sqrt(FH[n] / FmH[n]))
        n += 1
    return convolve(abs(res)**2, resol, mode='same')
