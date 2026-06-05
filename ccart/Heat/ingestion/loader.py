"""
CCART-Heat Ingestion Module (0.05° India grid, Big-BBox Safe Version)
With center-affine georeferencing + strict-mask utility (not applied here)
"""

import xarray as xr
import geopandas as gpd
import numpy as np
from pathlib import Path
from affine import Affine
import rasterio.features
from ccart.Heat.config import load_heat_paths


# ---------------------------------------------------------
# Load paths
# ---------------------------------------------------------
p = load_heat_paths()

DATA_ROOT     = Path(p["data_root"])
BOUNDARY_FILE = Path(p["boundaries"]["districts"])

HIST_OUT   = Path(p["ingested"]["hist"])
SSP370_OUT = Path(p["ingested"]["ssp370"])
SSP585_OUT = Path(p["ingested"]["ssp585"])

HIST_OUT.mkdir(parents=True, exist_ok=True)
SSP370_OUT.mkdir(parents=True, exist_ok=True)
SSP585_OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# BIG SAFE BBOX for ACCESS-CM2 (raw subset)
# ---------------------------------------------------------
RAW_LON_MIN = 60
RAW_LON_MAX = 105
RAW_LAT_MIN = 0
RAW_LAT_MAX = 40

# ---------------------------------------------------------
# Canonical 0.05° India grid (same as Flood)
# ---------------------------------------------------------
CAN_LON_MIN = 67.95
CAN_LON_MAX = 98.05
CAN_LAT_MIN = 5.95
CAN_LAT_MAX = 38.05

RES = 0.05

lon_target = np.arange(CAN_LON_MIN, CAN_LON_MAX + RES, RES)
lat_target = np.arange(CAN_LAT_MIN, CAN_LAT_MAX + RES, RES)

TARGET_GRID = xr.Dataset(coords=dict(lon=("lon", lon_target),
                                     lat=("lat", lat_target)))


# ---------------------------------------------------------
# Strict India mask utility (center-affine)
# ---------------------------------------------------------
def make_strict_mask(template_da, india_shp_path):
    """
    Create a strict India mask aligned to template_da using CENTER-AFFINE.
    Not applied during ingestion — used in hazard engines.
    """
    india = gpd.read_file(india_shp_path)
    india_union = india.unary_union

    lat = template_da.lat.values
    lon = template_da.lon.values

    dlat = float(lat[1] - lat[0])
    dlon = float(lon[1] - lon[0])

    transform = Affine(
        dlon, 0, lon.min() - dlon/2,
        0, dlat, lat.min() - dlat/2
    )

    out_shape = (len(lat), len(lon))

    mask = rasterio.features.rasterize(
        [(india_union, 1)],
        out_shape=out_shape,
        transform=transform,
        fill=0,
        all_touched=True
    )

    return xr.DataArray(
        mask.astype("uint8"),
        coords={"lat": lat, "lon": lon},
        dims=("lat", "lon"),
        name="strict_mask"
    )


# ---------------------------------------------------------
# Attach center-affine transform to dataset
# ---------------------------------------------------------
def attach_center_affine(ds):
    lat = ds.lat.values
    lon = ds.lon.values

    dlat = float(lat[1] - lat[0])
    dlon = float(lon[1] - lon[0])

    transform = Affine(
        dlon, 0, lon.min() - dlon/2,
        0, dlat, lat.min() - dlat/2
    )

    ds = ds.rio.write_transform(transform)
    ds = ds.rio.write_crs("EPSG:4326")
    return ds


# ---------------------------------------------------------
# Generic loader
# ---------------------------------------------------------
def load_raw(files):
    return xr.open_mfdataset(
        files,
        combine="by_coords",
        parallel=True,
        engine="h5netcdf",
        chunks={"time": 365}
    )


# ---------------------------------------------------------
# RH correction helper
# ---------------------------------------------------------
def fix_relative_humidity(ds_hurs):
    rh_max = float(ds_hurs["hurs"].max())
    if rh_max <= 1.5:
        ds_hurs["hurs"] *= 100
    ds_hurs["hurs"] = ds_hurs["hurs"].clip(0, 100)
    return ds_hurs


# ---------------------------------------------------------
# Regrid to canonical 0.05° India grid
# ---------------------------------------------------------
def regrid_to_india_005(ds):
    ds = ds.sel(
        lon=slice(RAW_LON_MIN, RAW_LON_MAX),
        lat=slice(RAW_LAT_MIN, RAW_LAT_MAX)
    )
    return ds.interp(lon=lon_target, lat=lat_target, method="linear")


# ---------------------------------------------------------
# Clip to canonical India box AFTER regridding
# ---------------------------------------------------------
def clip_to_india(ds):
    return ds.sel(
        lon=slice(CAN_LON_MIN, CAN_LON_MAX),
        lat=slice(CAN_LAT_MIN, CAN_LAT_MAX)
    )


