import os
import time

import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand

from .utils import check_files_not_exists, custom_exit, get_translations

STARTS_TIME = time.time()


def clear_allocine_fr_file(path_file):
    dataframe = []

    try:
        dataframe = pd.read_csv(path_file)
    except:
        custom_exit(f"Pandas cannot open the following file: {path_file}", STARTS_TIME)

    # Delete useless columns
    dataframe = dataframe.drop("film-url", axis=1)
    dataframe = dataframe.drop("Unnamed: 0", axis=1)

    # Rename column
    dataframe.rename(columns={"polarity": "satisfaction"}, inplace=True)

    # Choose 200 random rows
    dataframe_200 = dataframe.sample(n=1000, random_state=42)

    translations = []

    # Translate french to english
    translations = get_translations(dataframe_200, "fr", "en")

    dataframe_200["en"] = translations

    # Separate dataframe in 2 by droping useless columns
    dataframe_en_200 = dataframe_200[["satisfaction", "en"]]
    dataframe_fr_200 = dataframe_200[["satisfaction", "review"]]

    # Order dataframe  with first column as satisfaction
    cols_fr = ["satisfaction"] + [
        col for col in dataframe_fr_200.columns if col != "satisfaction"
    ]
    dataframe_fr_200 = dataframe_fr_200[cols_fr]

    cols_en = ["satisfaction"] + [
        col for col in dataframe_en_200.columns if col != "satisfaction"
    ]
    dataframe_en_200 = dataframe_en_200[cols_en]

    return dataframe_fr_200, dataframe_en_200


def clear_amazon_fr_en_file(path_file):
    dataframe = []

    try:
        dataframe = pd.read_csv(path_file)
    except:
        custom_exit(f"Pandas cannot open the following file: {path_file}", STARTS_TIME)

    # Transform data rating (1 to 5) at 0 and 1 only
    dataframe["satisfaction"] = np.where(dataframe["rating"] < 2.5, 0, 1)

    # Rename columns
    dataframe.rename(columns={"translation": "en"}, inplace=True)

    # Delete rating column
    dataframe = dataframe.drop("rating", axis=1)

    # Separate dataframe in 2 by droping useless columns
    dataframe_en = dataframe[["satisfaction", "en"]]
    dataframe_fr = dataframe[["satisfaction", "review"]]

    # Choose 200 random rows
    dataframe_fr_200 = dataframe_fr.sample(n=1000, random_state=42)
    dataframe_en_200 = dataframe_en.sample(n=1000, random_state=42)

    # Order dataframe  with first column as satisfaction
    cols_fr = ["satisfaction"] + [
        col for col in dataframe_fr_200.columns if col != "satisfaction"
    ]
    dataframe_fr_200 = dataframe_fr_200[cols_fr]

    cols_en = ["satisfaction"] + [
        col for col in dataframe_en_200.columns if col != "satisfaction"
    ]
    dataframe_en_200 = dataframe_en_200[cols_en]

    return dataframe_fr_200, dataframe_en_200


def clear_tweet_fr_file(path_file):
    dataframe = []

    try:
        dataframe = pd.read_csv(path_file)
    except:
        custom_exit(f"Pandas cannot open the following file: {path_file}", STARTS_TIME)

    # Rename columns
    dataframe.rename(columns={"label": "satisfaction"}, inplace=True)
    dataframe.rename(columns={"text": "review"}, inplace=True)

    # Choose 200 random rows
    dataframe_200 = dataframe.sample(n=1000, random_state=42)

    # Translate french to english
    translations = get_translations(dataframe_200, "fr", "en")

    dataframe_200["en"] = translations

    # Create a dataframe per language
    dataframe_en_200 = dataframe_200[["satisfaction", "en"]]
    dataframe_fr_200 = dataframe_200[["satisfaction", "review"]]

    # Order dataframe  with first column as satisfaction
    cols_fr = ["satisfaction"] + [
        col for col in dataframe_fr_200.columns if col != "satisfaction"
    ]
    dataframe_fr_200 = dataframe_fr_200[cols_fr]

    cols_en = ["satisfaction"] + [
        col for col in dataframe_en_200.columns if col != "satisfaction"
    ]
    dataframe_en_200 = dataframe_en_200[cols_en]

    return dataframe_fr_200, dataframe_en_200


