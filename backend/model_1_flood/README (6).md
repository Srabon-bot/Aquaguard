This repository contains the datasets for the paper titled "Multi-Satellite High-Frequency Monitoring of Water Levels, Discharge, and Floodplain Dynamics in the Brahmaputra River, Bangladesh" by Faruque Abdullah et al. submitted to MDPI Hydrology.

The main file in this repository (Data.zip) contains different output from the aforementioned paper within the following folders

1. WL
    1. WL-from-Altimetry_Bahadurabad_2008-2022.csv: Comma-separated spreadsheet containing the water level derived from different satellites at Bahadurabad station location. Unit meters, referenced to the mean sea level datum of water level at Bahadurabad.
    2. WL-from-S1_S2-Bahadurabad_2016-2022.csv: Comma-separated spreadsheet containing the water level derived from the inverse rating curve applied on the discharge computed from the river width from Sentinel-1 and Sentinel-2 images. Unit meters.
    3. COMBINED-WL-from-Altimetry_S1_S2-2008-2022_Bahadurabad.csv: Combined water level timeseries of 1 and 2. Unit meters.
2. Q 
    1. Own_Rated_Q_2008-2022_Bahadurabad.csv: Discharge computed using rating curve derived from in situ water level and discharge. Unit m3/sec.
    2. Q-from-Altimetry_2008-2022_Bahadurabad.csv: Discharge computed using rating curve derived from altimetry water level and rated discharge of 1. Unit m3/sec.
    3. Q-from-S1_S2_2016-2022_Bahadurabad.csv: Discharge computed using rating curve derived from river width and rated discharge of 1. Unit m3/sec.
    4. COMBINED_Q_from-Altimetry_S1_S2_2008-2022-Bahadurabad.csv: Combined discharge timeseries of 2 and 3. Unit m3/sec.
3. FPDEM
    1. 2016...2022.tif: Waterline derived DEM for each year from 2016 to 2022 regridded to 90m grid of FABDEM. Unit meters, upward positive, referenced to the mean sea level datum of Bangladesh
    2. FPDEM_16-22.tif: Waterline derived DEM for all the waterlines from 2016 to 2022 and regridded to 90m grid of FABDEM. Unit meters, upward positive, referenced to the mean sea level datum of Bangladesh.
4. Threshold
    1. S1-TH-timeseries.csv: Dynamic threshold derived for segmenting land and water from Sentinel-1 imagery using Otsu method. 
    2. Width-TH_timeseries_position01_2016-2022.csv: Width of the river derived at position 1 (see paper).



