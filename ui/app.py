import html
import json
import os
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st

# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FEEDBACK_FILE = PROJECT_ROOT / "data" / "feedback.json"

# Allow API_BASE to be overridden via environment variable so the same
# image works both locally (127.0.0.1:8000) and inside Docker (api:8000).
API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")
ASK_URL   = f"{API_BASE}/ask"
AGENT_URL = f"{API_BASE}/agent"


# =========================================================
# LOAN SCHEME DATA
# =========================================================

MUDRA_BANDS = [
    {
        "name":    "Shishu",
        "emoji":   "🌱",
        "min":     0,
        "max":     50_000,
        "colour":  "#1e8e3e",
        "desc":    "Up to ₹50,000 — for micro enterprises just starting out.",
        "margin":  None,
    },
    {
        "name":    "Kishor",
        "emoji":   "🌿",
        "min":     50_001,
        "max":     5_00_000,
        "colour":  "#1a73e8",
        "desc":    "₹50,001 – ₹5 lakh — for established micro/small businesses.",
        "margin":  None,
    },
    {
        "name":    "Tarun",
        "emoji":   "🌳",
        "min":     5_00_001,
        "max":     10_00_000,
        "colour":  "#f9ab00",
        "desc":    "₹5 lakh – ₹10 lakh — for growing businesses.",
        "margin":  None,
    },
    {
        "name":    "Tarun Plus",
        "emoji":   "🏆",
        "min":     10_00_001,
        "max":     20_00_000,
        "colour":  "#e37400",
        "desc":    "₹10 lakh – ₹20 lakh — only for borrowers who have repaid a Tarun loan.",
        "margin":  None,
    },
]

STANDUP_BAND = {
    "name":   "Stand-Up India",
    "emoji":  "🏛️",
    "min":    10_00_000,
    "max":    1_00_00_000,
    "colour": "#9334e6",
    "desc":   "₹10 lakh – ₹1 crore — for SC/ST & women entrepreneurs setting up greenfield enterprises.",
    "margin_old": "up to 25%",
    "margin_new": "up to 15%",
    "margin_note": (
        "⚠️ **Document Disagreement:** An older version of the Stand-Up India FAQ "
        "states the margin money requirement was **up to 25%** of project cost. "
        "Following the Union Budget 2021-22, this was **reduced to up to 15%** "
        "(with at least 10% own contribution). "
        "If your lender quotes 25%, ask them to apply the updated 2021-22 scheme terms."
    ),
}


def rupees_label(amount):
    """Format an integer amount as a readable ₹ string."""
    if amount >= 1_00_00_000:
        return f"₹{amount / 1_00_00_000:.1f} Cr"
    if amount >= 1_00_000:
        return f"₹{amount / 1_00_000:.1f} L"
    if amount >= 1_000:
        return f"₹{amount / 1_000:.0f}K"
    return f"₹{amount:,}"


def get_scheme_info(amount):
    """Return (mudra_band | None, standup_eligible, conflict_note)."""
    mudra_match = None
    for band in MUDRA_BANDS:
        if band["min"] <= amount <= band["max"]:
            mudra_match = band
            break

    standup_eligible = (
        STANDUP_BAND["min"] <= amount <= STANDUP_BAND["max"]
    )

    conflict_note = None
    if standup_eligible:
        conflict_note = STANDUP_BAND["margin_note"]

    return mudra_match, standup_eligible, conflict_note


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
:root { color-scheme: dark; }

