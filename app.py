import streamlit as st
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(page_title="CustodyGuard", layout="wide")

st.title("CustodyGuard: Revenue Leakage Detection")
st.markdown("### Oil & Gas Custody Transfer Reconciliation")

# Load Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('custody_data.csv')
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    except FileNotFoundError:
        st.error("Data file 'custody_data.csv' not found. Please run generate_data.py first.")
        return None

df = load_data()

if df is not None:
    # --- Calculations ---
    
    # Standard Volume Calculation (Simplified to 60F)
    # VCF = exp(-alpha * delta_T * (1 + 0.8 * alpha * delta_T)) is the complex one
    # We will use the simplified linear approximation used in generation for consistency, 
    # but ideally we would use API tables.
    # Standard Vol = Observed Vol * (1 + (60 - Observed Temp) * 0.0005)
    
    # Constants
    OIL_PRICE = 75.0
    THERMAL_COEFF = 0.0005
    
    df['Seller_Std_Vol'] = df['Seller_Vol_Observed'] * (1 + (60 - df['Seller_Temp_F']) * THERMAL_COEFF)
    df['Buyer_Std_Vol'] = df['Buyer_Vol_Observed'] * (1 + (60 - df['Buyer_Temp_F']) * THERMAL_COEFF)
    
    # Variance Calculation
    # Variance = Seller - Buyer (Positive means Seller sent more than Buyer received -> Loss/Leakage)
    df['Variance_Bbl'] = df['Seller_Std_Vol'] - df['Buyer_Std_Vol']
    df['Variance_Pct'] = (df['Variance_Bbl'] / df['Seller_Std_Vol']) * 100
    df['Financial_Loss'] = df['Variance_Bbl'] * OIL_PRICE
    
    # Anomaly Detection
    # Critical if Variance % > 0.2%
    df['Is_Critical'] = df['Variance_Pct'] > 0.2
    
    # --- KPIs ---
    
    total_vol_seller = df['Seller_Std_Vol'].sum()
    total_financial_loss = df[df['Financial_Loss'] > 0]['Financial_Loss'].sum() # Only counting positive variance as loss
    critical_incidents_count = df['Is_Critical'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Volume (Seller Std)", f"{total_vol_seller:,.0f} bbl")
        
    with col2:
        st.metric("Total Financial Loss (Est)", f"${total_financial_loss:,.2f}")
        
    with col3:
        st.metric("Critical Incidents", f"{critical_incidents_count}", delta_color="inverse")
        
    # --- Visualizations ---
    
    st.subheader("Variance Trend Over Time")
    
    # Line Chart of Variance %
    st.line_chart(df.set_index('Timestamp')['Variance_Pct'])
    
    # --- Detailed Analysis ---
    
    st.subheader("Critical Anomalies (Variance > 0.2%)")
    
    critical_df = df[df['Is_Critical']].copy()
    
    # Format for display
    display_cols = ['Transaction_ID', 'Timestamp', 'Seller_Std_Vol', 'Buyer_Std_Vol', 'Variance_Bbl', 'Variance_Pct', 'Financial_Loss']
    
    st.dataframe(
        critical_df[display_cols].style.format({
            'Seller_Std_Vol': '{:.2f}',
            'Buyer_Std_Vol': '{:.2f}',
            'Variance_Bbl': '{:.2f}',
            'Variance_Pct': '{:.2f}%',
            'Financial_Loss': '${:,.2f}'
        })
    )
    
    # Show raw data option
    with st.expander("View Raw Data"):
        st.dataframe(df)

else:
    st.info("Awaiting data generation...")
