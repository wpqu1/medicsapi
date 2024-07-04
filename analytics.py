import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import io, base64
import sqlalchemy
from sqlalchemy import create_engine

# Analytics module for MEDICS app

connection_string = (
    "mssql+pyodbc://pupmedics_admin@pupmedics4:N0_Cap$t0ners@"
    "pupmedics4.database.windows.net:1433/"
    "medics4?driver=ODBC+Driver+18+for+SQL+Server"
)

engine = create_engine(connection_string)

def frequencyOfAppointments():  # Question 1: Frequency of Appointments per User
    
    df = pd.read_sql_table('AppointmentForms', engine)

    # Group the table by UserID and count the number of appointments for each user
    user_appointments = df.groupby('UserID')['FormID'].count()

    # Calculate the average number of appointments per user
    avg_appointments = user_appointments.mean()

    # Plot a histogram of the number of appointments per user
    plt.hist(user_appointments, bins=10, color='maroon')
    plt.xlabel('Number of appointments')
    plt.ylabel('Number of users')
    plt.title('Histogram of the number of appointments per user')
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    frequency_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    
    return frequency_url

def mostRequestedMedicine(): # Question 2: Most Requested Medicine
    
    df = pd.read_sql_table('MedicationForms', engine)

    # Group the table by BrandName and count the number of requests for each medicine
    medicine_requests = df.groupby('BrandName')['FormID'].count()

    # Sort the results in descending order and select the top 10 most requested medicines
    top_medicines = medicine_requests.sort_values(ascending=False).head(10)

    # Plot a pie chart of the percentage of requests for each medicine
    plt.pie(top_medicines, labels=top_medicines.index, autopct='%1.1f%%')
    plt.title('Pie chart of the percentage of requests for each medicine')
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    mostRequested_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    
    
    return mostRequested_url

def correlationAnalysis(): # Question 3: Correlation between Appointment Frequency and Medication Count (Bulk)

    # Get UserNumber from JSON request
    #user_number = '2020Student'
    #request.json.get('UserNumber')
    
    # Read the AppointmentForms and MedicationForms tables from the database
    df_app = pd.read_sql_table('AppointmentForms', engine)
    df_med = pd.read_sql_table('MedicationForms', engine)

    # Merge the two tables on the UserNumber column
    df_merged = pd.merge(df_app, df_med, left_on='UserID', right_on='UserNumber')

    # Group the new table by BrandName and calculate the average number of visits for each medicine
    medicine_visits = df_merged.groupby('BrandName')['FormID_x'].count() / df_merged.groupby('BrandName')['UserNumber'].nunique()

    # Calculate the correlation coefficient between the number of visits and the type of medicine
    medicine_type = pd.Series(medicine_visits.index)
    correlation = medicine_visits.corr(medicine_type)

    # Plot a scatter plot of the number of visits versus the type of medicine
    plt.scatter(medicine_visits.index, medicine_visits, color='maroon')
    plt.xlabel('Type of medicine')
    plt.ylabel('Average number of visits')
    plt.title('Frequency of visits vs. Drug Prescribed')
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    correlation_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    return correlation_url
    
def Barchart(user_number):
    
    # Read the AppointmentForms and MedicationForms tables from the database
    df_app = pd.read_sql_table('AppointmentForms', engine)
    df_med = pd.read_sql_table('MedicationForms', engine)
    
    # Filter the MedicationForms for the specific StudentNumber
    df_med_user = df_med[df_med['UserNumber'] == user_number]
    
    # Count the number of medication requests per brand for the user
    med_counts = df_med_user['BrandName'].value_counts()
    
    # Create a bar plot for the medication request counts
    med_counts.plot(kind='bar', color='maroon')
    
    plt.xlabel('Brand Name of Medicine')
    plt.ylabel('Number of Requests')
    plt.title(f'Number of Medication Requests for User {user_number}')
    plt.xticks(rotation=45, ha='right')  # Rotate brand names for better readability
    plt.tight_layout()  # Adjust layout to fit labels
    
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    barchart_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    
    return barchart_url
