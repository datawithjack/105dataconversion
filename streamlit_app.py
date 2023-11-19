
import streamlit as st
import pandas as pd
from io import StringIO

# Define the function to apply the final transformations to a DataFrame
def transform_data(df, controller_value, team_value):
    # Drop specified columns
    columns_to_drop = ['Tf+Tc', 'PPO / Total mass', 'Tf\\Tc', 'Height', 'Rsi', 'Ppo', 
                       'LegStiffness', 'Impulse', 'DeviceCount', 'Total']
    df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    # Rename specified columns
    columns_to_rename = {
        'GivenName': 'Given Name', 
        'FamilyName': 'Family Name', 
        'JumpIndex': 'Jump index', 
        'ContactTime': 'Contact time', 
        'FlightTime': 'Flight time'
    }
    df.rename(columns=columns_to_rename, inplace=True)

    # Duplicate columns
    df['First Name'] = df['Given Name']
    df['Last Name'] = df['Family Name']

    # Add empty columns
    empty_columns = ['Controller', 'Team', 'Start mode', 'Mass unit', 'Height Unit', 
                     'Testing Type', 'External mass', 'Drop height']
    for col in empty_columns:
        df[col] = None

    # Populate specified columns based on non-empty Date column
    date_condition = df['Date'].notna()
    df.loc[date_condition, 'Mass unit'] = "Kilogram"
    df.loc[date_condition, 'Height Unit'] = "Centimetre"
    df.loc[date_condition, 'Testing Type'] = "Testing"
    


    # Convert 'Time' column to datetime format and perform the same operation as before
    df['Time'] = pd.to_datetime(df['Time'], format='%I:%M %p')

    # Group by 'First Name' and 'Last Name', and find the minimum time for each group
    min_time_group_new = df.groupby(['First Name', 'Last Name'])['Time'].min().reset_index()

    # Merge the minimum time back to the original dataframe
    new_data_merged = pd.merge(df, min_time_group_new, on=['First Name', 'Last Name'], how='left')

    # Replace the original 'Time' column with the minimum time
    new_data_merged = new_data_merged.drop('Time_x', axis=1)
    new_data_merged = new_data_merged.rename({'Time_y': 'Time'}, axis=1)
    
    # Parse the full timestamp
    new_data_merged['Time'] = pd.to_datetime(new_data_merged['Time'], format='%d/%m/%Y %H:%M')  # Convert to datetime
    new_data_merged['Time'] = new_data_merged['Time'].dt.strftime('%H:%M')
    new_data_merged['Controller'] = controller_value
    new_data_merged['Team'] = team_value


    return new_data_merged


# Streamlit app
st.title('10-5 Data Transformation App')

# Dropdown menu for selecting Controller
controller_options = ['Jack Andrew', 'Alexander Johan Daalhuizen', 'Kenneth Mcmillan']
team_options = ['Development 1', 'Development 2', 'Development 3', 'Sprints','Jumps','Throws','Endurance']

selected_controller = st.selectbox('Select Controller', controller_options)
selected_team = st.selectbox('Select Team', team_options)

# File uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    # Read the uploaded CSV file into a DataFrame
    df = pd.read_csv(uploaded_file)

    # Process the DataFrame with the transform_data function
    transformed_df = transform_data(df, selected_controller, selected_team)

    # Convert the processed DataFrame to CSV
    csv = transformed_df.to_csv(index=False).encode('utf-8')

    # Display download button for the processed CSV
    st.download_button(
        label="Download Processed CSV",
        data=csv,
        file_name='processed.csv',
        mime='text/csv',
    )