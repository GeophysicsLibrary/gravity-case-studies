"""
Defines a function to load data and metadata from an ICGEM .gdf file.
"""
from __future__ import division
import numpy as np


def load_icgem_gdf(fname):
    """
    Load data from an ICGEM .gdf files.

    Parameters
    ----------
    fname : str
        The name of the .gdf file.

    Returns
    -------
    data : dict
        A dictionary with the data columns and metadata (shape of the grid,
        height, header, etc). Column data are numpy arrays.

    """
    with open(fname) as gdf_file:

        # Read the header and extract metadata
        metadata = []
        shape = [None, None]
        size = None
        height = None
        attributes = None
        attr_line = False
        area = [None]*4
        for line in gdf_file:
            if line.strip()[:11] == 'end_of_head':
                break
            metadata.append(line)
            if not line.strip():
                attr_line = True
                continue
            if not attr_line:
                parts = line.strip().split()
                if parts[0] == 'height_over_ell':
                    height = float(parts[1])
                elif parts[0] == 'latitude_parallels':
                    shape[0] = int(parts[1])
                elif parts[0] == 'longitude_parallels':
                    shape[1] = int(parts[1])
                elif parts[0] == 'number_of_gridpoints':
                    size = int(parts[1])
                elif parts[0] == 'latlimit_south':
                    area[0] = float(parts[1])
                elif parts[0] == 'latlimit_north':
                    area[1] = float(parts[1])
                elif parts[0] == 'longlimit_west':
                    area[2] = float(parts[1])
                elif parts[0] == 'longlimit_east':
                    area[3] = float(parts[1])
            else:
                attributes = line.strip().split()
                attr_line = False

        # Read the numerical values
        rawdata = np.loadtxt(gdf_file, ndmin=2, unpack=True)

    # Package the data in a dictionary with the attribute names that we got
    # from the file and the header information.
    data = dict(shape=shape, area=area, metadata=''.join(metadata))
    for attr, value in zip(attributes, rawdata):
        # Need to invert the data matrices in latitude "[::-1]"
        # because the ICGEM grid varies latitude from N to S
        # instead of S to N.
        data[attr] = value.reshape(shape)[::-1].ravel()
    if (height is not None):
        data['h_over_ellipsoid'] = height*np.ones(size)

    # Sanity checks
    assert all(n is not None for n in shape), "Couldn't read shape of grid."
    assert size is not None, "Couldn't read size of grid."
    shape = tuple(shape)
    assert shape[0]*shape[1] == size, \
        "Grid shape '{}' and size '{}' mismatch.".format(shape, size)
    assert attributes is not None, "Couldn't read column names."
    if usecols is not None:
        attributes = [attributes[i] for i in usecols]
    assert len(attributes) == rawdata.shape[0], \
        "Number of attributes ({}) and data columns ({}) mismatch".format(
            len(attributes), rawdata.shape[0])
    assert all(i is not None for i in area), "Couldn't read the grid area."
    if 'latitude' in attributes and 'longitude' in attributes:
        lat, lon = data['latitude'], data['longitude']
        area = (lat.min(), lat.max(), lon.min(), lon.max())
        assert np.allclose(area, data['area']), \
            "Grid area in header ({}) and calculated ({}) mismatch.".format(
                data['area'], area)

    return data
