#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: A_BOULLE & M_SOUILAH
# Radmax project

'''
*Radmax Graph module*
'''

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.lines import Line2D
from matplotlib.artist import Artist
from matplotlib.patches import Polygon

from Parameters4Radmax import *

"""Pubsub message"""
pubsub_draw_graph = "DrawGraph"
pubsub_Draw_XRD = "DrawXRD"
pubsub_Draw_Strain = "DrawStrain"
pubsub_Draw_DW = "DrawDW"
pubsub_Draw_Fit_Live_XRD = "DrawFitLiveXRD"
pubsub_Update_Fit_Live = "UpdateFitLive"
pubsub_Re_Read_field_paramters_panel = "ReReadParametersPanel"
pubsub_OnFit_Graph = "OnFitGraph"
pubsub_Update_Scale_Strain = "OnUpdateScaleStrain"
pubsub_Update_Scale_DW = "OnUpdateScaleDW"
pubsub_Permute_Graph = "PermuteGrpah"

colorBackgroundGraph = '#F0F0F0'

font = {'family': 'serif',
        'color': 'darkred',
        'weight': 'normal',
        'size': 14,
        }


# ------------------------------------------------------------------------------
class GraphPanel(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar

        mastersizer = wx.BoxSizer(wx.HORIZONTAL)

        size_Strain_DW_Box = (500, 500)
        size_XRD_Box = (300, 140)
        fontStaticBox = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)

        Graph_Strain_DW_box = wx.StaticBox(self, -1,
                                           " Strain and DW profiles ",
                                           size=size_Strain_DW_Box)
        Graph_Strain_DW_box.SetFont(fontStaticBox)
        Graph_Strain_DW_box_sizer = wx.StaticBoxSizer(Graph_Strain_DW_box,
                                                      wx.VERTICAL)
        self.in_Graph_Strain_DW_box_sizer = wx.GridBagSizer(hgap=1, vgap=2)
        self.in_Graph_Strain_DW_box_sizer_Pv = wx.GridBagSizer(hgap=1, vgap=2)

        Graph_XRD_box = wx.StaticBox(self, -1,
                                     " XRD profile ", size=size_XRD_Box)
        Graph_XRD_box.SetFont(fontStaticBox)
        Graph_XRD_box_sizer = wx.StaticBoxSizer(Graph_XRD_box, wx.VERTICAL)
        in_Graph_XRD_box_sizer = wx.GridBagSizer(hgap=1, vgap=1)

        panelOne = LeftGraphTop(self, self.statusbar)
        panelTwo = LeftGraphBottom(self, self.statusbar)
        panelThree = RightGraph(self, self.statusbar)

        in_Graph_XRD_box_sizer.Add(panelThree, pos=(0, 0))
        Graph_XRD_box_sizer.Add(in_Graph_XRD_box_sizer, 0, wx.ALL, 5)

        self.in_Graph_Strain_DW_box_sizer.Add(panelOne, pos=(0, 0))
        self.in_Graph_Strain_DW_box_sizer.Add(panelTwo, pos=(1, 0))
        Graph_Strain_DW_box_sizer.Add(self.in_Graph_Strain_DW_box_sizer,
                                      0, wx.ALL, 5)

        mastersizer.Add(Graph_Strain_DW_box_sizer, 0, wx.ALL, 5)
        mastersizer.Add(Graph_XRD_box_sizer, 0, wx.ALL, 5)

        pub.subscribe(self.OnPermuteGraph, pubsub_Permute_Graph)

        self.SetSizer(mastersizer)
        self.Fit()
        self.Layout()

    def OnPermuteGraph(self, choice):
        if choice == 0:
            self.in_Graph_Strain_DW_box_sizer.Show(True)
        elif choice == 1:
            self.in_Graph_Strain_DW_box_sizer.Show(True)
        self.Fit()
        self.Layout()


