#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

#==============================================================================
# Radmax read module
#==============================================================================

from wx.lib.pubsub import pub

import os
from sys import exit
from sys import platform as _platform

import Parameters4Radmax as p4R
from Parameters4Radmax import P4Rm

try:
    from ConfigParser import SafeConfigParser, MissingSectionHeaderError
except (ImportError):
    from configparser import SafeConfigParser, MissingSectionHeaderError

from numpy import savetxt, loadtxt, column_stack, pi

from time import sleep

import logging
logger = logging.getLogger(__name__)

lecture_fichier = []
result_values = []

pubsub_ChangeFrameTitle = "ChangeFrameTitle"
pubsub_changeColor_field4Save = "ChangeColorField4Save"
pubsub_Read_field4Save = "ReadField4Save"


# -----------------------------------------------------------------------------
class ReadFile():
    """
    Reading '.ini' project
    Test if the config file has the waiting structure
    if not, the project can't be launch, and a warning is write in the log file
    """
    def __init__(self):
        self.section_name = []
        self.structure_section = []

    def on_read_init_parameters(self, filename, choice):
        if choice == 'RadmaxFile':
            self.section_name = p4R.Radmax_all_section
            self.structure_section = p4R.Radmax_File_section
        elif choice == 'ExperimentFile':
            self.section_name = p4R.Exp_file_all_section
            self.structure_section = p4R.Exp_file_section
        if not os.path.exists(filename):
            _msg = "! Pay attention, the config file does not exist: "
            logger.log(logging.WARNING, _msg + str(filename))
            if choice == 'RadmaxFile':
                _msg = "Making of the config file with initial parameters"
                logger.log(logging.WARNING, _msg + str(filename))
                a = SaveFile4Diff()
                a.on_makingof_config_file(filename)
        else:
            result_values[:] = []
            _msg = "Trying to load the following config file: "
            logger.log(logging.INFO, _msg + str(filename))
            if choice == 'ExperimentFile':
                self.test_data_file(filename)
            self.test_existence_section(filename)

    def test_existence_section(self, filename):
        test_true_false = []
        parser = SafeConfigParser(allow_no_value=True)
        try:
            parser.read(filename)
        except MissingSectionHeaderError:
            print ("\n! Config file structure is not correct," +
                   "please check your config file !!")
            exit(1)
        for nameofsection in self.structure_section:
            var = parser.has_section(nameofsection)
            test_true_false.append(var)
        indices_section = self.all_indices(False, test_true_false)
        if indices_section != []:
            print ("\n! Check your config file!" +
                   "The following sections are not being present:")
            for char in indices_section:
                print (self.structure_section[char])
        else:
            self.test_existence_option(filename, self.section_name)

    def test_existence_option(self, filename, section_name):
        test_true_false = []
        parser = SafeConfigParser(allow_no_value=True)
        parser.read(filename)
        lecture_fichier[:] = []
        for nameofsection in self.structure_section:
            for name, value in parser.items(nameofsection):
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
            print ("\n! Check your config file!" +
                   "The following sections are not being present:")
            for chare in difference:
                print (chare)

    def test_existence_value(self, filename, section_name):
        parser = SafeConfigParser(allow_no_value=True)
        parser.read(filename)
        nulle = self.all_indices('', lecture_fichier)
        if nulle == []:
            for nameofsection in parser.sections():
                for name, value in parser.items(nameofsection):
                    var = parser.get(nameofsection, name)
                    result_values.append(var)
        else:
            print ("\n! Check your config file!" +
                   "The following sections are not being present:")
            logger.log(logging.WARNING, "Check your config file!")
            logger.log(logging.WARNING, "Value of option section are" +
                       "not being present:")
            for chare in nulle:
                print (section_name[chare])
                logger.log(logging.ERROR, "Missing data from: " +
                           str(section_name[chare]))

    def read_result_value(self):
        if result_values != []:
            return result_values

    def all_indices(self, value, qlist):
        """
        return indice of list containing identical value
        """
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
        """
        return difference between 2 list
        """
        b = set(b)
        return [aa for aa in a if aa not in b]

    def test_data_file(self, name):
        with open(name, 'r') as f:
            skip_line = 2
            [next(f) for x in range(skip_line)]
            header = next(f)
            mline = ""
            for i in header:
                mline += i
            ll = mline.split()
            if ll == []:
                self.convert_Data_File(name)
            else:
                if ll[0] == 'substrate_name':
                    return 0
                else:
                    self.convert_Data_File(name)

    def nonblank_lines(self, f):
        for l in f:
            line = l.rstrip()
            if line:
                yield line

    def convert_Data_File(self, name):
        ll_0 = []
        ll_1 = []
        a = P4Rm()
        with open(name, 'r') as f:
            for line in self.nonblank_lines(f):
                if line[0] is not '[':
                    ll = line.split(' = ')
                    ll_0.append(ll[0])
                    ll_1.append(ll[1])
        i = 0
        P4Rm.AllDataDict['model'] = 0.0
        for k in ll_0:
            P4Rm.AllDataDict[k] = ll_1[i]
            i += 1
        P4Rm.AllDataDict['substrate_name'] = a.AllDataDict['crystal_name']
        for k in p4R.s_radmax_3 + p4R.s_radmax_4 + p4R.s_radmax_5:
            P4Rm.AllDataDict[k] = p4R.FitParamDefault[k]
        data_path = os.path.split(name)[0]
        data_file_name = os.path.splitext(os.path.basename(name))[0]
        data_name = os.path.join(data_path, data_file_name + '.ini')
        P4Rm.PathDict['path2inicomplete'] = data_name
        b = SaveFile4Diff()
        b.save_project(1)
        return 0

