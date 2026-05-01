import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import streamlit as st
import uuid
from backend.query_processor import process_query_sync
from backend.utils import cleanup_session_artifacts
from ui.streaming_callbacks import StreamlitAgentStatusCallback

st.set_page_config(
    page_title="XYZ Bank Advisor",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

st.title("XYZ Bank Advisor")
st.write("Ask your banking question and get intelligence powered by the XYZ Bank.")

session_id = st.query_params['session_id'] if 'session_id' in st.query_params else None

if not session_id:
    session_id = uuid.uuid4().hex
    st.query_params["session_id"] = session_id

if "response_data" not in st.session_state:
    st.session_state.response_data = None

if "last_query" not in st.session_state:
    st.session_state.last_query = ""

if "chat_ended" not in st.session_state:
    st.session_state.chat_ended = False

with st.sidebar:
    st.header("Conversation")
    st.write(f"Session ID: `{session_id}`")
    if st.button("Reset conversation"):
        st.session_state.response_data = None
        st.session_state.last_query = ""
        st.session_state.chat_ended = False
        new_session_id = uuid.uuid4().hex
        st.query_params["session_id"] = new_session_id
        st.rerun()
    if st.button("End chat"):
        cleanup_session_artifacts(session_id)
        st.session_state.response_data = None
        st.session_state.last_query = ""
        st.session_state.chat_ended = True
        #st.query_params["session_id"] = uuid.uuid4().hex
        st.success("Session cleaned up. Closing this tab...")

if st.session_state.chat_ended:
    st.info("Session ended. Closing this tab...")
    st.html(
        """
        <script>
        (() => {
            const closeTab = () => {
                try {
                    window.open('', '_self');
                    window.close();
                } catch (error) {
                    console.debug('Unable to close browser tab:', error);
                }

                setTimeout(() => {
                    if (!window.closed) {
                        window.location.replace('about:blank');
                    }
                }, 500);
            };

            setTimeout(closeTab, 100);
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )
    st.stop()

query = st.chat_input("Ask about loans, accounts, policies, or investment guidance...")

rendered_live_answer = False

if query:
    st.session_state.last_query = query.strip()
    st.markdown("## Results")
    answer_placeholder = st.empty()
    answer_placeholder.info("Preparing your answer...")
    status = st.status("Processing your query...", expanded=True)
    status.update(label="Classifying the query and preparing the agent...", state="running", expanded=True)
    status.write("Classifying the query and preparing the agent...")
    streaming_callback = StreamlitAgentStatusCallback(status, answer_placeholder)

    st.session_state.response_data = process_query_sync(
        query,
        session_id,
        callbacks=[streaming_callback],
    )
    rendered_live_answer = True

    response_text = st.session_state.response_data.get("response_text", "")
    if response_text:
        answer_placeholder.info(response_text)

    if not streaming_callback.had_error:
        status.update(label="Response ready.", state="complete", expanded=False)

response_data = st.session_state.response_data

if response_data:
    intent = response_data.get("intent", {})
    source_documents = response_data.get("source_documents", [])
    scratchpad = response_data.get("scratchpad", "No scratchpad available.")
    agent_feedback = response_data.get("agent_feedback", [])
    response_text = response_data.get("response_text", "")

    if not rendered_live_answer:
        st.markdown("## Results")
        st.info(response_text)

    with st.expander("User Context"):
        st.write(f"**Detected Intent:** {intent.get('intent', 'unknown').replace('_', ' ').title()}")
        st.write(f"**Confidence:** {intent.get('confidence_score', 0.0):.2f}")
        if intent.get('feedback'):
            st.write(f"**Detected Feedback:** {intent.get('feedback')}")

    with st.expander("Knowledge Source"):
        if source_documents:
            for idx, doc in enumerate(source_documents, start=1):
                st.markdown(f"**Chunk {idx}**")
                st.write(f"Source: {doc.get('source', 'unknown')}")
                st.write(f"Page: {doc.get('page', 'unknown')}")
                st.write(doc.get('content', ''))
                st.divider()
        else:
            st.write("No Qdrant chunks were retrieved for this query.")

    with st.expander("Diagnostics"):
        st.subheader("Scratchpad")
        st.write(scratchpad or "No scratchpad information available.")

        st.subheader("Feedback")
        if agent_feedback:
            for item in agent_feedback:
                st.write(f"- {item}")
        else:
            st.write("No agent feedback found for this session.")

    with st.expander("Session Details"):
        st.write(f"Session ID: `{session_id}`")
        st.write(f"Query: {st.session_state.last_query}")
