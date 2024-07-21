import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import calendar

# Kết nối cơ sở dữ liệu SQLite
def connect_db():
    return sqlite3.connect('company.db')

# Tạo bảng nhân viên
def create_employee_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            base_salary REAL NOT NULL,
            allowance REAL NOT NULL,
            insurance REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Tạo bảng chấm công
def create_attendance_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            date TEXT,
            presence REAL,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
            UNIQUE(employee_id, date)
        )
    ''')
    conn.commit()
    conn.close()

# Thêm nhân viên
def insert_employee(name, base_salary, allowance, insurance):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO employees (employee_name, base_salary, allowance, insurance)
        VALUES (?, ?, ?, ?)
    ''', (name, base_salary, allowance, insurance))
    conn.commit()
    conn.close()

# Cập nhật thông tin nhân viên
def update_employee(employee_id, name, base_salary, allowance, insurance):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE employees
        SET employee_name = ?, base_salary = ?, allowance = ?, insurance = ?
        WHERE employee_id = ?
    ''', (name, base_salary, allowance, insurance, employee_id))
    conn.commit()
    conn.close()

# Xóa nhân viên
def delete_employee(employee_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM employees WHERE employee_id = ?', (employee_id,))
    conn.commit()
    conn.close()

# Thêm hoặc cập nhật thông tin chấm công
def upsert_attendance(employee_id, date, presence):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO attendance (employee_id, date, presence)
        VALUES (?, ?, ?)
        ON CONFLICT(employee_id, date)
        DO UPDATE SET presence=excluded.presence
    ''', (employee_id, date, presence))
    conn.commit()
    conn.close()

# Lấy tên nhân viên
def get_employee_names():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id, employee_name FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return employees

# Lấy tất cả thông tin nhân viên
def get_all_employee_info():
    conn = connect_db()
    query = "SELECT * FROM employees"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Lấy dữ liệu chấm công theo tháng
def get_month_entries(year, month):
    conn = connect_db()
    query = '''
        SELECT employees.employee_name, attendance.date, attendance.presence
        FROM attendance
        JOIN employees ON attendance.employee_id = employees.employee_id
        WHERE strftime('%Y', attendance.date) = ? AND strftime('%m', attendance.date) = ?
    '''
    df = pd.read_sql_query(query, conn, params=(year, month))
    conn.close()
    return df

# Định dạng số với dấu phân cách hàng nghìn
def format_currency(value):
    return f"{value:,.0f}"

# Hiển thị giao diện nhập thông tin nhân viên
def display_employee_form():
    st.title("Quản lý Nhân Viên")

    # Tạo bảng nhân viên nếu chưa có
    create_employee_table()

    st.header("Nhập thông tin nhân viên")
    employee_name = st.text_input("Tên nhân viên")
    base_salary = st.number_input("Lương cơ bản", min_value=0.0, format="%.2f")
    allowance = st.number_input("Phụ cấp", min_value=0.0, format="%.2f")
    insurance = st.number_input("Bảo hiểm", min_value=0.0, format="%.2f")

    if st.button("Thêm nhân viên"):
        insert_employee(employee_name, base_salary, allowance, insurance)
        st.success("Nhân viên đã được thêm thành công!")

    st.header("Cập nhật hoặc xóa nhân viên")
    employees = get_employee_names()
    employee_ids = [emp[0] for emp in employees]
    employee_names = [emp[1] for emp in employees]
    selected_employee_id = st.selectbox("Chọn nhân viên", employee_ids, format_func=lambda x: dict(employees)[x])

    if selected_employee_id:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (selected_employee_id,))
        employee = cursor.fetchone()
        conn.close()

        if employee:
            new_name = st.text_input("Tên nhân viên", value=employee[1])
            new_base_salary = st.number_input("Lương cơ bản", value=employee[2], format="%.2f")
            new_allowance = st.number_input("Phụ cấp", value=employee[3], format="%.2f")
            new_insurance = st.number_input("Bảo hiểm", value=employee[4], format="%.2f")

            if st.button("Cập nhật thông tin"):
                update_employee(selected_employee_id, new_name, new_base_salary, new_allowance, new_insurance)
                st.success("Thông tin nhân viên đã được cập nhật thành công!")

            if st.button("Xóa nhân viên"):
                delete_employee(selected_employee_id)
                st.success("Nhân viên đã được xóa thành công!")

    st.header("Danh sách nhân viên")
    employees_df = get_all_employee_info()
    employees_df['base_salary'] = employees_df['base_salary'].apply(format_currency)
    employees_df['allowance'] = employees_df['allowance'].apply(format_currency)
    employees_df['insurance'] = employees_df['insurance'].apply(format_currency)
    st.write(employees_df)

