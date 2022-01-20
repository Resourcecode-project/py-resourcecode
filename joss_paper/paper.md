---
title: 'RESOURCECODE: A Python package for statistical analysis of sea-state hindcast data'
tags:
  - Python
  - Oceanography
  - Statistics
  - Hindcast
  - Sea-state
authors:
  - name: Nicolas Raillard^[corresponding author] # note this makes a footnote saying 'co-first author'
    orcid: 0000-0003-3385-5104
    affiliation: 1
  - name: Christophe Maisondieu
    orcid: 0000-0001-9883-5257
    affiliation: 1
  - name: David Darbynian
    affiliation: 2
  - name: Gregory Payne
    orcid: 0000-0002-8527-8815
    affiliation: 3
  - name: Louis Papillon
    affiliation: 4
affiliations:
 - name: Ifremer, RDT, F-29280 Plouzané, France
   index: 1
 - name: EMEC, Orkney, UK
   index: 2
 - name: Ecole Centrale Nantes, Nantes, France
   index: 3
 - name: Innosea, Nantes, France
   index: 4
citation_author: N. Raillard et al.
date: 30 November 2021
year: 2021
bibliography: paper.bib
output: rticles::joss_article
csl: apa.csl
journal: JOSS
---



# Summary

The **ResourceCODE** Marine Data Toolbox is a python package to facilitate the access to recent hindcast database of sea-state [@Accensi_2021], along with a set of state-of-the-art methods for data analysis. This toolbox provides developers with a set of standard functions for resource assessment and operations planning. The advanced statistical modelling tools provided together with the embedded high resolution wave hindcast database allow the developers with a set of standard functions for resource assessment, extreme values modelling and operations planning. It is dedicated to users without the knowledge of manipulating numerous netCDF files or developing statistical analysis, but is also designed to fulfill expert met-ocean analysts needs. The advanced statistical modelling tools provided allow the developers of Offshore Renewable Energy (**ORE**) devices to conduct the necessary assessments to reduce uncertainty in expected environmental conditions, and de-risk investment in future technology design.

# Statement of Need

The **ResourceCODE** library allows to retrieve, analyse, and write data files containing time series data extracted from the companion hindcast database. This database consist in a high-resolution unstructured grid, spanning from the south of Spain to the Faroe Islands and from the western Irish continental shelf to the Baltic Sea, over more than 328 000 nodes. At each node, 39 parameters and frequency spectrum of waves are available with a hourly time-step. Directional spectrum are also available, on a coarser grid over the area covered. This data has been extensively validated against both in-situ and space born data. However, this database is very large (more than 50Tb) and can not easily be downloaded by the end users. **ResourceCODE** objective is twofold: preparing data harvesting from the database, which is often one of the most time-consuming steps, and providing the user with unified, state-of-the-art methods for analyzing the data extracted. The analysis tools encompass different aspect such as resource assessment, design of ORE devices and the planning of Operation and Maintenance (O&M) tasks.

For non-expert users of the **ResourceCODE** dataset:
- data access;
- easy to use standard methods;
- available through the web portal as `nbviwer` or `binder` links

For experts met-ocean analysts:
- access to recent analytics tools;
- reproducible and reference implementation

# Key Features of `resourcecode` python package

`resourcecode` provides a wrapper for easy fetching data of the **ResourceCODE** database, by calling the Cassandra API. The database itself represents more the 40Tb of data, preventing standard user to download it as a whole. Instead, this toolbox is intended to provide access to time series of sea-state parameters, as simply as the following code snippet:


```python
import resourcecode
client = resourcecode.Client()
data = client.get_dataframe_from_criteria(
    """
{
    "node": 134939,
    "parameter": ["hs","fp","dp","cge"]
}
"""
)
```

In the example above, we used `resourcecode` to fetch data from node *134939*, for the entire time period, and for some parameters: significant wave height $H_s$, peak  wave frequency $f_p$, Mean direction at peak frequency $D_p$ and Wave Energy Flux $CgE$. Under the hood, `resourcecode` will construct the proper Cassandra request and will process the data internally to output a **pandas** data frame  (@pandas2010) workable in-memory.   

- Data management:
  - Extraction of sea-state parameters from Cassandra web-service;
  - Accessing database configuration:
    - nodes location and spectral data availability;
    - coastlines, islands ans mesh triangles;
    - bathymetry and bottom roughness;
    - List of output variables;
  - Easy to use **pandas** data frame (filtering,aggregating,...);
  - Data conversion: 
    - Directional spectra $\to$ Frequency spectra $\to$ Sea-state parameters;
    - Zonal/Meridional components to Intensity/Direction.
- Statistical modelling:
  - Environmental conditions assessment;
  - Extreme values modelling;
  - 2D and 3D environmental contours (as in @Raillard_2019).
- Weather windows for O&M:
 - Model based (as in @Walker_2013);
 - Empirical estimates.
- Producible estimation:
 - Standard WEC included, extensible with user-provided characteristics;
 - PTO optimization (as in @Payne_2021).

# Companion web Portal

The toolbox is associated to a Web Portal^[https://resourcecode.ifremer.fr/] for exploring the data and accessing some simplified use-case, dynamically rendered and based on the possibilities offered by the toolbox.

For example, it allows the user to find a specific location on the map, on which both the output node and the 2D spectral locations are available. See the left plot of Figure \ref{fig:portal}. It is also possible from this map to find a point from given coordinates and to specify a time period for data subsetting. The location selected by the user along with the period specified can be directly refered in a url^[https://resourcecode.ifremer.fr/explore?pointId=119949&startDateTime=1998-02-01T14%3A00%3A00.000Z&endDateTime=1998-02-01T23%3A00%3A00.000Z]

Once a node is selected, the user is offered several tools for analyzing the data available at the selected location. This tools are developed on top of the python package and allows for several statistical characterization of the selected site: summary statistics; time series visualization; bivariate statistics; wind and wave rose.

\begin{figure}

{\centering \includegraphics[width=0.495\linewidth]{selection_map} \includegraphics[width=0.495\linewidth]{previews} 

}

\caption{Left: Map for location selection. Right: Available previews.}\label{fig:portal}
\end{figure}

# Conclusion

The `resourcecode` package is offering to the met-oceanic engineering community a tool to access seamlessly to a large an complex dataset that have proved to be a reference for coastal sea-states. Along with the dataset, the functionalities offered permits to foster the development of OREs. For a complete list of available features, the reader can access to the full package documentation at https://resourcecode.gitlab-pages.ifremer.fr/resourcecode/. 

# Acknowledgements

The **ResourceCODE** project has received support under the framework of the OCEANERA-NET COFUND project, with funding provided by national/ regional sources and co-funding by the European Union's Horizon 2020 research and innovation program.

# References

