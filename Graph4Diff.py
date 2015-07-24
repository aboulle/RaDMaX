#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A_BOULLE & M_SOUILAH
# Version du : 22/06/2015

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.lines import Line2D
from matplotlib.artist import Artist
from matplotlib.mlab import dist_point_to_segment
from matplotlib.patches import Polygon

from Parameters4Diff import *

"""Pubsub message"""
pubsub_draw_graph = "DrawGraph"
pubsub_Draw_XRD = "DrawXRD"
pubsub_Draw_Strain = "DrawStrain"
pubsub_Draw_DW = "DrawDW"
pubsub_Draw_Fit_Live_XRD = "DrawFitLiveXRD"
pubsub_Update_Fit_Live = "UpdateFitLive"
pubsub_Re_Read_field_paramters_panel = "ReReadParametersPanel"
pubsub_OnFit_Graph = "OnFitGraph"

colorBackgroundGraph = '#F0F0F0'

font = {'family' : 'serif',
        'color'  : 'darkred',
        'weight' : 'normal',
        'size'   : 14,
        }

#------------------------------------------------------------------------------
class Graph_window(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar
        
        size_StaticBox = (800, 140)
        fontStaticBox = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
        
#        mastersizer = wx.BoxSizer(wx.VERTICAL)    
#        Graph_box = wx.StaticBox(self, -1, " Strain and DW profiles ", size=size_StaticBox)
#        Graph_box.SetFont(fontStaticBox)
#        Graph_box_sizer = wx.StaticBoxSizer(Graph_box, wx.VERTICAL)
#        in_box = wx.GridBagSizer(hgap=0, vgap=2)
#
#        panelOne = LeftGraphTop(self, self.statusbar)
#        panelTwo = LeftGraphBottom(self, self.statusbar)
#        
#        in_box.Add(panelOne, pos=(0,0))
#        in_box.Add(panelTwo, pos=(1,0))
#
#        Graph_box_sizer.Add(in_box, 1, wx.EXPAND)
#
#        mastersizer.Add(Graph_box_sizer, 0, wx.ALL, 5)
#        self.SetSizer(mastersizer)
#        self.Fit()
#        self.Layout()
#
#        
        mastersizer = wx.BoxSizer(wx.VERTICAL)    
        Graph_box = wx.StaticBox(self, -1, " Strain and DW profiles ", size=size_StaticBox)
        Graph_box.SetFont(fontStaticBox)
        Graph_box_sizer = wx.StaticBoxSizer(Graph_box, wx.VERTICAL)
        
        vSplitter = wx.SplitterWindow(self)
        panelOne = LeftGraphTop(vSplitter, self.statusbar)
        panelTwo = LeftGraphBottom(vSplitter, self.statusbar)
        vSplitter.SplitHorizontally(panelOne, panelTwo)
        vSplitter.SetSashGravity(0.5)
#        vSplitter.SetMinimumPaneSize(200)
          
        Graph_box_sizer.Add(vSplitter, 1, wx.ALL | wx.EXPAND)       
        mastersizer.Add(Graph_box_sizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(mastersizer)
        self.Layout()

#        mastersizer = wx.BoxSizer(wx.VERTICAL)    
#        Graph_box = wx.StaticBox(self, -1, " Strain and DW profiles ", size=size_StaticBox)
#        Graph_box.SetFont(fontStaticBox)
#        Graph_box_sizer = wx.StaticBoxSizer(Graph_box, wx.VERTICAL)
#
#        self.aui_mgr = aui.AuiManager()
#        self.aui_mgr.SetManagedWindow( self)
#        panelOne = LeftGraphTop(self, self.statusbar)
#        panelTwo = LeftGraphBottom(self, self.statusbar)
#       
#        self.aui_mgr.AddPane(panelOne, aui.AuiPaneInfo().Top().CenterPane().PaneBorder( False ).Position(1).MaximizeButton(False))
#        self.aui_mgr.AddPane(panelTwo, aui.AuiPaneInfo().Bottom().CenterPane().PaneBorder( False ).Position(1).MaximizeButton(False))
#
#        Graph_box_sizer.Add(self.aui_mgr, 1, wx.EXPAND)        
#        mastersizer.Add(Graph_box_sizer, 0, wx.ALL, 5)
#        self.SetSizer(mastersizer)
#
#        self.Layout()
#        self.Centre( wx.BOTH )
#        self.aui_mgr.Update()
       
#------------------------------------------------------------------------------
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

        self.fig = Figure((12.0, 1.0))
        self.canvas = FigCanvas(self, -1, self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("Strain", fontdict=font)
        self.ax.set_xlabel("Depth ($\AA$)", fontdict=font)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Hide()
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        
        self.fig.patch.set_facecolor(colorBackgroundGraph)

        self._ind = None # the active vert
        self.poly = []
        self.line = []
        self.showverts = True
        self.epsilon = 5  # max pixel distance to count as a vertex hit
        self.new_coord = {'indice':0, 'x':0, 'y':0}
        
        self.u_key_press = False

        xs = [-1]
        ys = [-1]    
        poly = Polygon(list(zip(xs, ys)), fill =False, closed=False, animated=True)
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])
        self.draw_c(poly, xs, ys)

        self.canvas.mpl_connect('draw_event', self.draw_callback)
        self.canvas.mpl_connect('button_press_event', self.button_press_callback)
        self.canvas.mpl_connect('key_press_event', self.key_press_callback)
        self.canvas.mpl_connect('key_release_event', self.key_release_callback)
        self.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas.mpl_connect('scroll_event', self.scroll_callback)
        self.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas.mpl_connect('motion_notify_event', self.on_update_coordinate)
        
        self.press = None
        mastersizer.Add(self.canvas, 1, wx.EXPAND)
        mastersizer.Add(self.toolbar, 1, wx.EXPAND)
        pub.subscribe(self.OnDrawGraph, pubsub_Draw_Strain)
        
        self.SetSizer(mastersizer)
        self.Raise()
        self.SetPosition((0,0))
        self.Fit()


    def OnDrawGraph(self, b=None):
        self.ax.clear() 
        if b != 2:
            a = P4Diff()
            x_sp = a.x_sp
            y_sp = a.strain_shifted
            xs = deepcopy(a.depth)
            ys = deepcopy(a.strain_i*100)
            P4Diff.DragDrop_Strain_x = x_sp
            P4Diff.DragDrop_Strain_y = y_sp
            ymin = min(ys) + min(ys)*10/100
            ymax = max(ys) + max(ys)*10/100
            self.ax.set_ylim([ymin, ymax])
#            self.ax.set_ylim([0, a.initial_parameters[15]*a.strain_multiplication])
        elif b == 2:
            x_sp = [-1]
            y_sp = [-1]
            xs = [-1]
            ys = [-1]    
            self.ax.set_xlim([0, 1])
            self.ax.set_ylim([-1, 1])
        poly = Polygon(list(zip(x_sp, y_sp)), ls='dashdot', color='g', fill =False, closed=False, animated=True)
#        poly = Polygon(list(zip(x_sp, y_sp)), ls='dashdot', color='g', fill =False, closed=False, animated=True, joinstyle='round')
        self.draw_c(poly, xs, ys)

    def draw_c(self, data, x, y):
        self.ax.plot(x, y, 'g', lw=2.)
#        self.ax.plot(x, y, marker='o', alpha=0.0)
        self.ax.set_ylabel("Strain", fontdict=font)
        self.poly = data
        xs, ys = zip(*self.poly.xy)
#        self.line = Line2D(xs, ys, marker='o', ms = 12, markerfacecolor='g', color='g')
        self.line = Line2D(xs, ys,lw=1., ls='-.', color='g', marker='.', ms=32, markerfacecolor='g', markeredgecolor='k', mew=1.0)

        self.ax.add_line(self.line)
        cid = self.poly.add_callback(self.poly_changed)
        self.ax.add_patch(self.poly)
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
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
#        d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
        d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]

        if d[ind]>=self.epsilon:
            ind = None
        
        return ind

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if self.canvas.HasCapture():
            self.canvas.ReleaseMouse()
            if not self.showverts: return
            if event.inaxes==None: return
            if event.button != 1: return
            self._ind = self.get_ind_under_point(event)
            self.new_coord['indice'] = self._ind

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if self.canvas.HasCapture():
            self.canvas.ReleaseMouse()
        else:
            if not self.showverts: return
            if event.button != 1: return            
            if self.new_coord['indice'] != None:
                a = P4Diff()
                P4Diff.DragDrop_Strain_y[self.new_coord['indice']] = self.new_coord['y']
