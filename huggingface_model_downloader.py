import os
import sys
import requests
import logging
from bs4 import BeautifulSoup
from bdownload import BDownloader, BDownloaderException
import warnings
warnings.filterwarnings("ignore")
logging.basicConfig(
    format = "[%(levelname)s] %(message)s", level=logging.INFO
)


class ColorCodes:
    grey = "\x1b[38;21m"
    green = "\x1b[1;32m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[1;34m"
    light_blue = "\x1b[1;36m"
    purple = "\x1b[1;35m"
    reset = "\x1b[0m"

MODEL_NAME = sys.argv[1]
DOWNLOAD_PATH = "./" + MODEL_NAME.split('/') [-1]+"/"

logging.info("MODEL NAME:" + ColorCodes.light_blue + f"\"{MODEL_NAME}\"" + ColorCodes.reset)
logging.info("DOWNLOAD PATH:" + ColorCodes.light_blue + f"\"{os.path.join(os.getcwd(), MODEL_NAME.split('/')[-1])}\"" +  ColorCodes.reset)
MAIN_URL = "https://huggingface.co"
URL_TO_GET_FILES = MAIN_URL + "/" + MODEL_NAME + "/tree/main"
FILE_URLS = []
ss=set()

def find_downloadable_files_and_paths (URL, PATH): 
    global MAIN_URL, MODEL_NAME, FILE_URLS
    reqs = requests.get(URL, verify=False) 
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href') 
        if href.startswith("/" + MODEL_NAME + "/resolve/main/"):
            FILE_URLS.append([PATH, MAIN_URL + href])
            if href.startswith("/" + MODEL_NAME + "/tree/main/"): 
                if MAIN_URL+href not in ss:
                    ss.add(MAIN_URL+href)
                    find_downloadable_files_and_paths (MAIN_URL + href, PATH+ href.split('/')[-1]+'/')
                    ss.remove(MAIN_URL+href)


find_downloadable_files_and_paths(URL_TO_GET_FILES, DOWNLOAD_PATH)

logging.info(f"TOTAL FILES TO DOWNLOAD: {len(FILE_URLS)}")
print("ALL FILES:")
for idx, val in enumerate (FILE_URLS, start=1):
    print("\t{}. {}".format(idx, val[1][val[1].find("resolve/main/")+13:]))

print("\nDownloading...\n")
with BDownloader(progress = 'mill', min_split_size=1024*1024*256, chunk_size=1024*1024*20, check_certificate=False) as downloader:
    downloader.downloads(FILE_URLS)
    downloader.results()
    if downloader.result() == 0:
        logging.info("ALL FILES HAVE BEEN DOWNLOADED. STATUS:" + ColorCodes.green + "SUCCESSFUL" + ColorCodes.reset)
    else:
        logging.error("SOME ERROR HAS OCCURRED WHILE DOWNLADING. STATUS: " + ColorCodes.red + "NOT SUCCESSFUL" + ColorCodes.reset)
    downloader.close()
