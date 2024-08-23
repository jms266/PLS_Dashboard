# Importing the required libraries

import pandas as pd
import streamlit as st
# import os
from fuzzywuzzy import process, fuzz

# Loading the PLS and Error Code datasets from specific paths
# Need to upload them on github and change the path accordingly during deployment

#PLS_df = pd.read_excel("c:/Users/320258268/OneDrive - Philips/Desktop/output.xlsx")
PLS_df = pd.read_excel("https://github.com/jms266/PLS_Dashboard/blob/main/output.xlsx")
#Error_df = pd.read_excel("c:/Users/320258268/OneDrive - Philips/Desktop/ErrorCodes.xlsx")
Error_df = pd.read_excel("https://github.com/jms266/PLS_Dashboard/blob/main/ErrorCodes.xlsx")
#catheterdesc_df = pd.read_excel("c:/Users/320258268/OneDrive - Philips/Desktop/CathPinCodes.xlsx")
catheterdesc_df = pd.read_excel("https://github.com/jms266/PLS_Dashboard/blob/main/CathPinCodes.xlsx")
catheterdesc_df['Pin Code'] = catheterdesc_df['Pin Code'].astype(str)


def load_data(data_file):

    """
    Loading a single CSV file into a DataFrame with appropriate column names and handling for errors.
    
    Args:
        data_file (file-like object): The file to be loaded.
    
    Returns:
        DataFrame: The loaded DataFrame.
    """

    try:
        data = pd.read_csv(data_file, header=None, quotechar='"', sep=r',(?![^\[]*\])', engine='python')

       
        num_cols = len(data.columns)
        if num_cols == 6:
            column_names = ["ID", "SysTime", "Codes", "MessageID", "AddInfo", "N"]
        elif num_cols == 5:
            column_names = ["ID", "SysTime", "Codes", "MessageID", "AddInfo"]
        else:
            st.warning(f"Unexpected number of columns ({num_cols}) in file {data_file.name}. Please rectify and reupload!")
            st.stop()  

        data.columns = column_names

        num_cols = len(data.columns)
        if num_cols == 6:
            data.drop(columns=['N'], inplace=True)
        
        return data

    except pd.errors.ParserError as e:
        st.warning(f"Error parsing the file: {e}. Please check the file format and reupload.")
        st.stop()  

    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        st.stop()

def get_unique_catheters_from_dataset(dataset):

    """
    Extracting unique catheter IDs from the dataset.

    Returns a list of unique catheter IDs.

    """

    # uci = dataset[dataset['MessageID'] == 'CATHETER_ID']['AddInfo'].str.strip('[]').unique().tolist()

    uci = dataset[dataset['MessageID'] == 'CATHETER_ID']['AddInfo'].str.strip('[]').unique().tolist()
    
    # Removing 'Not Inserted' from the list if it exists
    uci = [catheter_id for catheter_id in uci if catheter_id != 'Not Inserted']
    
    return uci

