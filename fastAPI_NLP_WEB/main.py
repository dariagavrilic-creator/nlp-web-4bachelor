"""Сервис NLP+WEB. Пары 5–6.

Запуск:  uvicorn main:app --reload
Проверка: http://127.0.0.1:8000/docs

Шаг 1 уже написан — остальные делаете вы. После каждого шага сохраняйте файл
(uvicorn перезапустится сам) и запускайте проверку: python test_api.py
"""

import time

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from nlp import MODES, analyze

app = FastAPI(
    title="Мой NLP-сервис",          # впишите название своего сервиса
    description="Учебный проект курса «Основы web-программирования»",
    version="0.1.0",
)

# Это понадобится на паре 13, когда страница начнёт обращаться к серверу.
# Без этих строк браузер не пустит её запросы: страница и сервер будут
# по разным адресам, а это для браузера «чужой сайт».
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HISTORY = []        # история запросов живёт в памяти процесса: перезапуск её обнуляет


# ——————————————————————————————————————————————————————————————
# Шаг 1. Готово — смотрите, как устроен эндпоинт
# ——————————————————————————————————————————————————————————————
# @app.get(...) — декоратор: он говорит FastAPI «по этому адресу вызывай
# функцию ниже». Что функция вернёт, то FastAPI превратит в JSON.

@app.get("/hello")
def hello():
    return {"message": "Hello, FastAPI!"}


# ——————————————————————————————————————————————————————————————
# Шаг 2. Эндпоинт /greet с параметром запроса
# ——————————————————————————————————————————————————————————————
# Нужно: GET /greet?name=Alex  →  {"message": "Hello, Alex!"}
#        GET /greet            →  {"message": "Hello, stranger!"}
#
# Query("stranger", min_length=1, max_length=50) задаёт значение по умолчанию
# и ограничения: FastAPI проверит их сам и вернёт 422, если они нарушены.
#
# TODO: раскомментируйте и допишите

# @app.get("/greet")
# def greet(name: str = Query(..., ...)):
#     return {"message": ...}


# ——————————————————————————————————————————————————————————————
# Шаг 3. POST /feedback с Pydantic-моделью
# ——————————————————————————————————————————————————————————————
# Нужно: POST /feedback с телом {"username": "Alex", "comment": "норм"}
#        →  {"message": "Thanks for your feedback, Alex!"}
#
# Класс-наследник BaseModel описывает, что должно прийти в теле запроса.
# Проверку типов и ограничений FastAPI делает сам.
#
# TODO: раскомментируйте и допишите

# class Feedback(BaseModel):
#     username: str = Field(min_length=1, max_length=50)
#     comment: str = ...
#
# @app.post("/feedback")
# def feedback(item: Feedback):
#     return {"message": ...}


# ——————————————————————————————————————————————————————————————
# Шаг 4. Главный эндпоинт проекта: POST /api/analyze
# ——————————————————————————————————————————————————————————————
# Это шаг 3, переименованный под ваш проект. Ответ должен совпадать
# с тем, что записано в вашем файле API.md:
#
#   {"ok": true,
#    "result": {...},                                  ← то, что вернула analyze()
#    "meta": {"chars": 0, "mode": "stats", "took_ms": 0}}
#
# Если analyze() подняла ValueError (пустой текст, неизвестный режим) —
# отвечаем кодом 400 и текстом ошибки.
#
# TODO: раскомментируйте и допишите

# class AnalyzeIn(BaseModel):
#     text: str = Field(min_length=1, max_length=20000)
#     mode: str = "stats"
#
# @app.post("/api/analyze")
# def analyze_text(item: AnalyzeIn):
#     started = time.perf_counter()
#     try:
#         result = analyze(item.text, item.mode)
#     except ValueError as error:
#         raise HTTPException(400, str(error))
#
#     response = {
#         "ok": True,
#         "result": result,
#         "meta": {
#             "chars": len(item.text),
#             "mode": item.mode,
#             "took_ms": round((time.perf_counter() - started) * 1000, 1),
#         },
#     }
#     HISTORY.append({"text": item.text[:80], "mode": item.mode, "result": result})
#     return response


# ——————————————————————————————————————————————————————————————
# Шаг 5. Режимы анализа — в файле nlp.py
# ——————————————————————————————————————————————————————————————
# Откройте nlp.py: режим "stats" написан, "freq" и "longest" ваши.
# Здесь ничего менять не нужно, кроме эндпоинта ниже.
#
# TODO: раскомментируйте — он отдаёт список доступных режимов,
# чтобы страница на паре 13 могла построить выпадающий список сама

# @app.get("/api/modes")
# def modes():
#     return {"modes": MODES}


# ——————————————————————————————————————————————————————————————
# Со звёздочкой
# ——————————————————————————————————————————————————————————————
# 1. GET /api/health → {"status": "ok", "requests": <сколько запросов было>}
# 2. GET /api/history?limit=10 → последние запросы из HISTORY, новые сверху
# 3. Четвёртый режим анализа на вашем материале — в nlp.py
# 4. Сохранять историю не в список, а в MongoDB из занятия 3
