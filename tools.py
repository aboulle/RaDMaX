#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A_BOULLE & M_SOUILAH

import csv
from scipy import *
from scipy.interpolate import *

'''Find the number of a given line'''
def find(x, Z):
	i = where(x == Z)
	return i[0]
	
'''sign function'''
def signe(x):
	return x.real / abs(x.real)

'''Pseudo-Voigt function'''
def f_pVoigt(x, pv_p):
	max = pv_p[0]
	pos = pv_p[1]
	FWHM = pv_p[2]
	eta = pv_p[3]
	gauss = max * exp(-log(2.) * ((x-pos)/(0.5*FWHM))**2)
	lorentz = max / (1. + ((x - pos)/(0.5*FWHM))**2)
	return eta*lorentz + (1-eta)*gauss

'''Computes planar spacing and cell volume'''
def f_dhkl_V(h,k,l,a,b,c, alpha, beta, gamma):
	cosa = cos(alpha*pi/180)
	cosb = cos(beta*pi/180)
	cosg = cos(gamma*pi/180)
	sina = sin(alpha*pi/180)
	sinb = sin(beta*pi/180)
	sing = sin(gamma*pi/180)
	V = a*b*c*sqrt(1 - cosa**2 - cosb**2 - cosg**2 + 2*cosa*cosb*cosg)
	s11 = (b*c*sina)**2
	s22 = (a*c*sinb)**2
	s33 = (a*b*sing)**2
	s12 = a*b*c*c*(cosa*cosb - cosg)
	s23 = a*a*b*c*(cosb*cosg - cosa)
	s13 = a*b*b*c*(cosg*cosa - cosb)
	dhkl = V / sqrt(s11*h*h + s22*k*k + s33*l*l + 2*s12*h*k + 2*s23*k*l + 2*s13*h*l)
	return dhkl, V

'''Read csv file, converts to elements dictionnary'''
def csv2dic_el(nom):
    try:
        with open(nom, 'r') as f:
            reader = csv.reader(f)
            dictionnaire = {}	
            for row in reader:
            	Z, symbol, name = row
            	dictionnaire[symbol] = Z
        return dictionnaire
    except IOError:
        print "Cannot open file"
        return False
	
'''Read csv file, converts to dictionnary with the f0 parameters'''
def csv2dic_f0(nom):
    try:
        with open(nom, 'r') as f:
            reader = csv.reader(f)
            dictionnaire = {}	
            for row in reader:
                symbol, a1, a2, a3, a4, a5, c, b1, b2, b3, b4, b5 = row
#                symbol, coefs = row
                dictionnaire[symbol] =  array([a1, a2, a3, a4, a5, c, b1, b2, b3, b4, b5], dtype = 'float')
        return dictionnaire
    except IOError:
        print "Cannot open file"
        return False

'''Read the structure file and extract element names and coordinates'''
def read_structure(nom):
    try:
        with open(nom, 'r') as f:
            first = True
            i = -1
            for line in f:
                if first:
                    elements = line.split()
                    xyz = [None]*len(elements)
                    first = False            
                else:
                    if line.startswith("#"):
                        i +=1
                        new = True
                        xyz[i] = zeros(3)
                    else:
                        x, y, z = line.split()
                        if new:
        			xyz[i] = array([float(x), float(y), float(z)])
        			new = False
                        else: 
        			xyz[i] = vstack((xyz[i], array([float(x), float(y), float(z)])))
        return elements, xyz
    except IOError:
        print "Cannot open file"
        return False
        

'''write file from dictionnary'''
def dic2file(dictionnaire, nom_fichier): 
    try:
        with open(nom_fichier, 'w') as f:
            for Z in dictionnaire.keys(): 
                f.write('%s %s\n' % (Z, dictionnaire[Z]))  
    except IOError:
        print "Cannot open file"
        return False