# ------------------------------------------------------------------------------
class LeftGraphTop(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar
        """
        An polygon editor.
        Key-bindings
          't' toggle vertex markers on and off.  When vertex markers are on,
              you can move them, delete them
          'd' delete the vertex under point
          'i' insert a vertex at point.  You must be within epsilon of the
              line connecting two existing vertices
        """
        mastersizer = wx.BoxSizer(wx.VERTICAL)

        self.fig = Figure((6.0, 3.0))
        self.canvas = FigCanvas(self, -1, self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("Strain", fontdict=font)
        self.ax.set_xlabel("Depth ($\AA$)", fontdict=font)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Hide()
        self.fig.patch.set_facecolor(colorBackgroundGraph)

        self._ind = None  # the active vert
        self.poly = []
        self.line = []
        self.showverts = True
        self.epsilon = 5   # max pixel distance to count as a vertex hit
        self.new_coord = {'indice': 0, 'x': 0, 'y': 0}
        self.modelpv = False
        self.u_key_press = False

        xs = [-1]
        ys = [-1]
        poly = Polygon(list(zip(xs, ys)),
                       fill=False, closed=False, animated=True)
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])
        self.draw_c(poly, xs, ys)

        self.canvas.mpl_connect('draw_event',
                                self.draw_callback)
        self.canvas.mpl_connect('button_press_event',
                                self.button_press_callback)
        self.canvas.mpl_connect('button_release_event',
                                self.button_release_callback)
        self.canvas.mpl_connect('scroll_event',
                                self.scroll_callback)
        self.canvas.mpl_connect('motion_notify_event',
                                self.motion_notify_callback)
        self.canvas.mpl_connect('motion_notify_event',
                                self.on_update_coordinate)
        self.press = None
        mastersizer.Add(self.canvas, 1, wx.ALL)
        mastersizer.Add(self.toolbar, 1, wx.ALL)
        pub.subscribe(self.OnDrawGraph, pubsub_Draw_Strain)
        pub.subscribe(self.scale_manual, pubsub_Update_Scale_Strain)

        self.SetSizer(mastersizer)
        self.Raise()
        self.SetPosition((0, 0))
        self.Fit()

    def OnDrawGraph(self, b=None):
        a = P4Radmax()
        self.modelpv = a.modelPv
        self.ax.clear()
        if b != 2:
            x_sp = a.ParamDict['x_sp']
            y_sp = a.ParamDict['strain_shifted']
            xs = deepcopy(a.ParamDict['depth'])
            ys = deepcopy(a.ParamDict['strain_i']*100)
            P4Radmax.DragDrop_Strain_x = x_sp
            P4Radmax.DragDrop_Strain_y = y_sp
            ymin = min(ys) - min(ys)*10/100
            ymax = max(ys) + max(ys)*10/100
            self.ax.set_ylim([ymin, ymax])
        elif b == 2:
            x_sp = [-1]
            y_sp = [-1]
            xs = [-1]
            ys = [-1]
            self.ax.set_xlim([0, 1])
            self.ax.set_ylim([-1, 1])
        poly = Polygon(list(zip(x_sp, y_sp)), lw=0, ls='dashdot', color='g',
                       fill=False, closed=False, animated=True)
        if self.modelpv is True:
            P4Radmax.ParamDict['sp_pv_backup'] = a.ParamDict['sp']
        self.draw_c(poly, xs, ys)

    def draw_c(self, data, x, y):
        self.ax.plot(x[1:], y[1:], 'g', lw=2.)
        self.ax.set_ylabel("Strain", fontdict=font)
        self.ax.set_xticklabels([])
        self.poly = data
        xs, ys = zip(*self.poly.xy)
        self.line = Line2D(xs, ys, lw=0, ls='-.', color='g', marker='.', ms=32,
                           markerfacecolor='g', markeredgecolor='k', mew=1.0)
        self.ax.add_line(self.line)
        self.ax.add_patch(self.poly)
        self.canvas.draw()
        self.Update()

    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def poly_changed(self, poly):
        'this method is called whenever the polygon object is called'
        # only copy the artist props to the line (except visibility)
        vis = self.line.get_visible()
        Artist.update_from(self.line, poly)
        self.line.set_visible(vis)  # don't use the poly visibility state

    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'

        # display coords
        xy = np.asarray(self.poly.xy)
        xyt = self.poly.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]
        if d[ind] >= self.epsilon:
            ind = None
        return ind

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if self.canvas.HasCapture():
            self.canvas.ReleaseMouse()
            if not self.showverts:
                return
            if event.inaxes is None:
                return
            if event.button != 1:
                return
            self._ind = self.get_ind_under_point(event)
            self.new_coord['indice'] = self._ind

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if self.canvas.HasCapture():
            self.canvas.ReleaseMouse()
        else:
            if not self.showverts:
                return
            if event.button != 1:
                return
            if self.new_coord['indice'] is not None:
                a = P4Radmax()
                temp_1 = self.new_coord['y']
                temp_2 = self.new_coord['x']
                P4Radmax.DragDrop_Strain_y[self.new_coord['indice']] = temp_1
                P4Radmax.DragDrop_Strain_x[self.new_coord['indice']] = temp_2
                if self.modelpv is True:
                    t_temp = a.ParamDict['depth'] + a.ParamDict['z']
                    t = t_temp[0]
                    sp_temp = range(7)
                    sp_temp[0] = a.DragDrop_Strain_y[0]
                    sp_temp[1] = 1 - a.DragDrop_Strain_x[0]/t
                    sp_temp[2] = 2*(-1 + a.ParamDict['sp'][1] +
                                    a.DragDrop_Strain_x[1]/t)
                    sp_temp[3] = 2*(1 - a.ParamDict['sp'][1] -
                                    1*a.DragDrop_Strain_x[2]/t)
                    sp_temp[4] = a.ParamDict['sp'][4]
                    sp_temp[5] = a.ParamDict['sp'][5]
                    sp_temp[6] = a.DragDrop_Strain_y[3]
                    P4Radmax.ParamDict['sp'] = deepcopy(sp_temp)
                    P4Radmax.ParamDictbackup['sp'] = deepcopy(sp_temp)
                    P4Radmax.ParamDict['sp_pv'] = deepcopy(sp_temp)
                else:
                    temp = self.new_coord['y']
                    P4Radmax.DragDrop_Strain_y[self.new_coord['indice']] = temp
                    temp = [strain*scale/100 for strain, scale in
                            zip(a.DragDrop_Strain_y,
                                a.ParamDict['scale_strain'])]
                    temp = [float(format(val, '.8f')) for val in temp]
                    temp1 = temp[1:]
                    temp2 = [a.ParamDict['stain_out']]
                    temp3 = deepcopy(np.concatenate((temp1, temp2), axis=0))
                    P4Radmax.ParamDict['sp'] = temp3
                    P4Radmax.ParamDictbackup['sp'] = temp3

                pub.sendMessage(pubsub_Update_Fit_Live)
            self._ind = None

    def scroll_callback(self, event):
        if not event.inaxes:
            return
        a = P4Radmax()
        if event.key == 'u' and event.button == 'up':
            temp = a.ParamDict['strain_multiplication'] + 0.01
            P4Radmax.ParamDict['strain_multiplication'] = temp
        elif event.key == 'u' and event.button == 'down':
            temp = a.ParamDict['strain_multiplication'] - 0.01
            P4Radmax.ParamDict['strain_multiplication'] = temp
        temp_1 = a.ParamDictbackup['sp']
        temp_2 = a.ParamDict['strain_multiplication']
        P4Radmax.ParamDict['sp'] = multiply(temp_1, temp_2)
        pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)

    def scale_manual(self, event, val=None):
        a = P4Radmax()
        if val is not None:
            P4Radmax.ParamDict['strain_multiplication'] = val
        temp_1 = a.ParamDict['sp']
        temp_2 = a.ParamDict['strain_multiplication']
        P4Radmax.ParamDict['sp'] = multiply(temp_1, temp_2)
        pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)

    def motion_notify_callback(self, event):
        'on mouse movement'
        a = P4Radmax()
        if not self.showverts:
            return
        if self._ind is None:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        if self.modelpv is True:
            if self._ind == 0:
                y = event.ydata
                x = event.xdata
            elif self._ind == 1 or self._ind == 2:
                y = a.DragDrop_Strain_y[self.new_coord['indice']]
                x = event.xdata
            else:
                x = a.DragDrop_Strain_x[self.new_coord['indice']]
                y = event.ydata
        else:
            y = event.ydata
            x = a.DragDrop_Strain_x[self.new_coord['indice']]
        self.new_coord['x'] = x
        self.new_coord['y'] = y

        self.poly.xy[self._ind] = x, y
        self.line.set_data(zip(*self.poly.xy))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def on_update_coordinate(self, event):
        if event.inaxes is None:
            self.statusbar.SetStatusText(u"", 1)
            self.statusbar.SetStatusText(u"", 2)
        else:
            x, y = event.xdata, event.ydata
            xfloat = round(float(x), 2)
            yfloat = round(float(y), 2)
            self.statusbar.SetStatusText(u"x = " + str(xfloat), 1)
            self.statusbar.SetStatusText(u"y = " + str(yfloat), 2)

            xy = np.asarray(self.poly.xy)
            xyt = self.poly.get_transform().transform(xy)
            xt, yt = xyt[:, 0], xyt[:, 1]
            d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
            indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
            ind = indseq[0]

            if d[ind] >= self.epsilon:
                self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            elif d[ind] <= self.epsilon:
                self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_HAND))


