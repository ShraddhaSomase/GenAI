import html
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FEEDBACK_FILE = PROJECT_ROOT / "data" / "feedback.json"

API_URL = "http://127.0.0.1:8001/ask"


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="MudraMitra AI",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# DARK THEME STYLING
# =========================================================

st.markdown("""
<style>
:root {
    color-scheme: dark;
}

.stApp {
    background: #0b1220;
    color: #e8eef8;
}

header[data-testid="stHeader"] {
    background: rgba(11, 18, 32, 0.95);
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

h1, h2, h3, h4, p, label {
    color: #e8eef8;
}

/* Brand header */
.brand {
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 8px 0 22px 0;
    border-bottom: 1px solid #263449;
    margin-bottom: 35px;
}

.brand-icon {
    width: 46px;
    height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    background: linear-gradient(135deg, #245a91, #3989d5);
    font-size: 24px;
}

.brand-name {
    color: #f5f8ff;
    font-size: 21px;
    font-weight: 750;
    letter-spacing: -0.5px;
}

.brand-subtitle {
    color: #91a4bd;
    font-size: 12px;
    margin-top: 2px;
}

/* Welcome section */
.welcome {
    text-align: center;
    padding: 35px 12px 25px 12px;
}

.welcome-icon {
    font-size: 38px;
    margin-bottom: 14px;
}

.welcome h1 {
    color: #f4f7fc;
    font-size: 35px;
    font-weight: 750;
    letter-spacing: -1.2px;
    margin-bottom: 12px;
}

.welcome p {
    color: #9aabc1;
    font-size: 15px;
    line-height: 1.7;
}

/* Suggested question cards */
div.st-key-suggestion_1 button,
div.st-key-suggestion_2 button,
div.st-key-suggestion_3 button,
div.st-key-suggestion_4 button {
    width: 100%;
    min-height: 90px;
    text-align: left;
    white-space: normal;
    background: #151f30;
    border: 1px solid #293a52;
    border-radius: 15px;
    color: #dce8f8;
    padding: 14px;
    transition: all 0.2s ease;
}

div.st-key-suggestion_1 button:hover,
div.st-key-suggestion_2 button:hover,
div.st-key-suggestion_3 button:hover,
div.st-key-suggestion_4 button:hover {
    background: #1c2d45;
    border-color: #4c91d5;
    color: white;
}

/* Chat messages */
div[data-testid="stChatMessage"] {
    background: #131e2e;
    border: 1px solid #26364c;
    border-radius: 17px;
    padding: 15px;
    margin-bottom: 14px;
}

div[data-testid="stChatMessage"] p {
    color: #e5edf8;
    line-height: 1.7;
}

/* Chat input */
div[data-testid="stChatInput"] {
    background: #151f30;
    border: 1px solid #344761;
    border-radius: 17px;
}

div[data-testid="stChatInput"] textarea {
    color: #f4f7fc;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #8395ad;
}

/* Buttons */
.stButton button,
.stFormSubmitButton button {
    background: #286ba8;
    color: white;
    border: 1px solid #397fbd;
    border-radius: 11px;
    font-weight: 600;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background: #347fbe;
    border-color: #64a9e5;
    color: white;
}

/* Citation section */
div[data-testid="stExpander"] {
    background: #111d2c;
    border: 1px solid #2c4059;
    border-radius: 13px;
}

div[data-testid="stExpander"] summary {
    color: #a9d2fa;
}

/* Feedback */
.feedback-note {
    color: #91a4bd;
    font-size: 13px;
}

hr {
    border-color: #263449;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #101a29;
}

section[data-testid="stSidebar"] * {
    color: #e5edf8;
}

/* Small metadata */
.metadata {
    color: #8fa3bd;
    font-size: 12px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "feedback_saved_for" not in st.session_state:
    st.session_state.feedback_saved_for = set()


# =========================================================
# BRAND HEADER
# =========================================================

st.markdown("""
<div class="brand">
    <div class="brand-icon">💰</div>
    <div>
        <div class="brand-name">MudraMitra</div>
        <div class="brand-subtitle">AI Loan Assistant</div>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# BACKEND REQUEST
# =========================================================

def ask_backend(question):
    payload = json.dumps({
        "question": question,
        "top_k": 10
    }).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


# =========================================================
# FEEDBACK STORAGE
# =========================================================

def save_feedback(question, answer, rating):
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

    feedback = []

    if FEEDBACK_FILE.exists():
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as file:
                feedback = json.load(file)

            if not isinstance(feedback, list):
                feedback = []

        except (json.JSONDecodeError, OSError):
            feedback = []

    feedback.append({
        "question": question,
        "answer": answer,
        "rating": rating,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    with open(FEEDBACK_FILE, "w", encoding="utf-8") as file:
        json.dump(feedback, file, indent=4, ensure_ascii=False)


# =========================================================
# CITATION DISPLAY
# =========================================================

def display_citations(citations):
    if not citations:
        st.caption("No supporting citations were returned.")
        return

    with st.expander(
        f"📚 View {len(citations)} source citation(s)",
        expanded=False
    ):
        for index, citation in enumerate(citations, start=1):
            source = html.escape(str(citation.get("source", "Unknown")))
            title = html.escape(str(citation.get("title", "Unknown")))
            page = html.escape(str(citation.get("page", "N/A")))
            citation_number = html.escape(
                str(citation.get("citation", index))
            )
            chunk_id = html.escape(
                str(citation.get("chunk_id", "N/A"))
            )

            st.markdown(f"**{source}**")
            st.caption(f"Document: {title}")
            st.caption(
                f"Page: {page}  ·  Citation: {citation_number}"
            )
            st.caption(f"Chunk ID: `{chunk_id}`")

            if index < len(citations):
                st.divider()


# =========================================================
# WELCOME SCREEN AND SUGGESTED QUESTIONS
# =========================================================

if not st.session_state.messages:

    st.markdown("""
    <div class="welcome">
        <div class="welcome-icon">✦</div>
        <h1>How can I help you today?</h1>
        <p>
            Ask anything about MUDRA loans.<br>
            Get clear, document-based answers with source references.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### Explore suggested questions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "💼  Loan categories\n\nExplore Shishu, Kishor and Tarun",
            key="suggestion_1",
            use_container_width=True
        ):
            st.session_state.pending_question = (
                "What are the different categories available under PMMY?"
            )
            st.rerun()

        if st.button(
            "📋  Eligibility criteria\n\nUnderstand MUDRA loan eligibility",
            key="suggestion_2",
            use_container_width=True
        ):
            st.session_state.pending_question = (
                "What are the eligibility criteria for a MUDRA loan?"
            )
            st.rerun()

    with col2:
        if st.button(
            "₹  Loan amounts\n\nUnderstand the different loan limits",
            key="suggestion_3",
            use_container_width=True
        ):
            st.session_state.pending_question = (
                "What are the loan amounts available under PMMY?"
            )
            st.rerun()

        if st.button(
            "📚  Document search\n\nAsk about information in stored documents",
            key="suggestion_4",
            use_container_width=True
        ):
            st.session_state.pending_question = (
                "What information is available in the stored MUDRA documents?"
            )
            st.rerun()


# =========================================================
# CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            display_citations(message.get("citations", []))

            if "retrieved_chunks" in message:
                st.caption(
                    f"Documents retrieved: {message['retrieved_chunks']}"
                )


# =========================================================
# CHAT INPUT
# =========================================================

typed_question = st.chat_input(
    "Ask MudraMitra anything..."
)

question = typed_question

if not question and st.session_state.pending_question:
    question = st.session_state.pending_question

if question:
    st.session_state.pending_question = None

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Thinking and searching your documents..."):

            try:
                result = ask_backend(question)

                answer = result.get(
                    "answer",
                    "Sorry, no answer was returned."
                )

                citations = result.get("citations", [])

                st.markdown(answer)
                display_citations(citations)

                retrieved_chunks = result.get("retrieved_chunks", 0)

                st.caption(
                    f"Documents retrieved: {retrieved_chunks}"
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "citations": citations,
                    "found": result.get("found", False),
                    "question": question,
                    "retrieved_chunks": retrieved_chunks,
                    "message_id": str(uuid4())
                })

            except urllib.error.HTTPError as error:
                error_message = (
                    f"The server returned an error (HTTP {error.code}). "
                    "Please try again."
                )

                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "citations": [],
                    "question": question,
                    "message_id": str(uuid4()),
                    "error": True
                })

            except urllib.error.URLError:
                error_message = (
                    "I can't connect to the AI service right now. "
                    "Please make sure the server is running and try again."
                )

                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "citations": [],
                    "question": question,
                    "message_id": str(uuid4()),
                    "error": True
                })

            except Exception:
                error_message = (
                    "Something went wrong while processing your question. "
                    "Please try again."
                )

                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "citations": [],
                    "question": question,
                    "message_id": str(uuid4()),
                    "error": True
                })

    st.rerun()


# =========================================================
# FEEDBACK FOR LATEST ANSWER
# =========================================================

if st.session_state.messages:

    latest = st.session_state.messages[-1]

    if (
        latest["role"] == "assistant"
        and latest.get("question")
        and not latest.get("error", False)
    ):

        message_id = latest.get("message_id", "")

        st.divider()
        st.markdown("##### Was this answer helpful?")
        st.caption(
            "Your feedback helps us improve the quality of answers."
        )

        if message_id in st.session_state.feedback_saved_for:
            st.success("Thank you. Your feedback has been saved.")

        else:
            with st.form(f"feedback_form_{message_id}"):

                rating_label = st.radio(
                    "Choose your feedback",
                    ["👍 Helpful", "👎 Not helpful"],
                    horizontal=True,
                    label_visibility="collapsed"
                )

                submitted = st.form_submit_button(
                    "Submit feedback",
                    use_container_width=True
                )

                if submitted:
                    rating = (
                        "helpful"
                        if rating_label == "👍 Helpful"
                        else "not_helpful"
                    )

                    try:
                        save_feedback(
                            latest["question"],
                            latest["content"],
                            rating
                        )

                        st.session_state.feedback_saved_for.add(
                            message_id
                        )

                        st.rerun()

                    except (OSError, ValueError):
                        st.error(
                            "Feedback could not be saved. Please try again."
                        )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 💰 MudraMitra")

    st.caption("Your AI loan assistant")

    st.divider()

    if st.button(
        "＋  New conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    st.markdown("---")

    st.caption("Ask questions about MUDRA loan schemes and find answers from your stored documents.")

    st.markdown("---")

    st.caption("Powered by AI · RAG · Document Search")

