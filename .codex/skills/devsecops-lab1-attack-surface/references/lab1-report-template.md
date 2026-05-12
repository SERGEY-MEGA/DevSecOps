# Lab 1 Report Template

Use this as the working skeleton for the Russian report.

## 1. Шапка

- ФИО:
- Группа:
- Лабораторная работа: №1, «Развёртывание веб-приложения и анализ поверхности атаки»
- GitLab-репозиторий:
- Исходный репозиторий: `https://github.com/vulnerable-apps/vuln_django_play`
- Дата выполнения:

## 2. Описание исходных данных

Выбран проект `<project-name>`, потому что он является открытым уязвимым веб-приложением и поддерживает локальный запуск.

Функциональность приложения: `<уточнить после чтения README и проверки UI/API>`.

## 3. Настройка и развёртывание стенда

### Требования

| ПО | Версия / источник | Для чего нужно |
|---|---|---|
| Docker | `<docker --version>` | запуск контейнеров |
| Docker Compose | `<docker compose version>` | запуск стенда |
| Git | `<git --version>` | работа с репозиторием |
| Runtime / DB | `<уточнить по Dockerfile и compose>` | приложение |

### Команды запуска

```bash
git clone <repo>
cd <repo>
docker compose up -d --build
docker compose ps
curl -i http://localhost:<port>/
```

### Типичные ошибки и исправления

| Ошибка | Причина | Исправление |
|---|---|---|
| `<заполнить фактом>` | `<причина>` | `<команда/действие>` |

## 4. Процесс исследования поверхности атаки

Источники:

- `README.md`
- `docker-compose.yml`
- `Dockerfile`
- `.env*`
- Django settings / URL routing
- `docker compose ps`
- `ss -tlnp` или `lsof -iTCP -sTCP:LISTEN -P`
- `curl -i`
- браузер / DevTools
- исходный код

Команды:

```bash
docker compose ps
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"
lsof -iTCP -sTCP:LISTEN -P
rg "path\(|re_path\(|url\(" -g "*.py"
rg "request\.GET|request\.POST|request\.body|request\.FILES" -g "*.py"
rg -n "(password|passwd|secret|api[_-]?key|token|private[_-]?key)\s*[=:]"
curl -i http://localhost:<port>/
```

## 5. Результаты анализа поверхности атаки

### 5.1 Условия развёртывания и границы рассмотрения

Приложение развёрнуто локально через `<Docker Compose / другой способ>`.
Внешняя среда: браузер пользователя и запросы с хоста на `localhost`.
Внутренняя среда: Docker-сеть, контейнеры приложения и зависимых сервисов.
В рамках работы рассматриваются сетевой и программный уровни поверхности атаки.
Физическая безопасность хоста и человеческий фактор рассматриваются справочно или находятся вне рамок.

### 5.2 Состав системы и используемые технологии

| Компонент | Программное решение | Назначение | Где запущено |
|---|---|---|---|
| Web / Backend | `<уточнить>` | `<уточнить>` | `<container / host>` |
| Database | `<уточнить>` | хранение данных | `<container / host>` |
| Static / Proxy | `<если есть>` | `<уточнить>` | `<container / host>` |
| Dependencies | `<requirements/package>` | библиотеки приложения | репозиторий / контейнер |

### 5.3 Сетевые точки доступа

| Адрес и порт | Компонент | Протокол | Назначение | Доступно извне |
|---|---|---|---|---|
| `localhost:<port>` | `<component>` | HTTP/TCP | `<purpose>` | да/нет |

Сверить `docker-compose.yml` с `docker compose ps` и `lsof/ss`. Расхождения вынести в наблюдения.

### 5.4 Точки входа в приложение

| Категория | Путь / страница | Тип запроса | Авторизация | Принимаемые данные |
|---|---|---|---|---|
| Главная | `/` | GET | `<да/нет>` | нет |
| Login | `<path>` | POST | нет | login/password or form fields |
| Admin | `/admin/` | GET/POST | admin/session | forms, CSRF |
| API/Form | `<path>` | GET/POST | `<да/нет>` | query/body/form/files |

### 5.5 Доступ, роли, данные и секреты

#### 5.5.1 Способы аутентификации и роли

| Способ входа | Где используется | Что передаётся |
|---|---|---|
| Session cookie | browser-backend | `sessionid` or actual cookie name |
| Admin login | `/admin/` if Django admin exists | username/password + CSRF |

Роли: `<уточнить по моделям/админке/README>`.

#### 5.5.2 Ценные данные и секреты

| Данные | Где хранятся |
|---|---|
| Учетные записи | `<DB/model>` |
| Сессии | `<cookie/db/cache>` |
| Пользовательский ввод | `<DB/logs/files>` |
| Логи | `<stdout/volume/file>` |

Секреты приложения без значений:

- `SECRET_KEY` / `DJANGO_SECRET_KEY` — `<где задается>`
- DB password/user/name — `<.env/compose/settings>`
- Tokens/API keys — `<если есть>`

### 5.6 Границы доверия

| Граница | Где проходит | Что должно быть на границе |
|---|---|---|
| Клиент <-> сервер | browser/host -> web app | server-side validation, auth, CSRF, security headers |
| App <-> DB | web container -> database | least privilege DB user, parameterized queries |
| Container <-> host | Docker container -> host OS | non-root user, restricted volumes, minimal exposed ports |
| Developer <-> repo | local git -> GitLab | secrets scan, code review, protected branches |

## Минимальный вывод

В результате инвентаризации была построена карта поверхности атаки: состав системы, опубликованные порты, основные точки входа, ценные данные, секреты по именам и границы доверия. На этом этапе уязвимости не эксплуатировались: цель работы — Inventory как первый шаг Inventory -> Minimization -> Hardening.
