from transformers import pipeline
import re
import os
import math
import unicodedata
import google.generativeai as genai

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
try:
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print(f"⚠️ Gemini model load failed: {e}")
    gemini_model = None

def clean_text(txt):
    if isinstance(txt, list):
        txt = " ".join(txt)

    txt = unicodedata.normalize("NFKC", str(txt))
    txt = re.sub(r'\s+', ' ', txt)
    txt = re.sub(r'\b(uh|um|you know|like|so|yeah)\b', '', txt, flags=re.IGNORECASE)
    return txt.strip()

def summarize_segments(segment_text, max_len=50, min_len=20):
    """
    Summarize a single transcript segment using BART.
    Example: "The host discusses MCP servers and their advantages for debugging."
    """
    segment_text = clean_text(segment_text)
    if not segment_text:
        return "No content available for this segment."

    if len(segment_text) > 3500:
        segment_text = segment_text[:3500]

    raw_summary = summarizer(
        segment_text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False,
        truncation=True
    )[0]["summary_text"]

    summary = raw_summary.strip()
    if not summary.endswith('.'):
        summary += '.'

    return summary

def refine_with_gemini(bart_summaries):
    """
    Combine multiple BART summaries and refine them into one short,
    natural paragraph using Gemini.
    """
    if not bart_summaries:
        return "No summaries to refine."

    combined_text = " ".join(bart_summaries)
    prompt = f"""
    Combine and refine the following podcast segment summaries into one short paragraph (2–3 lines),
    written in third person and focused on the main discussion topic.
    Keep it natural, objective, and concise.
    ---
    {combined_text}
    """

    try:
        if gemini_model:
            response = gemini_model.generate_content(prompt)
            refined = response.text.strip()
            return refined if refined else combined_text
        else:
            return combined_text
    except Exception as e:
        print(f"⚠️ Gemini summarization failed: {e}")
        return combined_text