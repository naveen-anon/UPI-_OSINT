import re
import sys
import time

KNOWN_HANDLES = {
    "paytm": "Paytm",
    "ybl": "Yes Bank",
    "oksbi": "State Bank of India",
    "okhdfcbank": "HDFC Bank",
    "okaxis": "Axis Bank",
    "okicici": "ICICI Bank",
    "ibl": "IDBI Bank",
    "upi": "Generic UPI"
}

FAKE_KEYWORDS = ["test", "demo", "fake", "sample", "temp", "dummy", "check"]

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════╗
║                🔍 ADVANCED UPI OSINT SCANNER            ║
║                     Developed by naveen_anon             ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_colored(text, color_code):
    """Print colored text"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    return f"{colors.get(color_code, '')}{text}{colors['end']}"

def loading_animation():
    """Show loading animation"""
    for i in range(3):
        sys.stdout.write('\r' + 'Analyzing' + '.' * (i+1) + '   ')
        sys.stdout.flush()
        time.sleep(0.3)
    print()

def advanced_upi_osint(upi):
    report = {}
    score = 100
    warnings = []
    recommendations = []

    # 1️⃣ Format check
    pattern = r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$"
    if not re.match(pattern, upi):
        report["status"] = "❌ INVALID FORMAT"
        report["score"] = 0
        report["verdict"] = "❌ INVALID UPI ID"
        return report

    username, handle = upi.split("@", 1)
    handle_lower = handle.lower()

    report["Username"] = print_colored(username, 'cyan')
    report["Handle"] = print_colored(handle, 'yellow')
    
    # 2️⃣ Handle intelligence
    if handle_lower in KNOWN_HANDLES:
        report["Provider"] = print_colored(KNOWN_HANDLES[handle_lower], 'green')
        recommendations.append(f"Verified {KNOWN_HANDLES[handle_lower]} UPI handle")
    else:
        report["Provider"] = print_colored("Unknown / Custom", 'yellow')
        warnings.append("⚠️ Unknown UPI handle detected")
        score -= 20
        recommendations.append("Verify this handle with the recipient")

    # 3️⃣ Mobile-number pattern
    if re.fullmatch(r"[6-9]\d{9}", username):
        report["Type"] = print_colored("Mobile Number based", 'blue')
        warnings.append("📱 Username appears to be a mobile number")
        score -= 5
        recommendations.append("Cross-check with registered mobile number")
    else:
        report["Type"] = print_colored("VPA (Virtual Payment Address)", 'blue')

    # 4️⃣ Repeated characters
    if re.search(r"(.)\1\1+", username):
        warnings.append("🔄 Repeated characters detected")
        score -= 15

    # 5️⃣ Random digits / year pattern
    if re.search(r"\d{4,}", username):
        warnings.append("🔢 Long number sequence in username")
        score -= 10

    # 6️⃣ Fake keywords
    found_keywords = []
    for word in FAKE_KEYWORDS:
        if word in username.lower():
            found_keywords.append(word)
            score -= 30
    
    if found_keywords:
        warnings.append(f"🚨 Suspicious keywords found: {', '.join(found_keywords)}")

    # 7️⃣ Username length checks
    if len(username) < 3:
        warnings.append("📏 Username too short (risk of typo)")
        score -= 25
    elif len(username) > 30:
        warnings.append("📏 Username unusually long")
        score -= 10

    # 8️⃣ Special characters check
    special_chars = re.findall(r'[^a-zA-Z0-9.\-_]', username)
    if special_chars:
        warnings.append(f"⚡ Unusual characters detected: {set(special_chars)}")
        score -= 5

    # 9️⃣ Common patterns
    if username.isdigit():
        warnings.append("🔢 Username is all digits")
        score -= 5
    elif username.isalpha():
        recommendations.append("✅ All-alphabetic username is good practice")

    # 🔟 Final verdict
    if score >= 80:
        verdict = print_colored("✅ LIKELY GENUINE", 'green')
        report["Risk Level"] = print_colored("LOW", 'green')
    elif score >= 60:
        verdict = print_colored("⚠️ CAUTION ADVISED", 'yellow')
        report["Risk Level"] = print_colored("MEDIUM", 'yellow')
        recommendations.append("Send small test amount first")
    elif score >= 40:
        verdict = print_colored("⚠️ SUSPICIOUS", 'yellow')
        report["Risk Level"] = print_colored("HIGH", 'red')
        recommendations.append("Verify through alternative channel")
    else:
        verdict = print_colored("❌ VERY LIKELY FAKE", 'red')
        report["Risk Level"] = print_colored("CRITICAL", 'red')
        recommendations.append("DO NOT PROCEED without verification")

    report["Confidence Score"] = print_colored(f"{max(score, 0)}/100", 'bold')
    report["Verdict"] = verdict
    report["Warnings"] = warnings if warnings else [print_colored("✅ No warnings", 'green')]
    report["Recommendations"] = recommendations

    return report

def print_report(result):
    """Print formatted report"""
    print("\n" + "═" * 60)
    print(print_colored("📊 ANALYSIS REPORT", 'bold'))
    print("═" * 60)
    
    # Basic Info Section
    print(print_colored("\n📋 BASIC INFORMATION", 'cyan'))
    print("─" * 40)
    print(f"{'Username:':<25} {result.get('Username', 'N/A')}")
    print(f"{'Handle:':<25} {result.get('Handle', 'N/A')}")
    print(f"{'Provider:':<25} {result.get('Provider', 'N/A')}")
    print(f"{'Type:':<25} {result.get('Type', 'N/A')}")
    
    # Risk Assessment Section
    print(print_colored("\n⚠️  RISK ASSESSMENT", 'cyan'))
    print("─" * 40)
    print(f"{'Confidence Score:':<25} {result.get('Confidence Score', 'N/A')}")
    print(f"{'Risk Level:':<25} {result.get('Risk Level', 'N/A')}")
    print(f"{'Verdict:':<25} {result.get('Verdict', 'N/A')}")
    
    # Warnings Section
    print(print_colored("\n🚨 WARNINGS & ALERTS", 'cyan'))
    print("─" * 40)
    warnings = result.get("Warnings", [])
    if warnings:
        for warning in warnings:
            print(f"• {warning}")
    else:
        print("✅ No issues detected")
    
    # Recommendations Section
    print(print_colored("\n💡 RECOMMENDATIONS", 'cyan'))
    print("─" * 40)
    recommendations = result.get("Recommendations", [])
    for rec in recommendations:
        print(f"• {rec}")
    
    print("\n" + "═" * 60)

def main():
    print_banner()
    
    while True:
        print(print_colored("\nUPI ID Analysis Tool", 'bold'))
        print("─" * 40)
        
        upi_id = input(print_colored("Enter UPI ID: ", 'yellow')).strip()
        
        if not upi_id:
            print(print_colored("Please enter a valid UPI ID!", 'red'))
            continue
            
        if upi_id.lower() in ['exit', 'quit', 'q']:
            print(print_colored("\nExiting... Stay safe! 👋", 'cyan'))
            break
        
        loading_animation()
        
        result = advanced_upi_osint(upi_id)
        print_report(result)
        
        # Disclaimer
        print(print_colored("\nℹ️  IMPORTANT DISCLAIMER:", 'bold'))
        print("This tool uses OSINT + heuristics for analysis.")
        print("Always verify through official UPI apps payment preview.")
        print("Send a small test amount first for unknown recipients.")
        print("Never share OTP or UPI PIN with anyone.")
        
        # Continue option
        print("\n" + "─" * 60)
        cont = input(print_colored("Check another UPI ID? (y/n): ", 'yellow')).lower()
        if cont != 'y':
            print(print_colored("\nThank you for using UPI OSINT Scanner!", 'cyan'))
            print(print_colored("Credits: naveen_anon", 'purple'))
            print(print_colored("Stay safe online! 🔒", 'green'))
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(print_colored("\n\nProcess interrupted. Goodbye! 👋", 'cyan'))
        sys.exit(0)
    except Exception as e:
        print(print_colored(f"\nError: {e}", 'red'))
        sys.exit(1)
