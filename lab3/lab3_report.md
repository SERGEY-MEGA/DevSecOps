# Лабораторная работа №3
# Управление и поиск уязвимостей в используемых компонентах

ФИО: Мегерян Сергей Сергеевич  
Группа: М09КИИ-25  
Дата: 13.05.2026

## 1. Цель работы

Цель работы — получить практический опыт управления уязвимостями в компонентах приложения: собрать инвентаризацию зависимостей и сервисов, найти публичные CVE для конкретных версий, проверить применимость к стенду и оформить результаты в реестр для DefectDojo.

В этой работе важно было не просто найти CVE по названию компонента, а проверить: используется ли компонент в стенде, попадает ли наша версия в уязвимый диапазон и есть ли реальный сценарий эксплуатации.

## 2. Используемый стенд

Для анализа использовалось учебное приложение `vulnerable-apps/vuln_django_play`:

```text
https://github.com/vulnerable-apps/vuln_django_play
```

Локальная копия проекта:

```text
/Users/sergejmegeran/Desktop/DevSecOps/vuln_django_play
```

Проект представляет собой намеренно уязвимое Django-приложение с опросами. В README указано, что приложение основано на Django Polls tutorial и содержит учебные XSS/SQLi-проблемы.

В учебной инфраструктуре также используются:

| Сервис | Адрес | Назначение |
|---|---|---|
| GitLab | `http://10.0.0.10` | хранение учебных проектов |
| Registry + Runner | `10.0.0.11` | контейнерный registry и CI runner |
| DefectDojo | `http://10.0.0.20:8080` | учёт найденных уязвимостей |
| Dependency-Track | `http://10.0.0.30:8080`, API `8081` | анализ компонентного состава и SBOM |
| vulnerable-code-snippets | `10.0.0.40:1331-1338` | стенды для web-уязвимостей из предыдущей лабораторной |

Учётные данные в отчёт не включаются.

Основные сервисы самого `vuln_django_play`:

| Сервис | Где описан | Назначение |
|---|---|---|
| `vuln-django` | `docker-compose.yml` | all-in-one контейнер Django + Gunicorn + nginx + SQLite |
| `vuln-proxy` | `docker-micro.yml` | nginx proxy в micro-варианте |
| `vuln-django:micro` | `docker-micro.yml`, `Dockerfile` | backend-контейнер с Django и Gunicorn |
| `db` | `docker-micro.yml` | PostgreSQL в micro-варианте |

Использованные инструменты:

| Инструмент | Для чего использовался |
|---|---|
| Git | получение локальной копии проекта |
| Docker / Docker Compose | анализ compose-файлов и способа запуска |
| Терминал | сбор версий, поиск файлов, проверка конфигурации |
| DefectDojo | оформление findings |
| Браузер | ручная проверка открытых источников CVE |
| NVD, OSV, GHSA, MITRE CVE | поиск и проверка уязвимостей |

## 3. DefectDojo

Для ведения результатов использовался DefectDojo:

```text
http://10.0.0.20:8080
```

В DefectDojo нужно создать структуру:

```text
Product -> Engagement -> Test -> Findings
```

Рекомендуемые значения:

| Объект | Значение |
|---|---|
| Product | `vuln_django_play` |
| Engagement | `Lab3 - Component Vulnerability Management` |
| Test | `Manual component CVE review` или `Generic Findings Import` |

Места под скриншоты:

[Вставить скриншот Product в DefectDojo]

[Вставить скриншот Engagement в DefectDojo]

[Вставить скриншот Test в DefectDojo]

[Вставить скриншот Findings]

## 4. Методика сбора компонентов

Сначала были просмотрены файлы, которые обычно подтверждают состав приложения:

| Файл | Что проверялось |
|---|---|
| `vuln_django_play/README.md` | назначение приложения и способы запуска |
| `vuln_django_play/requirements.txt` | Python-зависимости и точные версии библиотек |
| `vuln_django_play/Dockerfile` | базовый образ, установка зависимостей, запуск Gunicorn/nginx |
| `vuln_django_play/docker-compose.yml` | all-in-one запуск на порту `8020` |
| `vuln_django_play/docker-micro.yml` | micro-запуск с nginx и PostgreSQL |
| `vuln_django_play/nginx.default` | nginx proxy в dev-варианте |
| `vuln_django_play/nginx.conf.micro` | nginx proxy в micro-варианте |
| `vuln_django_play/vuln_django/settings.py` | Django apps, middleware, БД, allowed hosts |
| `vuln_django_play/polls/views.py` | внешние endpoint и потенциально опасные участки |

