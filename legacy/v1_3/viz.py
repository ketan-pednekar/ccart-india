import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors


def ccart_choropleth(
    gdf_districts,
    df_losses,
    district_col="District",
    loss_col="loss",
    state_filter=None,
    title="CCART District-Level Loss Map (USD)",
    cmap="OrRd",
    figsize=(10, 12),
    save_path=None
):
    """
    Create a district-level choropleth for CCART losses (USD).
    Robust to:
    - lowercase/uppercase district names
    - missing or corrupted names
    - zero-loss cases
    - invalid geometries
    """

    # ------------------------------------------------------------
    # 0. Copy to avoid modifying original
    # ------------------------------------------------------------
    gdf = gdf_districts.copy()

    # ------------------------------------------------------------
    # 1. Normalize district key in both tables
    # ------------------------------------------------------------
    if district_col not in gdf.columns:
        raise KeyError(
            f"district_col='{district_col}' not found in gdf_districts. "
            f"Available columns: {list(gdf.columns)}"
        )

    if district_col not in df_losses.columns:
        raise KeyError(
            f"district_col='{district_col}' not found in df_losses. "
            f"Available columns: {list(df_losses.columns)}"
        )

    gdf[district_col] = (
        gdf[district_col].astype(str).str.strip().str.upper()
    )
    df_losses[district_col] = (
        df_losses[district_col].astype(str).str.strip().str.upper()
    )

    # ------------------------------------------------------------
    # 2. Optional state filter
    # ------------------------------------------------------------
    if state_filter:
        if "state" not in gdf.columns:
            raise KeyError("Column 'state' not found in gdf_districts.")

        gdf["state_norm"] = (
            gdf["state"].astype(str).str.strip().str.upper()
        )
        state_norm = state_filter.strip().upper()

        gdf = gdf[gdf["state_norm"] == state_norm]

        if gdf.empty:
            raise ValueError(
                f"No districts found for state_filter='{state_filter}'. "
                f"Check spelling or normalization."
            )

    # ------------------------------------------------------------
    # 3. Merge CCART losses into district GeoDataFrame
    # ------------------------------------------------------------
    gdf = gdf.merge(df_losses, on=district_col, how="left")

    # ------------------------------------------------------------
    # 4. Replace missing losses with zero
    # ------------------------------------------------------------
    gdf[loss_col] = gdf[loss_col].fillna(0)

    # ------------------------------------------------------------
    # 5. Ensure geometries are valid
    # ------------------------------------------------------------
    if not gdf.geometry.is_valid.all():
        gdf["geometry"] = gdf["geometry"].buffer(0)

    # ------------------------------------------------------------
    # 6. Logarithmic color scaling (avoid log(0))
    # ------------------------------------------------------------
    vmax = gdf[loss_col].max()
    vmin = max(gdf[loss_col].min(), 1)

    if vmax <= 0:
        raise ValueError(
            "All loss values are zero. Cannot create a LogNorm choropleth. "
            "Check your merge keys or CCART output."
        )

    norm = colors.LogNorm(vmin=vmin, vmax=vmax)

    # ------------------------------------------------------------
    # 7. Plot
    # ------------------------------------------------------------
    fig, ax = plt.subplots(1, 1, figsize=figsize)

    gdf.plot(
        column=loss_col,
        cmap=cmap,
        linewidth=0.2,
        edgecolor="grey",
        norm=norm,
        ax=ax,
        legend=True,
        legend_kwds={
            "label": "Economic Loss (USD)",
            "shrink": 0.6,
            "orientation": "vertical",
            "pad": 0.02
        }
    )

    # Center the map by adjusting axis limits
    bounds = gdf.total_bounds  # [xmin, ymin, xmax, ymax]
    xmid = (bounds[0] + bounds[2]) / 2
    ymid = (bounds[1] + bounds[3]) / 2
    xrange = bounds[2] - bounds[0]
    yrange = bounds[3] - bounds[1]

    ax.set_xlim(xmid - xrange / 2, xmid + xrange / 2)
    ax.set_ylim(ymid - yrange / 2, ymid + yrange / 2)

    ax.set_title(title, fontsize=16, loc="center")
    ax.axis("off")

    # ------------------------------------------------------------
    # 8. Save if requested
    # ------------------------------------------------------------
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()

    return gdf
