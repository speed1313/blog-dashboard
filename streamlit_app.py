import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Blog Post View Rankings Over the Past Year',
    page_icon=':bar_chart:',
)


st.header("Blog Post View Rankings Over the Past Year", divider='gray')



df = pd.read_csv('ranking.csv')

cols = st.columns(3)

with cols[0]:
    st.write('Rank')
with cols[1]:
    st.write('Page Path')
with cols[2]:
    st.write('Views')

for i, row in df.iterrows():
    with cols[0]:
        st.markdown(f'{i+1}')
    with cols[1]:
        pagepath = row['pagePath']
        st.write(f'[{pagepath}](https://speed1313.github.io/posts/{pagepath})')
    with cols[2]:
        st.markdown(int(row['screenPageViews']))


