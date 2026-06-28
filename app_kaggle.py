import streamlit as st
import kagglehub
from kagglehub import KaggleDatasetAdapter

# Page config
st.set_page_config(
    page_title="Direct Kaggle Loader",
    page_icon="🚕",
    layout="wide"
)

st.title("🚕 Direct Kaggle Dataset Loader")
st.markdown("This app pulls the dataset directly into a Pandas DataFrame using `kagglehub.load_dataset` without manual steps.")

# The exact filename we found in the dataset
file_path = "NYC_Taxi_Cleaned_Analysis_Ready.csv"
dataset_handle = "aryanpatel212/cleaned-nyc-taxi-trip-data-2025-sample"

st.info(f"**Dataset Handle:** `{dataset_handle}`\n\n**Target File:** `{file_path}`")

if st.button("🚀 Load Dataset Directly from Kaggle"):
    with st.spinner("Pulling data from Kaggle (downloading under the hood if not cached)..."):
        try:
            # Load dataset directly in one go
            df = kagglehub.load_dataset(
                KaggleDatasetAdapter.PANDAS,
                dataset_handle,
                file_path
            )
            
            st.success("Successfully loaded dataset directly in one step!")
            
            # Show preview
            st.markdown("### 📊 Preview (First 10 Rows)")
            st.dataframe(df.head(10))
            
            # Show metadata
            st.markdown("### ℹ️ Dataset Info")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Rows", f"{len(df):,}")
            with col2:
                st.metric("Total Columns", f"{len(df.columns)}")
                
        except Exception as e:
            st.error(f"Error loading dataset: {e}")
