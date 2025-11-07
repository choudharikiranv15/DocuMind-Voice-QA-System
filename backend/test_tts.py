import requests
import json

# Test TTS endpoint
print("Testing Text-to-Speech endpoint...")
response = requests.post(
    "http://localhost:8080/speak",
    json={"text": "Hello! This is DocuMind Voice testing the text to speech feature."}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200 and response.json().get('success'):
    audio_url = response.json()['audio_url']
    print(f"\n✅ TTS Success! Audio available at: http://localhost:8080{audio_url}")
    print(f"Duration: {response.json()['duration']:.2f}s")
else:
    print(f"\n❌ TTS Failed: {response.json().get('message')}")
