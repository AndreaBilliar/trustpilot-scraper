"""
Trustpilot Review Scraper
Description: Automated script using Selenium and undetected_chromedriver to extract
Trustpilot reviews in authenticated mode.
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys  
import pandas as pd
import time
import random
import re
import os
from dotenv import load_dotenv

def clean_text(text):
    """Cleans review text by removing useless metadata and UI strings."""
    if not isinstance(text, str): 
        return ""
    
    # Remove common UI strings found on French/English Trustpilot versions
    text = text.replace("Voir plus", "").replace("See more", "")
    text = text.replace("Date de l'expérience :", "").replace("Date of experience:", "")
    
    # Handle specific formatting cases found in previous versions
    if "|" in text and len(text) < 500:
        parts = text.split("|")
        text = max(parts, key=len).strip()
        
    return text.strip()

def collect_trustpilot_reviews(target_url, user_email, start_page=1, end_page=10, headless_mode=False):
    """
    Main function to initialize the driver, log in, and scrape reviews.
    """
    print("--- Starting Collection (Authenticated Mode) ---")
    
    options = uc.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2 # Disable images for speed
    }
    options.add_experimental_option("prefs", prefs)
    
    try:
        # Check if the user forced a specific Chrome version via .env
        forced_version = os.getenv("CHROME_VERSION")
        
        # Dynamic browser argument configuration
        driver_kwargs = {
            "options": options,
            "use_subprocess": True,
            "headless": headless_mode
        }
        
        if forced_version:
            print(f"-> Starting with forced Chrome version: {forced_version}")
            driver_kwargs["version_main"] = int(forced_version)
        else:
            print("-> Starting with automatic version detection...")
            
        if headless_mode:
            print("-> Headless mode (background) enabled.")
            
        driver = uc.Chrome(**driver_kwargs)
            
    except Exception as e:
        print(f"Driver initialization error: {e}")
        print("\nTip: If the error mentions a wrong ChromeDriver version,")
        print("add 'CHROME_VERSION=XXX' to your .env file with your current major version.")
        return

    reviews_list = []
    
    try:
        print("\n--- Login Stage ---")
        driver.get("https://trustpilot.com/users/connect")
        wait = WebDriverWait(driver, 15)
        
        # 1. Handle cookies (Reject all)
        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
            cookie_button.click()
            print("-> Cookies rejected successfully.")
            time.sleep(1)
        except Exception:
            pass # No cookie banner detected

        try:
            # 2. Click initial login/continue button
            try:
                login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div/main/div/div/div[1]/div/div/div/button')))
                login_button.click()
                time.sleep(1)
            except Exception:
                pass # Button might not be present

            # 3. Enter email
            print(f"Attempting login with: {user_email}")
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#email-lookup")))
            email_input.clear()
            email_input.send_keys(user_email)
            time.sleep(1)
            email_input.send_keys(Keys.ENTER)
            
            # 4. Enter verification code (OTP)
            print("\nA verification code has been sent to your email address.")
            verification_code = input(">>> Please enter the code here: ")
            
            code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#verification-code-input")))
            code_input.clear()
            code_input.send_keys(verification_code)
            
            print("-> Waiting for redirection...")
            time.sleep(5) 
            
        except Exception:
            if headless_mode:
                print("Automatic login failed. Headless mode prevents manual login. Stopping script.")
                return
            else:
                print("Automatic login failed. Please log in manually in the Chrome window.")
                input(">>> Press ENTER here once logged in to continue...")

        print(f"\n--- Scraping URL: {target_url} ---")

        for page_num in range(start_page, end_page + 1):
            url_page = f"{target_url}?page={page_num}&sort=recency"
            print(f"\n>>> Processing Page {page_num}")
            driver.get(url_page)
            
            # Anti-bot measure: Random wait time
            wait_time = random.uniform(2, 5)
            time.sleep(wait_time)
            
            # Find all review articles on the page
            articles = driver.find_elements(By.TAG_NAME, "article")
            
            if len(articles) == 0:
                print("    Warning: Empty page. Attempting refresh...")
                driver.refresh()
                time.sleep(5)
                articles = driver.find_elements(By.TAG_NAME, "article")
                if len(articles) == 0:
                    print("    Stop: No more reviews found.")
                    break

            for article in articles:
                try:
                    # Scrape Title
                    title = "Not specified"
                    try:
                        title = article.find_element(By.CSS_SELECTOR, "h2[data-service-review-title-typography='true']").text.strip()
                    except:
                        pass

                    # Scrape Comment/Body
                    comment = ""
                    try:
                        comment = article.find_element(By.CSS_SELECTOR, "p[data-service-review-text-typography='true']").text.strip()
                    except:
                        try:
                            # Fallback method if standard selector fails
                            raw_text = article.text.replace("\n", " | ")
                            comment = clean_text(raw_text)
                        except:
                            pass

                    # Scrape Rating
                    rating = 0
                    try:
                        img = article.find_element(By.CSS_SELECTOR, "img[alt*='ur 5'], img[alt*='toiles'], img[alt*='ut of 5']")
                        rating = int(re.search(r'(\d)', img.get_attribute("alt")).group(1))
                    except:
                        pass
                    
                    # Scrape Date
                    date = "Unknown"
                    try:
                        date = article.find_element(By.TAG_NAME, "time").get_attribute("datetime").split('T')[0]
                    except:
                        pass

                    # Only add if we have minimal data
                    if comment or rating > 0:
                        reviews_list.append({
                            "Date": date, 
                            "Rating": rating, 
                            "Title": title, 
                            "Comment": comment
                        })
                except:
                    continue # Skip problematic individual reviews
            
            print(f"    -> {len(articles)} reviews analyzed. Security pause...")

    except Exception as e:
        print(f"Critical error during execution: {e}")
    finally:
        # Ensure browser closes even if errors occur
        driver.quit()
        
    # Save data to CSV if any reviews were found
    if reviews_list:
        df = pd.DataFrame(reviews_list)
        df.drop_duplicates(inplace=True)
        
        # Generate filename based on URL
        company_name = target_url.split("www.")[-1].split(".")[0] if "www." in target_url else "export"
        filename = f"{company_name}_reviews_p{start_page}_to_{end_page}.csv"
        
        # Save using Excel-friendly formatting (UTF-8 with BOM, semicolon separator)
        df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')
        print(f"\nSuccess! {len(df)} reviews saved in '{filename}'.")
    else:
        print("\nNo data could be retrieved.")

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Retrieve configuration
    TARGET_URL = os.getenv("TARGET_URL")
    USER_EMAIL = os.getenv("USER_EMAIL")
    START_PAGE = int(os.getenv("START_PAGE", 1))
    END_PAGE = int(os.getenv("END_PAGE", 10))
    # Parse HEADLESS boolean (accepts "True", "true", "1")
    IS_HEADLESS = os.getenv("HEADLESS", "False").lower() in ("true", "1", "t")
    
    # Validate required fields
    if not TARGET_URL or not USER_EMAIL:
        print("Error: .env file missing or incomplete. Please copy .env.example to .env and fill in details.")
        exit(1)
        
    # Run the scraper
    collect_trustpilot_reviews(TARGET_URL, USER_EMAIL, start_page=START_PAGE, end_page=END_PAGE, headless_mode=IS_HEADLESS)