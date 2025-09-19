

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import re

# 1. Data loading and caching
@st.cache
def load_data(csv_path=r"C:\Users\ble\Downloads\metadata_clean.csv"):
    df = pd.read_csv(csv_path)
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

# Bar plot
fig_journals, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y=journal_counts.index, x=journal_counts.values, palette='viridis', ax=ax)
ax.set_title(f'Top {top_n} Journals by Paper Count')
ax.set_xlabel('Number of Papers')
ax.set_ylabel('Journal')
plt.tight_layout()
st.pyplot(fig_journals)

# Pie chart
if st.checkbox('Show pie chart'):
    fig_pie, ax = plt.subplots(figsize=(8, 8))
    journal_counts.plot(kind='pie', autopct='%1.0f%%', ax=ax)
    ax.set_ylabel('')
    ax.set_title(f'Top {top_n} Journals Distribution')
    st.pyplot(fig_pie)

# COVID-19 specific analysis
if st.checkbox('Show COVID-19 specific analysis'):
    st.subheader("COVID-19 Specific Analysis")
    
    # Filter for COVID-19 related papers
    mask = (
        filtered['title'].str.contains('covid', case=False, na=False) |
        filtered['abstract'].str.contains('covid', case=False, na=False)
    )
    covid_journals = filtered[mask]['journal'].value_counts().head(10)
    
    # COVID-19 journals bar plot
    fig_covid, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(y=covid_journals.index, x=covid_journals.values, palette='viridis', ax=ax)
    ax.set_title('Top 10 Journals for COVID-19 Research')
    ax.set_xlabel('Number of Papers')
    ax.set_ylabel('Journal')
    plt.tight_layout()
    st.pyplot(fig_covid)
    
    # Word frequency analysis
    st.subheader("Most Frequent Words in Titles")
    titles = filtered['title'].dropna().astype(str).str.lower()
    all_words = titles.str.findall(r'\b\w+\b').explode()
    all_words = all_words[all_words.str.len() > 2]  # Remove short words
    word_counts = Counter(all_words)
    common_words = word_counts.most_common(20)
    
    words, counts = zip(*common_words)
    fig_words, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=counts, y=words, palette='viridis', ax=ax)
    ax.set_title('Top 20 Words in Titles')
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Words')
    plt.tight_layout()
    st.pyplot(fig_words)

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

