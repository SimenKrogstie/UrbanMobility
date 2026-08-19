base_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]


def building_type_color_mapping(building_types: list[str]) -> dict[str, str]:
    """
    Maps building types to colors.

    Parameters
    ----------
    building_types : list[str]
        List of unique building types.

    Returns
    -------
    dict[str, str]
        Dictionary mapping building types to colors.
    """
    color_mapping = {}
    for i, btype in enumerate(building_types):
        color_mapping[btype] = base_colors[i % len(base_colors)]
    return color_mapping
