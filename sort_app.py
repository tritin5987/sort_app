import pandas as pd
import streamlit as st
from io import BytesIO


st.title("📊 App Sort & Filter Dữ Liệu Excel")

uploaded_file = st.file_uploader("Chọn file Excel", type=["xlsx"])

if uploaded_file:
    # Đọc thô để xem trước
    df_raw = pd.read_excel(uploaded_file, header=None)
    st.subheader("Xem vài dòng đầu tiên (chưa set header)")
    st.dataframe(df_raw.head(10), use_container_width=True)

    # Chọn dòng làm header
    header_row = st.number_input(
        "Chọn dòng làm tiêu đề (Excel: dòng 1 = 0)",
        min_value=0,
        max_value=len(df_raw) - 1,
        value=4
    )

    # Đọc lại với header đã chọn
    df = pd.read_excel(uploaded_file, header=header_row)
    st.subheader("Dữ liệu sau khi chọn header")
    st.dataframe(df, use_container_width=True)

    # Sort (tự nhận diện ngày / số / chữ)
    sort_col = st.selectbox("Chọn cột để sort", df.columns)
    order = st.radio("Chiều sắp xếp", ["Tăng dần (A-Z)", "Giảm dần (Z-A)"])

    col = df[sort_col]

    parsed_date = pd.to_datetime(
        col,
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce"
    )

    if parsed_date.notna().sum() > 0:
        df["_sort_key"] = parsed_date
    else:
        df["_sort_key"] = col

    sorted_df = df.sort_values(
        by="_sort_key",
        ascending=(order == "Tăng dần (A-Z)")
    ).drop(columns="_sort_key")

    # Filter
    filter_col = st.selectbox("Chọn cột để lọc", df.columns)
    unique_values = sorted_df[filter_col].dropna().unique().tolist()
    selected_values = st.multiselect(
        "Chọn giá trị cần hiển thị",
        unique_values,
        default=unique_values
    )

    filtered_df = sorted_df[sorted_df[filter_col].isin(selected_values)]

    st.subheader("Kết quả sau khi sort + filter")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    # Xuất Excel
    buffer = BytesIO()
    filtered_df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    st.download_button(
        "📥 Tải file Excel sau khi lọc",
        data=buffer,
        file_name="filtered_sorted_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
