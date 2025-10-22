import time

from django.core.management.base import BaseCommand

STARTS_TIME = time.time()


import re


def clean_text(text):
    text = text.lower()  # minuscule
    text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s]", " ", text)  # caractères spéciaux
    text = re.sub(r"\s+", " ", text).strip()  # espaces
    return text


import joblib


class Command(BaseCommand):
    help = "This command trains simple IA models to classify satisfaction from review"

    def handle(self, *args, **options):
        # All files must be in this folder
        pipeline_charge = joblib.load("./pipeline_text_fr.pkl")

        nouveau_texte = ["Vous etes nul affreux c'est zero "]

        # Prédiction avec le pipeline chargé
        prediction = pipeline_charge.predict(nouveau_texte)
        print("Prédiction :", prediction[0])  # 0 = sain, 1 = malade
