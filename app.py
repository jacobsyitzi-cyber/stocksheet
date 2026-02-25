import streamlit as st
import pandas as pd

st.set_page_config(page_title="Stock & Pricing Search", layout="wide")

st.title("📦 Stock & Pricing Search System")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:

    # Read all sheets
    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(excel_data.keys())

    # Sheet selector
    selected_sheet = st.sidebar.selectbox("Select Sheet", sheet_names)
    df = excel_data[selected_sheet]

    df = df.fillna("")

    st.sidebar.markdown("---")
    st.sidebar.header("🔎 Live Search")

    # ---------------- LIVE SEARCH ----------------
    search_query = st.sidebar.text_input(
        "Type to search",
        placeholder="Example: ipad wifi 256"
    )

    # Multi-word partial search
    if search_query:
        words = search_query.lower().split()

        def matches(row):
            row_text = " ".join(str(value).lower() for value in row)
            return all(word in row_text for word in words)

        filtered_df = df[df.apply(matches, axis=1)]
    else:
        filtered_df = df

    st.markdown(f"### 🔍 {len(filtered_df)} Results Found")

    # ---------------- DISPLAY CARDS ----------------
    for _, row in filtered_df.iterrows():

        with st.container():
            st.markdown("---")
            col_left, col_right = st.columns([3, 2])

            # LEFT SIDE - General Info
            with col_left:
                for column in df.columns:
                    if not any(keyword in column.lower() for keyword in ["price", "stock", "qty", "quantity"]):
                        st.markdown(f"**{column}:** {row[column]}")

            # RIGHT SIDE - Pricing & Stock
            with col_right:

                for column in df.columns:

                    col_lower = column.lower()

                    # Price columns (anything with price/b2b/education)
                    if any(keyword in col_lower for keyword in ["price", "b2b", "education"]):
                        st.markdown(f"💰 **{column}:** {row[column]}")

                    # Stock columns
                    if any(keyword in col_lower for keyword in ["stock", "qty", "quantity"]):
                        stock_value = row[column]

                        try:
                            stock_num = float(stock_value)

                            if stock_num <= 5:
                                st.markdown(
                                    f"<span style='color:red; font-weight:bold;'>📦 {column}: {stock_value}</span>",
                                    unsafe_allow_html=True
                                )
                            else:
                                st.markdown(f"📦 **{column}:** {stock_value}")

                        except:
                            st.markdown(f"📦 **{column}:** {stock_value}")

else:
    st.info("Please upload an Excel file to begin.")
