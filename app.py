import os

import httpx
import streamlit as st

API_URL = os.environ.get("API_URL", "http://127.0.0.1:5002")

st.title("Fredagsbarens events")

if "name" not in st.session_state:
    st.session_state["name"] = ""

name = st.sidebar.text_input("Mit navn", key="name")

def event_label(event):
    return f"{event['title']} (#{event['id']})"

with st.form("create_event"):
    event_title = st.text_input("Titel")
    event_date = st.date_input("Dato")
    event_capacity = st.number_input(
        "Antal pladser", min_value=1, value=10, step=1
    )

    submitted = st.form_submit_button("Opret event")

try:
    if submitted and event_date is None:
        st.error("Vælg en dato til eventet.")

    if submitted and event_date is not None:
        response = httpx.post(
            f"{API_URL}/events",
            json={
                "title": event_title,
                "date": event_date.isoformat(),
                "capacity": event_capacity
            },
            timeout=2
        )
        response.raise_for_status()
        st.success("Eventet er oprettet!")

    response = httpx.get(f"{API_URL}/events", timeout=2)
    response.raise_for_status()

    events = response.json()
    rows = []

    for event in events:
        participants_count = len(event["participants"])
        available_places = event["capacity"] - participants_count

        rows.append({
            "Titel": event["title"],
            "Dato": event["date"],
            "Antal tilmeldte": participants_count,
            "Ledige pladser": available_places
        })

    st.dataframe(rows, hide_index=True)

    if events:
        event_labels = []
        for event in events:
            event_labels.append(event_label(event))

        selected_label = st.selectbox("Vælg et event", event_labels)

        for event in events:
            if event_label(event) == selected_label:
                selected_event = event

        st.write("Deltagere:")
        st.write(", ".join(selected_event["participants"]) or "Ingen endnu")

        full = len(selected_event["participants"]) >= selected_event["capacity"]

        if st.button("Tilmeld mig", disabled=full or not name.strip()):
            response = httpx.post(
                f"{API_URL}/events/{selected_event['id']}/signups",
                json={"name": name},
                timeout=2
            )
            response.raise_for_status()
            st.rerun()

        if st.button("Afmeld mig", disabled=not name.strip()):
            response = httpx.delete(
                f"{API_URL}/events/{selected_event['id']}/signups/{name.strip()}",
                timeout=2
            )
            response.raise_for_status()
            st.rerun()

    else:
        st.info("Der er ingen events endnu.")

except httpx.ConnectError:
    st.error("Kan ikke kontakte API'en. Kontrollér, at den kører.")

except httpx.TimeoutException:
    st.error("API'en svarede for langsomt. Prøv igen.")

except httpx.HTTPStatusError as error:
    try:
        message = error.response.json()["error"]
    except (ValueError, KeyError, TypeError):
        message = "API'en returnerede en uventet fejl."

    st.error(message)

except httpx.RequestError:
    st.error("Der opstod en netværksfejl. Prøv igen.")

except ValueError:
    st.error("API'en returnerede et ugyldigt svar. Prøv igen.")
