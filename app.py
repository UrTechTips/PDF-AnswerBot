import streamlit as st
from utils import extract_text, chunk_text, find_best_match, export_txt, export_pdf, export_markdown
from llm import get_response

st.set_page_config(page_title="Chat with Your PDFs", layout="wide")

st.title("📄 Chat with Your PDFs")
uploaded_files = st.file_uploader("Upload a PDF", type="pdf", accept_multiple_files=True)

if "history" not in st.session_state:
    st.session_state.history = []
if "num_questions_with_answers" not in st.session_state:
    st.session_state.num_questions_with_answers = 0
     
if uploaded_files:
    texts = [extract_text(uploaded_file) for uploaded_file in uploaded_files]
    chunks = [chunk_text(text) for text in texts]
    st.success(f"Parsed {', '.join([str(len(c)) for c in chunks])} chunks from {len(uploaded_files)} PDF's.")

    question = st.text_input("Ask a question about the document:", key="question_input")
    best_chunk = find_best_match(question, chunks)
    if not isinstance(best_chunk, tuple):
        best_chunk_text = best_chunk['text']
        best_chunk_page = f"Page: {best_chunk['page']}"
        best_chunk_file = f"File: {uploaded_files[best_chunk['file_idx']].name}"
    else:
        best_chunk_page = f"Page: {best_chunk[0]['page']}" + ' & ' + f"Page: {best_chunk[1]['page']}"
        best_chunk_text = best_chunk[0]['text'] + '\n\n' + best_chunk[1]['text']
        best_chunk_file = f"Files: {', '.join([uploaded_files[i['file_idx']].name for i in best_chunk])}"
    # best_match = chunks[best_chunk_idx] if best_chunk_idx is not None else None
    if question:
        if best_chunk_text:
            if isinstance(best_chunk, tuple):
                st.markdown("### 🧠 Best-Matching Paragraphs")
                for i in best_chunk:
                    st.info(f"**File: {uploaded_files[i['file_idx']].name}** - **Page {i['page']}**: {i['text']}")
            else:
                st.markdown("### 🧠 Best-Matching Paragraph")
                st.info(f"**File: {uploaded_files[best_chunk['file_idx']].name}** - **Page {best_chunk['page']}**:{best_chunk['text']}")

            with st.spinner("Thinking..."):
                response = get_response(question, best_chunk_text)

                if response.strip() != "I couldn't find that in the document.":
                    his = {
                        "question": question,
                        "answer": response,
                        "chunk": best_chunk_text,
                        "page": best_chunk_page,
                        "file": best_chunk_file
                    }
                    already_asked = any(h['question'] == question and h['answer'] == response for h in st.session_state.history)
                    if not already_asked:
                        st.session_state.history.append(his)
                        st.session_state.num_questions_with_answers += 1

                st.markdown("### 🪄 AI Response")
                st.markdown(response)
        else:
            st.error("No relevant content found.")

with st.sidebar:
    if st.button("🗑 Clear History"):
        st.session_state.history = []
        st.session_state.num_questions_with_answers = 0
    st.markdown("### History")
    for i, item in enumerate(st.session_state.history):
        st.markdown(f"**Q{i+1}:** {item['question']}")
        st.markdown(f"**A:** {item['answer'][:50]}...")

    if st.session_state.history:
        export_format = st.selectbox("Choose format:", ["TXT", "PDF", "Markdown"])

        if export_format == "TXT":
            bufferValue, mime, file_ext = export_txt(st.session_state.history)
        elif export_format == "PDF":
            bufferValue, mime, file_ext = export_pdf(st.session_state.history)
        elif export_format == "Markdown":
            bufferValue, mime, file_ext = export_markdown(st.session_state.history)

        if isinstance(bufferValue, str):
            bufferValue = bufferValue.encode('utf-8')
        st.download_button(
                label="📥 Save File",
                data=bufferValue,
                file_name=f"{'&'.join([file.name for file in uploaded_files])}_Questions.{file_ext}",
                mime=mime
            )