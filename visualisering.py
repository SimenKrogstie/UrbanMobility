from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import geopandas as gpd


def plot_mobilitetsindikatorer(
        mobilitet_gdf: gpd.GeoDataFrame,
        bydel_a: str,
        bydel_b: str
    ) -> Figure:
    """
    Plotter et sett mobilitetsindikatorer som barplott for to valgte bydeler.

    Funksjonen lager ett subplot per indikator og viser:
    - antall turer (start/slutt/netto/totalt)
    - turer per km^2
    - turer per innbygger
    - befolkningstetthet

    Negative indikatorer markeres i rødt, positive i rødt.

    Parameters
    ----------
    mobilitet_gdf : gpd.GeoDataFrame
        GeoDataFrame med mobilitetsindikatorer.
    bydel_a : str
        Navn på første bydel som skal sammenlignes.
    bydel_b : str
        Navn på andre bydel som skal sammenlignes.

    Returns
    -------
    fig : Figure
        Figur med subplots for hver indikator.
    
    Raises
    ------
    KeyError
        Hvis en av de oppgitte bydelene ikke finnes i "mobilitet_gdf.index".

    """
    # Sjekker at bydelene finnes
    for i in [bydel_a, bydel_b]:
        if i not in mobilitet_gdf.index:
            raise KeyError(f"Bydelen {i!r} finnes ikke i mobilitet_gdf.")
    
    # Filtrerer på de bydelene som er valgt
    df = mobilitet_gdf.loc[[bydel_a, bydel_b]].copy()

    # Indikatorer som skal visualiseres
    indikatorer = [
        "turer_startet", "turer_sluttet", "netto_turer", "turer_totalt",
        "turer_startet_per_km2", "turer_sluttet_per_km2", "netto_turer_per_km2", "totalt_turer_per_km2",
        "turer_startet_per_innbygger", "turer_sluttet_per_innbygger",
        "netto_turer_per_innbygger", "totalt_turer_per_innbygger",
        "befolkningstetthet_km2"
    ]

    bydeler = [bydel_a, bydel_b]

    # Størrelse for subplot
    n = len(indikatorer)
    cols = 4
    rows = int(np.ceil(n / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
    axes = axes.flatten()

    # Plotter hver indikator i hver sin subplot
    for i, ind in enumerate(indikatorer):
        ax = axes[i]

        values = df[ind].values
        colors= ["tab:red" if v < 0 else "green" for v in values]

        ax.bar(bydeler, values, color=colors, zorder=3)
        ax.set_title(ind.replace("_", " "), fontsize=11)
        ax.tick_params(axis="x", rotation=30)
        ax.grid(True, linestyle="--", alpha=0.6, zorder=0)

    # Sjuler tomme plots
    for j in range(i+1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    return fig


def plot_tidsprofil(
        turer_df: pd.DataFrame,
        bydel_a: str,
        bydel_b: str,
        start_col: str = "start_bydel",
        slutt_col: str = "slutt_bydel",
        tidskolonne: str = "started_at",
) -> Figure:
    """
    Plotter tidsprofiler (per time) for to bydeler:

    Funksjonen lager en figur med to subplots:
    - Venstre: antall turer per time som starter i hver bydel.
    - Høyre: antall turer per time som slutter i hver bydel.

    Parameters
    ----------
    turer_df : pd.DataFrame
        DataFrame med turdata.
    bydel_a : str
        Navn på første bydel som skal sammenlignes.
    bydel_b : str
        Navn på andre bydel som skal sammenlignes.
    start_col : str, optional
        Navn på kolonnen i "turer_df" med startbydel.
        Default er "start_bydel".
    slutt_col : str, optional
        Navn på kolonnen i "turer_df" med sluttbydel.
        Default er "slutt_bydel".
    tidskolonne : str, optional
        Navn på kolonnen i "turer_df" med starttidspunkt for turen.
        Default er "started_at".

    Returns
    -------
    fig : Figure
        Figure med to linjediagram med start og slutt per time. 
    
    Raises
    ------
    KeyError
        Hvis "start_col", "slutt_col" eller "tidskolonne" mangler i "turer_df".
    """
    df = turer_df.copy()

    # Sjekker at nødvendige kolonner finnes
    for col in [start_col, slutt_col, tidskolonne]:
        if col not in df.columns:
            raise KeyError(f"Kolonnen {col!r} mangler i turer_df.")

    # Sørger for datetime
    if not pd.api.types.is_datetime64_any_dtype(df[tidskolonne]):
        df[tidskolonne] = pd.to_datetime(df[tidskolonne], errors="coerce", utc=True)

    # Fjerner rader uten gyldig tid og legger til kolonne for tid på døgnet
    df = df.dropna(subset=[tidskolonne])
    df["time"] = df[tidskolonne].dt.hour

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), sharex=True)
    ax_start = axes[0]
    ax_slutt = axes[1]

    bydeler = [bydel_a, bydel_b]
    colors = ["tab:blue", "tab:orange"]

    # For start av turer
    for bydel, color in zip(bydeler, colors):
        df_start = df[df[start_col] == bydel]
        antall_start = df_start.groupby("time").size().reindex(range(24), fill_value=0)

        ax_start.plot(
            antall_start.index,
            antall_start.values,
            marker="o",
            color=color,
            label=f"{bydel}")
    
    ax_start.set_title("Turer som starter i bydelene")
    ax_start.set_xlabel("Time på døgnet")
    ax_start.set_ylabel("Antall turer")
    ax_start.grid(True, linestyle="--", alpha=0.6)
    ax_start.legend(title="Bydel")

    # For slutt av turer
    for bydel, color in zip(bydeler, colors):
        df_slutt = df[df[slutt_col] == bydel]
        antall_slutt = df_slutt.groupby("time").size().reindex(range(24), fill_value=0)
        
        ax_slutt.plot(
            antall_slutt.index,
            antall_slutt.values,
            marker="o",
            color=color,
            label=f"{bydel}")
    
    ax_slutt.set_title("Turer som slutter i bydelene")
    ax_slutt.set_xlabel("Time på døgnet")
    ax_slutt.set_ylabel("Antall turer")
    ax_slutt.grid(True, linestyle="--", alpha=0.6)
    ax_slutt.legend(title="Bydel")

    plt.tight_layout()
    return fig


def plot_tidsprofil_retninger(
        turer_df: pd.DataFrame,
        bydel_a: str,
        bydel_b: str,
        start_col: str = "start_bydel",
        slutt_col: str = "slutt_bydel",
        tidskolonne: str = "started_at",
) -> Figure:
    """
    Plotter tidsprofilen (per time) for turer mellom to bydeler i begge retninger:
    
    To linjer plottes:
    - turer fra bydel_a til bydel_b
    - turer fra bydel_b til bydel_a

    Parameters
    ----------
    turer_df : pd.DataFrame
        DataFrame med turdata.
    bydel_a : str
        Navn på første bydel som skal sammenlignes.
    bydel_b : str
        Navn på andre bydel som skal sammenlignes.
    start_col : str, optional
        Navn på kolonnen i "turer_df" med startbydel.
        Default er "start_bydel".
    slutt_col : str, optional
        Navn på kolonnen i "turer_df" med sluttbydel.
        Default er "slutt_bydel".
    tidskolonne : str, optional
        Navn på kolonnen i "turer_df" med starttidspunkt for turen.
        Default er "started_at".
    
    Returns
    -------
    fig : Figure
        Figur med tidsprofil for begge retninger.
    
    Raises
    ------
    KeyError
        Hvis nødvendige kolonner mangler i "turer_df".
    """
    df = turer_df.copy()

    # Sjekker nødvendige kolonner
    for col in [start_col, slutt_col, tidskolonne]:
        if col not in df.columns:
            raise KeyError(f"Kolonnen {col!r} mangler i turer_df.")
    
    # Sørger for datetime
    if not pd.api.types.is_datetime64_any_dtype(df[tidskolonne]):
        df[tidskolonne] = pd.to_datetime(df[tidskolonne], errors="coerce", utc=True)
    
    # Fjerner rader uten gyldig tid og legger til kolonne for tid på døgnet
    df = df.dropna(subset=[tidskolonne])
    df["time"] = df[tidskolonne].dt.hour

    fig, ax = plt.subplots(figsize=(10,5))

    # Definerer retninger
    retninger = [
        (bydel_a, bydel_b, "tab:blue"),
        (bydel_b, bydel_a, "tab:orange")
    ]

    for start_bydel, slutt_bydel, color in retninger:
        df_dir = df[(df[start_col] == start_bydel) & (df[slutt_col] == slutt_bydel)]
        antall = df_dir.groupby("time").size().reindex(range(24), fill_value=0)

        ax.plot(
            antall.index,
            antall.values,
            marker="o",
            color=color,
            label=f"{start_bydel} -> {slutt_bydel}"
        )
    
    ax.set_xlabel("Time på døgnet")
    ax.set_ylabel("Antall turer")
    ax.set_title(f"Tidsprofil for turer mellom {bydel_a} og {bydel_b}")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    
    return fig


def plot_bygningsindikatorer(
        bygningsindikatorer_gdf: gpd.GeoDataFrame,
        bydel_a: str,
        bydel_b: str
) -> Figure:
    """
    Visualiserer bygningsindikatorer med barplott for to valgte bydeler.

    Funksjonen lager et rutenett av barplott hvor hver indikator vises for
    bydel_a og bydel_b. Farger markerer evt. negative verdier (rød) eller
    positive (grønn).

    Indikatorene som plottes er:
    - antall bygninger
    - bygningareal (m^2)
    - antall bygninger per km^2
    - bebygd areal i prosent
    - gjennomsnittlig størrelse på bygninger (m^2)

    Parameters
    ----------
    bygningsindikatorer_gdf : gpd.GeoDataFrame
        GeoDataFrame med bygningsindikatorer.
    bydel_a : str
        Navn på første bydel som skal sammenlignes.
    bydel_b : str
        Navn på andre bydel som skal sammenlignes.

    Returns
    -------
    fig : Figure
        Figur med barplott for hver indikator.
    
    Raises
    ------
    KeyError
        Hvis en av bydelene eller indikatorene ikke finnes. 
    """

    # Sjekker at bydeler finnes
    for i in [bydel_a, bydel_b]:
        if i not in bygningsindikatorer_gdf.index:
            raise KeyError(f"Bydelen {i!r} finnes ikke i bygningsindikatorer_gdf.")
    
    df = bygningsindikatorer_gdf.loc[[bydel_a, bydel_b]].copy()

    indikatorer = [
        "antall_bygninger",
        "bygning_areal_m2",
        "bygninger_per_km2",
        "bebygd_areal_prosent",
        "avg_bygning_areal_m2"
    ]

    # Sjekker at alle indikatorer finnes 
    for col in indikatorer:
        if col not in bygningsindikatorer_gdf.columns:
            raise KeyError(f"Kolonnen {col!r} finnes ikke i GeoDataFrame.")

    bydeler = [bydel_a, bydel_b]
    
    # Størrelse på subplot
    n = len(indikatorer)
    cols = 3
    rows = int(np.ceil(n / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
    axes = axes.flatten()

    # Plotter indikatorene
    for i, ind in enumerate(indikatorer):
        ax = axes[i]

        values = df[ind].values
        colors = ["tab:red" if v < 0 else "green" for v in values]

        ax.bar(bydeler, values, color=colors, zorder=3)
        ax.set_title(ind.replace("_", " "), fontsize=11)
        ax.tick_params(axis="x", rotation=30)
        ax.grid(True, linestyle="--", alpha=0.6, zorder=0)

    # Skjuler tomme plots
    for j in range(i+1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    return fig


def plot_bygningstyper(
        bygninger_gdf: gpd.GeoDataFrame,
        bydel_a: str,
        bydel_b: str,
        bydel_col: str = "bydel",
        type_col: str = "building",
        typer: list[str] | None = None,
        normalize: bool = False,
) -> Figure:
    """
    Plotter fordeling av bygningstyper for to valgte bydeler.
    
    For hver bydel lages et stolpediagram der hver stolpe representerer én
    bygningstype, og farger er konsistente på tvers av bydeler.

    Hvis "normalize=True", plottes andeler i prosent i stedet for antall.

    Parameters
    ----------
    bygninger_gdf : gpd.GeoDataFrame
        GeoDataFrame med bygninger.
    bydel_a : str
        Navn på første bydel som skal sammenlignes.
    bydel_b : str
        Navn på andre bydel som skal sammenlignes.
    bydel_col : str, optional
        Navn på kolonne i "bygninger_gdf" med bydelnavn.
        Default er "bydel".
    type_col : str, optional
        Navn på kolonne for bygningstype (f.eks. OSM "building"-tag).
        Default er "building".
    typer : list of str or None, optional
        Liste over bygningstyper som skal inkluderes i plottet. 
        Hvis None brukes alle bygningstyper som forekommer i dataene.
    normalize : bool, optional
        Hvis True normaliseres stolpene til prosentandel per bydel.
        Hvis False plottes antall bygninger.
        Default er False.

    Returns
    -------
    fig : Figure
        Figur som viser fordeling av bygningstyper per bydel.
    
    Raises 
    ------
    KeyError
        Hvis "bydel_col" eller "type_col" mangler i "bygninger_gdf",
        eller hvis en av de oppgitte bydelene ikke finnes i datasettet.
    ValueError
        Hvis ingen bygningstyper gjenstår etter filtrering.
    """

    # Sjekker at kolonnene finnes
    if bydel_col not in bygninger_gdf.columns:
        raise KeyError(f"Fant ikke kolonnen {bydel_col!r}.")
    if type_col not in bygninger_gdf.columns:
        raise KeyError(f"Fant ikke kolonnen {type_col!r}.")
    
    # Sjekker at bydelene finnes
    fokus = [bydel_a, bydel_b]
    for b in fokus:
        if b not in bygninger_gdf[bydel_col].unique():
            raise KeyError(f"Bydelen {b!r} finnes ikke i datasettet.")

    # Filtrerer til valgte bydeler og håndterer manglende bygningstype
    df = bygninger_gdf.copy()
    df[type_col] = df[type_col].fillna("ukjent")
    df = df[df[bydel_col].isin(fokus)]

    # Teller relevante bygningstyper
    total_counts = df[type_col].value_counts()

    if typer is not None:
        typer = [t for t in typer if total_counts.get(t, 0) > 0]
    else:
        typer = [t for t, c in total_counts.items() if c > 0]

    if len(typer) == 0:
        raise ValueError("Ingen bygningstyper å vise etter filtrering.")

    # Fargemapping
    base_colors = [
        "#1b9e77", "#d95f02", "#7570b3", "#e7298a",
        "#66a61e", "#e6ab02", "#a6761d", "#666666",
        "#1f78b4", "#b2df8a", "#fb9a99", "#cab2d6"
    ]
    type_to_color = {t: base_colors[i % len(base_colors)] for i, t in enumerate(typer)}

    fig, axes = plt.subplots(2, 1, figsize=(9, 5), sharex=True, sharey=not normalize)
    axes = axes.flatten()

    # Lager plott for hver bydel
    for ax, bydel in zip(axes, fokus):
        subset = df[df[bydel_col] == bydel]

        counts = subset[type_col].value_counts().reindex(typer, fill_value=0)

        if normalize:
            total = counts.sum()
            if total > 0:
                counts = counts / total * 100

        colors = [type_to_color[t] for t in counts.index]

        ax.bar(counts.index, counts.values, color=colors, edgecolor="black")

        ax.set_title(f"Bygningstyper i {bydel}" + (" (%)" if normalize else ""), fontsize=13)
        ax.set_ylabel("Prosent" if normalize else "Antall bygninger")
        ax.tick_params(axis="x", rotation=45)

        ax.grid(True, linestyle="--", alpha=0.6, zorder=0)

    plt.tight_layout()
    return fig