from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime
import json
import os
import sys

def load_reported_threads():
    reported_file = "reported_threads.json"
    if os.path.exists(reported_file):
        with open(reported_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_reported_threads(reported_threads):
    reported_file = "reported_threads.json"
    with open(reported_file, 'w', encoding='utf-8') as f:
        json.dump(reported_threads, f, ensure_ascii=False, indent=2)

def check_earthquake_threads():
    earthquake_keywords = [
        'galatasaray', 'deprem', 'zelzele', 'sarsıntı', 'earthquake', 
        'kandilli', 'afad', 'richter', 'büyüklüğünde deprem'
    ]
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--lang=tr-TR')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    
    try:
        print(f"\n{'='*80}")
        print(f"Starting check at: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        print("Starting Chrome browser...")
        
        if sys.platform.startswith('win'):
            chrome_binary = r"D:\Chrome\Application\chrome.exe"
            if os.path.exists(chrome_binary):
                chrome_options.binary_location = chrome_binary
        
        driver = webdriver.Chrome(options=chrome_options)
        
        print("Loading Ekşi Sözlük main page...")
        driver.get("https://eksisozluk.com")
        
        time.sleep(5)
        
        print("Searching for gündem topics...")
        
        try:
            gundem_section = driver.find_element(By.CSS_SELECTOR, "ul.topic-list.partial")
            topics = gundem_section.find_elements(By.TAG_NAME, "a")
            print(f"Found {len(topics)} topics in gündem section")
        except:
            try:
                topics = driver.find_elements(By.CSS_SELECTOR, "ul.topic-list a")
                print(f"Found {len(topics)} topics in topic-list")
            except:
                topics = driver.find_elements(By.CSS_SELECTOR, "a[href*='--']")
                print(f"Found {len(topics)} topic links on page")
        
        earthquake_threads = []
        
        for topic in topics:
            try:
                topic_text = topic.text.strip().lower()
                topic_url = topic.get_attribute('href')
                
                for keyword in earthquake_keywords:
                    if keyword in topic_text:
                        earthquake_threads.append({
                            'title': topic.text.strip(),
                            'url': topic_url
                        })
                        break
            except:
                continue
        
        if earthquake_threads:
            print(f"\n⚠️  ALERT: Found {len(earthquake_threads)} earthquake-related thread(s)!\n")
            
            reported_threads = load_reported_threads()
            new_threads = []
            
            for thread in earthquake_threads:
                if thread['url'] not in reported_threads:
                    new_threads.append(thread)
                    reported_threads.append(thread['url'])
            
            if new_threads:
                print(f"Found {len(new_threads)} NEW thread(s) (not reported before):\n")
                
                for i, thread in enumerate(new_threads, 1):
                    print(f"{i}. {thread['title']}")
                    print(f"   {thread['url']}")
                
                today = datetime.now().strftime("%d.%m.%Y")
                current_time = datetime.now().strftime("%H:%M:%S")
                filename = f"earthquake_alert_{today.replace('.', '_')}_{current_time.replace(':', '_')}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"⚠️  EARTHQUAKE ALERT ⚠️\n")
                    f.write(f"Date: {today}\n")
                    f.write(f"Time: {current_time}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for i, thread in enumerate(new_threads, 1):
                        f.write(f"{i}. {thread['title']} entries\n")
                        f.write(f"   {thread['url']}\n\n")
                
                print(f"\n✓ Alert saved to: {filename}")
                
                save_reported_threads(reported_threads)
                print(f"✓ Updated reported threads list")
                
                return True
            else:
                print("All earthquake threads were already reported. No new alert file created.")
                return False
            
        else:
            print("✓ No earthquake-related threads found. All clear.")
            return False
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

def run_continuous():
    check_interval_minutes = 10
    check_interval_seconds = check_interval_minutes * 60
    
    print("="*80)
    print("AUTOMATIC EARTHQUAKE CHECKER")
    print(f"Checking Ekşi Sözlük every {check_interval_minutes} minutes")
    print("Press Ctrl+C to stop")
    print("="*80)
    
    while True:
        try:
            check_earthquake_threads()
            
            next_check = datetime.now().timestamp() + check_interval_seconds
            next_check_time = datetime.fromtimestamp(next_check).strftime('%d.%m.%Y %H:%M:%S')
            
            print(f"\n{'='*80}")
            print(f"Next check scheduled for: {next_check_time}")
            print(f"Waiting {check_interval_minutes} minutes...")
            print(f"{'='*80}\n")
            
            time.sleep(check_interval_seconds)
            
        except KeyboardInterrupt:
            print("\n\nStopping automatic checker...")
            break
        except Exception as e:
            print(f"\nError in automatic checker: {e}")
            print("Waiting 2 minutes before retry...")
            time.sleep(120)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        run_continuous()
    else:
        check_earthquake_threads()