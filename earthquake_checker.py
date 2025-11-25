import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import json

def load_reported_threads():
    """Load list of already reported thread URLs"""
    reported_file = "reported_threads.json"
    if os.path.exists(reported_file):
        with open(reported_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_reported_threads(reported_threads):
    """Save list of reported thread URLs"""
    reported_file = "reported_threads.json"
    with open(reported_file, 'w', encoding='utf-8') as f:
        json.dump(reported_threads, f, ensure_ascii=False, indent=2)

def check_earthquake_threads():
    earthquake_keywords = [
        'deprem', 'zelzele', 'sarsıntı', 'earthquake', 
        'kandilli', 'afad', 'richter', 'büyüklüğünde deprem'
    ]
    
    try:
        print(f"\n{'='*80}")
        print(f"Starting check at: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        print("Fetching Ekşi Sözlük main page...")
        response = requests.get("https://eksisozluk.com", headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("Searching for gündem topics...")
        
        gundem_section = soup.find('ul', class_='topic-list')
        
        if not gundem_section:
            print("Could not find gündem section")
            return
        
        topics = gundem_section.find_all('a')
        print(f"Found {len(topics)} topics in gündem")
        
        earthquake_threads = []
        
        for topic in topics:
            try:
                topic_text = topic.get_text(strip=True).lower()
                topic_url = topic.get('href')
                
                if topic_url and not topic_url.startswith('http'):
                    topic_url = f"https://eksisozluk.com{topic_url}"
                
                for keyword in earthquake_keywords:
                    if keyword in topic_text:
                        earthquake_threads.append({
                            'title': topic.get_text(strip=True),
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
        
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

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