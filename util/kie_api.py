import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

KIE_API_URL = "https://api.kie.ai/api/v1/generate"
KIE_RECORD_URL = "https://api.kie.ai/api/v1/generate/record-info"

FAILURE_STATUSES = {
    "CREATE_TASK_FAILED",
    "GENERATE_AUDIO_FAILED",
    "SENSITIVE_WORD_ERROR",
    "CALLBACK_EXCEPTION",
}

POLL_INTERVAL = 30
MAX_POLL_TIME = 600


def generate_music_kie(
    prompt: str,
    style: str,
    title: str,
    model: str = "V5",
    output_path: str | Path | None = None,
    instrumental: bool = False,
    negative_tags: str | None = None,
) -> dict:
    api_key = os.environ["KIE_API_KEY"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    print(f"Generating music with lyrics: {prompt}")
    print(f"Style: {style}")
    print(f"Title: {title}")
    print(f"Model: {model}")
    print(f"Instrumental: {instrumental}")
    print(f"Negative tags: {negative_tags}")

    payload = {
        "prompt": prompt,
        "style": style,
        "title": title,
        "model": model,
        "customMode": True,
        "instrumental": instrumental,
        "callBackUrl": "https://example.com/callback",
    }
    if negative_tags:
        payload["negativeTags"] = negative_tags

    resp = requests.post(KIE_API_URL, headers=headers, json=payload)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 200:
        raise RuntimeError(f"Generation request failed: {data}")

    task_id = data["data"]["taskId"]
    print(f"Task submitted: {task_id}")

    start = time.time()
    while time.time() - start < MAX_POLL_TIME:
        time.sleep(POLL_INTERVAL)
        poll_resp = requests.get(
            KIE_RECORD_URL,
            headers=headers,
            params={"taskId": task_id},
        )
        poll_resp.raise_for_status()
        poll_data = poll_resp.json()

        if poll_data.get("code") != 200:
            raise RuntimeError(f"Poll request failed: {poll_data}")

        record = poll_data["data"]
        status = record.get("status", "")
        print(f"Status: {status}")

        if status in FAILURE_STATUSES:
            raise RuntimeError(f"Generation failed with status: {status}\n{json.dumps(record, indent=2)}")

        if status == "SUCCESS":
            print(f"Record data: {json.dumps(record, indent=2)}")
            tracks = record.get("response", {}).get("sunoData", [])
            if output_path and tracks:
                audio_url = tracks[0].get("audioUrl")
                if audio_url:
                    print(f"Downloading audio to {output_path}")
                    audio_resp = requests.get(audio_url)
                    audio_resp.raise_for_status()
                    out = Path(output_path)
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(audio_resp.content)
            return record

    raise TimeoutError(f"Generation did not complete within {MAX_POLL_TIME}s")
