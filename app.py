import os
import logging
from pyrogram import Client, filters
import asyncio 
from datetime import datetime
import time
from tools import *
from alive import keep_alive 
from config import *
from database import *
import static_ffmpeg
from video import *
from links import extract_urls




# Configure logging
logging.basicConfig(
    filename='PHVDL.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


database_name = "Spidydb"
db = connect_to_mongodb(DATABASE, database_name)
collection_name = COLLECTION_NAME

# Uncomment if needed
static_ffmpeg.add_paths()
keep_alive()


# Create the Pyrogram client
app = Client("Spidydb", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN,workers=100)


@app.on_message(filters.command("start"))
async def start_command(client, message):
    chat_id = message.chat.id
    await message.delete()
    welcome = await app.send_message(chat_id, "Send Any Yt-Dlp Supported Link to Download..")
    await asyncio.sleep(3)

   
    
@app.on_message(filters.command("speedtest"))
async def speedtest_command(client, message):
    chat_id = message.chat.id
    start = await app.send_message(chat_id, "<i>Initiating Speedtest...<i>")
    stats = get_speedtest_stats()
    caption = stats[1]
    photo = stats[0]
    await app.send_photo(chat_id, photo, caption)
    await start.delete()



@app.on_message(filters.command("stats"))
async def stats_command(client, message):
    chat_id = message.chat.id
    info = get_system_info()
    await app.send_message(chat_id,info)



@app.on_message(filters.text)
async def video(client, message):
    try:
        start_time = datetime.now()
        chat_id = message.chat.id

        if message.text.startswith("https://") or message.text.startswith("http://"):
            video_urls = [i.strip() for i in message.text.split()]
            if "model" in message.text or "channel" in message.text or "pornstar" in message.text:
                   video_urls = extract_urls(message.text.strip())
            await message.delete()
            uploading = []

            video_hash = hash(video_urls[0])
            download_dir = f'downloads/{video_hash}'
            status = await app.send_message(LOG_ID,f"Processing {len(video_urls)} video(s) [{video_hash}]")
            for video_url in video_urls:
                    if not os.path.exists(download_dir):
                            os.makedirs(download_dir)
           

                    if check_db(db,collection_name,video_url):
                        data = get_info(db,collection_name,video_url)
                        if chat_id != DUMP_ID:
                            await app.copy_message(chat_id,DUMP_ID,data["DMID"],caption=data['File_Name'])
                            uploading.append([data['File_Name'],video_url])
                        
                    else:
                            textst = f"""Processed {len(uploading)} Out Of {len(video_urls)}"""
                            if textst != status.text:
                                status = await status.edit_text(textst)
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
                                        video = await upload_video(app, chat_id, exact_file_path, thumbnail_path)
                                        if video:
                                            DM = await app.copy_message(DUMP_ID, video.chat.id,video.id,caption=f"""<b>File_Name:</b> <code>{exact_file_path.split("/", 2)[-1]}</code>\n<b>CHAT_ID:</b> <code>{chat_id}</code>""")
                                        result = {
                                            "DMID": DM.id,
                                            "DUMP_ID": DUMP_ID,
                                            "URL": video_url,
                                            "File_Name": exact_file_path.split("/", 2)[-1],
                                            "CHAT_ID": chat_id,
                                        }
                                        insert_document(db, collection_name, result)
                                        logging.info("Updated to Database!!")               
                                        os.remove(exact_file_path)
                                        os.remove(thumbnail_path)
                            else:
                                if len(uploading) == 0:
                                    logging.error(f"Downloaded video or thumbnail file not found in '{download_dir}' directory.")
            await status.delete()
            ST = await app.send_message(chat_id,f"{len(uploading)} Video/s Has Uploaded")
            await asyncio.sleep(3)
            await ST.delete()
                
    except Exception as e:
        print(e)
        status = await app.send_message(LOG_ID,f"Error Occurred: {e}")
        logging.error(f"An error occurred: {e}")


print("Bot Started")
app.run()
