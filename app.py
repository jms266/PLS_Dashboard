#  Importing all the required libraries and functions
# All the functions can be found in either data_processing2.py or visualization2.py (if it is a plot of any kind, it will be in visualization2.py)
import streamlit as st
from data_processing2 import analyze_lasing_trains, get_unique_catheters_from_dataset, calculate_top_fixes, get_catheter_info, analyze_error_codes, expected_vs_actual_VES, expected_vs_actual_CES, expected_vs_actual_PES, combine_files, load_data
from visualization2 import plot_laser_shots, plot_expected_vs_actual, plot_differences, plot_exception_counts1, plot_exception_counts2, plot_energy_boxplot, plot_comparison_actual, plot_exception_messageids, plot_contains_exception_messageids, plot_comparison, plot_vessel_degradation
import pandas as pd

# Loading the data from excel files for error code analysis
PLS_df = pd.read_excel("c:/Users/320258268/OneDrive - Philips/Desktop/output.xlsx")
Error_df = pd.read_excel("c:/Users/320258268/OneDrive - Philips/Desktop/ErrorCodes.xlsx")
catheterdesc_df = pd.read_excel("c:/Users/320258268/OneDrive - Philips/Desktop/CathPinCodes.xlsx")
catheterdesc_df['Pin Code'] = catheterdesc_df['Pin Code'].astype(str)

