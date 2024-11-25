# Glassbox and Direction Analyzer

This repository contains two scripts for analyzing glassbox and direction data.

The glassbox analyzer script analyzes the glassbox data to determine the best glass type for each row.
The direction analyzer script analyzes the direction data to determine the best direction for each row.

**This project and its results are part of a research project by Nada Saleh Ammoo.**
**Please refer to the research work associated with this project for more information on the methodology and the data.**

## Prerequisites to run the scripts

- Python 3.10 or higher [must be installed](https://www.python.org/downloads/)
- pandas library. [Install using Pip](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html#installing-from-pypi)
- NumPy library. [Install using Pip](https://numpy.org/install/)


## Best Direction Analyzer

The best direction analyzer script is located in the `best-direction-analyzer` directory.
The directory contains the following files:
- `analyzer.py`: The main script for analyzing the direction data.
- `ICONALLDATA-no-concrete.csv`: The data for the no-concrete scenario.
- `ICONALLDATA-with-concrete.csv`: The data for the with-concrete scenario.

To run the script, navigate to the `best-direction-analyzer` directory and run the following command:
```
python analyzer.py
```

The script will output the results to the `output` directory.
Two output files will be created:
- `statistics_no_concrete.csv`: The statistics for the no-concrete scenario.
- `statistics_with_concrete.csv`: The statistics for the with-concrete scenario.

All filenames, directories, and paths are hardcoded in the script.
If you want to change them, you will need to modify the script.

The paths are relative to the location of the script.
The input files should be in the `best-direction-analyzer` directory with the names `ICONALLDATA-no-concrete.csv` and `ICONALLDATA-with-concrete.csv`.


## Best Glass Structure Analyzer

The best glass structure analyzer script is located in the `best-glass-structure` directory.
The directory contains the following files:
- `analyzer.py`: The main script for analyzing the glass structure data.
- `GLASSBOX-T174H-north-winter.csv`: The data for the north winter scenario.
- `GLASSBOX-T174H-south-summer.csv`: The data for the south summer scenario.

To run the script, navigate to the `best-glass-structure` directory and run the following command:
```
python analyzer.py
```

The script will output the results to the `output` directory.
Two output files will be created:
- `glassbox_analysis_north_winter.csv`: The analysis for the north winter scenario.
- `glassbox_analysis_south_summer.csv`: The analysis for the south summer scenario. 

All filenames, directories, and paths are hardcoded in the script.
If you want to change them, you will need to modify the script.

The paths are relative to the location of the script.
The input files should be in the `best-glass-structure` directory with the names `GLASSBOX-T174H-north-winter.csv` and `GLASSBOX-T174H-south-summer.csv`.


