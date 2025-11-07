"""
Quick test script for voice features
"""
import requests
import json

BASE_URL = "http://localhost:8080"

def test_tts():
    """Test Text-to-Speech"""
    print("\n🔊 Testing Text-to-Speech...")
    
    response = requests.post(
        f"{BASE_URL}/speak",
        json={"text": "Hello! This is DocuMind Voice. I can read and speak about your documents."}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ TTS Success!")
            print(f"   Audio URL: {data['audio_url']}")
            print(f"   Duration: {data['duration']:.2f}s")
            return True
        else:
            print(f"❌ TTS Failed: {data.get('message')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    return False

def test_system_stats():
    """Test system stats endpoint"""
    print("\n📊 Testing System Stats...")
    
    response = requests.get(f"{BASE_URL}/stats")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ Stats Retrieved!")
            stats = data['stats']
            print(f"   Documents: {stats.get('total_documents', 0)}")
            print(f"   Chunks: {stats.get('total_chunks', 0)}")
            return True
        else:
            print(f"❌ Stats Failed: {data.get('message')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    return False

def main():
    print("=" * 60)
    print("🎤 DocuMind Voice - Feature Test")
    print("=" * 60)
    
    # Test 1: System Stats
    test_system_stats()
    
    # Test 2: Text-to-Speech
    test_tts()
    
    print("\n" + "=" * 60)
    print("✅ Basic tests complete!")
    print("\n📝 Next steps:")
    print("   1. Open http://localhost:8080/voice-test in your browser")
    print("   2. Test voice recording and transcription")
    print("   3. Upload a PDF and try voice queries")
    print("=" * 60)

if __name__ == "__main__":
    main()
