#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

from Def_Strain4Radmax import f_strain
from Def_DW4Radmax import f_DW
from Parameters4Radmax import P4Rm
from scipy import tan, exp, sin, pi, convolve, sqrt
from Tools4Radmax import signe

# =============================================================================
# Calcul de la réflectivité dynamique
# =============================================================================


def f_Refl(choice, Data=None):
    if choice == 0:
        res = f_Refl_Default()
    elif choice == 1:
        res = f_Refl_Thin_Film()
    elif choice == 2:
        res = f_Refl_Thick_Film()
    elif choice == 3:
        res = f_Refl_Thick_Film_and_Substrate()
    elif choice == 4:
        res = f_Refl_Substrate
    return res


def f_Refl_fit(choice, Data=None):
    if choice == 0:
        res = f_Refl_Default_fit(Data)
    elif choice == 1:
        res = f_Refl_Thin_Film_fit(Data)
    elif choice == 2:
        res = f_Refl_Thick_Film_fit(Data)
    elif choice == 3:
        res = f_Refl_Thick_Film_and_Substrate_fit(Data)
    elif choice == 4:
        res = f_Refl_Substrate_fit(Data)
    return res


# =============================================================================
# # # # # # For Fit ONLY
# =============================================================================

# =============================================================================
# label_1 = "Default"
# =============================================================================
def f_Refl_Default_fit(Data):
    strain = Data[0]
    DW = Data[1]

    dat = Data[2]
    wl = dat[0]
    N = dat[2]

    phi = dat[3]
    t_l = dat[4]
    b_S = dat[5]
    thB_S = dat[6]
    G = dat[7]
    F0 = dat[8]
    FH = dat[9]
    FmH = dat[10]
    th = dat[19]

    thB = thB_S - strain * tan(thB_S)  # angle de Bragg dans chaque lamelle
    eta = ((-b_S*(th-thB_S)*sin(2*thB_S) - 0.5*G*F0[0]*(1-b_S)) /
           ((abs(b_S)**0.5) * G * (FH[0]*FmH[0])**0.5))
    res = (eta - signe(eta.real)*((eta*eta - 1)**0.5))

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
        res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))
        n += 1
    return res


# =============================================================================
# label_2 = "Thin film"
# =============================================================================
def f_Refl_Thin_Film_fit(Data):
    strain = Data[0]
    DW = Data[1]

    dat = Data[2]
    wl = dat[0]
    N = dat[2]

    phi = dat[3]
    t_l = dat[4]
    thB_S = dat[6]
    G = dat[7]
    F0 = dat[8]
    FH = dat[9]
    FmH = dat[10]
    th = dat[19]

    thB = thB_S - strain * tan(thB_S)  # angle de Bragg dans chaque lamelle

    eta = 0
    res = 0

    n = 1
    while (n <= N):
        g0 = sin(thB[n] - phi)  # gamma 0
        gH = -sin(thB[n] + phi)  # gamma H
        b = g0 / gH
        T = pi * G * ((FH[n]*FmH[n])**0.5) * t_l * DW[n] / (wl * (abs(g0*gH)**0.5))
        eta = (-b*(th-thB[n])*sin(2*thB_S) - 0.5*G*F0[n]*(1-b)) / ((abs(b)**0.5) * G * DW[n] * (FH[n]*FmH[n])**0.5)
        S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
        S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
        res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))
        n += 1
    return res


