from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

def get_response(question: str, paragraph: str) -> str:
    prompt = f"""
            You are a helpful assistant that answers questions based only on the given document content, The question is only related to the content provided. If the answer isn't in the content, say 'I couldn't find that in the document.'
            Content: {paragraph.strip()}
            Question: {question.strip()}
            """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    return resp.text