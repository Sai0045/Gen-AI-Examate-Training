
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

# Add the project root so Python can find the backend app package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT_STR = str(PROJECT_ROOT)

# Keep the project root before the ui directory to avoid
# confusing ui/app.py with the backend app package.
while PROJECT_ROOT_STR in sys.path:
    sys.path.remove(PROJECT_ROOT_STR)

sys.path.insert(0, PROJECT_ROOT_STR)

import requests
import streamlit as st

from app.tools import vaccine_due_dates
from ui.storage import (
    get_completed_doses,
    init_db,
    save_dose_status,
    save_feedback,
)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="TeekaTimer",
    page_icon="💉",
    layout="wide"
)

API_URL = os.getenv(
    "TEEKATIMER_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

init_db()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_agent" not in st.session_state:
    st.session_state.pending_agent = None


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def get_citations(data):
    citations = data.get("citations", [])

    if not citations and isinstance(data.get("result"), dict):
        citations = data["result"].get("citations", [])

    return citations or []


def format_agent_result(data):
    result = data.get("result", data)

    if isinstance(result, dict):
        answer = (
            result.get("answer")
            or result.get("response")
            or result.get("message")
        )

        if answer:
            return str(answer)

        return json.dumps(result, indent=2, ensure_ascii=False)

    return str(result)


def show_citations(citations):
    if not citations:
        return

    with st.expander("📚 View sources and citations"):
        for citation in citations:
            if isinstance(citation, dict):
                title = (
                    citation.get("title")
                    or citation.get("source")
                    or citation.get("filename")
                    or "Source"
                )

                page = (
                    citation.get("page")
                    or citation.get("page_number")
                )

                st.write(f"**{title}**")

                if page is not None:
                    st.caption(f"Page: {page}")
            else:
                st.write(citation)


def persist_dose(dob, record_id, dose_number, widget_key):
    is_done = bool(st.session_state[widget_key])

    save_dose_status(
        date_of_birth=dob,
        record_id=record_id,
        dose_number=dose_number,
        is_done=is_done
    )


def get_status_color(status):
    colors = {
        "Done": "#198754",
        "Due this week": "#fd7e14",
        "Overdue": "#dc3545",
        "Too late": "#8b0000",
        "Upcoming": "#0d6efd",
    }

    return colors.get(status, "#6c757d")


def show_status(status):
    color = get_status_color(status)

    st.markdown(
        f"""
        <span style="
            background-color:{color};
            color:white;
            padding:4px 10px;
            border-radius:12px;
            font-size:12px;
            font-weight:600;">
            {status}
        </span>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("💉 TeekaTimer")
st.subheader("Your baby's vaccination assistant")

st.write(
    "Ask questions about the official MoHFW immunization "
    "schedule and keep track of your baby's vaccination calendar."
)


# --------------------------------------------------
# Backend connection check
# --------------------------------------------------

connected = False
status_message = None

for attempt in range(3):
    try:
        health_response = requests.get(
            f"{API_URL}/health",
            timeout=20
        )

        if health_response.ok:
            connected = True
            st.success("Backend connected")
            break

        if health_response.status_code not in [429, 502, 503, 504]:
            status_message = (
                f"Backend responded with status code: "
                f"{health_response.status_code}"
            )
            break

    except requests.RequestException:
        pass

    if attempt < 2:
        time.sleep(2)

if not connected:
    if status_message:
        st.warning(status_message)
    else:
        st.warning(
            "Backend is currently unavailable. "
            "Please wait a moment and refresh the page."
        )

    st.caption(f"Backend URL: {API_URL}")


# --------------------------------------------------
# Chat section
# --------------------------------------------------

st.divider()
st.header("💬 Vaccination Assistant")

mode = st.radio(
    "Choose assistant mode:",
    ["RAG (/ask)", "Agent (/agent)"],
    horizontal=True
)

selected_mode = "RAG" if mode.startswith("RAG") else "Agent"

# Display previous conversation
for index, message in enumerate(st.session_state.messages):

    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message["role"] == "assistant":

            show_citations(message.get("citations", []))

            if message.get("note"):
                st.caption(message["note"])

            feedback = message.get("feedback")

            if feedback is None and message.get("question"):
                col1, col2, col3 = st.columns([1, 1, 8])

                with col1:
                    if st.button(
                        "👍",
                        key=f"feedback_up_{index}"
                    ):
                        save_feedback(
                            message["question"],
                            message["content"],
                            1,
                            message.get("mode", "RAG")
                        )

                        message["feedback"] = 1
                        st.rerun()

                with col2:
                    if st.button(
                        "👎",
                        key=f"feedback_down_{index}"
                    ):
                        save_feedback(
                            message["question"],
                            message["content"],
                            -1,
                            message.get("mode", "RAG")
                        )

                        message["feedback"] = -1
                        st.rerun()

            elif feedback is not None:
                st.caption("Thank you for your feedback!")


# --------------------------------------------------
# Handle new question
# --------------------------------------------------

if prompt := st.chat_input("Ask about baby vaccinations..."):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.spinner("Preparing your answer..."):

        try:
            if selected_mode == "RAG":

                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": prompt,
                        "k": 6
                    },
                    timeout=90
                )

                response.raise_for_status()
                data = response.json()

                answer = data.get(
                    "answer",
                    "I don't know."
                )

                citations = get_citations(data)

                note = data.get("note")

            else:

                response = requests.post(
                    f"{API_URL}/agent",
                    json={
                        "question": prompt
                    },
                    timeout=90
                )

                response.raise_for_status()
                data = response.json()

                status = data.get("status")

                if status == "approval_required":

                    approval = data.get("approval", {})

                    answer = (
                        "The agent needs your approval before "
                        "executing the selected tool: "
                        f"{approval.get('tool', 'Unknown tool')}."
                    )

                    st.session_state.pending_agent = {
                        "thread_id": data.get("thread_id"),
                        "question": prompt
                    }

                else:
                    answer = format_agent_result(data)

                citations = get_citations(data)
                note = data.get("note")

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "question": prompt,
                "mode": selected_mode,
                "citations": citations,
                "note": note,
                "feedback": None
            })

        except requests.RequestException as error:

            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    f"Could not get an answer from the backend: {error}"
                ),
                "question": prompt,
                "mode": selected_mode,
                "citations": [],
                "feedback": None
            })

    st.rerun()


# --------------------------------------------------
# Agent approval section
# --------------------------------------------------

if st.session_state.pending_agent:

    st.divider()
    st.subheader("Agent tool approval")

    st.warning(
        "The agent has requested permission to execute a tool. "
        "Review the request before approving."
    )

    col1, col2 = st.columns(2)

    with col1:
        approve = st.button(
            "Approve",
            type="primary",
            key="approve_agent"
        )

    with col2:
        reject = st.button(
            "Reject",
            key="reject_agent"
        )

    if approve or reject:

        pending = st.session_state.pending_agent
        approved = bool(approve)

        with st.spinner("Processing approval..."):

            try:
                response = requests.post(
                    f"{API_URL}/agent",
                    json={
                        "question": pending["question"],
                        "thread_id": pending["thread_id"],
                        "approved": approved
                    },
                    timeout=90
                )

                response.raise_for_status()
                data = response.json()

                if data.get("status") == "completed":
                    answer = format_agent_result(data)
                elif data.get("status") == "rejected":
                    answer = "Tool execution was rejected."
                else:
                    answer = format_agent_result(data)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "question": pending["question"],
                    "mode": "Agent",
                    "citations": get_citations(data),
                    "feedback": None
                })

                st.session_state.pending_agent = None

            except requests.RequestException as error:
                st.error(f"Approval request failed: {error}")

        st.rerun()


# --------------------------------------------------
# Personal vaccine calendar
# --------------------------------------------------

st.divider()
st.header("📅 Personal Vaccine Calendar")

st.write(
    "Enter your baby's date of birth to generate a vaccination "
    "timeline. Mark a dose as completed after vaccination."
)

dob = st.date_input(
    "Baby's date of birth",
    value=date.today(),
    max_value=date.today(),
    key="baby_dob"
)

dob_string = dob.isoformat()

try:
    calendar = vaccine_due_dates(
        date_of_birth=dob_string
    )

    doses = calendar.get("doses", [])

    completed_doses = get_completed_doses(dob_string)

    st.write(
        f"**Total scheduled doses:** {len(doses)}"
    )

    if doses:

        st.caption(
            "The calendar uses the existing vaccine schedule "
            "and date calculation in your backend project."
        )

        # Status summary
        status_counts = {
            "Done": 0,
            "Due this week": 0,
            "Overdue": 0,
            "Too late": 0,
            "Upcoming": 0
        }

        for dose in doses:
            key = (
                dose["record_id"],
                dose["dose_number"]
            )

            status = (
                "Done"
                if key in completed_doses
                else dose["status"]
            )

            status_counts[status] = (
                status_counts.get(status, 0) + 1
            )

        cols = st.columns(5)

        for column, (status, count) in zip(
            cols,
            status_counts.items()
        ):
            with column:
                st.metric(status, count)

        st.divider()
        st.subheader("Vaccination timeline")

        # Sort doses by due date
        sorted_doses = sorted(
            doses,
            key=lambda item: item["due_date"]
        )

        for index, dose in enumerate(sorted_doses):

            record_id = dose["record_id"]
            dose_number = dose["dose_number"]

            dose_key = (record_id, dose_number)

            is_done = dose_key in completed_doses

            widget_key = (
                f"dose_{dob_string}_{record_id}_{dose_number}"
            )

            if widget_key not in st.session_state:
                st.session_state[widget_key] = is_done

            current_status = (
                "Done"
                if is_done
                else dose["status"]
            )

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(
                        f"**{dose['vaccine']} – Dose {dose_number}**"
                    )

                    st.caption(
                        f"Due date: {dose['due_date']} | "
                        f"Dose: {dose['dose']}"
                    )

                    st.caption(
                        f"Route/site: {dose['route_site']}"
                    )

                with col2:
                    show_status(current_status)

                    st.checkbox(
                        "Mark as Done",
                        key=widget_key,
                        on_change=persist_dose,
                        args=(
                            dob_string,
                            record_id,
                            dose_number,
                            widget_key
                        )
                    )

        # --------------------------------------------------
        # Fridge list export
        # --------------------------------------------------

        st.divider()
        st.subheader("🧾 Download vaccination fridge list")

        fridge_lines = [
            "TEEKATIMER - VACCINATION CHECKLIST",
            "=" * 42,
            f"Date of birth: {dob_string}",
            f"Generated on: {date.today().isoformat()}",
            "",
            "VACCINATION SCHEDULE",
            "-" * 42
        ]

        for dose in sorted_doses:

            key = (
                dose["record_id"],
                dose["dose_number"]
            )

            status = (
                "Done"
                if key in completed_doses
                else dose["status"]
            )

            checkbox = "[X]" if status == "Done" else "[ ]"

            fridge_lines.append(
                f"{checkbox} {dose['vaccine']} - "
                f"Dose {dose['dose_number']}"
            )

            fridge_lines.append(
                f"    Due: {dose['due_date']} | Status: {status}"
            )

        fridge_lines.extend([
            "",
            "Please confirm vaccination details with your healthcare professional.",
            "This checklist is a tracking aid, not a medical prescription.",
        ])

        fridge_list = "\n".join(fridge_lines)

        st.download_button(
            label="📥 Download fridge list",
            data=fridge_list,
            file_name="teekatimer_vaccination_checklist.txt",
            mime="text/plain"
        )

    else:
        st.info("No vaccine doses were returned for this date.")

except (ValueError, OSError) as error:
    st.error(
        f"Could not generate the vaccine calendar: {error}"
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "TeekaTimer is an educational vaccination tracking assistant. "
    "Always confirm vaccination decisions and schedules with "
    "a qualified healthcare professional."
)
