'''
This code has been taken from matlibplot polygon interaction

@author: Mr. Srikanth Nagella
'''
# pylint: disable=E1103
# pylint: disable=no-name-in-module
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
from matplotlib.artist import Artist
from matplotlib.mlab import dist_point_to_segment
from matplotlib.widgets import RectangleSelector


polygon_alpha = 0.2
class PolygonEditor(object):
    '''
    This edits the polygons drawn on the map
    '''

    show_verts = True
    epsilon = 3 #threshold
    def __init__(self, axis, canvas):
        '''
        initialises the editable polygon object
        '''
        self.axis = axis
        self.polygon = None
        self.line = None
        self.xy_values = np.array([])
        self._ind = None
        self.background = None #background copying

        self._callback_ids = list()
        self._callback_ids.append(canvas.mpl_connect('draw_event',
                                                     self.draw_callback))
        self._callback_ids.append(canvas.mpl_connect('button_press_event',
                                                     self.button_press_callback))
        self._callback_ids.append(canvas.mpl_connect('button_release_event',
                                                     self.button_release_callback))
        self._callback_ids.append(canvas.mpl_connect('motion_notify_event',
                                                     self.motion_notify_callback))
        self.canvas = canvas

    def add_point(self, xval, yval):
        """ adds an new point to the selection list and redraws the selection tool"""
        if self.xy_values.shape[0] == 0:
            self.xy_values = np.array([(xval, yval), ])
        else:
            self.xy_values = np.concatenate((self.xy_values, [[xval, yval], ]), axis=0)
        self.refresh()

    def refresh(self):
        """ This method looks at the list of points available and depending on the number of
        points in the list creates a point or line or a polygon and draws them"""
        if self.xy_values.shape[0] == 0: # No points available
            self.reset_line()
            self.reset_polygon()
        elif self.xy_values.shape[0] <= 2: # point or line for 1 or 2 points
            xval, yval = zip(*self.xy_values)
            if self.line == None:
                self.line = Line2D(xval, yval, marker='o', markerfacecolor='r', animated=True)
                self.axis.add_line(self.line)
            else:
                self.line.set_data(zip(*self.xy_values))
            self.reset_polygon()
        else: # more than 2 points if polygon is not created then creates one and draws
            if self.polygon == None:
                self.polygon = Polygon(self.xy_values, animated=True, alpha=polygon_alpha)
                self.polygon.add_callback(self.polygon_changed)
                self.axis.add_patch(self.polygon)
            else:
                self.polygon.xy = self.xy_values
            self.line.set_data(zip(*self.xy_values))
        self.draw_callback(None)
        self.canvas.draw()

    def reset_line(self):
        """ resets the line i.e removes the line from the axes and resets to None """
        if self.line != None:
            self.line.remove()
            self.line = None

    def reset_polygon(self):
        """ resets the polygon ie. removes the polygon from the axis and reset to None """
        if self.polygon != None:
            self.polygon.remove()
            self.polygon = None

    def draw_line(self):
        """ draws the line if available """
        if self.line != None:
            self.axis.draw_artist(self.line)

    def draw_polygon(self):
        """ draws polygon if available"""
        if self.polygon != None:
            self.axis.draw_artist(self.polygon)

    def disable(self):
        """ disables the events and the selection """
        self.set_visibility(False)
        for callback_id in self._callback_ids:
            self.canvas.mpl_disconnect(callback_id)
        self.canvas = None

    def enable(self):
        """ enables the selection """
        self.set_visibility(True)

    def set_visibility(self, status):
        """ sets the visibility of the selection object """
        if self.polygon != None:
            self.polygon.set_visible(status)
        if self.line != None:
            self.line.set_visible(status)
        self.canvas.blit(self.axis.bbox)

    def draw_callback(self, dummy_event):
        """ this method draws the selection object """
        self.background = self.canvas.copy_from_bbox(self.axis.bbox)
        self.draw_polygon()
        self.draw_line()
        self.canvas.blit(self.axis.bbox)

    def polygon_changed(self, poly):
        """ redraws the polygon """
        vis = self.line.get_visible()
        Artist.update_from(self.line, poly)
        self.line.set_visible(vis)

    def get_index_under_point(self, event):
        """ gets the index of the point under the event (mouse click) """
        if self.xy_values.shape[0] == 0:
            return None
        xy_values = self.xy_values
        xt_values, yt_values = xy_values[:, 0], xy_values[:, 1]
        dist = np.sqrt((xt_values-event.xdata)**2 + (yt_values-event.ydata)**2)
        indseq = np.nonzero(np.equal(dist, np.amin(dist)))[0]
        ind = indseq[0]
        if dist[ind] >= self.epsilon:
            ind = None
        return ind

    def button_press_callback(self, event):
        """ callback to mouse press event """
        if not self.show_verts:
            return
        if event.inaxes == None:
            return
        if event.button != 1:
            return
        self._ind = self.get_index_under_point(event)
        if self._ind == None:
            self.insert_datapoint(event)

    def button_release_callback(self, event):
        """ callback to mouse release event """
        if not self.show_verts:
            return
        if event.button == 2:
            self.insert_datapoint(event)
            return
        if event.button == 3:
            self.delete_datapoint(event)
            return
        if event.button != 1:
            return
        self._ind = None

    def insert_datapoint(self, event):
        """ inserts a new data point between the segment that is closest in polygon """
        if self.xy_values.shape[0] <= 2:
            self.add_point(event.xdata, event.ydata)
        else:
            event_point = event.xdata, event.ydata
            prev_d = dist_point_to_segment(event_point, self.xy_values[0], self.xy_values[-1])
            prev_i = len(self.xy_values)
            for i in range(len(self.xy_values)-1):
                seg_start = self.xy_values[i]
                seg_end = self.xy_values[i+1]
                dist_p_s = dist_point_to_segment(event_point, seg_start, seg_end)
                if dist_p_s < prev_d:
                    prev_i = i
                    prev_d = dist_p_s
            self.xy_values = np.array(list(self.xy_values[:prev_i+1]) +
                                      [(event.xdata, event.ydata)] +
                                      list(self.xy_values[prev_i+1:]))
            self.refresh()

    def delete_datapoint(self, event):
        """ deletes the data point under the point in event """
        ind = self.get_index_under_point(event)
        if ind is not None:
            self.xy_values = np.array([tup for i, tup in enumerate(self.xy_values) if i != ind])
            self.refresh()
        self.canvas.draw()

    def motion_notify_callback(self, event):
        """ callback for the mouse motion with button press.
        this is to move the edge points of the polygon"""
        if not self.show_verts:
            return
        if self._ind is None:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        xval, yval = event.xdata, event.ydata

        self.xy_values[self._ind] = xval, yval
        self.refresh()

        self.canvas.restore_region(self.background)
        self.axis.draw_artist(self.polygon)
        self.axis.draw_artist(self.line)
        self.canvas.blit(self.axis.bbox)

    def reset(self):
        """ resets the points in the selection deleting the line and polygon"""
        self.xy_values = np.array([])
        self.reset_line()
        self.reset_polygon()

