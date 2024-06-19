# path/streamlit_app.py

import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
import io

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

# Initialize session state for wide mode
if "wide_mode" not in st.session_state:
    st.session_state.wide_mode = False

# Set page configuration based on session state
layout = 'wide' if st.session_state.wide_mode else 'centered'
st.set_page_config(layout=layout)

# Functions for each page
# Function to toggle wide mode
def toggle_wide_mode():
    st.session_state.wide_mode = not st.session_state.wide_mode
    st.experimental_rerun()

# Overview page function
def overview_page(clients, forms, questions, responses, client_form_responses, protocols):
    st.title("Overview")
    st.write("## Summary Statistics")

    # Summary Statistics Table
    num_clients = len(clients)
    num_questions_filled = len(client_form_responses)
    total_forms = len(forms)
    protocols_count = len(protocols)

    summary_data = {
        "Total Clients": [num_clients],
        "Questions Filled": [num_questions_filled],
        "Total Forms": [total_forms],
        "Total Protocols": [protocols_count]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)

    # Variance bars and counts checkboxes
    show_variance_bars = st.checkbox("Show Variance Bars", value=False, 
                                     help="Toggle to display variance bars on the graph. Variance bars indicate the spread of responses around the mean, calculated as the standard deviation.")
    show_counts = st.checkbox("Show Response Counts (n)", value=False, 
                              help="Toggle to display the number of responses (n) at each time point on the graph.")
    show_percentages = st.checkbox("Show Percentages at Each Time Point", value=False, 
                                   help="Toggle to display the average percentage score at each time point on the graph.")

    if st.session_state.wide_mode:
        col1, col2 = st.columns(2)
    else:
        col1 = col2 = st.container()  # Create a container to use the same logic for wide mode and centered mode

    with col1:
        st.write("## Form Responses Over Time")
        st.info("This section provides an overview of average scores for selected forms over different time points. "
                "You can filter the forms displayed using the dropdown menu. Use the checkboxes to toggle the display of variance bars, "
                "number of responses (n), and percentage scores at each time point.")

        # Calculating average scores and counts
        avg_scores = client_form_responses.groupby(['form_id', 'time_point']).apply(
            lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).mean() * 100 / 4
        ).reset_index(name='average_score')
        
        counts = client_form_responses.groupby(['form_id', 'time_point']).size().reset_index(name='count')
        scores_with_counts = avg_scores.merge(counts, on=['form_id', 'time_point'])
        scores_with_counts = scores_with_counts.merge(forms, left_on='form_id', right_on='id')

        # Calculating standard deviation for variance bars
        std_devs = client_form_responses.groupby(['form_id', 'time_point']).apply(
            lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).std() * 100 / 4
        ).reset_index(name='std_dev')
        scores_with_counts = scores_with_counts.merge(std_devs, on=['form_id', 'time_point'])

        # Sorting time points
        time_points_order = ["Baseline", "1-Month", "3-Months", "6-Months", "1-Year"]
        scores_with_counts['time_point'] = pd.Categorical(scores_with_counts['time_point'], categories=time_points_order, ordered=True)
        scores_with_counts = scores_with_counts.sort_values('time_point')

        # Form checkboxes
        form_names = scores_with_counts['name'].unique()
        selected_forms = st.multiselect("Select Forms to Display", form_names, default=form_names,
                                        help="Select which forms' data you want to visualize.")

        # Filter data based on selected forms
        filtered_data = scores_with_counts[scores_with_counts['name'].isin(selected_forms)]

        # Plotting with variance bars
        fig = px.line(filtered_data, x='time_point', y='average_score', color='name',
                      labels={'time_point': 'Time Point', 'average_score': 'Average Score (%)', 'name': 'Form'})
        
        # Adding variance bars, counts, and percentages
        for form_name in selected_forms:
            form_data = filtered_data[filtered_data['name'] == form_name]
            if show_variance_bars:
                fig.add_scatter(x=form_data['time_point'], y=form_data['average_score'],
                                error_y=dict(type='data', array=form_data['std_dev']),
                                mode='markers', name=f"{form_name} (Variance)")
            if show_counts:
                for idx, row in form_data.iterrows():
                    fig.add_annotation(x=row['time_point'], y=row['average_score'],
                                       text=f"N={row['count']}", showarrow=False, yshift=10)
            if show_percentages:
                for idx, row in form_data.iterrows():
                    fig.add_annotation(x=row['time_point'], y=row['average_score'],
                                       text=f"{row['average_score']:.2f}%", showarrow=False, yshift=-10)

        st.plotly_chart(fig)

    with col2:
        st.write("## Protocol Responses Over Time")
        st.info("This section provides an overview of average scores for selected protocols over different time points. "
                "You can filter the protocols displayed using the dropdown menu. Use the checkboxes to toggle the display of variance bars, "
                "number of responses (n), and percentage scores at each time point.")

        # Calculating average scores and counts per protocol
        avg_scores_protocols = client_form_responses.groupby(['protocol_id', 'time_point']).apply(
            lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).mean() * 100 / 4
        ).reset_index(name='average_score')
        
        counts_protocols = client_form_responses.groupby(['protocol_id', 'time_point']).size().reset_index(name='count')
        scores_with_counts_protocols = avg_scores_protocols.merge(counts_protocols, on=['protocol_id', 'time_point'])
        scores_with_counts_protocols = scores_with_counts_protocols.merge(protocols, left_on='protocol_id', right_on='id')

        # Calculating standard deviation for variance bars per protocol
        std_devs_protocols = client_form_responses.groupby(['protocol_id', 'time_point']).apply(
            lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).std() * 100 / 4
        ).reset_index(name='std_dev')
        scores_with_counts_protocols = scores_with_counts_protocols.merge(std_devs_protocols, on=['protocol_id', 'time_point'])

        scores_with_counts_protocols['time_point'] = pd.Categorical(scores_with_counts_protocols['time_point'], categories=time_points_order, ordered=True)
        scores_with_counts_protocols = scores_with_counts_protocols.sort_values('time_point')

        protocol_names = scores_with_counts_protocols['name'].unique()
        selected_protocols = st.multiselect("Select Protocols to Display", protocol_names, default=protocol_names,
                                            help="Select which protocols' data you want to visualize.")

        filtered_protocol_data = scores_with_counts_protocols[scores_with_counts_protocols['name'].isin(selected_protocols)]

        fig_protocols = px.line(filtered_protocol_data, x='time_point', y='average_score', color='name',
                                labels={'time_point': 'Time Point', 'average_score': 'Average Score (%)', 'name': 'Protocol'})
        
        for protocol_name in selected_protocols:
            protocol_data = filtered_protocol_data[filtered_protocol_data['name'] == protocol_name]
            if show_variance_bars:
                fig_protocols.add_scatter(x=protocol_data['time_point'], y=protocol_data['average_score'],
                                          error_y=dict(type='data', array=protocol_data['std_dev']),
                                          mode='markers', name=f"{protocol_name} (Variance)")
            if show_counts:
                for idx, row in protocol_data.iterrows():
                    fig_protocols.add_annotation(x=row['time_point'], y=row['average_score'],
                                                 text=f"N={row['count']}", showarrow=False, yshift=10)
            if show_percentages:
                for idx, row in protocol_data.iterrows():
                    fig_protocols.add_annotation(x=row['time_point'], y=row['average_score'],
                                                 text=f"{row['average_score']:.2f}%", showarrow=False, yshift=-10)

        st.plotly_chart(fig_protocols)

