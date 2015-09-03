#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A_BOULLE & M_SOUILAH

'''
Calcule la fonction de base Bspline et la cubic-spline
attention l'échelle horizontale est arbitraire (z = 0 -> 1ere abscisse
z=max -> dernière abscisse
'''	

def bSpline3(z):
    if z <= 0 :
        return 0
    elif z <= 1:
        return (z**3)/6
    elif z <= 2:
        return (2./3) + z * (-2 + z*(2 - z/2))
    elif z <= 3:
        return (-22./3) + z * (10 + z*(-4 + z/2))
    elif z <= 4:
        return (32./3) + z * (-8 + z*(2 - z/6))
    else :
        return 0

##definition de la fonction cubic-spline
def cubicSpline(z,w):
    somme = 0
    index = 0
    for poids in w:
        somme = somme + poids * bSpline3(z-index+3)
        index = index + 1
    return somme

def bSpline1(z):
    if z <= 0 :
        return 0
    elif z <= 1:
        return z
    elif z <= 2:
        return 2-z
    else :
        return 0

def linearSpline(z,w):
    somme = 0
    index = 0
    for poids in w:
        somme = somme + poids * bSpline1(z-index+1)
        index = index + 1
    return somme

def bSpline0(z):
    if z <= 0 :
        return 0
    elif z <= 1:
        return 1
    else :
        return 0

def constantSpline(z,w):
    somme = 0
    index = 0
    for poids in w:
        somme = somme + poids * bSpline0(z-index)
        index = index + 1
    return somme
