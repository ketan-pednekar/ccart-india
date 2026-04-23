"""
Module: interpolate_fsi_idw
CCART-Floods — IDW interpolation of point-based FSI_v1_2 to 0.05° India grid.
"""

import numpy as np
from scipy.spatial import cKDTree

def build_india_grid(res=0.05, min_lon=68, max_lon=98, min_lat=6, max_lat=37):
    lon = np.arange(min_lon, max_lon, res)
    lat = np.arange(min_lat, max_lat, res)
    grid_x, grid_y = np.meshgrid(lon, lat)
    return lon, lat, grid_x, grid_y

def idw_interpolation(x, y, z, xi, yi, power=2, k=8):
    tree = cKDTree(np.c_[x, y])
    dist, idx = tree.query(np.c_[xi.ravel(), yi.ravel()], k=k)
    dist = np.where(dist == 0, 1e-10, dist)
    weights = 1.0 / dist**power
    weights /= weights.sum(axis=1)[:, None]
    zi = np.sum(weights * z[idx], axis=1)
    return zi.reshape(xi.shape)

def interpolate_fsi_idw(gdf_fsi, res=0.05):
    lons = gdf_fsi["Longitude"].values
    lats = gdf_fsi["Latitude"].values
    fsi  = gdf_fsi["FSI_v1_2"].values

    lon, lat, grid_x, grid_y = build_india_grid(res=res)
    grid_fsi = idw_interpolation(lons, lats, fsi, grid_x, grid_y)

    # distance mask (~1° cutoff)
    tree = cKDTree(np.c_[lons, lats])
    dist_to_nearest, _ = tree.query(np.c_[grid_x.ravel(), grid_y.ravel()], k=1)
    dist_to_nearest = dist_to_nearest.reshape(grid_x.shape)
    grid_fsi[dist_to_nearest > 1.0] = np.nan

    return grid_fsi, lon, lat