# =============================================================================
# label_3 = "Thick film"
# =============================================================================
def f_Refl_Thick_Film_fit(Data):
    strain = Data[0]
    DW = Data[1]

    dat = Data[2]
    wl = dat[0]
    t = dat[1]
    N = dat[2]

    phi = dat[3]
    t_l = dat[4]
    thB_S = dat[6]
    G = dat[7]
    F0 = dat[8]
    FH = dat[9]
    FmH = dat[10]
    t_film = dat[17]
    th = dat[19]
    delta_t = t_film - t

    thB = thB_S - strain * tan(thB_S)  # angle de Bragg dans chaque lamelle

    eta = 0
    res = 0

    g0 = sin(thB[0] - phi)  # gamma 0
    gH = -sin(thB[0] + phi)  # gamma H
    b = g0 / gH
    T = pi * G * ((FH[0]*FmH[0])**0.5) * delta_t / (wl * (abs(g0*gH)**0.5))
    eta = (-b*(th-thB[0])*sin(2*thB_S) - 0.5*G*F0[0]*(1-b)) / ((abs(b)**0.5) * G  * (FH[0]*FmH[0])**0.5)
    S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
    S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
    res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))

    n = 1
    while (n <= N):
        g0 = sin(thB[n] - phi)  # gamma 0
        gH = -sin(thB[n] + phi)  # gamma H
        b = g0 / gH
        T = pi * G * ((FH[n]*FmH[n])**0.5) * t_l * DW[n] / (wl * (abs(g0*gH)**0.5))
        eta = (-b*(th-thB[n])*sin(2*thB_S) - 0.5*G*F0[n]*(1-b)) / ((abs(b)**0.5) * G * DW[n] * (FH[n]*FmH[n])**0.5)
        S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
        S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
        res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))
        n += 1
    return res


# =============================================================================
# label_4 = "Thick film + substrate"
# =============================================================================
def f_Refl_Thick_Film_and_Substrate_fit(Data):
    strain = Data[0]
    DW = Data[1]

    dat = Data[2]
    wl = dat[0]
    t = dat[1]
    N = dat[2]

    phi = dat[3]
    t_l = dat[4]
    thB_S = dat[6]
    G = dat[7]
    F0 = dat[8]
    FH = dat[9]
    FmH = dat[10]

    b_Sub = dat[11]
    thB_Sub = dat[12]
    G_Sub = dat[13]
    F0_Sub = dat[14]
    FH_Sub = dat[15]
    FmH_Sub = dat[16]

    t_film = dat[17]
    dw_film = dat[18]
    th = dat[19]
    delta_t = t_film - t

    thB = thB_S - strain * tan(thB_S)  # angle de Bragg dans chaque lamelle

    temp1 = -b_Sub*(th-thB_Sub)*sin(2*thB_Sub) - (0.5*G_Sub*F0_Sub[0]*(1-b_Sub))
    temp2 = (abs(b_Sub)**0.5) * G_Sub * (FH_Sub[0]*FmH_Sub[0])**0.5
    eta = temp1/temp2
    res = (eta - signe(eta.real)*((eta*eta - 1)**0.5))

    g0 = sin(thB[0] - phi)  # gamma 0
    gH = -sin(thB[0] + phi)  # gamma H
    b = g0 / gH
    T = pi * G * ((FH[0]*FmH[0])**0.5) * delta_t * dw_film / (wl * (abs(g0*gH)**0.5))
    eta = (-b*(th-thB[0])*sin(2*thB_S) - 0.5*G*F0[0]*(1-b)) / ((abs(b)**0.5) * G  * dw_film * (FH[0]*FmH[0])**0.5)
    S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
    S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
    res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))

    n = 1
    while (n <= N):
        g0 = sin(thB[n] - phi)  # gamma 0
        gH = -sin(thB[n] + phi)  # gamma H
        b = g0 / gH
        T = pi * G * ((FH[n]*FmH[n])**0.5) * t_l * DW[n] * dw_film / (wl * (abs(g0*gH)**0.5))
        eta = (-b*(th-thB[n])*sin(2*thB_S) - 0.5*G*F0[n]*(1-b)) / ((abs(b)**0.5) * G * DW[n] * dw_film * (FH[n]*FmH[n])**0.5 )
        S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
        S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
        res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))
        n += 1
    return res


# =============================================================================
# Only substrate for t=0 --> damaged depth
# =============================================================================
def f_Refl_Substrate_fit(Data):
    a = P4Rm()

    G = a.ParamDict['G']
    thB_S = a.ParamDict['thB_S']
    resol = a.ParamDict['resol']
    b_S = a.ParamDict['b_S']
    FH = a.ParamDict['FH']
    FmH = a.ParamDict['FmH']
    F0 = a.ParamDict['F0']
    th = a.ParamDict['th']	
    eta = (-b_S*(th-thB_S)*sin(2*thB_S) - 0.5*G*F0[0]*(1-b_S)) / ((abs(b_S)**0.5) * G * (FH[0]*FmH[0])**0.5)
    res = (eta - signe(eta.real)*((eta*eta - 1)**0.5)) * (FH[0] / FmH[0])**0.5
    return convolve(abs(res)**2, resol, mode='same')

