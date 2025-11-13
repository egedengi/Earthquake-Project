from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime

os.environ['WDM_LOG'] = '0'

def check_earthquake_threads():
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--lang=tr-TR')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    earthquake_keywords = [
        'depremi', 'deprem', 'sarsıntı', 
        'kandilli', 'afad', 'büyüklüğünde'
    ]
    
    try:
        print("Starting browser...")

        chrome_options.binary_location = r"D:\Chrome\Application\chrome.exe"

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        print("Loading Ekşi Sözlük main page...")
        driver.get("https://eksisozluk.com")
        
        time.sleep(3)
        
        print("\nSearching for gündem topics...\n")
        
        try:
            gundem_section = driver.find_element(By.CSS_SELECTOR, "ul.topic-list.partial")
            topics = gundem_section.find_elements(By.TAG_NAME, "a")
            print(f"Found {len(topics)} topics in gündem section")
        except Exception as e:
            print(f"Could not locate gündem section: {e}")
            topics = []
        
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
        
        today = datetime.now().strftime("%d.%m.%Y")
        
        if earthquake_threads:
            print(f"✓ FOUND {len(earthquake_threads)} earthquake-related thread(s):\n")
            print("=" * 80)
            
            for i, thread in enumerate(earthquake_threads, 1):
                print(f"\n{i}. {thread['title']}")
                print(f"   URL: {thread['url']}")
            
            print("\n" + "=" * 80)
            print(f"\n⚠️  Possible earthquake detected today ({today})")
            
            save_dir = r"D:\Python Projects D"
            os.makedirs(save_dir, exist_ok=True)  # make sure the folder exists
            output_path = os.path.join(save_dir, f"earthquake_threads_{today.replace('.', '_')}.txt")


            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Earthquake-related threads found on Ekşi Sözlük\n")
                f.write(f"Date: {today}\n")
                f.write(f"Time: {datetime.now().strftime('%H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, thread in enumerate(earthquake_threads, 1):
                    f.write(f"{i}. {thread['title']} entries\n")
                    f.write(f"   {thread['url']}\n\n")
            
            print(f"\n✓ Results saved to: earthquake_threads_{today.replace('.', '_')}.txt")
            
        else:
            print("✓ No earthquake-related threads found on the main page.")
            print(f"✓ All clear for today ({today})")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()

if __name__ == "__main__":
    check_earthquake_threads()