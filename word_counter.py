import string
import logging
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        logging.info(f"Successfully fetched text from {url}")
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching the text: {e}")
        return None

# Function to remove punctuation
def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))

def map_function(word):
    return word, 1

def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)

# Execute MapReduce
def map_reduce(text, search_words=None):
    logging.info("Starting MapReduce process")

    # Remove punctuation
    text = remove_punctuation(text)
    words = text.split()
    logging.info(f"Total words to process: {len(words)}")

    # If a list of search words is given, consider only those words
    if search_words:
        words = [word for word in words if word in search_words]
        logging.info(f"Filtered words to search: {search_words}")

    # Parallel Mapping
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    logging.info(f"Mapping completed with {len(mapped_values)} mapped values")

    # Shuffling
    shuffled_values = shuffle_function(mapped_values)
    logging.info("Shuffling completed")

    # Parallel Reduction
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    logging.info("Reduction completed")
    return dict(reduced_values)

# Function to visualize top words
def visualize_top_words(counter, top_n=10):
    most_common = sorted(counter.items(), key=lambda item: item[1], reverse=True)[:top_n]
    words, frequencies = zip(*most_common)
    
    plt.figure(figsize=(10, 5))
    plt.bar(words, frequencies, color='blue')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title(f'Top {top_n} Words by Frequency')
    plt.xticks(rotation=45)
    plt.show()
    logging.info(f"Visualized top {top_n} words")

if __name__ == '__main__':
    # URL of a text file from Project Gutenberg
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"  # Example: War and Peace by Leo Tolstoy
    text = get_text(url)
    if text:
        # Perform MapReduce on the input text
        result = map_reduce(text)
        
        # Visualize top 10 words
        visualize_top_words(result, top_n=10)
    else:
        logging.error("Error: Failed to retrieve the input text.")
