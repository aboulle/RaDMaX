#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

import numpy as np


def f_Gauss(x, param):
    max_ = param[0]
    pos = param[1]
    FWHM = param[2]
    return max_ * np.exp(-np.log(2.) * ((x-pos)/(0.5*FWHM))**2)


def f_Lorentz(x, param):
    max_ = param[0]
    pos = param[1]
    FWHM = param[2]
    return max_ / (1. + ((x - pos)/(0.5*FWHM))**2)


def f_pVoigt(x, param):
    max_ = param[0]
    pos = param[1]
    FWHM = param[2]
    eta = param[3]
    gauss = max_ * np.exp(-np.log(2.) * ((x-pos)/(0.5*FWHM))**2)
    lorentz = max_ / (1. + ((x - pos)/(0.5*FWHM))**2)
    return eta*lorentz + (1-eta)*gauss


def f_gbell(x, param):
    max_ = param[0]
    pos = param[1]
    FWHM = param[2]
    b = param[3]
    return max_ / (1. + (abs((x - pos)/(0.5*FWHM)))**(2*b))


def f_splitpV(x, param):
    max_ = param[0]
    pos = param[1]
    FWHMl = param[2]
    FWHMr = param[3]
    etal = param[4]
    etar = param[5]
    pv = f_pVoigt(x, [max_, pos, FWHMl, etal])
    pvr = f_pVoigt(x, [max_, pos, FWHMr, etar])
    pv[x > pos] = pvr[x > pos]
    return pv
