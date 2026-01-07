import streamlit as st
import os
import requests
import tempfile
import json
import time
import re

from utils.listennotes_api import search_podcast, get_episodes, get_audio_url
from utils.transcriber import transcribe_audio
from utils.segmenter import segment_transcript
from utils.summarizer import summarize_segments, refine_with_gemini

st.set_page_config(page_title="🎧 Podcast Segmenter & Tagger", layout="wide", page_icon="🎧")
st.title("🎧 Automated Podcast Segmenter & Tagger")

CACHE_DIR = "cache"
SEGMENT_STORE_DIR = "segment_store"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(SEGMENT_STORE_DIR, exist_ok=True)

def normalize_filename(s: str) -> str:
    """Normalize a string for safe and comparable filenames."""
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

def find_file_by_partial_match(directory, query):
    """Find file in directory that matches query after normalization."""
    if not os.path.exists(directory):
        return None
    q_norm = normalize_filename(query)
    for fname in os.listdir(directory):
        f_norm = normalize_filename(fname)
        if q_norm in f_norm or f_norm in q_norm:
            return os.path.join(directory, fname)
    return None

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def find_cached_metadata_for_query(query):
    """
    Find cached JSON in CACHE_DIR that partially matches query in filename or title.
    Returns tuple (data, path)
    """
    if not os.path.exists(CACHE_DIR):
        return None, None
    q = query.lower().strip()

    #Trying filename match
    for fname in os.listdir(CACHE_DIR):
        if q in fname.lower():
            path = os.path.join(CACHE_DIR, fname)
            data = load_json(path)
            if data:
                return data, path

    #Trying title match inside file content
    for fname in os.listdir(CACHE_DIR):
        path = os.path.join(CACHE_DIR, fname)
        data = load_json(path)
        if data and "title" in data and q in data["title"].lower():
            return data, path
    return None, None

