import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import json
import requests
from bs4 import BeautifulSoup
import nltk
nltk.download('punkt_tab')  # ✅ This is the correct one

import nltk
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# Sumy for summarization
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def summarize_text(text, sentence_count=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary)

def load_bookmarks(file_path):
    bookmarks = []

    if file_path.endswith('.html'):
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            for link in soup.find_all('a'):
                bookmarks.append({
                    'title': link.get_text(),
                    'url': link.get('href')
                })
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            def extract_json_bookmarks(node):
                if isinstance(node, dict):
                    if node.get("type") == "url":
                        bookmarks.append({
                            'title': node.get("name", ""),
                            'url': node.get("url", "")
                        })
                    for child in node.get("children", []):
                        extract_json_bookmarks(child)
                elif isinstance(node, list):
                    for item in node:
                        extract_json_bookmarks(item)

            extract_json_bookmarks(data.get("roots", {}))

    return bookmarks

def fetch_and_summarize(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = " ".join(p.get_text() for p in paragraphs if len(p.get_text()) > 30)

        if len(text) < 100:
            return "⚠️ Page contains mostly diagrams or very little text.", False

        summary = summarize_text(text[:2000])
        return summary, True
    except Exception as e:
        return f"❌ Failed to fetch or summarize content: {str(e)}", False

def search_bookmarks(bookmarks, keyword):
    results = []
    for bookmark in bookmarks:
        if keyword.lower() in bookmark['title'].lower() or keyword.lower() in bookmark['url'].lower():
            summary, summarizable = fetch_and_summarize(bookmark['url'])
            results.append((bookmark['title'], bookmark['url'], summary, summarizable))
    return results

# Tkinter UI
class BookmarkSummarizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bookmark Summarizer (Offline - Sumy)")
        self.bookmarks = []

        # File upload button
        self.upload_btn = tk.Button(root, text="Upload Bookmark File (HTML or JSON)", command=self.upload_file)
        self.upload_btn.pack(pady=10)

        # Keyword search
        self.keyword_label = tk.Label(root, text="Enter keyword to search:")
        self.keyword_label.pack()
        self.keyword_entry = tk.Entry(root, width=40)
        self.keyword_entry.pack(pady=5)

        self.search_btn = tk.Button(root, text="Search and Summarize", command=self.search_and_display)
        self.search_btn.pack(pady=10)

        # Result area
        self.result_area = scrolledtext.ScrolledText(root, width=100, height=30, wrap=tk.WORD)
        self.result_area.pack(pady=10)

    def upload_file(self):
        file_path = filedialog.askopenfilename(title="Select Bookmarks File", filetypes=[("HTML or JSON", "*.html *.json *")])
        if file_path:
            try:
                self.bookmarks = load_bookmarks(file_path)
                messagebox.showinfo("Success", f"Loaded {len(self.bookmarks)} bookmarks.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load bookmarks: {str(e)}")

    def search_and_display(self):
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Missing Input", "Please enter a keyword to search.")
            return
        if not self.bookmarks:
            messagebox.showwarning("Missing File", "Please upload a bookmarks file first.")
            return

        self.result_area.delete(1.0, tk.END)
        results = search_bookmarks(self.bookmarks, keyword)

        if not results:
            self.result_area.insert(tk.END, "No bookmarks found for the given keyword.\n")
        else:
            for title, url, summary, summarizable in results:
                self.result_area.insert(tk.END, f"🔗 {title}\n{url}\n")
                if summarizable:
                    self.result_area.insert(tk.END, f"📝 Summary:\n{summary}\n")
                else:
                    self.result_area.insert(tk.END, f"🖼️ Info:\n{summary}\n")
                self.result_area.insert(tk.END, "-" * 80 + "\n")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = BookmarkSummarizerApp(root)
    root.mainloop()
