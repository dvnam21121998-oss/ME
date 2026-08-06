import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import calendar

# ==========================================
# CẤU HÌNH TRANG
# ==========================================
st.set_page_config(page_title="Dashboard OEE Toàn Diện", layout="wide", initial_sidebar_state="expanded")

ALL_FEATURES = [
    "📊 Dashboard OEE",
    "🏭 Quản Lý Máy Móc",
    "👤 Quản Lý Tài Khoản"
]

# ==========================================
# HÀM HỖ TRỢ HIỂN THỊ DIALOG/MODAL GIỮA MÀN HÌNH
# ==========================================
@st.dialog("🔔 THÔNG BÁO HỆ THỐNG")
def show_popup_message(title, message, icon="ℹ️"):
    st.markdown(f"### {icon} {title}")
    st.write(message)
    if st.button("Đóng", use_container_width=True, type="primary"):
        st.rerun()

# ==========================================
# HÀM HỖ TRỢ XỬ LÝ FILE DỮ LIỆU MẪU
# ==========================================
def load_sample_file_data(uploaded_file):
    """Hàm đọc file excel/csv và trả về DataFrame chuẩn hóa"""
    try:
        filename = uploaded_file.name.lower()
        if filename.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            engine = 'pyxlsb' if filename.endswith('.xlsb') else 'openpyxl'
            df = pd.read_excel(uploaded_file, engine=engine)
        return df
    except Exception as e:
        st.error(f"Lỗi khi đọc file mẫu: {e}")
        return None

def generate_mock_machine_data(machine_obj, start_date, end_date):
    """Tạo dữ liệu phân tích mô phỏng dựa trên Máy cụ thể và khoảng thời gian tìm kiếm"""
    date_range = pd.date_range(start=start_date, end=end_date)
    data = []
    
    seed_val = sum(ord(c) for c in machine_obj["id"]) + int(start_date.strftime("%d%m%Y"))
    np.random.seed(seed_val)
    
    base_uph = machine_obj.get("uph", 1000)
    
    for d in date_range:
        availability = np.random.uniform(80, 98)
        performance = np.random.uniform(85, 99)
        quality = np.random.uniform(95, 99.9)
        oee = (availability * performance * quality) / 10000
        downtime = round(np.random.uniform(10, 120), 1)
        uph = int(base_uph * np.random.uniform(0.85, 1.05))
        
        data.append({
            "Ngày": d.strftime("%Y-%m-%d"),
            "Mã máy": machine_obj["id"],
            "Tên máy": machine_obj["name"],
            "Dây chuyền": machine_obj["line"],
            "Sẵn sàng (%)": round(availability, 1),
            "Hiệu suất (%)": round(performance, 1),
            "Chất lượng (%)": round(quality, 1),
            "OEE (%)": round(oee, 1),
            "Downtime (Phút)": downtime,
            "Sản lượng UPH": uph
        })
    return pd.DataFrame(data)

# ==========================================
# KHỞI TẠO CƠ SỞ DỮ LIỆU (Session State)
# ==========================================
if "USER_DB" not in st.session_state:
    st.session_state["USER_DB"] = {
        "admin": {
            "password": "123",
            "name": "Giám Đốc Nhà Máy",
            "department": "Ban Giám Đốc",
            "position": "Giám Đốc",
            "role": "Admin",
            "allowed_pages": ALL_FEATURES
        },
        "manager": {
            "password": "123",
            "name": "Kỹ Sư IE",
            "department": "Kỹ Thuật (IE)",
            "position": "Trưởng Nhóm IE",
            "role": "Manager",
            "allowed_pages": ["📊 Dashboard OEE"]
        }
    }

