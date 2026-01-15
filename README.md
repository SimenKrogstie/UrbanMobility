
# Urbane mobilitets- og bygningsindikatorer: En analyse av bysykkelbruk og arealstruktur i Ullern og Grünerløkka.

Formålet med denne oppgaven er å undersøke hvordan mobilitetsmønstre fra bysykkel 
henger sammen med arealstruktur og bygningstyper i ulike bydeler i Oslo. 
Ved hjelp av romlige analyser, mobilitetsindikatorer og bygningstyper fra 
OpenStreetMap undersøker jeg hvordan ulik byform påvirker bruk av bysykler.

Analysen prøver å besvare:

1. Hvordan varierer mobilitetsnivået mellom Ullern og Grünerløkka, og hvilke 
   indikatorer viser tydeligst forskjell?
2. Kan variasjoner i mobilitet forklares gjennom forskjeller i befolkningstetthet, 
   bygningsstruktur eller funksjonsblanding?
3. Hvordan ser døgnprofilen for sykkelbruk ut i de to bydelene, og hvilke 
   pendlermønstre kan identifiseres?
4. Hvordan reflekteres disse sammenhengene i et interaktivt kart som kombinerer 
   mobilitetsindikatorer og bygningstyper?

En komplett Jupyter Notebook (`analyse.ipynb`) viser bruken av funksjonene og 
inneholder all analyse, figurer og tolkning av resultatene. Se også diskusjon av
resultater lenger ned i README.


---

##  Prosjektstruktur
Prosjektmappen består av følgende filer.
```text
Project/
├── data/
│   ├── oslo_bydeler_befolkning_2024.geojson   # Befolknings- og bydelsdata
│   └── sykkel_oktober_2025.csv                # Sykkelturdata
│
├── analyse.ipynb                              # Hovedrapport med analyser og visualiseringer
│
├── data_prosessering.py                       # Spatial join, punktkonvertering, OSM-bygg
├── helpers.py                                 # CRS-hjelpefunksjon
├── indikatorer.py                             # Mobilitets- og bygningsindikatorer
├── lese_data.py                               # Funksjoner for innlasting av data
├── map.py                                     # Interaktivt Folium-kart
├── visualisering.py                           # Plotfunksjoner for indikatorer, bygg, tidsprofiler
│
└── README.md                                  # Dokumentasjon av prosjektet
```

---


## Installasjon

Prosjektet bruker kun pakker som inngår i conda-miljøet **gmgi221**.
Alle nødvendige avhengigheter er definert i `gmgi221.yml`.

#### Opprett og aktiver conda-miljøet

```bash
conda env create -f gmgi221.yml
conda activate gmgi221
```

---

## Hvordan kjøre prosjektet

1. Åpne en terminal og naviger til prosjektmappen.
2. Start JupyterLab.
3. Åpne og kjør notebooken `analyse.ipynb`.

### Notebookens funksjonalitet

Notebooken utfører følgende operasjoner:

- laster inn og klargjør datasett
- beregner mobilitets- og bygningsrelaterte indikatorer
- analyserer tidsprofiler
- visualiserer indikatorer ved hjelp av stolpediagrammer
- genererer et interaktivt kart ved bruk av Folium
- sammenligner resultater for Ullern og Grünerløkka


---

## Funksjonene
### lese_data.py
- csv_til_df() – Leser sykkelturdata og håndterer datatyper
- data_til_gdf() – Leser GeoData (ShapeFile, GeoJSON, etc.)

### data_prosessering.py
- punkter_gdf() – Konverterer lat/lon til punktgeometri
- legg_til_bydeler() – Romlig join mellom punkt og bydelsgeometri
- hent_bygninger() – Henter bygninger fra OSM og klipper dem til bydelene

### indikatorer.py
- mobilitetsindikatorer() – Beregner turer inn/ut, per km², per innbygger
- bygningsindikatorer() – Beregner antall bygninger, bygningsareal, tetthet

