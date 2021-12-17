---
title: 'RESOURCECODE: A Python package for statistical analysis of sea-state hindcast data'
tags:
  - Python
  - oceanography
  - statistics
  - hindcast
  - sea-state
authors:
  - name: Nicolas Raillard^[corresponding author] # note this makes a footnote saying 'co-first author'
    orcid: 0000-0003-3385-5104
    affiliation: 1
  - name: Christophe Maisondieu
    orcid: 0000-0001-9883-5257
    affiliation: 1
  - name: Mickael Accensi
    orcid: 0000-0003-1125-7568
    affiliation: 2
  - name: David Darbynian
    affiliation: 3
  - name: Gregory Payne
    orcid: 0000-0002-8527-8815
    affiliation: 4
  - name: Louis Papillon
    affiliation: 5
  - name: Simon Chabot
    affiliation: 6
affiliations:
 - name: IFREMER, LCSM, Plouzané, France
   index: 1
 - name: IFREMER, LOPS, Plouzané, France
   index: 2
 - name: EMEC, Orkney, UK
   index: 3
 - name: Ecole Centrale Nantes, Nantes, France
   index: 4
 - name: Innosea, Nantes, France
   index: 5
 - name: Logilab, Paris, France
   index: 6
citation_author: N. Raillard et al.
date: 30 November 2021
year: 2021
bibliography: paper.bib
output: rticles::joss_article
csl: apa.csl
journal: JOSS
---

# Summary

The **ResourceCODE** Marine Data Toolbox is a python package to facilitate the access to recent hindcast database of sea-state [@Accensi_2021], along with a set of state-of-the-art methods for data analysis. This toolbox provides developers with a set of standard functions for resource assessment and operations planning. The advanced statistical modelling tools provided together with the embedded high resolution wave hindcast database allow the developers with a set of standard functions for resource assessment, extreme values modelling and operations planning. It is dedicated to users without the knowledge of manipulating numerous netCDF files or developing statistical analysis, but is also designed to fulfil expert met-ocean analysts needs. The advanced statistical modelling tools provided allow the developers of Offshore Renewable Energy (**ORE**) devices to conduct the necessary assessments to reduce uncertainty in expected environmental conditions, and de-risk investment in future technology design.

# Statement of Need

The **ResourceCODE** library allows to retrieve, analyse, and write data files containing time series data extracted from the companion hindcast database. This database consist in a high-resolution unstructured grid, spanning from the south of Spain to
the Faroe Islands and from the western Irish continental shelf to the Baltic Sea, over more than 328 000 nodes. At each node, 39 parameters and frequency spectrum of waves are available with a hourly time-step. Directional spectrum are also available, on a coarser grid over the area covered. This data has been extensively validated against both in-situ and space born data. However, this database is very large (more than 50Tb) and can not easily be downloaded by the end users. **ResourceCODE** objective is twofold: preparing data harvesting from the database, which is often one of the most time-consuming steps, and providing the user with state-of-the-art methods for analysing the data extracted. The analysis tools encompass different aspect such as resource assessment, design of ORE devices and the planning of Operation and Maintenance (O&M) tasks.

For non-expert users of the Resourcecode dataset:
- data acess;
- esay to use standard methods;
- available thru the web portal as nbviwer of binder links

For experts met-ocean analysts:
- access to recent analytical tools;
- reproducible and reference implementation

# Key Features of **resourcecode**

- Data management:
  - Extraction from Cassandra web-service;
  - Accessing database configuration (nodes location, spectral data availability, coastlines...);
  - easy to use any **pandas** data frame (filtering,aggregating,...);
  - data manipulation: conversion 2D -> 1D -> Sea-state parameters.
- Statistical modelling:
  - Environmental conditions assessment;
  - Extreme values modelling;
  - 2D and 3D environmental contours (as in @Raillard_2019).
- Weather windows:
 - Model based (as in @Walker_2013);
 - Empirical estimated.
- Producible estimation:
 - Standard WEC or user-provider;
 - PTO optimization at each step (as in @Payne_2021)

# Acknowledgements

The ResourceCODE project has received support under the framework of the OCEANERA-NET COFUND project, with funding provided by national/ regional sources and co-funding by the European Union's Horizon 2020 research and innovation programme.

# References

