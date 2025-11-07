"""Create a test audio file using gTTS"""
from gtts import gTTS
import os

# Create test audio
text = "What is artificial intelligence?"
tts = gTTS(text=text, lang='en', slow=False)

# Save to file
os.makedirs('./test_audio', exist_ok=True)
output_file = './test_audio/test_question.mp3'
tts.save(output_file)

print(f"✅ Created test audio file: {output_file}")
print(f"Text: {text}")
