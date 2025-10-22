import os
import time

from deep_translator import GoogleTranslator


def get_translations(data, src_lang, dest_lang):
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


def custom_exit(error, start_time):
    print(
        f"\033[91m\nExiting with error: {error}, after {time.time() - start_time:.2f}",
        "sec \033[0m",
    )
    exit()


def check_files_not_exists(list_files, path):
    """
    if all files exist return false
    Otherwise use custom_exist to exist
    """
    for file in list_files:
        if not os.path.isfile(path + file):
            custom_exit(f"Missing a file: {path + file}")
    return False
