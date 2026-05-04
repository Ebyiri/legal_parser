import fitz  # PyMuPDF
import re
import os

def extract_rwandan_law(pdf_path):
    """
    Extracts text using a 3-column clip to separate 
    Kinyarwanda, English, and French.
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        w = page.rect.width
        h = page.rect.height
        
        # Define the three vertical columns (Left, Middle, Right)
        # Column 1: Kinyarwanda | Column 2: English | Column 3: French
        columns = [
            fitz.Rect(0, 0, w/3, h),       
            fitz.Rect(w/3, 0, 2*w/3, h),   
            fitz.Rect(2*w/3, 0, w, h)      
        ]
        
        for col in columns:
            full_text += page.get_text("text", clip=col) + "\n"
    
    return full_text

def chunk_by_articles(text):
    pattern = r'(Article\s+(?:\d+|One|I|II|III|IV|V)|Icyungo\s+\d+)'
    parts = re.split(pattern, text)
    chunks = []
    
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        # Normalization: Change 'Article One' to 'Article 1' for easier searching
        title = title.replace("Article One", "Article 1").replace("Article I", "Article 1")
        
        content = parts[i+1].strip() if i+1 < len(parts) else ""
        chunks.append({"title": title, "content": content})
    
    return chunks
if __name__ == "__main__":
    # 1. Get the folder where THIS script lives (the 'src' folder)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Go up one level to the main 'Rwanda_Legal_Parser' folder
    project_root = os.path.dirname(current_dir)
    
    # 3. Point to the 'laws' folder correctly
    laws_dir = os.path.join(project_root, "laws")
    
    # Check if the folder exists and has PDFs
    if os.path.exists(laws_dir):
        pdf_files = [f for f in os.listdir(laws_dir) if f.endswith(".pdf")]
        
        if pdf_files:
            # Use the first PDF found
            test_pdf = os.path.join(laws_dir, pdf_files[0])
            print(f"Found PDF: {pdf_files[0]}")
            
            raw_text = extract_rwandan_law(test_pdf)
            legal_chunks = chunk_by_articles(raw_text)
            
            for chunk in legal_chunks[:2]:
                print(f"\n--- {chunk['title']} ---")
                print(chunk['content'][:200] + "...")
        else:
            print(f"No PDF files found in: {laws_dir}")
    else:
        print(f"Directory not found: {laws_dir}")