def get_catheter_info(dff, catheter_id):

    """
    Retrieves and displays information about a specific catheter ID.
    
    Args:
        dff (DataFrame): The input dataset.
        catheter_id (str): The catheter ID to retrieve information for.

    """

    #  Handling invalid datetimes if present  

    dff['SysTime'] = dff['SysTime'].apply(lambda x: x if pd.to_datetime(x, errors='coerce') is not pd.NaT else '9999-01-01')  
    filtered_data = dff[dff['MessageID'].isin(['CATHETER_ID', 'VES_EXPECTED_ENERGY'])]
 
    catheter_shots = {}
    catheter_sessions = {}
    current_catheter_id = None
    laser_shots = 0
    
    for index, row in filtered_data.iterrows():
        # st.write('Checking in the loop')  # Debug Statement
        if row['MessageID'] == 'CATHETER_ID':
            current_catheter_id = row['AddInfo']
            laser_shots = 0
            catheter_sessions[current_catheter_id] = catheter_sessions.get(current_catheter_id, 0) + 1
        elif row['MessageID'] == 'VES_EXPECTED_ENERGY':
            laser_shots += 1
            catheter_shots[current_catheter_id] = catheter_shots.get(current_catheter_id, 0) + 1

    catheter_time = {}

    current_catheter_id = None
    start_time = None

    for index, row in filtered_data.iterrows():
        if row['MessageID'] == 'CATHETER_ID':
            current_catheter_id = row['AddInfo']
            start_time = pd.to_datetime(row['SysTime'])
        elif row['MessageID'] == 'VES_EXPECTED_ENERGY' and start_time is not None:
            end_time = pd.to_datetime(row['SysTime'])
            duration_minutes = (end_time - start_time).total_seconds() / 60
            catheter_time[current_catheter_id] = catheter_time.get(current_catheter_id, 0) + duration_minutes
            start_time = None

    if '['+catheter_id+']' not in catheter_shots:
        st.write("No laser shots fired for this Catheter ID. Please try again!")
        st.write(f"Catheter ID '{catheter_id}' not found. Please try again!")
        return

    # Retrieve the catheter description from the catheterdesc_df
    catheter_description = catheterdesc_df.loc[catheterdesc_df['Pin Code'] == catheter_id, 'Description'].values
    catheter_description = catheter_description[0] if len(catheter_description) > 0 else "Unknown Catheter"

    # Displaying the catheter information
    st.markdown(f"""
        <div style="padding: 10px; border-radius: 10px; background-color: #f9f9f9; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #4CAF50;">Catheter ID: {catheter_description} - {'['+catheter_id+']'}</h2>
            <p><strong>Laser Shots:</strong> {catheter_shots['['+catheter_id+']']}</p>
            <p><strong>Total Time (minutes):</strong> {catheter_time['['+catheter_id+']']}</p>
            <p><strong>Number of Sessions:</strong> {catheter_sessions['['+catheter_id+']']}</p>
        </div>
    """, unsafe_allow_html=True)

def analyze_lasing_trains(dff, catheter_id):

    """
    This function analyzes lasing trains to detect exceptions based on catheter ID.
    
    Parameters:
    dff (pd.DataFrame): DataFrame containing the data to be analyzed.
    catheter_id (str): The catheter ID to filter the data.

    """

    dff['SysTime'] = dff['SysTime'].apply(lambda x: x if pd.to_datetime(x, errors='coerce') is not pd.NaT else '9999-01-01')

    # Filtering for relevant columns
    filtered_data = dff[dff['MessageID'].isin(['CATHETER_ID', 'VES_EXPECTED_ENERGY', 'EXCEPTION'])]


    lasing_trains = []
    current_catheter_id = None
    laser_shots = 0
    current_train = []
    
    for index, row in filtered_data.iterrows():
        if row['MessageID'] == 'CATHETER_ID':
            if current_catheter_id is not None and current_train:
                lasing_trains.append((current_catheter_id, len(current_train), 'No Exception', None))
            current_catheter_id = row['AddInfo']
            laser_shots = 0
            current_train = []
        elif row['MessageID'] == 'VES_EXPECTED_ENERGY':
            if current_catheter_id is not None:
                laser_shots += 1
                current_train.append(row['SysTime'])
        elif 'EXCEPTION' in row['MessageID']:
            if current_catheter_id is not None:
                lasing_trains.append((current_catheter_id, len(current_train), row['MessageID'], row['AddInfo']))
                current_train = []
    
    # Adding the last train if exists
    if current_catheter_id is not None and current_train:
        lasing_trains.append((current_catheter_id, len(current_train), 'No Exception', None))


    # st.write("Lasing trains:") # Debug statement
    # st.write(lasing_trains)

    st.write("Lasing Trains Analysis For Exceptions:")
    exceptions_found = False
    for train in lasing_trains:
        if train[0] == '['+catheter_id+']' and train[2] != 'No Exception':
            st.write(f"Catheter: {train[0]}")
            st.write(f"Number of laser shots: {train[1]}")
            # st.write(f"{train[2]}") # Debug statement
            if train[3] is not None:
                st.write(f"Exception ID: {train[3]}")
            exceptions_found = True

    if not exceptions_found:
        st.write("No exceptions found for the given catheter ID.")