# =============================================================================
# # # # # #
# =============================================================================


# =============================================================================
# label_1 = "Default"
# =============================================================================
def f_Refl_Default():
    a = P4Rm()

    wl = a.AllDataDict['wavelength']
    t = a.AllDataDict['damaged_depth']
    N = a.AllDataDict['number_slices']

    G = a.ParamDict['G']
    thB_S = a.ParamDict['thB_S']
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

    strain = f_strain(z, param[:len(sp):], t, spline_strain)
    DW = f_DW(z, param[len(sp):len(sp)+len(dwp):], t, spline_DW)

    thB = thB_S - strain * tan(thB_S)  # angle de Bragg dans chaque lamelle
    eta = ((-b_S*(th-thB_S)*sin(2*thB_S) - 0.5*G*F0[0]*(1-b_S)) /
           ((abs(b_S)**0.5) * G * (FH[0]*FmH[0])**0.5))
    res = (eta - signe(eta.real)*((eta*eta - 1)**0.5))

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
        res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))
        n += 1
    return convolve(abs(res)**2, resol, mode='same')


# =============================================================================
# label_2 = "Thin film"
# =============================================================================
def f_Refl_Thin_Film():
    a = P4Rm()

    wl = a.AllDataDict['wavelength']
    t = a.AllDataDict['damaged_depth']
    N = a.AllDataDict['number_slices']

    G = a.ParamDict['G']
    thB_S = a.ParamDict['thB_S']
    resol = a.ParamDict['resol']
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

    strain = f_strain(z, param[:len(sp):], t, spline_strain)
    DW = f_DW(z, param[len(sp):len(sp)+len(dwp):], t, spline_DW)
    thB = thB_S - strain * tan(thB_S)  # angle de Bragg dans chaque lamelle

    eta = 0
    res = 0

    n = 1
    while (n <= N):
        g0 = sin(thB[n] - phi)  # gamma 0
        gH = -sin(thB[n] + phi)  # gamma H
        b = g0 / gH
        T = pi * G * ((FH[n]*FmH[n])**0.5) * t_l * DW[n] / (wl * (abs(g0*gH)**0.5))
        eta = (-b*(th-thB[n])*sin(2*thB_S) - 0.5*G*F0[n]*(1-b)) / ((abs(b)**0.5) * G * DW[n] * (FH[n]*FmH[n])**0.5)
        S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
        S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
        res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))
        n += 1
    return convolve(abs(res)**2, resol, mode='same')


# =============================================================================
# label_3 = "Thick film"
# =============================================================================
def f_Refl_Thick_Film():
    a = P4Rm()

    wl = a.AllDataDict['wavelength']
    t = a.AllDataDict['damaged_depth']
    N = a.AllDataDict['number_slices']
    t_film = a.AllDataDict['film_thick']

    G = a.ParamDict['G']
    thB_S = a.ParamDict['thB_S']
    resol = a.ParamDict['resol']
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
    delta_t = t_film - t

    strain = f_strain(z, param[:len(sp):], t, spline_strain)
    DW = f_DW(z, param[len(sp):len(sp)+len(dwp):], t, spline_DW)
    thB = thB_S - strain * tan(thB_S)  # angle de Bragg dans chaque lamelle

    eta = 0
    res = 0

    g0 = sin(thB[0] - phi)  # gamma 0
    gH = -sin(thB[0] + phi)  # gamma H
    b = g0 / gH
    T = pi * G * ((FH[0]*FmH[0])**0.5) * delta_t / (wl * (abs(g0*gH)**0.5))
    eta = (-b*(th-thB[0])*sin(2*thB_S) - 0.5*G*F0[0]*(1-b)) / ((abs(b)**0.5) * G  * (FH[0]*FmH[0])**0.5)
    S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
    S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
    res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))

    n = 1
    while (n <= N):
        g0 = sin(thB[n] - phi)  # gamma 0
        gH = -sin(thB[n] + phi)  # gamma H
        b = g0 / gH
        T = pi * G * ((FH[n]*FmH[n])**0.5) * t_l * DW[n] / (wl * (abs(g0*gH)**0.5))
        eta = (-b*(th-thB[n])*sin(2*thB_S) - 0.5*G*F0[n]*(1-b)) / ((abs(b)**0.5) * G * DW[n] * (FH[n]*FmH[n])**0.5)
        S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
        S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
        res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))
        n += 1
    return convolve(abs(res)**2, resol, mode='same')