def display_segments_from_file(segment_path):
    """Display timeline segments with nice styling."""
    segments = load_json(segment_path)
    if not segments:
        st.error("Segment file exists but could not be read.")
        return

    st.markdown("""
    <style>
    .timeline-box { background: #0f0f0f; border-radius: 12px; padding: 16px 20px; margin: 16px 0;
                   box-shadow: 0 1px 4px rgba(255,255,255,0.06); }
    .time-header { font-weight: 600; color: #60a5fa; font-size: 15px; margin-bottom: 6px; }
    .summary-text { font-size: 15px; line-height: 1.6; color: #e5e7eb; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

    st.subheader("🕒 Episode Timeline & Summaries")
    for seg in segments:
        timeline = seg.get("timeline", "")
        title = seg.get("title", "")
        summary = seg.get("summary", seg.get("text", ""))
        st.markdown(f"""
        <div class='timeline-box'>
            <div class='time-header'>{timeline} — {title}</div>
            <p class='summary-text'>{summary}</p>
        </div>
        """, unsafe_allow_html=True)


query = st.text_input("🔍 Enter Podcast Name or Episode Title", "")

if st.button("Search Podcast"):
    if not query.strip():
        st.warning("Please enter a podcast name or episode title.")
        st.stop()

    normalized_query = query.strip().lower()

    #Trying to find existing segment file
    segment_path = find_file_by_partial_match(SEGMENT_STORE_DIR, normalized_query)

    # If not found, check cache metadata and then use title to locate segment file
    if not segment_path:
        cached_meta, _ = find_cached_metadata_for_query(normalized_query)
        if cached_meta and "title" in cached_meta:
            segment_path = find_file_by_partial_match(SEGMENT_STORE_DIR, cached_meta["title"])

    if segment_path:
        st.info("Found podcast in cached data")
        cached_meta, _ = find_cached_metadata_for_query(normalized_query)

        if cached_meta and "audio_url" in cached_meta:
            st.subheader(cached_meta.get("title", "Cached Episode"))
            st.audio(cached_meta["audio_url"])
        else:
            st.warning("Audio metadata not found in cache for this segment (showing segments only).")

        with st.spinner("Loading cached segments..."):
            time.sleep(0.8)
            display_segments_from_file(segment_path)
            st.success("Cached segments displayed.")
        st.stop()

    # If no segment file, try cached metadata
    cached_meta, cached_meta_path = find_cached_metadata_for_query(normalized_query)
    if cached_meta:
        st.info(f"Found cached metadata: {cached_meta.get('title', os.path.basename(cached_meta_path))}")
        if "audio_url" in cached_meta:
            st.subheader(cached_meta.get("title", "Cached Episode"))
            st.audio(cached_meta["audio_url"])
        else:
            st.warning("Cached metadata found but no audio_url inside it.")

        # Trying to show segment file by cached title
        cached_title = cached_meta.get("title", "")
        seg_by_title = find_file_by_partial_match(SEGMENT_STORE_DIR, cached_title)
        if seg_by_title:
            with st.spinner("Loading cached segments for this cached episode..."):
                time.sleep(0.8)
                display_segments_from_file(seg_by_title)
                st.success("Cached segments displayed.")
        else:
            st.warning("No segment file found for this cached episode.")
        st.stop()

    # No cache found: Fetch from ListenNotes
    with st.spinner("No cache found — searching ListenNotes..."):
        podcasts = search_podcast(query)

    if not podcasts:
        st.error("⚠️ ListenNotes API limit exceeded or returned no results.")
        st.stop()

    # Let user select podcast
    st.subheader("Select a Podcast")
    selected_podcast = st.selectbox(
        "Available Podcasts",
        podcasts,
        format_func=lambda p: p.get("title_original", "Unnamed Podcast")
    )

    if not selected_podcast:
        st.error("No podcast selected.")
        st.stop()

    podcast_id = selected_podcast["id"]
    with st.spinner("Fetching episodes..."):
        episodes = get_episodes(podcast_id)

    if not episodes:
        st.error("⚠️ No episodes found for this podcast.")
        st.stop()

    selected_episode = st.selectbox(
        "Select an Episode",
        episodes,
        format_func=lambda e: e.get("title", "Untitled Episode")
    )

    if not selected_episode:
        st.stop()

    episode_id = selected_episode["id"]
    audio_url, title = get_audio_url(episode_id)
    if not audio_url:
        st.error("⚠️ No audio available for this episode.")
        st.stop()

    st.audio(audio_url)
    st.subheader(f"🎙️ {title}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        st.write("Downloading audio...")
        response = requests.get(audio_url)
        tmp_file.write(response.content)
        tmp_path = tmp_file.name

    with st.spinner("Transcribing audio..."):
        transcript = transcribe_audio(tmp_path)

    with st.spinner("Segmenting transcript..."):
        segments = segment_transcript(transcript)

    with st.spinner("Summarizing segments..."):
        segment_texts = [seg.get("text", "") for seg in segments if "text" in seg]
        combined_segments = [" ".join(segment_texts[i:i+3]) for i in range(0, len(segment_texts), 3)]
        bart_summaries = [summarize_segments(text) for text in combined_segments]
        gemini_summaries = [refine_with_gemini(text) for text in bart_summaries]

    # Save cache metadata and segment file for reuse
    safe_query_name = normalize_filename(normalized_query)
    meta_cache_path = os.path.join(CACHE_DIR, f"{safe_query_name}_{episode_id}.json")
    with open(meta_cache_path, "w", encoding="utf-8") as f:
        json.dump({"title": title, "audio_url": audio_url, "episode_id": episode_id}, f, indent=4)

    segment_file_path = os.path.join(SEGMENT_STORE_DIR, f"{episode_id}_{normalize_filename(title)}.json")
    segment_data = [{"timeline": f"Segment {i+1}", "title": f"Part {i+1}", "summary": s}
                    for i, s in enumerate(gemini_summaries)]
    with open(segment_file_path, "w", encoding="utf-8") as f:
        json.dump(segment_data, f, indent=4)

    st.success("Summaries generated successfully!")
    display_segments_from_file(segment_file_path)
    st.success("Processing complete!")
