#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

from tools import *
from Parameters4Radmax import *


# Anomalous scattering factors
def f_f1f2(wl, el):
    # créer un dictionnaire el : Z
    h = 6.62606957e-34
    e = 1.602e-19
    c = 2.99792458e8
    Ewl = h*c / (wl*1e-10*e)
    if len(el[:-2:]) > 0:
        el = el[:-2]
    Z = int(csv2dic_el(os.path.join(struc_factors, "elements.csv"))[el])
    f = loadtxt(os.path.join(struc_factors, el + ".txt"))
    E = f[:, 0]
    f1 = f[:, 1]
    f2 = f[:, 2]
    f1_interp = interp1d(E, f1)(Ewl)
    f2_interp = interp1d(E, f2)(Ewl)

    return float(f1_interp)-Z + float(f2_interp)*1j


# Atomic scattering factor
def f_f0(th, wl, el):
    coeff = csv2dic_f0(os.path.join(struc_factors, "f0_all.csv"))[el]
    n = 0
    sum_ = coeff[5]
    while n <= 4:
        sum_ = sum_ + coeff[n] * exp(-coeff[n+6] * (sin(th) / wl)**2)
        n = n+1
    return sum_


def asf(th, wl, el):
    return f_f0(th, wl, el) + f_f1f2(wl, el), f_f0(0, wl, el) + f_f1f2(wl, el)


def structure_factor(h, k, l, wl, thB_S, alt, crystal_name):
    el, xyz = read_structure(os.path.join(structures_name, crystal_name))
    i = 0
    f, f0 = [None]*len(el), [None]*len(el)
    FH, FmH, F0 = [None]*len(el), [None]*len(el), [None]*len(el)
    while i < len(el):
        f[i], f0[i] = asf(thB_S, wl, el[i])
        FH[i] = f[i]*exp(-2j*pi*(h*xyz[i][:, 0] + k*xyz[i][:, 1] +
                         l*xyz[i][:, 2])).sum()
        FmH[i] = f[i]*exp(2j*pi*(h*xyz[i][:, 0] + k*xyz[i][:, 1] +
                          l*xyz[i][:, 2])).sum()
        F0[i] = f0[i]*shape(xyz[i])[0]
        i += 1
    FHo, FmHo, F0o = array(FH).sum(), array(FmH).sum(), array(F0).sum()
    FH, FmH, F0 = ones(len(alt))*FHo, ones(len(alt))*FmHo, ones(len(alt))*F0o
    return FH, FmH, F0


def f_FH(h, k, l, wl, thB_S, alt, crystal_name):
    """
    Replace name with appropriate material
    """
    FH, FmH, F0 = structure_factor(h, k, l, wl, thB_S, alt, crystal_name)
    return FH, FmH, F0
