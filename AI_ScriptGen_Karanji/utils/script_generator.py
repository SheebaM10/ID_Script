import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
from utils.prompt_builder import build_prompt
from utils.exporter import export_to_docx_table

# ✅ Gemini API setup
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def generate_script(content, output_dir):
    prompt = build_prompt(content)

    try:
        response = model.generate_content(prompt)
        markdown = response.text.strip()
    except Exception as e:
        return f"Gemini API Error: {str(e)}", None

    try:
        structured_script_data = parse_markdown_to_table(markdown)
    except Exception as e:
        return str(e), None

    # Extract the Welcome Slide title from the first row's On-Screen Text
    if structured_script_data and 'on_screen_text' in structured_script_data[0]:
        welcome_title = structured_script_data[0]['on_screen_text'].split('\n')[0].strip()
    else:
        welcome_title = generate_title(content)
    # Sanitize for filename
    safe_title = ''.join(c for c in welcome_title if c.isalnum() or c in (' ', '_', '-')).rstrip()
    file_base = safe_title.replace(' ', '_')[:40] or 'Instructional_Script'
    output_path = os.path.join(output_dir, f"{file_base}.docx")
    try:
        export_to_docx_table(structured_script_data, output_path, welcome_title)
    except Exception as e:
        return f"Export Error: {str(e)}", None

    return markdown, output_path

def generate_title(content):
    title_prompt = f"""
    You are an instructional designer. Based on the following content, generate a clear, concise title under 12 words for a training module.

    Only respond with the best possible title. Do not include multiple options.

    Content:
    \"\"\"{content}\"\"\"

    Title:
    """
    try:
        response = model.generate_content(title_prompt)
        title_lines = [line.strip().replace('"', '') for line in response.text.strip().splitlines() if line.strip()]
        title = title_lines[0] if title_lines else "Instructional Script"
        return title
    except Exception:
        return "Instructional Script"

def extract_markdown_table(text):
    """
    Extracts the largest markdown table from the text.
    Returns the table as a string, or an empty string if none found.
    """
    # Find all markdown tables (blocks of consecutive lines starting and ending with '|')
    tables = re.findall(r"((?:\|[^\n]*\|\n)+)", text)
    if not tables:
        return ""
    # Choose the largest table (most rows)
    largest_table = max(tables, key=lambda tbl: tbl.count('\n'))
    return largest_table.strip()

def parse_markdown_to_table(markdown_text):
    """
    Parses a markdown table with 5 expected columns into structured data rows.
    Skips duplicated headers or malformed rows.
    """
    rows = []
    lines = markdown_text.strip().splitlines()

    for line in lines:
        if not line.strip().startswith("|") or line.count("|") < 6:
            continue

        if all(p.strip('- ').strip() == '' for p in line.strip().split("|")[1:-1]):
            continue
        
        # Skip repeated header rows
        lower_line = line.lower()
        if all(h in lower_line for h in ["slide number", "voice-over", "on-screen", "video description", "image"]):
            continue

        parts = [p.strip() for p in line.strip().split("|")[1:-1]]
        if len(parts) == 5:
            rows.append({
                "slide_number": parts[0],
                "voice_over": parts[1],
                "on_screen_text": parts[2],
                "video_description": parts[3],
                "image_suggestion": parts[4],
            })

    if not rows:
        raise ValueError("Failed to parse any valid rows from Gemini response. Check if the table format is correct.")

    return rows
