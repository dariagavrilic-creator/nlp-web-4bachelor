"""Проверка окружения перед парой 6.  Запуск:  python check_env.py

Если скрипт напечатал «всё готово», на паре 6 вы ничего не устанавливаете.
"""

import sys

print(f"Python: {sys.version.split()[0]}")
if sys.version_info < (3, 9):
    print("  нужен Python 3.9 или новее — поставьте свежую версию с python.org")

problems = []

for package, install in [("fastapi", "fastapi"), ("uvicorn", "uvicorn"),
                         ("pydantic", "pydantic"), ("requests", "requests")]:
    try:
        module = __import__(package)
        version = getattr(module, "__version__", "?")
        print(f"{package}: {version}")
    except ImportError:
        problems.append(install)
        print(f"{package}: не установлен")

if problems:
    print("\nУстановите недостающее:")
    print("  pip install " + " ".join(problems))
    sys.exit(1)

# пробуем собрать приложение — так же, как это сделает uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/ping")
def ping():
    return {"pong": True}


print("\nПриложение собирается. Всё готово.")
print("На паре 6 запустите:  uvicorn main:app --reload")
