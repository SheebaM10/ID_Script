from bson import ObjectId
from flask import Flask, request, render_template, send_from_directory, flash, redirect, url_for, session, jsonify
import pymongo
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
import os
import uuid
import logging
import markdown as md
import threading
import time
import functools
from flask import g
from utils.exporter import export_to_docx_table
from utils.extractor import extract_text_from_file
from utils.script_generator import generate_script, parse_markdown_to_table, generate_title, model
from utils.prompt_builder import build_prompt
import re

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB file size limit

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'.docx', '.pdf', '.pptx'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)

progress_dict = {}

# In-memory rate limiting (per IP, 10/min)
rate_limit = {}
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = 60  # seconds

def check_rate_limit():
    ip = request.remote_addr
    now = int(time.time())
    window = now // RATE_LIMIT_WINDOW
    key = f"{ip}:{window}"
    count = rate_limit.get(key, 0)
    if count >= RATE_LIMIT_MAX:
        return False
    rate_limit[key] = count + 1
    return True

def allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def file_signature_check(filepath, ext):
    try:
        with open(filepath, 'rb') as f:
            sig = f.read(8)
        if ext == '.pdf' and not sig.startswith(b'%PDF'):
            return False
        if ext == '.docx' and sig[:2] != b'PK':  # DOCX is a zip file
            return False
        if ext == '.pptx' and sig[:2] != b'PK':  # PPTX is a zip file
            return False
        return True
    except Exception:
        return False

def update_recent_files(output_filename):
    recent_files = session.get("recent_files", [])
    if output_filename in recent_files:
        recent_files.remove(output_filename)
    recent_files.append(output_filename)
    session["recent_files"] = recent_files[-3:]
    session["last_generated_file"] = output_filename

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    generated_file = session.get("last_generated_file")

    recent_files = session.get("recent_files", [])

    return render_template(
        'index.html',
        generated_file=generated_file,
        recent_files=recent_files
    )



@app.route('/generate', methods=['POST'])
def generate():
    if 'user_id' not in session:
        flash("Please login first.", "danger")
        return redirect(url_for('login'))

    if not check_rate_limit():
        flash("Rate limit exceeded. Please try again later.", "error")
        return redirect(url_for('dashboard'))

    # Enforce upload limit for free users
    if session['plan'] == 'free' and session['doc_upload_count'] >= 10:
        flash("Free plan limit reached. Please upgrade to premium.", "danger")
        return redirect(url_for('dashboard'))

    file = request.files.get('file')
    if not file or file.filename.strip() == '':
        flash("No file selected.", "error")
        return redirect(url_for('dashboard'))

    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        flash("Invalid file type. Only DOCX, PDF, and PPTX are allowed.", "error")
        return redirect(url_for('dashboard'))

    ext = Path(filename).suffix
    unique_filename = f"{Path(filename).stem}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)

    if not file_signature_check(filepath, ext):
        os.remove(filepath)
        flash("File signature does not match file type.", "error")
        return redirect(url_for('dashboard'))

    extracted_text = extract_text_from_file(filepath)

    try:
        logging.info("Calling Gemini API for script generation...")
        markdown, docx_path = generate_script(extracted_text, OUTPUT_FOLDER, original_filename=filename)

    except Exception as e:
        logging.exception("Script generation failed:")
        flash("Script generation failed. Please try again.", "error")
        return redirect(url_for('dashboard'))

    if docx_path is None:
        flash(markdown or "Generation failed.", "error")
        return redirect(url_for('dashboard'))

    output_filename = Path(docx_path).name
    update_recent_files(output_filename)

    # Update document count
    users_col.update_one({"_id": ObjectId(session['user_id'])}, {"$inc": {"doc_upload_count": 1}})
    session['doc_upload_count'] += 1

    flash("Script generated successfully!", "success")
    return redirect(url_for('dashboard'))