.stApp {
    background: #0b1220;
    color: #e8eef8;
}
header[data-testid="stHeader"] {
    background: rgba(11,18,32,0.95);
}
.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}
h1, h2, h3, h4, p, label { color: #e8eef8; }

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
    width: 46px; height: 46px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 14px;
    background: linear-gradient(135deg, #245a91, #3989d5);
    font-size: 24px;
}
.brand-name {
    color: #f5f8ff; font-size: 21px; font-weight: 750; letter-spacing: -0.5px;
}
.brand-subtitle { color: #91a4bd; font-size: 12px; margin-top: 2px; }

/* Welcome */
.welcome { text-align: center; padding: 35px 12px 25px 12px; }
.welcome-icon { font-size: 38px; margin-bottom: 14px; }
.welcome h1 {
    color: #f4f7fc; font-size: 35px; font-weight: 750;
    letter-spacing: -1.2px; margin-bottom: 12px;
}
.welcome p { color: #9aabc1; font-size: 15px; line-height: 1.7; }

/* Suggested question cards */
div.st-key-suggestion_1 button,
div.st-key-suggestion_2 button,
div.st-key-suggestion_3 button,
div.st-key-suggestion_4 button {
    width: 100%; min-height: 90px; text-align: left; white-space: normal;
    background: #151f30; border: 1px solid #293a52; border-radius: 15px;
    color: #dce8f8; padding: 14px; transition: all 0.2s ease;
}
div.st-key-suggestion_1 button:hover,
div.st-key-suggestion_2 button:hover,
div.st-key-suggestion_3 button:hover,
div.st-key-suggestion_4 button:hover {
    background: #1c2d45; border-color: #4c91d5; color: white;
}

/* Chat messages */
div[data-testid="stChatMessage"] {
    background: #131e2e; border: 1px solid #26364c;
    border-radius: 17px; padding: 15px; margin-bottom: 14px;
}
div[data-testid="stChatMessage"] p { color: #e5edf8; line-height: 1.7; }

/* Chat input */
div[data-testid="stChatInput"] {
    background: #151f30; border: 1px solid #344761; border-radius: 17px;
}
div[data-testid="stChatInput"] textarea { color: #f4f7fc; }
div[data-testid="stChatInput"] textarea::placeholder { color: #8395ad; }

/* Buttons */
.stButton button, .stFormSubmitButton button {
    background: #286ba8; color: white;
    border: 1px solid #397fbd; border-radius: 11px; font-weight: 600;
}
.stButton button:hover, .stFormSubmitButton button:hover {
    background: #347fbe; border-color: #64a9e5; color: white;
}

/* Citations */
div[data-testid="stExpander"] {
    background: #111d2c; border: 1px solid #2c4059; border-radius: 13px;
}
div[data-testid="stExpander"] summary { color: #a9d2fa; }

/* Loan picker card */
.loan-card {
    border-radius: 16px;
    padding: 18px 20px;
    margin-top: 10px;
    margin-bottom: 6px;
    border: 2px solid;
}
.conflict-box {
    background: #1f1510;
    border: 1px solid #7a3c00;
    border-radius: 12px;
    padding: 14px 16px;
    margin-top: 10px;
    color: #f5c97a;
    font-size: 14px;
    line-height: 1.65;
}

hr { border-color: #263449; }

section[data-testid="stSidebar"] { background: #101a29; }
section[data-testid="stSidebar"] * { color: #e5edf8; }

.metadata { color: #8fa3bd; font-size: 12px; }
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

if "mode" not in st.session_state:
    st.session_state.mode = "ask"          # "ask" or "agent"

if "agent_thread_id" not in st.session_state:
    st.session_state.agent_thread_id = str(uuid4())

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None   # holds approval payload


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("### ⚙️ Settings")

    mode_choice = st.radio(
        "Response mode",
        ["💬 RAG (fast, cited)", "🤖 Agent (uses tools)"],
        index=0 if st.session_state.mode == "ask" else 1,
        help=(
            "RAG: retrieves documents and answers with citations.\n"
            "Agent: plans multi-step actions using tools like EMI calculator."
        )
    )
    st.session_state.mode = (
        "ask" if mode_choice.startswith("💬") else "agent"
    )

    st.divider()

    if st.button("🔄 New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.session_state.feedback_saved_for = set()
        st.session_state.pending_approval = None
        st.session_state.agent_thread_id = str(uuid4())
        st.rerun()

    st.divider()
    st.caption("MudraMitra · Checkpoint 2")
    st.caption("Sources: PMMY FAQ · Stand-Up India FAQ")


# =========================================================
# BRAND HEADER
# =========================================================

st.markdown("""
<div class="brand">
    <div class="brand-icon">💰</div>
    <div>
        <div class="brand-name">MudraMitra</div>
        <div class="brand-subtitle">AI Loan Assistant · Checkpoint 2</div>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# LOAN PICKER SLIDER
# =========================================================

with st.expander("🎚️ Loan Amount Picker — find your scheme", expanded=True):
    st.markdown(
        "Drag the slider to your required loan amount and the matching "
        "scheme highlights automatically."
    )

    # Slider max is ₹1 crore (Stand-Up India upper limit).
    # We use a step of ₹10,000 for fine control at the low end.
    slider_amount = st.slider(
        label="Required loan amount",
        min_value=10_000,
        max_value=1_00_00_000,
        value=50_000,
        step=10_000,
        format="%d",
        label_visibility="collapsed",
    )

    st.markdown(
        f"**Selected:** {rupees_label(slider_amount)}"
        f"  ·  ₹{slider_amount:,}"
    )

    mudra_match, standup_eligible, conflict_note = get_scheme_info(slider_amount)

    # --- Mudra band highlight ---
    if mudra_match:
        c = mudra_match["colour"]
        st.markdown(
            f"""
            <div class="loan-card" style="background:{c}18;border-color:{c};">
                <span style="font-size:22px">{mudra_match['emoji']}</span>&nbsp;
                <strong style="color:{c};font-size:17px;">
                    PMMY — {mudra_match['name']}
                </strong><br>
                <span style="color:#cdd8e8;font-size:14px;">
                    {mudra_match['desc']}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info(
            "This amount falls outside all MUDRA (PMMY) loan categories "
            "(max ₹20 lakh). Consider Stand-Up India if eligible.",
            icon="ℹ️",
        )

    # --- Stand-Up India band highlight ---
    if standup_eligible:
        c = STANDUP_BAND["colour"]
        st.markdown(
            f"""
            <div class="loan-card" style="background:{c}18;border-color:{c};margin-top:8px;">
                <span style="font-size:22px">{STANDUP_BAND['emoji']}</span>&nbsp;
                <strong style="color:{c};font-size:17px;">
                    Stand-Up India also applies
                </strong><br>
                <span style="color:#cdd8e8;font-size:14px;">
                    {STANDUP_BAND['desc']}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Document conflict note ---
    if conflict_note:
        st.markdown(
            f'<div class="conflict-box">{conflict_note}</div>',
            unsafe_allow_html=True,
        )

    # --- Quick reference table ---
    st.markdown("&nbsp;")
    st.markdown("**Quick reference — all scheme bands:**")
    rows = ""
    for b in MUDRA_BANDS:
        active = (
            " style='background:#1c2a3a;font-weight:600'"
            if mudra_match and mudra_match["name"] == b["name"]
            else ""
        )
        rows += (
            f"<tr{active}>"
            f"<td>{b['emoji']} {b['name']}</td>"
            f"<td>{rupees_label(b['min'])} – {rupees_label(b['max'])}</td>"
            f"<td>PMMY / MUDRA</td>"
            f"</tr>"
        )
    sui_active = (
        " style='background:#1c2a3a;font-weight:600'"
        if standup_eligible
        else ""
    )
    rows += (
        f"<tr{sui_active}>"
        f"<td>{STANDUP_BAND['emoji']} Stand-Up India</td>"
        f"<td>{rupees_label(STANDUP_BAND['min'])} – {rupees_label(STANDUP_BAND['max'])}</td>"
        f"<td>SC/ST · Women</td>"
        f"</tr>"
    )
    st.markdown(
        f"""
        <table style='width:100%;border-collapse:collapse;font-size:13px;
                      color:#cdd8e8;background:#0d1a28;border-radius:10px;overflow:hidden;'>
            <thead>
                <tr style='background:#182840;color:#a9c8f0;'>
                    <th style='padding:7px 10px;text-align:left'>Scheme</th>
                    <th style='padding:7px 10px;text-align:left'>Amount Range</th>
                    <th style='padding:7px 10px;text-align:left'>Target</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# BACKEND HELPERS
# =========================================================

def _post(url, payload_dict, timeout=120):
    """POST JSON payload, return parsed response dict."""
    data = json.dumps(payload_dict).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ask_backend(question):
    return _post(ASK_URL, {"question": question, "top_k": 10})


def agent_backend(question=None, thread_id=None, approved=None):
    payload = {"thread_id": thread_id or st.session_state.agent_thread_id}
    if question is not None:
        payload["question"] = question
    if approved is not None:
        payload["approved"] = approved
    return _post(AGENT_URL, payload)


# =========================================================
# FEEDBACK STORAGE
# =========================================================

def save_feedback(question, answer, rating):
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    feedback = []
    if FEEDBACK_FILE.exists():
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                feedback = json.load(f)
            if not isinstance(feedback, list):
                feedback = []
        except (json.JSONDecodeError, OSError):
            feedback = []

    feedback.append({
        "question": question,
        "answer": answer,
        "rating": rating,
        "timestamp": datetime.now(UTC).isoformat(),
    })
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback, f, indent=4, ensure_ascii=False)


# =========================================================
# CITATION DISPLAY
# =========================================================

def display_citations(citations):
    if not citations:
        return
    with st.expander(
        f"📚 View {len(citations)} source citation(s)", expanded=False
    ):
        for index, citation in enumerate(citations, start=1):
            source = html.escape(str(citation.get("source", "Unknown")))
            title  = html.escape(str(citation.get("title",  "Unknown")))
            page   = html.escape(str(citation.get("page",   "N/A")))
            cnum   = html.escape(str(citation.get("citation", index)))
            cid    = html.escape(str(citation.get("chunk_id", "N/A")))

            st.markdown(f"**{source}**")
            st.caption(f"Document: {title}")
            st.caption(f"Page: {page}  ·  Citation: {cnum}")
            st.caption(f"Chunk ID: `{cid}`")
            if index < len(citations):
                st.divider()


# =========================================================
# TOOLS-USED DISPLAY (agent mode)
# =========================================================

def display_tools_used(tools_used):
    if not tools_used:
        return
    with st.expander(f"🔧 Agent used {len(tools_used)} tool(s)", expanded=False):
        for item in tools_used:
            if isinstance(item, dict):
                name = item.get("tool") or item.get("name", "unknown")
                st.markdown(f"- `{name}`")
            else:
                st.markdown(f"- `{item}`")


# =========================================================
# PENDING TOOL-APPROVAL BANNER  (agent mode)
# =========================================================

def show_approval_banner():
    approval = st.session_state.pending_approval
    if approval is None:
        return

    st.warning(
        "🤖 **The agent wants to run a tool — please approve or deny.**",
        icon="⚠️",
    )
    with st.expander("Tool request details", expanded=True):
        st.json(approval)

    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("✅ Approve", key="approve_btn", use_container_width=True):
            _handle_approval(True)
    with col_no:
        if st.button("❌ Deny", key="deny_btn", use_container_width=True):
            _handle_approval(False)


def _handle_approval(approved: bool):
    with st.spinner("Resuming agent…"):
        try:
            result = agent_backend(approved=approved)
            st.session_state.pending_approval = None
            _process_agent_result(result, question=None)
        except Exception:
            st.error("Could not resume the agent. Please try again.")
    st.rerun()


def _process_agent_result(result, question):
    status = result.get("status")
    if status == "approval_required":
        st.session_state.pending_approval = result.get("approval")
        # Store a placeholder so the banner renders on rerun
        st.session_state.messages.append({
            "role": "assistant",
            "content": "_(Waiting for your approval to run a tool…)_",
            "citations": [],
            "question": question or "",
            "message_id": str(uuid4()),
            "tools_used": [],
            "agent": True,
            "approval_pending": True,
        })
    else:
        answer     = result.get("answer", "No answer returned.")
        tools_used = result.get("tools_used", [])
        st.session_state.pending_approval = None
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "citations": [],
            "question": question or "",
            "message_id": str(uuid4()),
            "tools_used": tools_used,
            "agent": True,
        })


# =========================================================
# WELCOME SCREEN
# =========================================================

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
        <div class="welcome-icon">✦</div>
        <h1>How can I help you today?</h1>
        <p>
            Ask anything about MUDRA or Stand-Up India loans.<br>
            Get clear, document-based answers with source references.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### Explore suggested questions")
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "💼  Loan categories\n\nExplore Shishu, Kishor and Tarun",
            key="suggestion_1", use_container_width=True
        ):
            st.session_state.pending_question = (
                "What are the different categories available under PMMY?"
            )
            st.rerun()

        if st.button(
            "📋  Eligibility criteria\n\nUnderstand MUDRA loan eligibility",
            key="suggestion_2", use_container_width=True
        ):
            st.session_state.pending_question = (
                "What are the eligibility criteria for a MUDRA loan?"
            )
            st.rerun()

    with col2:
        if st.button(
            "₹  Loan amounts\n\nUnderstand the different loan limits",
            key="suggestion_3", use_container_width=True
        ):
            st.session_state.pending_question = (
                "What are the loan amounts available under PMMY?"
            )
            st.rerun()

        if st.button(
            "🏛️  Stand-Up India\n\nSC/ST & women entrepreneur loans",
            key="suggestion_4", use_container_width=True
        ):
            st.session_state.pending_question = (
                "What is the Stand-Up India scheme and who is eligible?"
            )
            st.rerun()


# =========================================================
# PENDING APPROVAL BANNER (rendered before chat history)
# =========================================================

show_approval_banner()


# =========================================================
# CHAT HISTORY
# =========================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            display_citations(message.get("citations", []))
            display_tools_used(message.get("tools_used", []))

            if "retrieved_chunks" in message:
                st.caption(
                    f"Documents retrieved: {message['retrieved_chunks']}"
                )


# =========================================================
# CHAT INPUT
# =========================================================

typed_question = st.chat_input("Ask MudraMitra anything…")

question = typed_question
if not question and st.session_state.pending_question:
    question = st.session_state.pending_question

if question:
    st.session_state.pending_question = None

    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and searching your documents…"):
            try:
                if st.session_state.mode == "agent":
                    # --- Agent mode ---
                    result = agent_backend(
                        question=question,
                        thread_id=st.session_state.agent_thread_id,
                    )
                    _process_agent_result(result, question)
                    last = st.session_state.messages[-1]
                    st.markdown(last["content"])
                    display_tools_used(last.get("tools_used", []))

                else:
                    # --- RAG / ask mode ---
                    result = ask_backend(question)
                    answer  = result.get("answer", "Sorry, no answer was returned.")
                    citations = result.get("citations", [])
                    retrieved = result.get("retrieved_chunks", 0)

                    st.markdown(answer)
                    display_citations(citations)
                    st.caption(f"Documents retrieved: {retrieved}")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "citations": citations,
                        "found": result.get("found", False),
                        "question": question,
                        "retrieved_chunks": retrieved,
                        "message_id": str(uuid4()),
                    })

            except urllib.error.HTTPError as err:
                msg = (
                    f"The server returned an error (HTTP {err.code}). "
                    "Please try again."
                )
                st.error(msg)
                st.session_state.messages.append({
                    "role": "assistant", "content": msg,
                    "citations": [], "question": question,
                    "message_id": str(uuid4()), "error": True,
                })

            except urllib.error.URLError:
                msg = (
                    "I can't connect to the AI service right now. "
                    "Make sure `uvicorn app.main:app --reload` is running on port 8000."
                )
                st.error(msg)
                st.session_state.messages.append({
                    "role": "assistant", "content": msg,
                    "citations": [], "question": question,
                    "message_id": str(uuid4()), "error": True,
                })

            except Exception:
                msg = (
                    "Something went wrong while processing your question. "
                    "Please try again."
                )
                st.error(msg)
                st.session_state.messages.append({
                    "role": "assistant", "content": msg,
                    "citations": [], "question": question,
                    "message_id": str(uuid4()), "error": True,
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
        and not latest.get("approval_pending", False)
    ):
        message_id = latest.get("message_id", "")

        st.divider()
        st.markdown("##### Was this answer helpful?")
        st.caption("Your feedback helps improve answer quality.")

        if message_id in st.session_state.feedback_saved_for:
            st.success("Thank you — feedback saved.")
        else:
            with st.form(f"feedback_form_{message_id}"):
                rating_label = st.radio(
                    "Choose your feedback",
                    ["👍 Helpful", "👎 Not helpful"],
                    horizontal=True,
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button(
                    "Submit feedback", use_container_width=True
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
                            rating,
                        )
                        st.session_state.feedback_saved_for.add(message_id)
                        st.rerun()
                    except (OSError, ValueError):
                        st.error(
                            "Feedback could not be saved. Please try again."
                        )
