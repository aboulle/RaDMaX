#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

from def_strain import f_strain
from def_DW import f_DW
from Parameters4Radmax import P4Diff
from scipy import tan, sin, exp, pi, convolve
from tools import signe

'''
Calcul de la réflectivité dynamique
'''
def f_Refl(data):
    a = P4Diff()
    G = a.G
    thB_S = a.thB_S
    wl = data['wavelength']
    t = data['damaged_depth']
    N = data['number_slices']
    resol = a.resol
    b_S = a.b_S
    phi = a.phi
    t_l = a.t_l
    z = a.z
    FH = a.FH
    FmH = a.FmH
    F0 = a.F0
    sp = a.sp
    dwp = a.dwp
    th = a.th
    spline_DW = a.splinenumber[1]
    spline_strain = a.splinenumber[0]
    param = a.par
    
    if a.fitlive == 1:
        param = a._fp_min

    strain = f_strain(z, param[:len(sp):], t, spline_strain)
    DW = f_DW(z, param[len(sp):len(sp)+len(dwp):], t, spline_DW)

    thB = thB_S - strain * tan(thB_S) ## angle de Bragg dans chaque lamelle	
    eta = (-b_S*(th-thB_S)*sin(2*thB_S) - 0.5*G*F0[0]*(1-b_S)) / ((abs(b_S)**0.5) * G * (FH[0]*FmH[0])**0.5 )
    res = (eta - signe(eta.real)*((eta*eta - 1)**0.5)) * (FH[0] / FmH[0])**0.5
    
    n = 1
    while (n<=N):
		#~ DW = exp(-1.*LH[n])
        g0 = sin(thB[n] - phi) ## gamma 0
        gH = -sin(thB[n] + phi) ## gamma H
        b = g0 / gH
        T = pi * G * ((FH[n]*FmH[n])**0.5) * t_l * DW[n]/ (wl * (abs(g0*gH)**0.5) )
        eta = (-b*(th-thB[n])*sin(2*thB_S) - 0.5*G*F0[n]*(1-b)) / ((abs(b)**0.5) * G * DW[n] * (FH[n]*FmH[n])**0.5 )
#        S = (eta*eta-1)**0.5
#            print n, S
        S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
#            print n, S1
        S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
        res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2))) * (FH[n] / FmH[n])**0.5
        n += 1
    return convolve(abs(res)**2, resol, mode='same')
        #return abs(res)**2

def f_Refl_lmfit(data, pars):
    a = P4Diff()
    G = a.G
    thB_S = a.thB_S
    wl = data['wavelength']
    t = data['damaged_depth']
    N = data['number_slices']
    resol = a.resol
    b_S = a.b_S
    phi = a.phi
    t_l = a.t_l
    z = a.z
    FH = a.FH
    FmH = a.FmH
    F0 = a.F0
    th = a.th
    if data['model'] == 2:
        spline_DW = 4
        spline_strain = 4
    elif data['model'] == 0:
        spline_DW = 5
        spline_strain = 5
    
    strain = f_strain(z, pars, t, spline_strain)
    DW = f_DW(z, pars, t, spline_DW)
    
    thB = thB_S - strain * tan(thB_S) ## angle de Bragg dans chaque lamelle
    eta = (-b_S*(th-thB_S)*sin(2*thB_S) - 0.5*G*F0[0]*(1-b_S)) / ((abs(b_S)**0.5) * G * (FH[0]*FmH[0])**0.5 )
    res = (eta - signe(eta.real)*((eta*eta - 1)**0.5)) * (FH[0] / FmH[0])**0.5
    
    n = 1
    while (n<=N):
		#~ DW = exp(-1.*LH[n])
        g0 = sin(thB[n] - phi) ## gamma 0
        gH = -sin(thB[n] + phi) ## gamma H
        b = g0 / gH
        T = pi * G * ((FH[n]*FmH[n])**0.5) * t_l * DW[n]/ (wl * (abs(g0*gH)**0.5) )
        eta = (-b*(th-thB[n])*sin(2*thB_S) - 0.5*G*F0[n]*(1-b)) / ((abs(b)**0.5) * G * DW[n] * (FH[n]*FmH[n])**0.5 )
#        S = (eta*eta-1)**0.5
#            print n, S
        S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
#            print n, S1
        S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
        res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2))) * (FH[n] / FmH[n])**0.5
        n += 1
    return convolve(abs(res)**2, resol, mode='same')
        #return abs(res)**2
