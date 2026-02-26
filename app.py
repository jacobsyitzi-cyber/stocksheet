import streamlit as st
import pandas as pd

st.set_page_config(page_title="Stock & Pricing Search", layout="wide")

LOW_STOCK_THRESHOLD = 5

# ---------- Sticky Header CSS ----------
st.markdown("""
<style>
div[data-testid="stTextInput"] {
    position: sticky;
    top: 0;
    background-color: white;
    padding-top: 10px;
    padding-bottom: 10px;
    z-index: 999;
}
</style>
""", unsafe_allow_html=True)

st.title("📦 Stock & Pricing Search")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(excel_data.keys())
    selected_sheet = st.sidebar.selectbox("Select Sheet", sheet_names)

    df_original = excel_data[selected_sheet].fillna("")

    total_products = len(df_original)

    df = df_original.copy()

    # ---------- Detect Columns ----------
    stock_columns = [
        col for col in df.columns
        if any(k in col.lower() for k in ["stock", "qty", "quantity", "sync", "westcoast", "td", "ingram"])
    ]

    price_columns = [
        col for col in df.columns
        if any(k in col.lower() for k in ["price", "cost", "rrp", "b2b", "edu", "public"])
    ]

    type_column = None
    for col in df.columns:
        if "type" in col.lower() or "category" in col.lower():
            type_column = col
            break

    brand_column = next((col for col in df.columns if "brand" in col.lower()), None)

    # ---------- Auto Total Stock ----------
    def calculate_total_stock(row):
        total = 0
        for col in stock_columns:
            try:
                total += float(row[col])
            except:
                pass
        return total

    df["Total_Stock_Calc"] = df.apply(calculate_total_stock, axis=1)

    # ---------- Filters ----------
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_query = st.text_input("🔎 Search Products", placeholder="Type to search...")

    with col2:
        if type_column:
            types = ["All"] + sorted(df[type_column].astype(str).unique())
            selected_type = st.selectbox("Product Type", types)
        else:
            selected_type = "All"

    with col3:
        sort_option = st.selectbox(
            "Sort By",
            ["None", "Brand", "Total Stock", "B2B Price", "Product Type"]
        )

    # ---------- Apply Type Filter ----------
    if selected_type != "All" and type_column:
        df = df[df[type_column].astype(str) == selected_type]

    # ---------- Apply Search (Live) ----------
    if search_query:
        words = search_query.lower().split()

        def matches(row):
            row_text = " ".join(str(value).lower() for value in row)
            return all(word in row_text for word in words)

        df = df[df.apply(matches, axis=1)]

    # ---------- Sorting ----------
    if sort_option == "Brand" and brand_column:
        df = df.sort_values(by=brand_column)
    elif sort_option == "Total Stock":
        df = df.sort_values(by="Total_Stock_Calc", ascending=False)
    elif sort_option == "Product Type" and type_column:
        df = df.sort_values(by=type_column)
    elif sort_option == "B2B Price":
        b2b_col = next((col for col in price_columns if "b2b" in col.lower()), None)
        if b2b_col:
            df = df.sort_values(by=b2b_col)

    # ---------- Summary ----------
    st.markdown(f"**Showing {len(df)} of {total_products} products**")
    st.markdown("---")

    # ---------- Display Products ----------
    for _, row in df.iterrows():

        total_stock = row["Total_Stock_Calc"]

        if total_stock == 0:
            status_icon = "🔴 Out of Stock"
        elif total_stock <= LOW_STOCK_THRESHOLD:
            status_icon = "🟠 Low Stock"
        else:
            status_icon = "🟢 In Stock"

        brand = row[brand_column] if brand_column else ""
        product_type = row[type_column] if type_column else ""
        part_number = next((row[col] for col in df.columns if "part" in col.lower()), "")
        description = next((row[col] for col in df.columns if "desc" in col.lower()), "")

        st.markdown(f"""
        **Brand:** {brand}  
        **Product Type:** {product_type}  
        **Part Number:** {part_number}  
        **Description:** {description}  

        📦 **Total Stock:** {int(total_stock)} — {status_icon}
        """)

        b2b_col = next((col for col in price_columns if "b2b" in col.lower()), None)
        if b2b_col:
            st.markdown(f"💰 **B2B Cost Price:** {row[b2b_col]}")

        with st.expander("Expand to show"):
            st.markdown("📦 **Distributor Stock**")
            for col in stock_columns:
                if col != "Total_Stock_Calc":
                    st.markdown(f"{col}: {row[col]}")

            for col in price_columns:
                if b2b_col and col == b2b_col:
                    continue
                st.markdown(f"💰 {col}: {row[col]}")

        st.markdown("---")

else:
    st.info("Upload an Excel file to begin.")
