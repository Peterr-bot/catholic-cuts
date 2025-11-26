"""Catholic Cuts - Gothic-themed Streamlit app for viral clip extraction.

Main user interface with dark Catholic theme, stained glass aesthetics,
and drag-and-drop functionality for video and transcript processing.
"""

import streamlit as st
import traceback
import sys
import os
from typing import Optional, Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import config
from src.transcript_utils import get_transcript_from_youtube
from src.llm_client import extract_moments
from src.cutsheets import generate_cut_sheets
from src.export_utils import to_csv, to_markdown, format_clip_summary
from src.export_utils_pdf import clips_to_pdf
from src.audio_utils import transcribe_video_to_text, get_supported_video_formats, format_file_size


def inject_catholic_gothic_css():
    """Inject CSS for dark Catholic Gothic theme with stained glass overlay."""
    css = """
    <style>
    /* Import Gothic fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Cinzel+Decorative:wght@700;900&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

    /* === STAINED GLASS BACKGROUND (VISIBLE) === */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("https://images.pexels.com/photos/2081166/pexels-photo-2081166.jpeg");
        background-size: cover;
        background-position: center;
        opacity: 0.45;
        filter: blur(3px) saturate(1.25);
        z-index: -2;
        pointer-events: none;
    }

    /* Dark veil for readability */
    .stApp::after {
        content: "";
        position: fixed;
        inset: 0;
        background: radial-gradient(
            circle at top,
            rgba(0, 0, 0, 0.55) 0%,
            rgba(0, 0, 0, 0.85) 45%,
            rgba(0, 0, 0, 0.96) 100%
        );
        z-index: -1;
        pointer-events: none;
    }

    /* Main app container */
    .stApp {
        background: linear-gradient(180deg,
                   rgba(20, 20, 25, 1) 0%,
                   rgba(15, 15, 20, 1) 50%,
                   rgba(10, 10, 15, 1) 100%);
        color: #E8E8E8 !important;
        font-family: 'Crimson Text', serif;
    }

    /* Catholic Cuts card styling */
    .cc-card {
        background: rgba(30, 30, 35, 0.85) !important;
        border: 1px solid rgba(184, 134, 11, 0.3) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        position: relative;
    }

    .cc-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg,
                   rgba(184, 134, 11, 0.1) 0%,
                   transparent 50%,
                   rgba(218, 165, 32, 0.05) 100%);
        border-radius: 12px;
        pointer-events: none;
    }

    /* Gothic title styling */
    .cc-title {
        font-family: 'Cinzel Decorative', cursive !important;
        font-size: 3rem !important;
        font-weight: 900 !important;
        text-align: center !important;
        background: linear-gradient(45deg,
                   #DAA520 0%,
                   #FFD700 30%,
                   #B8860B 70%,
                   #DAA520 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5) !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: 2px !important;
    }

    .cc-subtitle {
        font-family: 'Cinzel', serif !important;
        font-size: 1.1rem !important;
        text-align: center !important;
        color: #C0C0C0 !important;
        font-style: italic !important;
        margin-bottom: 2rem !important;
        letter-spacing: 1px !important;
    }

    /* Dropzone styling */
    .cc-dropzone {
        border: 2px dashed rgba(184, 134, 11, 0.5) !important;
        border-radius: 8px !important;
        padding: 2rem !important;
        text-align: center !important;
        background: rgba(40, 40, 45, 0.6) !important;
        transition: all 0.3s ease !important;
    }

    .cc-dropzone:hover {
        border-color: rgba(218, 165, 32, 0.8) !important;
        background: rgba(45, 45, 50, 0.8) !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg,
                   #B8860B 0%,
                   #DAA520 50%,
                   #B8860B 100%) !important;
        color: #000 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(184, 134, 11, 0.3) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg,
                   #DAA520 0%,
                   #FFD700 50%,
                   #DAA520 100%) !important;
        box-shadow: 0 6px 20px rgba(218, 165, 32, 0.4) !important;
        transform: translateY(-2px) !important;
    }

    /* Input styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: rgba(25, 25, 30, 0.8) !important;
        border: 1px solid rgba(184, 134, 11, 0.3) !important;
        border-radius: 6px !important;
        color: #E8E8E8 !important;
        font-family: 'Crimson Text', serif !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: rgba(218, 165, 32, 0.6) !important;
        box-shadow: 0 0 0 0.2rem rgba(184, 134, 11, 0.25) !important;
    }

    /* File uploader styling */
    .stFileUploader {
        background: rgba(30, 30, 35, 0.6) !important;
        border: 2px dashed rgba(184, 134, 11, 0.4) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }

    .stFileUploader:hover {
        border-color: rgba(218, 165, 32, 0.7) !important;
    }

    /* Section headers */
    .stSubheader, h2, h3 {
        font-family: 'Cinzel', serif !important;
        color: #DAA520 !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
    }

    /* Results section */
    .cc-results {
        margin-top: 2rem;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(40, 40, 45, 0.8) !important;
        border: 1px solid rgba(184, 134, 11, 0.2) !important;
        border-radius: 6px !important;
        color: #E8E8E8 !important;
        font-family: 'Cinzel', serif !important;
    }

    .streamlit-expanderContent {
        background: rgba(25, 25, 30, 0.9) !important;
        border: 1px solid rgba(184, 134, 11, 0.2) !important;
        border-top: none !important;
    }

    /* Metric styling */
    .metric-container {
        background: rgba(35, 35, 40, 0.7) !important;
        border: 1px solid rgba(184, 134, 11, 0.3) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }

    /* Progress bar */
    .stProgress .st-bo {
        background: linear-gradient(90deg, #B8860B, #DAA520) !important;
    }

    /* Info/success/error messages */
    .stAlert {
        background: rgba(30, 30, 35, 0.9) !important;
        border-left: 4px solid #DAA520 !important;
        color: #E8E8E8 !important;
        font-family: 'Crimson Text', serif !important;
    }

    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg,
                   #8B4513 0%,
                   #A0522D 50%,
                   #8B4513 100%) !important;
        color: #FFE4B5 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(135deg,
                   #A0522D 0%,
                   #CD853F 50%,
                   #A0522D 100%) !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def run_catholic_cuts(transcript_text: str, source_id: str) -> tuple:
    """Unified pipeline entry point for Catholic Cuts processing.

    Args:
        transcript_text: The transcript to process
        source_id: Identifier for the source (URL, filename, etc.)

    Returns:
        Tuple of (moments_with_cuts, metadata) or None on error
    """
    try:
        # Create basic metadata
        metadata = {
            "source_id": source_id,
            "title": f"Catholic Cuts - {source_id}",
            "source_type": "manual" if not source_id.startswith("http") else "youtube"
        }

        # Extract moments using existing LLM client
        st.info("🎯 **Extracting viral moments...**")
        moments = extract_moments(transcript_text, metadata)

        if not moments:
            st.warning("⚠️ No viral moments found in the transcript.")
            return None, None

        st.success(f"✅ Found {len(moments)} potential viral moments")

        # Generate cut sheets using existing function
        st.info("📋 **Generating editor cut sheets...**")
        moments_with_cuts = generate_cut_sheets(moments)
        st.success("✅ Cut sheets generated successfully")

        return moments_with_cuts, metadata

    except Exception as e:
        st.error(f"❌ **Processing failed:** {str(e)}")
        with st.expander("🔍 **Technical Details**"):
            st.code(traceback.format_exc())
        return None, None


def render_input_section():
    """Render the input section with drag-and-drop uploaders."""
    st.markdown('<div class="cc-card">', unsafe_allow_html=True)
    st.markdown("## 📝 **Input Methods**")

    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["📄 **Transcript File**", "🎥 **Video Upload**", "🔗 **YouTube URL**"])

    with tab1:
        st.markdown("### Upload Transcript File")
        st.markdown("*Upload a .txt or .md file containing your transcript*")

        transcript_file = st.file_uploader(
            "Choose transcript file",
            type=['txt', 'md'],
            help="Upload a text or markdown file containing the transcript",
            key="transcript_uploader"
        )

        if transcript_file:
            try:
                # Read the uploaded file
                transcript_text = str(transcript_file.read(), "utf-8").strip()

                if transcript_text:
                    st.success(f"✅ **Transcript loaded:** {len(transcript_text)} characters")

                    # Show preview
                    with st.expander("👀 **Preview Transcript**"):
                        st.text_area("Transcript Preview", transcript_text[:500] + "..." if len(transcript_text) > 500 else transcript_text, height=150, disabled=True)

                    # Process button
                    if st.button("🚀 **Process Transcript**", type="primary", key="process_transcript"):
                        process_content(transcript_text, transcript_file.name)
                else:
                    st.error("⚠️ **Uploaded file appears to be empty**")

            except Exception as e:
                st.error(f"❌ **Error reading file:** {str(e)}")

    with tab2:
        st.markdown("### Upload Video File")
        st.markdown("*Upload a video file for automatic transcription using AI*")

        # Show supported formats
        formats = get_supported_video_formats()
        st.caption(f"**Supported formats:** {', '.join(formats)} • **Max size:** 25MB")
        st.caption("⚠️ **Cloud deployment note:** .mov/.mkv/.avi not supported on Streamlit Community Cloud")

        video_file = st.file_uploader(
            "Choose video file",
            type=[fmt[1:] for fmt in formats],  # Remove the dot from extensions
            help="Upload a video file to transcribe using OpenAI Whisper",
            key="video_uploader"
        )

        if video_file:
            # Show file info
            file_size = format_file_size(video_file.size)
            st.info(f"📁 **File:** {video_file.name} ({file_size})")

            # Check file size
            if video_file.size > 25 * 1024 * 1024:  # 25MB limit
                st.error("❌ **File too large.** Please upload a video smaller than 25MB.")
            else:
                if st.button("🎙️ **Transcribe Video**", type="primary", key="transcribe_video"):
                    with st.spinner("🔄 **Transcribing video using AI...** This may take a few minutes."):
                        try:
                            transcript_text = transcribe_video_to_text(video_file)
                            if transcript_text:
                                st.success("✅ **Video transcribed successfully!**")

                                # Show preview
                                with st.expander("👀 **Preview Transcript**"):
                                    st.text_area("Transcript Preview", transcript_text[:500] + "..." if len(transcript_text) > 500 else transcript_text, height=150, disabled=True)

                                # Process the transcription
                                process_content(transcript_text, f"video-{video_file.name}")
                            else:
                                st.error("❌ **Transcription failed - no text extracted**")
                        except Exception as e:
                            st.error(f"❌ **Transcription error:** {str(e)}")

    with tab3:
        st.markdown("### YouTube URL")
        st.markdown("*Enter a YouTube URL to fetch the transcript automatically*")

        col1, col2 = st.columns([3, 1])

        with col1:
            youtube_url = st.text_input(
                "YouTube URL",
                placeholder="https://youtube.com/watch?v=dQw4w9WgXcQ",
                help="Accepts any YouTube format: watch, youtu.be, shorts, embed"
            )

        with col2:
            language = st.selectbox(
                "Language",
                options=["en", "es", "fr", "de", "it", "pt"],
                index=0,
                help="Transcript language"
            )

        if youtube_url.strip():
            if st.button("📺 **Fetch from YouTube**", type="primary", key="fetch_youtube"):
                with st.spinner("🔄 **Fetching transcript from YouTube...**"):
                    try:
                        transcript_text, metadata = get_transcript_from_youtube(youtube_url, language)
                        if transcript_text:
                            st.success("✅ **YouTube transcript fetched successfully!**")

                            # Show video metadata
                            if metadata:
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    if metadata.get("title"):
                                        st.metric("**Title**", f"📺 {metadata['title'][:30]}...")
                                with col2:
                                    if metadata.get("duration_seconds"):
                                        duration = metadata["duration_seconds"]
                                        mins, secs = divmod(duration, 60)
                                        st.metric("**Duration**", f"⏱️ {mins}m {secs}s")
                                with col3:
                                    if metadata.get("view_count"):
                                        st.metric("**Views**", f"👀 {metadata['view_count']:,}")

                            # Process the transcript
                            process_content(transcript_text, youtube_url, metadata)
                        else:
                            st.error("❌ **No transcript found for this video**")
                    except Exception as e:
                        st.error(f"❌ **YouTube fetch error:** {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)


def render_settings_section():
    """Render the settings/configuration section."""
    st.markdown('<div class="cc-card">', unsafe_allow_html=True)
    st.markdown("## ⚙️ **Settings**")

    # Performance settings
    st.markdown("### 🚀 **Performance**")

    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.number_input(
            "**Chunk Size (chars)**",
            min_value=5000,
            max_value=15000,
            value=config.CHARS_PER_CHUNK,
            step=1000,
            help="Larger chunks = fewer API calls but may reduce accuracy"
        )

    with col2:
        max_moments = st.number_input(
            "**Max Moments/Chunk**",
            min_value=1,
            max_value=10,
            value=config.MAX_MOMENTS_PER_CHUNK,
            help="Maximum viral moments to extract per chunk"
        )

    # Cache settings
    st.markdown("### 💾 **Cache**")
    cache_enabled = st.checkbox("**Enable Caching**", value=config.CACHE_ENABLED, help="Cache results to speed up re-processing")

    if cache_enabled and st.button("🗑️ **Clear Cache**", key="clear_cache"):
        try:
            from src.cache_utils import clear_cache
            clear_cache()
            st.success("✅ **Cache cleared successfully**")
        except Exception as e:
            st.error(f"❌ **Error clearing cache:** {str(e)}")

    # Model settings
    st.markdown("### 🤖 **AI Model**")
    st.info(f"**Primary Model:** {config.PRIMARY_MODEL}")
    st.info(f"**Fast Model:** {config.FAST_MODEL}")

    st.markdown('</div>', unsafe_allow_html=True)


def process_content(transcript_text: str, source_id: str, metadata: Dict = None):
    """Process content through the Catholic Cuts pipeline and store results."""
    # NOTE: We do NOT render inside this function anymore; main() will call
    # render_results_section() exactly once to avoid duplicate Streamlit elements.
    with st.spinner("⚡ **Processing through Catholic Cuts pipeline...**"):
        moments_with_cuts, processed_metadata = run_catholic_cuts(
            transcript_text, source_id
        )

        if moments_with_cuts:
            final_metadata = metadata or processed_metadata
            st.session_state.moments_with_cuts = moments_with_cuts
            st.session_state.metadata = final_metadata
            st.session_state.transcript_text = transcript_text


def render_results_section():
    """Render the results section with clips and export options."""
    if "moments_with_cuts" not in st.session_state:
        return

    moments_with_cuts = st.session_state.moments_with_cuts
    metadata = st.session_state.get("metadata", {})

    st.markdown('<div class="cc-card cc-results">', unsafe_allow_html=True)
    st.markdown("## 🎬 **Results**")

    # Display summary
    summary = format_clip_summary(moments_with_cuts)
    st.info(f"📊 **Summary:** {summary}")

    # Display video metadata if available
    if metadata and metadata.get("title"):
        st.markdown("### 🎥 **Source Information**")
        col1, col2, col3 = st.columns(3)

        with col1:
            if metadata.get("title"):
                st.markdown(f"**📺 Title:** {metadata['title']}")
            if metadata.get("channel_name"):
                st.markdown(f"**👤 Channel:** {metadata['channel_name']}")

        with col2:
            if metadata.get("duration_seconds"):
                duration = metadata["duration_seconds"]
                mins, secs = divmod(duration, 60)
                st.markdown(f"**⏱️ Duration:** {mins}m {secs}s")
            if metadata.get("view_count"):
                st.markdown(f"**👀 Views:** {metadata['view_count']:,}")

        with col3:
            if metadata.get("like_count"):
                st.markdown(f"**👍 Likes:** {metadata['like_count']:,}")
            if metadata.get("url"):
                st.markdown(f"**🔗 [Watch Video]({metadata['url']})**")

    # Display clips
    if moments_with_cuts:
        st.markdown("### ✂️ **Viral Clips**")

        for i, moment in enumerate(moments_with_cuts, 1):
            cut_sheet = moment.get("editor_cut_sheet", {})

            # Create expander title
            timestamps = moment.get("timestamps", "")
            energy_tag = moment.get("energy_tag", "")
            viral_trigger = moment.get("viral_trigger", "")
            clip_label = cut_sheet.get("clip_label", f"CLIP_{i}")

            expander_title = f"**Clip {i}: {clip_label}** • {timestamps} • {energy_tag} • {viral_trigger}"

            with st.expander(expander_title):
                # Quote
                quote = moment.get("quote", "")
                if quote:
                    st.markdown("#### 💬 **Quote**")
                    st.markdown(f"> {quote}")

                col1, col2 = st.columns([1, 1])

                with col1:
                    # Moment details
                    st.markdown("#### 🎯 **Moment Details**")

                    why_hits = moment.get("why_it_hits", "")
                    if why_hits:
                        st.markdown(f"**Why it hits:** {why_hits}")

                    duration = moment.get("clip_duration_seconds", "")
                    if duration:
                        st.markdown(f"**Duration:** {duration} seconds")

                    flags = moment.get("flags", [])
                    if flags:
                        st.markdown(f"**Flags:** {', '.join(flags)}")

                    # Persona captions
                    st.markdown("#### 👥 **Persona Captions**")
                    personas = moment.get("persona_captions", {})

                    for persona_key, persona_name in [
                        ("historian", "Historian"),
                        ("thomist", "Thomist"),
                        ("ex_protestant", "Ex-Protestant"),
                        ("meme_catholic", "Meme Catholic"),
                        ("old_world_catholic", "Old World Catholic"),
                        ("catholic", "Catholic")
                    ]:
                        caption = personas.get(persona_key, "")
                        if caption:
                            st.markdown(f"**{persona_name}:** {caption}")

                with col2:
                    # Editor cut sheet
                    st.markdown("#### 📋 **Editor Cut Sheet**")

                    st.markdown(f"**In/Out Points:** {cut_sheet.get('in_point', 'N/A')} → {cut_sheet.get('out_point', 'N/A')}")
                    st.markdown(f"**Aspect Ratio:** {cut_sheet.get('aspect_ratio', '9:16')}")
                    st.markdown(f"**Crop Note:** {cut_sheet.get('crop_note', 'N/A')}")

                    hook = cut_sheet.get('opening_hook_subtitle', '')
                    if hook:
                        st.markdown(f"**Hook Subtitle:** {hook}")

                    emphasis = cut_sheet.get('emphasis_words_caps', [])
                    if emphasis:
                        st.markdown(f"**Emphasis Words:** {', '.join(emphasis)}")

                    st.markdown(f"**Pacing:** {cut_sheet.get('pacing_note', 'N/A')}")
                    st.markdown(f"**B-Roll:** {cut_sheet.get('b_roll_ideas', 'none')}")
                    st.markdown(f"**Text on Screen:** {cut_sheet.get('text_on_screen_idea', 'none')}")
                    st.markdown(f"**Silence Handling:** {cut_sheet.get('silence_handling', 'none')}")
                    st.markdown(f"**Thumbnail Text:** {cut_sheet.get('thumbnail_text', 'N/A')}")
                    st.markdown(f"**Thumbnail Cue:** {cut_sheet.get('thumbnail_face_cue', 'N/A')}")
                    st.markdown(f"**Platform Priority:** {cut_sheet.get('platform_priority', 'All')}")

                    default_caption = cut_sheet.get('use_persona_caption', '')
                    if default_caption:
                        st.markdown(f"**Default Caption:** {default_caption}")

        # Export section
        st.markdown("---")
        st.markdown("### 📥 **Export Options**")

        col1, col2, col3 = st.columns([1, 1, 1])

        try:
            # Generate export data
            csv_data = to_csv(moments_with_cuts)
            md_data = to_markdown(moments_with_cuts)
            pdf_data = clips_to_pdf(moments_with_cuts, metadata)

            # Use clip count in keys so they are always unique even across reruns
            key_suffix = len(moments_with_cuts)

            with col1:
                st.download_button(
                    label="📊 **Download CSV**",
                    data=csv_data,
                    file_name="catholic_cuts_clips.csv",
                    mime="text/csv",
                    key=f"export_csv_{key_suffix}",
                    help="Download as CSV for spreadsheet editing"
                )

            with col2:
                st.download_button(
                    label="📝 **Download Markdown**",
                    data=md_data,
                    file_name="catholic_cuts_clips.md",
                    mime="text/markdown",
                    key=f"export_md_{key_suffix}",
                    help="Download as Markdown for documentation"
                )

            with col3:
                st.download_button(
                    label="📄 **Download PDF**",
                    data=pdf_data,
                    file_name="catholic_cuts_clips.pdf",
                    mime="application/pdf",
                    key=f"export_pdf_{key_suffix}",
                    help="One cut-sheet PDF for editors"
                )

        except Exception as e:
            st.error(f"❌ **Export error:** {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Main Catholic Cuts Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title="Catholic Cuts",
        page_icon="✂️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize configuration
    try:
        config.validate_config()
    except RuntimeError as e:
        st.error(f"Configuration Error: {e}")
        st.info("Please set the required environment variables and restart the app.")
        st.stop()

    # Inject Catholic Gothic CSS
    inject_catholic_gothic_css()

    # App header with Gothic styling
    st.markdown('<h1 class="cc-title">✂️ Catholic Cuts</h1>', unsafe_allow_html=True)
    st.markdown('<p class="cc-subtitle">Catholic Viral Clip Extraction Tool</p>', unsafe_allow_html=True)

    # Two-column layout
    col1, col2 = st.columns([2, 1])

    with col1:
        render_input_section()

    with col2:
        render_settings_section()

    # Results section (full width)
    render_results_section()


if __name__ == "__main__":
    main()