class BoxEditor(object):
    """ Box editor is to select area using rubber band sort of drawing rectangle.
    it uses matplotlib RectangleSelector under the hood """
    polygon = None
    def __init__(self, axes, canvas):
        """ initialises class and creates a rectangle selector """
        self.axes = axes
        self.canvas = canvas
        self.rectangle_selector = RectangleSelector(axes, self.line_select_callback, drawtype='box',
                                                    useblit=True, button=[1,],
                                                    minspanx=5, minspany=5,
                                                    spancoords='pixels')

    def line_select_callback(self, eclick, erelease):
        """ callback to the rectangleselector """
        x1_val, y1_val = eclick.xdata, eclick.ydata
        x2_val, y2_val = erelease.xdata, erelease.ydata
        xy_values = np.array([[x1_val, y1_val, ],
                              [x1_val, y2_val, ],
                              [x2_val, y2_val, ],
                              [x2_val, y1_val, ], ])
        self.reset_polygon()
        self.polygon = Polygon(xy_values, animated=False, alpha=polygon_alpha)
        self.axes.add_patch(self.polygon)
        self.canvas.draw()

    def enable(self):
        """ enable the box selector """
        self.rectangle_selector.set_active(True)

    def disable(self):
        """ disables or removes the box selector """
        self.reset_polygon()
        self.rectangle_selector.set_active(False)
        self.canvas.draw()

    def reset_polygon(self):
        """ resets rectangle polygon """
        if self.polygon != None:
            self.polygon.remove()
            self.polygon = None

    def reset(self):
        """ reset the Box selector """
        self.reset_polygon()

# if __name__ == '__main__':
#     import matplotlib.pyplot as plt
#     from matplotlib.patches import Polygon
#
#     theta = np.arange(0, 2*np.pi, 0.3)
#     r = 1.5
#
#     xs = r*np.cos(theta)
#     ys = r*np.sin(theta)
#
# #    poly = Polygon(list(zip(xs,ys)), animated=True)
#     poly = Polygon(list([(0,0)]), animated=True)
#
#     fig, ax = plt.subplots()
#     ax.add_patch(poly)
#     p = PolygonEditor(ax,poly)
#
#     ax.set_title('Click and drag a point to move it')
#     ax.set_xlim((-2,2))
#     ax.set_ylim((-2,2))
#     plt.show()
