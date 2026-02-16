import streamlit as st
import pandas as pd
from database import get_all_design_requests
from auth import try_auto_login

st.set_page_config(page_title="Design Dashboard", page_icon="🎨", layout="wide")

try_auto_login()

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access this page.")
    st.stop()

st.title("🎨 Design Dashboard")

requests = get_all_design_requests()

if not requests:
    st.info("No design requests found.")
else:
    # Convert to DataFrame
    data = [dict(row) for row in requests]
    df = pd.DataFrame(data)

    # Sidebar Filters
    st.sidebar.header("Filters")
    status_filter = st.sidebar.multiselect("Status", df['status'].unique(), default=df['status'].unique())
    priority_filter = st.sidebar.multiselect("Priority", df['priority'].unique(), default=df['priority'].unique())
    
    # Apply filters
    filtered_df = df[
        (df['status'].isin(status_filter)) &
        (df['priority'].isin(priority_filter))
    ]

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Requests", len(filtered_df))
    m2.metric("Open Requests", len(filtered_df[filtered_df['status'] == 'Open']))
    m3.metric("High Priority", len(filtered_df[filtered_df['priority'] == 'High']))
    
    st.divider()

    st.info("👆 Click on a row to view details.")
    
    event = st.dataframe(
        filtered_df[['id', 'screen_name', 'priority', 'status', 'submitter', 'created_at']],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "created_at": st.column_config.DatetimeColumn("Created At", format="D MMM YYYY, h:mm a"),
            "priority": st.column_config.TextColumn("Priority", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
        }
    )

    if event.selection.rows:
        selected_index = event.selection.rows[0]
        selected_req_id = filtered_df.iloc[selected_index]['id']
        st.session_state['selected_design_id'] = selected_req_id
        st.switch_page("pages/design_detail.py")