@app.route('/outputs/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

@app.route('/preview/<filename>')
def preview_file(filename):
    return send_from_directory(
        OUTPUT_FOLDER, filename,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

@app.route('/view_table/<filename>')
def view_table(filename):
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(filepath):
        flash('File not found.', 'error')
        return redirect(url_for('dashboard'))
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Preprocess: replace <...> with _..._ for HTML preview
    content = re.sub(r'<([^>]+)>', r'_\1_', content)
    html = md.markdown(content, extensions=['extra', 'tables'])
    return render_template('view_table.html', table_html=html, filename=filename)

@app.route('/generate_async', methods=['POST'])
def generate_async():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized. Please login.'}), 401

    if not check_rate_limit():
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

    if session['plan'] == 'free' and session['doc_upload_count'] >= 10:
        return jsonify({'error': 'Free plan limit reached. Upgrade to premium.'}), 403

    file = request.files.get('file')
    if not file or file.filename.strip() == '':
        return jsonify({'error': 'No file selected.'}), 400

    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        return jsonify({'error': 'Invalid file type.'}), 400

    ext = Path(filename).suffix
    unique_filename = f"{Path(filename).stem}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)

    if not file_signature_check(filepath, ext):
        os.remove(filepath)
        return jsonify({'error': 'File signature does not match file type.'}), 400

    task_id = uuid.uuid4().hex
    progress_dict[task_id] = {'progress': 0, 'status': 'Starting...'}

    # ✅ Extract data outside session for thread-safe access
    user_id = session['user_id']

    def run_generation(user_id=user_id):  # Pass user_id into thread
        try:
            progress_dict[task_id] = {'progress': 10, 'status': 'Extracting text...'}
            extracted_text = extract_text_from_file(filepath)

            progress_dict[task_id] = {'progress': 30, 'status': 'Generating script...'}
            logging.info(f"Calling Gemini API for script generation (async, task {task_id})...")
            markdown, docx_path = generate_script_with_progress(extracted_text, OUTPUT_FOLDER, task_id)

            if docx_path is None:
                progress_dict[task_id] = {'progress': 100, 'status': 'Failed', 'error': markdown or 'Generation failed.'}
                return

            output_filename = Path(docx_path).name
            progress_dict[task_id] = {'progress': 100, 'status': 'Done', 'file': output_filename}

            # ✅ DB update allowed from thread (not session)
            users_col.update_one({"_id": ObjectId(user_id)}, {"$inc": {"doc_upload_count": 1}})
            # ❌ Don't access session here

        except Exception as e:
            logging.exception(f"Script generation failed (async, task {task_id}):")
            progress_dict[task_id] = {'progress': 100, 'status': 'Failed', 'error': str(e)}

    threading.Thread(target=run_generation).start()
    return jsonify({'task_id': task_id})


def generate_script_with_progress(content, output_dir, task_id, original_filename=None):
    prompt = build_prompt(content)
    output_path = os.path.join(output_dir, "generated_script.docx")
    try:
        progress_dict[task_id] = {'progress': 40, 'status': 'Calling Gemini API...'}
        response = model.generate_content(prompt)
        markdown = response.text.strip()
    except Exception as e:
        return f"Gemini API Error: {str(e)}", None
    try:
        progress_dict[task_id] = {'progress': 70, 'status': 'Parsing script...'}
        structured_script_data = parse_markdown_to_table(markdown)
    except Exception as e:
        return str(e), None
    try:
        progress_dict[task_id] = {'progress': 85, 'status': 'Exporting to DOCX...'}
        generated_title = generate_title(content)
        if original_filename:
            filename = Path(original_filename).stem
        else:
            filename = generated_title
        safe_title = ''.join(c for c in filename if c.isalnum() or c in (' ', '_', '-')).rstrip()
        file_base = safe_title.replace(' ', '_')[:40] or 'Instructional_Script'
        output_path = os.path.join(output_dir, f"{file_base}.docx")
        export_to_docx_table(structured_script_data, output_path, generated_title)
    except Exception as e:
        return f"Export Error: {str(e)}", None
    progress_dict[task_id] = {'progress': 100, 'status': 'Done'}
    return markdown, output_path

@app.route('/progress/<task_id>')
def progress(task_id):
    prog = progress_dict.get(task_id)
    if prog and prog.get('status') == 'Done' and 'file' in prog:
        update_recent_files(prog['file'])

        # ✅ Safe session update here (within request context)
        if session.get('plan') == 'free':
            session['doc_upload_count'] += 1

    if not prog:
        return jsonify({'progress': 0, 'status': 'Not started'}), 404

    return jsonify(prog)


from pymongo import MongoClient

# MongoDB connection
# client = pymongo.MongoClient("mongodb://myUser:myPassword@13.235.78.101:27017/subscription_app?authSource=admin")
# MongoDB connection
# client = pymongo.MongoClient("mongodb://myUser:myPassword@13.235.78.101:27017/subscription_app?authSource=admin")
client = pymongo.MongoClient("mongodb://myUser:myPassword@13.204.31.17:27017/subscription_app?authSource=admin")
# client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client['subscription_app']
users_col = db['users']


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users_col.find_one({"username": username}):
            flash('Username already exists.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            users_col.insert_one({
                "username": username,
                "password": hashed_password,
                "plan": "free",
                "doc_upload_count": 0
            })
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_col.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['plan'] = user['plan']
            session['doc_upload_count'] = user['doc_upload_count']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))


@app.route('/upgrade')
def upgrade():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    users_col.update_one({"_id": ObjectId(session['user_id'])}, {"$set": {"plan": "premium"}})
    session['plan'] = 'premium'
    flash('You have been upgraded to premium!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('username') != 'admin':
        return redirect(url_for('login'))
    all_users = users_col.find()
    users = [{
        "username": user["username"],
        "plan": user["plan"],
        "doc_upload_count": user.get("doc_upload_count", 0)
    } for user in all_users]
    return render_template('admin_dashboard.html', users=users)


if __name__ == "__main__":
    app.run(debug=True)