def main():

    # Setting up the Streamlit page configuration

    st.set_page_config(page_title='PLS Dashboard', layout='wide')

    # Applying custom CSS styling for the Streamlit app

    st.markdown("""
    <style>
        /* Main background */
        .main {
            background-color: #ffffff !important;
        }
        /* Sidebar background */
        .css-1d391kg {
            background-color: #f0f2f6 !important;
        }
        /* Button styling */
        .stButton>button {
            background-color: #4CAF50 !important;
            color: white !important;
        }
        .stButton>button:hover {
            background-color: #45a049 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Displaying the title of the Streamlit app

    st.title('PLS Dashboard')

    # Initializing session state variables if they don't exist
    if 'catheter_id' not in st.session_state:
        st.session_state.catheter_id = ''
    if 'dataset_name' not in st.session_state:
        st.session_state.dataset_name = ''
    if 'show_catheter_form' not in st.session_state:
        st.session_state.show_catheter_form = False
    if 'show_error_form' not in st.session_state:
        st.session_state.show_error_form = False
    if 'show_visualization' not in st.session_state:
        st.session_state.show_visualization = False
    if 'show_lasing_analysis' not in st.session_state:
        st.session_state.show_lasing_analysis = False
    if 'show_expected_vs_actual' not in st.session_state:
        st.session_state.show_expected_vs_actual = False
    if 'show_expected_vs_actual_PES' not in st.session_state:
        st.session_state.show_expected_vs_actual_PES = False
    if 'show_multiple_file_analysis' not in st.session_state:
        st.session_state.show_multiple_file_analysis = False
    if 'selected_catheter' not in st.session_state:
        st.session_state.selected_catheter = None


    with st.sidebar:
        # Sidebar header
        st.header("Navigation")
        # Creating a radio button for navigation options
        selection = st.radio("Go to", ["Catheter Analysis", "Error Codes", "Visualizations", "Lasing Analysis", "Expected vs Actual VES", "Expected vs Actual PES", "Multiple File Analysis"])

    # Based on the user's selection, controlling the visibility of different sections

    if selection == "Catheter Analysis":
        st.session_state.show_catheter_form = True
        st.session_state.show_error_form = False
        st.session_state.show_visualization = False
        st.session_state.show_lasing_analysis = False
        st.session_state.show_expected_vs_actual = False
        st.session_state.show_expected_vs_actual_PES = False
        st.session_state.show_multiple_file_analysis = False
    elif selection == "Error Codes":
        st.session_state.show_catheter_form = False
        st.session_state.show_error_form = True
        st.session_state.show_visualization = False
        st.session_state.show_lasing_analysis = False
        st.session_state.show_expected_vs_actual = False
        st.session_state.show_expected_vs_actual_PES = False
        st.session_state.show_multiple_file_analysis = False
    elif selection == "Visualizations":
        st.session_state.show_catheter_form = False
        st.session_state.show_error_form = False
        st.session_state.show_visualization = True
        st.session_state.show_lasing_analysis = False
        st.session_state.show_expected_vs_actual = False
        st.session_state.show_expected_vs_actual_PES = False
        st.session_state.show_multiple_file_analysis = False
    elif selection == "Lasing Analysis":
        st.session_state.show_catheter_form = False
        st.session_state.show_error_form = False
        st.session_state.show_visualization = False
        st.session_state.show_lasing_analysis = True
        st.session_state.show_expected_vs_actual = False
        st.session_state.show_expected_vs_actual_PES = False
        st.session_state.show_multiple_file_analysis = False
    elif selection == "Expected vs Actual VES":
        st.session_state.show_catheter_form = False
        st.session_state.show_error_form = False
        st.session_state.show_visualization = False
        st.session_state.show_lasing_analysis = False
        st.session_state.show_expected_vs_actual = True
        st.session_state.show_expected_vs_actual_PES = False
        st.session_state.show_multiple_file_analysis = False
    elif selection == "Expected vs Actual PES":
        st.session_state.show_catheter_form = False
        st.session_state.show_error_form = False
        st.session_state.show_visualization = False
        st.session_state.show_lasing_analysis = False
        st.session_state.show_expected_vs_actual = False
        st.session_state.show_expected_vs_actual_PES = True
        st.session_state.show_multiple_file_analysis = False
    elif selection == "Multiple File Analysis":
        st.session_state.show_catheter_form = False
        st.session_state.show_error_form = False
        st.session_state.show_visualization = False
        st.session_state.show_lasing_analysis = False
        st.session_state.show_expected_vs_actual = False
        st.session_state.show_expected_vs_actual_PES = False
        st.session_state.show_multiple_file_analysis = True


    # Single File Analysis
    if st.session_state.show_catheter_form or st.session_state.show_error_form or st.session_state.show_visualization or st.session_state.show_lasing_analysis or st.session_state.show_expected_vs_actual or st.session_state.show_expected_vs_actual_PES:
            data = None # Initializing variable to store data
            unique_catheters = [] # Initializing list to store unique catheter IDs
            flag = 3 # Initializing the flag for error analysis

            # File uploader for CSV files
            if st.session_state.show_catheter_form or st.session_state.show_visualization or st.session_state.show_lasing_analysis or st.session_state.show_expected_vs_actual or st.session_state.show_expected_vs_actual_PES:
                
                data_file = st.file_uploader("Upload the Data file", type=['csv'])
                if data_file is not None:
                    data = load_data(data_file)  # Loading the data from the uploaded file
                    unique_catheters = get_unique_catheters_from_dataset(data) # Getting the unique catheter IDs from the dataset
                    # Filter the DataFrame to only include relevant catheters
                    catheterdesc_df_filtered = catheterdesc_df[catheterdesc_df['Pin Code'].isin(unique_catheters)]
        
                    # Create the dropdown options as "Description (Pin Code)"
                    catheter_options = catheterdesc_df_filtered.apply(
                        lambda row: f"{row['Description']} ({row['Pin Code']})", axis=1).tolist()

                else:
                    st.write("Please upload a file to proceed.")
                    catheter_options = []  # Providing an empty write operation for formatting


            # Catheter Analysis Form
    
            # st.write("Unique Catheters:", unique_catheters)
            if st.session_state.show_catheter_form:
                    with st.form(key='catheter_analysis_form'):
                        st.subheader('Catheter Analysis')
                        if catheter_options:
                            selected_catheter_display = st.selectbox(
                                'Select the catheter ID',
                                options=catheter_options,
                                index=0 if st.session_state.catheter_id not in unique_catheters else catheter_options.index(
                                    f"{catheterdesc_df.loc[catheterdesc_df['Pin Code'] == st.session_state.catheter_id, 'Description'].values[0]} ({st.session_state.catheter_id})"
                                )
                            )

                         # Extracting the selected Pin Code from the dropdown
                            st.session_state.catheter_id = selected_catheter_display.split(' (')[1][:-1]
                        else:
                            st.write("No matching catheters found in the uploaded file.")

                        submit_catheter = st.form_submit_button('Submit Catheter Analysis')
                        if submit_catheter and st.session_state.catheter_id:
                            get_catheter_info(data, st.session_state.catheter_id)
                        else:
                            st.write("Please select a valid catheter ID from the dropdown.")



            # Error Codes Form
            if st.session_state.show_error_form:
                top_3_fixes = calculate_top_fixes(PLS_df)  # Calculating the top 3 fixes for fault codes
                error_counts = PLS_df['Fault Code'].value_counts() # Counting the occurrences of each fault code

                # st.write(error_counts) # Debug statement

               # Button to display the list of errors and their descriptions
                if st.button('List of Errors'):
                    st.subheader('List of Errors and Their Descriptions')

                    error_codes_with_desc = Error_df[['Nexcimer Exception ID (CVX-300 Fault Code)', 'Name']]

                    error_codes_with_desc = error_codes_with_desc.dropna(subset=['Nexcimer Exception ID (CVX-300 Fault Code)'])

                     # Split the data into two equal parts for two-column display
                    split_index = len(error_codes_with_desc) // 3
                    left_column, middle_column, right_column = st.columns(3)


                    # Display the first part in the left column
                    with left_column:
                        for index, row in error_codes_with_desc.iloc[:split_index].iterrows():
                            error_code = row['Nexcimer Exception ID (CVX-300 Fault Code)']
                            description = row['Name']
                            st.markdown(f"**{error_code}**: {description}")

                    # Display the second part in the middle column
                    with middle_column:
                        for index, row in error_codes_with_desc.iloc[split_index:2*split_index].iterrows():
                            error_code = row['Nexcimer Exception ID (CVX-300 Fault Code)']
                            description = row['Name']
                            st.markdown(f"**{error_code}**: {description}")

                    # Display the third part in the right column
                    with right_column:
                        for index, row in error_codes_with_desc.iloc[2*split_index:].iterrows():
                            error_code = row['Nexcimer Exception ID (CVX-300 Fault Code)']
                            description = row['Name']
                            st.markdown(f"**{error_code}**: {description}")                   

                with st.form(key='error_codes_form'):
                    st.subheader('Top 3 Fixes')
                    user_error_code1 = st.text_input('Enter the error code for top fixes') # Getting the error code for the top 3 fixes button
                    submit_top_fixes = st.form_submit_button('Show Top 3 Fixes')
                   

                with st.form(key='all_fixes_form'):
                    st.subheader('All Available Fixes')
                    user_error_code2 = st.text_input('Enter the error code for all fixes') # Getting the error code for the all available fixes button
                    submit_all_fixes = st.form_submit_button('Show All Fixes')

                   
                # Simple logic to see if the user wants to see top 3 fixes or all available fixes

                if submit_top_fixes:
                    flag = 3
                    analyze_error_codes(flag, user_error_code1, top_3_fixes, error_counts, Error_df) # refer data_processing2.py for details on this function

                if submit_all_fixes:
                    flag = 0
                    analyze_error_codes(flag, user_error_code2, top_3_fixes, error_counts, Error_df) # refer data_processing2.py for details on this function


            # Visualizations tab in the sidebar

            if st.session_state.show_visualization:
                st.subheader('Visualizations')
                if data_file is None:
                    st.write("Please upload a file before submitting the form!")
                else:
                    if st.button('Plot Laser Shots Fired'):
                        plot_laser_shots(data) # Plotting laser shots data (function logic available in visualization2.py)
                    if st.button('Plot Expected vs Actual VES Mean Energy'):
                        df_expected_vs_actual1 = expected_vs_actual_VES(data) # refer data_processing2.py for details on this function
                        plot_expected_vs_actual(df_expected_vs_actual1) # Plotting VES mean energy
                        plot_differences(df_expected_vs_actual1)  # Plotting the differences between VES expected and actual energy means
                    if st.button('Plot Expected vs Actual PES Mean Energy'):
                        df_expected_vs_actual2 = expected_vs_actual_PES(data) # refer data_processing2.py for details on this function
                        plot_expected_vs_actual(df_expected_vs_actual2)  # Plotting PES mean energy
                        plot_differences(df_expected_vs_actual2) # Plotting the differences between PES expected and actual energy means
                    if st.button('Most Frequent Exeptions'):
                        # Different functions to see different kinds of visualizations that signify the exceptions present in the log files (please refer to visualization2.py for further details)
                        plot_exception_messageids(data)
                        plot_exception_counts1(data)
                        plot_exception_counts2(data)
                        plot_contains_exception_messageids(data)
                    if st.button("Plot Vessel Degradation Factor"):
                        plot_vessel_degradation(data) # Plotting the vessel degradation factor values
                    
                    if st.button('Plot Energy Boxplot'):
                        catheter_result_df2 = expected_vs_actual_VES(data, catheter_id=st.session_state.selected_catheter)
                        if not catheter_result_df2.empty:
                            plot_energy_boxplot(catheter_result_df2) # Plotting the energy boxplot for selected catheter
                        else:
                            st.write('Empty') # Handling the case when no data is available

                    # Comparing the VES and PES Energy data

                    if st.button('Compare VES vs PES'):
                        ves_data = expected_vs_actual_VES(data) # refer data_processing2.py for details on this function
                        pes_data = expected_vs_actual_PES(data) # refer data_processing2.py for details on this function
            
                        if not ves_data.empty and not pes_data.empty:
                            st.write('VES Data:', ves_data)
                            st.write('PES Data:', pes_data)
                            plot_comparison(ves_data, pes_data)

                    # Comparing the PES and CES Energy data

                    if st.button('Compare PES vs CES'):
                        pes_data = expected_vs_actual_PES(data) # refer data_processing2.py for details on this function
                        ces_data = expected_vs_actual_CES(data) # refer data_processing2.py for details on this function
            
                        if not pes_data.empty and not ces_data.empty:
                            st.write('PES Data:', pes_data)
                            st.write('CES Data:', ces_data)
                            plot_comparison_actual(pes_data, ces_data) # refer visualization2.py for details on this function

             # Lasing Analysis Form

            if st.session_state.show_lasing_analysis:
                if data_file is None:
                    st.write("Please upload a file before submitting the form!")
                else:
                    with st.form(key='lasing_analysis_form'):
                        st.subheader('Lasing Analysis')
                        st.session_state.catheter_id = st.selectbox('Select the catheter ID', options=unique_catheters, index=unique_catheters.index(st.session_state.catheter_id) if st.session_state.catheter_id in unique_catheters else 0)
                        submit_lasing_analysis = st.form_submit_button('Submit Lasing Analysis')
                        if submit_lasing_analysis:
                            analyze_lasing_trains(data, st.session_state.catheter_id)  # Analyzing the lasing trains for the selected catheter (# refer data_processing2.py for details on this function)
            
            # Expected vs Actual VES Energy Analysis (Data slicing option based on catheter id)

            if st.session_state.show_expected_vs_actual and data is not None:
                if data_file is None:
                    st.write("Please upload a file before submitting the form!")
                else:
                    st.subheader('Expected vs Actual VES Energy Analysis')
                    result_df = expected_vs_actual_VES(data) # refer data_processing2.py for details on this function
                    st.write("Expected vs Actual VES Energy Analysis Results")
                    st.write(result_df)

                    if not result_df.empty:
                        if st.button('Plot Expected vs Actual VES Means'):
                            plot_expected_vs_actual(result_df)  # Plotting the VES mean energy results
                        if st.button('Plot Differences'):
                            plot_differences(result_df)   # Plotting the differences in VES mean energy
                        
                        st.subheader('Select Catheter ID for Detailed Analysis')
                        for catheter_id in unique_catheters:
                            if st.button(catheter_id):
                                st.session_state.selected_catheter = catheter_id

                        if st.session_state.selected_catheter:
                            st.subheader(f'Expected vs Actual VES Mean Energy for Catheter ID: {st.session_state.selected_catheter}')
                            catheter_result_df = expected_vs_actual_VES(data, catheter_id=st.session_state.selected_catheter) # refer data_processing2.py for details on this function
                            st.write(f"Results for Catheter ID: {st.session_state.selected_catheter}")
                            st.write(catheter_result_df)

                            if not catheter_result_df.empty:
                                if st.button('Plot Expected vs Actual Means for Selected Catheter'):
                                    plot_expected_vs_actual(catheter_result_df) # Plotting the VES mean energy for selected catheter id
                                if st.button('Plot Differences for Selected Catheter'):
                                    plot_differences(catheter_result_df) # Plotting differences for selected catheter id

            # Expected vs Actual PES Energy Analysis (Data slicing option based on catheter id)

            if st.session_state.show_expected_vs_actual_PES and data is not None:
                if data_file is None:
                    st.write("Please upload a file before submitting the form!")
                else:
                    st.subheader('Expected vs Actual PES Energy Analysis')
                    result_df = expected_vs_actual_PES(data) # refer data_processing2.py for details on this function (Computing expected vs actual PES energy)
                    st.write("Expected vs Actual PES Energy Analysis Results")
                    st.write(result_df)

                    if not result_df.empty:
                        # Button to plot expected vs actual PES means
                        if st.button('Plot Expected vs Actual PES Means'):
                            plot_expected_vs_actual(result_df)
                        # Button to plot differences
                        if st.button('Plot Differences'):
                            plot_differences(result_df)
                        
                        st.subheader('Select Catheter ID for Detailed Analysis')

                        # Creating buttons for each catheter ID to view detailed analysis
                        for catheter_id in unique_catheters:
                            if st.button(catheter_id):
                                st.session_state.selected_catheter = catheter_id

                        # Displaying detailed analysis for the selected catheter

                        if st.session_state.selected_catheter:
                            st.subheader(f'Expected vs Actual PES Mean Energy for Catheter ID: {st.session_state.selected_catheter}')
                            catheter_result_df = expected_vs_actual_PES(data, catheter_id=st.session_state.selected_catheter)
                            st.write(f"Results for Catheter ID: {st.session_state.selected_catheter}")
                            st.write(catheter_result_df)

                            if not catheter_result_df.empty:
                                 # Button to plot expected vs actual PES means for selected catheter
                                if st.button('Plot Expected vs Actual PES Means for Selected Catheter'):
                                    plot_expected_vs_actual(catheter_result_df)
                                # Button to plot differences for selected catheter
                                if st.button('Plot Differences for Selected Catheter'):
                                    plot_differences(catheter_result_df)

    # Multiple File Analysis
    if st.session_state.show_multiple_file_analysis:
        st.subheader('Multiple File Analysis')
        # File uploader for multiple CSV files
        uploaded_files = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True)

        if uploaded_files:
            combined_df = combine_files(uploaded_files)  # Combining multiple files into a single DataFrame
            st.write("Combined Dataframe:", combined_df)  

            unique_catheters = get_unique_catheters_from_dataset(combined_df)  # Extracting unique catheter IDs from the combined data (refer data_processing2.py for details on this function)


            with st.form(key='catheter_analysis_form'):
                st.subheader('Catheter Analysis')
                st.session_state.catheter_id = st.selectbox('Select the catheter ID', options=unique_catheters, index=unique_catheters.index(st.session_state.catheter_id) if st.session_state.catheter_id in unique_catheters else 0)
                submit_catheter = st.form_submit_button('Submit Catheter Analysis')
                if submit_catheter:
                    get_catheter_info(combined_df, st.session_state.catheter_id)  # Analyzing laser shots information based on selected catheter ID (data_processing2.py)

            top_3_fixes = calculate_top_fixes(PLS_df)  # Calculating the top fixes for fault codes
            error_counts = PLS_df['Fault Code'].value_counts()   # Counting occurrences of each fault code

            st.subheader('Visualizations')
            if st.button('Visualize Data'):
                plot_laser_shots(combined_df)  # Plotting laser shots data

            with st.form(key='lasing_analysis_form'):
                st.subheader('Lasing Analysis')
                st.session_state.catheter_id = st.selectbox('Select the catheter ID', options=unique_catheters, index=unique_catheters.index(st.session_state.catheter_id) if st.session_state.catheter_id in unique_catheters else 0)
                submit_lasing_analysis = st.form_submit_button('Submit Lasing Analysis')
                if submit_lasing_analysis:
                    analyze_lasing_trains(combined_df, st.session_state.catheter_id)  # Analyzing lasing trains for the selected catheter

            st.subheader('Expected vs Actual Energy Analysis')
            result_df = expected_vs_actual_VES(combined_df) # Computing expected vs actual VES energy
            st.write("Expected vs Actual Energy Analysis Results")
            st.write(result_df)

            if not result_df.empty:
                # Button to plot expected vs actual VES means
                if st.button('Plot Expected vs Actual Means'):
                    plot_expected_vs_actual(result_df)
                # Button to plot differences
                if st.button('Plot Differences'):
                    plot_differences(result_df)

                st.subheader('Select Catheter ID for Detailed Analysis')
                # Creating buttons for each catheter ID to view detailed analysis

                for catheter_id in unique_catheters:
                    if st.button(catheter_id):
                        st.session_state.selected_catheter = catheter_id

                # Displaying detailed analysis for the selected catheter

                if st.session_state.selected_catheter:
                    st.subheader(f'Expected vs Actual Energy for Catheter ID: {st.session_state.selected_catheter}')
                    catheter_result_df = expected_vs_actual_VES(combined_df, catheter_id=st.session_state.selected_catheter)
                    st.write(f"Results for Catheter ID: {st.session_state.selected_catheter}")
                    st.write(catheter_result_df)

                    if not catheter_result_df.empty:
                        # Button to plot expected vs actual VES means for selected catheter
                        if st.button('Plot Expected vs Actual Means for Selected Catheter'):
                            plot_expected_vs_actual(catheter_result_df)
                         # Button to plot differences for selected catheter
                        if st.button('Plot Differences for Selected Catheter'):
                            plot_differences(catheter_result_df)

    else:
        st.write("")  # Handling the case when no condition is met

# Main function to run the Streamlit app

if __name__ == '__main__':
    main()
