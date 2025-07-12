# 🎥 SocialSnap Lite

SocialSnap Lite is a modern, user-friendly YouTube video and playlist downloader with a beautiful dark-themed interface. It supports downloading videos in various formats and qualities, with automatic audio-video merging capabilities.

## ✨ Features

- 🎯 Download single videos or entire playlists
- 🎨 Modern dark-themed UI with purple accents
- 📊 Real-time download progress tracking
- 🖼️ Video thumbnail preview
- 📝 Multiple format support (MP4, WebM)
- 🎵 Automatic audio-video merging
- 💫 Smooth animations and transitions

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/UTKARSHKUMAR712/SocialSnap-Lite.git
cd SocialSnap-Lite
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Download FFmpeg:
   - Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Place `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe` in the project root directory

## 🛠️ Usage

1. Run the application:
```bash
python main.py
```

2. Enter a YouTube video or playlist URL
3. Click "Detect Available Formats"
4. Select your preferred format from the dropdown
5. Click "Download"
6. Find your downloaded videos in the "Downloads/SocialSnap" folder

## 🔧 Requirements

- Python 3.7+
- yt-dlp
- tkinter
- Pillow
- FFmpeg

## 🎯 Technical Details

- Built with Python's tkinter for the GUI
- Uses yt-dlp for video downloading
- FFmpeg for audio-video merging
- Supports high-resolution video downloads
- Multi-threaded downloading for better performance
- Automatic audio stream selection for best quality

## 🔒 Security

- HTTPS support for secure downloads
- Certificate verification bypass option available
- Safe filename handling
- Error handling for failed downloads

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