Команды для повторения сбора вынесены в отдельный файл:

```text
docs/lab3_commands.md
```

Основные команды:

```bash
find vuln_django_play -maxdepth 3 -type f \( -name "Dockerfile*" -o -name "docker*.yml" -o -name "requirements*.txt" -o -name "README*" -o -name "nginx*" -o -name "*.py" \) | sort
sed -n '1,220p' vuln_django_play/requirements.txt
sed -n '1,260p' vuln_django_play/Dockerfile
docker compose -f vuln_django_play/docker-compose.yml config
docker compose -f vuln_django_play/docker-micro.yml config
```

В момент сбора информации Docker daemon не был запущен. Поэтому `docker ps`, `docker images` и `docker image inspect` нужно выполнить перед защитой, чтобы подтвердить точные digest и версии образов.

## 5. Таблица компонентов

Полный реестр компонентов находится в `docs/lab3_components.md`.

| Компонент | Тип | Версия | Источник версии | Где используется |
|---|---|---|---|---|
| Python | рантайм / базовый образ | `3.9-bookworm` | `Dockerfile` | базовый образ backend-контейнера |
| Debian Bookworm | ОС базового образа | `bookworm`, точный набор пакетов требует проверки образа | `Dockerfile` | ОС внутри backend-контейнера |
| Django | web-фреймворк | `3.0.4` | `requirements.txt` | маршруты `/polls/`, `/admin/` |
| Gunicorn | WSGI-сервер | `20.0.4` | `requirements.txt`, `Dockerfile` | запуск `vuln_django.wsgi` |
| nginx | reverse proxy | APT version в dev stage; `nginx:latest` в micro stage | `Dockerfile`, `docker-micro.yml` | внешний HTTP на `8020` |
| PostgreSQL | база данных | `postgres:latest`, точная версия не закреплена | `docker-micro.yml` | БД в micro-варианте |
| SQLite | база данных | версия не закреплена | `README.md`, `settings.py` | БД по умолчанию |
| sqlparse | SQL parser | `0.3.1` | `requirements.txt` | зависимость Django, важна из-за `/polls/sql/` |
| requests | HTTP client | `2.23.0` | `requirements.txt` | установлен в backend-образ |
| urllib3 | HTTP client | `1.25.8` | `requirements.txt` | транзитивная зависимость requests |
| psycopg2 | PostgreSQL driver | `2.8.5` | `requirements.txt` | подключение к PostgreSQL |
| mysqlclient | MySQL driver | `1.4.6` | `requirements.txt` | установлен, MySQL-сервис в compose не используется |
| Markdown | Markdown parser | `3.2.1` | `requirements.txt` | установлен, прямой импорт не найден |
| martor | Django markdown editor | `1.4.7` | `requirements.txt` | установлен, в `INSTALLED_APPS` не подключён |
| django-seed | генерация данных | `0.2.2` | `requirements.txt`, `Dockerfile` | seed учебных данных |
| django-request-logging | middleware | `0.7.1` | `requirements.txt`, `settings.py` | логирование HTTP-запросов |

## 6. Методика поиска уязвимостей

Поиск выполнялся вручную по открытым источникам:

| Источник | Что проверялось |
|---|---|
| NVD | CVE, CVSS, CWE, CPE-диапазоны |
| MITRE CVE / cve.org | каноническое описание CVE |
| GitHub Security Advisories | advisories по PyPI-пакетам |
| OSV.dev | affected ranges для open source пакетов |
| БДУ ФСТЭК | требуется ручная сверка по CVE перед финальной сдачей |
| CISA KEV | проверка наличия CVE в списке активно эксплуатируемых |
| EPSS | дополнительный показатель вероятности эксплуатации |

Для каждой уязвимости проверялось:

| Проверка | Зачем нужна |
|---|---|
| версия компонента | чтобы не добавить CVE от другой версии |
| уязвимый диапазон | чтобы подтвердить попадание нашей версии |
| место использования | чтобы понять, где компонент находится в стенде |
| доступность извне | чтобы оценить реальный путь атаки |
| уязвимая функциональность | чтобы не считать неприменимую CVE активной |
| рекомендация | чтобы было понятно, что исправлять |

Примеры запросов:

```text
Django 3.0.4 CVE NVD
Django 3.0.4 OSV
gunicorn 20.0.4 request smuggling GHSA
sqlparse 0.3.1 CVE
urllib3 1.25.8 CVE
requests 2.23.0 CVE
python:3.9-bookworm CVE Debian
```