# -----------------------------------------------------------------------------
    """
    Read method for XRD, Strain and DW files
    """
    def read_dw_file(self, filename_):
        """
        Opening file containing the experimental data
        """
        logger.log(logging.INFO, "Reading experimental data file: " +
                   filename_)
        try:
            P4Rm.ParamDict['dwp'] = loadtxt(filename_)
            return 0
        except (IOError):
            logger.log(logging.ERROR, "!!! .txt data file is not present !!!")
        except (IndexError):
            logger.log(logging.ERROR, "!!! The number of columns in the" +
                       "file is not correct !!!")

    def read_strain_file(self, filename_):
        """
        Opening file containing the experimental data
        """
        logger.log(logging.INFO, "Reading experimental data file: " +
                   filename_)
        try:
            P4Rm.ParamDict['sp'] = loadtxt(filename_)
            return 0
        except (IOError):
            logger.log(logging.ERROR, "!!! .txt data file is not present !!!")
        except (IndexError):
            logger.log(logging.ERROR, "!!! The number of columns in the" +
                       "file is not correct !!!")

    def read_dw_xy_file(self, filename_):
        """
        Opening file containing the experimental data
        """
        logger.log(logging.INFO, "Reading experimental data file: " +
                   filename_)
        try:
            data = loadtxt(filename_, unpack=True)
            return data
        except (IOError):
            logger.log(logging.ERROR, "!!! .txt data file is not present !!!")
        except (IndexError):
            logger.log(logging.ERROR, "!!! The number of columns in the" +
                       "file is not correct !!!")

    def read_strain_xy_file(self, filename_):
        """
        Opening file containing the experimental data
        """
        logger.log(logging.INFO, "Reading experimental data file: " +
                   filename_)
        try:
            data = loadtxt(filename_, unpack=True)
            return data
        except (IOError):
            logger.log(logging.ERROR, "!!! .txt data file is not present !!!")
        except (IndexError):
            logger.log(logging.ERROR, "!!! The number of columns in the" +
                       "file is not correct !!!")

    def read_xrd_file(self, filename_):
        """
        Opening file containing the experimental data
        """
        logger.log(logging.INFO, "Reading experimental data file: " +
                   filename_)
        try:
            P4Rm.ParamDict['data_xrd'] = loadtxt(filename_, unpack=True)
            return 0
        except (IOError):
            logger.log(logging.ERROR, "!!! .txt data file is not present !!!")
        except (IndexError):
            logger.log(logging.ERROR, "!!! The number of columns in the" +
                       "file is not correct !!!")


