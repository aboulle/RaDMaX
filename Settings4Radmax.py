#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

# =============================================================================
# Settings module
# =============================================================================


import os
import wx
import string

import Parameters4Radmax as p4R
from Parameters4Radmax import P4Rm

from Icon4Radmax import prog_icon

from threading import Thread

from sys import platform as _platform

import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger(__name__)

if 'phoenix' in wx.PlatformInfo:
    from wx import Validator as Validator
else:
    from wx import PyValidator as Validator

LEVELS = [
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL
]

ALPHA_ONLY = 1
DIGIT_ONLY = 2

Live_COUNT = wx.NewEventType()
LiveLimitExceeded_COUNT = wx.NewEventType()
Live_count_NbCycle = wx.NewEventType()
EVT_Live_COUNT = wx.PyEventBinder(Live_COUNT, 1)
EVT_LiveLimitExceeded_COUNT = wx.PyEventBinder(LiveLimitExceeded_COUNT, 1)
EVT_Live_count_NbCycle = wx.PyEventBinder(Live_count_NbCycle, 1)


# -----------------------------------------------------------------------------
class LogWindow(wx.Frame):
    """
    Creation of the log window
    we use the 'log_window_status' variable to ensure that only one instance of
    the window in launch at one time
    """
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, p4R.Application_name +
                          " - log window")
        wx.Frame.CenterOnScreen(self)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.SetIcon(prog_icon.GetIcon())
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._logFileContents = wx.TextCtrl(self, wx.ID_ANY, size=(600, 300),
                                            style=wx.TE_MULTILINE |
                                            wx.TE_READONLY | wx.VSCROLL)

        self.updateButton = wx.Button(self, wx.ID_ANY, label="Update")

        sizer.Add(self._logFileContents, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.updateButton, 0, wx.ALL | wx.EXPAND, 5)
        self.Bind(wx.EVT_BUTTON, self.on_update, self.updateButton)
        self.SetSizer(sizer)
        self.update()
        self.Layout()
        self.Fit()

    def update(self):
        with open(p4R.log_file_path, "r") as f:
            self._logFileContents.SetValue(f.read())

    def on_update(self, event):
        self.update()

    def onClose(self, event):
        P4Rm.log_window_status = False
        self.Destroy()
        event.Skip()


# -----------------------------------------------------------------------------
class LogSaver():
    """
    class used all along the modules to record the information available
    """
    # création de l'objet logger qui va nous servir à écrire dans les logs
    logger = logging.getLogger()
    # on met le niveau du logger à DEBUG, comme ça il écrit tout
    logger.setLevel(logging.DEBUG)

    # création d'un formateur qui va ajouter le temps, le niveau
    # de chaque message quand on écrira un message dans le log
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s ::' +
                                  '%(message)s')
    # création d'un handler qui va rediriger une écriture du log vers
    # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
    file_handler = RotatingFileHandler(p4R.log_file_path, 'a', 1000000, 1)
    # on lui met le niveau sur DEBUG,
    #        on lui dit qu'il doit utiliser le formateur
    # créé précédement et on ajoute ce handler au logger
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# -----------------------------------------------------------------------------
class WxTextCtrlHandler(logging.Handler):
    """
    Redirect the logger to a wxPython textCtrl
    """
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        s = self.format(record) + '\n'
        wx.CallAfter(self.ctrl.WriteText, s)


# -----------------------------------------------------------------------------
class TextValidator(Validator):
    """
    Used to test in the character enter in the textctrl are the one desired
    (letters, digits or punctuations)
    """
    def __init__(self, flag=None, pyVar=None):
        Validator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return TextValidator(self.flag)

    def Validate_Point_Coma(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        temp = []
        for x in val:
            if x == '.' or x == ',':
                temp.append(True)
            else:
                temp.append(False)
        if True in temp:
            return True
        else:
            return False

    def Validate_Sign(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        temp = []
        for x in val:
            if x == '-':
                temp.append(True)
            else:
                temp.append(False)
        if True in temp:
            return True
        else:
            return False

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if self.flag == ALPHA_ONLY and chr(key) in string.letters:
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in string.digits:
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in "eE":
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in ".,":
            test = self.Validate_Point_Coma(self)
            if test is False:
                event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in "-":
            test = self.Validate_Sign(self)
            if test is False:
                event.Skip()
            return

        if 'phoenix' in wx.PlatformInfo:
            if not wx.Validator.IsSilent():
                wx.Bell()
        else:
            if not wx.Validator_IsSilent():
                wx.Bell()
        return


# -----------------------------------------------------------------------------
class Sound_Launcher(Thread):
    def __init__(self, parent, case, random_music):
        Thread.__init__(self)
        self.case = case
        self.random_music = random_music
        self.start()

    def run(self):

        l_1 = [2, 18, 106, 107]
        l_2 = [99, 199]
        load_voice = ['Radmax_emma', 'Radmax_harry',
                      'Radmax_All_emma', 'Radmax_All_harry']
#       1=owin31, 2=Icq, 3=The_End
        if self.case == 0:
            if self.random_music in l_1:
                path2music = os.path.join(p4R.music_path, 'song_3.wav')
            elif self.random_music in l_2:
                path2music = os.path.join(p4R.music_path, 'song_1.wav')
            else:
                path2music = os.path.join(p4R.music_path, 'song_2.wav')
        elif self.case == 1:
            return
        elif self.case == 2:
            path2music = os.path.join(p4R.music_path,
                                      load_voice[self.random_music] + '.wav')

        if _platform == "linux" or _platform == "linux2":
            import subprocess
            subprocess.Popen(['aplay', path2music],
                             stdin=None, stdout=None,
                             stderr=None)
        elif _platform == 'darwin':
            import subprocess
            subprocess.Popen(['afplay', path2music],
                             stdin=None, stdout=None,
                             stderr=None)
        else:
            from playsound import playsound
            playsound(path2music, block=False)
