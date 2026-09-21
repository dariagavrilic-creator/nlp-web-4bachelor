# Занятие 3. MongoDB: установка, практика, проект

К концу занятия у каждого на ноутбуке работает MongoDB, в ней лежит своя коллекция текстов, а FastAPI умеет её читать и пополнять. Домашнее задание — разобрать чужой проект, где NLP, веб и MongoDB уже соединены, и увидеть в нём свой будущий сервис.

## 1. Установка на Windows

Ставим три программы: сервер **MongoDB Community Server** (сама база), **MongoDB Compass** (окно, где базу видно глазами) и **mongosh** (командная строка базы). Нужна 64-битная Windows 10 или 11 и права администратора на компьютере.

**Важно до занятия.** С российских адресов сайт mongodb.com иногда отдаёт ошибку 403, и скачать сервер не получается. Облачная MongoDB Atlas из России нам недоступна, поэтому работаем только с локальной базой. Разумнее всего, чтобы преподаватель скачал установщики заранее и выложил их на общий диск курса. Compass и mongosh публикуются ещё и на GitHub — оттуда они скачиваются без проблем.

| Что | Откуда | Файл |
| --- | --- | --- |
| MongoDB Community Server | [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community): Version — последняя 8.x, Platform — Windows, Package — msi | `mongodb-windows-x86_64-8.x.x-signed.msi` |
| MongoDB Compass | [github.com/mongodb-js/compass/releases](https://github.com/mongodb-js/compass/releases), раздел Assets последнего релиза | `mongodb-compass-…-win32-x64.exe` |
| mongosh | [github.com/mongodb-js/mongosh/releases](https://github.com/mongodb-js/mongosh/releases), раздел Assets | `mongosh-…-x64.msi` |

### Шаг 1. Сервер

1. Запустите `.msi` двойным щелчком.
2. Тип установки — **Complete**.
3. На экране Service Configuration оставьте галочку **Install MongoD as a Service** и вариант **Run service as Network Service user**. Имя службы — `MongoDB`. Так база будет запускаться сама при включении компьютера, и терминал держать открытым не придётся.
4. Папки данных и логов оставьте по умолчанию: `C:\Program Files\MongoDB\Server\8.x\data` и `…\log`.
5. Галочку **Install MongoDB Compass** можно оставить. Если установка на этом шаге зависает — снимите её и поставьте Compass отдельно (шаг 2).
6. Нажмите Install, согласитесь на запрос администратора, дождитесь конца.

### Шаг 2. Compass

Если Compass не встал вместе с сервером, запустите скачанный `.exe` с GitHub. Установка идёт без вопросов, в конце открывается окно Compass.

### Шаг 3. mongosh

Этот шаг часто пропускают: **mongosh не входит в установщик сервера**, его ставят отдельно. Запустите `mongosh-…-x64.msi` и согласитесь на добавление в PATH.

Если не хочется ставить mongosh вовсе — в Compass есть встроенная вкладка `>_MONGOSH` внизу окна. Для занятия её достаточно.

### Шаг 4. Путь к программам (по желанию)

Чтобы команда `mongod` работала из любой папки, добавьте в переменную PATH путь `C:\Program Files\MongoDB\Server\8.x\bin`: Пуск → «Изменение системных переменных среды» → Переменные среды → Path → Изменить → Создать. После этого терминал нужно открыть заново.

### Шаг 5. Python-библиотеки

В папке своего проекта, в активированном виртуальном окружении:

```powershell
pip install pymongo fastapi uvicorn
```

Драйвер **Motor**, который встречается почти во всех статьях и примерах, объявлен устаревшим с 14 мая 2026 года. Используем `pymongo` с асинхронным клиентом `AsyncMongoClient` — это его официальная замена, и код почти тот же.

## 2. Проверка и первое подключение

База работает, если служба MongoDB запущена и Compass подключается к `mongodb://localhost:27017`.

**Служба.** Откройте PowerShell и выполните:

```powershell
Get-Service MongoDB
```

В колонке Status должно стоять `Running`. Если там `Stopped`, запустите службу из PowerShell, открытого от имени администратора:

```powershell
Start-Service MongoDB
```

То же самое без команд: Win + R → `services.msc` → строка «MongoDB Server (MongoDB)» → Запустить.

**Compass.**

1. Откройте Compass → **Add new connection**.
2. В поле URI уже стоит `mongodb://localhost:27017` — это и есть адрес вашей базы. Нажмите **Save & Connect**.
3. Слева появятся служебные базы `admin`, `config`, `local`. Их не трогаем.

**mongosh.** В терминале или на вкладке `>_MONGOSH` в Compass:

```js
db.runCommand({ ping: 1 })   // ответ { ok: 1 } — база отвечает
show dbs                     // список баз
use nlp_course               // перейти в базу (появится при первой записи)
```

База и коллекция в MongoDB создаются сами при первой вставке документа. Создавать их заранее, как таблицы в PostgreSQL, не нужно.

## 3. Если что-то не так

| Что видим | Причина | Что делать |
| --- | --- | --- |
| 403 Forbidden при скачивании с mongodb.com | Ограничение доступа для российских адресов | Взять установщик с общего диска курса |
| `connect ECONNREFUSED 127.0.0.1:27017` в Compass | Служба не запущена | `Start-Service MongoDB` от администратора |
| Служба стартует и сразу останавливается | Порт 27017 занят или нет прав на папку данных | Посмотреть конец файла `…\log\mongod.log`; порт проверяется командой `netstat -ano \| findstr 27017` |
| `'mongosh' не является внутренней или внешней командой` | mongosh не установлен или не в PATH | Поставить отдельно (шаг 3) или работать во вкладке `>_MONGOSH` в Compass |
| У студента нет прав администратора | Нельзя ставить службу | При установке снять галочку Install as a Service, создать папку `C:\data\db` и запускать базу вручную: `mongod --dbpath C:\data\db`; окно не закрывать |
| В FastAPI: `ServerSelectionTimeoutError` | Код не находит базу | Проверить службу и строку подключения `mongodb://localhost:27017` |
| В FastAPI: `Object of type ObjectId is not JSON serializable` | Поле `_id` уходит в ответ как есть | Превратить `_id` в строку — функция `to_json` в разделе 5 |
| В FastAPI: `'coroutine' object is not iterable` | Забыт await | Перед `insert_one`, `find_one`, `to_list`, `aggregate` нужен `await` |

## 4. Задания в Compass: своя коллекция документов

Работаем в базе `nlp_course`. Каждый создаёт коллекцию под тему своего будущего сервиса: `texts`, `reviews`, `recipes`, `poems` — что ближе к вашему проекту NLP+WEB.

**Задание 4.1. Спроектировать документ.** Прежде чем что-то вставлять, запишите на бумаге или в `schema.md`, из каких полей состоит один документ. Минимум:

```json
{
  "text": "Сегодня в Петербурге снова дождь, но прогулка по набережной того стоила.",
  "label": "позитив",
  "source": "telegram",
  "author": "student_07",
  "date": { "$date": "2026-09-20T12:00:00Z" },
  "tags": ["погода", "город"],
  "analysis": { "tokens": 12, "unique": 12, "lang": "ru" }
}
```

Обязательно: одно поле-массив (`tags`) и один вложенный объект (`analysis`). Именно этим документная база отличается от таблицы Excel.

**Задание 4.2. Наполнить коллекцию (15–20 документов).**

- 3–5 документов вставьте вручную: *ADD DATA → Insert document*, вставить JSON.
- Остальные импортируйте: подготовьте `corpus.csv` или `corpus.json` (можно выгрузить из pandas: `df.to_json("corpus.json", orient="records", force_ascii=False)`) и загрузите через *ADD DATA → Import JSON or CSV file*. При импорте CSV проверьте типы колонок (число, дата, строка).
- Минимум 3 разные метки `label` и 2 разных `source`.

**Задание 4.3. Запросы (строка Filter в Compass).** Запишите каждый запрос и число найденных документов в отчёт.

| Что найти | Фильтр |
| --- | --- |
| Все документы одной метки | `{ label: "позитив" }` |
| Длинные тексты | `{ "analysis.tokens": { $gt: 30 } }` |
| Несколько источников сразу | `{ source: { $in: ["telegram", "vk"] } }` |
| Тексты с тегом | `{ tags: "погода" }` |
| Слово в тексте | `{ text: { $regex: "дожд", $options: "i" } }` |
| Два условия сразу | `{ label: "негатив", "analysis.tokens": { $lt: 15 } }` |

В *Options* попробуйте **Project** `{ text: 1, label: 1, _id: 0 }` (показать только нужные поля), **Sort** `{ date: -1 }` и **Limit** `5`.

Придумайте ещё 3 своих запроса, осмысленных для вашего корпуса.

**Задание 4.4. Изменение и удаление.**

- Исправьте метку у одного документа (карандаш в карточке документа или в mongosh: `db.texts.updateOne({ _id: ObjectId("...") }, { $set: { label: "нейтрально" } })`).
- Добавьте тег в массив: `{ $push: { tags: "проверено" } }`.
- Удалите один документ и убедитесь, что счётчик уменьшился.

**Задание 4.5. Схема и индекс.**

- Вкладка **Schema → Analyze**: какие поля есть в каждом документе, а какие не везде? Какие типы у `date`? Если после импорта дата стала строкой, это ошибка: исправьте.
- Вкладка **Indexes → Create index** по полю `label`. Повторите фильтр по метке и посмотрите вкладку **Explain Plan**: теперь там `IXSCAN` вместо `COLLSCAN`.

## 5. FastAPI + MongoDB: проверенный пример

Ниже полный `main.py`: сервис хранит тексты вместе с результатом «анализа». Функция `analyze` — заглушка, на её место потом встанет ваш NLP-модуль. Код рабочий: создание, список, поиск по id, изменение, удаление; неверный id → 400, несуществующий → 404, пустой текст → 422.

```python
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import re

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import AsyncMongoClient

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "nlp_course"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # подключаемся один раз при запуске сервера
    app.state.client = AsyncMongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
    app.state.db = app.state.client[DB_NAME]
    yield
    # и закрываем соединение при остановке
    await app.state.client.close()


app = FastAPI(title="Тексты в MongoDB", lifespan=lifespan)


def texts():
    return app.state.db["texts"]


def to_json(doc: dict) -> dict:
    """ObjectId не превращается в JSON сам — переводим его в строку."""
    doc["id"] = str(doc.pop("_id"))
    return doc


def as_object_id(text_id: str) -> ObjectId:
    try:
        return ObjectId(text_id)
    except InvalidId:
        raise HTTPException(400, "Неверный формат id")


def analyze(text: str) -> dict:
    """Заглушка NLP-модуля. Потом её заменит ваш настоящий анализ."""
    words = re.findall(r"[а-яёa-z]+", text.lower())
    return {"tokens": len(words), "unique": len(set(words))}


class TextIn(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    label: str = "без категории"


class LabelUpdate(BaseModel):
    label: str


@app.get("/api/health")
async def health():
    await app.state.client.admin.command("ping")
    return {"mongo": "ok"}


@app.post("/api/texts", status_code=201)
async def create_text(item: TextIn):
    doc = {
        "text": item.text,
        "label": item.label,
        "analysis": analyze(item.text),
        "created_at": datetime.now(timezone.utc),
    }
    result = await texts().insert_one(doc)
    return {"id": str(result.inserted_id)}


@app.get("/api/texts")
async def list_texts(label: str | None = None, limit: int = 20):
    query = {"label": label} if label else {}
    cursor = texts().find(query).sort("created_at", -1).limit(limit)
    return [to_json(doc) for doc in await cursor.to_list()]


@app.get("/api/texts/{text_id}")
async def get_text(text_id: str):
    doc = await texts().find_one({"_id": as_object_id(text_id)})
    if doc is None:
        raise HTTPException(404, "Текст не найден")
    return to_json(doc)


@app.patch("/api/texts/{text_id}")
async def update_label(text_id: str, update: LabelUpdate):
    result = await texts().update_one(
        {"_id": as_object_id(text_id)}, {"$set": {"label": update.label}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Текст не найден")
    return {"updated": True}


@app.delete("/api/texts/{text_id}")
async def delete_text(text_id: str):
    result = await texts().delete_one({"_id": as_object_id(text_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "Текст не найден")
    return {"deleted": True}


@app.get("/api/stats")
async def stats():
    pipeline = [
        {"$group": {
            "_id": "$label",
            "texts": {"$sum": 1},
            "avg_tokens": {"$avg": "$analysis.tokens"},
        }},
        {"$sort": {"texts": -1}},
    ]
    cursor = await texts().aggregate(pipeline)
    return [
        {"label": row["_id"], "texts": row["texts"], "avg_tokens": round(row["avg_tokens"], 1)}
        for row in await cursor.to_list()
    ]
```

**Запуск** (в той же папке, в активированном виртуальном окружении):

```powershell
uvicorn main:app --reload
```

Откройте <http://127.0.0.1:8000/docs>, вызовите `GET /api/health` (должно быть `{"mongo": "ok"}`), создайте три текста через `POST /api/texts` и обновите коллекцию в Compass: документы появятся там.

**Что здесь важно понять**

- **lifespan.** Клиент создаётся один раз на всё приложение и хранит пул соединений. Создавать клиента внутри каждого эндпоинта — типичная ошибка.
- **await.** Каждое обращение к базе идёт по сети, поэтому `insert_one`, `find_one`, `update_one`, `delete_one`, `aggregate` и `to_list` нужно ждать через `await`. Исключение: `find()` сразу возвращает курсор, без `await`; ждём уже `cursor.to_list()`.
- **ObjectId.** У каждого документа есть `_id` типа `ObjectId`. FastAPI не умеет отдать его в JSON, поэтому `to_json` превращает его в строку `id`. Обратно — `as_object_id`: строка из URL → `ObjectId`, иначе поиск ничего не найдёт.
- **Коды ответов.** 201 — создано, 400 — кривой id, 404 — нет такого документа, 422 — данные не прошли проверку Pydantic (это FastAPI делает сам).
- **Motor не нужен.** В чужих проектах вы встретите `motor.motor_asyncio.AsyncIOMotorClient` — это та же идея, только устаревшая библиотека. Главное отличие при чтении чужого кода: в Motor `aggregate()` вызывается без `await`, в PyMongo Async — с `await`.

## 6. Задания через FastAPI

Берём `main.py` из раздела 5 и превращаем его в сервис под свою коллекцию из раздела 4. Каждое задание проверяем в `/docs` и сразу смотрим результат в Compass.

**Задание 6.1. Своя модель.** Перепишите `TextIn` под свой документ: добавьте `source: str`, `tags: list[str] = []`, `author: str | None = None`. Поменяйте имя коллекции в `texts()` на своё. Проверьте, что `GET /api/texts` выдаёт документы, которые вы импортировали через Compass. *Если в старых документах нет какого-то поля, что произойдёт? Почему не упало?*

**Задание 6.2. Фильтры в адресе.** Добавьте в `GET /api/texts` необязательные параметры `tag` и `source`. Запрос `GET /api/texts?tag=погода&source=telegram` должен собирать фильтр из заданных условий:

```python
query = {}
if label:
    query["label"] = label
if tag:
    query["tags"] = tag
# ... source — сами
```

**Задание 6.3. Поиск по тексту.** Эндпоинт `GET /api/search?q=дождь`: поиск через `$regex` без учёта регистра. Пользовательский ввод обязательно экранируйте: `{"text": {"$regex": re.escape(q), "$options": "i"}}`. *Проверьте, что будет без `re.escape`, если искать `.*`.*

**Задание 6.4. Пагинация.** Добавьте параметр `page` (с 1) и ограничьте `limit` сверху: `limit: int = Query(20, ge=1, le=100)`. Далее `.skip((page - 1) * limit).limit(limit)`. Верните вместе с данными общее число: `total = await texts().count_documents(query)`.

**Задание 6.5. История анализа — мостик к проекту NLP+WEB.** В вашем сервисе уже есть (или будет) `POST /api/analyze`. Сделайте так, чтобы каждый вызов сохранял в коллекцию `history` документ `{text, result, model_version, created_at}`, и добавьте `GET /api/history?limit=10` — последние запросы. Именно так устроены проекты из раздела 7.

**Задание 6.6. Статистика через агрегацию.** Перенесите в код конвейер частоты тегов из задания 4.6 — эндпоинт `GET /api/stats/tags`. Затем ещё один на выбор: число текстов по дням (`$dateToString`), средняя длина по источникам или доля каждой метки в процентах. Эти числа — готовые данные для графика на фронтенде.

## 7. Главное задание: «Экскурсия по чужому проекту NLP + Web + MongoDB»

**Зачем.** До этого момента вы видели только учебный код. Здесь задача — посмотреть, как похожий на ваш сервис собирают другие люди: запустить, разобраться в устройстве, найти сильные и слабые места и перенести лучшее в свой проект.

### Проекты на выбор

|  | Проект | Стек | Что хранит в MongoDB | Запуск | Ограничения |
| --- | --- | --- | --- | --- | --- |
| А | [pulseai-sentiment-dashboard](https://github.com/AkashKeshari111/pulseai-sentiment-dashboard) | FastAPI + Motor + React | Отзывы с тональностью, уверенностью, категориями, версией модели; вся аналитика — aggregation pipelines | Базовая модель учится за пару минут, есть синтетический датасет, ключи не нужны | По умолчанию настроен на Atlas — заменить строку на `mongodb://localhost:27017`; лицензии нет |
| Б | [CodeAlpha_Sentiment_Emotion_Analysis](https://github.com/ganeshpalipi/CodeAlpha_Sentiment_Emotion_Analysis) | FastAPI + React + Motor + RoBERTa (Hugging Face) | История анализов тональности и эмоций | Ключи не нужны; без базы работает «в памяти» | Модели англоязычные и тяжёлые (скачивание весов); пароли по умолчанию в README; лицензии нет |
| В | [farm-stack-to-do-app](https://github.com/mongodb-developer/farm-stack-to-do-app) | FastAPI + React + MongoDB + nginx, Docker Compose | Списки дел | Официальный учебный пример MongoDB, `MONGODB_URI` в окружении | NLP нет — это эталон структуры проекта, а не содержания |

Уровни: **А** — основной вариант для большинства; **Б** — для тех, у кого мощный ноутбук и интерес к трансформерам; **В** — для тех, кому сложно, или в паре с А как образец «правильной» структуры.

> Проекты без лицензии можно изучать и запускать, но нельзя копировать код в свой репозиторий. Переносить в свой проект нужно идеи, переписанные своими руками.

### Что сделать

**Шаг 1. Запустить (фото или скриншот работающего проекта).** Клонировать, создать виртуальное окружение, поставить зависимости, направить на локальную MongoDB, запустить backend и открыть `/docs`. Если что-то не запускается, записать ошибку и то, что вы попробовали: это тоже результат.

**Шаг 2. Экскурсия по коду: найти и выписать (с путями к файлам и номерами строк):**

1. Где создаётся подключение к MongoDB и откуда берётся строка подключения.
2. Какие базы и коллекции используются.
3. Схема одного документа — откройте коллекцию в Compass после нескольких запросов и вставьте пример документа в отчёт.
4. Один insert, один find и одну агрегацию — и что каждая из них делает простыми словами.
5. Как проект справляется с `ObjectId` при отдаче JSON (сравните с `to_json` из раздела 5).
6. Где вызывается NLP-модель и в какой момент результат попадает в базу.

**Шаг 3. Карта соответствий с вашим сервисом.** Таблица из трёх колонок:

| Часть | В чужом проекте | В моём проекте |
| --- | --- | --- |
| Подключение к БД | `backend/app/db.py` … | `db.py` (будет) |
| NLP-модуль | … | `nlp.py` |
| Эндпоинты API | … | `API.md` |
| Фронтенд | … | `static/` |

**Шаг 4. Критический взгляд.** Три сильные стороны и три слабые. Подсказки, куда смотреть: пароли и ключи в коде или README, отсутствие лицензии, устаревшие библиотеки (Motor), обработка ошибок, проверка входных данных, тесты, понятность README.

**Шаг 5. Одна идея себе.** Что вы перенесёте в свой проект NLP+WEB (новое поле в документе, эндпоинт статистики, дашборд, версия модели в каждой записи…) и как это будет выглядеть в вашей коллекции.

### Другие проекты для самостоятельного изучения

- [mongodb-labs/full-stack-fastapi-mongodb](https://github.com/mongodb-labs/full-stack-fastapi-mongodb) — большой шаблон: авторизация, Docker, фронтенд;
- [Youngestdev/fastapi-mongo](https://github.com/Youngestdev/fastapi-mongo) — компактный backend FastAPI + MongoDB;
- [khanh41/fastapi-mongodb-base-project](https://github.com/khanh41/fastapi-mongodb-base-project) — пример структуры папок backend-проекта.

## 8. Сдача и отчётность

**Что сдаётся** (в личную папку на [Google Disk](https://drive.google.com/drive/folders/1HkILs7e-SxXEwdzpxYbsmnqLSvu6mpJF?usp=drive_link)):

- `schema.md` — схема документа и записанные запросы из раздела 4;
- `export.json` — экспорт коллекции;
- `main.py` с выполненными заданиями раздела 6;
- `review.md` — отчёт по чужому проекту на 1–2 страницы (шаги 1–5 раздела 7) со скриншотами.

**Демонстрация на паре — 5 минут:** показать свою коллекцию в Compass, вызвать два эндпоинта в `/docs`, рассказать одну находку из чужого проекта и что из неё может перейти в свой сервис.

**Чек-лист перед сдачей**

- [ ] Служба MongoDB запущена, Compass подключается
- [ ] В коллекции не меньше 15 документов, даты имеют тип `Date`, а не строка
- [ ] `uvicorn main:app --reload` запускается без ошибок
- [ ] В `review.md` есть ссылка на чужой репозиторий и скриншот запуска

## 9. Источники

- [Install MongoDB Community Edition on Windows — официальная инструкция](https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-windows/)
- [MongoDB Compass — релизы на GitHub](https://github.com/mongodb-js/compass/releases)
- [mongosh — релизы на GitHub](https://github.com/mongodb-js/mongosh/releases)
- [Motor на PyPI: статус устаревания](https://pypi.org/project/motor/)
- [Миграция с Motor на PyMongo Async](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/)
- [Вопрос на Хабр Q&A о доступе к MongoDB из России](https://qna.habr.com/q/1174792)
- Проекты из раздела 7: [pulseai-sentiment-dashboard](https://github.com/AkashKeshari111/pulseai-sentiment-dashboard), [CodeAlpha_Sentiment_Emotion_Analysis](https://github.com/ganeshpalipi/CodeAlpha_Sentiment_Emotion_Analysis), [farm-stack-to-do-app](https://github.com/mongodb-developer/farm-stack-to-do-app), [mongodb-translator](https://github.com/codeSTACKr/mongodb-translator)
