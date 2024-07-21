import streamlit as st
import pandas as pd


def load_data_from_urls_moto(urls_moto):
    dataframes = []
    for url in urls_moto:
        try:
            df = pd.read_csv(url, sep=',', header=0)
            
            # Convert the date column to string first
            df['Ngày'] = df['Ngày'].astype(str)
            
            # Try multiple date formats
            date_formats = ['%d/%m/%Y', '%d/%m/%y']
            for fmt in date_formats:
                df['Ngày'] = pd.to_datetime(df['Ngày'], format=fmt, errors='coerce')
                if df['Ngày'].notna().all():
                    break
            
            # Combine customer and street name
            df['Khách hàng'] = df['Khách hàng ( Hoặc số địa chỉ)'] + ' - ' + df['Tên đường']
            
            dataframes.append(df)
        except Exception as e:
            print(f"Error loading data from {url}: {e}")
    
    combined_data = pd.concat(dataframes,ignore_index=True)
    combined_data.dropna(subset=['Ngày'], inplace=True)
    combined_data.reset_index(drop=True, inplace=True)  
    combined_data = combined_data.sort_values(by='Ngày', ascending=False).reset_index(drop=True)
    # Check for missing dates and handle them
    missing_dates = combined_data['Ngày'].isna().sum()
    if missing_dates > 0:
        print(f"Warning: {missing_dates} rows have missing or improperly formatted dates.")
        # Investigate rows with missing dates
        missing_date_rows = combined_data[combined_data['Ngày'].isna()]
        print("Rows with missing dates:")
        print(missing_date_rows)
        
        # Optionally fill missing dates with a specific value or handle them as needed
        # combined_data['Ngày'].fillna(pd.Timestamp('1900-01-01'), inplace=True)
    print(combined_data)
    return combined_data


def load_data_from_urls_truck(urls_truck):
    dataframes = []
    for url in urls_truck:
        try:
            df = pd.read_csv(url, sep=',', header=0)
            
            # Convert the date column to string first
            df['Ngày'] = df['Ngày'].astype(str)
            
            # Try multiple date formats
            date_formats = ['%d/%m/%Y', '%d/%m/%y']
            for fmt in date_formats:
                df['Ngày'] = pd.to_datetime(df['Ngày'], format=fmt, errors='coerce')
                if df['Ngày'].notna().all():
                    break
            
            dataframes.append(df)
        except Exception as e:
            print(f"Error loading data from {url}: {e}")
    
    combined_data = pd.concat(dataframes, ignore_index=True)
    combined_data.dropna(subset=['Ngày'], inplace=True)
    combined_data.reset_index(drop=True, inplace=True)  
    combined_data = combined_data.sort_values(by='Ngày', ascending=False).reset_index(drop=True)
    # Check for missing dates and handle them
    missing_dates = combined_data['Ngày'].isna().sum()
    if missing_dates > 0:
        print(f"Warning: {missing_dates} rows have missing or improperly formatted dates.")
        # Investigate rows with missing dates
        missing_date_rows = combined_data[combined_data['Ngày'].isna()]
        print("Rows with missing dates:")
        print(missing_date_rows)
        
    print(combined_data)
    return combined_data
