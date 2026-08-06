import streamlit as st

import pandas as pd

# Cấu hình trang web rộng ra

st.set_page_config(page_title="Dashboard OEE", layout="wide")

st.title("📊 Hệ Thống Quản Lý OEE Nhà Máy")

# 1. Dữ liệu mô phỏng KPI

oee_data = {"OEE": 82.5, "Availability": 87.0, "Performance": 94.2, "Quality": 98.1}

# 2. Hiển thị các khối KPI (Tự động chia làm 4 cột rất đẹp)

col1, col2, col3, col4 = st.columns(4)

col1.metric(label="OEE Tổng Hệ Thống", value=f"{oee_data['OEE']}%")

col2.metric(label="Mức độ Sẵn sàng (A)", value=f"{oee_data['Availability']}%", delta="-12% so với tuần trước")

col3.metric(label="Hiệu suất (P)", value=f"{oee_data['Performance']}%")

col4.metric(label="Chất lượng (Q)", value=f"{oee_data['Quality']}%")

st.markdown("---") # Đường kẻ ngang

# 3. Dữ liệu thời gian chết (Downtime)

st.subheader("Phân tích Top Nguyên Nhân Dừng Máy (Downtime)")

downtime_data = pd.DataFrame({

    "Lý do dừng máy": ["Kẹt phôi / Kẹt máy", "Chờ nguyên liệu", "Hỏng cảm biến", "Vệ sinh đầu ca", "Chờ QC kiểm tra"],

    "Số phút": [150, 90, 60, 40, 25]

})

# 4. Vẽ biểu đồ bằng tính năng có sẵn của Streamlit

st.bar_chart(data=downtime_data, x="Lý do dừng máy", y="Số phút", color="#e11d48")
 