# Hiển thị giao diện chấm công
def display_time_tracking():
    st.title("Chấm Công")

    # Tạo bảng chấm công nếu chưa có
    create_attendance_table()

    # Chọn nhân viên
    employees = get_employee_names()
    employee_dict = {name: emp_id for emp_id, name in employees}
    selected_employee_name = st.selectbox("Chọn nhân viên", list(employee_dict.keys()))
    selected_employee_id = employee_dict[selected_employee_name]

    # Chọn tháng và năm
    now = datetime.now()
    selected_month = st.selectbox("Chọn tháng", list(range(1, 13)), format_func=lambda x: calendar.month_name[x])
    selected_year = st.selectbox("Chọn năm", list(range(2024, now.year + 1)))  # Điều chỉnh năm bắt đầu từ 2024

    # Tạo bảng với ngày trong tháng
    start_date = datetime(selected_year, selected_month, 1)
    end_date = (start_date + timedelta(days=calendar.monthrange(selected_year, selected_month)[1])).replace(day=1) - timedelta(days=1)

    days = [(start_date + timedelta(days=i)).strftime('%d/%m') for i in range((end_date - start_date).days + 1)]

    st.header(f"Nhập chấm công cho {selected_employee_name} - tháng {calendar.month_name[selected_month]} năm {selected_year}")

    # Xác định các ngày chủ nhật
    sundays = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1) if (start_date + timedelta(days=i)).weekday() == 6]
    sundays_str = [d.strftime('%d/%m') for d in sundays]

    # Tạo dữ liệu chấm công
    data = {}
    for day in days:
        default_value = 1.0 if day not in sundays_str else 0.0
        data[day] = st.number_input(f"{day}", min_value=0.0, max_value=1.0, step=0.25, value=default_value, format="%.2f")

    if st.button("Lưu dữ liệu"):
        for day in days:
            date = start_date.replace(day=int(day.split('/')[0])).strftime('%Y-%m-%d')
            presence = data[day]
            upsert_attendance(selected_employee_id, date, presence)
        st.success("Dữ liệu đã được lưu thành công!")

    # Hiển thị bảng chấm công của tháng được chọn
    st.header(f"Bảng chấm công tháng {calendar.month_name[selected_month]} năm {selected_year}")

    # Lấy dữ liệu chấm công theo tháng
    month_entries = get_month_entries(str(selected_year), f"{selected_month:02d}")

    # Xử lý dữ liệu chấm công
    if not month_entries.empty:
        month_entries['date'] = pd.to_datetime(month_entries['date'])
        pivot_table = month_entries.pivot(index='employee_name', columns='date', values='presence').fillna(0)
        pivot_table.columns = [d.strftime('%d/%m') for d in pivot_table.columns]
        st.write(pivot_table)

        # Tổng số ngày công
        work_days_count = len([d for d in days if d not in sundays_str])
        employee_summary = month_entries.groupby('employee_name')['presence'].sum().reset_index()
        employee_summary['presence'] = employee_summary['presence'].apply(lambda x: f"{x:.2f}")
        employee_summary['total_work_days'] = work_days_count

        st.write("Tổng số ngày công:")
        st.write(employee_summary)