unique_fault_codes = PLS_df['Fault Code'].unique()

def calculate_top_fixes(PLS_df):

    """
    This function calculates the top fixes for each fault code based on field service summary.
    
    Parameters:
    PLS_df (pd.DataFrame): DataFrame containing the data with 'Fault Code' and 'Field Service Summary' columns.

    Returns:
    pd.DataFrame: DataFrame containing the top fixes for each fault code with their counts and percentages.
    """

    data_subset = PLS_df[['Fault Code', 'Field Service Summary']]
    fix_counts = data_subset.groupby(['Fault Code', 'Field Service Summary']).size().reset_index(name='Count')
    total_counts = fix_counts.groupby('Fault Code')['Count'].sum().reset_index(name='Total Count')
    fix_counts = pd.merge(fix_counts, total_counts, on='Fault Code')
    fix_counts['Percentage'] = (fix_counts['Count'] / fix_counts['Total Count']) * 100
    fix_counts = fix_counts.sort_values(by=['Fault Code', 'Count'], ascending=[True, False])
    
    def get_top_fix(fix, existing_fixes, threshold=80):
        match = process.extractOne(fix, existing_fixes, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= threshold:
            return match[0]
        return fix
    data_subset['Field Service Summary'] = data_subset['Field Service Summary'].astype(str).fillna('')
    grouped = data_subset.groupby('Fault Code')

    results = []

    for fault_code, group in grouped:
        fixes = group['Field Service Summary'].tolist()
        unique_fixes = []
        fix_counts = {}
    
        for fix in fixes:
            top_fix = get_top_fix(fix, unique_fixes)
            if top_fix not in unique_fixes:
                unique_fixes.append(top_fix)
                fix_counts[top_fix] = 0
            fix_counts[top_fix] += 1
    
        total_count = sum(fix_counts.values())
        for fix, count in fix_counts.items():
            results.append({
                'Fault Code': fault_code,
                'Fix': fix,
                'Count': count,
                'Percentage': (count / total_count) * 100
            })
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by=['Fault Code', 'Count'], ascending=[True, False])
    return results_df


def display_top_fixes_for_fault_code(fault_code, results_df):

    """
    This function displays the top 3 fixes for a given fault code.
    
    results_df (pd.DataFrame): DataFrame containing the top fixes for each fault code.

    """

    fault_code_data = results_df[results_df['Fault Code'] == fault_code]
    if fault_code_data.empty:
        st.write(f"No fixes found for Fault Code: {fault_code}")
        return
    
    st.write(f"Fault Code: {fault_code}")
    top_3_fixes = fault_code_data.head(3)
    for _, row in top_3_fixes.iterrows():
        # st.write(row)
        if pd.isna(row['Fix']) or row['Fix'] == 'nan' or row['Fix'] == '':
            continue
        # st.write(f"  Fix: {row['Fix']}, Count: {row['Count']}, Percentage: {row['Percentage']:.2f}%")
        st.write(f"{row['Percentage']:.2f}% of the times, this fix worked in the field - {row['Fix']}")
    st.write()

def display_all_fixes_for_fault_code(fault_code, results_df):
    
    # This function displays all fixes for a given fault code.

    fault_code_data = results_df[results_df['Fault Code'] == fault_code]
    if fault_code_data.empty:
        st.write(f"No fixes found for Fault Code: {fault_code}")
        return
    
    st.write(f"Fault Code: {fault_code}")
    for _, row in fault_code_data.iterrows():
        # st.write(f"  Fix: {row['Fix']}, Count: {row['Count']}, Percentage: {row['Percentage']:.2f}%") # Debug Statement
        if pd.isna(row['Fix']) or row['Fix'] == 'nan' or row['Fix'] == '':
            continue
        st.write(f"{row['Percentage']:.2f}% of the times, this fix worked in the field - {row['Fix']}")
    st.write()

