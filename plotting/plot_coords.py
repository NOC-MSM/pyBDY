#!/usr/bin/env python3
"""
Plot the domain boundaries and show the different locations of the rim width.

Map showing location of boundaries. Rim width number increases inwards.
Benchmark data example useage:
python plotting/plot_coords.py outputs/NNA_R12_bdyT_y1979m11.nc outputs/coordinates.bdy.nc
"""
import sys

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset

# Read the input data
rootgrp = Dataset(str(sys.argv[1]), "r", format="NETCDF4")
bdy_msk = np.squeeze(rootgrp.variables["bdy_msk"][:]) - 1
bdy_lon = np.squeeze(rootgrp.variables["nav_lon"][:])
bdy_lat = np.squeeze(rootgrp.variables["nav_lat"][:])
rootgrp.close()

rootgrp = Dataset(str(sys.argv[2]), "r", format="NETCDF4")
bdy_it = np.squeeze(rootgrp.variables["nbit"][:])
bdy_jt = np.squeeze(rootgrp.variables["nbjt"][:])
bdy_rt = np.squeeze(rootgrp.variables["nbrt"][:])
rootgrp.close()

# Mask the invalid values
bdy_msk = np.ma.masked_where(bdy_msk < 0, bdy_msk)

# Update the values in the mask
for f in range(len(bdy_it)):
    bdy_msk[bdy_jt[f,], bdy_it[f,]] = bdy_rt[f,]

# Define the projection
crs = ccrs.LambertConformal(central_latitude=57.0, central_longitude=-12.5)

# Create a figure and axes
fig = plt.figure()
ax = fig.add_subplot(111, projection=crs)

# Plot the data
cs1 = ax.pcolormesh(
    bdy_lon[:, :],
    bdy_lat[:, :],
    bdy_msk,
    cmap="jet",
    vmin=-0.5,
    vmax=9.5,
    transform=crs,
)

# Add geographic features
ax.add_feature(
    cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
        edgecolor="black",
        alpha=0.7,
        facecolor=cfeature.COLORS["land"],
    )
)

# Coordinates to limit map area
bounds = [-25, 20, 37, 67]
ax.set_extent(bounds, crs=crs)

# Add a title and labels
ax.set_title("BDY Points")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# Add gridlines
gl = ax.gridlines(
    crs=ccrs.PlateCarree(),
    draw_labels=True,
    linewidth=2,
    color="gray",
    alpha=0.5,
    linestyle="--",
)
gl.top_labels = False
gl.right_labels = False

# Add a colorbar
cb = plt.colorbar(
    cs1, orientation="vertical", shrink=0.75, aspect=30, fraction=0.1, pad=0.05
)
cb.set_label("RimWidth Number")
cb.set_ticks(np.arange(10))

# Save the figure
fig.savefig("coords.png")
