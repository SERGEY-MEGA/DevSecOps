# Команды для повторения лабораторной работы №3

Команды выполнялись из каталога:

```bash
cd /Users/sergejmegeran/Desktop/DevSecOps
```

## Получить проект

```bash
git clone --depth 1 https://github.com/vulnerable-apps/vuln_django_play.git vuln_django_play
```

Если каталог уже есть:

```bash
git -C vuln_django_play status --short
git -C vuln_django_play rev-parse HEAD
```

## Посмотреть файлы проекта

```bash
find vuln_django_play -maxdepth 3 -type f \( -name "docker-compose*.yml" -o -name "docker-micro*.yml" -o -name "Dockerfile*" -o -name "requirements*.txt" -o -name "package*.json" -o -name "poetry.lock" -o -name "pom.xml" -o -name "go.mod" -o -name "README*" -o -name "nginx*" -o -name "*.py" \) | sort
```

## Найти зависимости и важные компоненты

```bash
sed -n '1,220p' vuln_django_play/requirements.txt
sed -n '1,260p' vuln_django_play/Dockerfile
sed -n '1,180p' vuln_django_play/docker-compose.yml
sed -n '1,220p' vuln_django_play/docker-micro.yml
sed -n '1,220p' vuln_django_play/nginx.default
sed -n '1,220p' vuln_django_play/nginx.conf.micro
sed -n '1,260p' vuln_django_play/vuln_django/settings.py
sed -n '1,260p' vuln_django_play/polls/views.py
```

## Быстро найти версии и опасные места

```bash
rg -n "^(FROM|RUN|CMD|ENTRYPOINT|EXPOSE)|image:|Django==|gunicorn==|requests==|urllib3==|sqlparse==|psycopg2==|mysqlclient==|Markdown==|django-seed==|martor==|Faker==|SQL_ENGINE|csrf_exempt|cursor\\.execute|ALLOWED_HOSTS|DEBUG" vuln_django_play
```

```bash
rg -n "Markdown|markdown|martor|requests|urllib3|sqlparse|psycopg2|mysqlclient|Faker|django_seed" vuln_django_play --glob '!static/**'
```

## Посмотреть Docker Compose в нормализованном виде

```bash
docker compose -f vuln_django_play/docker-compose.yml config
docker compose -f vuln_django_play/docker-micro.yml config
```

## Запустить all-in-one стенд

```bash
docker compose -f vuln_django_play/docker-compose.yml build
docker compose -f vuln_django_play/docker-compose.yml up -d
docker compose -f vuln_django_play/docker-compose.yml ps
```

Проверка приложения:

```bash
curl -i http://localhost:8020/polls/
curl -i http://localhost:8020/admin/
```

## Запустить micro-стенд

```bash
docker compose -f vuln_django_play/docker-micro.yml build
docker compose -f vuln_django_play/docker-micro.yml up -d
./vuln_django_play/scripts/migrations.sh
docker compose -f vuln_django_play/docker-micro.yml ps
```

## Посмотреть контейнеры и образы

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'
docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}'
docker image inspect vuln_django
docker image inspect vuln_django:micro
docker image inspect nginx
docker image inspect postgres
```

## Получить версии внутри контейнера

```bash
docker compose -f vuln_django_play/docker-compose.yml exec vuln-django python --version
docker compose -f vuln_django_play/docker-compose.yml exec vuln-django python -m django --version
docker compose -f vuln_django_play/docker-compose.yml exec vuln-django gunicorn --version
docker compose -f vuln_django_play/docker-compose.yml exec vuln-django nginx -v
docker compose -f vuln_django_play/docker-compose.yml exec vuln-django pip freeze
```

Для micro-стенда:

```bash
docker compose -f vuln_django_play/docker-micro.yml exec vuln-django python --version
docker compose -f vuln_django_play/docker-micro.yml exec vuln-django python -m django --version
docker compose -f vuln_django_play/docker-micro.yml exec vuln-django gunicorn --version
docker compose -f vuln_django_play/docker-micro.yml exec vuln-proxy nginx -v
docker compose -f vuln_django_play/docker-micro.yml exec db postgres --version
```

## Ручной поиск CVE

Примеры поисковых запросов:

```text
Django 3.0.4 CVE NVD
Django 3.0.4 GitHub advisory
Django 3.0.4 OSV
gunicorn 20.0.4 CVE request smuggling
gunicorn 20.0.4 GHSA
sqlparse 0.3.1 CVE
sqlparse 0.3.1 OSV
urllib3 1.25.8 CVE
requests 2.23.0 CVE
python:3.9-bookworm CVE Debian bookworm
nginx latest docker image CVE
postgres latest docker image CVE
```

Источники для ручной проверки:

```text
https://nvd.nist.gov/vuln/search
https://www.cve.org/
https://github.com/advisories
https://osv.dev/
https://bdu.fstec.ru/
https://www.cisa.gov/known-exploited-vulnerabilities-catalog
https://www.first.org/epss/
```

## Подготовить импорт в DefectDojo

Файл импорта:

```bash
cat docs/lab3_findings_defectdojo.json
```

Проверка JSON:

```bash
python3 -m json.tool docs/lab3_findings_defectdojo.json >/tmp/lab3_findings_checked.json
```

Порядок в интерфейсе:

```text
Product -> Engagement -> Test -> Findings -> Add Finding
```

или импорт:

```text
Engagement -> Import Scan Results -> Generic Findings Import -> docs/lab3_findings_defectdojo.json
```

## Что осталось проверить вручную

```bash
docker ps
docker images
docker image inspect vuln_django
docker image inspect nginx
docker image inspect postgres
```

После этого нужно уточнить CVE для точных digest образов `python:3.9-bookworm`, `nginx:latest` и `postgres:latest`.
