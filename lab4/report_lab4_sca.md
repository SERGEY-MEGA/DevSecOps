# Лабораторная работа №4

**Тема:** Композиционный анализ кода (SCA)  
**Проект:** `vulnerable-apps/vuln_django_play`  
**Стек:** Python / Django  
**Дата выполнения:** 14.05.2026  
**Студент:** Мегерян Сергей Сергеевич

## Содержание

1. Цель работы
2. Исходные данные
3. Подготовка проекта
4. Генерация SBOM
5. Загрузка SBOM в Dependency-Track
6. Анализ найденных уязвимостей
7. Сравнение с альтернативным SCA-сканером
8. Автоматизация в GitLab CI/CD
9. Вывод
10. Список источников

## 1. Цель работы

Цель работы - выполнить композиционный анализ программного обеспечения для учебного Django-приложения: определить состав зависимостей, сформировать SBOM в формате CycloneDX, загрузить SBOM в Dependency-Track, разобрать найденные уязвимости и предложить план исправления. Дополнительно был выполнен запуск второго SCA-сканера `pip-audit` и подготовлен вариант CI/CD-пайплайна для GitLab.

## 2. Исходные данные

Для анализа использовался репозиторий:

```text
https://github.com/vulnerable-apps/vuln_django_play
```

Локальный каталог проекта:

```text
/Users/sergejmegeran/Desktop/DevSecOps/vuln_django_play
```

Фиксируем commit, потому что SBOM имеет смысл только для конкретной версии исходного кода:

```bash
cd /Users/sergejmegeran/Desktop/DevSecOps/vuln_django_play
git rev-parse HEAD > .sca_commit
cat .sca_commit
```

Результат:

```text
d6ba1010a415a4c411e238ba926766ebc306159f
```

## 3. Подготовка проекта

Проект является Python/Django-приложением. Основной файл зависимостей - `requirements.txt`. Lock-файла типа `poetry.lock` или `Pipfile.lock` в проекте нет, поэтому граф транзитивных зависимостей восстанавливается хуже, чем в проектах с полноценным lock-файлом. При этом версии в `requirements.txt` зафиксированы, что позволяет выполнить SCA-анализ воспроизводимо.

Команды первичной инвентаризации:

```bash
cd /Users/sergejmegeran/Desktop/DevSecOps/vuln_django_play
cp requirements.txt deps_manual.txt
wc -l deps_manual.txt
sed -n '1,40p' deps_manual.txt
```

В проекте зафиксировано 27 Python-зависимостей. Основные компоненты: `Django==3.0.4`, `requests==2.23.0`, `urllib3==1.25.8`, `gunicorn==20.0.4`, `sqlparse==0.3.1`, `certifi==2019.11.28`.

**Таблица 1 - Исходная инвентаризация проекта**

| Параметр | Значение |
|---|---:|
| Стек | Python / Django |
| Файл зависимостей | `requirements.txt` |
| Lock-файл | отсутствует |
| Количество строк в `requirements.txt` | 27 |
| Commit анализа | `d6ba1010a415a4c411e238ba926766ebc306159f` |
| Контейнеризация | есть, `Dockerfile` |

## 4. Генерация SBOM

SBOM для файловой системы проекта был сформирован с помощью Trivy:

```bash
docker run --rm \
  -v /Users/sergejmegeran/Desktop/DevSecOps/vuln_django_play:/src \
  aquasec/trivy:latest \
  fs \
  --format cyclonedx \
  --output /src/sbom.cdx.json \
  /src
```

Проверка SBOM:

```bash
jq empty sbom.cdx.json && echo "OK"
jq '.bomFormat, .specVersion, .serialNumber' sbom.cdx.json
jq '.components | length' sbom.cdx.json
jq '[.components[] | select(.purl == null)] | length' sbom.cdx.json
jq '.dependencies | length' sbom.cdx.json
shasum -a 256 sbom.cdx.json
ls -lh sbom.cdx.json
```

Результат проверки:

**Таблица 2 - Метрики SBOM для файловой системы**

