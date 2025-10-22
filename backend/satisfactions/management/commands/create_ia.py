import os
import time

import pandas as pd
from django.core.management.base import BaseCommand

STARTS_TIME = time.time()


import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV, train_test_split


def clean_text(text):
    text = text.lower()  # minuscule
    text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s]", " ", text)  # caractères spéciaux
    text = re.sub(r"\s+", " ", text).strip()  # espaces
    return text


import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


class Command(BaseCommand):
    help = "This command trains simple IA models to classify satisfaction from review"

    def handle(self, *args, **options):
        # All files must be in this folder
        folder_path = os.getenv("FOLDER_PATH")

        if not os.path.isfile(folder_path + "dataframe_en.csv") and not os.path.isfile(
            folder_path + "dataframe_fr.csv"
        ):
            print(f"\033[91mDataframes are not present, you need to create them\033[0m")
            return

        df_fr = pd.read_csv(folder_path + "dataframe_fr.csv")

        # df_fr.rename(columns={'label': 'satisfaction'}, inplace=True)
        # df_fr.rename(columns={'text': 'review'}, inplace=True)
        # df_en = pd.read_csv(folder_path + "dataframe_en.csv")

        # df_fr = df_fr.sample(frac=0.1, random_state=42)
        df_fr["review"] = df_fr["review"].astype(str).apply(clean_text)

        y = df_fr["satisfaction"]
        X = df_fr["review"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=48
        )

        print("Train Set:", X_train.shape)
        print("Test Set:", X_test.shape)

        # vectorizer = CountVectorizer() #0.76
        # # vectorizer = TfidfVectorizer() # 0.77
        # vectorizer = TfidfVectorizer( # 0.7638
        #     stop_words=['french'],
        #     max_features=5000,
        #     ngram_range=(1, 2),  # Unigrammes et bigrammes
        #     min_df=2,  # Ignore les mots trop rares
        #     max_df=0.9,
        #     # sublinear_tf=True
        # )

        # X_train_vec = vectorizer.fit_transform(X_train)
        # X_test_vec = vectorizer.transform(X_test)

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

        grid_search_tune = GridSearchCV(pipeline, parameters, cv=2, n_jobs=2, verbose=3)
        grid_search_tune.fit(X_train, y_train)

        print("Best parameters set:")
        print(grid_search_tune.best_estimator_.steps)

        score = grid_search_tune.score(X_test, y_test)
        print(f"Accuracy sur le test : {score:.4f}")

        joblib.dump(grid_search_tune.best_estimator_, "pipeline_text_fr.pkl")  # 0.7736
        # param_grid = {
        #     'C': [0.01, 0.1, 1, 10, 100],
        #     'solver': ['liblinear', 'saga', 'lbfgs'],
        #     # 'penalty': ['l1', 'l2', 'elasticnet'],
        #     # 'l1_ratio': [0, 0.25, 0.5, 0.75, 1]
        # }
        # grid = GridSearchCV(LogisticRegression(max_iter=1000), param_grid, cv=5, n_jobs=-1)
        # grid.fit(X_train_vec, y_train)

        # print("Meilleurs paramètres :", grid.best_params_)
        # print("Score moyen en cross-validation :", grid.best_score_)

        # best_model = grid.best_estimator_
        # print("Accuracy finale :", best_model.score(X_test_vec, y_test))

        # cl1 = LogisticRegression()
        # cl1.fit(X_train_vec, y_train)
        # print("Accuracy score de la Régression Logistique : ",
        #     cl1.score(X_test_vec, y_test))

        # cl2 = DecisionTreeClassifier()
        # cl2.fit(X_train_vec, y_train)
        # print("Accuracy score de l'Arbre de Décision : ",
        #     cl2.score(X_test_vec, y_test))

        # cl3 = RandomForestClassifier()
        # cl3.fit(X_train_vec, y_train)
        # print("Accuracy score du Random Forest : ",
        #     cl3.score(X_test_vec, y_test))

        # models = [
        #     RandomForestClassifier(n_estimators=100),
        #     GradientBoostingClassifier(),
        #     SVC(kernel='linear'),
        #     MultinomialNB()
        # ]
        # for model in models:
        #     model.fit(X_train_vec, y_train)
        #     print(f"{model.__class__.__name__}: {model.score(X_test_vec, y_test)}")


"""
test1
vectorizer = CountVectorizer()
Accuracy score de la Régression Logistique :  0.7875
Accuracy score de l'Arbre de Décision :  0.7291666666666666
Accuracy score du Random Forest :  0.7833333333333333


"""

"""
     test 2
        
              vectorizer = TfidfVectorizer(stop_words=['french'], max_features=3000)

Train Set: (958,)
Test Set: (240,)
Accuracy score de la Régression Logistique :  0.7791666666666667
Accuracy score de l'Arbre de Décision :  0.7083333333333334
Accuracy score du Random Forest :  0.7625

"""


"""

test 3
vectorizer = TfidfVectorizer(stop_words=['french'], max_features=3000, ngram_range=(1,2))


docker compose exec api python manage.py create_ia
Train Set: (958,)
Test Set: (240,)
Accuracy score de la Régression Logistique :  0.7833333333333333
Accuracy score de l'Arbre de Décision :  0.675
Accuracy score du Random Forest :  0.7375


"""


"""

tset4
        vectorizer = TfidfVectorizer(stop_words=['french'], max_features=5000, ngram_range=(1,4))

docker compose exec api python manage.py create_ia
Train Set: (958,)
Test Set: (240,)
Accuracy score de la Régression Logistique :  0.775
Accuracy score de l'Arbre de Décision :  0.7125
Accuracy score du Random Forest :  0.7541666666666667

"""

"""
test 5
        df_fr["review"] = df_fr["review"].astype(str).apply(clean_text)

        vectorizer = TfidfVectorizer(
            stop_words=['french'],
            max_features=1000,
            ngram_range=(1,2),
            sublinear_tf=True
        )

"""


###
### PLUS DE DATA
"""t
test 1
    vectorizer = TfidfVectorizer(
            stop_words=['french'],
            max_features=1000,
            ngram_range=(1,2),
            sublinear_tf=True
        )
        
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)



        param_grid = {
            'C': [0.1, 1, 10],
            'solver': ['liblinear', 'lbfgs']
        }
        grid = GridSearchCV(LogisticRegression(max_iter=1000), param_grid, cv=5, n_jobs=-1)
        grid.fit(X_train_vec, y_train)"""


### ++++ de data

"""
test 1

coutnvector classiue 

docker compose exec api python manage.py create_ia
Train Set: (2878,)
Test Set: (720,)
Meilleurs paramètres : {'C': 1, 'solver': 'liblinear'}
Score moyen en cross-validation : 0.760600845410628
Accuracy finale : 0.7625
Accuracy score de la Régression Logistique :  0.7611111111111111
Accuracy score de l'Arbre de Décision :  0.6583333333333333
Accuracy score du Random Forest :  0.7347222222222223


"""
