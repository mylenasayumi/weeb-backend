import os
import time

import joblib
from django.core.management.base import BaseCommand

from .utils import print_color

STARTS_TIME = time.time()


class Command(BaseCommand):
    """
    Django management command to test a simple text classification model

    This command:
        - Checking which model is available
        - Splitting data into training and test sets
        - Using Pipeline to find the best params
        - Saving models

    How to use it?
        Using outside of docker when services are running:
            docker compose exec api python manage.py try_models

        Otherwise:
            python manage.py try_models
    """

    help = "Test the AI satisfaction classification model."

    def handle(self, *args, **options):
        # All files must be in this folder

        is_fr_model = True
        is_en_model = True

        if not os.path.isfile("model_ia_fr.pkl"):
            is_fr_model = False
        if not os.path.isfile("model_ia_en.pkl"):
            is_en_model = False

        if is_fr_model and is_en_model:
            lang = (
                input(f"\nWhich model do you want to try? (fr/en) : ").strip().lower()
            )
            while lang not in ["fr", "en"]:
                lang = input(f"Invalid input. Choose 'fr' or 'en' : ").strip().lower()
        elif is_fr_model:
            lang = "fr"
            print_color(f"\nOnly french model is available.", "yellow")
        elif is_en_model:
            lang = "en"
            print_color(f"\nOnly english model is available.", "yellow")
        else:
            print_color(f"\nNo models are present, end of the command.", "red")
            return

        if lang == "fr":
            model_charge = joblib.load("./model_ia_fr.pkl")

        if lang == "en":
            model_charge = joblib.load("./model_ia_en.pkl")
        print_color(
            f"\tLoaded model '{lang}' successfully! Type 'exit' to quit.", "green"
        )

        while True:
            text = input(
                f"\nEnter your text to classify - '{lang}' or 'exit' to quit: "
            ).strip()
            if text.lower() == "exit":
                print_color("Exiting. Goodbye!", "red")
                break

            # Prediction using model
            prediction = model_charge.predict([text.lower()])
            sentiment = "positive" if prediction[0] == 1 else "negative"

            print_color(f"\tOur prediction: {prediction[0]} ==> {sentiment}", "green")