### visualisering.py
- plot_mobilitetsindikatorer() – Barplot av mobilitetsindikatorer
- plot_tidsprofil() – Døgnprofil for startede turer
- plot_tidsprofil_retniger() – Turer mellom to bydeler over døgnet
- plot_bygningsindikatorer() – Sammenligning av bygningsindikatorer
- plot_bygningstyper() – Prosentvis fordeling av bygningstyper

### map.py
- interaktivt_kart() - Choropleth + bygningstyper i Folium


---

## Datasett
Jeg har brukt følgende datasett i analysen:
- **Bysykkelturer (Oslo Bysykkel / UIP)**  
  Turdata fra oktober 2025 som inneholder start- og sluttposisjon (koordinater), tidsstempel 
  og stasjonsinformasjon. Brukes til å beregne mobilitetsindikatorer.
  link: https://oslobysykkel.no/apne-data/historisk

- **Bygninger (OpenStreetMap via OSMnx)**  
  Bygninger innenfor de to utvalgte bydelene hentet fra OSM. Inneholder bygningstyper
  og footprint-geometri, og brukes til bygningsindikatorer og kartlag.

- **Befolkningstall/bydeler (SSB / Oslo kommune)**  
  Befolkningstall per bydel fra 2024, brukt til indikatorer per innbygger, kart, og for å knytte 
  start- og sluttpunkt for sykkelturer og bygninger til bydeler. 
  link: https://kart.ssb.no/wayfinder/default?x=23.514300&y=67.351581&z=3.6

Alle datasett reprojiseres til **EPSG:25833 (UTM 33N)** for korrekte arealberegninger.


---

## Metode
Analysen bygger på en kombinasjon av dataprosessering, indikatorberegning og visualisering, 
og består av følgende steg:

1. **Dataprosessering**  
   - Lese inn CSV og GeoJSON/GPKG-data  
   - Reprojisere til felles koordinatsystem  
   - Konvertere sykkelturpunkter til geometri  
   - Knytte punktdata til bydeler via spatial join

2. **Mobilitetsindikatorer**  
   - Turer startet og sluttet per bydel  
   - Netto turer (inn – ut)  
   - Mobilitet per km^2 og per innbygger  
   - Døgnprofil for startede turer  

3. **Bygningsindikatorer**  
   - Antall bygninger  
   - Bygningsareal   
   - Bygningstetthet per km²  
   - Fordeling av bygningstyper

4. **Visualiseringer**  
   - Barplot av indikatorer  
   - Døgnprofil for mobilitet  
   - Bygningstyper per bydel
   - Et interaktivt Folium-kart som kombinerer choropleth + bygningstyper


---

## Diskusjon av resultater

Analysen viser tydelige forskjeller mellom Ullern og Grünerløkka:

- Grünerløkka har betydelig høyere sykkelaktivitet, både totalt, per km² og per innbygger.  
- Døgnprofilen viser jevn aktivitet hele dagen i Grünerløkka, mens 
  Ullern har et tydligere pendlerpreg.
- Bygningstetthet og typefordeling forklarer mye av variasjonen.
- Kartet viser at mobilitet og arealbruk følger samme geografiske mønstre.

Samlet viser resultatene en sammenheng mellom urban tetthet, funksjonsblanding og mobilitet.


---

## Refleksjoner rundt dataene
- OpenStreetMap-data er crowdsourcet og bygningstyper kan være mangelfulle 
  eller ufullstendige.
- Sykkelturene dekker kun én måned, og er derfor sesongpreget.
- Spatial join kan gi feil hvis pukter ligger nær bydelsgrenser.
- Indikatorer sier ikke alt om infrastruktur, sosial eller økonomisk
  påvirkning.

Til tross for disse begrensningene viser analysen robuste mønstre som samsvarer 
med forventet bystruktur og mobilitetsmønstre i Oslo.

---

## Forfatter
Prosjektet er levert av:
Simen Roko Krogstie
