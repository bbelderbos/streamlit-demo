import os

import streamlit as st
import pandas as pd
import requests

DEBUG = bool(os.environ.get("DEBUG", False))
DOMAIN = "http://localhost:8000" if DEBUG else "https://pybitesbooks.com"
BOOKS_API_URL = DOMAIN + "/api/stats/{username}"
COMPLETED = "c"


@st.cache
def get_books_data(username):
    url = BOOKS_API_URL.format(username=username)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


st.title('How much are we reading?')

username = st.text_input('Pybites Books username')
if username:
    data = get_books_data(username)
    if not data:
        st.write(f"No data found for username {username}")
        st.stop()

    df = pd.DataFrame(data)
    # st.write(df.head())

    df = df.loc[df['status'] == COMPLETED]
    df["year"] = df.completed.str[:4]

    df_grouped = pd.DataFrame(
        df.groupby(['year']).count()['bookid'])
    df_grouped.columns = ['Books read']

    st.bar_chart(df_grouped)
