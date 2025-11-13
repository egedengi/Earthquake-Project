import re
import sys
from collections import Counter

def clean_word(word):
    word = word.lower()
    word = re.sub(r'[^\w\sığüşöçâîû]', '', word)
    word = word.strip()
    
    if re.search(r'\d', word):
        return ''
    
    return word


def count_words_from_txt(filename):
    try:
        print(f"Reading file: {filename}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("Counting words...")
        
        all_words = []
        words = content.split()
        
        for word in words:
            cleaned = clean_word(word)
            if len(cleaned) > 2:
                all_words.append(cleaned)
        
        word_counts = Counter(all_words)
        sorted_words = word_counts.most_common()
        
        output_filename = filename.replace('.txt', '_word_count.txt')
        
        print(f"\nWriting word count to: {output_filename}")
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(f"Word Count from: {filename}\n")
            f.write(f"Total unique words: {len(sorted_words)}\n")
            f.write(f"Total words counted: {len(all_words)}\n")
            f.write("=" * 80 + "\n\n")
            
            for word, count in sorted_words:
                f.write(f"{word} {count}\n")
        
        print(f"✓ Word count saved to: {output_filename}")
        print(f"✓ Total unique words: {len(sorted_words)}")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Enter the text file name: ")
    
    count_words_from_txt(filename)