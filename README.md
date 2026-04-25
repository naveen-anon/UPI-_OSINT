# 🔍 UPI Real Detector Pro v3

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Platform-Termux%20%7C%20Linux-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Version-v3-red?style=for-the-badge">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge">
</p>

<p align="center">
  <b>Advanced UPI ID Trust Analyzer & Fraud Detection Tool</b><br>
  Built for awareness, verification & scam prevention.
</p>

---

## 📌 About

**UPI Real Detector Pro v3** is a smart Python CLI tool that analyzes UPI IDs using:

- Scam pattern detection  
- Trust scoring  
- Fake support ID alerts  
- Brand impersonation checks  
- Name mismatch analysis  

This helps detect suspicious UPI IDs **before sending money**.

---

## ⚡ Features

- ✅ UPI Format Validation  
- ✅ Known Bank Handle Detection  
- ✅ Suspicious Keyword Scanner  
- ✅ Cashback / Refund / Support Fraud Alerts  
- ✅ Brand Impersonation Detection  
- ✅ Name Match Engine  
- ✅ Risk Score (0–100)  
- ✅ Fraud Verdict  
- ✅ JSON Export  
- ✅ Premium CLI UI  
- ✅ Termux / Linux Supported

---

## 🧠 Example Detection

```text
refundhelp123@oksbi
paytmsupport@upi
cashbackwinner999@ybl
googlepayverify@okaxis
```
## 📷 Output Example

╔══════════════════════════════╗
║   UPI REAL DETECTOR PRO v3  ║
╚══════════════════════════════╝
``
UPI ID      : cashback999@oksbi
Provider    : SBI
Score       : 28
Risk        : CRITICAL
Verdict     : VERY LIKELY FRAUD

Warnings:
• cashback keyword found
• suspicious numeric pattern
• impersonation style detected
``
## 🚀 Installation

### 📱 Termux (Android)

```bash
pkg update && pkg upgrade -y
pkg install git python -y
git clone https://github.com/naveen-anon/UPI-_OSINT.git
cd UPI-_OSINT
python upi_osint_pro.py
```

