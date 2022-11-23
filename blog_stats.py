import collections
import datetime

import streamlit as st
import pandas as pd
import requests

PYBITES_ARTICLES = "https://codechalleng.es/api/articles/"


@st.cache
def get_articles():
    response = requests.get(PYBITES_ARTICLES)
    response.raise_for_status()
    return response.json()


def group_tags_by_year(df):
    """
    Should be able to do with pandas but not sure how, this is easier.
    """
    tags = collections.defaultdict(list)
    for idx, row in df.iterrows():
        tags[row.year].extend(
            [tag.lower() for tag in row.tags.split(", ")]
        )
    return {
        year: collections.Counter(elements)
        for year, elements in sorted(tags.items())
    }


st.title('Pybites blog analysis')

data = get_articles()
df = pd.DataFrame(data)
df["year"] = df.publish_date.str[:4]

article_df = pd.DataFrame(
    df.groupby(['year']).count()['title'])
article_df.columns = ['Articles published']


def get_number_of_articles(df, year):
    return len(df.loc[df['year'] == str(year)])


col1, col2 = st.columns([4, 1])

with col1:
    st.line_chart(article_df)

with col2:
    this_year = datetime.date.today().year
    last_year = this_year - 1
    articles_this_year = get_number_of_articles(df, this_year)
    articles_last_year = get_number_of_articles(df, this_year - 1)
    st.metric(
        label="Articles this year",
        value=articles_this_year,
        delta=articles_this_year-articles_last_year
    )


def get_year_tags(year, year_tags, num_most_common=5):
    """
    How to convert Counter to df - https://stackoverflow.com/a/31111248
    """
    df = pd.DataFrame.from_dict(
        dict(year_tags.most_common(num_most_common)),
        orient='index'
    )
    df = df.rename(columns={0: year})
    return df


st.subheader("Most used tags over the years")

tags = group_tags_by_year(df)
cols = st.columns(len(tags))
for year, col in zip(tags, cols):
    df = get_year_tags(year, tags[year])
    with col:
        st.bar_chart(df)
