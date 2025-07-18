#!/usr/bin/env python3
"""
Complete MinIO setup script for real estate project
Creates bucket, uploads mock images, and configures public access
"""

from minio import Minio
from minio.error import S3Error
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import io
import random

def create_minio_client():
    """Create MinIO client"""
    return Minio(
        "127.0.0.1:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

def create_mock_image(width=800, height=600, filename=""):
    """Create a mock property image"""
    # Create image with gradient background
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for i in range(height):
        r = int(255 * (1 - i / height))
        g = int(200 * (1 - i / height))
        b = int(150 * (1 - i / height))
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # Add some geometric shapes to make it look like a property
    # House shape
    house_width = width // 3
    house_height = height // 3
    house_x = (width - house_width) // 2
    house_y = (height - house_height) // 2
    
    # House body
    draw.rectangle([house_x, house_y + house_height//3, 
                   house_x + house_width, house_y + house_height], 
                  fill=(180, 150, 120))
    
    # Roof
    roof_points = [
        (house_x, house_y + house_height//3),
        (house_x + house_width//2, house_y),
        (house_x + house_width, house_y + house_height//3)
    ]
    draw.polygon(roof_points, fill=(120, 80, 60))
    
    # Door
    door_width = house_width // 6
    door_height = house_height // 3
    door_x = house_x + house_width//2 - door_width//2
    door_y = house_y + house_height - door_height
    draw.rectangle([door_x, door_y, door_x + door_width, door_y + door_height], 
                  fill=(80, 40, 20))
    
    # Windows
    window_size = house_width // 8
    window_y = house_y + house_height//2
    # Left window
    draw.rectangle([house_x + house_width//4 - window_size//2, window_y,
                   house_x + house_width//4 + window_size//2, window_y + window_size], 
                  fill=(100, 150, 200))
    # Right window
    draw.rectangle([house_x + 3*house_width//4 - window_size//2, window_y,
                   house_x + 3*house_width//4 + window_size//2, window_y + window_size], 
                  fill=(100, 150, 200))
    
    # Add text
    try:
        # Try to use a font, fallback to default if not available
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    text = f"Property Image\n{filename}"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = height - text_height - 20
    
    # Add text background
    draw.rectangle([text_x - 10, text_y - 10, text_x + text_width + 10, text_y + text_height + 10], 
                  fill=(255, 255, 255, 200))
    draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def setup_real_estate_bucket():
    """Set up the real-estate bucket with mock images"""
    client = create_minio_client()
    bucket_name = "real-estate"
    
    try:
        # Create bucket if it doesn't exist
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"✅ Created bucket: {bucket_name}")
        else:
            print(f"✅ Bucket {bucket_name} already exists")
        
        # List of expected image files based on the database
        expected_images = [
            "30600318.png",
            "32764679.jpeg", 
            "34027421.jpeg",
            "35239143.jpeg",
            "35392496.jpeg",
            "36364715.png",
            "36545477.jpeg",
            "49587310.png"
        ]
        
        # Check which images already exist
        existing_objects = {obj.object_name for obj in client.list_objects(bucket_name, recursive=True)}
        
        # Create and upload missing images
        uploaded_count = 0
        for image_name in expected_images:
            if image_name not in existing_objects:
                print(f"📸 Creating mock image: {image_name}")
                
                # Create different sized images for variety
                width = random.randint(600, 1000)
                height = random.randint(400, 700)
                
                img_data = create_mock_image(width, height, image_name)
                
                # Determine content type
                if image_name.endswith('.png'):
                    content_type = "image/png"
                else:
                    content_type = "image/jpeg"
                
                # Upload to MinIO
                client.put_object(
                    bucket_name,
                    image_name,
                    img_data,
                    length=img_data.getbuffer().nbytes,
                    content_type=content_type
                )
                
                print(f"✅ Uploaded: {image_name}")
                uploaded_count += 1
            else:
                print(f"⏭️  Already exists: {image_name}")
        
        print(f"\n📊 Upload Summary: {uploaded_count} new images uploaded")
        
        # Configure public access
        configure_public_access(client, bucket_name)
        
        # List all objects in bucket
        print(f"\n📦 Final bucket contents:")
        objects = list(client.list_objects(bucket_name, recursive=True))
        for obj in objects:
            print(f"  🖼️  http://127.0.0.1:9000/{bucket_name}/{obj.object_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up bucket: {e}")
        return False

def configure_public_access(client, bucket_name):
    """Configure bucket for public read access"""
    try:
        # Define public read policy
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*", 
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                }
            ]
        }
        
        # Apply the policy
        client.set_bucket_policy(bucket_name, json.dumps(policy))
        print(f"✅ Configured public read access for {bucket_name}")
        
        # Verify access with a test
        verify_public_access(client, bucket_name)
        
    except Exception as e:
        print(f"❌ Error configuring public access: {e}")

def verify_public_access(client, bucket_name):
    """Verify public access is working"""
    try:
        import urllib.request
        import urllib.error
        
        objects = list(client.list_objects(bucket_name, recursive=True))
        if objects:
            test_object = objects[0].object_name
            test_url = f"http://127.0.0.1:9000/{bucket_name}/{test_object}"
            
            print(f"🧪 Testing public access: {test_url}")
            
            try:
                response = urllib.request.urlopen(test_url)
                if response.status == 200:
                    print("✅ Public access verified!")
                else:
                    print(f"❌ Public access failed: {response.status}")
            except urllib.error.HTTPError as e:
                print(f"❌ Public access failed: {e.code} - {e.reason}")
        
    except Exception as e:
        print(f"❌ Error verifying access: {e}")

if __name__ == "__main__":
    print("🏠 Real Estate MinIO Complete Setup")
    print("=" * 50)
    
    # Check if PIL is available
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("❌ PIL (Pillow) is required to create mock images")
        print("Install with: pip install Pillow")
        sys.exit(1)
    
    if setup_real_estate_bucket():
        print("\n🎉 MinIO setup complete!")
        print("\n📝 Next steps:")
        print("1. Restart your FastAPI backend")
        print("2. Test the frontend - images should now load")
        print("3. Visit: http://localhost:8080")
    else:
        print("❌ Setup failed")
