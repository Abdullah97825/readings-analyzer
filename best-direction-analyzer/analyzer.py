# analyzer.py

# Please make sure to refer to the research work associated with this project for more information on the methodology and the data.

# This script analyzes the glassbox data to determine the best direction for each row.

# Please note that this script is designed to work with the specific format of the glassbox data.
# If your data format is different, you may need to modify the script accordingly.

# The script assumes that the data is stored in CSV files with specific names, and that the columns are named according to the expected format.
# For data preprocessing, the script will check for null values and print the number of null values per column. Other preprocessing steps are not implemented.

# For direction analysis, the script will calculate the mean temperature and humidity for each direction and determine the best direction for each row.
# The best direction is the direction with the lowest mean temperature and humidity.

# The results will be saved to a CSV file in the output directory.

# The script also includes a modified version of the analyze_directions function for concrete data.


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

def calculate_direction_mean(row, direction, has_concrete=False):
    """
    Calculate mean of temperature and humidity for a given direction
    """
    if direction == 'south-con':
        temp_col = 'T1ENVIRO[C]-south-con'
        humidity_col = 'HUMD1ENVIRO[%rH]-south-con'
    else:
        temp_col = f'Temperature[C]-{direction}'
        humidity_col = f'Humidity[%rH]-{direction}'
    
    # Convert to numeric values
    temp_value = pd.to_numeric(row[temp_col], errors='coerce')
    humidity_value = pd.to_numeric(row[humidity_col], errors='coerce')
    
    return np.mean([temp_value, humidity_value])

def calculate_heat_index_1(temp, humidity):
    """
    Calculate heat index using equation 1: HI = Temp + (0.33 * humidity) - 0.7
    Temperature should be in Celsius
    """
    return temp + (0.33 * humidity) - 0.7

def calculate_heat_index_2(temp, humidity):
    """
    Calculate heat index using equation 2 (from glass structure analyzer)
    Temperature must be converted to Fahrenheit first
    """
    # Convert Celsius to Fahrenheit
    temp_f = (temp * 9/5) + 32
    
    c_1 = -42.379
    c_2 = 2.04901523
    c_3 = 10.14333127
    c_4 = -0.22475541
    c_5 = -0.0068783
    c_6 = -0.05481717
    c_7 = 0.00122874
    c_8 = 0.00085282
    c_9 = -0.00000199
    
    return (c_1 + (c_2 * temp_f) + (c_3 * humidity) + 
            (c_4 * temp_f * humidity) + (c_5 * (temp_f ** 2)) + 
            (c_6 * (humidity ** 2)) + (c_7 * (temp_f ** 2) * humidity) + 
            (c_8 * temp_f * (humidity ** 2)) + 
            (c_9 * (temp_f ** 2) * (humidity ** 2)))

def analyze_directions(df, method='mean', has_concrete=False):
    """
    Find the best direction and compare with north for each row
    method can be 'mean', 'heat_index_1', or 'heat_index_2'
    """
    # Define directions based on file type
    if has_concrete:
        directions = ['south-glass', 'south-con', 'west-glass', 'east-glass']
    else:
        directions = ['south-glass', 'west-glass', 'east-glass']
    
    # Convert temperature and humidity columns to numeric
    for direction in directions + ['north-glass']:
        if direction == 'south-con':
            temp_col = 'T1ENVIRO[C]-south-con'
            humidity_col = 'HUMD1ENVIRO[%rH]-south-con'
        else:
            temp_col = f'Temperature[C]-{direction}'
            humidity_col = f'Humidity[%rH]-{direction}'
        df[temp_col] = pd.to_numeric(df[temp_col], errors='coerce')
        df[humidity_col] = pd.to_numeric(df[humidity_col], errors='coerce')
    
    # Calculate values for each direction based on method
    for direction in directions + ['north-glass']:
        if direction == 'south-con':
            temp_col = 'T1ENVIRO[C]-south-con'
            humidity_col = 'HUMD1ENVIRO[%rH]-south-con'
        else:
            temp_col = f'Temperature[C]-{direction}'
            humidity_col = f'Humidity[%rH]-{direction}'
        
        if method == 'mean':
            df[f'Value_{direction}'] = df.apply(
                lambda row: calculate_direction_mean(row, direction, has_concrete),
                axis=1
            )
        elif method == 'heat_index_1':
            df[f'Value_{direction}'] = df.apply(
                lambda row: calculate_heat_index_1(
                    row[temp_col],
                    row[humidity_col]
                ),
                axis=1
            )
        elif method == 'heat_index_2':
            df[f'Value_{direction}'] = df.apply(
                lambda row: calculate_heat_index_2(
                    row[temp_col],
                    row[humidity_col]
                ),
                axis=1
            )
    
    # Find best direction (excluding north)
    df['Best_Direction'] = df.apply(
        lambda row: min(
            [(direction, row[f'Value_{direction}']) for direction in directions],
            key=lambda x: x[1]
        )[0],
        axis=1
    )
    
    # Get the value for the best direction
    df['Best_Direction_Value'] = df.apply(
        lambda row: row[f'Value_{row["Best_Direction"]}'],
        axis=1
    )
    
    # Compare with North
    df['Better_Than_North'] = df['Best_Direction_Value'] < df[f'Value_north-glass']
    
    return df

