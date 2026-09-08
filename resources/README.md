# Ресурсы

## Модели для русского языка

- `cointegrated/rubert-tiny2` — компактная, обучается за минуты, работает в Colab. Рекомендуется по умолчанию
- `ai-forever/ruBert-base` — крупнее, точнее, тяжелее
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` — для семантического поиска
- `cointegrated/rubert-tiny2` в режиме эмбеддингов — лёгкая альтернатива для поиска
- Natasha, DeepPavlov — готовые решения для NER и синтаксиса

## Наборы данных

- HuggingFace Datasets — huggingface.co/datasets
- Открытый корпус — opencorpora.org
- Национальный корпус русского языка — ruscorpora.ru
- CyberLeninka — научные аннотации, открытый доступ

## Инструменты

**Обработка текста:** razdel, pymorphy3, Natasha, spaCy
**Обучение:** transformers, sentence-transformers, scikit-learn
**Разметка:** Label Studio, doccano
**Серверная часть:** FastAPI, uvicorn
**Демонстрация:** Gradio, Streamlit

## Публикация

| Способ | Что подходит |
|---|---|
| HuggingFace Hub | Модели и наборы данных с карточками |
| HuggingFace Spaces | Демонстрационная версия вместе с моделью |
| ngrok | Временная ссылка на локальный сервер для защиты |
| Netlify | Только статическая часть сайта, без модели |

## Вычислительные ресурсы

- Google Colab — бесплатный GPU с ограничениями по времени
- Kaggle Notebooks — бесплатный GPU, до 30 часов в неделю

## Хостинг репозиториев

- GitHub — github.com
- GitVerse — gitverse.ru
- GitFlic — gitflic.ru
