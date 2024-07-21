import streamlit as st
import pandas as pd

urls = [
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vQjF-vOUyngQKPRXkYvKwIDMAAoK5Jm_RGblSz2FLJsRDmu8IwfwJpfgcPgAY16FmXMN3tBKIPslHem/pub?gid=568267471&single=true&output=csv',
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vQjF-vOUyngQKPRXkYvKwIDMAAoK5Jm_RGblSz2FLJsRDmu8IwfwJpfgcPgAY16FmXMN3tBKIPslHem/pub?gid=893951989&single=true&output=csv']

def load_data_from_urls(urls):
    dataframes = []
    for url in urls:
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

def display_statistics(filtered_data, period):
    # Ensure datetime conversion for necessary columns
    if 'Ngày' in filtered_data.columns:
        filtered_data['Ngày'] = pd.to_datetime(filtered_data['Ngày'], errors='coerce')

    if period == 'day':
        filtered_data['Period'] = filtered_data['Ngày'].dt.date
    elif period == 'week':
        filtered_data['Week_Start'] = filtered_data['Ngày'].dt.to_period('W-MON').dt.start_time
        filtered_data['Week_End'] = filtered_data['Week_Start'] + pd.Timedelta(days=6)
        filtered_data['Period'] = filtered_data['Week_Start'].dt.strftime('%d/%m') + ' - ' + filtered_data['Week_End'].dt.strftime('%d/%m')
    elif period == 'month':
        filtered_data['Month_Start'] = filtered_data['Ngày'].dt.to_period('M').dt.start_time
        filtered_data['Month_End'] = filtered_data['Month_Start'] + pd.offsets.MonthEnd(1)
        filtered_data['Period'] = filtered_data['Month_Start'].dt.strftime('%d/%m') + ' - ' + filtered_data['Month_End'].dt.strftime('%d/%m')
    elif period == 'quarter':
        filtered_data['Quarter_Start'] = filtered_data['Ngày'].dt.to_period('Q').dt.start_time
        filtered_data['Quarter_End'] = filtered_data['Quarter_Start'] + pd.offsets.QuarterEnd(startingMonth=3)
        filtered_data['Period'] = filtered_data['Quarter_Start'].dt.strftime('%d/%m') + ' - ' + filtered_data['Quarter_End'].dt.strftime('%d/%m')
    elif period == 'year':
        filtered_data['Year_Start'] = filtered_data['Ngày'].dt.to_period('A').dt.start_time
        filtered_data['Year_End'] = filtered_data['Year_Start'] + pd.offsets.YearEnd()
        filtered_data['Period'] = filtered_data['Year_Start'].dt.strftime('%d/%m') + ' - ' + filtered_data['Year_End'].dt.strftime('%d/%m')
    else:
        raise ValueError("Unsupported period type specified.")

    grouped = filtered_data.dropna(subset=['Period']).groupby('Period')

    stats = grouped.agg({
        'Số lượng Giao': 'sum',
        'Thanh Toán': 'sum',
        'Phương Thức Thanh Toán': lambda x: x.value_counts().to_dict()
    }).reset_index()

    # Convert the Period column to datetime for proper sorting
    if period == 'week':
        stats['Period_Start'] = pd.to_datetime(stats['Period'].str.split(' - ').str[0], format='%d/%m')
    elif period == 'month':
        stats['Period_Start'] = pd.to_datetime(stats['Period'].str.split(' - ').str[0], format='%d/%m')
    elif period == 'quarter':
        stats['Period_Start'] = pd.to_datetime(stats['Period'].str.split(' - ').str[0], format='%d/%m')
    elif period == 'year':
        stats['Period_Start'] = pd.to_datetime(stats['Period'].str.split(' - ').str[0], format='%d/%m')

    if period in ['week', 'month', 'quarter', 'year']:
        stats = stats.sort_values(by='Period_Start', ascending=False).drop(columns='Period_Start')
    else:
        stats = stats.sort_values(by='Period', ascending=False)

    return stats



def display_moto_data():

    data = load_data_from_urls(urls)

    st.sidebar.title("Bộ lọc dữ liệu cho Xe Máy")
    period = st.sidebar.selectbox("Chọn khoảng thời gian", ['day', 'week', 'month', 'quarter', 'year'])
    date_range = st.sidebar.date_input("Chọn khoảng ngày", [])

    customer_filter = st.sidebar.multiselect("Chọn khách hàng", options=data['Khách hàng'].unique())
    product_type_filter = st.sidebar.multiselect("Chọn loại sản phẩm", options=data['Loại sản phẩm'].unique())
    street_filter = st.sidebar.multiselect("Chọn Tên đường", options=data['Tên đường'].unique())
    payment_method_filter = st.sidebar.multiselect("Chọn Phương Thức Thanh Toán", options=data['Phương Thức Thanh Toán'].unique())

    filtered_data = data
    if date_range:
        start_date = pd.Timestamp(date_range[0])  # Convert to Timestamp
        end_date = pd.Timestamp(date_range[1])    # Convert to Timestamp
        filtered_data = filtered_data[(filtered_data['Ngày'] >= start_date) & (filtered_data['Ngày'] <= end_date)]
    
    if customer_filter:
        filtered_data = filtered_data[filtered_data['Khách hàng'].isin(customer_filter)]
    if product_type_filter:
        filtered_data = filtered_data[filtered_data['Loại sản phẩm'].isin(product_type_filter)]
    if street_filter:
        filtered_data = filtered_data[filtered_data['Tên đường'].isin(street_filter)]
    if payment_method_filter:
        filtered_data = filtered_data[filtered_data['Phương Thức Thanh Toán'].isin(payment_method_filter)]

    # Convert 'Ngày' to the desired format for display
    #filtered_data['Ngày'] = filtered_data['Ngày'].dt.strftime('%d/%m/%Y')

    # Display statistics
    stats = display_statistics(filtered_data, period)
    st.write(f"Thống kê theo {period}", stats)

    # Display the DataFrame in a scrollable container
    if filtered_data.empty:
        st.write("No data matches the filters.")
    else:
        st.dataframe(filtered_data, height=600)  # Show filtered data

    # Show overall statistics regardless of filtering
    overall_stats = filtered_data.agg({
        'Số lượng Giao': 'sum',
        'Thanh Toán': 'sum'
    })
    st.write("Thống kê tổng quan", overall_stats)
