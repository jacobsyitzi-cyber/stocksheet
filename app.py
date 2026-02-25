import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Stock Search", layout="wide")

# ---------------- CONFIG ----------------
LOW_STOCK_THRESHOLD = 5
PLACEHOLDER_IMAGE = "https://via.placeholder.com/150?text=No+Image"

# ---------------- IMAGE FETCH ----------------
@st.cache_data(show_spinner=False)
def get_product_image(query, access_key):
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 1,
        "client_id": access_key
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data["results"]:
            return data["results"][0]["urls"]["small"]
        else:
            return PLACEHOLDER_IMAGE
    except:
        return PLACEHOLDER_IMAGE

# ---------------- APP ----------------
st.title("📦 Stock & Pricing Search")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(excel_data.keys())
    selected_sheet = st.sidebar.selectbox("Select Sheet", sheet_names)

    df = excel_data[selected_sheet]
    df = df.fillna("")

    # ---------------- PRODUCT TYPE FILTER ----------------
    type_column = None
    for col in df.columns:
        if "type" in col.lower() or "category" in col.lower():
            type_column = col
            break

    if type_column:
        product_types = ["All"] + sorted(df[type_column].astype(str).unique().tolist())
        selected_type = st.selectbox("Filter by Product Type", product_types)
        if selected_type != "All":
            df = df[df[type_column].astype(str) == selected_type]

    # ---------------- SEARCH BAR ----------------
    search_query = st.text_input("🔎 Search Products", placeholder="Example: ipad wifi 256")

    if search_query:
        words = search_query.lower().split()

        def matches(row):
            row_text = " ".join(str(value).lower() for value in row)
            return all(word in row_text for word in words)

        df = df[df.apply(matches, axis=1)]

    st.markdown(f"### {len(df)} Products Found")

    # ---------------- DISPLAY PRODUCTS ----------------
    unsplash_key = st.secrets.get("UNSPLASH_ACCESS_KEY", "")

    for _, row in df.iterrows():

        st.markdown("---")
        col1, col2 = st.columns([1, 3])

        # Image
        with col1:
            product_name = str(row.iloc[0])
            if unsplash_key:
                image_url = get_product_image(product_name, unsplash_key)
            else:
                image_url = PLACEHOLDER_IMAGE
            st.image(image_url, width=120)

        # Details
        with col2:
            for column in df.columns:
                col_lower = column.lower()

                # Price columns
                if any(keyword in col_lower for keyword in ["price", "b2b", "education"]):
                    st.markdown(f"💰 **{column}:** {row[column]}")

                # Stock columns
                elif any(keyword in col_lower for keyword in ["stock", "qty", "quantity"]):
                    try:
                        stock_value = float(row[column])
                        if stock_value <= LOW_STOCK_THRESHOLD:
                            st.markdown(
                                f"<span style='color:red; font-weight:bold;'>📦 {column}: {row[column]}</span>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(f"📦 **{column}:** {row[column]}")
                    except:
                        st.markdown(f"📦 **{column}:** {row[column]}")

                else:
                    st.markdown(f"**{column}:** {row[column]}")

else:
    st.info("Upload an Excel file to begin.")
