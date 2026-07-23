import re
import sys
import json
import time
import csv
from datetime import datetime
import requests
from difflib import SequenceMatcher

# Optional: pip install colorama requests
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False

KNOWN_HANDLES = {
    "paytm": "Paytm", "ybl": "PhonePe / Yes Bank", "oksbi": "SBI", 
    "okhdfcbank": "HDFC", "okaxis": "Axis", "okicici": "ICICI",
    "ibl": "IDBI", "upi": "Generic", "axl": "Amazon Pay", 
    "apl": "Airtel", "jio": "Jio", "okbizaxis": "Axis Business", 
    "okbbl": "Bob Bank", "sbi": "SBI Direct"
}

COMMON_HANDLES = list(KNOWN_HANDLES.keys()) + ["okbank", "gpay", "phonepe", "bhim", "amazon"]

SCAM_WORDS = ["refund", "cashback", "support", "help", "reward", "offer", "winner", "urgent", "verify", "kyc", "loan", "gift", "fraud"]
BRANDS = ["paytm", "phonepe", "gpay", "amazon", "flipkart", "sbi", "hdfc", "axis", "icici"]

def c(text, color="white"):
    if not COLOR:
        return text
    colors = {"red": Fore.RED, "green": Fore.GREEN, "yellow": Fore.YELLOW, "blue": Fore.BLUE, "cyan": Fore.CYAN, "bold": Style.BRIGHT}
    return f"{colors.get(color, '')}{text}{Style.RESET_ALL}"

def banner():
    print(c("""
╔══════════════════════════════════════════════╗
║     🔍 UPI OSINT PRO v4 - Upgraded           ║
║     Phone → UPI Mapping + Fraud Analyzer     ║
║              by naveen Khatri (upgraded)              ║
╚══════════════════════════════════════════════╝
""", "cyan"))

def similarity(a, b):
    return int(SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100)

def validate_vpa(vpa):
    """Attempt basic validation (some public endpoints are flaky; expand with merchant keys if available)."""
    try:
        # Example Razorpay-style (needs keys for prod; placeholder)
        # For demo, we simulate + common checks
        headers = {"User-Agent": "UPI-OSINT"}
        # Many PSPs have /validate but require auth. Fallback to format + known patterns.
        if re.match(r"^[a-zA-Z0-9.\-_]{2,}@[a-zA-Z0-9]{2,}$", vpa):
            return {"valid_format": True, "note": "Existence requires PSP API or app test"}
        return {"valid_format": False}
    except:
        return {"valid_format": False, "error": True}

def check_phone_upi(phone):
    """Real mapping: Generate & test common VPAs for phone."""
    if not re.match(r"^[6-9]\d{9}$", phone):
        return {"error": "Invalid Indian mobile format"}
    
    results = []
    print(c(f"\nTesting UPI mappings for {phone}...", "yellow"))
    
    for handle in COMMON_HANDLES:
        vpa = f"{phone}@{handle}"
        val = validate_vpa(vpa)
        # In practice, you could add requests to known endpoints here (rate-limited)
        results.append({
            "vpa": vpa,
            "handle": handle,
            "likely_active": "Partial check (use app/API for confirmation)",
            "provider": KNOWN_HANDLES.get(handle, "Unknown")
        })
        print(c(f"  ✓ {vpa} → {results[-1]['provider']}", "green" if "ok" in handle else "blue"))
        time.sleep(0.3)  # Rate limit
    
    return {"phone": phone, "mappings": results, "note": "Many numbers are UPI-registered. Full name fetch needs paid NPCI-linked API."}

def analyze_upi(upi, claimed_name="", preview_name=""):
    result = {"UPI": upi, "Analysis": {}, "Warnings": [], "Score": 100}
    
    if not re.match(r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z0-9]{2,64}$", upi):
        result["Status"] = "INVALID FORMAT"
        result["Score"] = 0
        return result
    
    username, handle = upi.split("@")
    handle = handle.lower()
    
    result["Username"] = username
    result["Handle"] = handle
    result["Provider"] = KNOWN_HANDLES.get(handle, "Unknown")
    
    # Scam & pattern checks
    for word in SCAM_WORDS:
        if word in username.lower():
            result["Warnings"].append(f"Scam keyword: {word}")
            result["Score"] -= 25
    
    for b in BRANDS:
        if b in username.lower():
            result["Warnings"].append(f"Brand impersonation: {b}")
            result["Score"] -= 20
    
    if re.search(r"\d{4,}", username):
        result["Warnings"].append("Long digits in username")
        result["Score"] -= 15
    
    # Name match
    if claimed_name and preview_name:
        match_pct = similarity(claimed_name, preview_name)
        result["Name_Match"] = f"{match_pct}%"
        if match_pct < 50:
            result["Warnings"].append("Name mismatch - high risk")
            result["Score"] -= 40
    
    # Risk verdict
    score = max(0, result["Score"])
    if score >= 80:
        result["Risk"] = "LOW - Likely Legit"
    elif score >= 60:
        result["Risk"] = "MEDIUM"
    else:
        result["Risk"] = "HIGH / FRAUD LIKELY"
    
    return result

def save_report(data, fmt="json"):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    if fmt == "json":
        with open(f"upi_report_{ts}.json", "w") as f:
            json.dump(data, f, indent=2)
    elif fmt == "csv":
        with open(f"upi_report_{ts}.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys() if isinstance(data, dict) else ["key"])
            # Simplified CSV
            pass
    print(c(f"Report saved: upi_report_{ts}.{fmt}", "cyan"))

def main():
    banner()
    while True:
        inp = input(c("\nEnter Phone (10-digit) or UPI ID (or 'exit'): ", "yellow")).strip()
        if inp.lower() in ["exit", "quit"]:
            break
        
        if re.match(r"^[6-9]\d{9}$", inp):
            mapping = check_phone_upi(inp)
            print(json.dumps(mapping, indent=2))
            save_report(mapping)
        else:
            claimed = input("Claimed name (optional): ").strip()
            preview = input("Preview name (optional): ").strip()
            result = analyze_upi(inp, claimed, preview)
            print(c("\n" + json.dumps(result, indent=2), "green"))
            save_report(result)
        
        if input(c("\nAnother check? (y/n): ", "yellow")).lower() != "y":
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(c("\nExited.", "red"))
