import streamlit as st
import pandas as pd

st.set_page_config(page_title="Product Recommendation", layout="wide")

# ---------- Styles ----------
st.markdown(
    """
    <style>
    /* Khoảng cách cho Hero section */
    .hero {
        padding-bottom: 1.5rem;
        text-align: center;
    }
    
    /* Tạo dải màu gradient cho tiêu đề chính */
    .hero h1 {
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF904B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    /* Style chung cho Card */
    .soft-card, .product-card {
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }

    /* Thêm viền màu cho phần Summary */
    .soft-card {
        border-top: 4px solid #FF4B4B;
    }

    /* Hiệu ứng nổi lên khi hover cho Thẻ sản phẩm */
    .product-card {
        border-top: 4px solid #4CAF50;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }

    .soft-card *, .product-card * {
        color: var(--text-color) !important;
    }

    .muted {
        opacity: 0.7;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    /* Style riêng cho các Tag xếp hạng Vàng, Bạc, Đồng */
    .tag {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .tag-1 { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: #000 !important; } /* Vàng */
    .tag-2 { background: linear-gradient(135deg, #E0E0E0 0%, #9E9E9E 100%); color: #000 !important; } /* Bạc */
    .tag-3 { background: linear-gradient(135deg, #FF9A8B 0%, #FF6A88 100%); color: #fff !important; } /* Đồng/Đỏ nhạt */
    
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero">
      <h1>🛍️ Customer Product Recommendation</h1>
      <p style="opacity: 0.8; font-size: 1.1rem;">Enter a Customer ID to detect their group and uncover top personalized product picks.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- Load data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("Data/recommendations.csv")
    
    # Xử lý chuỗi: xóa khoảng trắng và xóa đuôi .0 (nếu có) bằng regex
    df["CustomerID"] = df["CustomerID"].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    df["cluster"] = df["cluster"].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    return df

rec_df = load_data()
all_customer_ids = sorted(rec_df["CustomerID"].unique().tolist())

# ---------- Sidebar ----------
st.sidebar.header("🔍 Lookup")
customer_input = st.sidebar.text_input(
    "Customer ID",
    placeholder="e.g. 17850"
).strip()

st.sidebar.caption("Tip: leave empty and pick from the list below.")
selected_customer = st.sidebar.selectbox(
    "Quick pick Customer ID",
    options=[""] + all_customer_ids
)

# Input priority: typed ID first, fallback to quick pick
customer_id = customer_input if customer_input else selected_customer

if not customer_id:
    st.info("👋 Enter or pick a Customer ID from the sidebar to view recommendations.")
    st.stop()

# ---------- Query ----------
row = rec_df[rec_df["CustomerID"] == customer_id].head(1)

if row.empty:
    st.warning(f"⚠️ No recommendation found for Customer ID: {customer_id}")
    st.stop()

group_value = row.iloc[0]["cluster"]

# ---------- Summary ----------
c1, c2 = st.columns([1, 1])
with c1:
    st.markdown(
        f"""
        <div class="soft-card">
            <div class="muted">👤 Customer ID</div>
            <h2 style="margin:0;">{customer_id}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
with c2:
    st.markdown(
        f"""
        <div class="soft-card">
            <div class="muted">🏷️ Detected Group</div>
            <h2 style="margin:0;">Group {group_value}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("### ✨ Top Recommended Products")

# ---------- Product cards ----------
products = []
for i in [1, 2, 3]:
    sc_col = f"StockCode{i}"
    ds_col = f"Description{i}"
    stock = row.iloc[0].get(sc_col, None)
    desc = row.iloc[0].get(ds_col, None)
    if pd.notna(stock) and pd.notna(desc):
        products.append({"StockCode": stock, "Description": desc})

if not products:
    st.info("This customer does not have complete recommendation items yet.")
else:
    cols = st.columns(3)
    for idx, product in enumerate(products):
        # Chọn màu tag (1, 2, hoặc 3)
        tag_class = f"tag-{idx + 1}"
        
        with cols[idx]:
            st.markdown(
                f"""
                <div class="product-card">
                    <div class="tag {tag_class}">🏆 Choice #{idx + 1}</div>
                    <div style="margin-bottom: 5px;"><b>📦 StockCode:</b> {product["StockCode"]}</div>
                    <div><b>📝 Description:</b><br>{product["Description"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("<br>", unsafe_allow_html=True) # Khoảng trắng tạo độ thở cho UI

# ---------- Sample table ----------
with st.expander("📊 View sample recommendations"):
    show_df = rec_df.rename(columns={"cluster": "Group"})
    st.dataframe(show_df.sample(min(20, len(show_df))), use_container_width=True)

# ---------- Download ----------
export_df = rec_df[rec_df["CustomerID"] == customer_id].rename(columns={"cluster": "Group"})
csv_data = export_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Download this customer's recommendations (CSV)",
    data=csv_data,
    file_name=f"recommendations_{customer_id}.csv",
    mime="text/csv",
    use_container_width=True
)