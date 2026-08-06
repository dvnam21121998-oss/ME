import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# CẤU HÌNH TRANG
# ==========================================
st.set_page_config(page_title="Dashboard OEE Toàn Diện", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# KHỞI TẠO CƠ SỞ DỮ LIỆU
# ==========================================
if "USER_DB" not in st.session_state:
    st.session_state["USER_DB"] = {
        "admin": {"password": "123", "role": "Admin", "name": "Giám Đốc Nhà Máy"},
        "manager": {"password": "123", "role": "Manager", "name": "Kỹ Sư IE"},
        "operator": {"password": "123", "role": "Operator", "name": "Tổ Trưởng Line G103"}
    }

if "MACHINE_DB" not in st.session_state:
    st.session_state["MACHINE_DB"] = [
        {"id": "M01", "name": "Máy dập Block 1", "line": "G103", "uph": 1200},
        {"id": "M02", "name": "Máy Test Hipot", "line": "G103", "uph": 800},
        {"id": "M03", "name": "Máy hàn tự động", "line": "G103", "uph": 600}
    ]

# ==========================================
# CÁC HÀM XỬ LÝ ĐĂNG NHẬP / ĐĂNG XUẤT
# ==========================================
def login():
    st.markdown("<h2 style='text-align: center; color: #1e293b;'>🔐 ĐĂNG NHẬP HỆ THỐNG OEE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Tài khoản mẫu: <b>admin</b> / <b>manager</b> / <b>operator</b> | Mật khẩu: <b>123</b></p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            submit_button = st.form_submit_button("Đăng nhập", use_container_width=True)
            if submit_button:
                if username in st.session_state["USER_DB"] and st.session_state["USER_DB"][username]["password"] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["name"] = st.session_state["USER_DB"][username]["name"]
                    st.session_state["role"] = st.session_state["USER_DB"][username]["role"]
                    st.rerun()
                else:
                    st.error("Tên đăng nhập hoặc mật khẩu không chính xác!")

def logout():
    st.session_state["logged_in"] = False
    st.session_state.pop("username", None)
    st.session_state.pop("name", None)
    st.session_state.pop("role", None)
    st.rerun()

# ==========================================
# GIAO DIỆN CHÍNH KHI ĐÃ ĐĂNG NHẬP
# ==========================================
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
else:
    # --- SIDEBAR MENU ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2046/2046024.png", width=100)
        st.success(f"👋 Xin chào, **{st.session_state['name']}**!")
        st.info(f"Vai trò: **{st.session_state['role']}**")
        st.markdown("---")
        
        # Tạo danh sách menu điều hướng
        menu_options = ["📊 Dashboard OEE"]
        
        # Chỉ hiển thị các mục quản trị nếu người dùng là Admin
        if st.session_state["role"] == "Admin":
            menu_options.extend([
                "👤 Quản Lý Tài Khoản",
                "🏭 Quản Lý Máy Móc"
            ])
            
        selected_menu = st.radio("📌 ĐIỀU HƯỚNG HỆ THỐNG", menu_options)
        
        st.markdown("---")
        st.button("Đăng xuất", on_click=logout, use_container_width=True)

    # ---------------------------------------------------------
    # TRANG 1: DASHBOARD OEE
    # ---------------------------------------------------------
    if selected_menu == "📊 Dashboard OEE":
        st.markdown("<h1 style='text-align: center; color: #0f172a;'>📊 MANAGEMENT DASHBOARD V2 ACTIONABLE</h1>", unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("### 01. Equipment Health Overview")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric(label="Downtime Rate", value="12.5%", delta="Mới phát sinh", delta_color="inverse")
        kpi2.metric(label="Availability (Sẵn sàng)", value="87.5%", delta="-12% so kỳ trước", delta_color="normal")
        kpi3.metric(label="MTBF (Chạy TB trước khi hỏng)", value="316 Phút", delta="Tốt", delta_color="normal")
        kpi4.metric(label="MTTR (Thời gian sửa TB)", value="45.1 Phút", delta="+5 Phút", delta_color="inverse")

        st.markdown("---")

        if st.session_state["role"] in ["Manager", "Admin"]:
            st.markdown("### 03. Pareto Downtime (80/20) & Phân loại 4M")
            pareto_col, pie_col = st.columns([6, 4])
            
            with pareto_col:
                df_pareto = pd.DataFrame({
                    "Trạm": ["Chưa xác định", "Block 5", "Block 6", "Block 7", "Block 4", "Block 1", "Block 3"],
                    "So_Phut": [2650, 2200, 1500, 900, 750, 500, 400]
                })
                tong_thoi_gian = df_pareto["So_Phut"].sum()
                df_pareto["Phan_Tram_Tich_Luy"] = (df_pareto["So_Phut"].cumsum() / tong_thoi_gian) * 100

                fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
                fig_pareto.add_trace(go.Bar(x=df_pareto["Trạm"], y=df_pareto["So_Phut"], name="Downtime (Phút)", marker_color="#e11d48"), secondary_y=False)
                fig_pareto.add_trace(go.Scatter(x=df_pareto["Trạm"], y=df_pareto["Phan_Tram_Tich_Luy"], name="% Luỹ kế", mode="lines+markers+text", text=df_pareto["Phan_Tram_Tich_Luy"].round(0).astype(str) + "%", textposition="top left", marker=dict(color="#0f766e", size=8), line=dict(width=3)), secondary_y=True)
                fig_pareto.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_pareto, use_container_width=True)

            with pie_col:
                labels = ['Máy móc (Machine)', 'Nguyên liệu (Material)', 'Phương pháp (Method)', 'Chưa phân loại']
                values = [1048, 735, 135, 480]
                colors = ['#dc2626', '#ea580c', '#2563eb', '#94a3b8']
                fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker=dict(colors=colors))])
                fig_pie.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("🔒 **Hạn chế truy cập:** Bạn đang đăng nhập với quyền Tổ Trưởng. Chỉ xem được thông số tổng quan.")

    # ---------------------------------------------------------
    # TRANG 2: QUẢN LÝ TÀI KHOẢN (Chỉ dành cho Admin)
    # ---------------------------------------------------------
    elif selected_menu == "👤 Quản Lý Tài Khoản":
        st.markdown("## ⚙️ QUẢN TRỊ HỆ THỐNG - QUẢN LÝ TÀI KHOẢN")
        st.markdown("---")
        col_list, col_add = st.columns([6, 4])
        with col_list:
            st.subheader("📋 Danh sách tài khoản")
            user_list = []
            for uname, info in st.session_state["USER_DB"].items():
                user_list.append({"Tên đăng nhập": uname, "Họ và Tên": info["name"], "Phân quyền": info["role"]})
            st.dataframe(pd.DataFrame(user_list), use_container_width=True)

        with col_add:
            st.subheader("➕ Cấp tài khoản mới")
            with st.form("add_user_form"):
                new_user = st.text_input("Tên đăng nhập (viết liền không dấu)*")
                new_pass = st.text_input("Mật khẩu*", type="password")
                new_name = st.text_input("Họ và Tên người dùng")
                new_role = st.selectbox("Cấp quyền truy cập", ["Operator", "Manager", "Admin"])
                submitted_user = st.form_submit_button("Tạo tài khoản", use_container_width=True)
                if submitted_user:
                    if new_user == "" or new_pass == "":
                        st.error("Vui lòng điền đủ Tên đăng nhập và Mật khẩu!")
                    elif new_user in st.session_state["USER_DB"]:
                        st.error("Tên đăng nhập này đã tồn tại!")
                    else:
                        st.session_state["USER_DB"][new_user] = {
                            "password": new_pass,
                            "role": new_role,
                            "name": new_name
                        }
                        st.success(f"Đã tạo thành công tài khoản: {new_user}")
                        st.rerun()

    # ---------------------------------------------------------
    # TRANG 3: QUẢN LÝ MÁY MÓC (Chỉ dành cho Admin)
    # ---------------------------------------------------------
    elif selected_menu == "🏭 Quản Lý Máy Móc":
        st.markdown("## ⚙️ QUẢN TRỊ HỆ THỐNG - QUẢN LÝ THIẾT BỊ & MÁY MÓC")
        st.markdown("---")
        col_mlist, col_madd = st.columns([6, 4])
        with col_mlist:
            st.subheader("📋 Danh sách thiết bị")
            st.dataframe(pd.DataFrame(st.session_state["MACHINE_DB"]), use_container_width=True)

        with col_madd:
            st.subheader("➕ Thêm máy mới")
            with st.form("add_machine_form"):
                m_id = st.text_input("Mã máy (VD: M04)*")
                m_name = st.text_input("Tên máy (VD: Máy mài CNC)*")
                m_line = st.selectbox("Thuộc chuyền (Line)", ["G103", "G104", "G111"])
                m_uph = st.number_input("Tốc độ chuẩn - UPH (Sản phẩm/Giờ)", min_value=1, value=100)
                submitted_machine = st.form_submit_button("Thêm máy móc", use_container_width=True)
                if submitted_machine:
                    if m_id == "" or m_name == "":
                        st.error("Vui lòng điền đủ Mã máy và Tên máy!")
                    else:
                        if any(m["id"] == m_id for m in st.session_state["MACHINE_DB"]):
                            st.error("Mã máy này đã tồn tại!")
                        else:
                            st.session_state["MACHINE_DB"].append({
                                "id": m_id,
                                "name": m_name,
                                "line": m_line,
                                "uph": m_uph
                            })
                            st.success("Thêm máy móc thành công!")
                            st.rerun()
