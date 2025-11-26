# Catholic Cuts ✂️

Catholic Media Viral Moment Extraction Tool - Transform long-form Catholic content into shareable clips with AI-powered moment detection and editor cut sheets.

## Features

🎯 **AI-Powered Viral Moment Detection** - Extracts the most engaging segments from Catholic media using GPT-5.1
📋 **Professional Cut Sheets** - Generates detailed editor instructions with timestamps, hooks, and platform optimization
🎨 **Catholic Gothic UI** - Beautiful stained glass themed interface
📹 **Multi-Input Support** - YouTube URLs, direct transcript upload, or video file transcription
📊 **Export Options** - CSV, Markdown, and PDF formats for different workflows
⚡ **Performance Optimized** - Parallel processing with intelligent caching

## Quick Start

### Option 1: Streamlit Community Cloud (Recommended)

1. **Fork this repository** to your GitHub account

2. **Set up environment variables** in your Streamlit Cloud dashboard:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   APIFY_TOKEN=your_apify_token_here
   APIFY_ACTOR_ID=your_apify_actor_id_here
   ```

3. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your forked repository
   - Set the main file path: `src/app_streamlit.py`
   - Deploy!

### Option 2: Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/catholic-cuts.git
   cd catholic-cuts
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   APIFY_TOKEN=your_apify_token_here
   APIFY_ACTOR_ID=your_apify_actor_id_here
   ```

4. **Run the application**:
   ```bash
   streamlit run src/app_streamlit.py
   ```

## Required API Keys

### OpenAI API Key
- Used for GPT-5.1 moment extraction and Whisper transcription
- Get your key at: [platform.openai.com](https://platform.openai.com/api-keys)

### Apify Token & Actor ID
- Used for YouTube transcript extraction
- Sign up at: [apify.com](https://apify.com)
- Find your token in Account Settings
- Actor ID is for the YouTube transcript extractor

## Video File Support

**Cloud Deployment (Streamlit Community Cloud)**:
- ✅ Supported: `.mp4`, `.mp3`, `.wav`, `.webm`
- ❌ Not supported: `.mov`, `.mkv`, `.avi` (cloud limitations)

**Local Development**:
- ✅ All formats supported with ffmpeg conversion

**File size limit**: 25MB (OpenAI Whisper requirement)

## Usage

1. **Choose your input method**:
   - **YouTube URL**: Paste any YouTube video link
   - **Upload Transcript**: Direct text file upload
   - **Upload Video**: Video file transcription (cloud-safe formats only)

2. **Process content**: Click "🚀 Generate Viral Clips"

3. **Review results**:
   - Viral moments with energy tags and triggers
   - Professional cut sheets with timestamps
   - Persona-specific captions

4. **Export**: Download as CSV, Markdown, or PDF

## Configuration

The application uses several performance optimizations:

- **Chunk Size**: 9,000 characters per chunk for efficient processing
- **Parallel Processing**: Up to 3 concurrent chunks
- **Intelligent Caching**: Avoid reprocessing identical content
- **Moment Limits**: Maximum 3 moments per chunk, 5 total

## Project Structure

```
catholic-cuts/
├── src/
│   ├── app_streamlit.py       # Main Streamlit application
│   ├── audio_utils.py         # Cloud-safe video transcription
│   ├── llm_client.py          # OpenAI GPT integration
│   ├── transcript_utils.py    # YouTube transcript extraction
│   ├── cutsheets.py          # Cut sheet generation
│   ├── cache_utils.py        # Performance caching
│   ├── export_utils.py       # CSV/Markdown export
│   ├── export_utils_pdf.py   # PDF export
│   ├── extraction.py         # Response parsing
│   └── config.py             # Configuration management
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Troubleshooting

### Common Issues

**"Configuration Error: Missing required environment variable"**
- Ensure all three API keys are set in your environment or `.env` file

**"Video file too large"**
- Maximum file size is 25MB (OpenAI Whisper limit)
- Consider compressing the video or using YouTube upload instead

**"Unsupported format in cloud"**
- On Streamlit Community Cloud, only `.mp4`, `.mp3`, `.wav`, `.webm` are supported
- Convert unsupported formats before uploading

### Performance Tips

- Use YouTube URLs when possible for fastest processing
- Cache is enabled by default - identical content won't be reprocessed
- For large transcripts, the app automatically chunks content for optimal performance

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test locally: `streamlit run src/app_streamlit.py`
5. Submit a pull request

## License

This project is designed for Catholic media content creators and educators. Please respect copyright laws and usage rights when processing content.

---

*Built with ❤️ for the Catholic media community*