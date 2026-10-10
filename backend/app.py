import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

try:
    from .final_ocr_system import MarksCardOCRSystem
except Exception:
    # Fallback when running app.py directly
    from final_ocr_system import MarksCardOCRSystem

# Flask config
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), 'web_results')
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

def generate_random_id(length=8):
    import random, string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# API route to get all documents in chronological order (public)
@app.route('/api/documents', methods=['GET'])
def api_documents():
    results_dir = app.config['RESULTS_FOLDER']
    docs = []
    if os.path.exists(results_dir):
        runs = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
        def extract_ts(name):
            parts = name.split('_')
            if len(parts) >= 2:
                try:
                    return datetime.strptime(parts[0] + '_' + parts[1], '%Y%m%d_%H%M%S')
                except Exception:
                    return datetime.min
            return datetime.min
        runs_sorted = sorted(runs, key=extract_ts, reverse=True)
        for run_id in runs_sorted:
            block_id = generate_random_id()
            docs.append({
                'id': block_id,
                'run_id': run_id,
                'name': run_id,
                'link': f'/result/{run_id}'
            })
    return jsonify(docs)


def allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{ts}_" + file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Run OCR
        ocr = MarksCardOCRSystem(confidence_threshold=0.5)
        data = ocr.process_marks_card(
            file_path,
            preprocess=True,
            do_deskew=True,
            do_denoise=True,
            use_adaptive=True,
            contrast=True,
            temp_dir=os.path.join(app.config['RESULTS_FOLDER'], 'preprocessed')
        )

        # Save results to dedicated folder per upload
        out_dir = os.path.join(app.config['RESULTS_FOLDER'], os.path.splitext(filename)[0])
        ocr.save_results(data, out_dir)

        return redirect(url_for('result', run_id=os.path.basename(out_dir)))

    return redirect(url_for('index'))


@app.route('/result/<run_id>', methods=['GET'])
def result(run_id: str):
    out_dir = os.path.join(app.config['RESULTS_FOLDER'], run_id)
    json_path = os.path.join(out_dir, 'marks_card_structured.json')

    if not os.path.exists(json_path):
        return redirect(url_for('index'))

    with open(json_path, 'r', encoding='utf-8') as f:
        data = f.read()

    return render_template('result.html', run_id=run_id, data_json=data)


@app.route('/download/<run_id>/<path:filename>')
def download(run_id: str, filename: str):
    out_dir = os.path.join(app.config['RESULTS_FOLDER'], run_id)
    return send_from_directory(out_dir, filename, as_attachment=True)


@app.route('/api/result/<run_id>')
def api_result(run_id: str):
    out_dir = os.path.join(app.config['RESULTS_FOLDER'], run_id)
    json_path = os.path.join(out_dir, 'marks_card_structured.json')
    if not os.path.exists(json_path):
        return jsonify({'error': 'not found'}), 404
    with open(json_path, 'r', encoding='utf-8') as f:
        return jsonify(**__import__('json').load(f))


if __name__ == '__main__':
    # Ensure the app runs inside the virtual environment `myenv` when started via PowerShell
    port = int(os.environ.get('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=True)