| Метрика | Значение |
|---|---:|
| Формат SBOM | CycloneDX |
| Версия спецификации | 1.6 |
| Serial Number | `urn:uuid:e9ef9631-e673-4d85-8894-c9f65b55f043` |
| Команда генерации | `trivy fs --format cyclonedx ...` |
| Количество компонентов | 28 |
| Количество компонентов без PURL | 1 |
| Количество записей в `dependencies` | 29 |
| Размер файла | 12 КБ |
| SHA-256 | `5e9d0f45e5be75ba10d30dd4836f558de6945041e155152c870bbd7c7dbc4ea5` |

Один компонент без PURL - это сам файл `requirements.txt`. Python-пакеты в SBOM имеют корректные PURL вида `pkg:pypi/django@3.0.4`, `pkg:pypi/requests@2.23.0`.

Так как проект контейнеризирован, был дополнительно собран Docker-образ и сформирован SBOM образа:

```bash
docker build -t vuln-django-play:lab4 .
docker run --rm \
  -v /Users/sergejmegeran/Desktop/DevSecOps/vuln_django_play:/out \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest \
  image \
  --format cyclonedx \
  --output /out/sbom-image.cdx.json \
  vuln-django-play:lab4
```

**Таблица 3 - Метрики SBOM для Docker-образа**

| Метрика | Значение |
|---|---:|
| Формат SBOM | CycloneDX |
| Версия спецификации | 1.6 |
| Serial Number | `urn:uuid:6024dd9f-884b-427b-b84c-46abb63e6470` |
| Количество компонентов | 489 |
| Количество компонентов без PURL | 1 |
| Количество записей в `dependencies` | 490 |
| Размер файла | 1.0 МБ |
| SHA-256 | `744b48ac7bdc0ce70e3876569f3b5d658bc38950e91b56144f836c56867fb210` |

Разница ожидаемая: SBOM по файловой системе показывает в основном зависимости приложения, а SBOM образа дополнительно включает системные пакеты Debian из базового образа `python:3.9-bookworm`.

## 5. Загрузка SBOM в Dependency-Track

В Dependency-Track был создан проект:

```text
Name: lab4-<фамилия>-python
Version: d6ba1010a415a4c411e238ba926766ebc306159f
Classifier: Application
Description: https://github.com/vulnerable-apps/vuln_django_play, анализ от 14.05.2026
```

Загрузка через UI:

1. `Projects -> Create Project`.
2. Создать проект `lab4-<фамилия>-python`.
3. Перейти в проект на вкладку `Components`.
4. Нажать `Upload BOM`.
5. Загрузить файл `sbom.cdx.json`.
6. Дождаться индексации компонентов.

Загрузка через API:

```bash
export DEPENDENCYTRACK_API_KEY="<значение хранится только в GitLab CI/CD Variables>"
export DEPENDENCYTRACK_PROJECT_UUID="<uuid проекта Dependency-Track>"

curl -X POST "http://10.0.0.30:8081/api/v1/bom" \
  -H "X-API-Key: $DEPENDENCYTRACK_API_KEY" \
  -F "project=$DEPENDENCYTRACK_PROJECT_UUID" \
  -F "bom=@sbom.cdx.json"
```

Ожидаемый ответ:

```json
{"token":"<token обработки BOM>"}
```

Проверка статуса обработки:

```bash
curl -s -H "X-API-Key: $DEPENDENCYTRACK_API_KEY" \
  "http://10.0.0.30:8081/api/v1/bom/token/<token>"
```

Ожидаемый результат после обработки:

```json
{"processing":false}
```

Секреты в репозиторий не добавлялись. API-ключ Dependency-Track хранится в GitLab CI/CD variable `DEPENDENCYTRACK_API_KEY` с флагом `Masked`. Флаг `Protected` в учебном стенде не включался, так как pipeline запускался из обычной ветки `main`; в промышленном проекте его следует включать для protected branches.

Места для скриншотов при сдаче:

```text
Скриншот 1 - Dependency-Track, карточка проекта lab4-<фамилия>-python.
Скриншот 2 - Dependency-Track, вкладка Components после загрузки sbom.cdx.json.
Скриншот 3 - Dependency-Track, вкладка Audit Vulnerabilities.
```

## 6. Анализ найденных уязвимостей

Для локального подтверждения результатов был запущен Trivy vulnerability scan:

```bash
docker run --rm \
  -v /Users/sergejmegeran/Desktop/DevSecOps/vuln_django_play:/src \
  aquasec/trivy:latest \
  fs \
  --scanners vuln \
  --format json \
  --output /src/trivy-fs-vuln.json \
  /src
```

Сводка по `requirements.txt`:

| Severity | Количество | Прямые | Транзитивные |
|---|---:|---:|---:|
| Critical | 2 | 2 | 0 |
| High | 17 | 17 | 0 |
| Medium | 21 | 21 | 0 |
| Low | 0 | 0 | 0 |
| **Итого** | **40** | **40** | **0** |

Все найденные Python-компоненты присутствуют в `requirements.txt`, поэтому в рамках данного проекта они классифицированы как прямые зависимости. В реальном проекте с lock-файлом часть пакетов, например `urllib3`, могла бы быть транзитивной зависимостью `requests`, но здесь `urllib3==1.25.8` записан явно.

Распределение уязвимостей по пакетам:

| Пакет | Количество уязвимостей |
|---|---:|
| Django | 17 |
| urllib3 | 10 |
| requests | 4 |
| sqlparse | 3 |
| certifi | 2 |
| gunicorn | 2 |
| Markdown | 1 |
| idna | 1 |

**Таблица 4 - Реестр топ-5 уязвимостей**

| # | CVE | Компонент | Версия | Fix-версия | Прямая/транз. | Путь зависимости | CVSS v3 | EPSS на 13.05.2026 | KEV | Решение |
|---:|---|---|---|---|---|---|---:|---:|---|---|
| 1 | CVE-2021-35042 | Django | 3.0.4 | 3.2.5 / 3.1.13 | прямая | `requirements.txt -> Django` | 9.8 | 0.89973 | нет | Срочно обновить Django до поддерживаемой LTS-ветки |
| 2 | CVE-2025-64459 | Django | 3.0.4 | 4.2.26 / 5.1.14 / 5.2.8 | прямая | `requirements.txt -> Django` | 9.1 | 0.00256 | нет | Обновить Django; текущая 3.0.4 давно не поддерживается |
| 3 | CVE-2023-37920 | certifi | 2019.11.28 | 2023.7.22 | прямая | `requirements.txt -> certifi` | 9.8 | 0.00112 | нет | Обновить `certifi` минимум до 2023.7.22 |
| 4 | CVE-2022-36359 | Django | 3.0.4 | 3.2.15 / 4.0.7 | прямая | `requirements.txt -> Django` | 8.8 | 0.00675 | нет | Закрывается обновлением Django |
| 5 | CVE-2024-1135 | gunicorn | 20.0.4 | 22.0.0 | прямая | `requirements.txt -> gunicorn` | 8.2 | 0.00054 | нет | Обновить `gunicorn` до 22.0.0 или выше |

Проверка KEV выполнялась по каталогу CISA Known Exploited Vulnerabilities. Для топ-5 записей совпадений в KEV не найдено. EPSS был получен через API FIRST:

```bash
curl -sS 'https://api.first.org/data/v1/epss?cve=CVE-2021-35042,CVE-2025-64459,CVE-2023-37920,CVE-2022-36359,CVE-2024-1135'
```

Отдельно был просканирован Docker-образ:

```bash
docker run --rm \
  -v /Users/sergejmegeran/Desktop/DevSecOps/vuln_django_play:/out \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest \
  image \
  --scanners vuln \
  --format json \
  --output /out/trivy-image-vuln.json \
  vuln-django-play:lab4
```

Сводка по образу:

| Severity | Количество |
|---|---:|
| Critical | 145 |
| High | 912 |
| Medium | 2269 |
| Low | 1173 |
| Unknown | 85 |

Количество уязвимостей в образе намного больше, потому что туда входят не только Python-библиотеки, но и системные пакеты Debian 12. Это важное различие: уязвимости приложения исправляются через `requirements.txt`, а уязвимости базового образа - через обновление базового образа, пересборку и минимизацию состава пакетов.

### Приоритизация remediation

Для приоритизации использовались четыре правила:

