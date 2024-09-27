import os
import logging
from pyrogram import Client, filters
import asyncio 
from datetime import datetime
import time
from tools import *
from config import *
from database import *
import static_ffmpeg
from video import *
from links import get_link,extract_urls

# Configure logging
logging.basicConfig(
    filename='Auto-PHVDL.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

db = connect_to_supabase()
table_name = TABLE_NAME


static_ffmpeg.add_paths()

# Create the Pyrogram client
app = Client("SpidyPHVDL", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN,workers=100)






async def main():
    async with app:
        video_urls = []
        video_urls = get_link(db,table_name)
        video_urls = video_urls[:100]
        uploading = []
        for video_url in video_urls:
            logging.info(video_url)
            video_hash = hash(video_url)
            download_dir = f'downloads/{video_hash}'
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            if len(uploading) >= 100:
                logging.info("Reached the limit of 100 videos. Stopping the download process.")
                break
            
            try:
                # Download the video
                downloaded_video_path = download_video(video_url, output_path=download_dir)

                exact_file_path = None
                thumbnail_path = None
                for root, dirs, files in os.walk(download_dir):
                    for file in files:
                        if file.endswith(('.mp4', '.mkv', '.webm')):
                            exact_file_path = os.path.join(root, file)
                        elif file.endswith(('.jpg', '.png', '.webp')):
                            thumbnail_path = os.path.join(root, file)
                        if exact_file_path and thumbnail_path and exact_file_path.split("/", 2)[-1] not in [uploads[0] for uploads in uploading]:
                                        uploading.append([exact_file_path.split("/", 2)[-1],video_url])
                                        await app.send_photo(LOG_ID,photo=thumbnail_path,caption= f"{video_url} is getting Uploaded")
                                        video = await upload_video(app, DRIVE_ID, exact_file_path, thumbnail_path)
                                        result = {
                                            "URL": video_url,
                                            "File_Name": exact_file_path.split("/", 2)[-1],
                                            "CHAT_ID": DRIVE_ID,    
                                         }
                                        insert_document(db, table_name, result)
                                        os.remove(exact_file_path)
                                        os.remove(thumbnail_path)
                else:
                    logging.error(f"Downloaded video or thumbnail file not found in '{download_dir}' directory.")
            except Exception as e:
                logging.error(f"An error occurred: {e}")

app.run(main())
