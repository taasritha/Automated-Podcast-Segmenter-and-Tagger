import os
import json
import math
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    from bertopic import BERTopic
    import umap
    import hdbscan
    USE_TOPIC_MODELING = True
except ImportError:
    USE_TOPIC_MODELING = False


def segment_transcript(segments, episode_title="Untitled_Episode", segment_length=300, use_topic_modeling=False, segment_store_dir="segment_store"):
    """
    Segment a podcast transcript via semantic topic modeling using SBERT + BERTopic,
    or fallback to time-based segmentation. Saves results to `segment_store` folder.

    Parameters:
        segments: list of {"start": float, "end": float, "text": str}
        episode_title: title of the episode (used as filename)
        segment_length: time-based fallback segment duration (seconds)
        use_topic_modeling: whether to use BERTopic
        segment_store_dir: directory to store the output file

    Returns:
        list of segment dicts like:
        [
            {"timeline": "00:00 – 03:45", "title": "Intro", "summary": "Episode starts..."},
            ...
        ]
    """

    if not segments:
        return []

    os.makedirs(segment_store_dir, exist_ok=True)
    safe_filename = "".join(c if c.isalnum() or c in "_-" else "_" for c in episode_title)
    output_path = os.path.join(segment_store_dir, f"{safe_filename}.json")


    # Semantic Topic Segmentation (SBERT + BERTopic)
    if use_topic_modeling and USE_TOPIC_MODELING:
        try:
            texts = [seg["text"] for seg in segments if seg.get("text")]
            timestamps = [(seg["start"], seg["end"]) for seg in segments]

            # SBERT Embeddings
            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = model.encode(texts, show_progress_bar=False)

            # BERTopic clustering
            topic_model = BERTopic(
                umap_model=umap.UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine'),
                hdbscan_model=hdbscan.HDBSCAN(min_cluster_size=3, metric='euclidean', cluster_selection_method='eom'),
                calculate_probabilities=True,
                verbose=False
            )
            topics, _ = topic_model.fit_transform(texts, embeddings)

            # Map topic transitions
            segmented = []
            current_topic = topics[0]
            current_start = timestamps[0][0]
            current_texts = [texts[0]]

            for i in range(1, len(topics)):
                if topics[i] != current_topic:
                    segmented.append({
                        "start": current_start,
                        "end": timestamps[i - 1][1],
                        "text": " ".join(current_texts).strip()
                    })
                    current_topic = topics[i]
                    current_start = timestamps[i][0]
                    current_texts = [texts[i]]
                else:
                    current_texts.append(texts[i])

            if current_texts:
                segmented.append({
                    "start": current_start,
                    "end": timestamps[-1][1],
                    "text": " ".join(current_texts).strip()
                })

        except Exception as e:
            print(f"[Warning] Semantic segmentation failed: {e}")
            print("→ Falling back to time-based segmentation.")
            segmented = _time_based_segmentation(segments, segment_length)
    else:
        segmented = _time_based_segmentation(segments, segment_length)

    # Convert segments to structured output
    final_segments = []
    for seg in segmented:
        timeline = f"{_format_time(seg['start'])} – {_format_time(seg['end'])}"
        final_segments.append({
            "timeline": timeline,
            "title": _generate_segment_title(seg["text"]),
            "summary": _generate_segment_summary(seg["text"])
        })

    # Save to JSON file in segment_store

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_segments, f, ensure_ascii=False, indent=4)

    print(f"Segments saved to {output_path}")
    return final_segments

def _time_based_segmentation(segments, segment_length):
    """Simple time-based segmentation fallback (~5 mins each)."""
    segmented = []
    current_text = []
    current_start = segments[0]["start"]
    current_end = current_start + segment_length

    for seg in segments:
        if seg["end"] <= current_end:
            current_text.append(seg["text"])
        else:
            segmented.append({
                "start": current_start,
                "end": current_end,
                "text": " ".join(current_text).strip()
            })
            current_start = current_end
            current_end = current_start + segment_length
            current_text = [seg["text"]]

    if current_text:
        segmented.append({
            "start": current_start,
            "end": current_end,
            "text": " ".join(current_text).strip()
        })

    return segmented


def _format_time(seconds):
    """Convert seconds → mm:ss format."""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def _generate_segment_title(text):
    """Generate a placeholder title (you can replace with LLM summary later)."""
    if not text.strip():
        return "Untitled Segment"
    words = text.split()
    snippet = " ".join(words[:8])
    return snippet[:70].strip().capitalize() + "..."


def _generate_segment_summary(text):
    """Generate a placeholder summary."""
    if not text.strip():
        return "No content available."
    words = text.split()
    return " ".join(words[:50]).strip().capitalize() + "..."
