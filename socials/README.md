# Socials Video Generator

This script generates a TikTok/Instagram-style vertical slideshow video for a real estate listing, overlaying property stats on the images, with company music in the background.

## Features
- Fetches listing stats and images from the backend
- Creates a vertical (9:16) video slideshow
- Overlays stats text on all images
- Pans horizontal images for a dynamic effect (planned)
- Adds background music (replace `dummy_music.mp3` with your own)

## Requirements
- Python 3.7+
- `moviepy`, `pillow`, `requests`

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
```bash
python generate_social_video.py <property_id>
```

- Set the backend URL with the `BACKEND_URL` environment variable if not running on localhost.
- Place your company music as `dummy_music.mp3` in this folder to override the default.

## Output
- The script will generate a file named `property_<property_id>_social.mp4` in the current directory. 