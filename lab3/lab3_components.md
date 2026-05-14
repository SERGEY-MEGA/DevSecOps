# Реестр компонентов

Проект: `vulnerable-apps/vuln_django_play`  
Локальная копия: `/Users/sergejmegeran/Desktop/DevSecOps/vuln_django_play`

| Компонент | Тип | Версия | Источник версии | Где используется |
|---|---|---|---|---|
| vuln_django_play | учебное Django-приложение | commit локальной копии, точный hash можно уточнить через `git -C vuln_django_play rev-parse HEAD` | `README.md`, локальный каталог `vuln_django_play` | основное приложение для лабораторной работы |
| Python | рантайм / базовый образ | `3.9-bookworm` | `vuln_django_play/Dockerfile`, строка `FROM python:3.9-bookworm as base` | базовый образ backend-контейнера |
| Debian Bookworm | ОС базового образа | `bookworm`, точный набор пакетов требует проверки образа | `vuln_django_play/Dockerfile`, тег `python:3.9-bookworm` | ОС внутри backend-контейнера |
| Django | web-фреймворк | `3.0.4` | `vuln_django_play/requirements.txt` | основной web-фреймворк, маршруты `/polls/` и `/admin/` |
| Gunicorn | WSGI-сервер | `20.0.4` | `vuln_django_play/requirements.txt`, `Dockerfile` CMD в stage `micro` | запускает `vuln_django.wsgi` на порту `8010` |
| nginx | web-сервер / reverse proxy | в `dev` stage устанавливается из APT без закрепления версии; в micro compose используется образ `nginx:latest` | `vuln_django_play/Dockerfile`, `vuln_django_play/docker-micro.yml`, `nginx.default`, `nginx.conf.micro` | принимает HTTP на `8020` и проксирует в Gunicorn |
| PostgreSQL | база данных | образ `postgres:latest`, точная версия не закреплена | `vuln_django_play/docker-micro.yml` | БД в micro-варианте стенда |
| SQLite | база данных | версия не закреплена отдельно | `vuln_django_play/README.md`, `vuln_django_play/vuln_django/settings.py` | БД по умолчанию в all-in-one варианте |
| sqlparse | библиотека SQL-парсинга | `0.3.1` | `vuln_django_play/requirements.txt` | зависимость Django; дополнительно важна из-за endpoint `/polls/sql/` |
| requests | HTTP-клиент | `2.23.0` | `vuln_django_play/requirements.txt` | установлен в backend-образ, прямой импорт в коде приложения не найден |
| urllib3 | HTTP-клиент нижнего уровня | `1.25.8` | `vuln_django_play/requirements.txt` | транзитивно используется `requests`, установлен в backend-образ |
| psycopg2 | PostgreSQL-драйвер | `2.8.5` | `vuln_django_play/requirements.txt`, `docker-micro.yml` с `SQL_ENGINE=django.db.backends.postgresql` | подключение Django к PostgreSQL в micro-варианте |
| mysqlclient | MySQL-драйвер | `1.4.6` | `vuln_django_play/requirements.txt`, README с примечанием про MySQL/PostgreSQL client modules | установлен как зависимость, в текущем compose MySQL-сервис не используется |
| Markdown | Markdown-парсер | `3.2.1` | `vuln_django_play/requirements.txt` | установлен в backend-образ, прямой импорт в коде приложения не найден |
| martor | Markdown editor для Django | `1.4.7` | `vuln_django_play/requirements.txt` | установлен в backend-образ, в `INSTALLED_APPS` не подключён |
| django-seed | генерация тестовых данных | `0.2.2` | `vuln_django_play/requirements.txt`, `Dockerfile` команда `manage.py seed` | наполнение учебных данных при сборке `dev` stage |
| Faker | генерация тестовых данных | `4.0.2` | `vuln_django_play/requirements.txt` | зависимость `django-seed` |
| django-request-logging | middleware логирования запросов | `0.7.1` | `vuln_django_play/requirements.txt`, `settings.py` `request_logging.middleware.LoggingMiddleware` | логирование HTTP-запросов в Django |
| Docker Compose all-in-one | профиль запуска | Compose schema `3.7` | `vuln_django_play/docker-compose.yml` | один контейнер `vuln-django`, порт `8020` |
| Docker Compose micro | профиль запуска | Compose schema `3.7` | `vuln_django_play/docker-micro.yml` | отдельные сервисы `vuln-proxy`, `vuln-django`, `db` |

## Что нужно уточнить перед защитой

В момент сбора информации Docker daemon не был запущен, поэтому точные digest и runtime-версии образов `python:3.9-bookworm`, `nginx:latest`, `postgres:latest` не были подтверждены через `docker images` и `docker inspect`.

Перед защитой нужно выполнить:

```bash
docker compose -f vuln_django_play/docker-compose.yml build
docker compose -f vuln_django_play/docker-compose.yml up -d
docker ps
docker images
docker image inspect vuln_django
docker image inspect nginx
docker image inspect postgres
```