1. Если CVE есть в CISA KEV, исправление должно быть выполнено в течение 24 часов.
2. Если CVSS >= 9.0 и EPSS >= 0.5, исправление выполняется в течение 72 часов.
3. Если CVSS >= 7.0 и зависимость прямая, исправление планируется в ближайший спринт.
4. Если CVSS ниже 7.0, зависимость транзитивная и нет KEV/высокого EPSS, задача попадает в backlog.

По этим правилам самый высокий приоритет получает `CVE-2021-35042`: CVSS 9.8 и EPSS 0.89973. Несмотря на отсутствие KEV, вероятность эксплуатации высокая, а компонент `Django==3.0.4` является прямой зависимостью. Рекомендуемое действие - перейти на поддерживаемую LTS-версию Django, например ветку 4.2.x или 5.2.x, затем прогнать миграции и регрессионные тесты.

Также нужно обновить `certifi`, `gunicorn`, `urllib3`, `requests`, `sqlparse`, `Markdown` и `idna`. В учебном проекте можно начать с изменения `requirements.txt`, но в промышленном процессе правильнее сначала зафиксировать совместимые версии в отдельной ветке, собрать контейнер, прогнать тесты и повторно выполнить SCA.

## 7. Сравнение с альтернативным SCA-сканером

В качестве второго SCA-сканера выбран `pip-audit`, потому что это manifest-based инструмент для Python. Он анализирует `requirements.txt` и использует Python Packaging Advisory Database / OSV, то есть работает иначе, чем связка `Trivy -> SBOM -> Dependency-Track`.

Команда запуска:

```bash
docker run --rm \
  -v /Users/sergejmegeran/Desktop/DevSecOps/vuln_django_play:/src \
  python:3.9-bookworm \
  sh -c 'python -m pip install --quiet pip-audit && pip-audit -r /src/requirements.txt -f json -o /src/pip-audit.json || true'
```

Версия сканера:

```text
pip-audit 2.9.0
```

Результат:

```text
Found 40 known vulnerabilities in 8 packages
```

Фрагмент JSON-отчёта:

```json
{
  "name": "django",
  "version": "3.0.4",
  "vulns": [
    {
      "id": "PYSEC-2021-9",
      "aliases": ["GHSA-fvgf-6h6h-3322", "CVE-2021-3281"],
      "fix_versions": ["2.2.18", "3.0.12", "3.1.6"]
    }
  ]
}
```

**Таблица 5 - Сравнение результатов Trivy/Dependency-Track и pip-audit**

| CVE / Advisory | Trivy / Dependency-Track | pip-audit | Комментарий |
|---|---|---|---|
| CVE-2021-35042 | Critical | найдено как alias | Совпадает, уязвимость Django |
| CVE-2025-64459 | Critical | найдено как alias | Совпадает, свежая уязвимость Django |
| CVE-2023-37920 | High | найдено как alias | Совпадает, пакет `certifi` |
| CVE-2022-36359 | High | найдено как alias | Совпадает, пакет `Django` |
| CVE-2024-1135 | High | найдено как alias | Совпадает, пакет `gunicorn` |
| GHSA-27jp-wm6q-gp25 | Medium | найдено как GHSA | У записи нет CVE, поэтому в отчётах удобнее сверять GHSA/advisory ID |

Общий вывод по сравнению: на этом проекте количество находок совпало - 40 уязвимостей, но формат отличается. Trivy сразу добавляет severity, CVSS, ссылки и фикс-версии в одном JSON. `pip-audit` чаще показывает первичный advisory ID (`PYSEC` или `GHSA`) и CVE как alias. Поэтому при сравнении нельзя смотреть только на поле `id`: нужно учитывать aliases.

## 8. Автоматизация в GitLab CI/CD

Для автоматизации были подготовлены переменные GitLab CI/CD:

| Переменная | Назначение | Тип хранения |
|---|---|---|
| `DEPENDENCYTRACK_URL` | URL API Dependency-Track, например `http://10.0.0.30:8081` | Variable |
| `DEPENDENCYTRACK_API_KEY` | API-ключ Dependency-Track | Masked |
| `DEPENDENCYTRACK_PROJECT_UUID` | UUID проекта в Dependency-Track | Variable |
| `DEFECTDOJO_URL` | URL DefectDojo, например `http://10.0.0.20:8080` | Variable |
| `DEFECTDOJO_TOKEN` | API v2 token DefectDojo | Masked + Protected |
| `DEFECTDOJO_PRODUCTID` | ID продукта в DefectDojo | Variable |

