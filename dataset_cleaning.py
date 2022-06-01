import pandas as pd
import os


def clean_dataset(name):
    df = pd.read_csv(f"csvs/{name}.csv", index_col=0)
    df = df.dropna()
    df = df[df['price'] > 0]
    if name in ["boredapeyachtclub", "mutant-ape-yacht-club", "bored-ape-kennel-club"]:
        names = df['name'].apply(int).apply(str).values
    else:
        names = df['name'].values

    directory = f"collections/{name}"
    end = 4
    for file in os.listdir(directory):
        filename = str(os.fsdecode(file))
        if filename.endswith(".png"):
            end = 4
        elif filename.endswith(".jpeg"):
            end = 5
        elif filename.endswith("mp4"):
            os.remove(directory + '/' + filename)
            continue

        if filename[:-end] in names:
            continue
        else:
            os.remove(directory + '/' + filename)

    files = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        files.append(filename[:-end])

    if sorted(names) == sorted(files):
        print(f"{name} was cleaned successfully")
    else:
        print(f"{name} something went wrong")


collections = ["akumaorigins",
               "arcade-land",
               "azuki",
                "beanzofficial",
               "bored-ape-kennel-club",
               "boredapeyachtclub",
                "clonex",
               "cool-cats-nft",
               "doodles-official",
                "eightbitme",
               "galverse",
               "karafuru",
               "mfers",
               "murakami-flowers-2022-official",
               "proof-moonbirds",
               "the-art-of-seasons",
               "toxic-skulls-club",
               "unemployables",
                "vaynersports-pass-vsp",
               ]


for col in collections:
    clean_dataset(col)
