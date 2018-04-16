"""
Helper functions for displaying data and making interactive plots.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import ipywidgets as widgets
from IPython.display import display, clear_output
import cmocean
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


def minmax(data, fields):
    """
    Get the minimum and maximum data values out of all fields given.
    Returns them in a dictionary with the 'vmin' and 'vmax' keys.
    """
    vmin = min(data[field].min() for field in fields)
    vmax = max(data[field].max() for field in fields)
    return dict(vmin=vmin, vmax=vmax)


def plot_field(ax, data, field, cmap=None, gridline_spacing=3, cb_pad=0.03,
               cb_aspect=50, cb_shrink=0.8, ticks=True, title=True, **kwargs):
    """
    Make a pcolormesh plot of the given data field.
    Set's the plot extent and includes ticks in longitude and latitude.
    """
    if title:
        ax.set_title(field)
    if 'add_colorbar' not in kwargs:
        kwargs['cbar_kwargs'] = dict(orientation='horizontal',
                                     aspect=cb_aspect, pad=cb_pad,
                                     shrink=cb_shrink)
    data[field].plot.pcolormesh(ax=ax, add_labels=False, cmap=cmap, **kwargs)
    ax.coastlines()
    w, e, s, n = [data.longitude.values.min(), data.longitude.values.max(),
                  data.latitude.values.min(), data.latitude.values.max()]
    ax.set_extent([w, e, s, n])
    xlocs = np.arange(w, e + 0.01, gridline_spacing)
    ylocs = np.arange(s, n + 0.01, gridline_spacing)
    if ticks:
        ax.set_xticks(xlocs)
        ax.set_yticks(ylocs)
        ax.xaxis.set_major_formatter(LongitudeFormatter())
        ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.gridlines(color="#cccccc55", xlocs=xlocs, ylocs=ylocs)


def plot_hawaii_data(data, field, **kwargs):
    """
    Plot a given field from our Hawai'i dataset.
    """
    fig = plt.figure(figsize=(12, 13))
    ax = plt.axes(projection=ccrs.PlateCarree())
    plot_field(ax, data, field, **kwargs)
    plt.tight_layout(pad=0)


def plot_japan_data(data, field, **kwargs):
    """
    Plot a given field from our Japan dataset.
    """
    fig = plt.figure(figsize=(12, 13))
    ax = plt.axes(projection=ccrs.PlateCarree())
    plot_field(ax, data, field, gridline_spacing=5, **kwargs)
    plt.tight_layout(pad=0)


def plot_himalayas_data(data, field, **kwargs):
    """
    Plot a given field from our Himalayas dataset.
    """
    fig = plt.figure(figsize=(12, 13))
    ax = plt.axes(projection=ccrs.PlateCarree())
    plot_field(ax, data, field, **kwargs)
    plt.tight_layout(pad=0)


class ProfileSelector(object):
    """
    Define a widget for selecting and plotting profiles from a dataset.

    Use the ``interact`` method to insert an interactive widget to control
    the profile location.

    Use the ``plot`` method to plot a static profile figure.

    Parameters
    ----------
    data : xarray.Dataset
        The data grid.
    fields : list of str
        The fields to plot in the upper profile
    figsize : tuple
        The size of the profile figure
    projection : cartopy CRS
        A cartopy projection to apply to the data maps

    """

    def __init__(self, data, fields, projection, figsize=(15, 9),
                 profile_interval=10):
        self.data = data
        self.fields = fields
        self._plot_initiated = False
        self.projection = projection
        self.figsize = figsize
        self.profile_interval = profile_interval

    def plot(self, location, dimension):
        """
        Plot a figure of the profile at location along dimension.
        """
        if not self._plot_initiated:
            # Setup the figure and subplot grid
            self.fig = plt.figure(figsize=self.figsize)
            grid = GridSpec(2, 3, hspace=0, wspace=0)
            self.ax_data = self.fig.add_subplot(grid[0,:-1])
            self.ax_topo = self.fig.add_subplot(grid[1,:-1])
            self.ax_data_map = self.fig.add_subplot(grid[0,-1],
                                                    projection=self.projection)
            self.ax_topo_map = self.fig.add_subplot(grid[1,-1],
                                                    projection=self.projection)

            # The y axis limits for the profiles
            self._topo_base = -10000
            ylim_topo = [self._topo_base, self.data.topography_ell.max()*1.1]
            ylim_data = list(sorted(minmax(self.data, self.fields).values()))

            # Set labels and dimensions
            self.ax_data.set_ylim(ylim_data)
            self.ax_data.set_ylabel('mGal')
            self.ax_topo.set_ylim(ylim_topo)
            self.ax_topo.set_ylabel('Tropography (m)')
            self.ax_data.grid(True)
            self.ax_data.set_xticklabels([])

            # Draw the profile lines
            self._data_lines = {}
            for field in self.fields:
                self._data_lines[field], = self.ax_data.plot([0], [0], '-',
                                                             label=field)
            self.ax_data.legend(loc='upper right')

            # Place holders for the topography polygons
            self._water_fill = None
            self._topo_fill = None

            # Plot the maps
            plot_field(self.ax_data_map, self.data, self.fields[0],
                       ticks=False, add_colorbar=False, title=False,
                       cmap='RdBu_r')
            plot_field(self.ax_topo_map, self.data, 'topography_ell',
                       ticks=False, add_colorbar=False, title=False,
                       cmap=cmocean.cm.delta)
            # Draw on the maps showing the profiles
            self._datamap_profile, = self.ax_data_map.plot([0, 0], [0, 0],
                                                           '--k')
            self._topomap_profile, = self.ax_topo_map.plot([0, 0], [0, 0],
                                                           '--k')

            plt.tight_layout(pad=0, h_pad=0, w_pad=0)

            self._plot_initiated = True

        # Get the name of the other dimension
        dim_comp = set(self.data.dims).difference({dimension}).pop()

        # Get the profile
        x = self.data[dimension]
        xlim = [x.min(), x.max()]
        profile = self.data.loc[{dim_comp: location}]

        # Update the data plots
        for field in self.fields:
            self._data_lines[field].set_data(x, profile[field])

        # Update the topography plot
        if self._topo_fill is not None:
            self._topo_fill.remove()
        if self._water_fill is not None:
            self._water_fill.remove()
        self._water_fill = self.ax_topo.fill_between(xlim, [0, 0],
                                                     self._topo_base,
                                                     color='#2780E3')
        self._topo_fill = self.ax_topo.fill_between(x, profile.topography_ell,
                                                    self._topo_base,
                                                    color='#333333')

        # Update the profile location plot
        profile_location = [xlim, [location, location]]
        if dimension.lower() == 'latitude':
            profile_location = profile_location[::-1]
        self._datamap_profile.set_data(*profile_location)
        self._topomap_profile.set_data(*profile_location)

        # Make sure the plots are tight
        self.ax_data.set_xlim(xlim)
        self.ax_topo.set_xlim(xlim)
        self.ax_topo.set_xlabel(dimension.capitalize())

        plt.show()

    def interact(self):
        """
        Display an interactive widget for choosing the profile.
        """
        # Setup the initial value options for the location
        options = self.data.longitude.values.tolist()[::self.profile_interval]
        mid = options[len(options)//2]
        dimension = 'longitude'

        # Make the slider for choosing the location
        slider_label = widgets.Label("at {} value".format(dimension))
        slider = widgets.SelectionSlider(options=options, value=mid,
                                         layout=widgets.Layout(width="350px"))
        # Make a menu for choosing the profile direction
        dimension_chooser = widgets.Dropdown(
            options=self.data.dims.keys(), value=self.data.dims.keys()[0],
            description="Profile along")

        def displayer(location, dimension):
            "Update and display the plot with given arguments"
            self.plot(location, dimension)
            display(self.fig)

        def handle_dimension_change(change):
            "Change the location options when dimension changes"
            dim2 = set(self.data.dims).difference({change.new}).pop()
            slider_label.value = "at {} value".format(dim2)
            options = self.data[dim2].values.tolist()[::self.profile_interval]
            slider.options = options
            slider.value = options[len(options)//2]

        # Connect the dimension change to the slider
        dimension_chooser.observe(handle_dimension_change, names='value')

        # Make the output display and connect it to the callback
        output = widgets.interactive_output(
            displayer, {'location': slider, 'dimension': dimension_chooser})

        # Make a title for the widget
        title = widgets.HTML(
            '<strong style="font-size: 1.5em;">Profile selector</strong>')

        # Layout the widgets
        layout = widgets.VBox(
            [title,
             widgets.HBox([dimension_chooser, slider_label, slider]),
             output],
            layout=widgets.Layout(align_items="center"))

        # For some reason, calling _figure_setup inserts a plot in the output
        # Call clear_output to get rid of it.
        with output:
            clear_output(wait=True)
            display(self.fig)

        return layout
