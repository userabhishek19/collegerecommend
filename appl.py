import streamlit as st
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(
    page_title="College Recommendation System",
    page_icon="🎓",
    layout="wide"
)

# Function to clean fee data
def clean_fee(fee_str):
    if pd.isna(fee_str) or fee_str == '--':
        return 0.0
    # Remove commas and convert to float
    return float(str(fee_str).replace(',', ''))

# Function to format currency
def format_currency(amount):
    return f"₹{amount:,.2f}"

# Function to load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("College_data.csv")
        # Clean fee columns
        df['UG_fee'] = df['UG_fee'].apply(clean_fee)
        df['PG_fee'] = df['PG_fee'].apply(clean_fee)
        return df
    except FileNotFoundError:
        st.error("College_data.csv file not found. Please ensure the file exists in the correct location.")
        return None

# Load the data
df = load_data()

if df is not None:
    # Main title
    st.title("🎓 College Recommendation System")
    st.write("Find the best college based on your preferences!")

    # Create two columns for filters
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Location Preferences")
        # State selection with "All" option
        all_states = ["All"] + sorted(df["State"].unique().tolist())
        state = st.selectbox("Select State", all_states)
        
        # Stream selection
        stream = st.selectbox("Select Stream", sorted(df["Stream"].unique().tolist()))

    with col2:
        st.subheader("Fee Range")
        # Fee range sliders
        max_ug_fee = float(df["UG_fee"].max())
        max_pg_fee = float(df["PG_fee"].max())
        
        ug_fee_range = st.slider(
            "UG Fee Range",
            min_value=0.0,
            max_value=max_ug_fee,
            value=(0.0, max_ug_fee)
        )
        st.write(f"Selected UG Fee Range: {format_currency(ug_fee_range[0])} - {format_currency(ug_fee_range[1])}")
        
        pg_fee_range = st.slider(
            "PG Fee Range",
            min_value=0.0,
            max_value=max_pg_fee,
            value=(0.0, max_pg_fee)
        )
        st.write(f"Selected PG Fee Range: {format_currency(pg_fee_range[0])} - {format_currency(pg_fee_range[1])}")

    # Create columns for ratings
    st.subheader("Rating Preferences")
    rating_cols = st.columns(4)

    with rating_cols[0]:
        min_rating = st.slider("Minimum Overall Rating", 0.0, 10.0, 0.0)
        min_academic = st.slider("Minimum Academic Rating", 0.0, 10.0, 0.0)

    with rating_cols[1]:
        min_accommodation = st.slider("Minimum Accommodation Rating", 0.0, 10.0, 0.0)
        min_faculty = st.slider("Minimum Faculty Rating", 0.0, 10.0, 0.0)

    with rating_cols[2]:
        min_infrastructure = st.slider("Minimum Infrastructure Rating", 0.0, 10.0, 0.0)
        min_placement = st.slider("Minimum Placement Rating", 0.0, 10.0, 0.0)

    with rating_cols[3]:
        min_social = st.slider("Minimum Social Life Rating", 0.0, 10.0, 0.0)

    # Filter button
    if st.button("Find Colleges"):
        # Initialize mask
        mask = pd.Series(True, index=df.index)

        # Apply filters
        if state != "All":
            mask &= df["State"] == state
        mask &= df["Stream"] == stream
        mask &= df["UG_fee"].between(ug_fee_range[0], ug_fee_range[1])
        mask &= df["PG_fee"].between(pg_fee_range[0], pg_fee_range[1])
        
        # Convert ratings to float and replace '--' with 0
        rating_columns = ["Rating", "Academic", "Accommodation", "Faculty", 
                         "Infrastructure", "Placement", "Social_Life"]
        
        for col in rating_columns:
            df[col] = pd.to_numeric(df[col].replace('--', '0'), errors='coerce').fillna(0)

        # Rating filters
        mask &= df["Rating"] >= min_rating
        mask &= df["Academic"] >= min_academic
        mask &= df["Accommodation"] >= min_accommodation
        mask &= df["Faculty"] >= min_faculty
        mask &= df["Infrastructure"] >= min_infrastructure
        mask &= df["Placement"] >= min_placement
        mask &= df["Social_Life"] >= min_social

        # Filter the dataframe
        filtered_df = df[mask].copy()

        # Calculate weighted score based on ratings
        filtered_df["Overall_Score"] = (
            filtered_df["Rating"] * 0.2 +
            filtered_df["Academic"] * 0.2 +
            filtered_df["Placement"] * 0.15 +
            filtered_df["Infrastructure"] * 0.15 +
            filtered_df["Faculty"] * 0.1 +
            filtered_df["Accommodation"] * 0.1 +
            filtered_df["Social_Life"] * 0.1
        )

        # Sort by overall score
        filtered_df = filtered_df.sort_values("Overall_Score", ascending=False)

        # Display results
        if len(filtered_df) > 0:
            st.subheader(f"Found {len(filtered_df)} matching colleges:")
            
            # Display colleges in an expandable format
            for idx, row in filtered_df.iterrows():
                with st.expander(f"{row['College_Name']} - Overall Score: {row['Overall_Score']:.2f}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Basic Information:**")
                        st.write(f"State: {row['State']}")
                        st.write(f"Stream: {row['Stream']}")
                        st.write(f"UG Fee: {format_currency(row['UG_fee'])}")
                        st.write(f"PG Fee: {format_currency(row['PG_fee'])}")
                    
                    with col2:
                        st.write("**Ratings:**")
                        st.write(f"Overall Rating: {row['Rating']:.1f}/10")
                        st.write(f"Academic: {row['Academic']:.1f}/10")
                        st.write(f"Placement: {row['Placement']:.1f}/10")
                        st.write(f"Infrastructure: {row['Infrastructure']:.1f}/10")
        else:
            st.warning("No colleges found matching your criteria. Try adjusting your filters.")

        # Add download button for filtered results
        if len(filtered_df) > 0:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="recommended_colleges.csv",
                mime="text/csv"
            )
else:
    st.error("Unable to load the college data. Please check if the data file exists and is properly formatted.")