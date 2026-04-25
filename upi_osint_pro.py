import re
import sys
import json
import time
import difflib
from datetime import datetime

# =====================================================
#            UPI REAL DETECTOR PRO v3
#         Developed by naveen_anon (upgraded)
# =====================================================

KNOWN_HANDLES = {
    "paytm": "Paytm",
    "ybl": "PhonePe / Yes Bank",
    "oksbi": "State Bank of India",
    "okhdfcbank": "HDFC Bank",
    "okaxis": "Axis Bank",
    "okicici": "ICICI Bank",
    "ibl": "IDBI Bank",
    "upi": "Generic UPI",
    "axl": "Amazon Pay",
    "apl": "Airtel Payments Bank",
    "jio": "Jio Payments"
}

SCAM_WORDS = [
    "refund", "cashback", "support", "help",
    "reward", "offer", "winner", "urgent",
    "verify", "kyc", "loan", "gift"
]

BRANDS = [
    "paytm", "phonepe", "gpay", "googlepay",
    "amazon", "flipkart", "bank", "sbi",
    "hdfc", "axis", "icici"
]

# -------------------------------------

def color(txt, c):
    codes = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "bold": "\033[1m",
        "end": "\033[0m"
    }
    return f"{codes.get(c,'')}{txt}{codes['end']}"

# -------------------------------------

def banner():
    print(color("""
╔══════════════════════════════════════════════╗
║        🔍 UPI REAL DETECTOR PRO v3          ║
║          Fraud & Trust Analyzer             ║
║             by naveen_anon                  ║
╚══════════════════════════════════════════════╝
""", "cyan"))

# -------------------------------------

def loading():
    for i in range(3):
        print(color("Analyzing" + "." * (i + 1), "yellow"))
        time.sleep(0.4)

# -------------------------------------

def similarity(a, b):
    return int(difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100)

# -------------------------------------

def analyze_upi(upi, claimed_name="", preview_name=""):
    result = {}
    warnings = []
    rec = []
    score = 100

    pattern = r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z0-9]{2,64}$"

    if not re.match(pattern, upi):
        return {
            "status": "INVALID FORMAT",
            "score": 0,
            "risk": "CRITICAL"
        }

    username, handle = upi.split("@")
    handle = handle.lower()

    result["UPI ID"] = upi
    result["Username"] = username
    result["Handle"] = handle

    # Provider check
    if handle in KNOWN_HANDLES:
        result["Provider"] = KNOWN_HANDLES[handle]
    else:
        result["Provider"] = "Unknown"
        warnings.append("Unknown handle")
        score -= 20

    # Scam keywords
    for word in SCAM_WORDS:
        if word in username.lower():
            warnings.append(f"Scam keyword detected: {word}")
            score -= 25

    # Brand impersonation
    for b in BRANDS:
        if b in username.lower():
            warnings.append(f"Possible brand impersonation: {b}")
            score -= 20

    # Digits
    if re.search(r"\d{4,}", username):
        warnings.append("Long digit sequence")
        score -= 10

    # Repeated chars
    if re.search(r"(.)\1\1+", username):
        warnings.append("Repeated characters")
        score -= 10

    # Mobile style
    if re.fullmatch(r"[6-9]\d{9}", username):
        warnings.append("Looks like mobile number based UPI")
        score -= 5

    # Claimed vs Preview Name
    if claimed_name and preview_name:
        match = similarity(claimed_name, preview_name)
        result["Name Match"] = f"{match}%"

        if match < 40:
            warnings.append("Claimed name mismatch")
            score -= 35
        elif match < 70:
            warnings.append("Partial name mismatch")
            score -= 15
        else:
            rec.append("Name matches receiver")

    # Final Risk
    score = max(score, 0)

    if score >= 80:
        risk = "LOW"
        verdict = "LIKELY SAFE"
    elif score >= 60:
        risk = "MEDIUM"
        verdict = "CAUTION ADVISED"
    elif score >= 40:
        risk = "HIGH"
        verdict = "SUSPICIOUS"
    else:
        risk = "CRITICAL"
        verdict = "VERY LIKELY FRAUD"

    result["Score"] = score
    result["Risk"] = risk
    result["Verdict"] = verdict
    result["Warnings"] = warnings
    result["Recommendations"] = rec

    if risk in ["HIGH", "CRITICAL"]:
        rec.append("Do NOT send money without verification")
    else:
        rec.append("Send small test amount first")

    return result

# -------------------------------------

def show(result):
    print(color("\n════════ REPORT ════════", "bold"))

    for k, v in result.items():
        if k not in ["Warnings", "Recommendations"]:
            print(f"{k:<18}: {v}")

    print(color("\nWarnings:", "yellow"))
    if result["Warnings"]:
        for w in result["Warnings"]:
            print("•", w)
    else:
        print("No warnings")

    print(color("\nRecommendations:", "green"))
    for r in result["Recommendations"]:
        print("•", r)

# -------------------------------------

def save_json(data):
    file = "upi_report.json"
    with open(file, "w") as f:
        json.dump(data, f, indent=4)
    print(color(f"\nSaved report: {file}", "cyan"))

# -------------------------------------

def main():
    banner()

    while True:
        upi = input(color("Enter UPI ID: ", "yellow")).strip()

        if upi.lower() in ["exit", "quit"]:
            print("Goodbye 👋")
            break

        claimed = input("Claimed Receiver Name (optional): ").strip()
        preview = input("Payment Preview Name (optional): ").strip()

        loading()

        result = analyze_upi(upi, claimed, preview)
        show(result)

        ask = input("\nSave JSON report? (y/n): ").lower()
        if ask == "y":
            save_json(result)

        again = input("\nCheck another? (y/n): ").lower()
        if again != "y":
            break

# -------------------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExited.")
