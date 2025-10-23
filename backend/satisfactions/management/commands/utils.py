import os
import re
import time

from deep_translator import GoogleTranslator


def print_color(msg, color="white"):
    colors = {
        "white": "\033[97m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m",
    }
    print(f"{colors[color]}{msg}{colors['reset']}")


def exit_with_error(error, start_time):
    print_color(
        f"Exiting with error: {error}, after {time.time() - start_time:.2f}", "red"
    )
    exit()


def clean_text_fr(text):
    text = text.lower()
    text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_text_en(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_translations(data, src_lang, dest_lang):
    """
    Translate string from 'src_lang' to 'dest_lang'
    Could take a long time.

    Returns translations
    """
    translations = []
    translator = GoogleTranslator(source=src_lang, target=dest_lang)

    for i, text in enumerate(data["review"]):
        try:
            if not text:
                translations.append("")
                continue

            translated = translator.translate(text)
            translations.append(translated)

            print(f"\t\tTranslating ... {i+1}/{len(data)}", end="\r")
            time.sleep(0.1)

        except Exception as e:
            print(f"\n[Error at ligne {i}] {e} — text: {text}")
            translations.append("")

    return translations


def check_files_not_exists(list_files, path):
    """
    if all files exist return false
    Otherwise use custom_exist to exist
    """
    for file in list_files:
        if not os.path.isfile(path + file):
            exit_with_error(f"Missing a file: {path + file}")
    return False