# =============================================================================
# label_4 = "Thick film + substrate"
# =============================================================================
def f_Refl_Thick_Film_and_Substrate():
    a = P4Rm()

    wl = a.AllDataDict['wavelength']
    t = a.AllDataDict['damaged_depth']
    N = a.AllDataDict['number_slices']
    t_film = a.AllDataDict['film_thick']
    dw_film = a.AllDataDict['dw_thick']

    G = a.ParamDict['G']
    thB_S = a.ParamDict['thB_S']
    resol = a.ParamDict['resol']
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
    b_Sub = a.ParamDict['b_S_s']
    thB_Sub = a.ParamDict['thB_S_s']
    G_Sub = a.ParamDict['G_s']
    F0_Sub = a.ParamDict['F0_s']
    FH_Sub = a.ParamDict['FH_s']
    FmH_Sub = a.ParamDict['FmH_s']
    delta_t = t_film - t

    strain = f_strain(z, param[:len(sp):], t, spline_strain)
    DW = f_DW(z, param[len(sp):len(sp)+len(dwp):], t, spline_DW)
    thB = thB_S - strain * tan(thB_S)  # angle de Bragg dans chaque lamelle

    temp1 = -b_Sub*(th-thB_Sub)*sin(2*thB_Sub) - (0.5*G_Sub*F0_Sub[0]*(1-b_Sub))
    temp2 = (abs(b_Sub)**0.5) * G_Sub * (FH_Sub[0]*FmH_Sub[0])**0.5
    eta = temp1/temp2
    res = (eta - signe(eta.real)*((eta*eta - 1)**0.5))

    g0 = sin(thB[0] - phi)  # gamma 0
    gH = -sin(thB[0] + phi)  # gamma H
    b = g0 / gH
    T = pi * G * ((FH[0]*FmH[0])**0.5) * delta_t * dw_film / (wl * (abs(g0*gH)**0.5))
    eta = (-b*(th-thB[0])*sin(2*thB_S) - 0.5*G*F0[0]*(1-b)) / ((abs(b)**0.5) * G  * dw_film * (FH[0]*FmH[0])**0.5)
    S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
    S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
    res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))

    n = 1
    while (n <= N):
        g0 = sin(thB[n] - phi)  # gamma 0
        gH = -sin(thB[n] + phi)  # gamma H
        b = g0 / gH
        T = pi * G * ((FH[n]*FmH[n])**0.5) * t_l * DW[n] * dw_film / (wl * (abs(g0*gH)**0.5))
        eta = (-b*(th-thB[n])*sin(2*thB_S) - 0.5*G*F0[n]*(1-b)) / ((abs(b)**0.5) * G * DW[n] * dw_film * (FH[n]*FmH[n])**0.5)
        S1 = (res - eta + (eta*eta-1)**0.5)*exp(-1j*T*(eta*eta-1)**0.5)
        S2 = (res - eta - (eta*eta-1)**0.5)*exp(1j*T*(eta*eta-1)**0.5)
        res = (eta + ((eta*eta-1)**0.5) * ((S1+S2)/(S1-S2)))
        n += 1
    return convolve(abs(res)**2, resol, mode='same')


# =============================================================================
# Only substrate for t=0 --> damaged depth
# =============================================================================
def f_Refl_Substrate(th, param):
    a = P4Rm()

    G = a.ParamDict['G']
    thB_S = a.ParamDict['thB_S']
    resol = a.ParamDict['resol']
    b_S = a.ParamDict['b_S']
    FH = a.ParamDict['FH']
    FmH = a.ParamDict['FmH']
    F0 = a.ParamDict['F0']
    th = a.ParamDict['th']
		
    eta = (-b_S*(th-thB_S)*sin(2*thB_S) - 0.5*G*F0[0]*(1-b_S)) / ((abs(b_S)**0.5) * G * (FH[0]*FmH[0])**0.5)
    res = (eta - signe(eta.real)*((eta*eta - 1)**0.5)) * (FH[0] / FmH[0])**0.5
    return convolve(abs(res)**2, resol, mode='same')
