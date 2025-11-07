"""Test the complete voice pipeline"""
import requests
import json
import os

print("=" * 60)
print("🎤 Testing Complete Voice Pipeline")
print("=" * 60)

# Step 1: Check if we have documents
print("\n1️⃣ Checking system stats...")
response = requests.get("http://localhost:8080/stats")
if response.status_code == 200:
    stats = response.json()['stats']
    print(f"   Documents loaded: {stats.get('total_documents', 0)}")
    print(f"   Total chunks: {stats.get('total_chunks', 0)}")
else:
    print(f"   ⚠️  Could not get stats")

# Step 2: Test voice query with the audio file we created
print("\n2️⃣ Testing voice query pipeline...")
print("   Sending audio: 'What is artificial intelligence?'")

with open('./test_audio/test_question.mp3', 'rb') as audio_file:
    files = {'audio': audio_file}
    response = requests.post(
        "http://localhost:8080/voice-query",
        files=files
    )

print(f"\n   Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print(f"\n✅ Voice Pipeline Success!\n")
        print(f"📝 Your Question (transcribed):")
        print(f"   {data['question']}\n")
        print(f"💬 AI Answer:")
        print(f"   {data['answer'][:200]}...\n")
        print(f"🔊 Audio Response:")
        print(f"   http://localhost:8080{data['audio_url']}\n")
        print(f"📊 Metadata:")
        print(f"   Language: {data['transcription_language']}")
        print(f"   Sources used: {data['metadata']['sources_used']}")
        print(f"   Confidence: {data['metadata']['confidence']:.2%}")
    else:
        print(f"\n❌ Failed: {data.get('message')}")
else:
    print(f"\n❌ HTTP Error: {response.status_code}")
    print(f"   Response: {response.text}")

print("\n" + "=" * 60)
print("✅ Voice pipeline test complete!")
print("=" * 60)
