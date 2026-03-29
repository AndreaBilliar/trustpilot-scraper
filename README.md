#  Trustpilot Review Scraper 

A professional-grade Python tool designed to scrape customer reviews (date, rating, title, and body) from any company profile on Trustpilot.
It leverages `undetected_chromedriver` to bypass anti-bot protections and supports secure email-based authentication.

---

##  Key Features

* **Anti-Bot Bypass**: Uses `undetected_chromedriver` to reduce detection risk
* **Authentication Support**: Login via email with OTP verification directly in the terminal
* **Headless Mode**: Run the scraper in the background without opening a browser window
* **Clean Data Export**: Outputs structured `.csv` files (UTF-8-SIG, Excel-compatible)
* **Secure Configuration**: Sensitive data stored safely using `.env` files

---

##  Prerequisites

Before getting started, make sure you have:

1. A valid **Trustpilot account**
2. **Python 3.8+** installed
3. **Google Chrome** installed on your system

---

##  Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/AndreaBilliar/trustpilot-scraper.git
cd trustpilot-scraper
```

### 2. Create a virtual environment (recommended)

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Create your `.env` file

Copy the template:

**Windows**

```bash
copy .env.example .env
```

**Linux / macOS**

```bash
cp .env.example .env
```

### 2. Fill in your configuration

```env
#  Target company Trustpilot page
TARGET_URL=https://www.trustpilot.com/review/example.com

#  Your Trustpilot login email
USER_EMAIL=your_email@example.com

#  Scraping range
START_PAGE=1
END_PAGE=5

#  Browser mode
# True = headless (no browser UI)
# False = visible browser (recommended for debugging)
HEADLESS=False

#  Optional: Force Chrome version (only if mismatch error occurs)
# Example: CHROME_VERSION=146
# CHROME_VERSION=
```

###  Notes

* Never share your `.env` file publicly
* Ensure `.env` is listed in your `.gitignore`
* Adjust page range based on your scraping needs
* Use `HEADLESS=False` if you face login or detection issues

---

##  Usage

Run the scraper:

```bash
python trustpilot_scraper.py
```

###  Login Process

1. Chrome will open automatically
2. Your email will be entered
3. Check your inbox for the OTP code
4. Enter the code in the terminal

###  Data Collection

* The bot navigates through pages automatically
* Extracts reviews (date, rating, title, body)
* Saves results into a `.csv` file in the project folder

---

##  Troubleshooting

###  ChromeDriver Version Error

**Error:** `SessionNotCreatedException`

**Fix:**

* Check your Chrome version (Settings → About Chrome)
* Set the version in your `.env`:

```env
CHROME_VERSION=146
```

---

###  Connection Error

**Error:** `getaddrinfo failed` / `[Errno 11001]`

**Fix:**

* Check your internet connection
* Disable VPN or firewall if blocking Python

---

##  Legal Disclaimer

This tool is for educational purposes only.
Web scraping may violate Trustpilot's Terms of Service.

Use responsibly:

* Respect robots.txt
* Avoid aggressive scraping
* Follow applicable laws and platform rules

The author is not responsible for misuse.

---

##  License

This project is licensed under the **MIT License**.

---
