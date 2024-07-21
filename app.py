import streamlit as st
import moto
import attendance
import truck
import analysis
import salary
import data_prepare
import inventory
import customer_pricing

urls_moto = [
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vQjF-vOUyngQKPRXkYvKwIDMAAoK5Jm_RGblSz2FLJsRDmu8IwfwJpfgcPgAY16FmXMN3tBKIPslHem/pub?gid=568267471&single=true&output=csv',
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vQjF-vOUyngQKPRXkYvKwIDMAAoK5Jm_RGblSz2FLJsRDmu8IwfwJpfgcPgAY16FmXMN3tBKIPslHem/pub?gid=261999241&single=true&output=csv',
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vQjF-vOUyngQKPRXkYvKwIDMAAoK5Jm_RGblSz2FLJsRDmu8IwfwJpfgcPgAY16FmXMN3tBKIPslHem/pub?gid=893951989&single=true&output=csv']
urls_truck = [
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vQjF-vOUyngQKPRXkYvKwIDMAAoK5Jm_RGblSz2FLJsRDmu8IwfwJpfgcPgAY16FmXMN3tBKIPslHem/pub?gid=63454759&single=true&output=csv'
    ]

raw_data_moto = data_prepare.load_data_from_urls_moto(urls_moto)
raw_data_truck = data_prepare.load_data_from_urls_truck(urls_truck) 

st.sidebar.title("Chọn chức năng muốn thao tác")
option = st.sidebar.selectbox('Chức năng',['Truy xuất dữ liệu xe máy', 'Truy xuất dữ liệu ô tô','Quản lý công nợ hàng hoá',
                                                               'Quản lý giá cả khách hàng','Bảng chấm công','Bảng tính lương','Công nợ khách hàng','Quản lý Nhân Viên'])

if option == 'Truy xuất dữ liệu xe máy':
    st.header("Thông tin xe máy")
    moto.display_moto_data(raw_data_moto)

elif option == 'Bảng chấm công':
    st.header("Bảng chấm công")
    attendance.display_time_tracking()


elif option == 'Quản lý công nợ hàng hoá':
    inventory. run_inventory_management_app(raw_data_moto,raw_data_truck)

elif option == 'Quản lý giá cả khách hàng':
    st.header("Quản lý giá cả khách hàng")
    customer_pricing.run_pricing_app(raw_data_moto,raw_data_truck)

elif option == 'Quản lý Nhân Viên':
    attendance.display_employee_form()

elif option == 'Truy xuất dữ liệu ô tô':
    st.header("Thông tin ô tô")
    truck.display_truck_data(raw_data_truck)



# elif option == 'Phân tích':
#     st.header("Thông tin Phân tích")
#     analysis.display_car_data()
# elif option == 'Lương':
#     st.header("Thông tin ô tô")
#     salary.display_car_data()
