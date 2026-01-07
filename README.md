# Automated Podcast Segmenter and Tagger
This project is a Streamlit-based application that automates the process of fetching, transcribing, segmenting, and summarizing podcast episodes. It uses OpenAI Whisper for transcription, BERTopic for topic-based segmentation, and Google Gemini or BART models for summarization. The application provides a simple and interactive interface for users to explore podcast content efficiently.

---

## Features
- Podcast search and episode retrieval using the ListenNotes API  
- Automatic audio transcription using OpenAI Whisper  
- Intelligent transcript segmentation using BERTopic or time-based fallback  
- Summarization of segments using BART and Google Gemini  
- Caching and storage of transcripts and summaries for faster reprocessing  
- User-friendly interface built with Streamlit  

---

## Project Structure
AUTOMATED PODCAST SEGMENTER/
│
├── app.py                      # Main Streamlit app file
├── requirements.txt             # Dependencies file
├── .env                         # Environment file containing API keys
│
├── cache/                       # Stores cached transcripts and metadata
├── segment_store/                # Stores segmented and summarized transcripts
│
└── utils/
├── audio_processor.py        # Handles audio preprocessing using PyDub
├── listennotes_api.py        # Fetches podcasts and episodes using ListenNotes API
├── transcriber.py            # Transcribes audio files using Whisper
├── segmenter.py              # Segments transcripts by topics or time
├── summarizer.py             # Summarizes text using BART and Gemini
├── test.py                   # Utility or testing script



---

## Installation
### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/automated-podcast-segmenter.git
cd automated-podcast-segmenter
```

### Step 2: Create a Virtual Environment
```bash
python -m venv venv
```

Activate the environment:
```bash
# For Windows
venv\Scripts\activate
# For macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Environment Variables
Create a `.env` file in the project root and add the following:

```
LISTENNOTES_API_KEY=your_listennotes_api_key
GOOGLE_API_KEY=your_google_api_key
```

You can get a free ListenNotes API key from [https://www.listennotes.com/api/](https://www.listennotes.com/api/)
and a Gemini API key from [https://aistudio.google.com/](https://aistudio.google.com/).

---

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

Then open your browser and go to:

```
http://localhost:8501
```

### Steps to Use
1. Enter a podcast name in the search bar.
2. Select an episode from the search results.
3. The application will automatically:

   * Download and process the audio
   * Transcribe the content using Whisper
   * Segment the transcript intelligently
   * Summarize each segment
   * Display all results on the interface

---

## Technologies Used
| Purpose              | Tool / Library                                  |
| -------------------- | ----------------------------------------------- |
| Web Interface        | Streamlit                                       |
| Audio Transcription  | OpenAI Whisper                                  |
| Audio Processing     | PyDub                                           |
| Summarization        | Hugging Face Transformers (BART), Google Gemini |
| Topic Segmentation   | BERTopic, SentenceTransformers, UMAP, HDBSCAN   |
| Podcast Metadata     | ListenNotes API                                 |
| Environment Handling | Python-dotenv                                   |

---

## Data Storage
| Folder         | Description                                                     |
| -------------- | --------------------------------------------------------------- |
| cache/         | Stores raw transcript data and intermediate results             |
| segment_store/ | Stores segmented and summarized outputs                         |
| utils/         | Contains all utility scripts for processing and API integration |
| .env           | Contains sensitive environment variables                        |

The application uses caching to prevent redundant API calls and reprocessing.

---

## Future Enhancements
* Add export options for transcripts and summaries (PDF or text format)
* Support for multiple languages in transcription
* Integration with databases such as SQLite or MongoDB for caching and storage
* UI improvements using Streamlit components
* Enhanced summarization models for better topic context

---


## Author
Developed by T Aasritha
Year: 2025

An AI-powered system designed to simplify podcast analysis and improve accessibility to long-form audio content.

