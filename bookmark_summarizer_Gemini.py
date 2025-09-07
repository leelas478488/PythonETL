# bookmark_summarizer_Gemini.py

import os
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from langdetect import detect
import threading
import re

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
BOOKMARKS_PATH = r'C:\Users\91888\AppData\Local\Google\Chrome\User Data\Default\Bookmarks'
#BOOKMARKS_PATH = os.path.expanduser('~C:\Users\91888\AppData\Local\Google\Chrome\User')
# For Windows: os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks')
# For Linux: os.path.expanduser('~/.config/google-chrome/Default/Bookmarks')
#For MAC: os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Bookmarks')  # macOS example

# Check if the platform is Windows, macOS, or Linux
if os.name == 'nt':  # Windows
    BOOKMARKS_PATH = os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks')
elif os.uname()[0] == 'Darwin':  # macOS
    BOOKMARKS_PATH = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Bookmarks')
elif os.uname()[0] == 'Linux':  # Linux
    BOOKMARKS_PATH = os.path.expanduser('~/.config/google-chrome/Default/Bookmarks')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    messagebox.showerror("API Key Error", "OPENAI_API_KEY not found. Please create a .env file.")


# --- Bookmark Parsing Functions ---
def parse_bookmarks_recursive(json_data):
    """Recursively parses a Chrome bookmarks JSON object to find all bookmarks."""
    bookmarks = []
    if isinstance(json_data, dict):
        if json_data.get("type") == "url":
            bookmarks.append({
                "name": json_data.get("name"),
                "url": json_data.get("url")
            })
        if "children" in json_data:
            for child in json_data["children"]:
                bookmarks.extend(parse_bookmarks_recursive(child))
    return bookmarks


# bookmark_summarizer_Gemini.py

# ... (rest of the code)

def load_and_search_bookmarks(keyword):
    """
    Loads bookmarks from the JSON file and searches for a keyword.

    Args:
        keyword (str): The search term.

    Returns:
        list: A list of matching bookmarks.
    """
    # Initialize all_bookmarks with an empty list
    all_bookmarks = []

    try:
        with open(BOOKMARKS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_bookmarks = parse_bookmarks_recursive(data.get("roots"))

    except FileNotFoundError:
        messagebox.showerror("Error", f"Bookmarks file not found at: {BOOKMARKS_PATH}")
        return []
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while parsing bookmarks: {e}")
        return []

    matches = []
    for bookmark in all_bookmarks:
        name = bookmark['name']
        url = bookmark['url']

        # Case-insensitive search on title and URL
        if keyword.lower() in name.lower() or keyword.lower() in url.lower():
            matches.append(bookmark)

    return matches



# --- Content Fetching & Summarization Functions ---
def fetch_web_content(url):
    """
    Fetches the main textual content from a URL.

    Args:
        url (str): The URL to fetch.

    Returns:
        tuple: (content_text, status_code). Content is a string, or None if error.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Heuristic to find main content
        main_content = soup.find('main') or soup.find('article') or soup.find(id='content')
        if not main_content:
            text = soup.get_text()
        else:
            text = main_content.get_text()

        # Clean up text: remove multiple newlines and extra spaces
        clean_text = re.sub(r'\s+', ' ', text).strip()

        # Heuristic for unsuitable pages (too short)
        if len(clean_text.split()) < 100:
            return None, response.status_code

        # Check for non-English and translate if needed
        try:
            if detect(clean_text) != 'en':
                # Simplified translation fallback (would need a translation API for production)
                return "The content is not in English and could not be automatically translated.", response.status_code
        except:
            pass  # Ignore language detection errors

        return clean_text, response.status_code

    except requests.exceptions.RequestException as e:
        return None, str(e)


def summarize_with_ai(text):
    """
    Summarizes a given text using OpenAI's GPT-3.5-turbo model.

    Args:
        text (str): The text to summarize.

    Returns:
        str: A bullet-point summary or an error message.
    """
    if not OPENAI_API_KEY:
        return "AI summarization unavailable. No API key found."

    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        prompt = f"""
        Summarize the following text in 3 to 5 concise bullet points. The summary should be in plain English.

        Text:
        {text[:4000]} # Truncate to avoid API token limits
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes web content."},
                {"role": "user", "content": prompt}
            ]
        )

        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return f"Could not generate summary: {e}"


# --- User Interface (Tkinter) ---
class BookmarkSummarizerApp(tk.Tk):
    """Main application window for the bookmark summarizer."""

    def __init__(self):
        super().__init__()
        self.title("AI Bookmark Summarizer")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        """Builds the UI components."""

        # Search Frame
        search_frame = tk.Frame(self, pady=10)
        search_frame.pack(fill='x')

        tk.Label(search_frame, text="Enter keyword:").pack(side='left', padx=(10, 5))

        self.keyword_entry = tk.Entry(search_frame, width=50)
        self.keyword_entry.pack(side='left', padx=(0, 10), expand=True, fill='x')

        search_button = tk.Button(search_frame, text="Search & Summarize", command=self.start_search)
        search_button.pack(side='left', padx=(0, 10))

        # Results Frame
        results_frame = tk.Frame(self)
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, state='disabled')
        self.results_text.pack(fill='both', expand=True)

    def start_search(self):
        """Starts the search process in a new thread to keep the UI responsive."""
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Input Error", "Please enter a search keyword.")
            return

        # Clear previous results and show loading message
        self.results_text.config(state='normal')
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, "Searching and summarizing... this may take a moment.\n")
        self.results_text.config(state='disabled')
        self.update_idletasks()

        # Start a new thread for the main task
        search_thread = threading.Thread(target=self.run_search, args=(keyword,))
        search_thread.start()

    def run_search(self, keyword):
        """Performs the main search, content fetching, and summarization."""
        matches = load_and_search_bookmarks(keyword)

        self.results_text.config(state='normal')
        self.results_text.delete('1.0', tk.END)

        if not matches:
            self.results_text.insert(tk.END, "No matching bookmarks found.\n")
        else:
            for bookmark in matches:
                self.results_text.insert(tk.END, f"• {bookmark['name']}\n")
                self.results_text.insert(tk.END, f"  URL: {bookmark['url']}\n", 'link')

                content, status = fetch_web_content(bookmark['url'])

                if content:
                    summary = summarize_with_ai(content)
                    self.results_text.insert(tk.END, f"  Summary:\n  {summary}\n\n")
                else:
                    self.results_text.insert(tk.END,
                                             f"  Note: Could not fetch content or page is unsuitable. Status: {status}\n\n")

                self.results_text.update_idletasks()  # Refresh UI during long loop

        self.results_text.config(state='disabled')


# --- Main Execution ---
if __name__ == "__main__":
    app = BookmarkSummarizerApp()
    app.mainloop()