# This file contains all the required functions for different plots/visualizations present in the dashboard
# Importing the required libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_laser_shots(dff):

    """
    This function plots the number of laser shots fired for each catheter ID.
    
    Parameters:
    dff (pd.DataFrame): DataFrame containing the data to be plotted.
    """
    dff.columns = ["ID", "SysTime", "Codes", "MessageID", "AddInfo"]
    # Handling the invalid date formats by assigning a default value
    dff['SysTime'] = dff['SysTime'].apply(lambda x: x if pd.to_datetime(x, errors='coerce') is not pd.NaT else '9999-01-01')
    # Filtering the data for relevant MessageIDs
    filtered_data = dff[dff['MessageID'].isin(['CATHETER_ID', 'VES_EXPECTED_ENERGY'])]
    catheter_shots = {}
    current_catheter_id = None
    # Looping through the filtered data to count laser shots for each catheter ID
    for index, row in filtered_data.iterrows():
        if row['MessageID'] == 'CATHETER_ID':
            current_catheter_id = row['AddInfo'].strip('[]')
        elif row['MessageID'] == 'VES_EXPECTED_ENERGY':
            if current_catheter_id:
                catheter_shots[current_catheter_id] = catheter_shots.get(current_catheter_id, 0) + 1
 
    catheter_ids = list(catheter_shots.keys())
    shots_fired = list(catheter_shots.values())
   
    # Plotting the data
    plt.figure(figsize=(10, 6))
    plt.plot(catheter_ids, shots_fired, marker='o')
    plt.title('Number of Laser Shots Fired for Each Catheter ID')
    plt.xlabel('Catheter ID')
    plt.ylabel('Number of Laser Shots')
    plt.xticks(rotation=90)
    plt.grid(True)
    st.pyplot(plt)


def plot_expected_vs_actual(df):

    """
    this function plots the expected vs actual mean energy.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data to be plotted.
    """

    plt.figure(figsize=(12, 6))
    plt.plot(df['index'], df['expected_mean'], label='Expected Mean', color='blue')
    plt.plot(df['index'], df['actual_mean'], label='Actual Mean', color='red')
    plt.xlabel('Index')
    plt.ylabel('Mean Energy')
    plt.title('Expected vs Actual Mean Energy')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)


def plot_differences(df):

    """
    this function plots the difference between actual and expected mean energy.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data to be plotted.
    """

    plt.figure(figsize=(12, 6))
    plt.plot(df['index'], df['difference'], label='Difference', color='green')
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Index')
    plt.ylabel('Difference in Mean Energy')
    plt.title('Difference between Actual & Expected Mean Energy (Actual - Expected)')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)


def plot_exception_counts1(df):

    """
    this function plots the most common exceptions for MAINS_VOLTAGE_MAXIMUM_EXCEPTION.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data to be plotted.
    """

    # Filtering the rows where MessageID contains "MAINS_VOLTAGE_MAXIMUM_EXCEPTION"
    exceptions_df = df[df['MessageID'].str.contains('MAINS_VOLTAGE_MAXIMUM_EXCEPTION', na=False)]

    # Counting the occurrences of each type of exception in AddInfo column
    exception_counts = exceptions_df['AddInfo'].value_counts()

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.barplot(x=exception_counts.index, y=exception_counts.values, palette='viridis')
    plt.title('Most Common Exceptions')
    plt.xlabel('MAINS_VOLTAGE_MAXIMUM_EXCEPTION')
    plt.ylabel('Count')
    plt.xticks(rotation=90)
    plt.grid(True)
    st.pyplot(plt)

def plot_exception_counts2(df):
    # Filter rows where MessageID contains "MAINS_VOLTAGE_MIN_EXCEPTION"
    exceptions_df = df[df['MessageID'].str.contains('MAINS_VOLTAGE_MIN_EXCEPTION', na=False)]

    # Count occurrences of each type of exception in AddInfo column
    exception_counts = exceptions_df['AddInfo'].value_counts()

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.barplot(x=exception_counts.index, y=exception_counts.values, palette='viridis')
    plt.title('Most Common Exceptions')
    plt.xlabel('MAINS_VOLTAGE_MIN_EXCEPTION')
    plt.ylabel('Count')
    plt.xticks(rotation=90)
    plt.grid(True)
    st.pyplot(plt)

def plot_exception_messageids(df):
    # Filtering the rows where MessageID exactly matches 'EXCEPTION'
    exact_exception_df = df[df['MessageID'] == 'EXCEPTION']

    # Counting the number of occurrences of each MessageID with exact 'EXCEPTION'
    exact_exception_counts = exact_exception_df['AddInfo'].value_counts()

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.barplot(x=exact_exception_counts.index, y=exact_exception_counts.values, palette='viridis')
    plt.title('MessageID = "EXCEPTION"')
    plt.xlabel('Exception IDs')
    plt.ylabel('Count')
    plt.xticks(rotation=90)
    plt.grid(True)
    st.pyplot(plt)