def form_response_distribution(forms, client_form_responses, responses, questions):
    st.title("Form Response Distribution")

    st.info("This section allows you to explore the distribution of responses for different forms. "
            "Select a form from the dropdown menu to see how responses are distributed.")

    # Form selection dropdown
    selected_form = st.selectbox("Select Form", forms['name'], help="Select a form to see the distribution of responses.")
    form_id = forms[forms['name'] == selected_form]['id'].values[0]

    # Filter responses for the selected form
    form_responses = client_form_responses[client_form_responses['form_id'] == form_id]
    response_ids = form_responses['response_id'].map(responses.set_index('id')['text'].astype(int)).to_frame()
    response_ids.columns = ['Response Score']

    # Checkboxes for additional visualizations and statistics
    show_histogram = st.checkbox("Show Histogram", value=True, help="Display the histogram of response scores.")
    show_boxplot = st.checkbox("Show Box Plot", value=False, help="Display the box plot of response scores.")
    show_bar_chart = st.checkbox("Show Bar Chart", value=False, help="Display the bar chart of response counts.")
    show_statistics = st.checkbox("Show Statistics", value=False, help="Display mean, median, and mode of the responses.")

    # Layout using columns
    col1, col2 = st.columns(2)

    if show_histogram:
        with col1:
            st.write("### Histogram of Response Scores")
            fig_histogram = px.histogram(response_ids, x='Response Score', nbins=10, labels={'Response Score': 'Response Score'})
            st.plotly_chart(fig_histogram)

    if show_boxplot:
        with col2:
            st.write("### Box Plot of Response Scores")
            fig_boxplot = px.box(response_ids, y='Response Score', labels={'Response Score': 'Response Score'})
            st.plotly_chart(fig_boxplot)

    if show_bar_chart:
        with col1:
            st.write("### Bar Chart of Response Counts")
            response_counts = response_ids['Response Score'].value_counts().reset_index()
            response_counts.columns = ['Response Score', 'Count']
            fig_bar_chart = px.bar(response_counts, x='Response Score', y='Count', labels={'Response Score': 'Response Score', 'Count': 'Count'})
            st.plotly_chart(fig_bar_chart)

    if show_statistics:
        with col2:
            st.write("### Response Statistics")
            mean_score = response_ids['Response Score'].mean()
            median_score = response_ids['Response Score'].median()
            mode_score = response_ids['Response Score'].mode().values[0]
            st.write(f"**Mean:** {mean_score:.2f}")
            st.write(f"**Median:** {median_score:.2f}")
            st.write(f"**Mode:** {mode_score:.2f}")