def print_top_fixes_for_error_code(flag, error_code, top_3_fixes, error_counts, Error_df):

    """
    This function prints the top fixes for a given error code based on its frequency and field service summary.

    Parameters:
    flag (int): Indicator to determine the display format (0 for all fixes, 3 for top 3 fixes).
    error_code (str): The error code to filter the data.
    top_3_fixes (pd.DataFrame): DataFrame containing the top fixes for each error code.
    error_counts (pd.Series): Series containing the count of each error code.
    Error_df (pd.DataFrame): DataFrame containing error details.

    """
    
    filtered_df = Error_df[Error_df['Nexcimer Exception ID (CVX-300 Fault Code)'] == error_code]
    # st.write(filtered_df)
    if not filtered_df.empty:
        error_row = filtered_df.iloc[0]
        st.markdown(f"**<span style='font-size:18px;'>The Error Simplified:</span>** {error_row['Translation Rationale']}", unsafe_allow_html=True)

        st.markdown(f"**<span style='font-size:16px;'>Error Popup Text:</span>** {error_row['Error Popup Text']}", unsafe_allow_html=True)
        st.markdown(f"<i>Subtext:</i> {error_row['Subtext']}", unsafe_allow_html=True)

    # Further processing with error_row
    else:
        st.write(f"No rows found in the data for error_code {error_code}")
        return
    
    sorted_fault_codes = error_counts.sort_values(ascending=False)
    # st.write(sorted_fault_codes) # Debug statement
    total_fault_occurrences = len(sorted_fault_codes)
    found = False
    # Calculating the frequency of the error codes and putting them in a percentage bin based on the same
    for rank, (fault_code, count) in enumerate(sorted_fault_codes.items(), start=1):
        if fault_code == error_code:
            if rank <= total_fault_occurrences * 0.1:
                percentile_range = "Top 10%"
            elif rank <= total_fault_occurrences * 0.25:
                percentile_range = "10-25%"
            elif rank <= total_fault_occurrences * 0.5:
                percentile_range = "25-50%"
            else:
                percentile_range = "50% and above"
                
            st.write(f"Based on the frequency of the occurrence of fault code {fault_code}, the rank is {rank} ({percentile_range}) (Frequency: {count})")
            found = True
            break

    if not found:
        st.write(f"Error code {error_code} does not have any available fixes. Please contact customer support if further assistance is required!")
        return
    
    st.markdown(f"**<span style='font-size:20px;'>Top fix that solved this error:</span>**", unsafe_allow_html=True)

    if flag == 0:
        display_all_fixes_for_fault_code(error_code, top_3_fixes)
    elif flag == 3:
        display_top_fixes_for_fault_code(error_code, top_3_fixes)   

    return


def analyze_error_codes(flag, user_error_code, top_3_fixes, error_counts, Error_df):
    try:
        # Converting the user error code to a float
        user_error_code = float(user_error_code)
        # Printing the top fixes for the given error code
        print_top_fixes_for_error_code(flag, user_error_code, top_3_fixes, error_counts, Error_df)
    except ValueError:
        # Handling the invalid error code inputs
        st.write("Invalid error code. Please enter a numeric value.")


