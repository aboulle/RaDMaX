#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project
from __future__ import division

from math import tan, sin
from math import sqrt as sqrt_
from cmath import exp as cexp
from cmath import sqrt
import numpy as np

try:
    from numba import jit, i4, c16, f8
    
    @jit([(f8[:], f8[:], c16[:], c16[:], c16[:], f8[:],
         f8[:], i4, i4, c16[:], c16[:], f8[:])], cache=True, nopython=True)
    def f_Refl_jit(strain, DW, FH, FmH, F0, th, const_all, z, number_slices,
                   res, etas, thB):
    
        wl = const_all[0]
    #    t = const_all[1]
        phi = const_all[2]
        b_S = const_all[3]
        G = const_all[4]
        thB_S = const_all[5]
        t_l = const_all[6]
        N = number_slices
        N1 = N + 1
        N2 = th.shape[0]
    
        for i in range(N1):
            thB[i] = thB_S - strain[i]*tan(thB_S)
    
        for i in range(N2):
            a1 = -1.0*b_S*(th[i]-thB_S)*sin(2.*thB_S)
            a2 = 0.5*G*F0[0]*(1.-b_S)
            aa = a1 - a2
            bb = sqrt_(abs(b_S)) * G * sqrt(FH[0]*FmH[0])
            etas[i] = aa/bb
            eta = etas[i]
            real_eta_part = eta.real
            cc = eta - (real_eta_part/abs(real_eta_part))*(sqrt(eta*eta - 1.))
            dd = sqrt(FH[0] / FmH[0])
            res[i] = cc*dd
    
        for n in range(1, N):
            g0 = sin(thB[n] - phi)
            gH = -sin(thB[n] + phi)
            b = g0 / gH
            t_1_a = np.pi * G
            t_1_b = sqrt(FH[n]*FmH[n])
            t_1_c = t_l * DW[n]
            t_1 = t_1_a * t_1_b * t_1_c
            t_2 = wl * sqrt_(abs(g0*gH))
            T = t_1 / t_2
            for i in range(N2):
                eta_1 = -b*(th[i]-thB[n])*sin(2*thB_S) - 0.5*G*F0[n]*(1-b)
                eta_2 = sqrt_(abs(b)) * G * DW[n] * sqrt(FH[n]*FmH[n])
                etas[i] = eta_1 / eta_2
                eta = etas[i]
                S1 = (res[i] - eta + sqrt(eta * eta - 1)) * cexp(-1j * T * sqrt(eta * eta - 1.0))
                S2 = (res[i] - eta - sqrt(eta * eta - 1)) * cexp(1j * T * sqrt(eta * eta - 1))
                res[i] = (eta + sqrt(eta*eta-1) * ((S1 + S2)/(S1 - S2))) * sqrt(FH[n] / FmH[n])
except ImportError:
    pass