def client_progress_over_time(clients, client_form_responses, responses, questions):
    st.title("Client Progress Over Time")
    st.info("This section allows facilitators to view detailed progress data for individual clients over different time points. "
            "Select a client from the dropdown menu to visualize their data.")

    # Client selection
    selected_client = st.selectbox("Select Client", clients['name'], help="Select a client to view their progress data.")
    client_id = clients[clients['name'] == selected_client]['id'].values[0]

    # Display client information
    client_info = clients[clients['id'] == client_id]
    st.subheader("Client Information")
    st.write(f"**Name:** {client_info['name'].values[0]}")
    st.write(f"**Email:** {client_info['email'].values[0]}")

    st.write("---")

    # Tabs for different views
    tabs = st.tabs(["Protocols Over Time", "Forms Over Time", "Response Distribution", "Statistics", "Export Report"])

    with tabs[0]:
        st.subheader("Protocols Over Time")
        st.write("### Filter by Protocol")
        protocol_names = client_form_responses.merge(protocols, left_on='protocol_id', right_on='id')['name'].unique()
        selected_protocols = st.multiselect("Select Protocols to Display", protocol_names, default=protocol_names,
                                            help="Select which protocols' data you want to visualize for this client.")
        
        # Filter data based on selected protocols
        client_data = client_form_responses[(client_form_responses['client_id'] == client_id) & 
                                            (client_form_responses['protocol_id'].isin(
                                                protocols[protocols['name'].isin(selected_protocols)]['id'].values))]
        client_data = client_data.merge(responses, left_on='response_id', right_on='id')

        # Variance bars and counts checkboxes for protocols
        show_variance_bars_protocols = st.checkbox("Show Variance Bars (Protocols)", value=False, 
                                                   help="Toggle to display variance bars on the protocol graph.")
        show_counts_protocols = st.checkbox("Show Response Counts (n) (Protocols)", value=False, 
                                            help="Toggle to display the number of responses (n) at each time point on the protocol graph.")
        show_percentages_protocols = st.checkbox("Show Percentages at Each Time Point (Protocols)", value=False, 
                                                 help="Toggle to display the average percentage score at each time point on the protocol graph.")

        # Calculating average scores and counts per form
        avg_scores = client_data.groupby(['form_id', 'time_point']).apply(
            lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).mean() * 100 / 4
        ).reset_index()
        avg_scores.columns = ['form_id', 'time_point', 'average_score']
        
        counts = client_data.groupby(['form_id', 'time_point']).size().reset_index()
        counts.columns = ['form_id', 'time_point', 'count']
        scores_with_counts = avg_scores.merge(counts, on=['form_id', 'time_point'])
        scores_with_counts = scores_with_counts.merge(forms, left_on='form_id', right_on='id')

        # Calculating standard deviation for variance bars
        std_devs = client_data.groupby(['form_id', 'time_point']).apply(
            lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).std() * 100 / 4
        ).reset_index()
        std_devs.columns = ['form_id', 'time_point', 'std_dev']
        scores_with_counts = scores_with_counts.merge(std_devs, on=['form_id', 'time_point'])

        # Sorting time points
        time_points_order = ["Baseline", "1-Month", "3-Months", "6-Months", "1-Year"]
        scores_with_counts['time_point'] = pd.Categorical(scores_with_counts['time_point'], categories=time_points_order, ordered=True)
        scores_with_counts = scores_with_counts.sort_values('time_point')

        # Plotting line chart with variance bars (Per Protocol)
        fig_protocols = px.line(scores_with_counts, x='time_point', y='average_score', color='name',
                                labels={'time_point': 'Time Point', 'average_score': 'Average Score (%)', 'name': 'Form'})
        
        for form_name in scores_with_counts['name'].unique():
            form_data = scores_with_counts[scores_with_counts['name'] == form_name]
            if show_variance_bars_protocols:
                fig_protocols.add_scatter(x=form_data['time_point'], y=form_data['average_score'],
                                          error_y=dict(type='data', array=form_data['std_dev']),
                                          mode='markers', name=f"{form_name} (Variance)")
            if show_counts_protocols:
                for idx, row in form_data.iterrows():
                    fig_protocols.add_annotation(x=row['time_point'], y=row['average_score'],
                                                 text=f"N={row['count']}", showarrow=False, yshift=10)
            if show_percentages_protocols:
                for idx, row in form_data.iterrows():
                    fig_protocols.add_annotation(x=row['time_point'], y=row['average_score'],
                                                 text=f"{row['average_score']:.2f}%", showarrow=False, yshift=-10)

        st.plotly_chart(fig_protocols, use_container_width=True)

    with tabs[1]:
        st.subheader("Forms Over Time")
        st.write("### Filter by Form")
        form_names = client_form_responses.merge(forms, left_on='form_id', right_on='id')['name'].unique()
        selected_forms = st.multiselect("Select Forms to Display", form_names, default=form_names,
                                        help="Select which forms' data you want to visualize for this client.")

        # Filter data based on selected forms
        client_data_forms = client_form_responses[(client_form_responses['client_id'] == client_id) & 
                                                  (client_form_responses['form_id'].isin(
                                                      forms[forms['name'].isin(selected_forms)]['id'].values))]
        client_data_forms = client_data_forms.merge(responses, left_on='response_id', right_on='id')

        # Variance bars and counts checkboxes for forms
        show_variance_bars_forms = st.checkbox("Show Variance Bars (Forms)", value=False, 
                                               help="Toggle to display variance bars on the form graph.")
        show_counts_forms = st.checkbox("Show Response Counts (n) (Forms)", value=False, 
                                        help="Toggle to display the number of responses (n) at each time point on the form graph.")
        show_percentages_forms = st.checkbox("Show Percentages at Each Time Point (Forms)", value=False, 
                                             help="Toggle to display the average percentage score at each time point on the form graph.")

        # Calculating average scores and counts per form
        avg_scores_forms = client_data_forms.groupby(['form_id', 'time_point']).apply(
            lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).mean() * 100 / 4
        ).reset_index()
        avg_scores_forms.columns = ['form_id', 'time_point', 'average_score']
        
        counts_forms = client_data_forms.groupby(['form_id', 'time_point']).size().reset_index()
        counts_forms.columns = ['form_id', 'time_point', 'count']
        scores_with_counts_forms = avg_scores_forms.merge(counts_forms, on=['form_id', 'time_point'])
        scores_with_counts_forms = scores_with_counts_forms.merge(forms, left_on='form_id', right_on='id')

        # Calculating standard deviation for variance bars
        std_devs_forms = client_data_forms.groupby(['form_id', 'time_point']).apply(
            lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).std() * 100 / 4
        ).reset_index()
        std_devs_forms.columns = ['form_id', 'time_point', 'std_dev']
        scores_with_counts_forms = scores_with_counts_forms.merge(std_devs_forms, on=['form_id', 'time_point'])

        # Sorting time points
        scores_with_counts_forms['time_point'] = pd.Categorical(scores_with_counts_forms['time_point'], categories=time_points_order, ordered=True)
        scores_with_counts_forms = scores_with_counts_forms.sort_values('time_point')

        # Plotting line chart with variance bars (Per Form)
        fig_forms = px.line(scores_with_counts_forms, x='time_point', y='average_score', color='name',
                            labels={'time_point': 'Time Point', 'average_score': 'Average Score (%)', 'name': 'Form'})
        
        for form_name in scores_with_counts_forms['name'].unique():
            form_data = scores_with_counts_forms[scores_with_counts_forms['name'] == form_name]
            if show_variance_bars_forms:
                fig_forms.add_scatter(x=form_data['time_point'], y=form_data['average_score'],
                                      error_y=dict(type='data', array=form_data['std_dev']),
                                      mode='markers', name=f"{form_name} (Variance)")
            if show_counts_forms:
                for idx, row in form_data.iterrows():
                    fig_forms.add_annotation(x=row['time_point'], y=row['average_score'],
                                             text=f"N={row['count']}", showarrow=False, yshift=10)
            if show_percentages_forms:
                for idx, row in form_data.iterrows():
                    fig_forms.add_annotation(x=row['time_point'], y=row['average_score'],
                                             text=f"{row['average_score']:.2f}%", showarrow=False, yshift=-10)

        st.plotly_chart(fig_forms, use_container_width=True)

    with tabs[2]:
        st.subheader("Response Distribution")
        st.write("### Histogram of Response Scores")
        response_ids = client_data['response_id'].map(responses.set_index('id')['text'].astype(int)).to_frame()
        response_ids.columns = ['Response Score']
        fig_histogram = px.histogram(response_ids, x='Response Score', nbins=10, labels={'Response Score': 'Response Score'})
        st.plotly_chart(fig_histogram, use_container_width=True)

        st.write("### Box Plot of Response Scores")
        fig_boxplot = px.box(response_ids, y='Response Score', labels={'Response Score': 'Response Score'})
        st.plotly_chart(fig_boxplot, use_container_width=True)

    with tabs[3]:
        st.subheader("Statistics")
        st.write("### Response Statistics")
        mean_score = response_ids['Response Score'].mean()
        median_score = response_ids['Response Score'].median()
        mode_score = response_ids['Response Score'].mode().values[0]
        st.write(f"**Mean:** {mean_score:.2f}")
        st.write(f"**Median:** {median_score:.2f}")
        st.write(f"**Mode:** {mode_score:.2f}")

    with tabs[4]:
        st.subheader("Export Report")
        st.write("### Export Client Report")
        if st.button("Export Report as PDF", help="Export the client's data and visualizations as a PDF report."):
            st.write("Feature not implemented yet.")

