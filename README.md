# Urban Mobility and Building Indicators: An analysis of Bike-Sharing Usage and Urban Structure in Ullern and Grünerløkka

The purpose of this project is to investigate how urban mobility patterns derived from bike-sharing data
relate to land-use structure and building typologies across different districts in Oslo. 
Using spatial analysis, mobility indicators, and building data from OpenStreetMap, 
the project examines how variations in urban form influence bike-sharing usage.

The analysis addresses the following research questions:

1. How does the level of mobility differ between Ullern and Grünerløkka, and which 
   indicators most clearly capture these differences?
2. Can observed variations in mobility be explained by differences in population density,
   building structure, or land-use mix?
3. What do the daily usage profiles of bike-sharing look like in the two districts, and which
   commuting patterns can be identified?
4. How are these relationships represented in an interactive map that combines 
   mobility indicators and building typologies?



A complete Jupyter Notebook (`analysis.ipynb`) demonstrates the use of all implemented functions 
and contains the full analysis, visualizations, and interpretation of results.
 A discussion of the findings is provided further down in this README.



---

## Project Structure

The project directory contains the following files:

```text
Project/
├── data/
│   ├── oslo_bydeler_befolkning_2024.geojson   # Population and district data
│   └── sykkel_oktober_2025.csv                # Bike trip data
│
├── analysis.ipynb                             # Main analysis and visualizations
│
├── data_processing.py                         # Spatial joins, point conversion, OSM building retrieval
├── helpers.py                                 # CRS utility functions
├── indicators.py                              # Mobility and building indicators
├── data_reading.py                            # Data loading functions
├── map.py                                     # Interactive Folium map
├── visulization.py                            # Plotting functions for indicators and time profiles
│
└── README.md                                  # Project documentation
```

---


## Installation

The project relies exclusively on packages included in the **gmgi221** conda environment.
All required dependencies are defined in `gmgi221.yml`.

#### Create and activate the conda environment
```bash
conda env create -f gmgi221.yml
conda activate gmgi221
```

---

## Running the Project

1. Open a terminal and navigate to the project directory.
2. Start JupyterLab.
3. Open and run the notebook analyse.ipynb

### Notebook Functionality

The notebook performs the following tasks:

- loads and preprocesses datasets
- computes mobility- and building-related indicators
- analyzes temporal usage profiles
- visualizes indicators using bar charts
- generates an interactive map using Folium
- compares results between Ullern and Grünerløkka


---

## Functions
### data_reading.py
- csv_to_df() – Reads bike trip data and handles data types
- data_to_gdf() – Loads geospatial data (Shapefile, GeoJSON, etc.)

### data_processing.py
- points_gdf() – Converts latitude/longtitude coordinates to point geometries
- add_district() – Performs spatial join between points and district polygons
- fetch_buildings() – Retrieves building data from OSM and clips it to district boundaries

### indicators.py
- mobilityindicators() – Computes inbound/outbound trips, per km² and per capita
- buildingindicators() – Computes building counts, building area and density

### visualization.py
- plot_mobility_indicators() – Bar plots of mobility indicators
- plot_timeprofile() – Daily profile of trip start times
- plot_timeprofile_directions() – Trips between two districts over the course of the day
- plot_building_indicators() – Comparison of building indicators
- plot_buildingtypes() – Percentage distribution of building types

### map.py
- interactive_map() - Choropleth map combined with building typologies using Folium


---

## Datasets

The following datasets are used in the analysis:
- **Bike-Sharing Trips (Oslo Bysykkel / UIP)**
   Trip data from October 2025, including start and end coordinates, timestamps, and station information. Used to compute mobility indicators.
   Link: https://oslobysykkel.no/apne-data/historisk

- **Buildings (OpenStreetMap via OSMnx)**
   Building footprints and building types within the two selected districts. Used for building indicators and map layers.

- **Population and District Boundaries (SSB / Oslo Municipality)**
   Population counts per district (2024), used for per-capita indicators, mapping, and associating trip start/end points and building with districts.
   link: https://kart.ssb.no/wayfinder/default?x=23.514300&y=67.351581&z=3.6

All datasets are reprojected to **EPSG:25833 (UTM 33N)** to ensure accurate area calculations.


---

## Methology
The analysis combines data preprocessing, indicator computation, visualization, and consist of the following steps:

1. **Data Preprocessing**
   - Load CSV and GeoJSON/GPKG-data
   - Reproject data to a common coordinate referance system
   - Convert bike trip coordinates to point geometries
   - Assign points to districts using spatial joins

2. **Mobility Indicators**
   - Trips started and ended per district 
   - Net trips 
   - Mobility per km² and per capita
   - Daily profiles of trip starts

3. **Building Indicators**
   - Number of buildings
   - Total buildings area
   - Building density per km²
   - Distribution of building types

4. **Visualization**
   - Bar charts of indicators
   - Daily mobility profiles
   - Building type distributions by district
   - An interactive Folium map combining choropleth layers and building data


---

## Discussion of Results

The analysis reveals clear differences between Ullern and Grünerløkka:

- Grünerløkka exhibits significantly higher bike-sharing activity, both in total, per km², and per capita.
- The daily usage profile in Grünerløkka shows consisten activity throughout the day, while Ullern displays more pronunced commuting patterns.
- Building density and building type distribution explain a substantial portion of the observed variation. 
- The interactive map illustrates that mobility patterns closely allign with land-use and urban structure. 

Overall, the results indicate a strong relationship between urban density, land-use mix, and mobility behavior.


---

## Data limitations and Reflections

- OpenStreetMap data is crowdsourced, and building type classifications may be incomplete or inaccurate. 
- The bike-sharing data covers only a single month and i therefore subject to seasonal effects. 
- Spatial joins may introduce errors when points lie close to district boundaries. 
- The selected indicators do not capture infrastructure quality or socioeconomic factors. 

Despite these limitations, the analysis reveals robust patterns consistent with expecter urban structure and mobility dynamics in Oslo. 


---

## Author 
Project submitted by:
Simen Roko Krogstie


---

## Academic Context

This project was completed as part of the course **GMGI221** at **NMBU** (autumn 2025).  
Final grades: Project — **B**, Course — **A**.