def print_direction_analysis(df):
    """
    Print detailed analysis of directions
    """
    print("\n=== Direction Analysis Results ===")
    for index, row in df.iterrows():
        print(f"\nRow {index + 1} (ID: {row['id']}):")
        print(f"Best Direction: {row['Best_Direction']}")
        print(f"Better than North: {row['Better_Than_North']}")
        print(f"Best Direction Mean: {row['Best_Direction_Mean']:.2f}")
        print(f"North Mean: {row['Mean_north']:.2f}")
        
        # Show the actual temperature and humidity values
        direction = row['Best_Direction']
        print(f"\nBest Direction ({direction}) values:")
        print(f"Temperature: {row[f'Temperature[C]-{direction}-glass']:.2f}°C")
        print(f"Humidity: {row[f'Humidity[%rH]-{direction}-glass']:.2f}%")
        print(f"\nNorth values:")
        print(f"Temperature: {row['Temperature[C]-north-glass']:.2f}°C")
        print(f"Humidity: {row['Humidity[%rH]-north-glass']:.2f}%")
        print("-" * 50)

def analyze_file_statistics(df, directions, output_file, has_concrete=False):
    """
    Analyze and save statistics for each file
    """
    # Initialize counters
    best_direction_counts = {direction: 0 for direction in directions}
    better_than_north_counts = {direction: 0 for direction in directions}
    
    # Count occurrences
    for _, row in df.iterrows():
        best_dir = row['Best_Direction']
        best_direction_counts[best_dir] += 1
        
        if row['Better_Than_North']:
            better_than_north_counts[best_dir] += 1
    
    # Create results DataFrame
    results = pd.DataFrame({
        'Direction': list(directions),
        'Times_Best': [best_direction_counts[d] for d in directions],
        'Times_Better_Than_North': [better_than_north_counts[d] for d in directions]
    })
    
    # Save results using relative path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_file)
    
    # Create all necessary directories in the path
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    results.to_csv(output_path, index=False)
    print(f"\nStatistics saved to {output_path}")
    print("\nResults summary:")
    print(results)

def main():
    """
    Main function to handle both files with three different methods
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define methods and their output directories
    methods = {
        'mean': 'mean_eqn_output',
        'heat_index_1': 'heat_index_eqn1_output',
        'heat_index_2': 'heat_index_eqn2_output'
    }
    
    # Process each method
    for method, output_dir_name in methods.items():
        # Create output directory
        output_dir = os.path.join(script_dir, output_dir_name)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nProcessing using {method} method...")
        
        # Process no-concrete file
        no_concrete_file = os.path.join(script_dir, 'ICONALLDATA-no-concrete.csv')
        df_no_concrete = load_csv(no_concrete_file)
        if df_no_concrete is not None:
            df_no_concrete = analyze_directions(df_no_concrete, method=method, has_concrete=False)
            analyze_file_statistics(
                df_no_concrete,
                ['south-glass', 'west-glass', 'east-glass'],
                os.path.join(output_dir_name, 'statistics_no_concrete.csv')
            )
        
        # Process with-concrete file
        with_concrete_file = os.path.join(script_dir, 'ICONALLDATA-with-concrete.csv')
        df_with_concrete = load_csv(with_concrete_file)
        if df_with_concrete is not None:
            df_with_concrete = analyze_directions(df_with_concrete, method=method, has_concrete=True)
            analyze_file_statistics(
                df_with_concrete,
                ['south-glass', 'south-con', 'west-glass', 'east-glass'],
                os.path.join(output_dir_name, 'statistics_with_concrete.csv'),
                has_concrete=True
            )

if __name__ == "__main__":
    main()
