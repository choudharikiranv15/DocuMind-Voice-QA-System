import requests
import json

# Test STT endpoint
print("Testing Speech-to-Text endpoint...")
print("Uploading audio file: ./test_audio/test_question.mp3\n")

with open('./test_audio/test_question.mp3', 'rb') as audio_file:
    files = {'audio': audio_file}
    response = requests.post(
        "http://localhost:8080/transcribe",
        files=files
    )

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200 and response.json().get('success'):
    print(f"\n✅ STT Success!")
    print(f"Transcribed Text: {response.json()['text']}")
    print(f"Language: {response.json()['language']}")
    print(f"Duration: {response.json()['duration']:.2f}s")
else:
    print(f"\n❌ STT Failed: {response.json().get('message')}")