## 7. Реестр уязвимостей

Полный реестр находится в `docs/lab3_vulnerability_register.md`.

| ID | Компонент | Версия | Идентификатор | Критичность | Применимость к стенду | Статус |
|---|---|---|---|---|---|---|
| LAB3-001 | Django | `3.0.4` | `CVE-2020-13254` | Medium | версия уязвима, но Memcached не используется | Неприменимо |
| LAB3-002 | Django | `3.0.4` | `CVE-2020-13596` | Medium | версия уязвима, админка есть, но `ForeignKeyRawIdWidget` не найден | Неприменимо |
| LAB3-003 | Django | `3.0.4` | `CVE-2020-24583` | High | версия уязвима, Python 3.9; нужны проверки прав директорий после сборки | Требует дополнительной проверки |
| LAB3-004 | Django | `3.0.4` | `CVE-2020-24584` | High | версия уязвима, но filesystem cache не настроен | Неприменимо |
| LAB3-005 | Django | `3.0.4` | `CVE-2021-3281` | Medium | management-команды не доступны через HTTP | Неприменимо |
| LAB3-006 | Django | `3.0.4` | `CVE-2021-23336` | Medium | нужен кэширующий proxy, на стенде не настроен | Неприменимо |
| LAB3-007 | Django | `3.0.4` | `CVE-2021-28658` | Low | нужен upload endpoint, в коде не найден | Неприменимо |
| LAB3-008 | Gunicorn | `20.0.4` | `CVE-2024-1135` | High | Gunicorn реально используется за nginx; нужна проверка TE/CL | Требует дополнительной проверки |
| LAB3-009 | Gunicorn | `20.0.4` | `CVE-2024-6827` | High | Gunicorn реально используется за nginx; нужна проверка smuggling | Требует дополнительной проверки |
| LAB3-010 | sqlparse | `0.3.1` | `CVE-2023-30608` | Medium/High | версия уязвима, есть `/polls/sql/`, прямой вызов sqlparse надо проверить | Требует дополнительной проверки |
| LAB3-011 | sqlparse | `0.3.1` | `CVE-2024-4340` | High | версия уязвима, прямой вызов `sqlparse.parse()` не найден | Требует дополнительной проверки |
| LAB3-012 | urllib3 | `1.25.8` | `CVE-2021-33503` | High | версия уязвима, но исходящий HTTP endpoint не найден | Неприменимо |
| LAB3-013 | urllib3 | `1.25.8` | `CVE-2023-43804` | High | версия уязвима, но Cookie redirect-сценарий не найден | Неприменимо |
| LAB3-014 | requests | `2.23.0` | `CVE-2023-32681` | Medium | версия уязвима, но requests/proxy credentials в коде не найдены | Неприменимо |
| LAB3-015 | requests | `2.23.0` | `CVE-2024-35195` | Medium | версия уязвима, но `requests.Session(verify=False)` не найден | Неприменимо |

## 8. Топ-3 наиболее критичных уязвимости

### 1. `CVE-2024-1135` в Gunicorn

Компонент Gunicorn используется в backend-контейнере для запуска Django. В all-in-one и micro-варианте внешний HTTP идёт через nginx на порт `8020`, а дальше запрос попадает в Gunicorn.

Опасность в том, что request smuggling возникает на границе frontend proxy и backend server. Если nginx и Gunicorn по-разному обработают `Transfer-Encoding` и `Content-Length`, атакующий может повлиять на границы соседних запросов.

Что исправить первым: обновить Gunicorn до `22.0.0` или новее и проверить nginx на отклонение неоднозначных TE/CL-запросов.

### 2. `CVE-2024-6827` в Gunicorn

Эта находка похожа по классу риска: TE.CL request smuggling. Она важна не только из-за CVSS, а потому что Gunicorn находится в реальном пути обработки HTTP-запроса.

Что может сделать атакующий: отправить специально сформированный HTTP-запрос через внешний порт `8020` и попытаться добиться рассинхронизации между nginx и Gunicorn.

Что исправить первым: обновить Gunicorn и добавить ручной тест smuggling-запросов после запуска стенда.

### 3. `CVE-2023-30608` в sqlparse

sqlparse 0.3.1 попадает в уязвимый диапазон. На стенде есть endpoint `/polls/sql/`, который принимает SQL из GET-параметра и выполняет его через `cursor.execute()`. Прямой вызов `sqlparse.format()` в коде не найден, но из-за наличия внешнего SQL endpoint эту зависимость надо проверить особенно внимательно.

