import streamlit as st

import pandas as pd

import plotly.graph_objects as go

from plotly.subplots import make_subplots

# 1. Cấu hình trang

st.set_page_config(page_title="Dashboard OEE", layout="wide")

# --- CƠ SỞ DỮ LIỆU NGƯỜI DÙNG (Giả lập) ---

USER_DB = {

    "admin": {"password": "123", "role": "Admin", "name": "Giám Đốc"},

    "manager": {"password": "123", "role": "Manager", "name": "Kỹ Sư IE"},

    "operator": {"password": "123", "role": "Operator", "name": "Tổ Trưởng Line 1"}

}

# --- HÀM KIỂM TRA ĐĂNG NHẬP ---

def login():

    st.title("🔐 Đăng nhập Hệ Thống OEE")

    st.write("Vui lòng đăng nhập để tiếp tục (Tài khoản mẫu: admin / manager / operator - Mật khẩu: 123)")

    with st.form("login_form"):

        username = st.text_input("Tên đăng nhập")

        password = st.text_input("Mật khẩu", type="password")

        submit_button = st.form_submit_button("Đăng nhập")

        if submit_button:

            if username in USER_DB and USER_DB[username]["password"] == password:

                # Lưu thông tin vào session_state để hệ thống "nhớ"

                st.session_state["logged_in"] = True

                st.session_state["username"] = username

                st.session_state["name"] = USER_DB[username]["name"]

                st.session_state["role"] = USER_DB[username]["role"]

                st.rerun() # Tải lại trang sau khi đăng nhập thành công

            else:

                st.error("Tên đăng nhập hoặc mật khẩu không chính xác!")

# --- HÀM ĐĂNG XUẤT ---

def logout():

    st.session_state.clear()

    st.rerun()

# --- KIỂM TRA TRẠNG THÁI ---

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:

    # Nếu chưa đăng nhập -> Hiện màn hình đăng nhập

    login()

else:

    # --- NẾU ĐÃ ĐĂNG NHẬP THÀNH CÔNG -> HIỆN GIAO DIỆN PHẦN MỀM ---

    # Thanh điều hướng bên trái (Sidebar)

    with st.sidebar:

        st.success(f"👋 Xin chào, {st.session_state['name']}!")
st.info(f"Vai trò: **{st.session_state['role']}**")

        st.button("Đăng xuất", on_click=logout)

    st.title("📊 Hệ Thống Quản Lý OEE Nhà Máy")

    # ---------------------------------------------------------

    # PHẦN 1: AI CŨNG CÓ THỂ XEM (KPI Cơ bản)

    # ---------------------------------------------------------

    oee_data = {"OEE": 82.5, "Availability": 87.0, "Performance": 94.2, "Quality": 98.1}

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(label="OEE Tổng", value=f"{oee_data['OEE']}%")

    col2.metric(label="Sẵn sàng (A)", value=f"{oee_data['Availability']}%", delta="-12%")

    col3.metric(label="Hiệu suất (P)", value=f"{oee_data['Performance']}%")

    col4.metric(label="Chất lượng (Q)", value=f"{oee_data['Quality']}%")

    st.markdown("---")

    # ---------------------------------------------------------

    # PHẦN 2: PHÂN QUYỀN - CHỈ MANAGER VÀ ADMIN ĐƯỢC XEM

    # ---------------------------------------------------------

    if st.session_state["role"] in ["Manager", "Admin"]:

        st.subheader("Phân tích Pareto: Top Nguyên Nhân Dừng Máy")

        # Dữ liệu và vẽ biểu đồ Pareto

        df = pd.DataFrame({

            "Lý do": ["Kẹt phôi / Kẹt máy", "Chờ nguyên liệu", "Hỏng cảm biến", "Vệ sinh đầu ca", "Chờ QC kiểm tra"],

            "So_Phut": [150, 90, 60, 40, 25]

        })

        df = df.sort_values(by="So_Phut", ascending=False).reset_index(drop=True)

        tong_thoi_gian = df["So_Phut"].sum()

        df["Tich_Luy"] = df["So_Phut"].cumsum()

        df["Phan_Tram_Tich_Luy"] = (df["Tich_Luy"] / tong_thoi_gian) * 100

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(x=df["Lý do"], y=df["So_Phut"], name="Thời gian dừng (Phút)", marker_color="#e11d48"), secondary_y=False)

        fig.add_trace(go.Scatter(x=df["Lý do"], y=df["Phan_Tram_Tich_Luy"], name="% Tích lũy", mode="lines+markers+text", text=df["Phan_Tram_Tich_Luy"].round(1).astype(str) + "%", textposition="top left", marker=dict(color="#0369a1", size=8), line=dict(width=3)), secondary_y=True)

        fig.update_layout(title_text="Biểu đồ Pareto Downtime", hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

        fig.update_yaxes(title_text="Số phút", secondary_y=False)

        fig.update_yaxes(title_text="Tỷ lệ %", range=[0, 110], secondary_y=True)

        st.plotly_chart(fig, use_container_width=True)

    else:

        # Lời nhắn dành cho Operator
st.info("🔒 Bạn cần quyền Quản lý (Manager) hoặc Giám đốc (Admin) để xem biểu đồ phân tích sâu.")

    # ---------------------------------------------------------

    # PHẦN 3: PHÂN QUYỀN - CHỈ ADMIN ĐƯỢC XEM

    # ---------------------------------------------------------

    if st.session_state["role"] == "Admin":

        st.markdown("---")

        st.subheader("⚙️ Bảng Điều Khiển Quản Trị Hệ Thống")

        st.warning("Khu vực này chỉ dành cho Admin. Nơi đây sẽ chứa các tính năng như thêm người dùng, cấu hình máy móc, thay đổi ca làm việc...")
 
