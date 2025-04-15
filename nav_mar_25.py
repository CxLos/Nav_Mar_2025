# =================================== IMPORTS ================================= #

import os

# import json
import numpy as np 
import pandas as pd 
from datetime import datetime, timedelta

# import seaborn as sns 
import plotly.graph_objects as go
import plotly.express as px

import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import folium
from folium.plugins import MousePosition

import dash
from dash import dcc, html

# Google Web Credentials
import json
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 'data/~$bmhc_data_2024_cleaned.xlsx'
# print('System Version:', sys.version)
# =================================== DATA ==================================== #

current_dir = os.getcwd()
current_file = os.path.basename(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))
# data_path = 'data/Navigation_Responses.xlsx'
# file_path = os.path.join(script_dir, data_path)
# data = pd.read_excel(file_path)
# df = data.copy()

# Define the Google Sheets URL
sheet_url = "https://docs.google.com/spreadsheets/d/1Vi5VQWt9AD8nKbO78FpQdm6TrfRmg0o7az77Hku2i7Y/edit#gid=78776635"

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials
encoded_key = os.getenv("GOOGLE_CREDENTIALS")

if encoded_key:
    json_key = json.loads(base64.b64decode(encoded_key).decode("utf-8"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
else:
    creds_path = r"C:\Users\CxLos\OneDrive\Documents\BMHC\Data\bmhc-timesheet-4808d1347240.json"
    if os.path.exists(creds_path):
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    else:
        raise FileNotFoundError("Service account JSON file not found and GOOGLE_CREDENTIALS is not set.")

# Authorize and load the sheet
client = gspread.authorize(creds)
sheet = client.open_by_url(sheet_url)
data = pd.DataFrame(client.open_by_url(sheet_url).sheet1.get_all_records())
df = data.copy()

# Trim leading and trailing whitespaces from column names
df.columns = df.columns.str.strip()

# Filtered df where 'Date of Activity:' is in March
df["Date of Activity"] = pd.to_datetime(df["Date of Activity"], errors='coerce')
df = df[df['Date of Activity'].dt.month == 3]

# Get the reporting month:
current_month = datetime(2025, 3, 1).strftime("%B")
report_year = datetime(2025, 3, 1).year

df.columns = df.columns.str.strip()

# Define a discrete color sequence
# color_sequence = px.colors.qualitative.Plotly

# -----------------------------------------------
# print(df.head())
# print('Total entries: ', len(df))
# print('Column Names: \n', df.columns.tolist())
# print('Column Names: \n', df1.columns)
# print('DF Shape:', df.shape)
# print('Dtypes: \n', df.dtypes)
# print('Info:', df.info())
# print("Amount of duplicate rows:", df.duplicated().sum())

# print('Current Directory:', current_dir)
# print('Script Directory:', script_dir)
# print('Path to data:',file_path)

# ================================= Columns Navigation ================================= #

columns = [
  'Timestamp', 
  'Date of Activity', 
  'Person submitting this form:', 
  'Activity Duration (minutes):', 
  'Location Encountered:',
  "Individual's First Name:", 
  "Individual's Date of Birth:", 
  "Individual's Insurance Status:", 
  "Individual's street address:", 
  'City:', 
  'ZIP Code:', 
  'County:', 
  'Type of support given:', 
  'Provide brief support description:', "Individual's Status:", 
  'HMIS SPID Number:', 
  'MAP Card Number', 
  'Gender:', 
  'Race/Ethnicity:',
  'Total travel time (minutes):', 
  'Direct Client Assistance Amount:', 
  'Column 21', 
  "Individual's Last Name:"
  ]

# =============================== Missing Values ============================= #

# missing = df.isnull().sum()
# print('Columns with missing values before fillna: \n', missing[missing > 0])

#  HMIS SPID Number:               14
# MAP Card Number                 14
# Total travel time (minutes):    14

# =============================== Missing Values ============================= #

# missing = df_q1.isnull().sum()
# print('Columns with missing values before fillna: \n', missing[missing > 

# ============================== Data Preprocessing ========================== #

# Check for duplicate columns
# duplicate_columns = df.columns[df.columns.duplicated()].tolist()
# print(f"Duplicate columns found: {duplicate_columns}")
# if duplicate_columns:
#     print(f"Duplicate columns found: {duplicate_columns}")

# Fill Missing Values for df
columns_to_fill = [
    "Total travel time (minutes):",
]

# Fill missing values for categorical columns with 'Unknown'
for column in columns_to_fill:
    if column in df.columns:
        df[column] = df[column].fillna('Unknown')

# # Fill missing values for numerical columns with a specific value (e.g., -1)
df['HMIS SPID Number:'] = df['HMIS SPID Number:'].fillna(-1)
df['MAP Card Number'] = df['MAP Card Number'].fillna(-1)

# ------------------------------- Clients Serviced ---------------------------- #

# # Clients Serviced:
clients_served = len(df)
clients_served = str(clients_served)
# # print('Patients Served This Month:', patients_served)

# ------------------------------ Navigation Hours ---------------------------- #

# # Groupby Activity Duration:
df_duration = df['Activity Duration (minutes):'].sum()/60
df_duration = round(df_duration) 
# # print('Activity Duration:', df_duration/60, 'hours')

# ------------------------------ Travel Time ---------------------------- #

# 0     124
# 60      3
# 30      3
# 45      1

# print('Travel time unique values:', df['Total travel time (minutes):'].unique())
# print(df['Total travel time (minutes):'].value_counts())

df['Total travel time (minutes):'] = (
    df['Total travel time (minutes):']
    .astype(str)
    .str.strip()
    .replace(
        {
        'The Bumgalows': '0',
        }
    )
)

# Convert to float
df['Total travel time (minutes):'] = pd.to_numeric(df['Total travel time (minutes):'], errors='coerce')

# print('Value counts after:', df['Total travel time (minutes):'].value_counts())

# replace nan with '0'
df['Total travel time (minutes):'] = df['Total travel time (minutes):'].fillna(0)

# # Groupby Activity Duration:
travel_time = df['Total travel time (minutes):'].sum()/60
travel_time = round(travel_time) 
# print('Travel Time dtype:', df['Total travel time (minutes):'].dtype)
# print('Total Travel Time:', travel_time)

# ------------------------------- Gender Distribution ---------------------------- #

# Groupby 'Gender:'
df_gender = df['Gender:'].value_counts().reset_index(name='Count')

# Gender Bar Chart
gender_bar=px.bar(
    df_gender,
    x='Gender:',
    y='Count',
    color='Gender:',
    text='Count',
).update_layout(
    height=700, 
    width=1000,
    title=dict(
        text='Sex Distribution Bar Chart',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=0,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Gender",
            font=dict(size=20),  # Font size for the title
        ),
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title='Gender',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        visible=False
        
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.07,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b>Gender</b>: %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Gender Pie Chart
gender_pie=px.pie(
    df,
    names='Gender:'
).update_layout(
    height=700,
    title='Patient Visits by Sex',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    textinfo='value+percent',
    hovertemplate='<b>%{label} Visits</b>: %{value}<extra></extra>'
)

# ------------------------------- Race Graphs ---------------------------- #

# # Groupby Race/Ethnicity:
df_race = df['Race/Ethnicity:'].value_counts().reset_index(name='Count')

# Race Bar Chart
race_bar=px.bar(
    df_race,
    x='Race/Ethnicity:',
    y='Count',
    color='Race/Ethnicity:',
    text='Count',
).update_layout(
    height=700, 
    width=1000,
    title=dict(
        text='Race Distribution Bar Chart',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=-20,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Race/ Ethnicity",
            font=dict(size=20),  # Font size for the title
        ),
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title='Race/ Ethnicity',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        visible=False
        
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.07,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b>Race:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Race Pie Chart
race_pie=px.pie(
    df_race,
    names='Race/Ethnicity:',
    values='Count'
).update_layout(
    height=700, 
    title='Race Distribution Pie Chart',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    textinfo='value+percent',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ------------------------------- Age Distribution ---------------------------- #

# # Fill missing values for 'Birthdate' with random dates within a specified range
def random_date(start, end):
    return start + timedelta(days=np.random.randint(0, (end - start).days))

start_date = datetime(1950, 1, 1) # Example: start date, e.g., 1950-01-01
end_date = datetime(2000, 12, 31)

def random_date(start, end):
    return start + timedelta(days=np.random.randint(0, (end - start).days))

# # Define the date range for random dates
start_date = datetime(1950, 1, 1)
end_date = datetime(2000, 12, 31)

# # Convert 'Individual's Date of Birth:' to datetime, coercing errors to NaT
df['Individual\'s Date of Birth:'] = pd.to_datetime(df['Individual\'s Date of Birth:'], errors='coerce')

# # Fill missing values in 'Individual's Date of Birth:' with random dates
df['Individual\'s Date of Birth:'] = df['Individual\'s Date of Birth:'].apply(
    lambda x: random_date(start_date, end_date) if pd.isna(x) else x
)

# # Calculate 'Client Age' by subtracting the birth year from the current year
df['Client Age'] = pd.to_datetime('today').year - df['Individual\'s Date of Birth:'].dt.year

# # Handle NaT values in 'Client Age' if necessary (e.g., fill with a default value or drop rows)
df['Client Age'] = df['Client Age'].apply(lambda x: "N/A" if x < 0 else x)

# # Define a function to categorize ages into age groups
def categorize_age(age):
    if age == "N/A":
        return "N/A"
    elif 10 <= age <= 19:
        return '10-19'
    elif 20 <= age <= 29:
        return '20-29'
    elif 30 <= age <= 39:
        return '30-39'
    elif 40 <= age <= 49:
        return '40-49'
    elif 50 <= age <= 59:
        return '50-59'
    elif 60 <= age <= 69:
        return '60-69'
    elif 70 <= age <= 79:
        return '70-79'
    else:
        return '80+'

# # Apply the function to create the 'Age_Group' column
df['Age_Group'] = df['Client Age'].apply(categorize_age)

# # Group by 'Age_Group' and count the number of patient visits
df_decades = df.groupby('Age_Group',  observed=True).size().reset_index(name='Patient_Visits')

# # Sort the result by the minimum age in each group
age_order = [
            '10-19',
             '20-29', 
             '30-39', 
             '40-49', 
             '50-59', 
             '60-69', 
             '70-79',
             '80+'
             ]

df_decades['Age_Group'] = pd.Categorical(df_decades['Age_Group'], categories=age_order, ordered=True)
df_decades = df_decades.sort_values('Age_Group')
# print(df_decades.value_counts())

# Age Bar Chart
age_bar=px.bar(
    df_decades,
    x='Age_Group',
    y='Patient_Visits',
    color='Age_Group',
    text='Patient_Visits',
).update_layout(
    height=700, 
    width=1000,
    title=dict(
        text='Client Age Distribution',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=0,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Age Group",
            font=dict(size=20),  # Font size for the title
        ),
    ),
    yaxis=dict(
        title=dict(
            text='Number of Visits',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        visible=False
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b>Age:</b>: %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Pie chart showing values and percentages:

# # Age Pie Chart
age_pie = px.pie(
    df_decades,
    names='Age_Group',
    values='Patient_Visits',
).update_layout(
    height=700, 
    title='Client Age Distribution',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    textinfo='value+percent',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ------------------------------- Insurance Status ------------------------- #

# print("Insurance Unique:", df["Individual's Insurance Status:"].unique().tolist())

insurance_unique = [
    'Unknown', 
    'NONE', 
    'Private Insurance', 
    'MAP 100', 
    'NAPHCARE',
    'MAP Basic', 'Medicare', 
    'MAP',
    'None',
    'Medicaid'
]

df["Individual's Insurance Status:"] = (
    df["Individual's Insurance Status:"]
    .str.strip()
    .replace(   
    {
        'None': 'NONE',
    }
))

df_insurance = df.groupby("Individual's Insurance Status:").size().reset_index(name='Count')
# # print(df["Individual's Insurance Status:"].value_counts())

# Insurance Status Bar Chart
insurance_bar=px.bar(
    df_insurance,
    x="Individual's Insurance Status:",
    y='Count',
    color="Individual's Insurance Status:",
    text='Count',
).update_layout(
    height=700, 
    width=1000,
    title=dict(
        text='Insurance Status Bar Chart',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=-20,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Insurance",
            font=dict(size=20),  # Font size for the title
        ),
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title='Insurance',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        visible=False
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b>Insurance:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Insurance Status Pie Chart
insurance_pie=px.pie(
    df_insurance,
    names="Individual's Insurance Status:",
    values='Count'
).update_layout(
    height=700, 
    title='Insurance Status Pie Chart',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    textinfo='value+percent',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ------------------------------ Location Encountered --------------------------------- #

# Unique Values:
# print("Locations Unique:", df['Location Encountered:'].unique().tolist())

locations_unique = ['GudLife', 
             "Black Men's Health Clinic", 
             'Downtown Austin Community Court', 
             'Cross Creek Hospital', 
             'South Bridge', 
             'phone ', 
             'Home of resident',
             'Community First Village', 
             'Cross Creek hospital', 
             'over phone', 
             'phone', 
             'phone call',
             'over the phone',
             'Hungry Hill/Austin Urban League', 
             'Cross creek hospital', 
             'Vivent Health', 'Clients home',
             'Extended Stay America (Host Hotel) ', 
             'Extended Stay America ', 
             'The Bungalows', 
             'Outreach in the field ', 
             'Integral Care St. John Office ', 
             'Extended Stay America Hotel ', 
             'picked client up from encampment for SSA appointment']

df['Location Encountered:'] = (
    df['Location Encountered:']
    .str.strip()
    .replace(
        {
        'Southbridge': 'SouthBridge',
        'DACC': 'Downtown Austin Community Court',
        'SNHC': 'Sunrise Navigation Homeless Center',
        'HATC': 'Housing Authority of Travis County',
        'CFV': 'Community First Village',
        'BMHC': "Black Men's Health Clinic",
        "The Bumgalows" : "The Bungalows",
        "PHONE CONTACT" : "Phone Call",
        "PHONE" : "Phone Call",
        "phone call" : "Phone Call",
        "phone" : "Phone Call",
        "over phone" : "Phone Call",
        "over the phone" : "Phone Call",
        "Cross Creek hospital" : "Cross Creek Hospital",
        "Cross creek hospital" : "Cross Creek Hospital",
        "Extended Stay America (Host Hotel)" : "Extended Stay America",
        "Extended Stay America Hotel" : "Extended Stay America",
        "last known area was St. John. Connected with Hungry Hill to help me search for client" : "Client Missing",
        }
    )
)


df_location = df['Location Encountered:'].value_counts().reset_index(name='Count')
# # print(df['Location Encountered:'].value_counts())

# unique values
# print("Locations Encountered",df['Location Encountered:'].unique())

# Location Bar Chart
location_bar=px.bar(
    df_location,
    x="Location Encountered:",
    y='Count',
    color="Location Encountered:",
    text='Count',
).update_layout(
    height=900, 
    width=2000,
    title=dict(
        text='Location Encountered Bar Chart',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=-20,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Location",
            font=dict(size=20),  # Font size for the title
        ),
        # showticklabels=True 
        showticklabels=False  # Hide x-tick labels
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title='Location',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        # visible=False
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition=None,
    # textposition='auto',
    hovertemplate='<b>Insurance:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Location Pie Chart
location_pie=px.pie(
    df_location,
    names="Location Encountered:",
    values='Count'
).update_layout(
    height=900,
    width=1800,
    title='Location Encountered Pie Chart',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=50,
    textinfo='value+percent',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ------------------------------- Type of Support Given ---------------------------- #

# # 'How can BMHC support you today?'
df_support = df['Type of support given:'].value_counts().reset_index(name='Count')

support_bar=px.bar(
    df_support,
    x='Type of support given:',
    y='Count',
    color='Type of support given:',
    text='Count',
).update_layout(
    height=700, 
    width=1000,
    title=dict(
        text='Support Provided Distribution',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=0,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Type of Support",
            font=dict(size=20),  # Font size for the title
        ),
        showticklabels=False  # Hide x-tick labels
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        # title='Support',
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        visible=True
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='outside',
    hovertemplate='<b>Support:</b>: %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Support Pie Chart
support_pie = px.pie(
    df_support,
    names='Type of support given:',
    values='Count',
).update_layout(
    title='Support Distribution Pie Chart',
    height=700, 
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=110,
    textinfo='value+percent',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ------------------------ Individuals' Status (New vs. Returning) --------------------- #

# # "Individual's Status:" dataframe:
df_status = df['Individual\'s Status:'].value_counts().reset_index(name='Count')

# Status Bar Chart
status_bar=px.bar(
    df_status,
    x='Individual\'s Status:',
    y='Count',
    color='Individual\'s Status:',
    text='Count',
).update_layout(
    height=700, 
    width=900,
    title=dict(
        text='New vs. Returning Clients',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=0,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Status",
            font=dict(size=20),  # Font size for the title
        ),
        showticklabels=True  # Hide x-tick labels
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        # title='Support',
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        # visible=True
        visible=False
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b>Status:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Status Pie Chart
status_pie=px.pie(
    df_status,
    names="Individual\'s Status:",
    values='Count'  # Specify the values parameter
).update_layout(
    height=700, 
    title='New vs. Returning',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=-90,
    textinfo='value+percent',
    hovertemplate='<b>%{label} Status</b>: %{value}<extra></extra>',
)

# ----------------------- Person Filling Out This Form ------------------------ #

# print("Person Unique", df["Person submitting this form:"].unique().tolist())

person_unique = [
    'Sonya Hosey', 
    'Viviana Varela',
    'Jaqueline Oviedo', 
    'Michael Lambert',
    'Michael Lambert ', 
    'Larry Wallace Jr', 
    'Rishit Yokananth', 
    'Dominique Street', 
    'Dr Larry Wallace Jr',
    'Eric Roberts', 
    'Toya Craney', 
    'Eric roberts', 
    'EricRoberts', 
    'Kimberly Holiday'
]

df['Person submitting this form:'] = (
    df['Person submitting this form:']
    .str.strip()
    .replace({
        'Dominique': 'Dominique Street',
        'Jaqueline Ovieod': 'Jaqueline Oviedo',
        'Eric roberts': 'Eric Roberts',
        'EricRoberts': 'Eric Roberts',
        'Dr Larry Wallace Jr': 'Larry Wallace Jr',
        'Sonya': 'Sonya Hosey',
        })
    )

# # Groupby Person submitting this form:
df_person = df['Person submitting this form:'].value_counts().reset_index(name='Count')
# print('Person Submitting: \n', person_submitting)

# Person Submitting Bar Chart
person_bar=px.bar(
    df_person,
    x='Person submitting this form:',
    y='Count',
    color='Person submitting this form:',
    text='Count',
).update_layout(
    height=700, 
    width=900,
    title=dict(
        text='People Submitting Forms',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=0,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Name",
            font=dict(size=20),  # Font size for the title
        ),
        showticklabels=False  # Hide x-tick labels
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        # title='Support',
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        # visible=False
        visible=True
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='outside',
    hovertemplate='<b>Name:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Person Submitting Pie Chart
person_pie=px.pie(
    df_person,
    names="Person submitting this form:",
    values='Count'  # Specify the values parameter
).update_layout(
    height=700, 
    title='Ratio of People Submitting Forms',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=140,
    textinfo='value+percent',
    hovertemplate='<b>%{label} Status</b>: %{value}<extra></extra>',
)

# ---------------------- Zip 2 --------------------- #

zip_unique =['', 78741, 78723, 78744, 78724, 78754, 78753, 78758, 78660, 78752, 'Unknown ', 78745, 78617, 78702, 78664, 78613, 78653, 78721, 'Unknown', 78704, 78748, 78717, 78640, 'NA', 78757, 78727, 78749, 76537, 78729, 78725, 78759, 78750, 78621, 78728, 78731, 78683]


        
df['ZIP2'] = df['ZIP Code:']
zip2_mode = df['ZIP2'].mode()[0]

df['ZIP2'] = (
    df['ZIP2']
    .astype(str)
    .str.strip()
    .replace({
        'Texas': zip2_mode,
        'Unhoused': zip2_mode,
        'UNHOUSED': zip2_mode,
        'Unknown': zip2_mode,
        'Unknown ': zip2_mode,
        'NA': zip2_mode,
        'nan': zip2_mode,
        '': zip2_mode,
    })
)

df['ZIP2'] = df['ZIP2'].fillna(zip2_mode)
df_z = df['ZIP2'].value_counts().reset_index(name='Count')

# print('ZIP2 Unique:', df_z['ZIP2'].unique().tolist())

zip_fig =px.bar(
    df_z,
    x='Count',
    y='ZIP2',
    color='ZIP2',
    text='Count',
    orientation='h'  # Horizontal bar chart
).update_layout(
    title='Number of Clients by Zip Code',
    xaxis_title='Residents',
    yaxis_title='Zip Code',
    title_x=0.5,
    height=950,
    width=1500,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
        yaxis=dict(
        tickangle=0  # Keep y-axis labels horizontal for readability
    ),
        legend=dict(
        title='ZIP Code',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        xanchor="left",  # Anchor legend to the left
        y=1,  # Position legend at the top
        yanchor="top"  # Anchor legend at the top
    ),
).update_traces(
    textposition='auto',  # Place text labels inside the bars
    textfont=dict(size=30),  # Increase text size in each bar
    # insidetextanchor='middle',  # Center text within the bars
    textangle=0,            # Ensure text labels are horizontal
    hovertemplate='<b>ZIP Code</b>: %{y}<br><b>Count</b>: %{x}<extra></extra>'
)

# -----------------------------------------------------------------------------

# Get the distinct values in column

# distinct_service = df['What service did/did not complete?'].unique()
# print('Distinct:\n', distinct_service)

# =============================== Folium ========================== #

# empty_strings = df[df['ZIP Code:'].str.strip() == ""]
# print("Empty strings: \n", empty_strings.iloc[:, 10:12])

# Filter df to exclued all rows where there is no value for "ZIP Code:"
df = df[df['ZIP Code:'].str.strip() != ""]

mode_value = df['ZIP Code:'].mode()[0]
df['ZIP Code:'] = df['ZIP Code:'].fillna(mode_value)

# print("ZIP value counts:", df['ZIP Code:'].value_counts())
# print("Zip Unique Before:", df['ZIP Code:'].unique().tolist())

# Check for non-numeric values in the 'ZIP Code:' column
# print("ZIP non-numeric values:", df[~df['ZIP Code:'].str.isnumeric()]['ZIP Code:'].unique())

df['ZIP Code:'] = df['ZIP Code:'].astype(str).str.strip()

df['ZIP Code:'] = df['ZIP Code:'].replace({
    'Texas': mode_value,
    'Unhoused': mode_value,
    'Unknown': mode_value,
    'Unknown ': mode_value,
    'NA': mode_value,
    "": mode_value,
    'nan': mode_value  # Replace 'nan' strings
})

df['ZIP Code:'] = df['ZIP Code:'].where(df['ZIP Code:'].str.isdigit(), mode_value)
df['ZIP Code:'] = df['ZIP Code:'].astype(int)

df_zip = df['ZIP Code:'].value_counts().reset_index(name='Residents')
# df_zip['ZIP Code:'] = df_zip['index'].astype(int)
df_zip['Residents'] = df_zip['Residents'].astype(int)
# df_zip.drop('index', axis=1, inplace=True)

# print("Zip Unique After:", df['ZIP Code:'].unique().tolist())

# print(df_zip.head())

# Create a folium map
m = folium.Map([30.2672, -97.7431], zoom_start=10)

# Add different tile sets
folium.TileLayer('OpenStreetMap', attr='© OpenStreetMap contributors').add_to(m)
folium.TileLayer('Stamen Terrain', attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.').add_to(m)
folium.TileLayer('Stamen Toner', attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.').add_to(m)
folium.TileLayer('Stamen Watercolor', attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.').add_to(m)
folium.TileLayer('CartoDB positron', attr='Map tiles by CartoDB, under CC BY 3.0. Data by OpenStreetMap, under ODbL.').add_to(m)
folium.TileLayer('CartoDB dark_matter', attr='Map tiles by CartoDB, under CC BY 3.0. Data by OpenStreetMap, under ODbL.').add_to(m)

# Available map styles
map_styles = {
    'OpenStreetMap': {
        'tiles': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    },
    'Stamen Terrain': {
        'tiles': 'https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg',
        'attribution': 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under ODbL.'
    },
    'Stamen Toner': {
        'tiles': 'https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png',
        'attribution': 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under ODbL.'
    },
    'Stamen Watercolor': {
        'tiles': 'https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg',
        'attribution': 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under ODbL.'
    },
    'CartoDB positron': {
        'tiles': 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    },
    'CartoDB dark_matter': {
        'tiles': 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
        'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    },
    'ESRI Imagery': {
        'tiles': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        'attribution': 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    }
}

# Add tile layers to the map
for style, info in map_styles.items():
    folium.TileLayer(tiles=info['tiles'], attr=info['attribution'], name=style).add_to(m)

# Select a style
# selected_style = 'OpenStreetMap'
# selected_style = 'Stamen Terrain'
# selected_style = 'Stamen Toner'
# selected_style = 'Stamen Watercolor'
selected_style = 'CartoDB positron'
# selected_style = 'CartoDB dark_matter'
# selected_style = 'ESRI Imagery'

# Apply the selected style
if selected_style in map_styles:
    style_info = map_styles[selected_style]
    # print(f"Selected style: {selected_style}")
    folium.TileLayer(
        tiles=style_info['tiles'],
        attr=style_info['attribution'],
        name=selected_style
    ).add_to(m)
else:
    print(f"Selected style '{selected_style}' is not in the map styles dictionary.")
     # Fallback to a default style
    folium.TileLayer('OpenStreetMap').add_to(m)
    
geolocator = Nominatim(user_agent="your_app_name", timeout=10)

# Function to get coordinates from zip code
# def get_coordinates(zip_code):
#     geolocator = Nominatim(user_agent="response_q4_2024.py", timeout=10) # Add a timeout parameter to prevent long waits
#     location = geolocator.geocode({"postalcode": zip_code, "country": "USA"})
#     if location:
#         return location.latitude, location.longitude
#     else:
#         print(f"Could not find coordinates for zip code: {zip_code}")
#         return None, None
    
def get_coordinates(zip_code):
    for _ in range(3):  # Retry up to 3 times
        try:
            location = geolocator.geocode({"postalcode": zip_code, "country": "USA"})
            if location:
                return location.latitude, location.longitude
        except GeocoderTimedOut:
            time.sleep(2)  # Wait before retrying
    return None, None  # Return None if all retries fail

# Apply function to dataframe to get coordinates
df_zip['Latitude'], df_zip['Longitude'] = zip(*df_zip['ZIP Code:'].apply(get_coordinates))

# Filter out rows with NaN coordinates
df_zip = df_zip.dropna(subset=['Latitude', 'Longitude'])
# print(df_zip.head())
# print(df_zip[['Zip Code', 'Latitude', 'Longitude']].head())
# print(df_zip.isnull().sum())

# instantiate a feature group for the incidents in the dataframe
incidents = folium.map.FeatureGroup()

for index, row in df_zip.iterrows():
    lat, lng = row['Latitude'], row['Longitude']

    if pd.notna(lat) and pd.notna(lng):  
        incidents.add_child(# Check if both latitude and longitude are not NaN
        folium.vector_layers.CircleMarker(
            location=[lat, lng],
            radius=row['Residents'] * 1.2,  # Adjust the multiplication factor to scale the circle size as needed,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.4
        ))

# add pop-up text to each marker on the map
latitudes = list(df_zip['Latitude'])
longitudes = list(df_zip['Longitude'])

# labels = list(df_zip[['Zip Code', 'Residents_In_Zip_Code']])
labels = df_zip.apply(lambda row: f"ZIP Code: {row['ZIP Code:']}, Patients: {row['Residents']}", axis=1)

for lat, lng, label in zip(latitudes, longitudes, labels):
    if pd.notna(lat) and pd.notna(lng):
        folium.Marker([lat, lng], popup=label).add_to(m)
 
formatter = "function(num) {return L.Util.formatNum(num, 5);};"
mouse_position = MousePosition(
    position='topright',
    separator=' Long: ',
    empty_string='NaN',
    lng_first=False,
    num_digits=20,
    prefix='Lat:',
    lat_formatter=formatter,
    lng_formatter=formatter,
)

m.add_child(mouse_position)

# add incidents to map
m.add_child(incidents)

map_path = 'zip_code_map.html'
map_file = os.path.join(script_dir, map_path)
m.save(map_file)
map_html = open(map_file, 'r').read()

# # ========================== DataFrame Table ========================== #

# # Organizational Events Table
df_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df[col] for col in df.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

df_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=400,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# ============================== Dash Application ========================== #

app = dash.Dash(__name__)
server= app.server

app.layout = html.Div(
    children=[ 
        html.Div(
            className='divv', 
            children=[ 
            html.H1(
                'Navigation Impact Report', 
                className='title'),
            html.H1(
                'March 2025', 
                className='title2'),
            html.Div(
                className='btn-box', 
                children=[
                    html.A(
                        'Repo',
                        href='https://github.com/CxLos/Nav_Mar_2025',
                        className='btn'),
                ]),
    ]),  

# # Data Table
# html.Div(
#     className='row0',
#     children=[
#         html.Div(
#             className='table',
#             children=[
#                 html.H1(
#                     className='table-title',
#                     children='Data Table'
#                 )
#             ]
#         ),
#         html.Div(
#             className='table2', 
#             children=[
#                 dcc.Graph(
#                     className='data',
#                     figure=df_table
#                 )
#             ]
#         )
#     ]
# ),

# # ROW 1
html.Div(
    className='row1',
    children=[

        html.Div(
            className='graph11',
            children=[
                html.Div(
                    className='high3',
                    children=[f'{current_month} Clients Serviced:']
                ),
                html.Div(
                    className='circle2',
                    children=[
                        html.Div(
                            className='hilite',
                            children=[
                                html.H1(
                                    className='high4',
                                    children=[clients_served]
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className='graph22',
            children=[
                html.Div(
                    className='high1',
                    children=[f'{current_month} Navigation Hours:']
                ),
                html.Div(
                    className='circle1',
                    children=[
                        html.Div(
                            className='hilite',
                            children=[
                                html.H1(
                                    className='high2',
                                    children=[df_duration]
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),
    ]
),

# # ROW 1
html.Div(
    className='row1',
    children=[

        html.Div(
            className='graph11',
            children=[
                html.Div(
                    className='high3',
                    children=[f'{current_month} Travel Hours']
                ),
                html.Div(
                    className='circle2',
                    children=[
                        html.Div(
                            className='hilite',
                            children=[
                                html.H1(
                                    className='high5',
                                    children=[travel_time]
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className='graph22',
            children=[
                html.Div(
                    className='high1',
                    children=['Placeholder']
                ),
                html.Div(
                    className='circle1',
                    children=[
                        html.Div(
                            className='hilite',
                            children=[
                                html.H1(
                                    className='high2',
                                    children=[]
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),
    ]
),

# # ROW 3
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph3',
            children=[
                dcc.Graph(
                    figure=race_bar
                )
            ]
        ),
        html.Div(
            className='graph4',
            children=[
                dcc.Graph(
                    figure=race_pie
                )
            ]
        )
    ]
),

# # ROW 5
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph3',
            children=[
                dcc.Graph(
                    figure=gender_bar
                )
            ]
        ),
        html.Div(
            className='graph4',
            children=[
                #
                dcc.Graph(
                    figure=gender_pie
                )
            ]
        )
    ]
),

# # ROW 5
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph3',
            children=[
                dcc.Graph(
                    figure=age_bar
                )
            ]
        ),
        html.Div(
            className='graph4',
            children=[
                dcc.Graph(
                    figure=age_pie
                )
            ]
        )
    ]
),

# # ROW 3
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph3',
            children=[
                dcc.Graph(
                    figure=insurance_bar
                )
            ]
        ),
        html.Div(
            className='graph4',
            children=[
  
                dcc.Graph(
                    figure=insurance_pie
                )
            ]
        )
    ]
),

# # ROW 4
# html.Div(
#     className='row1',
#     children=[
#         html.Div(
#             className='graph1',
#             children=[
#                 dcc.Graph(
#                     figure=location_bar
#                 )
#             ]
#         ),
#         html.Div(
#             className='graph2',
#             children=[
#                 dcc.Graph(
#                     figure=location_pie
#                 )
#             ]
#         )
#     ]
# ),

html.Div(
    className='row3',
    children=[
        html.Div(
            className='graph33',
            children=[
                dcc.Graph(
                    figure=location_bar
                )
            ]
        ),
    ]
),   

html.Div(
    className='row3',
    children=[
        html.Div(
            className='graph33',
            children=[
                dcc.Graph(
                    figure=location_pie
                )
            ]
        ),
    ]
),   

# # ROW 5
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph3',
            children=[
                dcc.Graph(
                    figure=support_bar
                )
            ]
        ),
        html.Div(
            className='graph4',
            children=[
                #
                dcc.Graph(
                    figure=support_pie
                )
            ]
        )
    ]
),

# # ROW 6
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                dcc.Graph(
                    figure=status_bar

                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=status_pie
                )
            ]
        )
    ]
),

# # ROW 7
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                dcc.Graph(
                    figure=person_bar
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                # 
                dcc.Graph(
                    figure=person_pie
                )
            ]
        )
    ]
),

# ROW 9
html.Div(
    className='row4',
    children=[
        html.Div(
            className='graph5',
            children=[
                dcc.Graph(
                    figure=zip_fig
                )
            ]
        )
    ]
),

# # ROW 8
html.Div(
    className='row3',
    children=[
        html.Div(
            className='graph6',
            children=[
                html.H1(
                    'Number of Visitors by Zip Code', 
                    className='zip'
                ),
                html.Iframe(
                    className='folium',
                    id='folium-map',
                    srcDoc=map_html
                )
            ]
        )
    ]
)
])

print(f"Serving Flask app '{current_file}'! 🚀")

if __name__ == '__main__':
    app.run_server(debug=
                   True)
                #    False)
                
# ----------------------------------------------- Updated Database --------------------------------------

# updated_path = f'data/Navigation_{current_month}_{report_year}.xlsx'
# data_path = os.path.join(script_dir, updated_path)
# df.to_excel(data_path, index=False)
# print(f"DataFrame saved to {data_path}")

# updated_path1 = 'data/service_tracker_q4_2024_cleaned.csv'
# data_path1 = os.path.join(script_dir, updated_path1)
# df.to_csv(data_path1, index=False)
# print(f"DataFrame saved to {data_path1}")

# -------------------------------------------- KILL PORT ---------------------------------------------------

# netstat -ano | findstr :8050
# taskkill /PID 24772 /F
# npx kill-port 8050


# ---------------------------------------------- Host Application -------------------------------------------

# 1. pip freeze > requirements.txt
# 2. add this to procfile: 'web: gunicorn impact_11_2024:server'
# 3. heroku login
# 4. heroku create
# 5. git push heroku main

# Create venv 
# virtualenv venv 
# source venv/bin/activate # uses the virtualenv

# Update PIP Setup Tools:
# pip install --upgrade pip setuptools

# Install all dependencies in the requirements file:
# pip install -r requirements.txt

# Check dependency tree:
# pipdeptree
# pip show package-name

# Remove
# pypiwin32
# pywin32
# jupytercore

# ----------------------------------------------------

# Name must start with a letter, end with a letter or digit and can only contain lowercase letters, digits, and dashes.

# Heroku Setup:
# heroku login
# heroku create nav-jan-2025
# heroku git:remote -a nav-jan-2025
# git remote set-url heroku git@heroku.com:nav-jan-2025.git
# git push heroku main

# Clear Heroku Cache:
# heroku plugins:install heroku-repo
# heroku repo:purge_cache -a nav-nov-2024

# Set buildpack for heroku
# heroku buildpacks:set heroku/python

# Heatmap Colorscale colors -----------------------------------------------------------------------------

#   ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
            #  'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
            #  'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
            #  'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
            #  'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
            #  'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
            #  'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
            #  'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
            #  'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
            #  'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
            #  'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
            #  'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
            #  'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
            #  'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
            #  'ylorrd'].

# rm -rf ~$bmhc_data_2024_cleaned.xlsx
# rm -rf ~$bmhc_data_2024.xlsx
# rm -rf ~$bmhc_q4_2024_cleaned2.xlsx