#                print self.new_coord            
                temp = [strain*scale/100 for strain, scale in zip(a.DragDrop_Strain_y, a.scale_strain)]
                temp = [float(format(val, '.8f')) for val in temp]
                temp1 = temp[1:]
                temp2 =  [a.stain_out_save]
                P4Diff.sp = deepcopy(np.concatenate((temp1, temp2), axis=0))
                P4Diff.sp_backup = deepcopy(np.concatenate((temp1, temp2), axis=0))
                pub.sendMessage(pubsub_Update_Fit_Live)
            self._ind = None

    def key_press_callback(self, event):
        'whenever a key is pressed'
        if not event.inaxes: return
        if event.key == 'u':
            self.u_key_press = True

    def scroll_callback(self, event):
        if not event.inaxes: return
        a = P4Diff()
        if event.key == 'u' and event.button == 'up':
            P4Diff.strain_multiplication = a.strain_multiplication + 0.01
        elif event.key == 'u' and event.button == 'down':
            P4Diff.strain_multiplication = a.strain_multiplication - 0.01

    def key_release_callback(self, event):
        if not event.inaxes: return
        a = P4Diff()
        if event.key == 'u':
            self.u_key_press = False
            P4Diff.sp = multiply(a.sp_backup,a.strain_multiplication)
            pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)

    def motion_notify_callback(self, event):
        'on mouse movement'
        a = P4Diff()
        if not self.showverts: return
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
#        x,y = event.xdata, event.ydata
        y = event.ydata
        x = a.DragDrop_Strain_x[self.new_coord['indice']]
        self.new_coord['x'] = x
        self.new_coord['y'] = y
        
        self.poly.xy[self._ind] = x,y
        self.line.set_data(zip(*self.poly.xy))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def on_update_coordinate(self, event):
        if event.inaxes is None:
            self.statusbar.SetStatusText(u"", 1)
            self.statusbar.SetStatusText(u"", 2)
            return
        else:
            x, y = event.xdata, event.ydata
            xfloat = round(float(x),2)
            yfloat = round(float(y),2)            
            self.statusbar.SetStatusText(u"x = " + str(xfloat),1)
            self.statusbar.SetStatusText(u"y = " + str(yfloat),2)


