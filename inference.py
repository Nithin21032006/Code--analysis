import requests

BASE_URL = "http://localhost:7860"

print("[START]")

for level in ["easy", "medium", "hard"]:
    reset_response = requests.post(
        f"{BASE_URL}/reset",
        params={"level": level}
    )

    print(f"[STEP] reset={level}")
    print(reset_response.json())

print("[END]")