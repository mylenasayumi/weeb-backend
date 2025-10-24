import os
import time

import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand

from .utils import (
    check_files_not_exists,
    exit_with_error,
    get_translations,
    print_color,
)

START_TIME = time.time()
SAMPLE_SIZE = 200
DATA_FILES = [
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


def clean_allocine_reviews(path_file):
    """
    Clean the Allociné French reviews dataset:
    - remove unused columns
    - rename 'polarity' to 'satisfaction'
    - sample 1000 rows
    - translate reviews from French to English
    Returns:
        (DataFrame, DataFrame): French and English datasets
    """
    dataframe = []

    try:
        dataframe = pd.read_csv(path_file)
    except:
        exit_with_error(
            f"Pandas cannot open the following file: {path_file}", START_TIME
        )

    dataframe = dataframe.drop("film-url", axis=1)
    dataframe = dataframe.drop("Unnamed: 0", axis=1)

    dataframe.rename(columns={"polarity": "satisfaction"}, inplace=True)

    df_200 = dataframe.sample(n=SAMPLE_SIZE, random_state=42)

    translations = []

    translations = get_translations(df_200, "fr", "en")

    df_200["en"] = translations

    df_en_200 = df_200[["satisfaction", "en"]]
    df_fr_200 = df_200[["satisfaction", "review"]]

    cols_fr = ["satisfaction"] + [
        col for col in df_fr_200.columns if col != "satisfaction"
    ]
    df_fr_200 = df_fr_200[cols_fr]

    cols_en = ["satisfaction"] + [
        col for col in df_en_200.columns if col != "satisfaction"
    ]
    df_en_200 = df_en_200[cols_en]

    return df_fr_200, df_en_200


def clean_amazon_reviews(path_file):
    """
    Clean the Amazon French reviews dataset:
    - transform data 1 to 5 => 0 to 1
    - rename 'translation' to 'en'
    - delete 'rating' column
    - separate datagrame fron English and French
    Returns:
        (DataFrame, DataFrame): French and English datasets
    """
    dataframe = []

    try:
        dataframe = pd.read_csv(path_file)
    except:
        exit_with_error(
            f"Pandas cannot open the following file: {path_file}", START_TIME
        )

    dataframe["satisfaction"] = np.where(dataframe["rating"] < 2.5, 0, 1)

    dataframe.rename(columns={"translation": "en"}, inplace=True)

    dataframe = dataframe.drop("rating", axis=1)

    dataframe_en = dataframe[["satisfaction", "en"]]
    dataframe_fr = dataframe[["satisfaction", "review"]]

    df_fr_200 = dataframe_fr.sample(n=SAMPLE_SIZE, random_state=42)
    df_en_200 = dataframe_en.sample(n=SAMPLE_SIZE, random_state=42)

    # Order dataframe  with first column as satisfaction
    cols_fr = ["satisfaction"] + [
        col for col in df_fr_200.columns if col != "satisfaction"
    ]
    df_fr_200 = df_fr_200[cols_fr]

    cols_en = ["satisfaction"] + [
        col for col in df_en_200.columns if col != "satisfaction"
    ]
    df_en_200 = df_en_200[cols_en]

    return df_fr_200, df_en_200


def clean_tweeter_reviews(path_file):
    """
    Clean the tweets dataset:
    - rename 'label' to 'satisfaction' & 'text' to 'review'
    - translate reviews from French to English
    - separate datagrame fron English and French
    Returns:
        (DataFrame, DataFrame): French and English datasets
    """
    dataframe = []

    try:
        dataframe = pd.read_csv(path_file)
    except:
        exit_with_error(
            f"Pandas cannot open the following file: {path_file}", START_TIME
        )

    dataframe.rename(columns={"label": "satisfaction"}, inplace=True)
    dataframe.rename(columns={"text": "review"}, inplace=True)

    df_200 = dataframe.sample(n=SAMPLE_SIZE, random_state=42)

    translations = get_translations(df_200, "fr", "en")

    df_200["en"] = translations

    df_en_200 = df_200[["satisfaction", "en"]]
    df_fr_200 = df_200[["satisfaction", "review"]]

    # Order dataframe  with first column as satisfaction
    cols_fr = ["satisfaction"] + [
        col for col in df_fr_200.columns if col != "satisfaction"
    ]
    df_fr_200 = df_fr_200[cols_fr]

    cols_en = ["satisfaction"] + [
        col for col in df_en_200.columns if col != "satisfaction"
    ]
    df_en_200 = df_en_200[cols_en]

    return df_fr_200, df_en_200


def clean_ai_reviews(path_file):
    """
    Returns:
        Dataframe with 'satisfaction' as first column
    """
    dataframe = []

    try:
        dataframe = pd.read_csv(path_file)
    except:
        exit_with_error(
            f"Pandas cannot open the following file: {path_file}", START_TIME
        )

    # Order dataframe  with first column as satisfaction
    cols = ["satisfaction"] + [
        col for col in dataframe.columns if col != "satisfaction"
    ]
    dataframe = dataframe[cols]

    return dataframe


class Command(BaseCommand):
    """
    Django management command to clean and prepare all CSV datasets
    used for training the satisfaction classification AI model.

    This command:
        - validates all CSV fles
        - cleans and normalizes data
        - concatenates all processed dataframes into 2 files
            * dataframe_fr.csv — containing French reviews
            * dataframe_en.csv — containing English translations

    How to use it?
        Using outside of docker when services are running:
            docker compose exec api python manage.py create_dataframes

        Otherwise:
            python manage.py create_dataframes
    """

    help = "This command checks csv files and clear all datas"

    def handle(self, *args, **options):
        # All CSV files must be in this folder
        csv_path = os.getenv("DATA_PATH")

        if os.path.isfile(csv_path + "dataframe_en.csv") and os.path.isfile(
            csv_path + "dataframe_fr.csv"
        ):
            print_color(f"All dataframes are here, no need to create", "green")
            return

        print_color(f"Starting Clear Csv Files...", "yellow")

        # checks if all files exists
        check_files_not_exists(DATA_FILES, csv_path, START_TIME)

        dataframe_fr = []
        dataframe_en = []
        for file in DATA_FILES:
            print_color(f"\tClearing file: {file}")

            if file == "allocine_french_review.csv":
                df_allocine_fr, df_allocine_en = clean_allocine_reviews(
                    csv_path + file
                )

                dataframe_fr.append(df_allocine_fr)
                dataframe_en.append(df_allocine_en)
                print_color(
                    f"End of clean_allocine_reviews after: {time.time() - START_TIME:.2f} sec",
                    "blue",
                )

            if file == "amazon_fr_en_review.csv":
                df_amazon_fr, df_amazon_en = clean_amazon_reviews(csv_path + file)

                dataframe_fr.append(df_amazon_fr)
                dataframe_en.append(df_amazon_en)
                print_color(
                    f"End of clean_amazon_reviews after: {time.time() - START_TIME:.2f} sec",
                    "blue",
                )

            if file == "french_tweets.csv":
                df_tweet_fr, df_tweet_en = clean_tweeter_reviews(csv_path + file)

                dataframe_fr.append(df_tweet_fr)
                dataframe_en.append(df_tweet_en)
                print_color(
                    f"End of clean_tweeter_reviews after: {time.time() - START_TIME:.2f} sec",
                    "blue",
                )

            ia_files = ["chatgpt", "claude", "lechat"]
            if any(elem in file for elem in ia_files):
                if "fr" in file:
                    df_chat_fr = clean_ai_reviews(csv_path + file)
                    dataframe_fr.append(df_chat_fr)
                else:
                    df_chat_en = clean_ai_reviews(csv_path + file)
                    dataframe_en.append(df_chat_en)
                print_color(
                    f"End of ia reviews after: {time.time() - START_TIME:.2f} sec",
                    "blue",
                )

        df_final_fr = pd.concat(dataframe_fr)
        df_final_en = pd.concat(dataframe_en)

        print_color(
            f"Repartition FR Positive/Negative: {df_final_fr['satisfaction'].value_counts()} ",
            "yellow",
        )
        print_color(
            f"Repartition EN Positive/Negative: {df_final_en['satisfaction'].value_counts()} ",
            "yellow",
        )

        df_final_fr.to_csv(csv_path + "dataframe_fr.csv", sep=",", index=False)
        df_final_en.to_csv(csv_path + "dataframe_en.csv", sep=",", index=False)

        print_color(
            f"\nCreate 2 files: 'dataframe_fr.csv' and 'dataframe_en.csv' in {time.time() - START_TIME:.2f} sec",
            "green",
        )
