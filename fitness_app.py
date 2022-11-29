import urllib.parse

import streamlit as st
import pandas as pd
import requests


API_BASE = "http://localhost:8000"
API_GET_WORKOUTS = API_BASE + "/workouts"
API_GET_EXERCISES = API_BASE + "/exercises/{workout_id}"
API_CREATE_ENTRY = API_BASE + "/add"
API_GET_LOGS = API_BASE + "/logs"


@st.cache
def get_cached_data(*, url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def log_workout_entry(*, payload, url=API_CREATE_ENTRY):
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def get_workout_logs(**kwargs):
    query_str = urllib.parse.urlencode(kwargs)
    url = API_GET_LOGS + "?" + query_str

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data)
    df = df.drop("id", axis=1)

    # workaround to hide index - https://stackoverflow.com/a/69883754
    data = df.style.hide(axis="index").to_html()
    st.session_state.data = data


st.set_page_config(layout="wide")
st.title("Workout tracker")

data = get_cached_data(url=API_GET_WORKOUTS)
workouts = {row["id"]: row["name"] for row in data}

col1, col2 = st.columns(2)

with col1:
    st.subheader("Add a workout set:")
    workout_id = st.selectbox(
        "Select a workout",
        workouts.keys(),
        key="workout_for_post",
        format_func=lambda x: workouts[x],
    )

    url = API_GET_EXERCISES.format(workout_id=workout_id)
    data = get_cached_data(url=url)
    exercises = {row["id"]: row["name"] for row in data["exercises"]}

    exercise_id = st.selectbox(
        "Select an exercise",
        exercises.keys(),
        key="exercise_for_post",
        format_func=lambda x: exercises[x],
    )

    set_number = st.number_input("Set number:", min_value=1, max_value=6)
    weight = st.slider("Weight lifted:", min_value=5.0, max_value=150.0, step=0.5)
    reps = st.number_input("Reps performed:", min_value=1, max_value=20)
    date_recorded = st.date_input("Date:").strftime("%Y-%m-%d")  # type: ignore

    payload = {
        "workout_id": workout_id,
        "exercise_id": exercise_id,
        "set_number": set_number,
        "weight": weight,
        "reps": reps,
        "date_recorded": date_recorded,
    }
    st.button("Add entry", on_click=log_workout_entry, kwargs={"payload": payload})

with col2:
    st.subheader("Get workout data:")
    workouts = {**{None: "- select -"}, **workouts}
    workout_id = st.selectbox(
        "Select a workout",
        workouts.keys(),
        key="workout_for_get",
        format_func=lambda x: workouts[x],
    )

    if workout_id:
        url = API_GET_EXERCISES.format(workout_id=workout_id)
        data = get_cached_data(url=url)
        exercises = {row["id"]: row["name"] for row in data["exercises"]}

        exercise_id = st.selectbox(
            "Select an exercise",
            exercises.keys(),
            key="exercise_for_get",
            format_func=lambda x: exercises[x],
        )
        kwargs = {"workout_id": workout_id, "exercise_id": exercise_id}

        st.button("Get workout data", on_click=get_workout_logs, kwargs=kwargs)
        data = st.session_state.get("data")
        if data:
            st.write(data, unsafe_allow_html=True)