#------------------------------------------------------------------------------
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
        
        self.fig = Figure((12.0, 6.0))
        self.canvas = FigCanvas(self, -1, self.fig)
#        canvas.mpl_connect('button_release_event', self.MouseOnGraph)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("DW", fontdict=font)
        self.ax.set_xlabel("Depth ($\AA$)", fontdict=font)
        self.ax.xaxis.set_label_position('top') 
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Hide()
        
        self.fig.patch.set_facecolor(colorBackgroundGraph)

        self._ind = None # the active vert
        self.poly = []
        self.line = []
        self.showverts = True
        self.epsilon = 5  # max pixel distance to count as a vertex hit
        self.new_coord = {'indice':0, 'x':0, 'y':0}
        self.u_key_press = True

        xs = [-1]
        ys = [-1]    
        poly = Polygon(list(zip(xs, ys)), fill =False, closed=False, animated=True)
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])
        self.draw_c(poly, xs, ys)

        self.canvas.mpl_connect('draw_event', self.draw_callback)
        self.canvas.mpl_connect('button_press_event', self.button_press_callback)
        self.canvas.mpl_connect('key_press_event', self.key_press_callback)
        self.canvas.mpl_connect('key_release_event', self.key_release_callback)
        self.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas.mpl_connect('scroll_event', self.scroll_callback)
        self.canvas.mpl_connect('motion_notify_event', self.on_update_coordinate)
        mastersizer.Add(self.canvas, 1, wx.EXPAND)
        mastersizer.Add(self.toolbar, 1, wx.EXPAND)
        
        pub.subscribe(self.draw_c, pubsub_draw_graph)
        pub.subscribe(self.OnDrawGraph, pubsub_Draw_DW)
        
        self.SetSizer(mastersizer)
        self.Raise()
        self.SetPosition((0,0))
        self.Fit()

    def OnDrawGraph(self, b=None):
        self.ax.clear() 
        if b != 2:
            a = P4Diff()
            x_dwp = a.x_dwp
            y_dwp = a.DW_shifted
            xs = deepcopy(a.depth)
            ys = deepcopy(a.DW_i)
            P4Diff.DragDrop_DW_x = x_dwp
            P4Diff.DragDrop_DW_y = y_dwp
            ymin = min(ys) + min(ys)*10/100
            ymax = max(ys) + max(ys)*10/100
            self.ax.set_ylim([-1*ymin, ymax])
