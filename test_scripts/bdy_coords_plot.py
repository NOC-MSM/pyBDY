#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 11:28:04 2019.

@author: thopri
"""

# Hard file/folder paths in namelist file and in process_bdy call below need to be updated to suit user

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset

from pynemo.tests import bdy_coords as bdc

bdc.process_bdy("/Users/thopri/Projects/PyNEMO/inputs/namelist_remote.bdy", False)

rootgrp = Dataset(
    "/Users/thopri/Projects/PyNEMO/outputs/NNA_R12_bdyT_y1979m11.nc",
    "r",
    format="NETCDF4",
)
bdy_msk = np.squeeze(rootgrp.variables["bdy_msk"][:]) - 1
bdy_lon = np.squeeze(rootgrp.variables["nav_lon"][:])
bdy_lat = np.squeeze(rootgrp.variables["nav_lat"][:])
rootgrp.close()

rootgrp = Dataset(
    "/Users/thopri/Projects/PyNEMO/outputs/coordinates.bdy.nc", "r", format="NETCDF4"
)
bdy_it = np.squeeze(rootgrp.variables["nbit"][:])
bdy_jt = np.squeeze(rootgrp.variables["nbjt"][:])
bdy_rt = np.squeeze(rootgrp.variables["nbrt"][:])
rootgrp.close()

bdy_msk = np.ma.masked_where(bdy_msk < 0, bdy_msk)
for f in range(len(bdy_it)):
    bdy_msk[bdy_jt[f,], bdy_it[f,]] = bdy_rt[f,]

# Plot to check output
fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111)

map = Basemap(
    llcrnrlat=41.0,
    urcrnrlat=65.0,
    llcrnrlon=-22.0,
    urcrnrlon=25.0,
    rsphere=(6378137.00, 6356752.3142),
    resolution="l",
    projection="lcc",
    lat_1=57.0,
    lon_0=-12.5,
)
map.drawcoastlines()
map.drawcountries()
map.fillcontinents(color="grey")
map.drawmeridians(np.arange(-25.0, 25.0, 2), labels=[0, 0, 0, 1])
map.drawparallels(np.arange(40.0, 66.0, 2), labels=[1, 0, 0, 0])

cmap = plt.cm.get_cmap("jet", 10)
cmaplist = [cmap(i) for i in range(cmap.N)]
cmaplist[0] = (0.7, 0.7, 0.7, 1.0)
cmap = cmap.from_list("Custom cmap", cmaplist, cmap.N)

x1, y1 = map(bdy_lon[:, :], bdy_lat[:, :])
im = map.pcolormesh(x1, y1, bdy_msk, cmap=cmap, vmin=-0.5, vmax=9.5)
cb = plt.colorbar(
    orientation="vertical", shrink=0.75, aspect=30, fraction=0.1, pad=0.05
)
cb.set_label("RimWidth Number")
cb.set_ticks(np.arange(10))
th = plt.title(("BDY Points"), fontweight="bold")

plt.show()
