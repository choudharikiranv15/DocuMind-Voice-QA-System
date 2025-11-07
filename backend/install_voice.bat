@echo off
echo ========================================
echo Installing Voice Dependencies
echo ========================================
echo.

echo Installing Python packages...
pip install faster-whisper gtts pydub soundfile flask-cors

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Note: Piper TTS requires separate installation
echo Visit: https://github.com/rhasspy/piper
echo.
echo For now, the system will use gTTS (Google TTS) as fallback
echo which requires internet connection.
echo.
pause
