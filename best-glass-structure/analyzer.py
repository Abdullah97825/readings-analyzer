# analyzer.py

# Please make sure to refer to the research work associated with this project for more information on the methodology and the data.

# This script analyzes the glassbox data to determine the best glass type for each row.

# Please note that this script is designed to work with the specific format of the glassbox data.
# If your data format is different, you may need to modify the script accordingly.

# The script assumes that the data is stored in CSV files with specific names, and that the columns are named according to the expected format.
# For data preprocessing, the script will check for null values and print the number of null values per column. Other preprocessing steps are not implemented.


# For glassbox data analysis, the script will calculate the heat index for each category and determine the best category for each row.
# The results will be saved to a CSV file in the output directory.

# The heat index calculation is based on a specific formula, which is hardcoded in the script.

# The coefficients for the heat index calculation are hardcoded in the script.
# The coefficients are:
# c_1 = -42.379
# c_2 = 2.04901523
# c_3 = 10.14333127
# c_4 = -0.22475541
# c_5 = -0.0068783
# c_6 = -0.05481717
# c_7 = 0.00122874
# c_8 = 0.00085282
# c_9 = -0.00000199


import pandas as pd
import numpy as np
import os

def load_csv(file_path):
    """
    Load CSV file into a pandas DataFrame
    """
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while loading the file: {str(e)}")
        return None

def analyze_null_counts(df):
    """
    Analyze and print null value counts and percentages
    """
    # Get null counts per column
    null_check = df.isnull().sum()
    total_nulls = df.isnull().sum().sum()
    
    print("\n=== Null Values Analysis ===")
    print("\nNull values count per column:")
    print(null_check)
    print(f"\nTotal number of null values: {total_nulls}")
    
    # Calculate and print null percentages
    null_percentage = (df.isnull().sum() / len(df)) * 100
    print("\nPercentage of null values per column:")
    print(null_percentage.round(2))

def find_null_rows(df):
    """
    Find and print rows containing null values
    """
    rows_with_nulls = df[df.isnull().any(axis=1)]
    
    print("\n=== Rows Containing Null Values ===")
    print(f"Total rows with null values: {len(rows_with_nulls)}")
    
    if len(rows_with_nulls) > 0:
        print("\nHere are the rows containing null values:")
        print(rows_with_nulls)
        
        print("\n=== Detailed Null Analysis ===")
        for index, row in rows_with_nulls.iterrows():
            null_columns = row[row.isnull()].index.tolist()
            print(f"\nRow {index} has null values in these columns: {null_columns}")
    else:
        print("\nNo null values found in the dataset!")
    
    return rows_with_nulls

def calculate_heat_index(temp, humidity):
    """
    Calculate heat index using the provided coefficients and formula
    """
    c_1 = -42.379
    c_2 = 2.04901523
    c_3 = 10.14333127
    c_4 = -0.22475541
    c_5 = -0.0068783
    c_6 = -0.05481717
    c_7 = 0.00122874
    c_8 = 0.00085282
    c_9 = -0.00000199
    
    return (c_1 + (c_2 * temp) + (c_3 * humidity) + 
            (c_4 * temp * humidity) + (c_5 * (temp ** 2)) + 
            (c_6 * (humidity ** 2)) + (c_7 * (temp ** 2) * humidity) + 
            (c_8 * temp * (humidity ** 2)) + 
            (c_9 * (temp ** 2) * (humidity ** 2)))

def celsius_to_fahrenheit(celsius):
    """Convert Celsius temperature to Fahrenheit"""
    return (celsius * 9/5) + 32

def analyze_glassbox_data(df):
    """
    Analyze glassbox data and determine the best glass type for each row
    """
    # Convert all columns to numeric
    for col in df.columns:
        if col != 'DATA-ALL':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calculate heat indices for each category
    categories = ['environment', 'double-glass', 'triple-glass', 'quad-glass']
    
    for category in categories:
        df[f'{category}_heat_index'] = df.apply(
            lambda row: calculate_heat_index(
                celsius_to_fahrenheit(row[f'{category}-temp']),  # Convert Celsius to Fahrenheit
                row[f'{category}-humidity']
            ),
            axis=1
        )
    
    # Find best category for each row
    def find_best_category(row):
        env_hi = row['environment_heat_index']
        differences = {
            cat: abs(row[f'{cat}_heat_index'] - env_hi)
            for cat in ['double-glass', 'triple-glass', 'quad-glass']
        }
        return min(differences.items(), key=lambda x: x[1])[0]
    
    df['best_category'] = df.apply(find_best_category, axis=1)
    
    # Count occurrences of best categories
    counts = df['best_category'].value_counts()
    
    # Create DataFrame with fixed order of categories
    ordered_categories = ['double-glass', 'triple-glass', 'quad-glass']
    category_counts = pd.DataFrame({
        'category': ordered_categories,
        'times_best': [counts.get(cat, 0) for cat in ordered_categories]
    })
    
    return category_counts

#This function is used to print the heat indices for the first 30 rows of the dataframe for debugging purposes
def print_first_30_heat_indices(df):
    """
    Print heat indices for the first 30 rows of the dataframe
    """
    categories = ['environment', 'double-glass', 'triple-glass', 'quad-glass']
    
    print("\n=== Heat Indices for First 30 Rows ===")
    print("\nRow | Category | Temperature (C) | Temperature (F) | Humidity | Heat Index")
    print("-" * 75)
    
    for idx in range(min(30, len(df))):
        for category in categories:
            temp_c = df.iloc[idx][f'{category}-temp']
            temp_f = celsius_to_fahrenheit(temp_c)
            humidity = df.iloc[idx][f'{category}-humidity']
            heat_index = calculate_heat_index(temp_f, humidity)
            
            print(f"{idx:3d} | {category:10s} | {temp_c:13.2f} | {temp_f:13.2f} | {humidity:7.2f} | {heat_index:.2f}")
        print("-" * 75)

def main():
    """
    Main function to process both north winter and south summer files
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create output directory relative to script location
    output_dir = os.path.join(script_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Process north winter file
    print("\n=== Starting analysis of North Winter data ===")
    north_file = os.path.join(script_dir, 'GLASSBOX-T174H-north-winter.csv')
    df_north = load_csv(north_file)
    if df_north is not None:
        # Check for null values
        analyze_null_counts(df_north)
        find_null_rows(df_north)
        
        # Analyze data
        results_north = analyze_glassbox_data(df_north)
        output_path = os.path.join(output_dir, 'glassbox_analysis_north_winter.csv')
        results_north.to_csv(output_path, index=False)
        print("=== North Winter data analysis completed ===\n")
    
    # Process south summer file
    print("=== Starting analysis of South Summer data ===")
    south_file = os.path.join(script_dir, 'GLASSBOX-T174H-south-summer.csv')
    df_south = load_csv(south_file)
    if df_south is not None:
        # Check for null values
        analyze_null_counts(df_south)
        find_null_rows(df_south)
        
        # Analyze data
        results_south = analyze_glassbox_data(df_south)
        output_path = os.path.join(output_dir, 'glassbox_analysis_south_summer.csv')
        results_south.to_csv(output_path, index=False)
        print("=== South Summer data analysis completed ===\n")
        
        # Print first 30 heat indices for south summer data
        # print_first_30_heat_indices(df_south)

if __name__ == "__main__":
    main()