def expected_vs_actual_VES(data, catheter_id=None):

    """
    This function compares expected and actual VES mean values during procedure mode.
    
    Parameters:
    data (pd.DataFrame): DataFrame containing the data to be analyzed.
    catheter_id (str, optional): The catheter ID to filter the data. Defaults to None.

    Returns:
    pd.DataFrame: DataFrame containing the index, expected mean, actual mean, and the difference.
    """

    if catheter_id is not None:
        data = extract_data_for_catheter(data, catheter_id)
    expected_energies = []   # List to store expected energy values
    results = []  # List to store results
    in_procedure_mode = False  # Flag to track procedure mode
    
    # Iterating over each row in the DataFrame

    for i, row in data.iterrows():
        # Checking if the system is in procedure mode
        if row['MessageID'] == 'SYSTEM_MODE' and row['AddInfo'] == '[PROCEDURE]':
            in_procedure_mode = True
        elif row['MessageID'] == 'SYSTEM_MODE' and row['AddInfo'] != '[PROCEDURE]':
            in_procedure_mode = False
            expected_energies = []

        if in_procedure_mode:
            # st.write(row['MessageID'], row['AddInfo'])
            if row['MessageID'] == 'VES_EXPECTED_ENERGY':
                # st.write(f"running procedure mode at index {i}")
                # st.write(row)
                try:
                     # Converting expected energy value to float and store it
                    expected_energy = float(row['AddInfo'].strip('[]'))
                    expected_energies.append(expected_energy)
                    
                except ValueError:
                    st.write(f"Debug: Could not convert expected energy to float at index {i}: {row['AddInfo']}")
            elif row['MessageID'] == 'VES_MEAN':
                if expected_energies:
                    # Calculating the expected mean
                    expected_mean = sum(expected_energies) / len(expected_energies)
                    try:
                        # Converting actual mean value to float and store it in result
                        actual_mean = float(row['AddInfo'].strip('[]'))
                        difference = actual_mean - expected_mean
                        results.append({
                            'index': i,
                            'expected_mean': expected_mean,
                            'actual_mean': actual_mean,
                            'difference': difference
                        })
                    except ValueError:
                        st.write(f"Debug: Could not convert actual mean to float at index {i}: {row['AddInfo']}")
                    # st.write('YELLO', expected_energies)
                    expected_energies = []

    # Converting results to DataFrame and return from the function
    results_df = pd.DataFrame(results)
    return results_df

def expected_vs_actual_PES(data, catheter_id=None):
    """
    This function compares expected and actual PES mean values during procedure mode.
    
    Parameters:
    data (pd.DataFrame): DataFrame containing the data to be analyzed.
    catheter_id (str, optional): The catheter ID to filter the data. Defaults to None.

    Returns:
    pd.DataFrame: DataFrame containing the index, expected mean, actual mean, and the difference.
    """

    if catheter_id is not None:
        data = extract_data_for_catheter(data, catheter_id)
        
    expected_energies = []
    results = []
    in_procedure_mode = False
    
    # Iterating over each row in the DataFrame
    for i, row in data.iterrows():
        # Checking if the system is in procedure mode
        if row['MessageID'] == 'SYSTEM_MODE' and row['AddInfo'] == '[PROCEDURE]':
            in_procedure_mode = True
        elif row['MessageID'] == 'SYSTEM_MODE' and row['AddInfo'] != '[PROCEDURE]':
            in_procedure_mode = False
            expected_energies = []

        if in_procedure_mode:
            # st.write(row['MessageID'], row['AddInfo']) # Debug statements
            if row['MessageID'] == 'PES_EXPECTED_ENERGY':
                # st.write(f"running procedure mode at index {i}") # Debug Statement
                # st.write(row) # Debug Statement
                try:
                    # Converting the expected energy value to float and storing it if greater than 0
                    expected_energy = float(row['AddInfo'].strip('[]'))
                    if expected_energy > 0: 
                        expected_energies.append(expected_energy)
                    
                except ValueError:
                    st.write(f"Debug: Could not convert expected energy to float at index {i}: {row['AddInfo']}")
            elif row['MessageID'] == 'PES_MEAN':
                if expected_energies:
                    # Calculating the expected mean
                    expected_mean = sum(expected_energies) / len(expected_energies)
                    try:
                        #  Converting the actual mean value to float and storing it in results
                        actual_mean = float(row['AddInfo'].strip('[]'))
                        difference = actual_mean - expected_mean
                        results.append({
                            'index': i,
                            'expected_mean': expected_mean,
                            'actual_mean': actual_mean,
                            'difference': difference
                        })
                    except ValueError:
                        st.write(f"Debug: Could not convert actual mean to float at index {i}: {row['AddInfo']}")
                    # st.write('YELLO', expected_energies)
                    expected_energies = []

    results_df = pd.DataFrame(results)
    return results_df