# -----------------------------------------------------------------------------
class SaveFile4Diff():
    """
    Save the project in a '.ini' file
    several method are available, create a new file, update an existing file
    or making the 'RaDMax.ini' config file
    """

    def save_project(self, case):
        nunberofdatapersection = [0, len(p4R.s_crystal),
                                  len(p4R.s_data_file),
                                  len(p4R.s_experiment),
                                  len(p4R.s_material),
                                  len(p4R.s_strain_DW),
                                  len(p4R.s_GSA_options),
                                  len(p4R.s_bsplines),
                                  len(p4R.s_pv),
                                  len(p4R.s_GSA_expert),
                                  len(p4R.s_leastsq),
                                  len(p4R.s_geometry),
                                  len(p4R.s_substrate)]
        a = P4Rm()
        filename_ = a.PathDict['path2inicomplete']
        parser = SafeConfigParser()
        if case == 0:
            parser.read(filename_)
        new_section_name = p4R.Exp_file_all_section
        for i in range(len(p4R.Exp_file_section)):
            if case == 1:
                parser.add_section(p4R.Exp_file_section[i])
            k = nunberofdatapersection[i]
            r = nunberofdatapersection[i+1]
            new_section_name = new_section_name[k:]
            for l in range(r):
                parser.set(p4R.Exp_file_section[i], new_section_name[l],
                           str(a.AllDataDict[new_section_name[l]]))
        parser.write(open(filename_, 'w'))

    def on_update_config_file(self, filename, data, sequence):
        parser = SafeConfigParser()
        parser.read(filename)
        if sequence == 'project_folder':
            parser.set(p4R.Radmax_File_section[1], p4R.s_radmax_2[0], data)
        elif sequence == 'DW_folder':
            parser.set(p4R.Radmax_File_section[1], p4R.s_radmax_2[1], data)
        elif sequence == 'Strain_folder':
            parser.set(p4R.Radmax_File_section[1], p4R.s_radmax_2[2], data)
        elif sequence == 'XRD_folder':
            parser.set(p4R.Radmax_File_section[1], p4R.s_radmax_2[3], data)
        elif sequence == 'Save_as_folder':
            parser.set(p4R.Radmax_File_section[1], p4R.s_radmax_2[4], data)
        parser.write(open(filename, 'w'))

    def on_makingof_config_file(self, filename):
        nunberofdatapersection = [0, len(p4R.s_radmax_1),
                                  len(p4R.s_radmax_2),
                                  len(p4R.s_radmax_3),
                                  len(p4R.s_radmax_4),
                                  len(p4R.s_radmax_5),
                                  len(p4R.s_radmax_6),
                                  len(p4R.s_radmax_7),
                                  len(p4R.s_radmax_8)]
        pathini = [os.path.split(filename)[0]]*5
        data2ini = [p4R.Application_version, p4R.last_modification] + pathini
        parser = SafeConfigParser()
        new_section_name = p4R.Radmax_all_section
        Initial_data = dict(zip(p4R.Radmax_all_section, data2ini))
        Initial_data.update(p4R.FitParamDefault)
        for i in range(len(p4R.Radmax_File_section)):
            parser.add_section(p4R.Radmax_File_section[i])
            k = nunberofdatapersection[i]
            r = nunberofdatapersection[i+1]
            new_section_name = new_section_name[k:]
            for l in range(r):
                parser.set(p4R.Radmax_File_section[i], new_section_name[l],
                           str(Initial_data[new_section_name[l]]))
        parser.write(open(filename, 'w'))
        a = ReadFile()
        a.on_read_init_parameters(os.path.join(p4R.current_dir, filename),
                                  p4R.RadmaxFile)

    def on_update_config_file_parameters(self, filename):
        a = P4Rm()
        parser = SafeConfigParser()
        parser.read(filename)
        for name in p4R.s_radmax_3:
            parser.set(p4R.Radmax_File_section[2], name, str(a.DefaultDict[name]))
        for name in p4R.s_radmax_4:
            parser.set(p4R.Radmax_File_section[3], name, str(a.DefaultDict[name]))
        for name in p4R.s_radmax_5:
            parser.set(p4R.Radmax_File_section[4], name, str(a.DefaultDict[name]))
        for name in p4R.s_radmax_6:
            parser.set(p4R.Radmax_File_section[5], name, str(a.DefaultDict[name]))
        for name in p4R.s_radmax_7:
            parser.set(p4R.Radmax_File_section[6], name, str(a.DefaultDict[name]))
        for name in p4R.s_radmax_8:
            parser.set(p4R.Radmax_File_section[7], name, str(a.DefaultDict[name]))
        parser.write(open(filename, 'w'))

    def save_deformation(self, case, name, data, supp=None):
        a = P4Rm()
        if a.PathDict['project_name'] == "":
            name_ = 'temp_' + '_input_' + name + '_coeff.txt'
            path = os.path.join(a.PathDict[case], name_)
        else:
            name_ = (a.PathDict['project_name'] + '_input_' +
                     name + '_coeff.txt')
            path = os.path.join(a.DefaultDict['Save_as_folder'], name_)
            if supp == 1:
                name_ = 'temp_' + '_input_' + name + '_coeff.txt'
                path2remove = os.path.join(a.PathDict[case], name_)
                if os.path.isfile(path2remove):
                    os.remove(path2remove)
        P4Rm.PathDict[case] = path
        savetxt(path, data, fmt='%10.8f')

    def save_drx(self, case):
        a = P4Rm()
        name = a.PathDict['project_name'] + '.txt'
        path = os.path.join(a.DefaultDict['Save_as_folder'], name)
        P4Rm.PathDict[case] = path
        data = column_stack((2*a.ParamDict['th']*180/pi,
                             a.ParamDict['Iobs']))
        savetxt(path, data, fmt='%10.8f')

    def on_save_project(self, case, paths=None):
        """
        Saving project, save or save as depending of the action
        """
        a = P4Rm()
        pub.sendMessage(pubsub_Read_field4Save)

        if (a.checkInitialField is 1 and a.checkGeometryField is 1 and
            a.checkFittingField is 1):
            P4Rm.allparameters = (a.initial_parameters +
                                      a.fitting_parameters +
                                      a.sample_geometry)
            i = 0
            for k in p4R.IP_p + p4R.F_p + p4R.SG_p:
                P4Rm.AllDataDict[k] = a.allparameters[i]
                i += 1
            if (a.PathDict['DW_file'] is not "" or
                a.PathDict['Strain_file'] is not "" or
                a.PathDict['XRD_file'] is not ""):
                
                if case is 1:
                    P4Rm.DefaultDict['Save_as_folder'] = os.path.split(paths[0])[0]
                    
                    self.on_update_config_file(os.path.join(p4R.current_dir,
                                               p4R.filename + '.ini'), 
                                               a.DefaultDict['Save_as_folder'],
                                               'Save_as_folder')
                    P4Rm.PathDict['path2ini'] = os.path.split(paths[0])[0]
                    if _platform == "linux" or _platform == "linux2":
                        P4Rm.PathDict['path2inicomplete'] = paths[0] + '.ini'
                    elif _platform == "win32":
                        P4Rm.PathDict['path2inicomplete'] = paths[0]
                    P4Rm.PathDict['namefromini'] = os.path.splitext(os.path.basename(paths[0]))[0]
                P4Rm.PathDict['project_name'] = a.PathDict['namefromini']         

                self.save_deformation('Strain_file', 'strain',
                                      a.ParamDict['sp'], 1)
                self.save_deformation('DW_file', 'DW', a.ParamDict['dwp'], 1)
                if a.pathfromDB == 1:
                    self.save_drx('XRD_file')

                P4Rm.AllDataDict['crystal_name'] = a.PathDict['Compound_name']
                P4Rm.AllDataDict['substrate_name'] = a.PathDict['substrate_name']
                P4Rm.AllDataDict['input_dw'] = a.PathDict['DW_file']
                P4Rm.AllDataDict['input_strain'] = a.PathDict['Strain_file']
                P4Rm.AllDataDict['xrd_data'] = a.PathDict['XRD_file']
                self.save_project(case)
                pub.sendMessage(pubsub_changeColor_field4Save, color='#CCE5FF')
                sleep(0.8)
                pub.sendMessage(pubsub_changeColor_field4Save, color='#white')
                msg_ = ("Data have been saved to " +
                        a.PathDict['path2inicomplete'])
                logger.log(logging.INFO, msg_)

                pub.sendMessage(pubsub_ChangeFrameTitle,
                                NewTitle=p4R.Application_name + " - " +
                                a.PathDict['namefromini'])

    def on_save_from_fit(self):
        a = P4Rm()
        if a.PathDict['path2ini'] != '':
            path = a.PathDict['path2ini']
        else:
            path = a.PathDict['path2drx']
        try:
            header = ["2theta", "Iobs", "Icalc"]
            line = u'{:^12} {:^24} {:^12}'.format(*header)

            # -----------------------------------------------------------------
            name_ = (a.PathDict['namefromini'] + '_' +
                     p4R.output_name['out_strain_profile'])
            data_ = column_stack((a.ParamDict['depth'],
                                  a.ParamDict['strain_i']))
            savetxt(os.path.join(path, name_), data_, fmt='%10.8f')
            # -----------------------------------------------------------------
            name_ = (a.PathDict['namefromini'] + '_' +
                     p4R.output_name['out_dw_profile'])
            data_ = column_stack((a.ParamDict['depth'],
                                  a.ParamDict['DW_i']))
            savetxt(os.path.join(path, name_), data_, fmt='%10.8f')
            # -----------------------------------------------------------------
            if a.par_fit == []:
                # -------------------------------------------------------------
                name_ = (a.PathDict['namefromini'] + '_' +
                         p4R.output_name['out_strain'])
                data_ = a.ParamDict['sp']
                savetxt(os.path.join(path, name_),  data_, fmt='%10.8f')
                # -------------------------------------------------------------
                name_ = (a.PathDict['namefromini'] + '_' +
                         p4R.output_name['out_dw'])
                data_ = a.ParamDict['dwp']
                savetxt(os.path.join(path, name_), data_, fmt='%10.8f')
            else:
                # -------------------------------------------------------------
                name_ = (a.PathDict['namefromini'] + '_' +
                         p4R.output_name['out_strain'])
                data_ = a.par_fit[:int(a.AllDataDict['strain_basis_func'])]
                savetxt(os.path.join(path, name_), data_, fmt='%10.8f')
                # -------------------------------------------------------------
                name_ = (a.PathDict['namefromini'] + '_' +
                         p4R.output_name['out_dw'])
                data_ = a.par_fit[-1*int(a.AllDataDict['dw_basis_func']):]
                savetxt(os.path.join(path, name_), data_, fmt='%10.8f')
            # -----------------------------------------------------------------
            name_ = (a.PathDict['namefromini'] + '_' + p4R.output_name['out_XRD'])
            data_ = column_stack((a.ParamDict['th4live'], a.ParamDict['Iobs'],
                                  a.ParamDict['I_fit']))
            savetxt(os.path.join(path, name_), data_, header=line,
                    fmt='{:^12}'.format('%3.8f'))
            # -----------------------------------------------------------------
            logger.log(logging.INFO, "Data have been saved successfully")
        except IOError:
            msg = "Impossible to save data to file, please check your path !!"
            logger.log(logging.WARNING, msg)
