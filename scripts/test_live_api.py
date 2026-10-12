import json
import sys
import time
import urllib.request
from datetime import date

# Address of the live API (can be given on the command line)
API_URL = "https://ca-churn-api.yellowcliff-1636b7fd.francecentral.azurecontainerapps.io"
if len(sys.argv) > 1:
    API_URL = sys.argv[1]

# How many normal requests to send after the first one
NUMBER_OF_REQUESTS = 20

# The same test customer as in tests/test_app.py
CUSTOMER = {
    "tenure": 2,
    "MonthlyCharges": 85.5,
    "TotalCharges": 171,
    "SeniorCitizen": 0,
    "Contract": "Month-to-month",
    "InternetService": "Fiber optic",
    "PaymentMethod": "Electronic check",
    "PaperlessBilling": "Yes",
}


# Send one prediction request and return the answer and the time in seconds
def send_request():
    body = json.dumps(CUSTOMER).encode("utf-8")
    request = urllib.request.Request(
        API_URL + "/predict",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=120) as response:
        answer = json.loads(response.read())
    seconds = time.perf_counter() - start
    return answer, seconds


# The first request wakes the app up from 0 replicas (cold start)
answer, cold_start = send_request()
print(f"cold start: {cold_start:.2f} s, answer: {answer}")

# A fast first request means the app was already awake: do not overwrite the real result
if cold_start < 5:
    print("The app was already awake, so this is not a cold start.")
    print("Wait about 10 minutes without using the API, then run again. Nothing saved.")
    sys.exit()

# Then send the normal requests while the app is awake
times = []
for number in range(1, NUMBER_OF_REQUESTS + 1):
    answer, seconds = send_request()
    times.append(seconds)
    print(f"request {number:2d}: {seconds * 1000:.0f} ms")

# Compute the simple statistics in milliseconds
average = sum(times) / len(times) * 1000
fastest = min(times) * 1000
slowest = max(times) * 1000
print(f"average: {average:.0f} ms, fastest: {fastest:.0f} ms, slowest: {slowest:.0f} ms")

# Add this run as one new row at the end of the results table
row = f"| {date.today()} | {cold_start:.2f} s | {average:.0f} ms | {fastest:.0f} ms | {slowest:.0f} ms |\n"
with open("docs/results/api_speed.md", "a", encoding="utf-8") as file:
    file.write(row)
print("added one row to docs/results/api_speed.md")
