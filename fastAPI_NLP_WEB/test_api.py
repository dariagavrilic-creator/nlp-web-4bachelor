"""Проверка своего сервиса. Запускать в отдельном терминале, пока работает uvicorn:

    python test_api.py

Скрипт делает те же запросы, что и Swagger, только сам, и печатает,
что уже работает, а что ещё нет. Его вывод сдаётся вместе с кодом.
"""

import sys

try:
    import requests
except ImportError:
    sys.exit("Не установлена библиотека requests:  pip install requests")

BASE = "http://127.0.0.1:8000"

passed, failed = 0, 0


def check(title, func):
    """Выполняет одну проверку и печатает результат."""
    global passed, failed
    try:
        problem = func()
    except requests.ConnectionError:
        sys.exit(f"Сервер не отвечает на {BASE} — запущен ли uvicorn main:app --reload?")
    except Exception as error:
        problem = f"{type(error).__name__}: {error}"

    if problem:
        failed += 1
        print(f"  [ ] {title}\n        {problem}")
    else:
        passed += 1
        print(f"  [v] {title}")


def post_analyze(text, mode="stats"):
    return requests.post(f"{BASE}/api/analyze", json={"text": text, "mode": mode}, timeout=10)


print(f"Проверяю сервис на {BASE}\n")

# —— Шаг 1 ——
def t1():
    r = requests.get(f"{BASE}/hello", timeout=10)
    if r.status_code != 200:
        return f"ожидался код 200, пришёл {r.status_code}"
    if "message" not in r.json():
        return f"в ответе нет поля message: {r.json()}"

check("Шаг 1. GET /hello отвечает", t1)

# —— Шаг 2 ——
def t2():
    r = requests.get(f"{BASE}/greet", params={"name": "Alex"}, timeout=10)
    if r.status_code != 200:
        return f"ожидался код 200, пришёл {r.status_code}"
    if "Alex" not in str(r.json()):
        return f"в ответе нет имени: {r.json()}"

def t3():
    r = requests.get(f"{BASE}/greet", timeout=10)
    if r.status_code != 200:
        return f"без параметра ожидался код 200, пришёл {r.status_code}"
    if "stranger" not in str(r.json()):
        return f"без параметра ожидалось stranger: {r.json()}"

check("Шаг 2. GET /greet?name=Alex здоровается по имени", t2)
check("Шаг 2. GET /greet без параметра здоровается со stranger", t3)

# —— Шаг 3 ——
def t4():
    r = requests.post(f"{BASE}/feedback", json={"username": "Alex", "comment": "норм"}, timeout=10)
    if r.status_code != 200:
        return f"ожидался код 200, пришёл {r.status_code}"
    if "Alex" not in str(r.json()):
        return f"в ответе нет имени: {r.json()}"

check("Шаг 3. POST /feedback принимает отзыв", t4)

# —— Шаги 4–5 ——
SAMPLE = ("Язык устроен так, что небольшое число элементов порождает бесконечное "
          "число сообщений. Эта способность языка называется продуктивностью. "
          "Она отличает человеческую речь от систем общения животных.")

def t5():
    r = post_analyze(SAMPLE)
    if r.status_code != 200:
        return f"ожидался код 200, пришёл {r.status_code}: {r.text[:200]}"
    data = r.json()
    for field in ("ok", "result", "meta"):
        if field not in data:
            return f"в ответе нет поля {field}: {list(data)}"
    if not data["ok"]:
        return f"ok должно быть true: {data}"
    for field in ("chars", "took_ms"):
        if field not in data["meta"]:
            return f"в meta нет поля {field}: {data['meta']}"
    if data["meta"]["chars"] != len(SAMPLE):
        return f"meta.chars = {data['meta']['chars']}, а символов в тексте {len(SAMPLE)}"

def t6():
    r = post_analyze("   ")
    if r.status_code not in (400, 422):
        return f"на пустой текст ожидался код 400 или 422, пришёл {r.status_code}"

def t7():
    r = post_analyze(SAMPLE, mode="такого-режима-нет")
    if r.status_code != 400:
        return f"на неизвестный режим ожидался код 400, пришёл {r.status_code}"

def t8():
    r = post_analyze(SAMPLE, mode="freq")
    if r.status_code != 200:
        return f"режим freq отвечает кодом {r.status_code}: {r.text[:200]}"
    top = r.json()["result"].get("top")
    if not top:
        return f"в результате нет непустого поля top: {r.json()['result']}"

def t9():
    r = post_analyze(SAMPLE, mode="longest")
    if r.status_code != 200:
        return f"режим longest отвечает кодом {r.status_code}: {r.text[:200]}"
    words = r.json()["result"].get("words")
    if not words:
        return f"в результате нет непустого поля words: {r.json()['result']}"
    if list(words) != sorted(words, key=len, reverse=True):
        return "слова не отсортированы по убыванию длины"

check("Шаг 4. POST /api/analyze разбирает текст в режиме stats", t5)
check("Шаг 4. Пустой текст даёт код 400 или 422", t6)
check("Шаг 4. Неизвестный режим даёт код 400", t7)
check("Шаг 5. Режим freq возвращает частотный список", t8)
check("Шаг 5. Режим longest возвращает самые длинные слова", t9)

# —— Документация ——
def t10():
    r = requests.get(f"{BASE}/docs", timeout=10)
    if r.status_code != 200:
        return f"страница /docs отвечает кодом {r.status_code}"

check("Swagger доступен по адресу /docs", t10)

print(f"\nГотово: {passed} из {passed + failed}")
if failed:
    print("Оставшиеся пункты — это ваши следующие шаги, а не поломка.")
