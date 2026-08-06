import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date

# ==========================================
# CẤU HÌNH TRANG
# ==========================================
st.set_page_config(page_title="Dashboard OEE Toàn Diện", layout="wide", initial_sidebar_state="expanded")

# Danh sách tất cả tính năng trong hệ thống
ALL_FEATURES = [
    "📊 Dashboard OEE",
    "🏭 Quản Lý Máy Móc",
    "👤 Quản Lý Tài Khoản"
]

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
        },
        "operator": {
            "password": "123",
            "name": "Tổ Trưởng Line G103",
            "department": "Sản Xuất",
            "position": "Tổ Trưởng",
            "role": "Operator",
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
            "template_file": "template_oee_m01.xlsx"
        },
        {
            "id": "M02", 
            "name": "Máy Test Hipot", 
            "line": "G103", 
            "uph": 800, 
            "url": "http://192.168.1.101/m02", 
            "template_file": "template_oee_m02.csv"
        }
    ]

# Mặc định Trang chủ luôn là Dashboard OEE
if "selected_menu" not in st.session_state:
    st.session_state["selected_menu"] = "📊 Dashboard OEE"

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
                    st.session_state["user_info"] = st.session_state["USER_DB"][username]
                    st.session_state["selected_menu"] = "📊 Dashboard OEE"  # Reset về trang chủ khi đăng nhập
                    st.rerun()
                else:
                    st.error("Tên đăng nhập hoặc mật khẩu không chính xác!")

def logout():
    st.session_state["logged_in"] = False
    st.session_state.pop("username", None)
    st.session_state.pop("user_info", None)
    st.session_state["selected_menu"] = "📊 Dashboard OEE"
    st.rerun()

def go_home():
    st.session_state["selected_menu"] = "📊 Dashboard OEE"
    st.rerun()

