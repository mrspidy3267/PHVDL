import requests
from bs4 import BeautifulSoup
import os
import random
import subprocess
import logging
from config import *
from database import get_raw_url

# Configure logging
logging.basicConfig(
    filename='app.log', 
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

        logging.info("Fetched video links successfully.")
        return [
            div.find('a', class_='thumbnailTitle')['href'].replace("https://cf-proxy.mrspidyxd.workers.dev", base_url).split("&")[0]
            for div in soup.find_all('div', class_='vidTitleWrapper') if div.find('a', class_='thumbnailTitle')
        ]
    except requests.RequestException as e:
        logging.error(f"Error fetching video links: {e}")
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

        logging.info(f"Search for query '{query}' completed.")
        return [
            div.find('a', class_='thumbnailTitle')['href'].replace("https://cf-proxy.mrspidyxd.workers.dev", url).split("&")[0]
            for div in soup.find_all('div', class_='vidTitleWrapper') if div.find('a', class_='thumbnailTitle')
        ]
    except requests.RequestException as e:
        logging.error(f"Error searching video links for query '{query}': {e}")
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
            logging.info(f"Extracted URLs from {url}.")
            return urls
        else:
            logging.error(f"Error running yt-dlp: {result.stderr}")
            return []
    except Exception as e:
        logging.error(f"Error extracting URLs from {url}: {e}")
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
        logging.info("Fetched model URLs successfully.")
        return random.sample(
            [base_url + href for href in hrefs if "/model/" in href or "/pornstar/" in href or "/channel/" in href],
            5
        )
    except requests.RequestException as e:
        logging.error(f"Error fetching models: {e}")
        return []

def send_message(text, chat_id):
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('ok'):
                logging.info(f"Message sent to chat ID {chat_id}.")
            else:
                logging.error(f"Failed to send message: {response_data}")
        else:
            logging.error(f"Telegram API request failed with status code {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

def read_file_links():
    file_path = "links.txt"
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        logging.info("Read file links successfully.")
        return lines
    except FileNotFoundError:
        logging.error(f"Error: The file at {file_path} was not found.")
        return []
    except Exception as e:
        logging.error(f"Error reading file links: {e}")
        return []

def get_link(db=None, collection_name=None):
    logging.info("Started link_gen")
    try:
        urls = []
        links = read_file_links()
        if links:
            logging.info(links)
        for ph in fetch_models():
            logging.debug(f"Processing model: {ph}")
            urls.extend(extract_urls(ph))
        logging.info("Fetched recommended videos.")
        urls.extend(fetch_video_links())
        length = len(urls)
        logging.info(f"Total Videos: {length}")

        if db is not None:
            data = get_raw_url(db, collection_name)
            urls = [url for url in urls if url not in data]

        filtered = len(urls)
        logging.info(f"Filtered Videos: {filtered}")

        if urls:
            urls = random.sample(urls, min(100, len(urls)))  # Ensure we don't sample more than available
            send_message(text=data, chat_id=LOG_ID)
        else:
            logging.warning("No URLs to send.")
        
        return urls
    except Exception as e:
        logging.error(f"Error in get_link: {e}")
        return []
