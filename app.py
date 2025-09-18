import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 1. Data loading and caching
@st.cache
def load_data(path='/content/metadata_clean.csv'):
    df = pd.read_csv(path)
    df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
    df['year'] = df['publish_time'].dt.year
    return df

df = load_data()

# 2. Page layout
st.title("📊 Research Publications Dashboard")
st.markdown("""
Explore publication trends, top journals, and title word-clouds.  
Use the sidebar to filter by year and journal.
""")

# 3. Interactive filters
st.sidebar.header("🔍 Filters")
min_year, max_year = int(df['year'].min()), int(df['year'].max())
year_range = st.sidebar.slider(
    "Publication Year Range",
    min_year, max_year,
    (min_year, max_year)
)

journals = ["All"] + sorted(df['journal'].dropna().unique().tolist())
selected_journal = st.sidebar.selectbox("Journal", journals)

# 4. Data subsetting
mask = df['year'].between(year_range[0], year_range[1])
if selected_journal != "All":
    mask &= df['journal'] == selected_journal
filtered = df[mask]

# 5. Visualizations

## 5.1 Publications Over Time
st.subheader("Publications Over Time")
year_counts = filtered['year'].value_counts().sort_index()
fig1, ax1 = plt.subplots()
ax1.bar(year_counts.index, year_counts.values, color='skyblue')
ax1.set_xlabel("Year")
ax1.set_ylabel("Number of Papers")
ax1.set_title("Papers by Year")
st.pyplot(fig1)

## 5.2 Top Journals
st.subheader("Top Journals")
top_n = st.slider("Show Top N Journals", 5, 20, 10)
journal_counts = filtered['journal'].value_counts().head(top_n)
st.bar_chart(journal_counts)

## 5.3 Word Cloud of Titles
st.subheader("Title Word Cloud")
text = " ".join(filtered['title'].dropna().astype(str))
wc = WordCloud(width=800, height=400, background_color='white')\
       .generate(text)
fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.imshow(wc, interpolation='bilinear')
ax2.axis('off')
st.pyplot(fig2)

# 6. Sample of the data
st.subheader("Sample Data")
st.dataframe(filtered.head(10))
