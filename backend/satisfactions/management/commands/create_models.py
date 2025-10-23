import os
import time

import joblib
import pandas as pd
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from .utils import clean_text_en, clean_text_fr, print_color

START_TIME = time.time()


class Command(BaseCommand):
    """
    Django management command to train a simple text classification model
    to predict user satisfaction from French review text and English review text.

    This command:
        - Loading and clearing files
        - Splitting data into training and test sets
        - Using Pipeline to find the best params
        - Saving models

    How to use it?
        Using outside of docker when services are running:
            docker compose exec api python manage.py create_models

        Otherwise:
            python manage.py create_models
    """

    help = (
        "Train a simple AI model to classify satisfaction from French/English reviews."
    )

    def handle(self, *args, **options):
        # All files must be in this folder
        folder_path = os.getenv("FOLDER_PATH")

        if not os.path.isfile(folder_path + "dataframe_en.csv") and not os.path.isfile(
            folder_path + "dataframe_fr.csv"
        ):
            print_color(f"Dataframes are not present, you need to create them", "red")
            return

        if not os.path.isfile("model_ia_fr.pkl"):
            # First: French reviews.
            print_color(f"Loading French DF...", "yellow")
            df_fr = pd.read_csv(folder_path + "dataframe_fr.csv")

            # clear french reviews
            print_color(f"Clearing french reviews...", "yellow")
            df_fr["review"] = df_fr["review"].astype(str).apply(clean_text_fr)

            y = df_fr["satisfaction"]
            X = df_fr["review"]

            print_color(f"Splitting data...", "yellow")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=48
            )
            print_color(f"\tTrain set: {X_train.shape}, Train Set: {X_test.shape}")

            print_color(f"Buildind pipeline...", "yellow")
            pipeline = Pipeline(
                [
                    ("tfidf", TfidfVectorizer()),
                    (
                        "clf",
                        OneVsRestClassifier(
                            MultinomialNB(fit_prior=True, class_prior=None)
                        ),
                    ),
                ]
            )
            parameters = {
                # TF-IDF
                "tfidf__max_df": [0.25, 0.5, 0.75, 1.0],
                "tfidf__min_df": [1, 2, 5],
                "tfidf__ngram_range": [(1, 1), (1, 2), (1, 3)],
                "tfidf__sublinear_tf": [True, False],
                # MultinomialNB
                "clf__estimator__alpha": [1e-2, 1e-3, 1e-1],
                "clf__estimator__fit_prior": [True, False],
            }

            grid_search_tune = GridSearchCV(
                pipeline, parameters, cv=2, n_jobs=2, verbose=1
            )
            grid_search_tune.fit(X_train, y_train)

            print_color(f"\n\tBest parameters set for French Reviews:", "blue")
            print_color(f"\t\t{grid_search_tune.best_estimator_.steps}")

            score = grid_search_tune.score(X_test, y_test)
            print_color(f"\n\tAccuracy sur le test : {score:.4f}", "blue")

            joblib.dump(grid_search_tune.best_estimator_, "model_ia_fr.pkl")

            print_color(
                f"\nSaving best trained french model model_ia_fr.pkl in {time.time() - START_TIME:.2f} sec",
                "green",
            )
            time.sleep(2)

        if not os.path.isfile("model_ia_en.pkl"):
            # SECOND: English Reviews
            print_color(f"Loading English DF...", "yellow")
            df_en = pd.read_csv(folder_path + "dataframe_en.csv")

            # clear enflgish reviews
            print_color(f"clearing english reviews...", "yellow")
            df_en["en"] = df_en["en"].astype(str).apply(clean_text_en)

            y = df_en["satisfaction"]
            X = df_en["en"]

            print_color(f"Splitting data...", "yellow")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=48
            )
            print_color(f"\tTrain set: {X_train.shape}, Train Set: {X_test.shape}")

            print_color(f"Buildind pipeline...", "yellow")
            pipeline = Pipeline(
                [
                    ("tfidf", TfidfVectorizer()),
                    (
                        "clf",
                        OneVsRestClassifier(
                            MultinomialNB(fit_prior=True, class_prior=None)
                        ),
                    ),
                ]
            )
            parameters = {
                # TF-IDF
                "tfidf__max_df": [0.25, 0.5, 0.75, 1.0],
                "tfidf__min_df": [1, 2, 5],
                "tfidf__ngram_range": [(1, 1), (1, 2), (1, 3)],
                "tfidf__sublinear_tf": [True, False],
                # MultinomialNB
                "clf__estimator__alpha": [1e-2, 1e-3, 1e-1],
                "clf__estimator__fit_prior": [True, False],
            }

            grid_search_tune = GridSearchCV(
                pipeline, parameters, cv=2, n_jobs=2, verbose=1
            )
            grid_search_tune.fit(X_train, y_train)

            print_color(f"\n\tBest parameters set for English Reviews:", "blue")
            print_color(f"\t\t{grid_search_tune.best_estimator_.steps}")

            score = grid_search_tune.score(X_test, y_test)
            print_color(f"\n\tAccuracy sur le test : {score:.4f}", "blue")

            joblib.dump(grid_search_tune.best_estimator_, "model_ia_en.pkl")

            print_color(
                f"\nSaving best trained English model model_ia_en.pkl in {time.time() - START_TIME:.2f} sec",
                "green",
            )