Готовый пример пайплайна сохранён в файле:

```text
/Users/sergejmegeran/Desktop/DevSecOps/lab4/gitlab-ci-lab4.yml
```

Основные стадии пайплайна:

| Стадия | Что делает |
|---|---|
| `.pre` | Создаёт Engagement в DefectDojo и сохраняет `DEFECTDOJO_ENGAGEMENTID` в dotenv-артефакт |
| `pre-build` | Запускает `pip-audit`, сохраняет `pip-audit.json` |
| `build` | Генерирует `sbom.cdx.json` и `trivy-fs-vuln.json` через Trivy |
| `post-build` | Загружает SBOM в Dependency-Track и ждёт завершения обработки |
| `.post` | Импортирует `pip-audit.json` в DefectDojo |

Фрагмент загрузки SBOM в Dependency-Track. В финальном pipeline загрузка выполняется через `PUT /api/v1/bom`; для HTTP-запроса используется Python из локального образа `localhost:5000/semgrep:latest`, поэтому pipeline не зависит от Docker Hub:

```yaml
upload_dependency_track:
  stage: post-build
  image:
    name: localhost:5000/semgrep:latest
    entrypoint: [""]
  script:
    - |
      python3 - <<'PY'
      import base64, json, os, urllib.request
      api = os.environ["DEPENDENCYTRACK_URL"].rstrip("/")
      key = os.environ["DEPENDENCYTRACK_API_KEY"]
      project = os.environ["DEPENDENCYTRACK_PROJECT_UUID"]
      bom = base64.b64encode(open("sbom.cdx.json", "rb").read()).decode()
      payload = json.dumps({"project": project, "bom": bom}).encode()
      req = urllib.request.Request(
          f"{api}/api/v1/bom",
          data=payload,
          method="PUT",
          headers={"Content-Type": "application/json", "X-API-Key": key},
      )
      print(urllib.request.urlopen(req, timeout=30).read().decode())
      PY
```

Места для скриншотов при сдаче:

```text
Скриншот 4 - GitLab pipeline, все jobs зелёные.
Скриншот 5 - Dependency-Track, обновлённая дата импорта BOM.
Скриншот 6 - DefectDojo, созданный Engagement.
Скриншот 7 - DefectDojo, импортированные findings.
```

## 9. Вывод

В ходе лабораторной работы был выполнен SCA-анализ проекта `vuln_django_play`. Для проекта сформирован SBOM CycloneDX по файловой системе и по Docker-образу. SBOM по файловой системе содержит 28 компонентов, SBOM образа - 489 компонентов, что показывает разницу между анализом приложения и анализом готового контейнера.

По Python-зависимостям найдено 40 уязвимостей: 2 Critical, 17 High и 21 Medium. Наиболее приоритетная проблема - устаревший `Django==3.0.4`, так как он содержит критические SQL injection уязвимости, включая `CVE-2021-35042` с CVSS 9.8 и EPSS 0.89973. Основной план исправления - обновить Django до поддерживаемой LTS-версии, затем обновить `certifi`, `gunicorn`, `urllib3`, `requests`, `sqlparse`, `Markdown` и `idna`, после чего повторить SCA-анализ.

Сравнение с `pip-audit` показало, что разные SCA-инструменты могут давать одинаковое количество находок, но различаться по идентификаторам и структуре отчёта. Поэтому при анализе нужно сопоставлять не только CVE, но и GHSA/PYSEC aliases.

## 10. Список источников

1. OWASP CycloneDX Specification. URL: https://cyclonedx.org/specification/overview/
2. Aqua Security Trivy Documentation. URL: https://trivy.dev/latest/docs/
3. OWASP Dependency-Track Documentation. URL: https://docs.dependencytrack.org/
4. FIRST EPSS API. URL: https://api.first.org/data/v1/epss
5. CISA Known Exploited Vulnerabilities Catalog. URL: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
6. pip-audit Documentation. URL: https://github.com/pypa/pip-audit
7. DefectDojo API v2 Documentation. URL: https://documentation.defectdojo.com/
