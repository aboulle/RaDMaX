#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A_BOULLE & M_SOUILAH
# Version du : 22/06/2015

from Parameters4Diff import *
from ConfigParser import SafeConfigParser

"""Read and create config file"""
#definition of the exact structure of the config file
structure_section = ['Crystal', 'Data files', 'Experiment', 'Material', 'Strain and DW', 'GSA options', 'Advanced GSA options']
structure_Crystal = ['crystal_name']
structure_Data_filename = ['input_dw', 'input_strain', 'xrd_data']
structure_Experiment = ['wavelength', 'resolution', 'shape', 'background']
structure_Material = ['h', 'k', 'l', 'a', 'b', 'c', 'alpha', 'beta', 'gamma']
structure_Strain_and_DW = ['strain_basis_func', 'min_strain', 'max_strain', 'dw_basis_func', 'min_dw', 'max_dw', 'damaged_depth', 'number_slices']
structure_GSA_options = ['tmax', 'nb_cycle_max', 'nb_palier']
structure_Adv_GSA_options = ['qa', 'qv', 'qt']

section_name = structure_Crystal + structure_Data_filename + structure_Experiment + structure_Material + structure_Strain_and_DW + structure_GSA_options + structure_Adv_GSA_options

lecture_fichier = []
floatconv = []
result_values = []        
        
#------------------------------------------------------------------------------
class ReadFile(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY)

    def Read_init_Paramters(self, filename):
        if not os.path.exists(filename):
            logger.log(logging.WARNING, "! Attention, the config file does not exist: " + str(filename))
        else:
            result_values[:] = []
            logger.log(logging.INFO, "Trying to load the following config file: " + str(filename))
            self.test_existence_section(filename)

    def test_existence_section(self, filename):
        test_true_false = []
        parser = SafeConfigParser(allow_no_value = True)
        try:
            parser.read(filename)
        except ConfigParser.MissingSectionHeaderError:
               print "\n! Config file structure is not correct, please check your config file !!"
               sys.exit(1)
        for nameofsection in structure_section[:-1]:
            var = parser.has_section(nameofsection)
            test_true_false.append(var)
        indices_section = self.all_indices(False, test_true_false)
        if indices_section != []:
           print "\n! Check your config file!"
           print 'The following sections are not being present:'
           for char in indices_section:
              print structure_section[char]
        else:
             self.test_existence_option(filename, section_name)

    def test_existence_option(self, filename, section_name):
        test_true_false = []
        parser = SafeConfigParser(allow_no_value = True)
        parser.read(filename)
        lecture_fichier[:] = []
        for nameofsection in structure_section:
            for name, value in parser.items(nameofsection):
    #            print '%s.%s : %s' % (section_name, name, parser.has_option(section_name, name))
                var = name
                test_true_false.append(var)
        difference = self.diff(section_name, test_true_false)
        if difference == []:
           for nameofsection in parser.sections():
               for name, value in parser.items(nameofsection):
                   var = parser.get(nameofsection, name)
                   lecture_fichier.append(var)
           self.test_existence_value(filename, section_name)
        else:
           print "\n! Check your config file!"
           print 'The following options are not being present:'
           for chare in difference:
               print chare

    def test_existence_value(self, filename, section_name):
        parser = SafeConfigParser(allow_no_value = True)
        parser.read(filename)
        nulle = self.all_indices('', lecture_fichier)
        if nulle == []:
            for nameofsection in parser.sections():
                #print 'Section:', nameofsection
                #print '  Options:', parser.options(nameofsection)
                for name, value in parser.items(nameofsection):
                    var = parser.get(nameofsection, name)
                    result_values.append(var)
                    #print '  %s = %s' % (name, value)
                    #print
        else:
           print "\n! Check your config file!"
           print "Value of option section are not being present:"
           logger.log(logging.WARNING, "Check your config file!")
           logger.log(logging.WARNING, "Value of option section are not being present:")
           for chare in nulle:
               print section_name[chare]
               logger.log(logging.ERROR, "Missing data from: " + str(section_name[chare]))
             

    def read_result_value(self):
        if result_values != []:
            return result_values

