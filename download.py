import os
import sys
import signal
import requests
import pandas as pd
# import yadisk


API_URL = "https://api.opensea.io"
PAGE_SIZE = 50


QUIET = False
OUTPUT_DIR = "../../Downloads/collections"

usd_total = 0


def download_collection(collection):
    assets = None
    page = 0
    collection_prices = []

    while True:
        if page * PAGE_SIZE > 10000:
            break

        req_url = API_URL + "/assets"
        req_params = {
            "collection": collection,
            "offset": page * PAGE_SIZE,
            "limit": PAGE_SIZE,
            "order_direction": "asc"
        }

        resp = requests.get(req_url, params=req_params)
        if resp.status_code != 200:
            print(f"Error {resp.status_code} on page {page} of collection '{collection}'")
            break

        try:
            resp = resp.json()
        except Exception as e:
            print(e)
            break

        assets = resp["assets"]
        if assets == []:
            if page == 0:
                print(f"Collection '{collection}' does not exist")
            break

        if not os.path.isdir(OUTPUT_DIR + "/" + collection):
            os.mkdir(OUTPUT_DIR + "/" + collection)

        for asset in assets:
            try:
                name, price = download_asset(collection, asset)
                row = {"name": name, "price": price}
                collection_prices.append(row)
            except TypeError:
                print("type error")

        page += 1

    collection_df = pd.DataFrame.from_dict(collection_prices)
    collection_df.to_csv(f"{collection}.csv")


def download_asset(collection, asset):
    global usd_total

    asset_name = asset["name"]

    if asset_name is None:
        asset_name = asset["token_id"]

    asset_url = ""

    if asset["animation_url"] is not None:
        asset_url = asset["animation_url"]
    elif asset["image_url"] is not None:
        asset_url = asset["image_url"]

    if asset_url == "":
        return

    last_price = 0

    if asset["last_sale"] is not None:
        token_price_usd = float(asset["last_sale"]["payment_token"]["usd_price"])
        token_decimals = asset["last_sale"]["payment_token"]["decimals"]
        total_price = int(asset["last_sale"]["total_price"]) / 10**(token_decimals)
        last_price = int(total_price * token_price_usd)

    req = requests.get(asset_url, stream=True)

    asset_ext = ""
    ctype = req.headers["Content-Type"]
    if "image" in ctype or "video" or "audio" in ctype:
        asset_ext = ctype.split("/")[1]
    else:
        print(f"Unrecognized Content-Type: {ctype}")
        asset_ext = "bin"

    output_file = f"{OUTPUT_DIR}/{collection}/{asset_name}.{asset_ext}"

    if os.path.exists(output_file):
        return

    with open(output_file, "wb") as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    if not QUIET:
        if asset_name is None:
            asset_name = "noname"
        if last_price is None:
            last_price = 0
        print(f"{asset_name} - ${last_price}")
        return asset_name, last_price

    usd_total += last_price


def parse_flag(flag):
    flag = flag.split("=")
    prop = flag[0].lower()

    if prop == "quiet":
        global QUIET
        QUIET = True
    elif prop == "output-dir":
        global OUTPUT_DIR
        OUTPUT_DIR = flag[1]
    else:
        print(f"Unrecognized flag '{prop}'")
        exit()


def finish():
    print(f"\nYou acquired ${usd_total} worth of NFTs!\n")
    exit()


def sig_handler(num, frame):
    finish()


if __name__ == "__main__":
    for v in sys.argv[1:]:
        if v[0:2] == "--":
            parse_flag(v[2:])

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    signal.signal(signal.SIGINT, sig_handler)

    collections = [
                   "bored-ape-kennel-club",
    ]
    for col in collections:
        download_collection(col)

    finish()
