# QueryDoc 🧾

**QueryDoc** is a lightweight GenAI application that allows users to ask natural-language questions about the contents of a PDF document. It uses custom keyword-based retrieval and OpenAI's GPT model to generate context-aware answers.

> Upload any PDF → Ask a question → Get a smart answer grounded in the document.

---

## Features

- PDF text extraction and paragraph-based chunking
- Custom keyword-based chunk relevance scoring
- Gemini-powered response generation using selected paragraph
- Displays source paragraph for answer grounding
- Built with **Python + Streamlit** for rapid prototyping

---

## How It Works

1. **PDF Upload**  
   User uploads a document. Text is extracted using `PyMuPDF`.

2. **Paragraph Chunking**  
   The document is split into logical paragraphs (blank lines = separators).

3. **Keyword Matching**  
   When a question is asked, it's cleaned and compared to each paragraph using keyword overlap. The paragraph with the most shared meaningful words is selected.

4. **Answer Generation**  
   The selected paragraph and the question are sent to **OpenAI's GPT-3.5** to generate a clear, context-aware answer.

---
<!-- 
## Demo

![demo](path-to-screenshot.png) 

--- -->


## Installation

```bash
git clone https://github.com/your-username/querydoc.git
cd querydoc
pip install -r requirements.txt
```
---
## Usage

```bash
streamlit run app.py
```

Then:

1. Upload a PDF
2. Ask a question
3. View the matched paragraph and AI-generated answer

> Note: You’ll need an Google Gemini API key. Set it as an environment variable.

---

## Example Questions

Ask questions that relate directly to the **content** of the uploaded PDF. For example:

- “What does the second paragraph say about product safety?”
- “Explain the main idea in the section about data privacy.”
- “What is mentioned about warranty terms?”
- “How is the training process described?”
- “What does the document say about performance evaluation?”

> Avoid questions about metadata like “Who is the author?” or “How many pages?” as this system retrieves answers from **visible text**, not document properties.

---

## License

This project is for educational and demonstration purposes.



## Author

**Sai Sreenadh Chilukuri**

```
