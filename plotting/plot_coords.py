#!/usr/bin/env python3

import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from mpl_toolkits.basemap import Basemap
import sys

rootgrp = Dataset(str(sys.argv[1]), "r", format="NETCDF4")
bdy_msk = np.squeeze(rootgrp.variables['bdy_msk'][:]) - 1
bdy_lon = np.squeeze(rootgrp.variables['nav_lon'][:])
bdy_lat = np.squeeze(rootgrp.variables['nav_lat'][:])
rootgrp.close()

rootgrp = Dataset(str(sys.argv[2]), "r", format="NETCDF4")
bdy_it = np.squeeze(rootgrp.variables['nbit'][:])
bdy_jt = np.squeeze(rootgrp.variables['nbjt'][:])
bdy_rt = np.squeeze(rootgrp.variables['nbrt'][:])
rootgrp.close()

bdy_msk = np.ma.masked_where(bdy_msk < 0, bdy_msk)
for f in range(len(bdy_it)):
    bdy_msk[bdy_jt[f,],bdy_it[f,]] = bdy_rt[f,]

# Plot to check output
fig=plt.figure(figsize=(8,8))
ax=fig.add_subplot(111)

map = Basemap(llcrnrlat=37.,urcrnrlat=67.,\
            llcrnrlon=-25.,urcrnrlon=10.,\
            rsphere=(6378137.00,6356752.3142),\
            resolution='l',projection='lcc',\
            lat_1=57.,lon_0=-12.5)
map.drawcoastlines()
map.drawcountries()
map.fillcontinents(color='grey')
map.drawmeridians(np.arange(-25.,10.,5),labels=[0,0,0,1])
map.drawparallels(np.arange(38.,66.,2),labels=[1,0,0,0])

cmap = plt.cm.get_cmap('jet',10)
cmaplist = [cmap(i) for i in range(cmap.N)]
cmaplist[0] = (.7,.7,.7,1.0)
cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)

x1,y1 = map(bdy_lon[:,:],bdy_lat[:,:])
im = map.pcolormesh(x1, y1, bdy_msk, cmap=cmap, vmin=-0.5, vmax=9.5)
cb = plt.colorbar(orientation='vertical', shrink=0.75, aspect=30, fraction=0.1,pad=0.05)
cb.set_label('RimWidth Number')
cb.set_ticks(np.arange(10))
th=plt.title(('BDY Points'),fontweight='bold')
fig.savefig('coords.png')
