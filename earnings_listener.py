import os
import json
import time
from google import genai
import config

# Initialize Client
api_key = config.GEMINI_API_KEY
if api_key and api_key.startswith("ENC:"):
    from crypto_vault import decrypt_secret
    api_key = decrypt_secret(api_key[4:])

client = None
if api_key:
    client = genai.Client(api_key=api_key)

class EarningsListener:
    """
    The Ear. Listens to Audio for CEO Sentiment.
    """
    def __init__(self):
        self.temp_audio = "temp_earnings.mp3"
        
    def analyze_youtube_video(self, video_url):
        print(f"\n[EARNINGS LISTENER] 👂 Tuning into: {video_url}...")
        
        # 1. Download Audio
        # Requires yt-dlp installed in system path or env
        # Using basic command line wrapper
        try:
            import yt_dlp
        except ImportError:
            print("[ERR] yt_dlp not installed. Run 'pip install yt-dlp'.")
            return "Audio Analysis Failed: Missing Library."

        # Cleaning old files
        if os.path.exists(self.temp_audio):
            os.remove(self.temp_audio)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
            'outtmpl': 'temp_earnings',
            'quiet': True
        }

        print("   [DOWNLOAD] Extracting Audio Stream...", end=" ")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            print("✅ Captured.")
        except Exception as e:
            print(f"❌ Failed: {e}")
            return f"Download Failed: {e}"

        # 2. Upload to Gemini
        if not client: return "Client Error"
        
        print("   [LISTEN] Uploading to Brain...", end=" ")
        try:
            # Re-verify filename (yt-dlp sometimes adds extensions)
            actual_file = "temp_earnings.mp3"
            
            audio_file = client.files.upload(file=actual_file)
            
            # Wait for processing
            while "PROCESSING" in str(audio_file.state):
                time.sleep(1)
                audio_file = client.files.get(name=audio_file.name)
            print("✅ Ready.")
                
            # 3. Analyze
            prompt = """
            Listen to this Earnings Call / Market Update.
            TASK: Analyze the SPEAKER'S TONE and CONFIDENCE.
            1. Are they hesitant, dodging questions, or confident?
            2. Extract 3 Key Forward-Looking Statements.
            3. Sentiment Score: -10 (Panic) to +10 (Euphoria).
            
            OUTPUT JSON: { "tone": "string", "key_points": [], "score": int }
            """
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, audio_file],
                config={'response_mime_type': 'application/json'}
            )
            
            result = json.loads(response.text)
            print(f"   [ANALYSIS] Tone: {result.get('tone')} | Score: {result.get('score')}")
            return result

        except Exception as e:
            print(f"[ERR] Analysis Failed: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    listener = EarningsListener()
    # Test with a generic finance video if needed
    # listener.analyze_youtube_video("http://youtube.com/watch?v=EXAMPLE")