def expected_vs_actual_CES(data, catheter_id=None):

    # Compares the actual CES mean values during procedure mode.


    if catheter_id is not None:
        data = extract_data_for_catheter(data, catheter_id)
    results = []

    in_procedure_mode = False
    
    
    for i, row in data.iterrows():
        if row['MessageID'] == 'SYSTEM_MODE' and row['AddInfo'] == '[PROCEDURE]':
            in_procedure_mode = True
        elif row['MessageID'] == 'SYSTEM_MODE' and row['AddInfo'] != '[PROCEDURE]':
            in_procedure_mode = False

        if in_procedure_mode:

            if row['MessageID'] == 'CES_MEAN':
                
                try:
                    actual_mean = float(row['AddInfo'].strip('[]'))
                    results.append({
                        'index': i,      
                        'actual_mean': actual_mean,
                    })
                except ValueError:
                    st.write(f"Debug: Could not convert actual mean to float at index {i}: {row['AddInfo']}")
                    
    results_df = pd.DataFrame(results)
    return results_df


def extract_data_for_catheter(data, catheter_id):

    """
    this function extracts data for a specific catheter ID.
    
    Parameters:
    data (pd.DataFrame): DataFrame containing the data to be filtered.
    catheter_id (str): The catheter ID to filter the data.

    Returns:
    pd.DataFrame: DataFrame containing data for the specified catheter ID.
    """

    extracted_data = []  # List to store extracted data
    extracting = False  # Flag to start/stop extracting data
    valid_message_ids = {'CATHETER_ID', 'SYSTEM_MODE', 'VES_EXPECTED_ENERGY', 'VES_MEAN', 'PES_EXPECTED_ENERGY', 'PES_MEAN'}
    # st.write(data, catheter_id)
    last_system_mode = None  # To keep track of the last system mode

    for index, row in data.iterrows():
        if row['MessageID'] == 'SYSTEM_MODE':
            # Keeping track of the last system mode
            last_system_mode = row

        # Start extracting data when the specified catheter ID is found
        if row['MessageID'] == 'CATHETER_ID' and row['AddInfo'] == '[' + catheter_id + ']':
            extracting = True
            if last_system_mode is not None:
                extracted_data.append(last_system_mode)
                last_system_mode = None
            extracted_data.append(row)
        # Stop extracting data when a different catheter ID is found
        elif extracting and row['MessageID'] == 'CATHETER_ID' and row['AddInfo'] != '[' + catheter_id + ']':
            extracting = False
        # Continue extracting valid message IDs
        elif extracting and row['MessageID'] in valid_message_ids:
            extracted_data.append(row)

    result_df = pd.DataFrame(extracted_data)
    st.write(result_df)
    return result_df


def combine_files(files):

    """
    This function combines multiple CSV files into a single DataFrame.
    
    Parameters:
    files (list): List of file objects to be combined.

    Returns:
    pd.DataFrame: Combined DataFrame from all the files.
    """

    dataframes = []  # List to store individual DataFrames
    for file in files:
        try:
            df = pd.read_csv(file, header=None, quotechar='"', sep=r',(?![^\[]*\])', engine='python')
            num_cols = len(df.columns)
            # st.write(f"Number of columns in file {file.name}: {num_cols}")  # Debug Statement
    
            # Assigning column names based on the number of columns

            if num_cols == 6:
                column_names = ["ID", "SysTime", "Codes", "MessageID", "AddInfo", "N"]
            elif num_cols == 5:
                column_names = ["ID", "SysTime", "Codes", "MessageID", "AddInfo"]
            else:
                st.warning(f"Unexpected number of columns ({num_cols}) in file {file.name}. Skipping this file.")
                continue
            
            df.columns = column_names
            
            # Dropping the 'N' column if present
            if 'N' in df.columns:
                df.drop(columns=['N'], inplace=True)
            
            dataframes.append(df)
        
        except pd.errors.ParserError as e:
            st.error(f"Error parsing file {file.name}: {e}")
            continue
    
    if dataframes:
        # Combining all the DataFrames into one
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df
    else:
        st.error("No valid data files to combine.")
        return None
