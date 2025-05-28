from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sqlite3
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our custom modules
from resume_parser import ResumeParser
from job_matcher import JobMatcher

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = '../uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
resume_parser = ResumeParser()
job_matcher = JobMatcher()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    """Initialize SQLite database for storing user data"""
    # Create database directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
    os.makedirs(db_dir, exist_ok=True)

    # Connect to database
    db_path = os.path.join(db_dir, 'users.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create resume_analyses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            filename TEXT,
            extracted_text TEXT,
            skills TEXT,
            experience TEXT,
            education TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES users (session_id)
        )
    ''')

    # Create job_matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            resume_id INTEGER,
            job_title TEXT,
            company TEXT,
            match_score REAL,
            job_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES users (session_id),
            FOREIGN KEY (resume_id) REFERENCES resume_analyses (id)
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/upload', methods=['POST'])
def upload_resume():
    """Handle resume upload and analysis"""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if file and allowed_file(file.filename):
            # Secure the filename and save
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Parse the resume
            parsed_data = resume_parser.parse_resume(filepath)

            if parsed_data['success']:
                # Get session ID from request or generate new one
                session_id = request.form.get('session_id', f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

                # Store in database
                db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
                db_path = os.path.join(db_dir, 'users.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Insert or update user
                cursor.execute('INSERT OR IGNORE INTO users (session_id) VALUES (?)', (session_id,))

                # Insert resume analysis
                cursor.execute('''
                    INSERT INTO resume_analyses
                    (session_id, filename, extracted_text, skills, experience, education)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    filename,
                    parsed_data['text'],
                    json.dumps(parsed_data['skills']),
                    json.dumps(parsed_data['experience']),
                    json.dumps(parsed_data['education'])
                ))

                resume_id = cursor.lastrowid
                conn.commit()
                conn.close()

                # Clean up uploaded file
                os.remove(filepath)

                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'resume_id': resume_id,
                    'data': parsed_data
                })
            else:
                return jsonify({'error': parsed_data['error']}), 400

        else:
            return jsonify({'error': 'Invalid file type. Please upload PDF or DOCX files.'}), 400

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/match-jobs', methods=['POST'])
def match_jobs():
    """Find matching jobs for the parsed resume"""
    try:
        data = request.get_json()
        resume_data = data.get('resume_data')
        session_id = data.get('session_id')
        resume_id = data.get('resume_id')

        if not resume_data:
            return jsonify({'error': 'No resume data provided'}), 400

        # Get job matches
        matches = job_matcher.find_matches(resume_data)

        # Store matches in database
        if session_id and resume_id:
            db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
            db_path = os.path.join(db_dir, 'users.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            for match in matches:
                cursor.execute('''
                    INSERT INTO job_matches
                    (session_id, resume_id, job_title, company, match_score, job_description)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    resume_id,
                    match['title'],
                    match['company'],
                    match['match_score'],
                    match['description']
                ))

            conn.commit()
            conn.close()

        return jsonify({
            'success': True,
            'matches': matches
        })

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/skill-gap', methods=['POST'])
def analyze_skill_gap():
    """Analyze skill gaps between resume and job requirements"""
    try:
        data = request.get_json()
        resume_skills = data.get('resume_skills', [])
        job_description = data.get('job_description', '')

        gap_analysis = job_matcher.analyze_skill_gap(resume_skills, job_description)

        return jsonify({
            'success': True,
            'gap_analysis': gap_analysis
        })

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/history/<session_id>')
def get_user_history(session_id):
    """Get user's resume analysis and job match history"""
    try:
        db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
        db_path = os.path.join(db_dir, 'users.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get resume analyses
        cursor.execute('''
            SELECT id, filename, skills, experience, education, created_at
            FROM resume_analyses
            WHERE session_id = ?
            ORDER BY created_at DESC
        ''', (session_id,))

        resumes = []
        for row in cursor.fetchall():
            resumes.append({
                'id': row[0],
                'filename': row[1],
                'skills': json.loads(row[2]) if row[2] else [],
                'experience': json.loads(row[3]) if row[3] else [],
                'education': json.loads(row[4]) if row[4] else [],
                'created_at': row[5]
            })

        # Get job matches
        cursor.execute('''
            SELECT job_title, company, match_score, created_at
            FROM job_matches
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT 20
        ''', (session_id,))

        matches = []
        for row in cursor.fetchall():
            matches.append({
                'job_title': row[0],
                'company': row[1],
                'match_score': row[2],
                'created_at': row[3]
            })

        conn.close()

        return jsonify({
            'success': True,
            'resumes': resumes,
            'matches': matches
        })

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    # Initialize database
    init_database()

    # Load job data
    job_matcher.load_job_data()

    print("🚀 Resume Analyzer and Job Match Recommender")
    print("📊 Server starting on http://localhost:5000")
    print("📁 Upload folder:", os.path.abspath(app.config['UPLOAD_FOLDER']))

    app.run(debug=True, host='0.0.0.0', port=5000)
