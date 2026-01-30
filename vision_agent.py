import google.generativeai as genai
import os
from dotenv import load_dotenv

import config # Use Central Config for Decryption
# --- ROBUST MODEL CONFIGURATION ---
api_key = config.GEMINI_API_KEY

def get_model_candidates(api_key):
    """
    Returns priority list of models.
    """
    if not api_key: return []
    
    genai.configure(api_key=api_key)
    
    return [
        "gemini-2.5-flash",           # 1. New Flash Experiment (Prioritized for Speed)
        "gemini-2.0-flash",           # 2. The Flagship (Fast & Smart)
        "gemini-2.0-flash-lite",      # 3. The Backup (High Rate Limits)
        "gemini-flash-latest",        # 4. Stable Alias
        "gemini-1.5-flash-latest"     # 5. Legacy Fallback (Verified String)
    ]

model_candidates = get_model_candidates(api_key)

if not model_candidates:
    print("⚠️ [VISION] GEMINI_API_KEY not found. Vision features will be disabled.")

class VisionAgent:
    def __init__(self):
        self.personas = {
            # 1. SCALP MODE
            "SCALP": "You are a ruthless Scalp Trader. Look for 1-minute breakouts, liquidity sweeps, and quick 1:2 R:R setups. Be brief.",
            
            # 2. SWING MODE
            "SWING": "You are a patient Swing Trader. Look for 4H/Daily trends, major support/resistance, and chart patterns (Head & Shoulders, Flags).",
            
            # 3. RISK MANAGER
            # 3. RISK MANAGER (SIMPLIFIED)
            "RISK": "You are a Risk Manager. Explain to a complete beginner. Max 3 bullet points. 1. SAFETY LINE (Stop Loss Price). 2. DANGER ZONE (Price to avoid). 3. WHY? (One simple sentence). No complex jargon.",

            # 4. DEEP SCAN (ALL IN ONE)
            # 4. DEEP SCAN (ALL IN ONE - BEGINNER FRIENDLY)
            "DEEP_SCAN": "You are a Trading Mentor. Keep it SHORT and SIMPLE for a beginner. First, PROVE you see the chart: 'I see [Price/Color]...'. Then: 1. TREND: Up, Down, or Sideways? 2. ACTION: Buy or Wait? (Give entry). 3. STOP LOSS: Exact price. Max 100 words.",

            # 5. PRICE ACTION (Pure Structure)
            "PRICE_ACTION": "Ignore all indicators. Focus ONLY on Market Structure (HH/HL), Supply/Demand Zones, and Candlestick psychology. Tell me where the 'Smart Money' is waiting.",


            # 4. PRICE ACTION (Pure Structure)
            "PRICE_ACTION": "Ignore all indicators. Focus ONLY on Market Structure (HH/HL), Supply/Demand Zones, and Candlestick psychology. Tell me where the 'Smart Money' is waiting.",

            # 5. TRADE_PLAN (Actionable)
            "TRADE_PLAN": "Give me a strict execution plan. Format: ENTRY: [Price], STOP LOSS: [Price], TARGET 1: [Price], REASON: [1-sentence logic].",

            # 6. POST_MORTEM (The Reviewer)
            "ANALYSIS": "I have marked my trade on this chart. Critique it brutally. Did I chase? Was my stop loss logical? Rate this trade 1-10 based on risk management."
        }

    def analyze_chart(self, image_path, mode="SWING"):
        """
        Sends the chart image to the AI, trying multiple models if one fails (429/404).
        """
        global model_candidates
        if not model_candidates:
            return "⚠️ Vision Agent Error: API Key Missing. Please set GEMINI_API_KEY."

        # Check file
        if not os.path.exists(image_path):
            return f"⚠️ VISION ERROR: File not found ({image_path})"

        print(f"\n[VISION DEBUG] Received Request! \n   -> Image: {image_path}\n   -> Mode: {mode}\n   -> Models: {model_candidates}\n")
        
        print(f"[VISION AGENT] Analyzing {image_path} in [{mode}] mode...")
        
        # Prepare content
        try:
             sample_file = genai.upload_file(path=image_path, display_name="Chart Analysis")
             
             # 1. LOAD THE LIBRARY (RESTORED)
             import librarian
             print("   [LIBRARY] Fetching Knowledge Base...")
             knowledge_base = librarian.get_knowledge_base()

             # 🔥 NEW: THE "TRADING BUDDY" PROMPT

             # 🔥 NEW: THE "TRADING BUDDY" PROMPT
             prompt = (
                "You are a friendly, professional trading coach talking to a beginner friend. "
                "Look at this chart and give advice in SIMPLE, PLAIN ENGLISH. "
                "Do NOT use complex jargon like 'overhead supply' or 'range consolidation'. "
                "Do NOT use markdown bolding (**text**) or emojis. Keep the text clean and readable. "
                "Do NOT write long paragraphs. "
                
                "Output Structure:"
                "1. The Vibe: One sentence on what the stock is doing (e.g., 'It's stuck sideways', 'It's trying to recover')."
                "2. The Plan (Scalp):"
                "   - BUY above: [Price]"
                "   - TARGET: [Price]"
                "   - STOP LOSS: [Price]"
                "   - SELL below: [Price]"
                "3. Quick Warning: One bullet point on what to watch out for."
                
                "Tone: Encouraging, short, and direct. No emojis. No bold text. Max 150 words."
            )
             
             # Combine: [Knowledge Files] + [Image] + [Prompt]
             request_content = knowledge_base + [sample_file, prompt]
             
        except Exception as e:
            return f"⚠️ UPLOAD ERROR: {e}"

        # --- FALLBACK LOOP ---
        last_error = ""
        
        for model_name in model_candidates:
            try:
                print(f"   [>>] Attempting with model: {model_name}...")
                active_model = genai.GenerativeModel(model_name)
                
                # Generate with Context
                response = active_model.generate_content(request_content)
                
                # If we got here, it worked!
                print(f"   [OK] Success with {model_name}")
                return response.text
                
            except Exception as e:
                error_str = str(e)
                last_error = error_str
                
                # If it's a Rate Limit (429), try next immediately
                if "429" in error_str or "Quota" in error_str:
                    print(f"   [!!] Rate Limit Hit on {model_name}. Switching to backup...")
                    continue
                # If 404 (Not Found), try next
                if "404" in error_str:
                    print(f"   [??] Model {model_name} not found. Switching...")
                    continue
                
                # For other errors (like Auth), print and continue just in case
                print(f"   [XX] Error ({model_name}): {error_str[:50]}...")
                    
        return f"⚠️ ALL MODELS FAILED. Last Error: {last_error}"

# Test (Only runs if you execute this file directly)
if __name__ == "__main__":
    agent = VisionAgent()
    # Replace with a real image path on your laptop to test
    # print(agent.analyze_chart("test_chart.png", mode="SWING"))
