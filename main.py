# path/main.py

import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL

# Function to load data from the database
@st.cache_data
def load_data():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    clients = pd.read_sql_table('client', engine)
    forms = pd.read_sql_table('form', engine)
    questions = pd.read_sql_table('question', engine)
    responses = pd.read_sql_table('response', engine)
    client_form_responses = pd.read_sql_table('client_form_response', engine)
    protocols = pd.read_sql_table('protocol', engine)

    session.close()
    return clients, forms, questions, responses, client_form_responses, protocols

# Functions for each page
def overview_page(clients, forms, questions, responses, client_form_responses, protocols):
    st.title("Overview")
    st.write("## Summary Statistics")

    # Summary Statistics Table
    num_clients = len(clients)
    num_questions_filled = len(client_form_responses)
    forms_filled = client_form_responses['form_id'].nunique()

    summary_data = {
        "Total Clients": [num_clients],
        "Questions Filled": [num_questions_filled],
        "Forms Filled": [forms_filled]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)

    avg_scores = client_form_responses.groupby(['form_id', 'time_point']).apply(
        lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).mean()
    ).reset_index(name='average_score')
    
    avg_scores = avg_scores.merge(forms, left_on='form_id', right_on='id')

    fig = px.line(avg_scores, x='time_point', y='average_score', color='name',
                  labels={'time_point': 'Time Point', 'average_score': 'Average Score', 'name': 'Form'})
    st.plotly_chart(fig)

def form_response_distribution(forms, client_form_responses, responses, questions):
    st.title("Form Response Distribution")

    selected_form = st.selectbox("Select Form", forms['name'])
    form_id = forms[forms['name'] == selected_form]['id'].values[0]
    
    form_responses = client_form_responses[client_form_responses['form_id'] == form_id]
    response_ids = form_responses['response_id'].map(responses.set_index('id')['text'].astype(int)).to_frame()
    response_ids.columns = ['Response Score']
    
    fig = px.histogram(response_ids, x='Response Score', nbins=10, labels={'Response Score': 'Response Score'})
    st.plotly_chart(fig)

def client_progress_over_time(clients, client_form_responses, responses, questions):
    st.title("Client Progress Over Time")
    
    selected_client = st.selectbox("Select Client", clients['name'])
    client_id = clients[clients['name'] == selected_client]['id'].values[0]
    
    client_data = client_form_responses[client_form_responses['client_id'] == client_id]
    client_data = client_data.merge(responses, left_on='response_id', right_on='id')
    
    fig = px.line(client_data, x='time_point', y='text', color='form_id', 
                  labels={'time_point': 'Time Point', 'text': 'Response Score', 'form_id': 'Form'})
    st.plotly_chart(fig)

def protocol_effectiveness(protocols, client_form_responses, responses, forms):
    st.title("Protocol Effectiveness")

    avg_scores = client_form_responses.groupby(['protocol_id', 'time_point']).apply(
        lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).mean()
    ).reset_index(name='average_score')
    
    avg_scores = avg_scores.merge(protocols, left_on='protocol_id', right_on='id')

    fig = px.bar(avg_scores, x='time_point', y='average_score', color='name',
                 labels={'time_point': 'Time Point', 'average_score': 'Average Score', 'name': 'Protocol'})
    st.plotly_chart(fig)

def data_integration():
    st.title("Data Integration")
    st.write("API Integration status and real-time data sync status will be shown here.")

# Sidebar for navigation
st.sidebar.title("Naitur Dashboard Demo")
page = st.sidebar.radio("Go to", ["Overview", "Form Response Distribution", "Client Progress Over Time", "Protocol Effectiveness", "Data Integration"])

# Load data
clients, forms, questions, responses, client_form_responses, protocols = load_data()

# Render selected page
if page == "Overview":
    overview_page(clients, forms, questions, responses, client_form_responses, protocols)
elif page == "Form Response Distribution":
    form_response_distribution(forms, client_form_responses, responses, questions)
elif page == "Client Progress Over Time":
    client_progress_over_time(clients, client_form_responses, responses, questions)
elif page == "Protocol Effectiveness":
    protocol_effectiveness(protocols, client_form_responses, responses, forms)
elif page == "Data Integration":
    data_integration()