Что может сделать атакующий при применимом пути: отправить специально сформированную SQL-подобную строку и вызвать ReDoS, то есть отказ в обслуживании.

Что исправить первым: обновить sqlparse до `0.4.4+` и отдельно исправить `/polls/sql/`, потому что выполнение SQL из запроса само по себе является критичной проблемой приложения.

## 9. Приоритеты устранения

| Приоритет | Находки | Действие |
|---|---|---|
| Срочно исправить | `CVE-2024-1135`, `CVE-2024-6827` в Gunicorn | обновить Gunicorn, проверить nginx/Gunicorn на request smuggling |
| Срочно исправить | endpoint `/polls/sql/` как риск приложения | убрать выполнение произвольного SQL, использовать безопасные ORM-запросы |
| Исправить планово | Django `3.0.4` как EOL-версия | обновить Django до поддерживаемой версии, затем повторить regression-тест |
| Исправить планово | sqlparse `0.3.1` | обновить до `0.5.0+` |
| Исправить планово | requests `2.23.0`, urllib3 `1.25.8` | обновить даже если сейчас прямой путь эксплуатации не найден |
| Принять как риск / компенсировать | Docker images без закрепления digest | закрепить версии или digest; до этого вручную проверять образы |
| Неприменимо | Memcached/filesystem cache/upload-related Django CVE | оставить в реестре как проверенные и неприменимые к текущей конфигурации |

## 10. Внесение результатов в DefectDojo

Результаты можно внести двумя способами.

Ручной ввод:

```text
Product -> Engagement -> Test -> Findings -> Add Finding
```

Импорт:

```text
Engagement -> Import Scan Results -> Generic Findings Import
```

Файл для импорта:

```text
docs/lab3_findings_defectdojo.json
```

Перед импортом файл проверяется командой:

```bash
python3 -m json.tool docs/lab3_findings_defectdojo.json >/tmp/lab3_findings_checked.json
```

Для каждой finding в DefectDojo нужно проверить:

| Поле | Что должно быть |
|---|---|
| Title | CVE и краткое описание |
| Severity | Critical/High/Medium/Low |
| Component name | имя компонента |
| Component version | версия из проекта |
| Description | применимость к стенду |
| Mitigation | конкретное исправление |
| References | ссылки на NVD/OSV/GHSA |

## 11. Вывод

В ходе работы был составлен реестр компонентов для `vuln_django_play` и проверены публичные CVE по ключевым версиям. Наиболее рискованными оказались компоненты, которые находятся в реальном HTTP-пути: Gunicorn и Django. Также отдельно выделен sqlparse, потому что в приложении есть endpoint `/polls/sql/`, принимающий SQL из запроса.

Работа показала, что CVSS нельзя использовать без контекста. Например, у Django есть High CVE, но если уязвимая функция относится к filesystem cache или upload endpoint, а на стенде этого нет, находку нельзя считать активной без проверки. В то же время Gunicorn с request smuggling важен, потому что он реально принимает трафик через nginx.

DefectDojo нужен для того, чтобы такие результаты не оставались отдельной таблицей: в нём можно вести статус, критичность, рекомендации и дальнейшую проверку исправлений.

## 12. Список источников

| Источник | Ссылка |
|---|---|
| Репозиторий проекта | `https://github.com/vulnerable-apps/vuln_django_play` |
| NVD | `https://nvd.nist.gov/` |
| MITRE CVE / CVE.org | `https://www.cve.org/` |
| GitHub Security Advisories | `https://github.com/advisories` |
| OSV.dev | `https://osv.dev/` |
| БДУ ФСТЭК | `https://bdu.fstec.ru/` |
| CISA KEV | `https://www.cisa.gov/known-exploited-vulnerabilities-catalog` |
| EPSS | `https://www.first.org/epss/` |
| DefectDojo docs | `https://docs.defectdojo.com/` |
| Django security releases | `https://docs.djangoproject.com/en/3.0/releases/security/` |
| Gunicorn advisories | `https://github.com/advisories/GHSA-w3h3-4rj7-4ph4` |
| sqlparse advisory | `https://github.com/advisories/GHSA-rrm6-wvj7-cwh2` |
| requests advisories | `https://github.com/advisories/GHSA-j8r2-6x86-q33q`, `https://github.com/advisories/GHSA-9wx4-h78v-vm56` |
| urllib3 advisories | `https://github.com/advisories/GHSA-q2q7-5pp4-w6pg`, `https://github.com/advisories/GHSA-v845-jxx5-vc9f` |
