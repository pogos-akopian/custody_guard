import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_data():
    np.random.seed(42)
    n_rows = 1000
    
    # Generate timestamps
    start_time = datetime.now() - timedelta(days=30)
    timestamps = [start_time + timedelta(minutes=45*i) for i in range(n_rows)]
    
    # Generate Transaction IDs
    transaction_ids = [f"TXN-{10000+i}" for i in range(n_rows)]
    
    # Generate Seller Data
    # Seller Volume Observed: Normally distributed around 1000 bbl
    seller_vol_observed = np.random.normal(1000, 50, n_rows)
    
    # Seller Temp F: Normally distributed around 80 F
    seller_temp_f = np.random.normal(80, 5, n_rows)
    
    # Seller Pressure: Normally distributed around 150 psi
    seller_pressure = np.random.normal(150, 10, n_rows)
    
    # Buyer Data
    # Buyer Temp F: Usually slightly cooler than seller due to transport/pipe
    buyer_temp_f = seller_temp_f - np.random.uniform(0, 5, n_rows)
    
    # Calculate Buyer Volume Observed based on thermal contraction
    # Simplified VCF (Volume Correction Factor) logic:
    # Oil shrinks as it cools. Approx 0.0005 per degree F difference (simplified coefficient)
    # VCF = 1 - (Temp_Diff * Coefficient)
    # This is a simplification for demonstration purposes.
    
    temp_diff = seller_temp_f - buyer_temp_f
    # If buyer temp is lower, volume should be lower.
    # We'll apply a simplified shrinkage factor.
    # Volume_Buyer = Volume_Seller * (1 - (Seller_Temp - Buyer_Temp) * 0.0005)
    # Adding some random noise to the measurement
    measurement_noise = np.random.normal(0, 1, n_rows)
    
    buyer_vol_observed = seller_vol_observed * (1 - (seller_temp_f - buyer_temp_f) * 0.0005) + measurement_noise
    
    # Create DataFrame
    df = pd.DataFrame({
        'Transaction_ID': transaction_ids,
        'Timestamp': timestamps,
        'Seller_Vol_Observed': seller_vol_observed,
        'Seller_Temp_F': seller_temp_f,
        'Seller_Pressure': seller_pressure,
        'Buyer_Temp_F': buyer_temp_f,
        'Buyer_Vol_Observed': buyer_vol_observed
    })
    
    # Introduce Anomalies in the last 50 records
    # 1. Meter Failure: Buyer volume drops by 5%
    # 2. Theft: Volume drops by 20 bbl
    
    # Apply anomalies to a subset of the last 50 rows
    last_50_indices = df.index[-50:]
    
    # Randomly choose which anomaly to apply
    for idx in last_50_indices:
        anomaly_type = np.random.choice(['None', 'Meter_Failure', 'Theft'], p=[0.4, 0.3, 0.3])
        
        if anomaly_type == 'Meter_Failure':
            df.at[idx, 'Buyer_Vol_Observed'] *= 0.95
        elif anomaly_type == 'Theft':
            df.at[idx, 'Buyer_Vol_Observed'] -= 20
            
    # Save to CSV
    df.to_csv('custody_data.csv', index=False)
    print("Successfully generated 'custody_data.csv' with 1000 rows.")

if __name__ == "__main__":
    generate_data()