#    def read_result_value(self):
#        if result_values != []:
#            strconv = []
#            strconv.append(str(result_values[0]))
#            strconv.append(str(result_values[1]))
#            strconv.append(str(result_values[2]))
#            floatconv = [float(a) for a in result_values[3:23]]
#            result = strconv + floatconv
#        return result_values


    def all_indices(self, value, qlist):
        """return indice of list containing identical value"""
        indices = []
        idx = -1
        while True:
            try:
                idx = qlist.index(value, idx+1)
                indices.append(idx)
            except ValueError:
                break
        return indices


    def diff(self, a, b):
        """retrun difference between 2 list"""
        b = set(b)
        return [aa for aa in a if aa not in b]

    """End of read config file"""
    
#------------------------------------------------------------------------------
    def read_dw_file(self, filename_):
        """Opening file containing the experimental data"""
        logger.log(logging.INFO, "Reading experimental data file: " + filename_)
        try:
            P4Diff.dwp = loadtxt(filename_)
#            P4Diff.dwp = np.loadtxt(filename, dtype= np.float32, skiprows=0)
            return 0
        except (IOError):
            logger.log(logging.ERROR, "!!! .txt data file is not present !!!")
        except (IndexError):
            logger.log(logging.ERROR, "!!! The number of columns in the file is not correct !!!")

    def read_strain_file(self, filename_):
        """Opening file containing the experimental data"""
        logger.log(logging.INFO, "Reading experimental data file: " + filename_)
        try:
            P4Diff.sp = loadtxt(filename_)
#            P4Diff.sp = np.loadtxt(filename, dtype= np.float32, skiprows=0)
            return 0
        except (IOError):
            logger.log(logging.ERROR, "!!! .txt data file is not present !!!")
        except (IndexError):
            logger.log(logging.ERROR, "!!! The number of columns in the file is not correct !!!")

    def read_dw_xy_file(self, filename_):
        """Opening file containing the experimental data"""
        logger.log(logging.INFO, "Reading experimental data file: " + filename_)
        try:
            data = loadtxt(filename_, unpack=True)
            return data
        except (IOError):
            logger.log(logging.ERROR, "!!! .txt data file is not present !!!")
        except (IndexError):
            logger.log(logging.ERROR, "!!! The number of columns in the file is not correct !!!")

    def read_strain_xy_file(self, filename_):
        """Opening file containing the experimental data"""
        logger.log(logging.INFO, "Reading experimental data file: " + filename_)
        try:
            data = loadtxt(filename_, unpack=True)
            return data
        except (IOError):
            logger.log(logging.ERROR, "!!! .txt data file is not present !!!")
        except (IndexError):
            logger.log(logging.ERROR, "!!! The number of columns in the file is not correct !!!")

    def read_xrd_file(self, filename_):
        """Opening file containing the experimental data"""
        logger.log(logging.INFO, "Reading experimental data file: " + filename_)
        try:
            P4Diff.data_xrd = loadtxt(filename_, unpack=True)
#            P4Diff.data_xrd = np.loadtxt(filename, unpack=True, dtype=[('num1', np.float32),('num2',np.float32)], skiprows=0)
            return 0
        except (IOError):
            logger.log(logging.ERROR, "!!! .txt data file is not present !!!")
        except (IndexError):
            logger.log(logging.ERROR, "!!! The number of columns in the file is not correct !!!")

#------------------------------------------------------------------------------
class SaveFile4Diff(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY)

    def save_project(self, data, case):
        nunberofdatapersection = [0, len(structure_Crystal), len(structure_Data_filename), len(structure_Experiment),\
        len(structure_Material), len(structure_Strain_and_DW), len(structure_GSA_options), len(structure_Adv_GSA_options)]
        a = P4Diff()
        filename_ = a.path2inicomplete
        parser = SafeConfigParser()
        if case == 0:
            parser.read(filename_)
        new_section_name = section_name
        P4Diff.allparameters4save = data + a.allparameters
        Initial_data = dict(zip(section_name, a.allparameters4save))
        for i in range(len(structure_section)):
            if case == 1:
                parser.add_section(structure_section[i])
            k = nunberofdatapersection[i]
            r = nunberofdatapersection[i+1]
            new_section_name = new_section_name[k:]
            for l in range(r):
                parser.set(structure_section[i], new_section_name[l], str(Initial_data[new_section_name[l]]))
        parser.write(open(filename_,'w'))
        
