<h1 align='center'>
  Проект «Фудграм» 
</h1>

<h2 align='center'>
  Описание проекта
</h2>
 Проект в котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

<h2 align='center'>
  Технологии
</h2>

- Python  
- Django  
- Django REST Framework  
- PostgreSQL  
- nginx  
- gunicorn  
- docker  
- GitHub Actions 


<h2 align='center'>
  Как запустить проект:
</h2>

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Blathata/foodgram.git
```

Перейти в корневую директорию
```
cd foodgram
```

Создать файл .evn для хранения ключей:

```
DB_ENGINE=django.db.backends.postgresql

DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

DB_HOST=db # Имя контейнера с БД в docker-compose.yml
DB_PORT=5432

ALLOWED_HOSTS=<Your_host>
SECRET_KEY=<Your_some_long_string>
DEBUG=True
```

Генерируем секретный ключ:

```
Запускаем интерпретатор Python
python manage.py shell
Генерируем ключ
from django.core.management.utils import get_random_secret_key
get_random_secret_key()
Добавить в переменую в .evn SECRET_KEY=... сгенерированый ключ
```

Запустить docker-compose.production:

```
docker compose -f docker-compose.production.yml up
```

Выполнить миграции, сбор статики:

```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/

```

Создать суперпользователя, ввести необходимые поля:

```
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

<h1 align='center'>
  Как работать с репозиторием финального задания
</h1>
<h2 align='center'>
  Что нужно сделать
</h2>

Настроить запуск проекта foodgram в контейнерах и CI/CD с помощью GitHub Actions

<h1 align='center'>
  Как проверить работу с помощью автотестов
</h1>

<h1 align='center'>
  Чек-лист для проверки перед отправкой задания
</h1>

- Проект Taski доступен по доменному имени, указанному в `tests.yml`.
- Проект Kittygram доступен по доменному имени, указанному в `tests.yml`.
- Пуш в ветку main запускает тестирование и деплой Kittygram, а после успешного деплоя вам приходит сообщение в телеграм.
- В корне проекта есть файл `foodgram_workflow.yml`.

Проект разработал Брежнев Иван (https://github.com/Blathata).