def plot_contains_exception_messageids(df):
    # Filtering the rows where MessageID contains 'EXCEPTION'
    contains_exception_df = df[df['MessageID'].str.contains('EXCEPTION', na=False)]

    # Counting the number of occurrences of each MessageID containing 'EXCEPTION'
    contains_exception_counts = contains_exception_df['MessageID'].value_counts()

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.barplot(x=contains_exception_counts.index, y=contains_exception_counts.values, palette='viridis')
    plt.title('MessageIDs containing "EXCEPTION"')
    plt.xlabel('MessageID')
    plt.ylabel('Count')
    plt.xticks(rotation=90)
    plt.grid(True)
    st.pyplot(plt)

def plot_energy_boxplot(df):

    """
    this function plots a boxplot comparing the distribution of expected vs actual VES mean energy.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data to be plotted.
    """

    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df[['expected_mean', 'actual_mean']], palette='Set2')
    plt.title('Distribution of Expected vs Actual VES Mean Energy')
    plt.ylabel('Mean Energy')
    st.pyplot(plt)

def plot_comparison(ves_data, pes_data):

    """
    this function plots the comparison of actual and expected mean energy between VES and PES.

    Parameters:
    ves_data (pd.DataFrame): DataFrame containing VES data.
    pes_data (pd.DataFrame): DataFrame containing PES data.
    """

    fig, ax = plt.subplots(2, 1, figsize=(12, 12))
    
    # Plotting Actual Means
    ax[0].plot(ves_data['index'], ves_data['actual_mean'], label='VES Actual Mean', color='blue')
    ax[0].plot(pes_data['index'], pes_data['actual_mean'], label='PES Actual Mean', color='red')
    ax[0].set_xlabel('Index')
    ax[0].set_ylabel('Actual Mean Energy')
    ax[0].set_title('Actual VES vs PES Mean Energy')
    ax[0].legend()
    ax[0].grid(True)
    
    # Plotting Expected Means
    ax[1].plot(ves_data['index'], ves_data['expected_mean'], label='VES Expected Mean', color='blue')
    ax[1].plot(pes_data['index'], pes_data['expected_mean'], label='PES Expected Mean', color='red')
    ax[1].set_xlabel('Index')
    ax[1].set_ylabel('Expected Mean Energy')
    ax[1].set_title('Expected VES vs PES Mean Energy')
    ax[1].legend()
    ax[1].grid(True)
    
    st.pyplot(fig)

def plot_comparison_actual(pes_data, ces_data):

    """
    This function plots the comparison of actual mean energy between PES and CES.

    Parameters:
    pes_data (pd.DataFrame): DataFrame containing PES data.
    ces_data (pd.DataFrame): DataFrame containing CES data.
    """

    fig, ax = plt.subplots(figsize=(12, 8)) 
    
    # Plotting the Actual Means
    ax.plot(pes_data['index'], pes_data['actual_mean'], label='PES Actual Mean', color='blue')
    ax.plot(ces_data['index'], ces_data['actual_mean'], label='CES Actual Mean', color='red')
    
    ax.set_xlabel('Index')
    ax.set_ylabel('Actual Mean Energy')
    ax.set_title('Actual PES vs CES Mean Energy')
    ax.legend()
    ax.grid(True)
    
    st.pyplot(fig)



def plot_vessel_degradation(df):

    """
    this function plots the vessel degradation factor over time.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data to be plotted.
    """
    # Filtering the data for VESSEL_DEGRADATION_FACTOR
    vessel_degradation_data = df[df['MessageID'] == 'VESSEL_DEGRADATION_FACTOR'][['SysTime', 'AddInfo']]
    
    if vessel_degradation_data.empty:
        st.write("No data found for MessageID 'VESSEL_DEGRADATION_FACTOR'")
        return

    # Cleaning and converting data for plotting
    vessel_degradation_data['AddInfo'] = vessel_degradation_data['AddInfo'].str.strip('[]').astype(float)
    vessel_degradation_data.dropna(inplace=True)

    if vessel_degradation_data.empty:
        st.write("No valid data to plot after conversions")
        return

    # Plotting the data
    plt.figure(figsize=(12, 6))
    plt.plot(vessel_degradation_data['SysTime'], vessel_degradation_data['AddInfo'], label='Vessel Degradation Factor')
    plt.xlabel('Time')
    plt.ylabel('Vessel Degradation Factor')
    plt.title('Vessel Degradation Factor Over Time')
    plt.xticks(rotation = 45)
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)