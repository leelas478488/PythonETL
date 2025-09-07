import os
import json
import shutil
import tempfile
import requests
from bs4 import BeautifulSoup
from tkinter import Tk, simpledialog, scrolledtext, messagebox, Button, END
from dotenv import load_dotenv
import threading
import time

# Hugging Face pipeline (fallback if OpenAI quota fails)
from transformers import pipeline

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Hugging Face summarizer
hf_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Chrome Bookmarks path
BOOKMARKS_PATH = os.path.expanduser(
    r"C:\Users\91888\AppData\Local\Google\Chrome\User Data\Default\Bookmarks"
)

# -------------------------------
# Load Chrome bookmarks
# -------------------------------
def load_chrome_bookmarks():
    if not os.path.exists(BOOKMARKS_PATH):
        messagebox.showerror("Error", f"Bookmarks file not found at {BOOKMARKS_PATH}")
        return None
    try:
        temp_file = os.path.join(tempfile.gettempdir(), "Bookmarks_copy.json")
        shutil.copy2(BOOKMARKS_PATH, temp_file)
        with open(temp_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load bookmarks: {e}")
        return None

# -------------------------------
# Fetch webpage content
# -------------------------------
def fetch_page_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text_content = " ".join(p.get_text() for p in paragraphs if p.get_text())
        return text_content.strip()
    except Exception:
        return ""

# -------------------------------
# Summarization with OpenAI or HF
# -------------------------------
def ai_summarize(text, keyword):
    text = text[:4000]  # limit size
    summary_text = ""

    # Try OpenAI first
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that summarizes text in 3-5 concise bullet points.",
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this text focusing on '{keyword}':\n\n{text}",
                    },
                ],
                max_tokens=300,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ OpenAI failed, falling back to Hugging Face: {e}")

    # Always try Hugging Face if OpenAI fails or quota exceeded
    try:
        hf_summary = hf_summarizer(text, max_length=150, min_length=50, do_sample=False)
        return hf_summary[0]["summary_text"]
    except Exception as e:
        return f"[Error summarizing with both OpenAI and Hugging Face: {e}]"

    return summary_text

# -------------------------------
# Extract bookmarks and search
# -------------------------------
def search_bookmarks(data, keyword):
    def extract_bookmarks(node):
        if isinstance(node, dict):
            if node.get("type") == "url":
                title = node.get("name", "")
                url = node.get("url", "")

                # Fetch page content for search
                page_content = fetch_page_content(url)

                if (
                    keyword.lower() in title.lower()
                    or keyword.lower() in url.lower()
                    or keyword.lower() in page_content.lower()
                ):
                    if page_content:
                        summary = ai_summarize(page_content, keyword)
                    else:
                        summary = "⚠️ Page has no readable text (diagram/video/etc)."

                    # Update results live
                    text_area.insert(END, f"🔗 {title}\n{url}\n")
                    text_area.insert(END, f"📝 Summary:\n{summary}\n\n")
                    text_area.insert(END, "-" * 100 + "\n")
                    text_area.see(END)  # auto-scroll
                    root.update_idletasks()

            for child in node.get("children", []):
                extract_bookmarks(child)
        elif isinstance(node, list):
            for item in node:
                extract_bookmarks(item)

    for root_node in data.get("roots", {}).values():
        extract_bookmarks(root_node)

# -------------------------------
# Run search in background thread
# -------------------------------
def on_search():
    keyword = simpledialog.askstring("Search", "Enter keyword to search in bookmarks:")
    if not keyword:
        return

    data = load_chrome_bookmarks()
    if not data:
        return

    text_area.delete(1.0, END)
    text_area.insert(END, f"🔄 Searching for '{keyword}'... please wait.\n\n")
    root.update_idletasks()

    def task():
        search_bookmarks(data, keyword)
        text_area.insert(END, "\n✅ Search complete!\n")

    threading.Thread(target=task).start()

# -------------------------------
# GUI Setup
# -------------------------------
root = Tk()
root.title("AI-Powered Chrome Bookmark Summarizer")
root.geometry("900x700")

search_button = Button(root, text="Search Bookmarks", command=on_search)
search_button.pack(pady=10)

text_area = scrolledtext.ScrolledText(root, wrap="word", font=("Arial", 10))
text_area.pack(expand=True, fill="both")

root.mainloop()