# ==========================================
# GIAO DIỆN CHÍNH KHI ĐÃ ĐĂNG NHẬP
# ==========================================
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
else:
    current_user = st.session_state["user_info"]
    
    # --- SIDEBAR MENU ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2046/2046024.png", width=100)
        st.success(f"👋 **{current_user['name']}**")
        st.info(f"📍 Bộ phận: **{current_user.get('department', 'N/A')}**\n\n💼 Chức vụ: **{current_user.get('position', 'N/A')}**")
        st.markdown("---")
        
        user_pages = current_user.get("allowed_pages", ["📊 Dashboard OEE"])
        
        # Đảm bảo Dashboard OEE luôn đứng đầu danh sách
        if "📊 Dashboard OEE" in user_pages:
            user_pages.remove("📊 Dashboard OEE")
            user_pages.insert(0, "📊 Dashboard OEE")

        if st.session_state["selected_menu"] not in user_pages:
            st.session_state["selected_menu"] = "📊 Dashboard OEE"
            
        selected_menu = st.radio(
            "📌 ĐIỀU HƯỚNG HỆ THỐNG", 
            user_pages, 
            index=user_pages.index(st.session_state["selected_menu"]) if st.session_state["selected_menu"] in user_pages else 0,
            key="menu_radio"
        )
        st.session_state["selected_menu"] = selected_menu
        
        st.markdown("---")
        st.button("Đăng xuất", on_click=logout, use_container_width=True)

    # Nút Quay về Trang chủ dùng chung trên đầu màn hình
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

        # --- THANH TÌM KIẾM THEO NGÀY THÁNG VÀ SỐ LINE ---
        st.subheader("🔍 Bộ Lọc Tìm Kiếm Dữ Liệu")
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([3, 3, 3, 2])
        
        with filter_col1:
            start_date = st.date_input("Từ ngày", date(2026, 1, 1))
        with filter_col2:
            end_date = st.date_input("Đến ngày", date.today())
        with filter_col3:
            selected_line = st.selectbox("Chọn Số Chuyền (Line)", ["Tất cả Lines", "G103", "G104", "G111"])
        with filter_col4:
            st.write("") # Căn chỉnh lề
            st.write("")
            btn_search = st.button("🔎 Tìm kiếm", use_container_width=True)

        st.markdown("---")

        st.markdown(f"### 01. Equipment Health Overview ({selected_line} | {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric(label="Downtime Rate", value="12.5%", delta="Mới phát sinh", delta_color="inverse")
        kpi2.metric(label="Availability (Sẵn sàng)", value="87.5%", delta="-12% so kỳ trước", delta_color="normal")
        kpi3.metric(label="MTBF (Chạy TB trước khi hỏng)", value="316 Phút", delta="Tốt", delta_color="normal")
        kpi4.metric(label="MTTR (Thời gian sửa TB)", value="45.1 Phút", delta="+5 Phút", delta_color="inverse")

        st.markdown("---")

        if current_user["role"] in ["Manager", "Admin"]:
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
    # TRANG 2: QUẢN LÝ MÁY MÓC (FILE MẪU CHUẨN ĐỂ PHÂN TÍCH)
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
                        "Chuyền (Line)": m.get("line"),
                        "UPH (Cơ bản)": m.get("uph"),
                        "Đường dẫn tới máy": m.get("url", "Chưa cấu hình"),
                        "File mẫu dữ liệu chuẩn": m.get("template_file", "Chưa nạp file mẫu")
                    })
                st.dataframe(pd.DataFrame(m_display), use_container_width=True)
            else:
                st.info("Chưa có thiết bị nào trong cơ sở dữ liệu.")

        # TAB 2: THÊM MÁY MÓC MỚI VÀ FILE MẪU CHUẨN
        with tab_m_add:
            st.subheader("➕ Thêm máy móc & File dữ liệu mẫu để phần mềm phân tích")
            col1, col2 = st.columns(2)
            with col1:
                m_id = st.text_input("Mã máy (VD: M04)*")
                m_name = st.text_input("Tên máy (VD: Máy mài CNC)*")
                m_line = st.selectbox("Thuộc chuyền (Line)", ["G103", "G104", "G111"])
            with col2:
                m_uph = st.number_input("Tốc độ chuẩn - UPH (Sản phẩm/Giờ)", min_value=1, value=100)
                m_url = st.text_input("Đường dẫn tới máy (URL / IP / Path)", placeholder="http://192.168.1.x/m04")
                template_file = st.file_uploader("📁 Nạp File Mẫu Chuẩn (.csv, .xlsx, .xlsm, .xlsb)", type=["csv", "xlsx", "xlsm", "xlsb"])

            st.caption("💡 *Phần mềm sẽ sử dụng cấu trúc các cột trong file mẫu này để tự động đọc và trích xuất dữ liệu phân tích OEE.*")

            if st.button("💾 Lưu Thiết Bị & File Mẫu", use_container_width=True):
                if not m_id or not m_name:
                    st.error("Vui lòng điền đầy đủ Mã máy và Tên máy!")
                elif any(m["id"] == m_id for m in st.session_state["MACHINE_DB"]):
                    st.error(f"Mã máy `{m_id}` đã tồn tại!")
                else:
                    t_filename = template_file.name if template_file else "Chưa nạp file mẫu"
                    st.session_state["MACHINE_DB"].append({
                        "id": m_id,
                        "name": m_name,
                        "line": m_line,
                        "uph": m_uph,
                        "url": m_url if m_url else "Chưa cấu hình",
                        "template_file": t_filename
                    })
                    st.success(f"Thêm thành công thiết bị `{m_name}` ({m_id}) cùng File mẫu chuẩn!")
                    st.rerun()

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
                        
                        line_list = ["G103", "G104", "G111"]
                        l_idx = line_list.index(cur_m.get("line")) if cur_m.get("line") in line_list else 0
                        e_m_line = st.selectbox("Chuyền (Line)", line_list, index=l_idx)
                        
                        e_m_uph = st.number_input("UPH chuẩn", min_value=1, value=int(cur_m.get("uph", 100)))
                        e_m_url = st.text_input("Đường dẫn tới máy", value=cur_m.get("url", ""))
                        
                        st.info(f"File mẫu chuẩn hiện tại: **{cur_m.get('template_file', 'Chưa có file mẫu')}**")
                        e_template_file = st.file_uploader("Thay đổi File mẫu chuẩn mới (Nếu có)", type=["csv", "xlsx", "xlsm", "xlsb"], key="e_template")

                        if st.form_submit_button("💾 Cập Nhật Thiết Bị", use_container_width=True):
                            new_t_filename = e_template_file.name if e_template_file else cur_m.get("template_file", "Chưa có file mẫu")
                            st.session_state["MACHINE_DB"][m_idx] = {
                                "id": selected_m_id,
                                "name": e_m_name,
                                "line": e_m_line,
                                "uph": e_m_uph,
                                "url": e_m_url,
                                "template_file": new_t_filename
                            }
                            st.success(f"Đã cập nhật thiết bị `{selected_m_id}` thành công!")
                            st.rerun()

                with col_d_m:
                    st.subheader("❌ Xóa thiết bị")
                    st.warning(f"Thao tác này sẽ xóa vĩnh viễn máy **{selected_m_id}** khỏi hệ thống.")
                    if st.button("🗑️ Xóa Thiết Bị", type="primary", use_container_width=True):
                        st.session_state["MACHINE_DB"].pop(m_idx)
                        st.success(f"Đã xóa thành công máy `{selected_m_id}`!")
                        st.rerun()
            else:
                st.info("Chưa có máy nào để chỉnh sửa hoặc xóa.")

    # ---------------------------------------------------------
    # TRANG 3: QUẢN LÝ TÀI KHOẢN (CÓ THÊM / SỬA / XÓA)
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

        # TAB 2: TẠO MỚI
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
                        st.error("Vui lòng điền Tên tài khoản và Mật khẩu!")
                    elif a_username in st.session_state["USER_DB"]:
                        st.error("Tài khoản này đã tồn tại trên hệ thống!")
                    else:
                        st.session_state["USER_DB"][a_username] = {
                            "password": a_password,
                            "name": a_fullname,
                            "department": a_dept,
                            "position": a_pos,
                            "role": a_role,
                            "allowed_pages": a_pages
                        }
                        st.success(f"Tạo thành công tài khoản `{a_username}`!")
                        st.rerun()

        # TAB 3: CHỈNH SỬA & XÓA
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
                        st.success(f"Đã cập nhật tài khoản `{target_user}` thành công!")
                        st.rerun()

            with col_del:
                st.subheader("❌ Xóa tài khoản")
                st.warning(f"Thao tác này không thể hoàn tác với tài khoản **{target_user}**.")
                if st.button("🗑️ Xóa Tài Khoản", type="primary", use_container_width=True):
                    if target_user == st.session_state["username"]:
                        st.error("Bạn không thể xóa tài khoản hiện tại đang đăng nhập!")
                    else:
                        del st.session_state["USER_DB"][target_user]
                        st.success(f"Đã xóa tài khoản `{target_user}`!")
                        st.rerun()