#            self.ax.set_ylim([a.initial_parameters[17]*a.DW_multiplication, max(y_dwp)])
        elif b == 2:
            x_dwp = [-1]
            y_dwp = [-1]
            xs = [-1]
            ys = [-1]    
            self.ax.set_xlim([0, 1])
            self.ax.set_ylim([0, 1])
        poly = Polygon(list(zip(x_dwp, y_dwp)), ls='dashdot', color='r', fill =False, closed=False, animated=True)
#        poly = Polygon(list(zip(x_dwp, y_dwp)), ls='dashdot', color='r', fill =False, closed=False, animated=True, joinstyle='round')
        self.draw_c(poly, xs, ys)

    def draw_c(self, data, x, y):
        self.ax.plot(x, y, 'r', lw=2.)
        self.ax.set_ylabel("DW", fontdict=font)
        self.ax.set_xlabel("Depth ($\AA$)", fontdict=font)
        self.ax.xaxis.set_label_position('top') 
        self.ax.set_xticklabels([])
        self.poly = data
        xs, ys = zip(*self.poly.xy)
        self.line = Line2D(xs, ys,lw=1., ls='-.', color='r', marker='.', ms=32, markerfacecolor='r', markeredgecolor='k', mew=1.0)
        self.ax.add_line(self.line)
        cid = self.poly.add_callback(self.poly_changed)
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
#        d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
        d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]

        if d[ind]>=self.epsilon:
            ind = None
        return ind

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if self.canvas.HasCapture():
            self.canvas.ReleaseMouse()
            if not self.showverts: return
            if event.inaxes==None: return
            if event.button != 1: return
            self._ind = self.get_ind_under_point(event)
            self.new_coord['indice'] = self._ind 

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if self.canvas.HasCapture():
            self.canvas.ReleaseMouse()
        else:
            if not self.showverts: return
            if event.button != 1: return            
            if self.new_coord['indice'] != None:
                P4Diff.DragDrop_DW_y[self.new_coord['indice']] = self.new_coord['y']
#                print self.new_coord             
                a= P4Diff()
                temp = [dw*scale for dw, scale in zip(a.DragDrop_DW_y, a.scale_dw)]
                temp = [float(format(val, '.8f')) for val in temp]
                temp1 = temp[1:]
                temp2 =  [a.dw_out_save]
                P4Diff.dwp = deepcopy(np.concatenate((temp1, temp2), axis=0))
                P4Diff.dwp_backup = deepcopy(np.concatenate((temp1, temp2), axis=0))
                pub.sendMessage(pubsub_Update_Fit_Live)
            self._ind = None

    def key_press_callback(self, event):
        'whenever a key is pressed'
        if not event.inaxes: return
        if event.key=='t':
            self.showverts = not self.showverts
            self.line.set_visible(self.showverts)
            if not self.showverts: self._ind = None
        elif event.key=='d':
            ind = self.get_ind_under_point(event)
            if ind is not None:
                self.poly.xy = [tup for i,tup in enumerate(self.poly.xy) if i!=ind]
                self.line.set_data(zip(*self.poly.xy))
        elif event.key=='i':
            xys = self.poly.get_transform().transform(self.poly.xy)
            p = event.x, event.y # display coords
            for i in range(len(xys)-1):
                s0 = xys[i]
                s1 = xys[i+1]
                d = dist_point_to_segment(p, s0, s1)
                if d<=self.epsilon:
                    self.poly.xy = np.array(
                        list(self.poly.xy[:i]) +
                        [(event.xdata, event.ydata)] +
                        list(self.poly.xy[i:]))
                    self.line.set_data(zip(*self.poly.xy))
                    break
        self.canvas.draw()

    def key_press_callback(self, event):
        'whenever a key is pressed'
        if not event.inaxes: return
        if event.key == 'u':
            self.u_key_press = True

    def scroll_callback(self, event):
        if not event.inaxes: return
        a = P4Diff()
        if event.key == 'u' and event.button == 'up':
            P4Diff.DW_multiplication = a.DW_multiplication + 0.01
        elif event.key == 'u' and event.button == 'down':
            P4Diff.DW_multiplication = a.DW_multiplication - 0.01

    def key_release_callback(self, event):
        if not event.inaxes: return
        a = P4Diff()
        if event.key == 'u':
            self.u_key_press = False
            P4Diff.dwp = multiply(a.dwp_backup,a.DW_multiplication)
            pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)

    def motion_notify_callback(self, event):
        'on mouse movement'
        a = P4Diff()
        if not self.showverts: return
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        y = event.ydata
        x = a.DragDrop_Strain_x[self.new_coord['indice']]
        self.new_coord['x'] = x
        self.new_coord['y'] = y
        
        self.poly.xy[self._ind] = x,y
        self.line.set_data(zip(*self.poly.xy))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def on_update_coordinate(self, event):
        if event.inaxes is None:
            self.statusbar.SetStatusText(u"", 1)
            self.statusbar.SetStatusText(u"", 2)
            return
        else:
            x, y = event.xdata, event.ydata
            xfloat = round(float(x),2)
            yfloat = round(float(y),2)            
            self.statusbar.SetStatusText(u"x = " + str(xfloat),1)
            self.statusbar.SetStatusText(u"y = " + str(yfloat),2)
            
            
