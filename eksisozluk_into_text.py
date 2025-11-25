from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import sys
import time
import os
from collections import Counter

os.environ['WDM_LOG'] = '0'

def clean_word(word):
    word = word.lower()
    word = re.sub(r'[^\w\sığüşöçâîû]', '', word)
    return word.strip()

def scrape_eksisozluk_thread(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
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
    all_entries_data = []
    
    try:
        print("Starting browser...")
        
        chrome_options.binary_location = r"D:\Chrome\Application\chrome.exe"
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        print(f"Loading page: {url}")
        driver.get(url)
        
        time.sleep(2)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-id]"))
        )
        
        try:
            title_elem = driver.find_element(By.ID, "title")
            topic_title = title_elem.text.strip()
        except:
            topic_title = "unknown_topic"
        
        print(f"Topic: {topic_title}")
        
        page_num = 1
        
        while True:
            print(f"\n--- Processing Page {page_num} ---")
            
            time.sleep(1)
            
            entries = driver.find_elements(By.CSS_SELECTOR, "li[data-id]")
            
            if not entries:
                print("No entries found on this page.")
                break
            
            print(f"Found {len(entries)} entries on page {page_num}")
            
            for i, entry in enumerate(entries, 1):
                try:
                    entry_id = entry.get_attribute('data-id')
                    
                    if any(e['id'] == entry_id for e in all_entries_data):
                        continue
                    
                    try:
                        content_div = entry.find_element(By.CLASS_NAME, 'content')
                        content = content_div.text.strip()
                    except:
                        content = "No content found"
                    
                    try:
                        author_elem = entry.find_element(By.CLASS_NAME, 'entry-author')
                        author = author_elem.text.strip()
                    except:
                        author = "Unknown"
                    
                    try:
                        date_elem = entry.find_element(By.CLASS_NAME, 'entry-date')
                        date = date_elem.text.strip()
                    except:
                        date = "Unknown date"
                    
                    all_entries_data.append({
                        'id': entry_id,
                        'author': author,
                        'date': date,
                        'content': content
                    })
                    
                    print(f"  Extracted entry {len(all_entries_data)} (ID: {entry_id})")
                    
                except Exception as e:
                    print(f"  Error processing entry: {e}")
                    continue
            
            try:
                pager = driver.find_element(By.CLASS_NAME, "pager")
                page_links = pager.find_elements(By.TAG_NAME, "a")
                
                page_num += 1
                
                if '?' in url:
                    next_url = f"{url}&p={page_num}"
                else:
                    next_url = f"{url}?p={page_num}"
                
                print(f"Navigating to page {page_num}...")
                driver.get(next_url)
                
                time.sleep(1)
                
                try:
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-id]"))
                    )
                except:
                    print(f"\nNo entries found on page {page_num}. Reached the end.")
                    break
                
            except Exception as e:
                print(f"\nNo more pages found. Finished scraping.")
                break
        
        if not all_entries_data:
            print("\nNo entries were collected!")
            return
        
        print("\nWhat would you like to save?")
        print("1. Entries only (txt)")
        print("2. Word count only (txt)")
        print("3. Both")
        
        choice = input("\nEnter your choice (1/2/3): ").strip()
        
        filename_base = re.sub(r'[^\w\s-]', '', topic_title).strip().replace(' ', '_')
        
        if choice in ['1', '3']:
            filename = f"{filename_base}_entries.txt"
            
            print(f"\nWriting {len(all_entries_data)} entries to file...")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Topic: {topic_title}\n")
                f.write(f"URL: {url}\n")
                f.write(f"Total entries: {len(all_entries_data)}\n")
                f.write(f"Total pages scraped: {page_num}\n")
                f.write("=" * 80 + "\n\n")
                
                for entry_data in all_entries_data:
                    f.write(f"Entry ID: {entry_data['id']}\n")
                    f.write(f"Author: {entry_data['author']}\n")
                    f.write(f"Date: {entry_data['date']}\n")
                    f.write(f"Content:\n{entry_data['content']}\n")
                    f.write("-" * 80 + "\n\n")
            
            print(f"✓ Entries saved to: {filename}")
        
        if choice in ['2', '3']:
            print("\nCounting words...")
            all_words = []
            
            for entry_data in all_entries_data:
                content = entry_data['content']
                words = content.split()
                for word in words:
                    cleaned = clean_word(word)
                    if len(cleaned) > 2:
                        all_words.append(cleaned)
            
            word_counts = Counter(all_words)
            sorted_words = word_counts.most_common()
            
            filename_count = f"{filename_base}_word_count.txt"
            
            with open(filename_count, 'w', encoding='utf-8') as f:
                f.write(f"Word Count for: {topic_title}\n")
                f.write(f"Total unique words: {len(sorted_words)}\n")
                f.write(f"Total words counted: {len(all_words)}\n")
                f.write("=" * 80 + "\n\n")
                
                for word, count in sorted_words:
                    f.write(f"{word} {count}\n")
            
            print(f"✓ Word count saved to: {filename_count}")
            print(f"✓ Total unique words: {len(sorted_words)}")
        
        print(f"\n✓ Successfully scraped {len(all_entries_data)} entries from {page_num} pages!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter the Ekşi Sözlük thread URL: ")
    
    scrape_eksisozluk_thread(url)