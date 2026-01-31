import time
from duckduckgo_search import DDGS
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

class BankWatcher:
    """
    The Hawk. Monitors Central Banks for Policy Shifts.
    """
    def __init__(self):
        self.targets = {
            "RBI": "site:rbi.org.in \"Monetary Policy Statement\" filetype:pdf",
            "FED": "site:federalreserve.gov \"FOMC Minutes\" filetype:pdf"
        }
        
    def scan_central_banks(self):
        print("\n[BANK WATCHER] 🦅 Scanning Central Bank Frequencies...")
        
        alerts = []
        ddgs = DDGS()
        
        for bank, query in self.targets.items():
            print(f"   [SCAN] {bank}...", end=" ")
            try:
                # Search for VERY recent PDFs (last month implied by sort usually, but DDGS is simple)
                # We add current year to query to stay fresh
                current_year = time.strftime("%Y")
                full_query = f"{query} {current_year}"
                
                results = ddgs.text(full_query, max_results=1)
                
                if results:
                    doc = results[0]
                    title = doc['title']
                    link = doc['href']
                    snippet = doc['body']
                    
                    print(f"Found: {title[:30]}...")
                    
                    # Analyze Tone
                    analysis = self._analyze_tone(bank, snippet, title)
                    if analysis['alert']:
                        alerts.append(f"[{bank} ALERT] {analysis['tone']}: {title} ({link})")
                else:
                    print("No new documents.")
                    
            except Exception as e:
                print(f"[ERR] {e}")
                
        return alerts

    def _analyze_tone(self, bank, text, title):
        """
        Uses Gemini to sniff out Hawkish/Dovish intent.
        """
        if not client: return {'alert': False}
        
        prompt = f"""
        Review this Central Bank Document Snippet.
        BANK: {bank}
        TITLE: {title}
        TEXT: "{text}"
        
        TASK: Classification.
        1. Is this a MAJOR Policy Update? (True/False)
        2. Is the tone HAWKISH (Raise Rates) or DOVISH (Cut Rates)?
        
        OUTPUT JSON: {{ "major": bool, "tone": "HAWKISH/DOVISH/NEUTRAL" }}
        """
        
        try:
            # Using Flash for speed
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            import json
            result = json.loads(response.text)
            
            return {
                'alert': result.get('major', False),
                'tone': result.get('tone', 'NEUTRAL')
            }
        except:
            return {'alert': False, 'tone': 'ERROR'}

if __name__ == "__main__":
    hawk = BankWatcher()
    alerts = hawk.scan_central_banks()
    for a in alerts:
        print(a)
