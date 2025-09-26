# MIME Types Overview
A MIME type (Multipurpose Internet Mail Extensions type) is a standard way to indicate the nature and format of a file or data. It tells applications how to handle or interpret the content they receive.

MIME types follow a simple structure: `type/subtype`

**Common examples:**
- `text/html` - HTML web pages
- `text/plain` - Plain text files
- `image/jpeg` - JPEG images
- `image/png` - PNG images
- `application/pdf` - PDF documents
- `application/json` - JSON data
- `video/mp4` - MP4 video files
- `audio/mpeg` - MP3 audio files

**Where you'll encounter MIME types:**
- Web browsers use them to know how to display content (show an image, play a video, download a file)
- Email systems use them to handle attachments properly
- Web servers send MIME types in HTTP headers to tell browsers what kind of content they're receiving
- APIs often specify MIME types to indicate the format of data being sent or received

The system was originally designed for email attachments (hence "Mail Extensions" in the name) but is now used throughout the internet for content identification. When a web server sends a file to your browser, it includes the MIME type so the browser knows whether to display it as a webpage, show it as an image, prompt you to download it, or handle it in some other appropriate way.
