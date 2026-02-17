import streamlit as st
import pandas as pd
from database import get_all_requirements, delete_requirement
from auth import try_auto_login

st.set_page_config(page_title="Requirement Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

try_auto_login()

from navigation import render_sidebar
render_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📊 Requirement Dashboard")

# Admin Delete Mode
delete_mode = False
if st.session_state.get("role") == "Admin":
    delete_mode = st.toggle("Enable Delete Mode (Admin Only)", help="Enable to delete requirements by clicking on them.")

reqs = get_all_requirements()
if not reqs:
    st.info("No requirements found.")
else:
    # Convert to DataFrame
    df = pd.DataFrame([dict(r) for r in reqs])
    
    # Filter Sidebar
    st.sidebar.subheader("Filters")
    status_filter = st.sidebar.multiselect("Status", options=df['status'].unique(), default=df['status'].unique())
    type_filter = st.sidebar.multiselect("Type", options=df['requirement_type'].unique(), default=df['requirement_type'].unique())
    
    filtered_df = df[df['status'].isin(status_filter) & df['requirement_type'].isin(type_filter)]
    
    # Selection
    st.info("Select a row to view details.")
    
    # Show remarks in an expander for quick view
    with st.expander("Preview Remarks"):
        for index, row in filtered_df.iterrows():
            st.markdown(f"**{row['title']} ({row['id']}):**")
            st.write(row['remarks'])
            st.divider()

    event = st.dataframe(
        filtered_df[['id', 'title', 'requirement_type', 'status', 'submitter', 'created_at']],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    if event.selection.rows:
        selected_index = event.selection.rows[0]
        selected_req_id = filtered_df.iloc[selected_index]['id']
        
        if delete_mode:
            st.error(f"Are you sure you want to delete Requirement {selected_req_id}?")
            col_confirm, col_cancel = st.columns(2)
            if col_confirm.button("Confirm Delete", key="confirm_del"):
                delete_requirement(selected_req_id)
                st.success("Deleted!")
                st.rerun()
        else:
            st.session_state['selected_req_id'] = selected_req_id
            st.page_link("pages/requirement_detail.py", label=f"View Details for {selected_req_id}", icon="➡️")
