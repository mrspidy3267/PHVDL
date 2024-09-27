import requests
from bs4 import BeautifulSoup
import os
import random
import subprocess
from config import *
from database import get_raw_url

def fetch_video_links():
    try:
        proxy_url = "https://cf-proxy.mrspidyxd.workers.dev/?host="
        base_url = "https://www.pornhub.com"
        urls = [
            "https://www.pornhub.com",
            "https://www.pornhub.com/video?o=mv",
            "https://www.pornhub.com/video?o=ht",
            "https://www.pornhub.com/video?o=tr",
            "https://www.pornhub.com/video?o=cm"
        ]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        
        response = requests.get(proxy_url + random.choice(urls), headers=headers)
        response.raise_for_status()  # Check if request was successful
        soup = BeautifulSoup(response.content, 'html.parser')

        return [
            div.find('a', class_='thumbnailTitle')['href'].replace("https://cf-proxy.mrspidyxd.workers.dev", base_url).split("&")[0]
            for div in soup.find_all('div', class_='vidTitleWrapper') if div.find('a', class_='thumbnailTitle')
        ]
    except requests.RequestException as e:
        return []

def search_video_links(query):
    try:
        proxy_url = "https://cf-proxy.mrspidyxd.workers.dev/?host="
        search_url = "https://www.pornhub.com/video/search?search="
        url = "https://www.pornhub.com"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        
        response = requests.get(proxy_url + search_url + query, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        return [
            div.find('a', class_='thumbnailTitle')['href'].replace("https://cf-proxy.mrspidyxd.workers.dev", url).split("&")[0]
            for div in soup.find_all('div', class_='vidTitleWrapper') if div.find('a', class_='thumbnailTitle')
        ]
    except requests.RequestException as e:
        return []

def extract_urls(url):
    try:
        result = subprocess.run(['yt-dlp', '--flat-playlist', '-j', url], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout
            urls = []
            for line in output.strip().splitlines():
                parts = line.strip().split()
                for i in range(len(parts)):
                    if '"url":' == parts[i]:
                        urls.append(parts[i + 1].strip('"', ','))
            return urls
        else:
            return []
    except Exception as e:
        return []

def fetch_models():
    try:
        urls = [
            "https://www.pornhub.com/pornstars?performerType=amateur#subFilterListVideos",
            "https://www.pornhub.com/pornstars?o=mp&t=a&gender=female&performerType=amateur",
            'https://www.pornhub.com/pornstars?o=t#subFilterListVideos',
            "https://www.pornhub.com/pornstars?gender=female&performerType=amateur"
        ]
        base_url = "https://www.pornhub.com"
        response = requests.get(random.choice(urls))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        hrefs = set(link.get('href') for link in soup.find_all('a') if link.get('href'))
        return random.sample(
            [base_url + href for href in hrefs if "/model/" in href or "/pornstar/" in href or "/channel/" in href],
            5
        )
    except requests.RequestException as e:
        return []

def send_message(text, chat_id):
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, data=payload)
        
        if response.status_code != 200:
            # Handle unsuccessful response
            pass
    except Exception as e:
        pass

def read_file_links():
    file_path = "links.txt"
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        return lines
    except FileNotFoundError:
        return []
    except Exception as e:
        return []

def get_link(db=None, collection_name=None):
    try:
        urls = []
        for ph in fetch_models():
            urls.extend(extract_urls(ph))
        urls.extend(fetch_video_links())
        length = len(urls)

        if db is not None:
            data = get_raw_url(db, collection_name)
            urls = [url for url in urls if url not in data]

        if urls:
            urls = random.sample(urls, min(100, len(urls)))  # Ensure we don't sample more than available
            send_message(text=data, chat_id=LOG_ID)
        return urls
    except Exception as e:
        return []