if "MACHINE_DB" not in st.session_state:
    st.session_state["MACHINE_DB"] = [
        {
            "id": "M01", 
            "name": "Máy dập Block 1", 
            "line": "G103", 
            "uph": 1200, 
            "url": "http://192.168.1.100/m01", 
            "template_file": "template_oee_g103.xlsx",
            "has_file": True
        },
        {
            "id": "M02", 
            "name": "Máy Test Hipot", 
            "line": "G104", 
            "uph": 800, 
            "url": "http://192.168.1.101/m02", 
            "template_file": "template_oee_g104.csv",
            "has_file": True
        }
    ]

if "selected_menu" not in st.session_state:
    st.session_state["selected_menu"] = "📊 Dashboard OEE"

# ==========================================
# CÁC HÀM ĐĂNG NHẬP / ĐĂNG XUẤT / CHUYỂN TRANG
# ==========================================
def login():
    st.markdown("<h2 style='text-align: center; color: #1e293b;'>🔐 ĐĂNG NHẬP HỆ THỐNG OEE</h2>", unsafe_allow_html=True)
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
                    st.session_state["user_info"] = st.session_state["USER_DB"][username]
                    st.session_state["selected_menu"] = "📊 Dashboard OEE"
                    st.session_state["menu_radio"] = "📊 Dashboard OEE"
                    st.toast("🔔 Đăng nhập thành công!", icon="✅")
                    st.rerun()
                else:
                    st.error("Tên đăng nhập hoặc mật khẩu không chính xác!")

def logout():
    st.session_state["logged_in"] = False
    st.session_state.pop("username", None)
    st.session_state.pop("user_info", None)
    st.session_state["selected_menu"] = "📊 Dashboard OEE"

def go_home():
    st.session_state["selected_menu"] = "📊 Dashboard OEE"
    # Đồng bộ trực tiếp state của menu radio ở sidebar
    st.session_state["menu_radio"] = "📊 Dashboard OEE"

