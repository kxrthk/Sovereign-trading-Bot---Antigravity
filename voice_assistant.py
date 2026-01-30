import asyncio
import edge_tts
import os
import uuid
import requests
import base64
import json

# Configuration
VOICE_MALE_EDGE = "en-US-ChristopherNeural"
VOICE_FEMALE_EDGE = "en-US-AriaNeural"
OUTPUT_DIR = "dashboard/dist/assets/audio"
SARVAM_API_KEY = "sk_zsitm528_Y4FJQhpTAfEpmyj6quedWPoF"
SARVAM_URL = "https://api.sarvam.ai/text-to-speech"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class OracleVoice:
    async def generate_speech(self, text, gender="male"):
        """
        Generates Audio using Sarvam AI (Primary) or Edge TTS (Fallback).
        """
        # Sarvam returns WAV by default. Using .wav ensures browser plays it correctly immediately.
        filename = f"speech_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # 1. Try Sarvam AI First
        try:
            print(f"[SARVAM TTS] Requesting: {text[:30]}...")
            
            # Validated Speakers: 'anushka' (Female), 'kabir' (Male)
            target_speaker = "anushka" if gender.lower() == "female" else "kabir"
            
            payload = {
                "inputs": [text],
                "target_language_code": "en-IN", 
                "speaker": target_speaker,
                "pitch": 0,
                "pace": 1.0,
                "loudness": 1.0, # Natural loudness
                "speech_sample_rate": 16000,
                "enable_preprocessing": False, # DISABLED to prevent static/artifacts
                "model": "bulbul:v1" # UPDATED TO CORRECT VERSION
            }
            
            headers = {
                "Content-Type": "application/json",
                "api-subscription-key": SARVAM_API_KEY
            }
            
            # Make synchronous request non-blocking
            response = await asyncio.to_thread(
                requests.post, 
                SARVAM_URL, 
                json=payload, 
                headers=headers, 
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # Sarvam usually returns base64 audio in 'audios' list
                if "audios" in data and len(data["audios"]) > 0:
                    audio_b64 = data["audios"][0]
                    with open(output_path, "wb") as f:
                        f.write(base64.b64decode(audio_b64))
                        
                    print(f"[SARVAM TTS] Success! Saved to {filename}")
                    return f"/assets/audio/{filename}"
                else:
                    print(f"[SARVAM ERROR] No audio in response: {data}")
            else:
                print(f"[SARVAM ERROR] {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"[SARVAM FAILED] {e}. Falling back to Edge TTS.")

        # 2. Fallback to Edge TTS
        try:
            print("[EDGE TTS] Engaging Fallback...")
            if gender.lower() == "female":
                voice = VOICE_FEMALE_EDGE
                rate = "+10%"
                pitch = "+2Hz"
            else:
                voice = VOICE_MALE_EDGE
                rate = "-5%"
                pitch = "-2Hz"
            
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(output_path)
            return f"/assets/audio/{filename}"
            
        except Exception as e:
            print(f"[EDGE TTS ERROR] {e}")
            return None
