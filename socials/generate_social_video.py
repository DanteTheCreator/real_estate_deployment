import os
import sys
import requests
from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip, TextClip, AudioFileClip
from PIL import Image
from io import BytesIO

# --- CONFIG ---
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
DUMMY_AUDIO_PATH = os.path.join(os.path.dirname(__file__), "dummy_music.mp3")
VIDEO_SIZE = (720, 1280)  # Vertical 9:16
IMAGE_DISPLAY_DURATION = 2.5  # seconds per image
FONT = "Arial-Bold"
FONT_SIZE = 48
FONT_COLOR = "white"
STATS_BG_COLOR = "rgba(0,0,0,0.5)"


def fetch_property_stats(property_id):
    resp = requests.get(f"{BACKEND_URL}/properties/{property_id}")
    resp.raise_for_status()
    return resp.json()

def fetch_property_images(property_id):
    resp = requests.get(f"{BACKEND_URL}/properties/{property_id}/images")
    resp.raise_for_status()
    return resp.json()

def download_image(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content))

def make_vertical(image: Image.Image):
    # Pad or crop to vertical VIDEO_SIZE
    img = image.convert("RGB")
    img_ratio = img.width / img.height
    target_ratio = VIDEO_SIZE[0] / VIDEO_SIZE[1]
    if img_ratio > target_ratio:
        # Wider than vertical, crop sides
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        # Taller, pad sides
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop((0, top, img.width, top + new_height))
    return img.resize(VIDEO_SIZE)

def create_slideshow(images, stats_text, audio_path):
    clips = []
    for img in images:
        img_clip = ImageClip(img).set_duration(IMAGE_DISPLAY_DURATION)
        # Overlay stats
        txt_clip = TextClip(stats_text, fontsize=FONT_SIZE, font=FONT, color=FONT_COLOR, size=(VIDEO_SIZE[0]-40, None), method='caption', align='South')
        txt_clip = txt_clip.set_position((20, VIDEO_SIZE[1]-txt_clip.h-40)).set_duration(IMAGE_DISPLAY_DURATION)
        composite = CompositeVideoClip([img_clip, txt_clip], size=VIDEO_SIZE)
        clips.append(composite)
    video = concatenate_videoclips(clips, method="compose")
    if os.path.exists(audio_path):
        audio = AudioFileClip(audio_path).subclip(0, video.duration)
        video = video.set_audio(audio)
    return video

def main(property_id):
    print(f"Fetching property {property_id}...")
    stats = fetch_property_stats(property_id)
    images_meta = fetch_property_images(property_id)
    if not images_meta:
        print("No images found for this property.")
        sys.exit(1)
    # Compose stats text
    stats_text = f"{stats.get('title', 'Listing')}\nPrice: {stats.get('price', 'N/A')} {stats.get('currency', '')}\nRooms: {stats.get('bedrooms', 'N/A')} | {stats.get('bathrooms', 'N/A')} baths\nArea: {stats.get('area', 'N/A')} m²\nLocation: {stats.get('city', '')}, {stats.get('state', '')}"
    # Download and process images
    images = []
    for img_meta in images_meta:
        url = img_meta.get('url')
        if not url:
            continue
        img = download_image(url)
        img = make_vertical(img)
        images.append(img)
    if not images:
        print("No valid images downloaded.")
        sys.exit(1)
    # Create video
    print("Creating video...")
    video = create_slideshow(images, stats_text, DUMMY_AUDIO_PATH)
    out_path = f"property_{property_id}_social.mp4"
    video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac")
    print(f"Video saved to {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_social_video.py <property_id>")
        sys.exit(1)
    main(sys.argv[1]) 