import asyncio
import requests
from bs4 import BeautifulSoup
import json
import time
import os
import random 
from database import get_raw_url
from threading import Thread

def fetch_video_links():
    try:
        proxy_url = "https://cf-proxy.mrspidyxd.workers.dev/?host="
        base_url = "https://www.pornhub.com"
        url = ["https://www.pornhub.com", "https://www.pornhub.com/video?o=mv", "https://www.pornhub.com/video?o=ht", "https://www.pornhub.com/video?o=tr", "https://www.pornhub.com/video?o=cm"]
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        response = requests.get(proxy_url + random.choice(url), headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        return [div.find('a', class_='thumbnailTitle')['href'].replace("https://cf-proxy.mrspidyxd.workers.dev", base_url).split("&")[0] for div in soup.find_all('div', class_='vidTitleWrapper') if div.find('a', class_='thumbnailTitle')]
    except Exception as e:
        print(f"Error fetching video links: {e}")
        return []

def search_video_links(query):
    try:
        base_url = "https://cf-proxy.mrspidyxd.workers.dev/?host="
        search_url = "https://www.pornhub.com/video/search?search="
        url = "https://www.pornhub.com"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        response = requests.get(base_url + search_url + query, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        return [div.find('a', class_='thumbnailTitle')['href'].replace("https://cf-proxy.mrspidyxd.workers.dev", url).split("&")[0] for div in soup.find_all('div', class_='vidTitleWrapper') if div.find('a', class_='thumbnailTitle')]
    except Exception as e:
        print(f"Error searching video links for query {query}: {e}")
        return []

def extract_urls(url):
    try:
        temp_file = "dump.txt"
        os.system(f"yt-dlp --flat-playlist -j {url} > {temp_file}")
        urls = []
        with open(temp_file) as file:
            for line in file:
                parts = line.strip().split()
                for i in range(len(parts)):
                    if '"url":' == parts[i]:
                        urls.append(parts[i + 1].strip('"",'))
        os.remove(temp_file)
        return urls
    except Exception as e:
        print(f"Error extracting URLs from {url}: {e}")
        return []

def fetch_models():
    try:
        url = ["https://www.pornhub.com/pornstars?performerType=amateur#subFilterListVideos", "https://www.pornhub.com/pornstars?o=mp&t=a&gender=female&performerType=amateur", 'https://www.pornhub.com/pornstars?o=t#subFilterListVideos', "https://www.pornhub.com/pornstars?gender=female&performerType=amateur"]
        base_url = "https://www.pornhub.com"
        response = requests.get(random.choice(url))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        hrefs = set(link.get('href') for link in soup.find_all('a') if link.get('href'))
        return random.sample([base_url + href for href in hrefs if "/model/" in href or "/pornstar/" in href or "/channel/" in href], 5)
    except requests.RequestException as e:
        print(f"Error fetching models: {e}")
        return []

def send_message(text, chat_id):
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, data=payload)
        print(f"Message sent to chat ID {chat_id}.")
        print("Message Sent :" + str(response.json()['ok']))
    except Exception as e:
        print(f"Error sending message: {e}")

def read_file_links():
    try:
        with open("links.txt", 'r') as file:
            lines = file.readlines()
        return lines
    except FileNotFoundError:
        print(f"Error: The file at links.txt was not found.")
        return []
    except Exception as e:
        print(f"Error reading file links: {e}")
        return []

def get_link(db=None, collection_name=None):
    print("Started link_gen")
    try:
        urls = []
        print(read_file_links())
        time.sleep(10)
        for ph in fetch_models():
            urls.extend(extract_urls(ph))
        urls.extend(fetch_video_links())
        length = len(urls)
        print(f"Total Videos: {length}")
        
        if db is not None:
            data = get_raw_url(db, collection_name)
            urls = [url for url in urls if url not in data]
        filtered = len(urls)
        print(f"Filtered Videos: {filtered}")
        
        urls = random.sample(urls, 100)
        send_message(text=data, chat_id=LOG_ID)
        return urls
    except Exception as e:
        print(f"Error in get_link: {e}")
        return []