#------------------------------------------------------------------------------
class RightGraph(wx.Panel):
    def __init__(self, parent, statusbar):
        wx.Panel.__init__(self, parent)
        self.statusbar = statusbar
        fontStaticBox = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
        size_StaticBox = (800, 140)
        
        mastersizer = wx.BoxSizer(wx.VERTICAL)    
        Graph_box = wx.StaticBox(self, -1, " XRD profile ", size=size_StaticBox)
        Graph_box.SetFont(fontStaticBox)
        Graph_box_sizer = wx.StaticBoxSizer(Graph_box, wx.VERTICAL)           

        graph_control_sizer = wx.BoxSizer(wx.VERTICAL)           

        self.fig = Figure((12.0, 6.0))
        self.canvas = FigCanvas(self, -1, self.fig)
        self.fig.patch.set_facecolor(colorBackgroundGraph)

        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("Intensity (a.u.)", fontdict=font)
        self.ax.set_xlabel(r'2$\theta$ (deg.)', fontdict=font)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Hide()
        self.canvas.toolbar.zoom()
        self.toolbar.Disable()
        self.update_zoom = self.canvas.mpl_connect('button_press_event', self.MouseOnGraph)
        self.update_coordinate = self.canvas.mpl_connect('motion_notify_event', self.on_update_coordinate)   
        self.canvas.mpl_disconnect(self.update_coordinate)
        self.canvas.mpl_disconnect(self.update_zoom)
        self.ly = self.ax.axvline(color='r', lw=0.0)  # the vert line
        self.lx = self.ax.axhline(color='r', lw=0.0)  # the horiz line

        if not hasattr(self, "UnzoomID"):
#            self.zoomID = wx.NewId()
            self.UnzoomID = wx.NewId()
            self.CheckedGridId = wx.NewId()
            self.CursorId = wx.NewId()
            self.itemThreeId = wx.NewId()
#            self.Bind(wx.EVT_MENU, self.Onzoom, id=self.zoomID)
            self.Bind(wx.EVT_MENU, self.OnUnzoom, id=self.UnzoomID)
            self.Bind(wx.EVT_MENU, self.CheckedGrid, id=self.CheckedGridId)
            self.Bind(wx.EVT_MENU, self.CursorMove, id=self.CursorId)
 
        """build the menu"""
        self.menu = wx.Menu()
#        self.item_zoom = self.menu.Append(self.zoomID, "Zoom")
        self.item_unzoom = self.menu.Append(self.UnzoomID, "Unzoom")
        self.item_grid = self.menu.Append(self.CheckedGridId, "Show/Hide grid", kind=wx.ITEM_CHECK)
        self.item_cursor = self.menu.Append(self.CursorId, "Show/Hide cursor", kind=wx.ITEM_CHECK)