# ==========================================
# GIAO DIỆN CHÍNH KHI ĐÃ ĐĂNG NHẬP
# ==========================================
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
else:
    current_user = st.session_state["user_info"]
    
    # --- SIDEBAR MENU ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2046/2046024.png", width=90)
        st.success(f"👋 **{current_user['name']}**")
        st.info(f"📍 Bộ phận: **{current_user.get('department', 'N/A')}**\n\n💼 Chức vụ: **{current_user.get('position', 'N/A')}**")
        st.markdown("---")
        
        user_pages = current_user.get("allowed_pages", ["📊 Dashboard OEE"])
        if "📊 Dashboard OEE" in user_pages:
            user_pages.remove("📊 Dashboard OEE")
            user_pages.insert(0, "📊 Dashboard OEE")

        if st.session_state["selected_menu"] not in user_pages:
            st.session_state["selected_menu"] = "📊 Dashboard OEE"
            st.session_state["menu_radio"] = "📊 Dashboard OEE"

        selected_menu = st.radio(
            "📌 ĐIỀU HƯỚNG HỆ THỐNG", 
            user_pages, 
            key="menu_radio"
        )
        st.session_state["selected_menu"] = selected_menu
        
        st.markdown("---")
        st.button("🚪 Đăng xuất", on_click=logout, use_container_width=True)

    # Nút Quay về Trang chủ
    top_col1, top_col2 = st.columns([8, 2])
    with top_col2:
        if selected_menu != "📊 Dashboard OEE":
            st.button("🏠 Quay về Trang chủ", on_click=go_home, use_container_width=True)

    # ---------------------------------------------------------
    # TRANG CHỦ: DASHBOARD OEE
    # ---------------------------------------------------------
    if selected_menu == "📊 Dashboard OEE":
        st.markdown("<h1 style='text-align: center; color: #0f172a;'>📊 MANAGEMENT DASHBOARD V2 ACTIONABLE</h1>", unsafe_allow_html=True)
        st.markdown("---")

        # --- THANH TÌM KIẾM CẢI TIẾN: THEO MÃ/TÊN MÁY VÀ DÂY CHUYỀN ---
        st.subheader("🔍 Bộ Lọc Tìm Kiếm & Phân Tích Dữ Liệu")
        
        machine_db = st.session_state["MACHINE_DB"]
        existing_lines = sorted(list(set([m["line"] for m in machine_db if m.get("line")])))
        
        line_options = ["Tất cả Lines"] + existing_lines
        machine_options = ["Tất cả Máy"] + [f"{m['id']} - {m['name']} (Line: {m['line']})" for m in machine_db]

        filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([2.5, 2.5, 2.5, 2.5, 2])

        with filter_col1:
            start_date = st.date_input("Từ ngày", date(2026, 8, 1))
        with filter_col2:
            end_date = st.date_input("Đến ngày", date.today())
        with filter_col3:
            selected_line = st.selectbox("Dây Chuyền (Line)", line_options)
        with filter_col4:
            selected_machine_str = st.selectbox("Mã / Tên Thiết Bị", machine_options)
        with filter_col5:
            st.write("")
            st.write("")
            btn_search = st.button("🔎 Phân tích", use_container_width=True, type="primary")

        # Lọc dữ liệu theo đối tượng chọn
        filtered_machines = machine_db.copy()

        if selected_line != "Tất cả Lines":
            filtered_machines = [m for m in filtered_machines if m["line"] == selected_line]

        if selected_machine_str != "Tất cả Máy":
            selected_m_id = selected_machine_str.split(" - ")[0]
            filtered_machines = [m for m in filtered_machines if m["id"] == selected_m_id]

        target_display_name = selected_machine_str if selected_machine_str != "Tất cả Máy" else (selected_line if selected_line != "Tất cả Lines" else "Toàn Nhà Máy")

        if btn_search:
            show_popup_message("CẬP NHẬT DỮ LIỆU", f"Đã tải thành công dữ liệu phân tích cho: **{target_display_name}**!", icon="📊")

        st.markdown("---")

        # --- SECTION 1: TỔNG QUAN CHỈ SỐ SỨC KHỎE THIẾT BỊ ---
        st.markdown(f"### 01. Equipment Health Overview ({target_display_name} | {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric(label="Downtime Rate", value="12.5%", delta="Mới phát sinh", delta_color="inverse")
        kpi2.metric(label="Availability (Sẵn sàng)", value="87.5%", delta="-12% so kỳ trước", delta_color="normal")
        kpi3.metric(label="MTBF (Chạy TB trước khi hỏng)", value="316 Phút", delta="Tốt", delta_color="normal")
        kpi4.metric(label="MTTR (Thời gian sửa TB)", value="45.1 Phút", delta="+5 Phút", delta_color="inverse")

        st.markdown("---")

        # --- SECTION 2: BIỂU ĐỒ PARETO 80/20 & PHÂN LOẠI 4M ---
        if current_user["role"] in ["Manager", "Admin"]:
            st.markdown("### 02. Pareto Downtime (80/20) & Phân loại Nguyên nhân 4M")
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
            st.info("🔒 **Hạn chế truy cập:** Bạn đang đăng nhập với quyền Operator. Chỉ xem được thông số tổng quan.")

        st.markdown("---")

        # --- SECTION 3: PHÂN TÍCH TỰ ĐỘNG ---
        if filtered_machines:
            st.markdown(f"### 03. Phân Tích Xu Hướng Dữ Liệu Tự Động Từng Máy ({target_display_name})")
            
            all_df_list = []
            for m_item in filtered_machines:
                df_m = generate_mock_machine_data(m_item, start_date, end_date)
                all_df_list.append(df_m)
            
            if all_df_list:
                df_filtered = pd.concat(all_df_list, ignore_index=True)

                col_chart, col_table = st.columns([6, 4])
                with col_chart:
                    fig_line = go.Figure()
                    for m_item in filtered_machines:
                        df_sub = df_filtered[df_filtered["Mã máy"] == m_item["id"]]
                        fig_line.add_trace(go.Scatter(
                            x=df_sub["Ngày"], y=df_sub["OEE (%)"],
                            mode='lines+markers', name=f"{m_item['id']} - {m_item['name']}"
                        ))
                    fig_line.update_layout(title="Xu hướng Chỉ số OEE (%) Theo Ngày Được Lọc", xaxis_title="Ngày", yaxis_title="OEE (%)", hovermode="x unified")
                    st.plotly_chart(fig_line, use_container_width=True)

                with col_table:
                    st.markdown("**📋 Bảng tổng hợp chi tiết dữ liệu máy được chọn:**")
                    st.dataframe(df_filtered[["Ngày", "Mã máy", "Tên máy", "Dây chuyền", "OEE (%)", "Downtime (Phút)", "Sản lượng UPH"]], use_container_width=True, height=320)

            st.markdown("---")

            # SECTION 4: BẢNG TỔNG HỢP CẢ THÁNG
            current_month = start_date.month
            current_year = start_date.year
            _, last_day = calendar.monthrange(current_year, current_month)
            month_start = date(current_year, current_month, 1)
            month_end = date(current_year, current_month, last_day)

            st.markdown(f"### 04. Biểu Đồ & Bảng Tổng Hợp Xu Hướng Cả Tháng {current_month}/{current_year}")

            month_df_list = []
            for m_item in filtered_machines:
                df_m_month = generate_mock_machine_data(m_item, month_start, month_end)
                month_df_list.append(df_m_month)

            if month_df_list:
                df_month = pd.concat(month_df_list, ignore_index=True)

                m_col1, m_col2 = st.columns([6, 4])
                with m_col1:
                    fig_month = make_subplots(specs=[[{"secondary_y": True}]])
                    df_month_avg = df_month.groupby("Ngày")[["OEE (%)", "Downtime (Phút)"]].mean().reset_index()

                    fig_month.add_trace(go.Bar(x=df_month_avg["Ngày"], y=df_month_avg["Downtime (Phút)"], name="Tổng Downtime (Phút)", marker_color="#f43f5e"), secondary_y=False)
                    fig_month.add_trace(go.Scatter(x=df_month_avg["Ngày"], y=df_month_avg["OEE (%)"], name="OEE Trung Bình (%)", mode="lines+markers", line=dict(color="#0284c7", width=3)), secondary_y=True)
                    fig_month.update_layout(title=f"Tổng Quan Downtime & OEE Cả Tháng {current_month}/{current_year}", hovermode="x unified")
                    st.plotly_chart(fig_month, use_container_width=True)

                with m_col2:
                    st.markdown(f"**📊 Bảng chỉ số trung bình theo máy trong tháng {current_month}:**")
                    summary_month = df_month.groupby(["Mã máy", "Tên máy", "Dây chuyền"]).agg({
                        "OEE (%)": "mean",
                        "Sẵn sàng (%)": "mean",
                        "Downtime (Phút)": "sum",
                        "Sản lượng UPH": "mean"
                    }).reset_index().round(1)
                    st.dataframe(summary_month, use_container_width=True, height=320)
        else:
            st.warning("⚠️ Không tìm thấy thiết bị nào phù hợp với bộ lọc đã chọn!")

    # ---------------------------------------------------------
    # TRANG 2: QUẢN LÝ MÁY MÓC
    # ---------------------------------------------------------
    elif selected_menu == "🏭 Quản Lý Máy Móc":
        st.markdown("## ⚙️ QUẢN TRỊ HỆ THỐNG - QUẢN LÝ THIẾT BỊ & MÁY MÓC")
        st.markdown("---")

        tab_m_list, tab_m_add, tab_m_edit_del = st.tabs(["📋 Danh Sách Thiết Bị", "➕ Thêm Thiết Bị Mới", "✏️ Chỉnh Sửa / Xóa Máy"])

        # TAB 1: DANH SÁCH MÁY MÓC
        with tab_m_list:
            if st.session_state["MACHINE_DB"]:
                m_display = []
                for m in st.session_state["MACHINE_DB"]:
                    m_display.append({
                        "Mã máy": m.get("id"),
                        "Tên thiết bị": m.get("name"),
                        "Dây chuyền (Line)": m.get("line"),
                        "UPH (Cơ bản)": m.get("uph"),
                        "Đường dẫn tới máy": m.get("url", "Chưa cấu hình"),
                        "File mẫu dữ liệu chuẩn": m.get("template_file", "Chưa nạp file mẫu")
                    })
                st.dataframe(pd.DataFrame(m_display), use_container_width=True)
            else:
                st.info("Chưa có thiết bị nào trong cơ sở dữ liệu.")

        # TAB 2: THÊM MÁY MÓC MỚI
        with tab_m_add:
            st.subheader("➕ Thêm máy móc & Nạp file dữ liệu mẫu")
            col1, col2 = st.columns(2)
            with col1:
                m_id = st.text_input("Mã máy (VD: M04)*")
                m_name = st.text_input("Tên máy (VD: Máy mài CNC)*")
                m_line = st.text_input("Dây chuyền (Line)*", placeholder="Tự nhập tên Line (VD: G103, Line-A, SMT-1...)")
            with col2:
                m_uph = st.number_input("Tốc độ chuẩn - UPH (Sản phẩm/Giờ)", min_value=1, value=100)
                m_url = st.text_input("Đường dẫn tới máy (URL / IP / Path)", placeholder="http://192.168.1.x/m04")
                template_file = st.file_uploader("📁 Nạp File Mẫu Chuẩn (.csv, .xlsx, .xlsm, .xlsb)", type=["csv", "xlsx", "xlsm", "xlsb"])

            if st.button("💾 Lưu Thiết Bị Mới", use_container_width=True, type="primary"):
                if not m_id or not m_name or not m_line:
                    show_popup_message("LỖI NHẬP DỮ LIỆU", "Vui lòng điền đầy đủ **Mã máy**, **Tên máy** và **Dây chuyền (Line)**!", icon="❌")
                elif any(m["id"] == m_id for m in st.session_state["MACHINE_DB"]):
                    show_popup_message("TRÙNG MÃ MÁY", f"Mã máy `{m_id}` đã tồn tại trên hệ thống!", icon="⚠️")
                else:
                    t_filename = template_file.name if template_file else "Chưa nạp file mẫu"
                    has_f = True if template_file else False
                    
                    st.session_state["MACHINE_DB"].append({
                        "id": m_id,
                        "name": m_name,
                        "line": m_line.strip(),
                        "uph": m_uph,
                        "url": m_url if m_url else "Chưa cấu hình",
                        "template_file": t_filename,
                        "has_file": has_f
                    })
                    show_popup_message("TẠO MỚI THÀNH CÔNG", f"Đã lưu thành công thiết bị **{m_name} ({m_id})** vào Line **{m_line}**!", icon="🎉")

        # TAB 3: CHỈNH SỬA / XÓA MÁY MÓC
        with tab_m_edit_del:
            if st.session_state["MACHINE_DB"]:
                machine_options = [f"{m['id']} - {m['name']}" for m in st.session_state["MACHINE_DB"]]
                selected_m_option = st.selectbox("Chọn máy cần thao tác", machine_options)
                selected_m_id = selected_m_option.split(" - ")[0]
                
                m_idx = next((i for i, m in enumerate(st.session_state["MACHINE_DB"]) if m["id"] == selected_m_id), None)
                cur_m = st.session_state["MACHINE_DB"][m_idx]

                col_e_m, col_d_m = st.columns([7, 3])

                with col_e_m:
                    st.subheader(f"✏️ Cập nhật thông tin máy: {cur_m['id']}")
                    with st.form("form_edit_machine"):
                        e_m_name = st.text_input("Tên máy", value=cur_m.get("name", ""))
                        e_m_line = st.text_input("Dây chuyền (Line)", value=cur_m.get("line", ""))
                        e_m_uph = st.number_input("UPH chuẩn", min_value=1, value=int(cur_m.get("uph", 100)))
                        e_m_url = st.text_input("Đường dẫn tới máy", value=cur_m.get("url", ""))
                        
                        st.info(f"File mẫu chuẩn hiện tại: **{cur_m.get('template_file', 'Chưa có file mẫu')}**")
                        e_template_file = st.file_uploader("Thay đổi File mẫu chuẩn mới (Nếu có)", type=["csv", "xlsx", "xlsm", "xlsb"], key="e_template")

                        if st.form_submit_button("💾 Cập Nhật & Lưu Thay Đổi", use_container_width=True):
                            new_t_filename = e_template_file.name if e_template_file else cur_m.get("template_file", "Chưa có file mẫu")
                            has_f = True if e_template_file or cur_m.get("has_file") else False

                            st.session_state["MACHINE_DB"][m_idx] = {
                                "id": selected_m_id,
                                "name": e_m_name,
                                "line": e_m_line.strip(),
                                "uph": e_m_uph,
                                "url": e_m_url,
                                "template_file": new_t_filename,
                                "has_file": has_f
                            }
                            show_popup_message("CẬP NHẬT THÀNH CÔNG", f"Đã lưu các thay đổi cho thiết bị **{selected_m_id}**!", icon="💾")

                with col_d_m:
                    st.subheader("❌ Xóa thiết bị")
                    st.warning(f"Thao tác này sẽ xóa vĩnh viễn máy **{selected_m_id}** khỏi hệ thống.")
                    if st.button("🗑️ Xóa Thiết Bị", type="primary", use_container_width=True):
                        st.session_state["MACHINE_DB"].pop(m_idx)
                        show_popup_message("ĐÃ XÓA THIẾT BỊ", f"Đã xóa vĩnh viễn máy **{selected_m_id}** khỏi hệ thống!", icon="🗑️")
            else:
                st.info("Chưa có máy nào để chỉnh sửa hoặc xóa.")

    # ---------------------------------------------------------
    # TRANG 3: QUẢN LÝ TÀI KHOẢN
    # ---------------------------------------------------------
    elif selected_menu == "👤 Quản Lý Tài Khoản":
        st.markdown("## ⚙️ QUẢN TRỊ HỆ THỐNG - QUẢN LÝ TÀI KHOẢN")
        st.markdown("---")

        tab_list, tab_add, tab_edit_delete = st.tabs(["📋 Danh Sách Tài Khoản", "➕ Tạo Mới Tài Khoản", "✏️ Chỉnh Sửa / Xóa"])

        # TAB 1: DANH SÁCH
        with tab_list:
            display_data = []
            for uname, uinfo in st.session_state["USER_DB"].items():
                display_data.append({
                    "Tài khoản": uname,
                    "Mật khẩu": "••••••",
                    "Họ và Tên": uinfo.get("name", ""),
                    "Bộ phận": uinfo.get("department", ""),
                    "Chức vụ": uinfo.get("position", ""),
                    "Phân quyền": uinfo.get("role", ""),
                    "Mục được truy cập": ", ".join(uinfo.get("allowed_pages", []))
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)

        # TAB 2: TẠO MỚI TÀI KHOẢN
        with tab_add:
            with st.form("form_add_user"):
                st.subheader("Thêm tài khoản mới vào hệ thống")
                col_a, col_b = st.columns(2)
                with col_a:
                    a_username = st.text_input("Tên tài khoản (viết liền không dấu)*")
                    a_password = st.text_input("Mật khẩu*", type="password")
                    a_fullname = st.text_input("Họ và Tên")
                with col_b:
                    a_dept = st.text_input("Bộ phận", value="Sản Xuất")
                    a_pos = st.text_input("Chức vụ", value="Nhân Viên")
                    a_role = st.selectbox("Cấp độ hệ thống", ["Operator", "Manager", "Admin"])

                st.markdown("**Quyền được truy cập những mục nào trong phần mềm:**")
                a_pages = st.multiselect("Chọn các mục được phép dùng", ALL_FEATURES, default=["📊 Dashboard OEE"])

                btn_add = st.form_submit_button("➕ Tạo Tài Khoản Mới", use_container_width=True)
                if btn_add:
                    if not a_username or not a_password:
                        show_popup_message("LỖI ĐĂNG KÝ", "Vui lòng điền **Tên tài khoản** và **Mật khẩu**!", icon="❌")
                    elif a_username in st.session_state["USER_DB"]:
                        show_popup_message("TÀI KHOẢN ĐÃ TỒN TẠI", f"Tài khoản `{a_username}` đã tồn tại trên hệ thống!", icon="⚠️")
                    else:
                        st.session_state["USER_DB"][a_username] = {
                            "password": a_password,
                            "name": a_fullname,
                            "department": a_dept,
                            "position": a_pos,
                            "role": a_role,
                            "allowed_pages": a_pages
                        }
                        show_popup_message("TẠO TÀI KHOẢN THÀNH CÔNG", f"Đã khởi tạo thành công tài khoản **{a_username}**!", icon="👤")

        # TAB 3: CHỈNH SỬA & XÓA TÀI KHOẢN
        with tab_edit_delete:
            target_user = st.selectbox("Chọn tài khoản cần thao tác", list(st.session_state["USER_DB"].keys()))
            u_data = st.session_state["USER_DB"][target_user]

            col_edit, col_del = st.columns([7, 3])

            with col_edit:
                st.subheader(f"✏️ Cập nhật thông tin: {target_user}")
                with st.form("form_edit_user"):
                    e_password = st.text_input("Mật khẩu mới", value=u_data.get("password", ""))
                    e_fullname = st.text_input("Họ và Tên", value=u_data.get("name", ""))
                    e_dept = st.text_input("Bộ phận", value=u_data.get("department", ""))
                    e_pos = st.text_input("Chức vụ", value=u_data.get("position", ""))
                    
                    role_idx = ["Operator", "Manager", "Admin"].index(u_data.get("role", "Operator")) if u_data.get("role") in ["Operator", "Manager", "Admin"] else 0
                    e_role = st.selectbox("Cấp độ hệ thống", ["Operator", "Manager", "Admin"], index=role_idx)

                    st.markdown("**Quyền được truy cập những mục nào trong phần mềm:**")
                    e_pages = st.multiselect("Chọn các mục được phép dùng", ALL_FEATURES, default=u_data.get("allowed_pages", []))

                    btn_update = st.form_submit_button("💾 Lưu Thay Đổi", use_container_width=True)
                    if btn_update:
                        st.session_state["USER_DB"][target_user] = {
                            "password": e_password,
                            "name": e_fullname,
                            "department": e_dept,
                            "position": e_pos,
                            "role": e_role,
                            "allowed_pages": e_pages
                        }
                        if target_user == st.session_state["username"]:
                            st.session_state["user_info"] = st.session_state["USER_DB"][target_user]
                        show_popup_message("CẬP NHẬT THÀNH CÔNG", f"Đã lưu các thay đổi cho tài khoản **{target_user}**!", icon="💾")

            with col_del:
                st.subheader("❌ Xóa tài khoản")
                st.warning(f"Thao tác này không thể hoàn tác với tài khoản **{target_user}**.")
                if st.button("🗑️ Xóa Tài Khoản", type="primary", use_container_width=True):
                    if target_user == st.session_state["username"]:
                        show_popup_message("KHÔNG THỂ XÓA", "Bạn không thể xóa tài khoản hiện tại đang đăng nhập!", icon="🚫")
                    else:
                        del st.session_state["USER_DB"][target_user]
                        show_popup_message("ĐÃ XÓA TÀI KHOẢN", f"Đã xóa tài khoản **{target_user}** khỏi hệ thống!", icon="🗑️")
