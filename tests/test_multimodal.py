import requests
import json
with open("../image.png", "rb") as f:
    response = requests.post(
        "http://localhost:8000/diagnose",
        files={"file": ("image.png", f, "image/jpeg")}  # key must be "file"
    )
print(str(response)) 