#        self.item_zoom.Enable(False)
        self.item_unzoom.Enable(False)
        self.item_grid.Enable(False)
        self.item_cursor.Enable(False)

        self.canvas.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        
        Graph_box_sizer.Add(self.canvas, flag=wx.LEFT | wx.TOP | wx.GROW | wx.ALL)
        Graph_box_sizer.Add(self.toolbar, flag=wx.LEFT | wx.EXPAND | wx.ALL)
        
        mastersizer.Add(Graph_box_sizer, 0, wx.ALL, 5)
        pub.subscribe(self.OnDrawGraph, pubsub_Draw_XRD)
        pub.subscribe(self.OnDrawGraphLive, pubsub_Draw_Fit_Live_XRD)
        pub.subscribe(self.onFit, pubsub_OnFit_Graph)
        
        self.SetSizer(mastersizer)
        self.Raise()
        self.SetPosition((0,0))
        self.Fit()

    def OnDrawGraph(self, b=None):
        a = P4Diff()
        self.ax.clear() 
        if b == 1:
            self.ax.semilogy(2*a.th*180/pi, a.Iobs, 'o-k')
        elif b == 2:
            self.ax.set_xlim([0, 1])
            self.ax.set_ylim([0, 1])
            self.ax.clear() 
        else:
            a = P4Diff()
            xx = 2*a.th*180/pi
            self.ax.semilogy(xx, a.Iobs, 'o-k')
            self.ax.semilogy(xx, a.I_i, 'c-')
            middle = len(a.th)/2
            self.ly = self.ax.axvline(x=xx[middle],color='r', lw=0.0)  # the vert line
            self.lx = self.ax.axhline(color='r', lw=0.0)  # the horiz line
        self.ax.set_ylabel("Intensity (a.u.)", fontdict=font)
        self.ax.set_xlabel(r'2$\theta$ (deg.)', fontdict=font)
        self.CheckedGrid()
        self.CursorMove()

    def OnDrawGraphLive(self, val=None):
        a = P4Diff()
        if val != []:
            P4Diff.I_fit = val
        self.ax.clear() 
        self.ax.semilogy(a.th4live, a.Iobs, 'o-k')
        self.ax.semilogy(a.th4live, a.I_fit, 'r-')
        self.ax.set_ylabel("Intensity (a.u.)", fontdict=font)
        self.ax.set_xlabel(r'2$\theta$ (deg.)', fontdict=font)
        self.canvas.draw()
        
    def onDoubleClick(self, event):
        print "DoubleClick"

    def onFit(self, b=None):
        if b == 1:
            self.update_coordinate = self.canvas.mpl_connect('motion_notify_event', self.on_update_coordinate)   
            self.update_zoom = self.canvas.mpl_connect('button_release_event', self.MouseOnGraph)
#            self.item_zoom.Enable(True)
            self.item_unzoom.Enable(True)
            self.item_grid.Enable(True)
            self.item_cursor.Enable(True)
        else:
            self.menu.Check(self.CursorId, check=False)
#            self.item_zoom.Enable(False)
            self.item_unzoom.Enable(False)
            self.item_grid.Enable(False)
            self.item_cursor.Enable(False)
            self.ly.set_linewidth(0)
            self.lx.set_linewidth(0)
            self.canvas.mpl_disconnect(self.update_coordinate)
            self.canvas.mpl_disconnect(self.update_zoom)

    def MouseOnGraph(self, event):
        a = P4Diff()
        if a.fitlive == 1: return
        if event.inaxes is not None:
            if event.button == 1 and self.menu.IsEnabled(self.CheckedGridId) == True:
                xlim = self.ax.get_xlim()
                ylim = self.ax.get_ylim()
                xlim_min = xlim[0]*pi/(2*180)
                xlim_max = xlim[1]*pi/(2*180)
                itemindex = where((a.th > xlim_min) & (a.th < xlim_max))
                P4Diff.th = a.th[itemindex[0][0]:itemindex[0][-1]]
                P4Diff.Iobs = a.Iobs[itemindex[0][0]:itemindex[0][-1]]
                P4Diff.th4live = 2*a.th*180/pi

    def OnRightDown(self, event):
        a = P4Diff()
        if a.fitlive == 1: return
        self.PopupMenu(self.menu)

    def Onzoom(self, event):
        self.canvas.toolbar.zoom()
        
    def OnUnzoom(self, event):
        self.canvas.toolbar.home()
        a = P4Diff()
        P4Diff.th = a.th_backup
        P4Diff.Iobs = a.Iobs_backup
        P4Diff.th4live = 2*a.th*180/pi
        pub.sendMessage(pubsub_Re_Read_field_paramters_panel, event=event)
        self.CheckedGrid(event)
        self.CursorMove(event)

    def CheckedGrid(self, event=None):
        if self.menu.IsChecked(self.CheckedGridId) == True:
            self.ax.grid(True, color='gray')
        elif self.menu.IsChecked(self.CheckedGridId) == False:
            self.ax.grid(False)
        self.canvas.draw()

    def CursorMove(self, event=None):
        if self.menu.IsChecked(self.CursorId) == True:
            self.ly.set_linewidth(1)
            self.lx.set_linewidth(1)
        elif self.menu.IsChecked(self.CursorId) == False:
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
            xfloat = round(float(x),4)
            yfloat = round(float(y),8)            
            self.statusbar.SetStatusText(u"x = " + str(xfloat),1)
            self.statusbar.SetStatusText(u"y = " + str(yfloat),2)
            self.canvas.draw()

