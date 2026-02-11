import geopandas as gpd
import matplotlib.pyplot as plt

def ccart_choropleth_v2(
    gdf_districts: gpd.GeoDataFrame,
    df_losses,
    district_col: str = "District",
    loss_col: str = "loss_usd_hwe",
    state_filter=None,
    title: str = "",
    save_path: str | None = None,
    cmap: str = "Reds",
):
    """
    CCART v2 choropleth:
    - Robust to geometry_x / geometry_y
    - Handles duplicate loss columns (loss_x, loss_y)
    - Works with district-level or district-based state maps
    - df_losses should contain only merge key + loss column
    """

    # ------------------------------------------------------------
    # 1. Ensure gdf_districts is a proper GeoDataFrame
    # ------------------------------------------------------------
    if not isinstance(gdf_districts, gpd.GeoDataFrame):
        raise TypeError("gdf_districts must be a GeoDataFrame with geometry.")

    if gdf_districts.geometry.name != "geometry":
        gdf_districts = gdf_districts.set_geometry("geometry")

    # ------------------------------------------------------------
    # 2. Clean df_losses (remove geometry if present)
    # ------------------------------------------------------------
    df_losses = df_losses.copy()
    if "geometry" in df_losses.columns:
        df_losses = df_losses.drop(columns=["geometry"])

    # ------------------------------------------------------------
    # 3. Merge districts + losses
    # ------------------------------------------------------------
    gdf = gdf_districts.merge(df_losses, on=district_col, how="left")

    # ------------------------------------------------------------
    # 4. FIX DUPLICATE LOSS COLUMNS (critical)
    # ------------------------------------------------------------
    loss_x = f"{loss_col}_x"
    loss_y = f"{loss_col}_y"

    if loss_x in gdf.columns and loss_y in gdf.columns:
        # Prefer the right-hand side (df_losses)
        gdf[loss_col] = gdf[loss_y]
        gdf = gdf.drop(columns=[loss_x, loss_y])

    # If only one exists, rename it to the clean name
    elif loss_x in gdf.columns:
        gdf = gdf.rename(columns={loss_x: loss_col})
    elif loss_y in gdf.columns:
        gdf = gdf.rename(columns={loss_y: loss_col})

    # ------------------------------------------------------------
    # 5. Fix geometry after merge
    # ------------------------------------------------------------
    geom_cols = [c for c in gdf.columns if c.startswith("geometry")]

    if "geometry_x" in geom_cols:
        gdf = gdf.set_geometry("geometry_x")
        gdf = gdf.drop(columns=[c for c in geom_cols if c != "geometry_x"])
        gdf = gdf.rename(columns={"geometry_x": "geometry"})

    elif "geometry_y" in geom_cols:
        gdf = gdf.set_geometry("geometry_y")
        gdf = gdf.drop(columns=[c for c in geom_cols if c != "geometry_y"])
        gdf = gdf.rename(columns={"geometry_y": "geometry"})

    else:
        gdf = gdf.set_geometry("geometry")

    gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs=gdf_districts.crs)

    # ------------------------------------------------------------
    # 6. Optional state filter
    # ------------------------------------------------------------
    if state_filter is not None and "state" in gdf.columns:
        if isinstance(state_filter, str):
            state_filter = [state_filter]
        gdf = gdf[gdf["state"].isin(state_filter)].copy()

    # ------------------------------------------------------------
    # 7. Clean geometry
    # ------------------------------------------------------------
    gdf["geometry"] = gdf["geometry"].buffer(0)

    # ------------------------------------------------------------
    # 8. Ensure loss column exists
    # ------------------------------------------------------------
    if loss_col not in gdf.columns:
        raise KeyError(
            f"Loss column '{loss_col}' not found after merge. "
            f"Available columns: {list(gdf.columns)}"
        )

    # ------------------------------------------------------------
    # 9. Plot
    # ------------------------------------------------------------
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    gdf.plot(
        column=loss_col,
        ax=ax,
        cmap=cmap,
        legend=True,
        edgecolor="black",
        linewidth=0.2,
        missing_kwds={"color": "lightgrey", "label": "No data"},
    )

    ax.set_title(title, fontsize=14)
    ax.set_axis_off()

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.close(fig)