def clear_ia_file(path_file, lang):
    dataframe = []

    try:
        dataframe = pd.read_csv(path_file)
    except:
        custom_exit(f"Pandas cannot open the following file: {path_file}", STARTS_TIME)

    # Order dataframe  with first column as satisfaction
    cols = ["satisfaction"] + [
        col for col in dataframe.columns if col != "satisfaction"
    ]
    dataframe = dataframe[cols]

    return dataframe


class Command(BaseCommand):
    """
    This command is used to clear all csv files used
    to create an classification IA.
    It deletes useless columnc, bad data, rename columns etc
    """

    help = "This command checks csv files and clear all datas"

    def handle(self, *args, **options):
        # All files must be in this folder
        folder_path = os.getenv("FOLDER_PATH")

        if os.path.isfile(folder_path + "dataframe_en.csv") and os.path.isfile(
            folder_path + "dataframe_fr.csv"
        ):
            print(f"\033[92mAll dataframes are here, no need to create\033[0m")
            return

        print(f"\033[93m\nStarting Clear Csv Files...\033[0m")
        csv_files_lst = [
            "allocine_french_review.csv",  # https://www.kaggle.com/datasets/djilax/allocine-french-movie-reviews
            "amazon_fr_en_review.csv",  # https://www.kaggle.com/datasets/dargolex/french-reviews-on-amazon-items-and-en-translation
            "french_tweets.csv",  # https://www.kaggle.com/datasets/hbaflast/french-twitter-sentiment-analysis
            "chatgpt_en.csv",
            "chatgpt_fr.csv",
            "claude_fr.csv",
            "claude_en.csv",
            "lechat_fr.csv",
            "lechat_en.csv",
        ]

        # checks if all files exists
        check_files_not_exists(csv_files_lst, folder_path)

        dataframe_fr = []
        dataframe_en = []
        for file in csv_files_lst:
            print(f"\n\tClearing file: {file}")

            if file == "allocine_french_review.csv":
                df_allocine_fr, df_allocine_en = clear_allocine_fr_file(
                    folder_path + file
                )

                dataframe_fr.append(df_allocine_fr)
                dataframe_en.append(df_allocine_en)
                print(
                    f"\033[94m\tEnd of clear_allocine_fr_file after: {time.time() - STARTS_TIME:.2f}",
                    "sec \033[0m",
                )

            if file == "amazon_fr_en_review.csv":
                df_amazon_fr, df_amazon_en = clear_amazon_fr_en_file(folder_path + file)

                dataframe_fr.append(df_amazon_fr)
                dataframe_en.append(df_amazon_en)
                print(
                    f"\033[94m\tEnd of clear_amazon_fr_en_file after: {time.time() - STARTS_TIME:.2f}",
                    "sec \033[0m",
                )

            if file == "french_tweets.csv":
                df_tweet_fr, df_tweet_en = clear_tweet_fr_file(folder_path + file)

                dataframe_fr.append(df_tweet_fr)
                dataframe_en.append(df_tweet_en)
                print(
                    f"\033[94m\tEnd of clear_tweet_fr_file after: {time.time() - STARTS_TIME:.2f}",
                    "sec \033[0m",
                )

            ia_files = ["chatgpt", "claude", "lechat"]
            if any(elem in file for elem in ia_files):
                if "fr" in file:
                    df_chat_fr = clear_ia_file(folder_path + file, "fr")
                    dataframe_fr.append(df_chat_fr)
                else:
                    df_chat_en = clear_ia_file(folder_path + file, "en")
                    dataframe_en.append(df_chat_en)

                print(
                    f"\033[94m\tEnd of chatgpt_file after: {time.time() - STARTS_TIME:.2f}",
                    "sec \033[0m",
                )

        df_final_fr = pd.concat(dataframe_fr)
        df_final_en = pd.concat(dataframe_en)

        df_final_fr.to_csv(folder_path + "dataframe_fr.csv", sep=",", index=False)
        df_final_en.to_csv(folder_path + "dataframe_en.csv", sep=",", index=False)

        print(
            f"\033[92m\nCreate 2 files: 'dataframe_fr.csv' and 'dataframe_en.csv' in {time.time() - STARTS_TIME:.2f}",
            "sec \033[0m",
        )
