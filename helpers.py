"""
Helper functions for displaying data and making interactive plots.
"""
import numpy as np
import matplotlib.pyplot as plt
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
               cb_aspect=50, cb_shrink=0.8, **kwargs):
    """
    Make a pcolormesh plot of the given data field.
    Set's the plot extent and includes ticks in longitude and latitude.
    """
    w, e, s, n = [data.longitude.min(), data.longitude.max(),
                  data.latitude.min(), data.latitude.max()]
    ax.set_title(field)
    data[field].plot.pcolormesh(
        ax=ax, add_labels=False, cmap=cmap,
        cbar_kwargs=dict(orientation='horizontal', aspect=cb_aspect,
                         pad=cb_pad, shrink=cb_shrink),
        **kwargs)
    xlocs = np.arange(w, e + 0.01, gridline_spacing)
    ylocs = np.arange(s, n + 0.01, gridline_spacing)
    ax.coastlines()
    ax.set_extent([w, e, s, n])
    ax.set_xticks(xlocs)
    ax.set_yticks(ylocs)
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.gridlines(color="#cccccc55", xlocs=xlocs, ylocs=ylocs)


def plot_hawaii_data(data, field, **kwargs):
    """
    Plot a given field from our Hawai'i dataset.
    """
    fig = plt.figure(figsize=(9, 11))
    ax = plt.axes(projection=ccrs.PlateCarree())
    plot_field(ax, data, field, **kwargs)
    plt.tight_layout(pad=0)