# ---------------------------------------------------------
# Main ingestion function
# ---------------------------------------------------------
def load_hist_and_future():

    CHUNKS = {"time": 30, "lat": 200, "lon": 200}

    # If ingestion exists, load directly
    if (HIST_OUT / ".zmetadata").exists() and \
       (SSP370_OUT / ".zmetadata").exists() and \
       (SSP585_OUT / ".zmetadata").exists():

        print("Loaded CCART-Heat ingestion from ingested/ folder.")

        ds_hist = xr.open_zarr(HIST_OUT).chunk(CHUNKS)
        ds_370  = xr.open_zarr(SSP370_OUT).chunk(CHUNKS)
        ds_585  = xr.open_zarr(SSP585_OUT).chunk(CHUNKS)

        return (
            ds_hist["tasmax"], ds_hist["hurs"],
            ds_370["tasmax"],  ds_370["hurs"],
            ds_585["tasmax"],  ds_585["hurs"]
        )

    print("Running full CCART-Heat ingestion (BIG-BBOX safe version)...")

    # -----------------------------------------------------
    # Historical
    # -----------------------------------------------------
    hist_tasmax_files = sorted((DATA_ROOT / "historical" / "tasmax").glob("*.nc"))
    hist_hurs_files   = sorted((DATA_ROOT / "historical" / "hurs").glob("*.nc"))

    ds_hist_tasmax = load_raw(hist_tasmax_files)
    ds_hist_hurs   = fix_relative_humidity(load_raw(hist_hurs_files))

    common_time = np.intersect1d(ds_hist_tasmax.time.values,
                                 ds_hist_hurs.time.values)

    ds_hist_tasmax = ds_hist_tasmax.sel(time=common_time)
    ds_hist_hurs   = ds_hist_hurs.sel(time=common_time)

    ds_hist_tasmax, ds_hist_hurs = xr.align(ds_hist_tasmax, ds_hist_hurs, join="inner")

    ds_hist_tasmax_05 = clip_to_india(regrid_to_india_005(ds_hist_tasmax))
    ds_hist_hurs_05   = clip_to_india(regrid_to_india_005(ds_hist_hurs))

    # -----------------------------------------------------
    # SSP370
    # -----------------------------------------------------
    ssp370_tasmax_files = sorted((DATA_ROOT / "ssp370" / "tasmax").glob("*.nc"))
    ssp370_hurs_files   = sorted((DATA_ROOT / "ssp370" / "hurs").glob("*.nc"))

    ds_370_tasmax_05 = clip_to_india(regrid_to_india_005(load_raw(ssp370_tasmax_files)))
    ds_370_hurs_05   = clip_to_india(regrid_to_india_005(fix_relative_humidity(load_raw(ssp370_hurs_files))))

    # -----------------------------------------------------
    # SSP585
    # -----------------------------------------------------
    ssp585_tasmax_files = sorted((DATA_ROOT / "ssp585" / "tasmax").glob("*.nc"))
    ssp585_hurs_files   = sorted((DATA_ROOT / "ssp585" / "hurs").glob("*.nc"))

    ds_585_tasmax_05 = clip_to_india(regrid_to_india_005(load_raw(ssp585_tasmax_files)))
    ds_585_hurs_05   = clip_to_india(regrid_to_india_005(fix_relative_humidity(load_raw(ssp585_hurs_files))))

    # -----------------------------------------------------
    # Build final datasets + attach center-affine
    # -----------------------------------------------------
    ds_hist = attach_center_affine(xr.Dataset({
        "tasmax": ds_hist_tasmax_05["tasmax"],
        "hurs":   ds_hist_hurs_05["hurs"]
    })).chunk(CHUNKS)

    ds_370 = attach_center_affine(xr.Dataset({
        "tasmax": ds_370_tasmax_05["tasmax"],
        "hurs":   ds_370_hurs_05["hurs"]
    })).chunk(CHUNKS)

    ds_585 = attach_center_affine(xr.Dataset({
        "tasmax": ds_585_tasmax_05["tasmax"],
        "hurs":   ds_585_hurs_05["hurs"]
    })).chunk(CHUNKS)

    # -----------------------------------------------------
    # Write to ingested folder
    # -----------------------------------------------------
    ds_hist.to_zarr(HIST_OUT, mode="w")
    ds_370.to_zarr(SSP370_OUT, mode="w")
    ds_585.to_zarr(SSP585_OUT, mode="w")

    print("CCART-Heat ingestion completed successfully (BIG-BBOX + center-affine).")

    return (
        ds_hist["tasmax"], ds_hist["hurs"],
        ds_370["tasmax"],  ds_370["hurs"],
        ds_585["tasmax"],  ds_585["hurs"]
    )


if __name__ == "__main__":
    load_hist_and_future()

