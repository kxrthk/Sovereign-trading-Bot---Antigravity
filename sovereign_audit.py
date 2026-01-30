import google.generativeai as genai
import os
import librarian  # Your bulk loader
from dotenv import load_dotenv

# --- PERSISTENT SECRETS LOADING ---
load_dotenv()
user_secrets_path = os.path.join(os.path.expanduser("~"), "sovereign_secrets.env")
if os.path.exists(user_secrets_path):
    load_dotenv(user_secrets_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # print("[ERROR] API Key Missing. Please run Setup_Secrets.bat")
    pass
else:
    genai.configure(api_key=api_key)

# THE LAW: Use this system instruction to "jail" the AI in your data
STRICT_LAW = (
    "You are a Sovereign Auditor. You are FORBIDDEN from using any knowledge "
    "not found in the provided research papers. If an answer isn't in the PDFs, "
    "say 'DATA NOT IN RESEARCH'. "
    "Every claim MUST include a citation: '[Source: File_Name.pdf(or ppt), Page X]'. "
    "If papers contradict, prioritize the most recent date."
)

import model_factory
model = model_factory.get_functional_model(system_instruction=STRICT_LAW)

def run_internal_audit(chart_path):
    print(f"\n[AUDIT] Convening The Boardroom for {chart_path}...")
    
    # 1. Load the 'Sovereign Knowledge' (Your 25+ PDFs)
    print("   [1/4] Loading Knowledge Base (may take time)...")
    textbooks = librarian.get_knowledge_base()
    
    if not textbooks:
        print("[ERR] No books found. Audit Cancelled.")
        return

    # Check Chart
    if not os.path.exists(chart_path):
        print(f"[ERR] Chart not found: {chart_path}")
        return

    print("   [2/4] Uploading Chart Evidence...")
    chart = genai.upload_file(chart_path)

    # --- STEP 1: THE PROPOSAL ---
    print("\n[ANALYST] Scanning for opportunities...")
    analyst_prompt = (
        "Role: Optimistic Analyst. "
        "Task: Identify a BUY or SELL setup in this chart using ONLY the provided PDFs. "
        "Output: Strategy Name, Entry Price, and Citation."
    )
    # Note: We pass the list of file handles + chart + prompt
    proposal = model.generate_content(textbooks + [chart, analyst_prompt])
    print(f"\n[PROPOSAL]:\n{proposal.text}")

    # --- STEP 2: THE CHALLENGE ---
    print("\n[SKEPTIC] Searching for risks...")
    skeptic_prompt = (
        f"Role: Bearish Risk Manager. "
        f"The Analyst proposed this: {proposal.text}. "
        "Find every reason in the research papers to REJECT this trade. "
        "Look for risk factors, contradicting patterns, or poor risk/reward rules in the docs."
    )
    challenge = model.generate_content(textbooks + [chart, skeptic_prompt])
    print(f"\n[CHALLENGE]:\n{challenge.text}")

    # --- STEP 3: THE FINAL VERDICT ---
    print("\n[JUDGE] Deliberating...")
    judge_prompt = (
        f"Analyst says: {proposal.text}. Skeptic says: {challenge.text}. "
        "Based ONLY on the research papers, who wins? "
        "Answer: 'APPROVED' or 'REJECTED' followed by a 1-sentence Final Verdict citing the winning rule."
    )
    verdict = model.generate_content(textbooks + [chart, judge_prompt])
    
    return verdict.text

if __name__ == "__main__":
    # Test file path - User should replace this
    test_chart = "dashboard/dist/assets/test_chart.png" 
    
    # If no test chart, user needs one
    if not os.path.exists(test_chart):
        # Look for ANY png in current dir
        files = [f for f in os.listdir('.') if f.lower().endswith('.png')]
        if files:
            test_chart = files[0]
        else:
            print("\n[SETUP NEEDED] Please name a chart image 'chart.png' in this folder to test.")
            exit()
            
    final_answer = run_internal_audit(test_chart)
    print(f"\n[DECISION]:\n{final_answer}")
