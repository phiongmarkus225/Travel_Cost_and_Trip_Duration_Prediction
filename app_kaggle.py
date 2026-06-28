import streamlit as st
import kagglehub
import os
import pandas as pd

# Page config for a modern look
st.set_page_config(
    page_title="Kaggle Dataset Explorer",
    page_icon="📊",
    layout="wide"
)

# Title section
st.title("🚕 Kaggle Dataset Explorer & Loader")
st.markdown("This application downloads and loads the specified Kaggle dataset using `kagglehub`.")

dataset_handle = "aryanpatel212/cleaned-nyc-taxi-trip-data-2025-sample"
st.info(f"**Dataset Handle:** `{dataset_handle}`")

# Button to trigger download
if st.button("⚡ Download Dataset Files from Kaggle"):
    with st.spinner("Downloading dataset..."):
        try:
            # Download dataset files
            dataset_path = kagglehub.dataset_download(dataset_handle)
            st.session_state["dataset_path"] = dataset_path
            st.success(f"Successfully downloaded to: `{dataset_path}`")
        except Exception as e:
            st.error(f"Error downloading dataset: {e}")

# If downloaded, display files and show options to view them
if "dataset_path" in st.session_state:
    path = st.session_state["dataset_path"]
    
    # List files in the downloaded directory
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    
    if not files:
        st.warning("No files found in the dataset directory.")
    else:
        st.markdown("### 📁 Select File to Load")
        selected_file = st.selectbox("Choose a file", files)
        
        if st.button("📊 Load File into Table"):
            with st.spinner(f"Loading {selected_file}..."):
                try:
                    file_full_path = os.path.join(path, selected_file)
                    # Load based on extension
                    if selected_file.endswith(".csv"):
                        df = pd.read_csv(file_full_path)
                    elif selected_file.endswith(".parquet"):
                        df = pd.read_parquet(file_full_path)
                    else:
                        df = pd.read_csv(file_full_path) # Fallback
                    
                    st.success(f"Successfully loaded {selected_file}!")
                    st.markdown("#### Preview (First 10 Rows)")
                    st.dataframe(df.head(10))
                    
                    st.markdown("#### Dataset Info")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Rows", f"{len(df):,}")
                    with col2:
                        st.metric("Total Columns", f"{len(df.columns)}")
                    
                    st.markdown("#### Columns and Data Types")
                    st.write(df.dtypes.to_frame(name="Data Type"))
                    
                except Exception as e:
                    st.error(f"Error loading file: {e}")
