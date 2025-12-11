from fastapi import HTTPException
from typing import List
import numpy as np
import os

try:
    from config.settings import settings
except ImportError:
    class Settings:
        WEIGHT_MATRIX_PATH = "weight_matrix.npy"
        DEFAULT_TOP_K = 5
    settings = Settings()


def recommend_from_vector(user_vector, weight_matrix, K=5):
    """
    user_vector - vector of implicit (0/1) responses
    weight_matrix - matrix of weights
    K - variable for top@k
    """

    user_vector = np.asarray(user_vector, dtype=np.float64).ravel() # приводим к 1D размеру
    scores = np.dot(user_vector, weight_matrix)
    scores = np.ravel(scores) # убеждаемся, что это 1D массив

    scores[user_vector > 0] = -np.inf # убираем уже просмотренные

    topk = np.argsort(-scores)[:K]
    return topk


def recommend(cats: List[str], top_k: int = None):
    if top_k is None:
        top_k = settings.DEFAULT_TOP_K

    user_vec = np.zeros(36)

    try:
        for c in cats:
            user_vec[CATEGORIES[c]] = 1
    except KeyError:
        raise HTTPException(status_code=404, detail='unknown category was transmitted')

    weight_matrix_path = settings.WEIGHT_MATRIX_PATH

    try:
        # Проверяем существование файла
        if not os.path.exists(weight_matrix_path):
            raise FileNotFoundError(f"File {weight_matrix_path} not found")

        weight_matrix = np.load(weight_matrix_path)
        top_rec = recommend_from_vector(user_vec, weight_matrix, K=top_k)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f'weight matrix not found at path: {weight_matrix_path}'
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'error loading weight matrix: {str(e)}'
        )
    top_rec_names = []
    for category_id in top_rec:
        for k, v in CATEGORIES.items():
            if v == category_id:
                top_rec_names.append(k)

    return {'recommendations': top_rec_names}


CATEGORIES = {'Закрытие задолженностей': 1,
             'Химия': 2,
             'Наука': 3,
             'Клуб наставников': 4,
             'Глубокое обучение': 5,
             'Backend-разработка': 6,
             'Экономика': 7,
             'Frontend разработка': 8,
             'IOS-разработка': 9,
             'Музыка': 10,
             'Туризм': 11,
             'DevOps': 12,
             'Робототехника': 13,
             'Волонтерство': 14,
             'Хакатоны': 15,
             'Иностранные языки': 16,
             'Вокал': 17,
             'Android-разработка': 18,
             '3D-моделирование': 19,
             'Промышленный дизайн': 20,
             'Физика': 21,
             'Стажировки': 22,
             'Танцы': 23,
             'Машинное обучение': 24,
             'Творчество': 25,
             'Театр': 26,
             'Спортивное программирование': 27,
             'Предпринимательство': 28,
             'Интеллектуальные игры': 29,
             'Анализ данных и Big Data': 30,
             'Гейм-дизайн': 31,
             'Кибербезопасность': 32,
             'Спорт': 33,
             'КВН': 34,
             'Дизайн': 35}
