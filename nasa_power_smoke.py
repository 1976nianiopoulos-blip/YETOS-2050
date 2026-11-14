import requests

url = "https://power.larc.nasa.gov/api/temporal/daily/point"

params = {
    "parameters": "T2M,PRECTOTCORR",
    "community": "AG",
    "latitude": 52.6638,
    "longitude": -8.6267,
    "start": "20230101",
    "end": "20230103",
    "format": "JSON",
    "time-standard": "UTC",
}

response = requests.get(url, params=params, timeout=60)
print("HTTP STATUS:", response.status_code)
response.raise_for_status()

data = response.json()
header = data.get("header", {})
series = data["properties"]["parameter"]

print("SOURCE URL:", response.url)
print("TIME STANDARD:", header.get("time_standard"))
print("FILL VALUE:", header.get("fill_value"))
print("PARAMETER METADATA:", data.get("parameters"))

for date in sorted(series["T2M"]):
    temperature = series["T2M"][date]
    precipitation = series["PRECTOTCORR"].get(date)
    print(date, "T2M:", temperature, "PREC:", precipitation)

print("NASA POWER RESPONSE RECEIVED")
