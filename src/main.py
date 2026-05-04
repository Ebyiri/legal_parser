import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import fitz
import re
import json

def extract_trilingual_json(pdf_path):
    doc = fitz.open(pdf_path)
    law_data = {
        "metadata": {"filename": os.path.basename(pdf_path)},
        "articles": []
    }
    
    full_text_rw = ""
    full_text_en = ""
    full_text_fr = ""

    for page in doc:
        w, h = page.rect.width, page.rect.height
        # Defining coordinate-based zones for each language
        rw_zone = fitz.Rect(0, 0, w*0.33, h)
        en_zone = fitz.Rect(w*0.33, 0, w*0.66, h)
        fr_zone = fitz.Rect(w*0.66, 0, w, h)
        
        full_text_rw += page.get_text("text", clip=rw_zone) + "\n"
        full_text_en += page.get_text("text", clip=en_zone) + "\n"
        full_text_fr += page.get_text("text", clip=fr_zone) + "\n"

    # Regex anchor to split by Articles
    pattern = r'(Article\s+(?:\d+|One|I|II|III|IV|V)|Ingingo\s+ya\s+\d+|Article\s+premier)'
    
    chunks_en = re.split(pattern, full_text_en)
    chunks_rw = re.split(pattern, full_text_rw)
    chunks_fr = re.split(pattern, full_text_fr)

    # Synchronizing the 3 languages into a hierarchy
    # We iterate through the English chunks and find corresponding translations
    for i in range(1, len(chunks_en), 2):
        title_en = chunks_en[i].strip().replace("Article One", "Article 1")
        content_en = chunks_en[i+1].strip() if i+1 < len(chunks_en) else ""
        
        # Simple index matching (Assuming columns are balanced)
        content_rw = chunks_rw[i+1].strip() if i+1 < len(chunks_rw) else "N/A"
        content_fr = chunks_fr[i+1].strip() if i+1 < len(chunks_fr) else "N/A"

        law_data["articles"].append({
            "article_id": title_en,
            "translations": {
                "kinyarwanda": content_rw,
                "english": content_en,
                "french": content_fr
            }
        })
    
    return law_data

def start_process():
    path = filedialog.askdirectory()
    if not path: return
    
    files = [f for f in os.listdir(path) if f.lower().endswith(".pdf")]
    if not files:
        messagebox.showerror("Error", "No PDFs found!")
        return

    display_area.delete('1.0', tk.END)
    for file in files:
        data = extract_trilingual_json(os.path.join(path, file))
        # Format as pretty JSON for the UI
        pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
        display_area.insert(tk.END, f"FILE: {file}\n" + "-"*30 + "\n")
        display_area.insert(tk.END, pretty_json + "\n\n")

# --- UI Setup ---
root = tk.Tk()
root.title("Rwandan Trilingual Legal Parser (Advanced)")
root.geometry("1000x700")

tk.Button(root, text="Select Folder & Generate Trilingual JSON", 
          command=start_process, bg="#2c3e50", fg="white", font=("Arial", 11, "bold")).pack(pady=20)

display_area = scrolledtext.ScrolledText(root, wrap=tk.NONE, width=120, height=35, bg="#1e1e1e", fg="#d4d4d4")
display_area.pack(padx=20, pady=10)

root.mainloop()