"""
CCART v1.0 — Exposure Module
----------------------------

This module handles all exposure-related operations for the CCART Cyclone
Impact Engine, including:

- Loading district boundaries
- Loading LitPop exposure (via CLIMADA API)
- Subsetting LitPop to a state
- Computing district-level exposure totals

These functions are reusable across states and cyclones.
"""

import geopandas as gpd
import pandas as pd
from climada.util.api_client import Client


def load_districts(path: str,
                   district_col: str = "District",
                   crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """
    Load district boundaries for a state.

    Parameters
    ----------
    path : str
        Path to district boundary file (GeoJSON, Shapefile, etc.).
    district_col : str
        Column containing district names.
    crs : str
        Coordinate reference system to enforce.

    Returns
    -------
    GeoDataFrame
        Standardized district polygons with columns:
        - District
        - geometry
    """
    gdf = gpd.read_file(path).to_crs(crs)
    gdf["District"] = gdf[district_col].astype(str).str.strip()
    return gdf[["District", "geometry"]].copy()


def load_litpop_for_state(country_code: str,
                          districts: gpd.GeoDataFrame,
                          cached_litpop=None):
    """
    Load LitPop for a country and subset to the given state's districts.

    Parameters
    ----------
    country_code : str
        ISO country code (e.g., "IND").
    districts : GeoDataFrame
        District polygons for the state.
    cached_litpop : GeoDataFrame or None
        Optional cached India-wide LitPop to avoid repeated API calls.

    Returns
    -------
    assets_state : GeoDataFrame
        LitPop exposure points within the state.
    district_exp : DataFrame
        District-level exposure totals.
    """
    if cached_litpop is None:
        client = Client()
        assets = client.get_litpop(country=country_code)
        litpop = gpd.GeoDataFrame(
            assets.gdf,
            geometry="geometry",
            crs="EPSG:4326"
        )
    else:
        litpop = cached_litpop

    litpop = litpop.to_crs(districts.crs)

    assets_state = gpd.sjoin(
        litpop,
        districts[["District", "geometry"]],
        how="inner",
        predicate="within"
    )

    district_exp = (
        assets_state.groupby("District")["value"]
        .sum()
        .reset_index()
        .rename(columns={"value": "Exposure_Value"})
    )

    return assets_state, district_exp


def compute_district_exposure(assets_state: pd.DataFrame,
                              value_col: str = "value") -> pd.DataFrame:
    """
    Aggregate exposure (LitPop) to district level.

    Parameters
    ----------
    assets_state : DataFrame
        Exposure points for the state, must include:
        - 'District' column
        - value column (e.g., 'value')
    value_col : str
        Column representing exposure magnitude.

    Returns
    -------
    DataFrame
        Columns: ['District', 'Exposure_Value']
    """
    exp_dist = (
        assets_state
        .groupby("District")[value_col]
        .sum()
        .reset_index()
        .rename(columns={value_col: "Exposure_Value"})
    )

    return exp_dist