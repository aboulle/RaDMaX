#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

'''
*Radmax Initial Parameters module*
'''

from Parameters4Radmax import *
from ConfigParser import SafeConfigParser

lecture_fichier = []
floatconv = []
result_values = []


# -----------------------------------------------------------------------------
class ReadFile(wx.Panel):
    """
    Reading '.ini' project
    Test if the config file has the waiting structure
    if not, the project can't be launch, and a warning is write in the log file
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY)
        self.section_name = []
        self.structure_section = []
        P4Radmax.old_file_version = 0
        self.Fit()

    def on_read_init_parameters(self, filename, choice):
        if choice == 'ConfigFile':
            self.section_name = Config_File_all_section
            self.structure_section = Config_File_section
        elif choice == 'ConfigDataFile':
            self.section_name = Config_DataFile_all_section
            self.structure_section = Config_DataFile_section
        if not os.path.exists(filename):
            _msg = "! Pay attention, the config file does not exist: "
            logger.log(logging.WARNING, _msg + str(filename))
            if choice == 'ConfigFile':
                _msg = "Making of the config file with initial parameters"
                logger.log(logging.WARNING, _msg + str(filename))
                a = SaveFile4Diff(self)
                a.on_makingof_config_file(filename)
        else:
            result_values[:] = []
            _msg = "Trying to load the following config file: "
            logger.log(logging.INFO, _msg + str(filename))
            if choice == 'ConfigDataFile':
                self.test_data_file(filename)
            self.test_existence_section(filename)

    def test_existence_section(self, filename):
        test_true_false = []
        parser = SafeConfigParser(allow_no_value=True)
        try:
            parser.read(filename)
        except ConfigParser.MissingSectionHeaderError:
            print ("\n! Config file structure is not correct," +
                   "please check your config file !!")
            exit(1)
        for nameofsection in self.structure_section:
            var = parser.has_section(nameofsection)
            test_true_false.append(var)
        indices_section = self.all_indices(False, test_true_false)
        if indices_section != []:
            print "\n! Check your config file!"
            print 'The following sections are not being present:'
            for char in indices_section:
                print self.structure_section[char]
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
            print "\n! Check your config file!"
            print 'The following options are not being present:'
            for chare in difference:
                print chare

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
            print "\n! Check your config file!"
            print "Value of option section are not being present:"
            logger.log(logging.WARNING, "Check your config file!")
            logger.log(logging.WARNING, "Value of option section are" +
                       "not being present:")
            for chare in nulle:
                print section_name[chare]
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
            skip_line = 39
            [next(f) for x in xrange(skip_line)]
            header = next(f)
            mline = ""
            for i in header:
                mline += i
            ll = mline.split()
            if ll[0] == 'strain_min':
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
        with open(name, 'r') as f:
            for line in self.nonblank_lines(f):
                if line[0] is not '[':
                    ll = line.split(' = ')
                    ll_0.append(ll[0])
                    ll_1.append(ll[1])
        i = 0
        P4Radmax.AllDataDict['model'] = 0.0
        for k in ll_0:
            P4Radmax.AllDataDict[k] = ll_1[i]
            i += 1
        for k, v in FitParamDefault.items():
            try:
                P4Radmax.AllDataDict[k] = FitParamDefault[k]
                i += 1
            except (IndexError):
                break
        data_path = os.path.split(name)[0]
        data_file_name = os.path.splitext(os.path.basename(name))[0]
        data_name = os.path.join(data_path, data_file_name + '.ini')
        P4Radmax.PathDict['path2inicomplete'] = data_name
        b = SaveFile4Diff(self)
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
            P4Radmax.ParamDict['dwp'] = loadtxt(filename_)
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
            P4Radmax.ParamDict['sp'] = loadtxt(filename_)
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
            P4Radmax.ParamDict['data_xrd'] = loadtxt(filename_, unpack=True)
            return 0
        except (IOError):
            logger.log(logging.ERROR, "!!! .txt data file is not present !!!")
        except (IndexError):
            logger.log(logging.ERROR, "!!! The number of columns in the" +
                       "file is not correct !!!")


# -----------------------------------------------------------------------------
class SaveFile4Diff(wx.Panel):
    """
    Save the project in a '.ini' file
    several method are available, create a new file, update an existing file
    or making the 'RaDMax.ini' config file
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY)
        self.Fit()

    def save_project(self, case):
        nunberofdatapersection = [0, len(structure_Crystal),
                                  len(structure_Data_filename),
                                  len(structure_Experiment),
                                  len(structure_Material),
                                  len(structure_Strain_and_DW),
                                  len(structure_GSA_options),
                                  len(Config_File_section_4),
                                  len(Config_File_section_3),
                                  len(Config_File_section_5),
                                  len(Config_File_section_6)]
        a = P4Radmax()
        filename_ = a.PathDict['path2inicomplete']
        parser = SafeConfigParser()
        if case == 0:
            parser.read(filename_)
        new_section_name = Config_DataFile_all_section
        for i in range(len(Config_DataFile_section)):
            if case == 1:
                parser.add_section(Config_DataFile_section[i])
            k = nunberofdatapersection[i]
            r = nunberofdatapersection[i+1]
            new_section_name = new_section_name[k:]
            for l in range(r):
                parser.set(Config_DataFile_section[i], new_section_name[l],
                           str(a.AllDataDict[new_section_name[l]]))
        parser.write(open(filename_, 'w'))

    def on_update_config_file(self, filename, data, sequence):
        parser = SafeConfigParser()
        parser.read(filename)
        if sequence == 'project_file':
            parser.set(Config_File_section[1], Config_File_section_2[0], data)
        elif sequence == 'DW_file':
            parser.set(Config_File_section[1], Config_File_section_2[1], data)
        elif sequence == 'Strain_file':
            parser.set(Config_File_section[1], Config_File_section_2[2], data)
        elif sequence == 'XRD_file':
            parser.set(Config_File_section[1], Config_File_section_2[3], data)
        elif sequence == 'Save_as_file':
            parser.set(Config_File_section[1], Config_File_section_2[4], data)
        parser.write(open(filename, 'w'))

    def on_makingof_config_file(self, filename):
        nunberofdatapersection = [0, len(Config_File_section_1),
                                  len(Config_File_section_2),
                                  len(Config_File_section_3),
                                  len(Config_File_section_4),
                                  len(Config_File_section_5),
                                  len(Config_File_section_6)]
        pathini = [os.path.split(filename)[0]]*5
        data2ini = [Application_version, last_modification] + pathini
        parser = SafeConfigParser()
        new_section_name = Config_File_all_section
        Initial_data = dict(zip(Config_File_all_section, data2ini))
        Initial_data.update(FitParamDefault)
        for i in range(len(Config_File_section)):
            parser.add_section(Config_File_section[i])
            k = nunberofdatapersection[i]
            r = nunberofdatapersection[i+1]
            new_section_name = new_section_name[k:]
            for l in range(r):
                parser.set(Config_File_section[i], new_section_name[l],
                           str(Initial_data[new_section_name[l]]))
        parser.write(open(filename, 'w'))
        a = ReadFile(self)
        a.on_read_init_parameters(os.path.join(current_dir, filename),
                                  ConfigFile)

    def on_update_config_file_parameters(self, filename):
        a = P4Radmax()
        parser = SafeConfigParser()
        parser.read(filename)
        for name in Config_File_section_3:
            parser.set(Config_File_section[2], name, str(a.DefaultDict[name]))
        for name in Config_File_section_4:
            parser.set(Config_File_section[3], name, str(a.DefaultDict[name]))
        for name in Config_File_section_5:
            parser.set(Config_File_section[4], name, str(a.DefaultDict[name]))
        for name in Config_File_section_6:
            parser.set(Config_File_section[5], name, str(a.DefaultDict[name]))
        parser.write(open(filename, 'w'))
