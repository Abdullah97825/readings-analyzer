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

def analyze_directions(df, has_concrete=False):
    """
    Find the best direction and compare with north for each row
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
    
    # Calculate means for each direction for each row
    for direction in directions + ['north-glass']:
        df[f'Mean_{direction}'] = df.apply(
            lambda row: calculate_direction_mean(row, direction, has_concrete), 
            axis=1
        )
    
    # Find best direction (excluding north)
    df['Best_Direction'] = df.apply(
        lambda row: min(
            [(direction, row[f'Mean_{direction}']) for direction in directions],
            key=lambda x: x[1]
        )[0],
        axis=1
    )
    
    # Get the mean value for the best direction
    df['Best_Direction_Mean'] = df.apply(
        lambda row: row[f'Mean_{row["Best_Direction"]}'],
        axis=1
    )
    
    # Compare with North
    df['Better_Than_North'] = df['Best_Direction_Mean'] < df[f'Mean_north-glass']
    
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
    
    # Save results
    output_path = f'output/{output_file}'
    results.to_csv(output_path, index=False)
    print(f"\nStatistics saved to {output_path}")
    print("\nResults summary:")
    print(results)

def analyze_directions_with_concrete(df):
    """
    Modified version of analyze_directions for concrete data
    """
    # Convert all temperature and humidity columns to numeric
    directions = ['south-glass', 'south-con', 'west', 'east']
    for direction in directions + ['north']:
        if direction == 'south-con':
            temp_col = 'T1ENVIRO[C]-south-con'
            humidity_col = 'HUMD1ENVIRO[%rH]-south-con'
        else:
            temp_col = f'Temperature[C]-{direction}-glass'
            humidity_col = f'Humidity[%rH]-{direction}-glass'
        df[temp_col] = pd.to_numeric(df[temp_col], errors='coerce')
        df[humidity_col] = pd.to_numeric(df[humidity_col], errors='coerce')
    
    # Calculate means
    for direction in directions + ['north']:
        if direction == 'south-con':
            df[f'Mean_{direction}'] = df.apply(
                lambda row: np.mean([
                    row['T1ENVIRO[C]-south-con'],
                    row['HUMD1ENVIRO[%rH]-south-con']
                ]),
                axis=1
            )
        else:
            df[f'Mean_{direction}'] = df.apply(
                lambda row: calculate_direction_mean(row, direction),
                axis=1
            )
    
    # Rest of the analysis remains similar
    df['Best_Direction'] = df.apply(
        lambda row: min(
            [(direction, row[f'Mean_{direction}']) for direction in directions],
            key=lambda x: x[1]
        )[0],
        axis=1
    )
    
    df['Best_Direction_Mean'] = df.apply(
        lambda row: row[f'Mean_{row["Best_Direction"]}'],
        axis=1
    )
    
    df['Better_Than_North'] = df['Best_Direction_Mean'] < df['Mean_north']
    
    return df

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
                row[f'{category}-temp'],
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

if __name__ == "__main__":
    main()