# Data export page function
# path/streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
import io


# Data export page function
def data_export(clients, forms, questions, responses, client_form_responses, protocols):
    st.title("Data Export and Report Generation")
    st.info("This section allows facilitators to export client data in .csv format and generate reports in PDF format.")

    # Create tabs
    tab1, tab2 = st.tabs(["Export Data to CSV", "Generate Report"])

    with tab1:
        st.subheader("Export Data to CSV")

        # Client selection
        selected_client = st.selectbox("Select Client", clients['name'], help="Select a client to view and export their data.")
        client_id = clients[clients['name'] == selected_client]['id'].values[0]

        # Filter client data
        client_data = client_form_responses[client_form_responses['client_id'] == client_id]

        # Merge necessary tables
        client_data = client_data.merge(responses, left_on='response_id', right_on='id', suffixes=('', '_response'))
        client_data = client_data.merge(questions, left_on='question_id', right_on='id', suffixes=('', '_question'))
        client_data = client_data.merge(forms, left_on='form_id', right_on='id', suffixes=('', '_form'))
        client_data = client_data.merge(protocols, left_on='protocol_id', right_on='id', suffixes=('', '_protocol'))

        # Rename columns for readability
        client_data.rename(columns={
            'name': 'Client Name', 
            'email': 'Email', 
            'name_form': 'Form Name', 
            'name_protocol': 'Protocol Name', 
            'text_question': 'Question Text', 
            'text': 'Response Text', 
            'time_point': 'Time Point'
        }, inplace=True)

        # Column selection for CSV export
        available_columns = client_data.columns.tolist()
        default_columns = ['Client Name', 'Email', 'Form Name', 'Protocol Name', 'Question Text', 'Response Text', 'Time Point']
        default_columns = [col for col in default_columns if col in available_columns]

        selected_columns = st.multiselect("Select Columns to Export", available_columns, default=default_columns)

        # Filter selected columns
        client_data_csv = client_data[selected_columns]

        # Export data as CSV
        st.download_button(
            label="Download Client Data as CSV",
            data=client_data_csv.to_csv(index=False),
            file_name=f"{selected_client}_data.csv",
            mime="text/csv"
        )

    with tab2:
        st.subheader("Generate Report")

        # Report options
        report_type = st.selectbox("Select Report Type", ["Protocol Efficacy", "Client Report"])
        
        if report_type == "Protocol Efficacy":
            st.info("Generate a report showing the efficacy of selected protocols.")
            selected_protocols = st.multiselect("Select Protocols", protocols['name'], default=protocols['name'].tolist())
            selected_protocol_ids = protocols[protocols['name'].isin(selected_protocols)]['id'].tolist()

            # Filter data for selected protocols
            protocol_data = client_form_responses[client_form_responses['protocol_id'].isin(selected_protocol_ids)]
            protocol_data = protocol_data.merge(responses, left_on='response_id', right_on='id', suffixes=('', '_response'))
            protocol_data = protocol_data.merge(questions, left_on='question_id', right_on='id', suffixes=('', '_question'))
            protocol_data = protocol_data.merge(forms, left_on='form_id', right_on='id', suffixes=('', '_form'))
            protocol_data = protocol_data.merge(protocols, left_on='protocol_id', right_on='id', suffixes=('', '_protocol'))

            # Plotting protocol efficacy
            avg_scores_protocols = protocol_data.groupby(['protocol_id', 'time_point']).apply(
                lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).mean() * 100 / 4
            ).reset_index(name='average_score')
            avg_scores_protocols = avg_scores_protocols.merge(protocols, left_on='protocol_id', right_on='id')

            fig_protocols = px.line(avg_scores_protocols, x='time_point', y='average_score', color='name',
                                    labels={'time_point': 'Time Point', 'average_score': 'Average Score (%)', 'name': 'Protocol'})
            st.plotly_chart(fig_protocols)

            if st.button("Generate PDF Report"):
                st.write("Feature not implemented yet.")

        elif report_type == "Client Report":
            st.info("Generate a detailed report for the selected client.")
            
            # Filter client data
            client_data = client_form_responses[client_form_responses['client_id'] == client_id]
            client_data = client_data.merge(responses, left_on='response_id', right_on='id', suffixes=('', '_response'))
            client_data = client_data.merge(questions, left_on='question_id', right_on='id', suffixes=('', '_question'))
            client_data = client_data.merge(forms, left_on='form_id', right_on='id', suffixes=('', '_form'))
            client_data = client_data.merge(protocols, left_on='protocol_id', right_on='id', suffixes=('', '_protocol'))

            # Plotting client data
            avg_scores_forms = client_data.groupby(['form_id', 'time_point']).apply(
                lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).mean() * 100 / 4
            ).reset_index(name='average_score')
            avg_scores_forms = avg_scores_forms.merge(forms, left_on='form_id', right_on='id')

            fig_forms = px.line(avg_scores_forms, x='time_point', y='average_score', color='name',
                                labels={'time_point': 'Time Point', 'average_score': 'Average Score (%)', 'name': 'Form'})
            st.plotly_chart(fig_forms)

            avg_scores_protocols = client_data.groupby(['protocol_id', 'time_point']).apply(
                lambda x: x['response_id'].map(responses.set_index('id')['text'].astype(int)).mean() * 100 / 4
            ).reset_index(name='average_score')
            avg_scores_protocols = avg_scores_protocols.merge(protocols, left_on='protocol_id', right_on='id')

            fig_protocols = px.line(avg_scores_protocols, x='time_point', y='average_score', color='name',
                                    labels={'time_point': 'Time Point', 'average_score': 'Average Score (%)', 'name': 'Protocol'})
            st.plotly_chart(fig_protocols)

            if st.button("Generate PDF Report"):
                st.write("Feature not implemented yet.")

# Sidebar for navigation
st.sidebar.image("assets/naiture_ai_white.png", use_column_width=True)
st.sidebar.title("Dashboard Demo")
page = st.sidebar.radio("Go to", ["Overview", "Form Response Distribution", "Client Progress Over Time", "Data Export"])

# Page Settings section
st.sidebar.title("Page Settings")
if st.sidebar.button("Toggle Wide Mode", help="Switch between wide and centered page layouts."):
    toggle_wide_mode()

# Load data
clients, forms, questions, responses, client_form_responses, protocols = load_data()

# Render selected page
if page == "Overview":
    overview_page(clients, forms, questions, responses, client_form_responses, protocols)
elif page == "Form Response Distribution":
    form_response_distribution(forms, client_form_responses, responses, questions)
elif page == "Client Progress Over Time":
    client_progress_over_time(clients, client_form_responses, responses, questions)
elif page == "Data Export":
    data_export(clients, forms, questions, responses, client_form_responses, protocols)