# ------------------------------------------------------------------------------
class LeftGraphBottom(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar
        """
        An polygon editor.
        Key-bindings
          't' toggle vertex markers on and off.  When vertex markers are on,
              you can move them, delete them
          'd' delete the vertex under point
          'i' insert a vertex at point.  You must be within epsilon of the
              line connecting two existing vertices
        """
        mastersizer = wx.BoxSizer(wx.VERTICAL)
        self.fig = Figure((6.0, 3.0))
        self.canvas = FigCanvas(self, -1, self.fig)
        self.ax = self.fig.add_subplot(111)
        """ subplots_adjust(bottom=0.14): permet d'ajuster la taille du canevas
        en prenant en compte la legende
        sinon la legende est rognee"""
        self.fig.subplots_adjust(bottom=0.20)
        self.ax.set_ylabel("DW", fontdict=font)
        self.ax.set_xlabel("Depth ($\AA$)", fontdict=font)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Hide()
        self.fig.patch.set_facecolor(colorBackgroundGraph)

        self._ind = None  # the active vert
        self.poly = []
        self.line = []
        self.showverts = True
        self.epsilon = 5  # max pixel distance to count as a vertex hit
        self.new_coord = {'indice': 0, 'x': 0, 'y': 0}
        self.u_key_press = True
        self.modelpv = False

        xs = [-1]
        ys = [-1]
        poly = Polygon(list(zip(xs, ys)),
                       fill=False, closed=False, animated=True)
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])
        self.draw_c(poly, xs, ys)

        self.canvas.mpl_connect('draw_event',
                                self.draw_callback)
        self.canvas.mpl_connect('button_press_event',
                                self.button_press_callback)
        self.canvas.mpl_connect('button_release_event',
                                self.button_release_callback)
        self.canvas.mpl_connect('motion_notify_event',
                                self.motion_notify_callback)
        self.canvas.mpl_connect('scroll_event',
                                self.scroll_callback)
        self.canvas.mpl_connect('motion_notify_event',
                                self.on_update_coordinate)
        mastersizer.Add(self.canvas, 1, wx.ALL)
        mastersizer.Add(self.toolbar, 1, wx.ALL)

        pub.subscribe(self.draw_c, pubsub_draw_graph)
        pub.subscribe(self.OnDrawGraph, pubsub_Draw_DW)
        pub.subscribe(self.scale_manual, pubsub_Update_Scale_DW)

        self.SetSizer(mastersizer)
        self.Raise()
        self.SetPosition((0, 0))
        self.Fit()

    def OnDrawGraph(self, b=None):
        a = P4Radmax()
        self.modelpv = a.modelPv
        self.ax.clear()
        if b != 2:
            x_dwp = a.ParamDict['x_dwp']
            y_dwp = a.ParamDict['DW_shifted']
            xs = deepcopy(a.ParamDict['depth'])
            ys = deepcopy(a.ParamDict['DW_i'])
            P4Radmax.DragDrop_DW_x = x_dwp
            P4Radmax.DragDrop_DW_y = y_dwp
            ymin = min(ys) - min(ys)*10/100
            ymax = max(ys) + max(ys)*10/100
            self.ax.set_ylim([ymin, ymax])
        elif b == 2:
            x_dwp = [-1]
            y_dwp = [-1]
            xs = [-1]
            ys = [-1]
            self.ax.set_xlim([0, 1])
            self.ax.set_ylim([0, 1])
        poly = Polygon(list(zip(x_dwp, y_dwp)), lw=0, ls='dashdot', color='r',
                       fill=False, closed=False, animated=True)
        if self.modelpv is True:
            P4Radmax.ParamDict['dwp_pv_backup'] = a.ParamDict['dwp']
        self.draw_c(poly, xs, ys)

    def draw_c(self, data, x, y):
        self.ax.plot(x, y, 'r', lw=2.)
        self.ax.set_ylabel("DW", fontdict=font)
        self.ax.set_xlabel("Depth ($\AA$)", fontdict=font)
        self.poly = data
        xs, ys = zip(*self.poly.xy)
        self.line = Line2D(xs, ys, lw=0, ls='-.', color='r', marker='.', ms=32,
                           markerfacecolor='r', markeredgecolor='k', mew=1.0)
        self.ax.add_line(self.line)
        self.ax.add_patch(self.poly)
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.canvas.draw()

    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def poly_changed(self, poly):
        'this method is called whenever the polygon object is called'
        # only copy the artist props to the line (except visibility)
        vis = self.line.get_visible()
        Artist.update_from(self.line, poly)
        self.line.set_visible(vis)  # don't use the poly visibility state

    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'

        # display coords
        xy = np.asarray(self.poly.xy)
        xyt = self.poly.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]

        if d[ind] >= self.epsilon:
            ind = None
        return ind

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if self.canvas.HasCapture():
            self.canvas.ReleaseMouse()
            if not self.showverts:
                return
            if event.inaxes is None:
                return
            if event.button != 1:
                return
            self._ind = self.get_ind_under_point(event)
            self.new_coord['indice'] = self._ind

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if self.canvas.HasCapture():
            self.canvas.ReleaseMouse()
        else:
            if not self.showverts:
                return
            if event.button != 1:
                return
            if self.new_coord['indice'] is not None:
                a = P4Radmax()
                temp_1 = self.new_coord['y']
                temp_2 = self.new_coord['x']
                P4Radmax.DragDrop_DW_y[self.new_coord['indice']] = temp_1
                P4Radmax.DragDrop_DW_x[self.new_coord['indice']] = temp_2
                if self.modelpv is True:
                    t_temp = a.ParamDict['depth'] + a.ParamDict['z']
                    t = t_temp[0]
                    dwp_temp = range(7)
                    dwp_temp[0] = a.DragDrop_DW_y[0]
                    dwp_temp[1] = 1 - a.DragDrop_DW_x[0]/t
                    dwp_temp[2] = 2*(-1 + a.ParamDict['dwp'][1] +
                                     a.DragDrop_DW_x[1]/t)
                    dwp_temp[3] = 2*(1 - a.ParamDict['dwp'][1] -
                                     1*a.DragDrop_DW_x[2]/t)
                    dwp_temp[4] = a.ParamDict['dwp'][4]
                    dwp_temp[5] = a.ParamDict['dwp'][5]
                    dwp_temp[6] = a.DragDrop_DW_y[3]
                    P4Radmax.ParamDict['dwp'] = deepcopy(dwp_temp)
                    P4Radmax.ParamDictbackup['dwp'] = deepcopy(dwp_temp)
                    P4Radmax.ParamDict['dwp_pv'] = deepcopy(dwp_temp)
                else:
                    temp = self.new_coord['y']
                    P4Radmax.DragDrop_DW_y[self.new_coord['indice']] = temp
                    temp = [dw*scale for dw,
                            scale in zip(a.DragDrop_DW_y,
                                         a.ParamDict['scale_dw'])]
                    temp = [float(format(val, '.8f')) for val in temp]
                    temp1 = temp[1:]
                    temp2 = [a.ParamDict['dw_out']]
                    temp3 = deepcopy(np.concatenate((temp1, temp2), axis=0))
                    P4Radmax.ParamDict['dwp'] = temp3
                    P4Radmax.ParamDictbackup['dwp'] = temp3
                pub.sendMessage(pubsub_Update_Fit_Live)
            self._ind = None

    def scroll_callback(self, event):
        if not event.inaxes:
            return
        a = P4Radmax()
        if event.key == 'u' and event.button == 'up':
            temp = a.ParamDict['DW_multiplication'] + 0.01
            P4Radmax.ParamDict['DW_multiplication'] = temp
        elif event.key == 'u' and event.button == 'down':
            temp = a.ParamDict['DW_multiplication'] - 0.01
            P4Radmax.ParamDict['DW_multiplication'] = temp
        P4Radmax.ParamDict['dwp'] = multiply(a.ParamDictbackup['dwp'],
                                             a.ParamDict['DW_multiplication'])
        pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)

    def scale_manual(self, event, val=None):
        a = P4Radmax()
        if val is not None:
            P4Radmax.ParamDict['DW_multiplication'] = val
        P4Radmax.ParamDict['dwp'] = multiply(a.ParamDict['dwp'],
                                             a.ParamDict['DW_multiplication'])
        pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)

    def motion_notify_callback(self, event):
        'on mouse movement'
        a = P4Radmax()
        if not self.showverts:
            return
        if self._ind is None:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return

        if self.modelpv is True:
            if self._ind == 0:
                y = event.ydata
                x = event.xdata
            elif self._ind == 1 or self._ind == 2:
                y = a.DragDrop_DW_y[self.new_coord['indice']]
                x = event.xdata
            else:
                x = a.DragDrop_DW_x[self.new_coord['indice']]
                y = event.ydata
        else:
            y = event.ydata
            x = a.DragDrop_DW_x[self.new_coord['indice']]

        self.new_coord['x'] = x
        self.new_coord['y'] = y
        self.poly.xy[self._ind] = x, y
        self.line.set_data(zip(*self.poly.xy))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def on_update_coordinate(self, event):
        if event.inaxes is None:
            self.statusbar.SetStatusText(u"", 1)
            self.statusbar.SetStatusText(u"", 2)
        else:
            x, y = event.xdata, event.ydata
            xfloat = round(float(x), 2)
            yfloat = round(float(y), 2)
            self.statusbar.SetStatusText(u"x = " + str(xfloat), 1)
            self.statusbar.SetStatusText(u"y = " + str(yfloat), 2)
            xy = np.asarray(self.poly.xy)
            xyt = self.poly.get_transform().transform(xy)
            xt, yt = xyt[:, 0], xyt[:, 1]
            d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
            indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
            ind = indseq[0]

            if d[ind] >= self.epsilon:
                self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            elif d[ind] <= self.epsilon:
                self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_HAND))


