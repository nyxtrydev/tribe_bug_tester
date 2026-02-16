import streamlit as st
import pandas as pd
from database import get_all_issues, delete_issue
from auth import try_auto_login

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

try_auto_login()

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📊 Issue Dashboard")

issues = get_all_issues()

if not issues:
    st.info("No issues found.")
else:
    # Convert to DataFrame
    data = [dict(row) for row in issues]
    df = pd.DataFrame(data)

    # Sidebar Filters
    st.sidebar.header("Filters")
    status_filter = st.sidebar.multiselect("Status", df['status'].unique(), default=df['status'].unique())
    severity_filter = st.sidebar.multiselect("Severity", df['severity'].unique(), default=df['severity'].unique())
    account_filter = st.sidebar.multiselect("Account Type", df['account_type'].unique(), default=df['account_type'].unique())
    
    # Apply filters
    filtered_df = df[
        (df['status'].isin(status_filter)) &
        (df['severity'].isin(severity_filter)) &
        (df['account_type'].isin(account_filter))
    ]

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Issues", len(filtered_df))
    m2.metric("Open Issues", len(filtered_df[filtered_df['status'] == 'Open']))
    m3.metric("Critical Issues", len(filtered_df[filtered_df['severity'] == 'Critical']))
    
    st.divider()

    st.info("👆 Click on a row to view details.")

    # Admin Delete Mode
    delete_mode = False
    if st.session_state.get("role") == "Admin":
        delete_mode = st.toggle("Enable Delete Mode (Super Admin Only)", help="Enable to delete issues by clicking on them.")
    
    selection_mode = "single-row"
    
    # Determine columns to display
    display_cols = ['id', 'title', 'severity', 'status', 'submitter', 'created_at']
    # Check if columns exist in filtered_df to avoid key errors if empty (though checked above)
    display_df = filtered_df[display_cols]

    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode=selection_mode,
        column_config={
            "created_at": st.column_config.DatetimeColumn("Created At", format="D MMM YYYY, h:mm a")
        }
    )

    if event.selection.rows:
        selected_index = event.selection.rows[0]
        # map selection index back to filtered_df id
        selected_issue_id = filtered_df.iloc[selected_index]['id']
        
        if delete_mode:
            st.error(f"Are you sure you want to delete Issue {selected_issue_id}?")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("🗑️ Yes, Delete Issue"):
                    delete_issue(selected_issue_id)
                    st.success(f"Issue {selected_issue_id} deleted!")
                    st.rerun()
            with col_cancel:
                if st.button("Cancel"):
                    st.rerun()
        else:
            st.session_state['selected_issue_id'] = selected_issue_id
            st.switch_page("pages/issue_detail.py")
