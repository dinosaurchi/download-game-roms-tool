from requests_toolbelt import MultipartEncoder
from tqdm.auto import tqdm

import pandas as pd
import numpy as np

import os
import json
import pathlib
import time
import traceback
import requests
import shutil
import urllib
import urllib.parse
import random
import string
import argparse
import logging


def parse_quoted_url_file_name(target_url:str):
    file_name = os.path.basename(target_url)
    file_name = urllib.parse.unquote(file_name)
    return file_name


def download_file(session:requests.Session, target_url:str, output_file_path:pathlib.Path):
    # Reference: https://www.alpharithms.com/progress-bars-for-python-downloads-580122/
    # make an HTTP request within a context manager
    with session.get(target_url, stream=True) as r:
        # check header to get content length, in bytes
        total_length = int(r.headers.get("Content-Length"))
        
        # implement progress bar via tqdm
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="")as raw:
        
            # save the output to a file
            with open(str(output_file_path), 'wb')as output:
                shutil.copyfileobj(raw, output)


def get_game_hash(title:str, platform:str):
    platform = platform.lower().strip("\n\t\b ")
    title = title.lower().replace(" ", "_").strip("\n\t\b ")
    return f"{platform}@{title}"


def log_to_downloaded(status_file_path:pathlib.Path, game_hash:str):
    with open(str(status_file_path), "a+") as f:
        f.write(f"{game_hash}\n")


def filter_out_downloaded(game_infos:list, status_file_path:pathlib.Path):
    if not status_file_path.exists():
        return list(game_infos)

    with open(str(status_file_path), "r") as f:
        game_hashes = f.read().split("\n")
        game_hashes = [h.strip("\n\t\b ") for h in game_hashes]
        game_hashes = [h for h in game_hashes if len(h) > 0]

    res = []
    for info in game_infos:
        game_hash = get_game_hash(title=info["title"], platform=info["platform"])
        if game_hash in game_hashes:
            continue
        res.append(info)
    return res


def to_size_string(size_gb_value:float):
    if size_gb_value < 1:
        value = size_gb_value * 1000
        return f"{value} MB"
    return f"{size_gb_value} GB"


def login(username:str, password:str) -> requests.Session:
    session = requests.Session()

    with open("secrets/archive.org.json", "r") as f:
        account_info = json.loads(f.read())

    username = account_info["username"]
    password = account_info["password"]

    # Prepare cookies
    session.get(url="https://archive.org/download/no-intro_romsets/no-intro%20romsets/")
    session.get(url="https://archive.org/account/login")

    # Reference: https://stackoverflow.com/questions/51349340/recreate-post-request-with-webkitformboundary-using-pythons-requests
    fields = {
        "username": username,
        "password": password,
        "remember": "false",
        "referer": "https://archive.org/download/no-intro_romsets/no-intro%20romsets/",
        "login": "true",
        "submit_by_js": "true"
    }
    boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
    m = MultipartEncoder(fields=fields, boundary=boundary)

    headers = {
        'authority': 'archive.org',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': m.content_type,
        'origin': 'https://archive.org',
        'referer': 'https://archive.org/account/login',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    }
    session.post('https://archive.org/account/login', headers=headers, data=m)
    return session


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--database", help="Game database CSV file path", type=str, required=True)
    parser.add_argument("--out", help="Output directory path", type=str, required=True)
    parser.add_argument("--account", help="archive.org user's account JSON file path", type=str, required=True)
    args = parser.parse_args()

    output_game_dir = pathlib.Path(args.out)
    os.makedirs(output_game_dir, exist_ok=True)

    status_file_path = pathlib.Path("./status.txt")

    game_database = pd.read_csv(args.database, sep=",")

    with open(args.account, "r") as f:
        account_info = json.loads(f.read())

    game_database = game_database[["title", "platform", "unit", "size_gb", "is_downloaded", "link"]]
    game_database = game_database.dropna(subset=["link"])
    game_database = game_database[game_database["is_downloaded"] == "No"]
    game_database = game_database.reset_index()

    game_database["platform"] = game_database["platform"].str.lower()

    game_infos = game_database.to_dict("records")
    game_infos = sorted(game_infos, key=lambda x: x["size_gb"] if not np.isnan(x["size_gb"]) else 9999)

    game_infos = filter_out_downloaded(game_infos=game_infos, status_file_path=status_file_path)

    session = login(username=account_info["username"], password=account_info["password"])

    skipped_infos = []

    for i, info in enumerate(game_infos):
        title = info["title"]
        platform = info["platform"]
        link = info["link"]
        size_string = to_size_string(size_gb_value=info["size_gb"])
        game_hash = get_game_hash(title=title, platform=platform)

        cur_dir = pathlib.Path(output_game_dir, platform)
        os.makedirs(cur_dir, exist_ok=True)

        file_name = parse_quoted_url_file_name(target_url=link)
        output_file_path = pathlib.Path(cur_dir, file_name)

        logging.info(f"Downloading [{i+1}/{len(game_infos)}] (skipped: {len(skipped_infos)})")
        logging.info(f"  - Title    : {title}")
        logging.info(f"  - Platform : {platform}")
        logging.info(f"  - Size     : {size_string}")
        logging.info(f"  - URL      : {link}")
        logging.info(f"  - Output   : {output_file_path}")

        max_trials = 2
        while max_trials > 0:
            try:
                # Start downloading
                download_file(session=session, target_url=link, output_file_path=output_file_path)
                break
            except Exception as e:
                max_trials -= 1
                traceback.print_exc()
                logging.info(str(e))
                logging.info("Waiting for next trial")
                time.sleep(5)
                session = login(username=account_info["username"], password=account_info["password"])
        
        if max_trials > 0:
            log_to_downloaded(status_file_path=status_file_path, game_hash=game_hash)
        else:
            logging.info(f"Skipped {link}")
            skipped_infos.append(info)

        logging.info("Done\n-----------------------------------------")
        logging.info("")

    logging.info("Skipped summary:")
    for info in skipped_infos:
        link = info["link"]
        logging.info(f" - {link}")