# ------------------------------------------------------------------------------
class RightGraph(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar

        mastersizer = wx.BoxSizer(wx.VERTICAL)
        self.fig = Figure((7.0, 6.0))
        self.canvas = FigCanvas(self, -1, self.fig)
        self.fig.patch.set_facecolor(colorBackgroundGraph)

        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("Intensity (a.u.)", fontdict=font)
        self.ax.set_xlabel(r'2$\theta$ (deg.)', fontdict=font)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Hide()
        self.canvas.toolbar.zoom()
        self.toolbar.Disable()
        self.update_zoom = self.canvas.mpl_connect('motion_notify_event',
                                                   self.MouseOnGraph)
        self.ly = self.ax.axvline(color='r', lw=0.0)  # the vert line
        self.lx = self.ax.axhline(color='r', lw=0.0)  # the horiz line

        if not hasattr(self, "UnzoomID"):
            self.UnzoomID = wx.NewId()
            self.CheckedGridId = wx.NewId()
            self.CursorId = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnUnzoom, id=self.UnzoomID)
            self.Bind(wx.EVT_MENU, self.CheckedGrid, id=self.CheckedGridId)
            self.Bind(wx.EVT_MENU, self.CursorMove, id=self.CursorId)
        """build the menu"""
        self.menu = wx.Menu()
        self.item_unzoom = self.menu.Append(self.UnzoomID, "Unzoom")
        self.item_grid = self.menu.Append(self.CheckedGridId, "Show/Hide grid",
                                          kind=wx.ITEM_CHECK)
        self.item_cursor = self.menu.Append(self.CursorId, "Show/Hide cursor",
                                            kind=wx.ITEM_CHECK)
        self.item_unzoom.Enable(False)
        self.item_grid.Enable(False)
        self.item_cursor.Enable(False)

        self.canvas.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        mastersizer.Add(self.canvas, 1, wx.ALL)
        mastersizer.Add(self.toolbar, 1, wx.ALL)

        pub.subscribe(self.OnDrawGraph, pubsub_Draw_XRD)
        pub.subscribe(self.OnDrawGraphLive, pubsub_Draw_Fit_Live_XRD)
        pub.subscribe(self.onFit, pubsub_OnFit_Graph)
        self.SetSizer(mastersizer)
        self.Raise()
        self.SetPosition((0, 0))
        self.Fit()

    def OnDrawGraph(self, b=None):
        a = P4Radmax()
        self.ax.clear()
        if b == 1:
            self.ax.semilogy(2*a.ParamDict['th']*180/np.pi,
                             a.ParamDict['Iobs'], 'o-k')
        elif b == 2:
            self.ax.set_xlim([0, 1])
            self.ax.set_ylim([0, 1])
            self.ax.clear()
        else:
            a = P4Radmax()
            xx = 2*a.ParamDict['th']*180/np.pi
            self.ax.semilogy(xx, a.ParamDict['Iobs'], 'o-k')
            self.ax.semilogy(xx, a.ParamDict['I_i'], 'c-')
            middle = len(a.ParamDict['th'])/2
            self.ly = self.ax.axvline(x=xx[middle], color='r', lw=0.0)
            self.lx = self.ax.axhline(color='r', lw=0.0)  # the horiz line
        self.ax.set_ylabel("Intensity (a.u.)", fontdict=font)
        self.ax.set_xlabel(r'2$\theta$ (deg.)', fontdict=font)
        self.CheckedGrid()
        self.CursorMove()

    def OnDrawGraphLive(self, val=None):
        a = P4Radmax()
        if val != []:
            P4Radmax.ParamDict['I_fit'] = val
        self.ax.clear()
        self.ax.semilogy(a.ParamDict['th4live'], a.ParamDict['Iobs'], 'o-k')
        self.ax.semilogy(a.ParamDict['th4live'], a.ParamDict['I_fit'], 'r-')
        self.ax.set_ylabel("Intensity (a.u.)", fontdict=font)
        self.ax.set_xlabel(r'2$\theta$ (deg.)', fontdict=font)
        self.canvas.draw()

    def onFit(self, b=None):
        if b == 1:
            t = self.canvas.mpl_connect('motion_notify_event',
                                        self.on_update_coordinate)
            t1 = self.canvas.mpl_connect('button_release_event',
                                         self.MouseOnGraph)
            self.update_coordinate = t
            self.update_zoom = t1
            self.item_unzoom.Enable(True)
            self.item_grid.Enable(True)
            self.item_cursor.Enable(True)
        else:
            self.menu.Check(self.CursorId, check=False)
            self.item_unzoom.Enable(False)
            self.item_grid.Enable(False)
            self.item_cursor.Enable(False)
            self.ly.set_linewidth(0)
            self.lx.set_linewidth(0)
            self.canvas.mpl_disconnect(self.update_coordinate)
            self.canvas.mpl_disconnect(self.update_zoom)

    def MouseOnGraph(self, event):
        a = P4Radmax()
        if a.fitlive == 1:
            return
        if event.inaxes is not None:
            if a.ParamDict['Iobs'] is not "":
                xlim = self.ax.get_xlim()
                xlim_min = xlim[0]*np.pi/(2*180)
                xlim_max = xlim[1]*np.pi/(2*180)
                itemindex = where((a.ParamDict['th'] > xlim_min) &
                                  (a.ParamDict['th'] < xlim_max))
                t1 = itemindex[0][0]
                t2 = itemindex[0][-1]
                P4Radmax.ParamDict['th'] = a.ParamDict['th'][t1:t2]
                P4Radmax.ParamDict['Iobs'] = a.ParamDict['Iobs'][t1:t2]
                P4Radmax.ParamDict['th4live'] = 2*a.ParamDict['th']*180/np.pi

    def OnRightDown(self, event):
        a = P4Radmax()
        if a.fitlive == 1:
            return
        self.PopupMenu(self.menu)

    def OnUnzoom(self, event):
        self.canvas.toolbar.home()
        P4Radmax.zoomOn = 0
        a = P4Radmax()
        P4Radmax.ParamDict['th'] = a.ParamDictbackup['th']
        P4Radmax.ParamDict['Iobs'] = a.ParamDictbackup['Iobs']
        P4Radmax.ParamDict['th4live'] = 2*a.ParamDict['th']*180/np.pi
        pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)
        self.CheckedGrid(event)
        self.CursorMove(event)

    def CheckedGrid(self, event=None):
        if self.menu.IsChecked(self.CheckedGridId) is True:
            self.ax.grid(True, color='gray')
        elif self.menu.IsChecked(self.CheckedGridId) is False:
            self.ax.grid(False)
        self.canvas.draw()

    def CursorMove(self, event=None):
        if self.menu.IsChecked(self.CursorId) is True:
            self.ly.set_linewidth(1)
            self.lx.set_linewidth(1)
        elif self.menu.IsChecked(self.CursorId) is False:
            self.ly.set_linewidth(0)
            self.lx.set_linewidth(0)

    def on_update_coordinate(self, event):
        if event.inaxes is None:
            self.statusbar.SetStatusText(u"", 1)
            self.statusbar.SetStatusText(u"", 2)
            return
        else:
            x, y = event.xdata, event.ydata
            self.ly.set_xdata(x)
            self.lx.set_ydata(y)
            xfloat = round(float(x), 4)
            yfloat = round(float(y), 8)
            self.statusbar.SetStatusText(u"x = " + str(xfloat), 1)
            self.statusbar.SetStatusText(u"y = " + str(yfloat), 2)
            self.canvas.draw()
