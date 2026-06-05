from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import re
import sys
import time
import os


def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--lang=tr-TR')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    if sys.platform.startswith('win'):
        win_chrome = r"D:\Chrome\Application\chrome.exe"
        if os.path.exists(win_chrome):
            chrome_options.binary_location = win_chrome
        from webdriver_manager.chrome import ChromeDriverManager
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    else:
        driver = webdriver.Chrome(options=chrome_options)

    return driver


def scrape_thread(url):
    driver = None
    all_entries = []
    topic_title = "unknown_topic"

    try:
        print(f"Starting browser...")
        driver = get_chrome_driver()

        print(f"Loading: {url}")
        driver.get(url)
        time.sleep(2)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-id]"))
        )

        try:
            topic_title = driver.find_element(By.ID, "title").text.strip()
        except:
            pass

        print(f"Topic: {topic_title}")

        page_num = 1

        while True:
            print(f"Processing page {page_num}...")
            time.sleep(1)

            entries = driver.find_elements(By.CSS_SELECTOR, "li[data-id]")
            if not entries:
                break

            print(f"  Found {len(entries)} entries on page {page_num}")

            for entry in entries:
                try:
                    entry_id = entry.get_attribute('data-id')

                    if any(e['id'] == entry_id for e in all_entries):
                        continue

                    try:
                        content = entry.find_element(By.CLASS_NAME, 'content').text.strip()
                    except:
                        content = ""

                    try:
                        author = entry.find_element(By.CLASS_NAME, 'entry-author').text.strip()
                    except:
                        author = "unknown"

                    try:
                        date = entry.find_element(By.CLASS_NAME, 'entry-date').text.strip()
                    except:
                        date = ""

                    if content:
                        all_entries.append({
                            'id': entry_id,
                            'author': author,
                            'date': date,
                            'content': content
                        })

                except:
                    continue

            try:
                driver.find_element(By.CLASS_NAME, "pager")
                page_num += 1
                next_url = f"{url}{'&' if '?' in url else '?'}p={page_num}"
                driver.get(next_url)
                time.sleep(1)

                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-id]"))
                    )
                except:
                    break

            except:
                break

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if driver:
            driver.quit()

    return all_entries, topic_title


def save_entries(entries, topic_title, url):
    safe_title = re.sub(r'[^\w\s-]', '', topic_title).strip().replace(' ', '_')
    filename = f"{safe_title}_entries.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Topic: {topic_title}\n")
        f.write(f"URL: {url}\n")
        f.write(f"Total entries: {len(entries)}\n")
        f.write("=" * 80 + "\n\n")

        for entry in entries:
            f.write(f"Entry ID: {entry['id']}\n")
            f.write(f"Author: {entry['author']}\n")
            f.write(f"Date: {entry['date']}\n")
            f.write(f"Content:\n{entry['content']}\n")
            f.write("-" * 80 + "\n\n")

    print(f"Saved {len(entries)} entries to: {filename}")
    return filename


def main():
    if len(sys.argv) < 2:
        print("Usage: python eksisozluk_into_text.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    entries, topic_title = scrape_thread(url)

    if not entries:
        print("No entries found.")
        sys.exit(1)

    save_entries(entries, topic_title, url)


if __name__ == "__main__":
    main()