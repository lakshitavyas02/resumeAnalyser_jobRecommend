# 🎯 AI-Powered Resume Analyzer & Job Matcher

## 📌 Project Overview

An intelligent web application that analyzes resumes using advanced NLP techniques and matches candidates with relevant job opportunities using real-time job data from multiple sources. Features dynamic skill learning, TF-IDF similarity scoring, and comprehensive skill gap analysis.

![image](https://github.com/user-attachments/assets/53081cc5-e42e-47d5-b05e-4b0505d1fea8)

## ✨ Core Features

- **🔍 Smart Resume Parsing**: Upload PDF/DOCX files with advanced text extraction
- **🧠 Dynamic Skill Learning**: AI learns new skills from job postings and trending technologies
- **🌐 Live Job Data Integration**: Real-time job fetching from Indeed, RemoteOK, and USAJobs
- **📊 TF-IDF Job Matching**: Advanced similarity scoring using cosine similarity
- **📈 Skill Gap Analysis**: Detailed analysis of missing skills vs job requirements
- **💾 User History & Dashboard**: Track resume analyses and job matches
- **🔄 Auto-updating Job Database**: Refreshes job data every 6 hours
- **🎨 Responsive Web Interface**: Modern, mobile-friendly design

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Backend**: Python 3.8+, Flask, Flask-CORS
- **NLP & AI**: spaCy, NLTK, TextBlob, Sentence Transformers
- **Machine Learning**: Scikit-learn, TF-IDF, Cosine Similarity, NumPy, Pandas
- **Document Processing**: PyMuPDF, python-docx, docx2txt
- **Database**: SQLite with dynamic schema
- **APIs**: Indeed RapidAPI, RemoteOK, USAJobs
- **Deployment**: Gunicorn-ready for cloud deployment

## 📁 Project Structure

```
JOB/
├── backend/                          # Core application logic
│   ├── app.py                       # Main Flask application
│   ├── resume_parser.py             # Resume text extraction & parsing
│   ├── job_matcher.py               # TF-IDF job matching engine
│   ├── live_job_fetcher.py          # Real-time job data fetching
│   ├── dynamic_skill_learner.py     # AI skill learning system
│   ├── database/                    # Backend data storage
│   │   └── learned_skills.pkl       # Dynamically learned skills
│   └── utils/                       # Utility modules
│       ├── pdf_parser.py            # PDF text extraction
│       ├── skill_extractor.py       # NLP skill extraction
│       └── similarity.py            # Text similarity calculations
├── database/                        # Main data storage
│   ├── users.db                     # SQLite user database
│   ├── jobs.csv                     # Static job data
│   ├── live_jobs.csv               # Live fetched job data
│   ├── learned_skills.pkl          # AI learned skills backup
│   └── last_update.txt             # Last job data update timestamp
├── templates/                       # HTML templates
│   ├── index.html                  # Main upload page
│   └── dashboard.html              # User dashboard
├── static/                         # Static web assets
│   ├── style.css                   # Custom CSS styles
│   └── scripts.js                  # Frontend JavaScript
├── uploads/                        # Temporary file uploads
├── venv/                          # Python virtual environment
├── requirements.txt               # Python dependencies
├── INDEED_API_SETUP.md           # API setup guide
├── sample_resume.txt              # Sample resume for testing
└── README.md                      # Project documentation
```

## 🚀 Quick Start

### Option 1: Basic Setup (Recommended)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd JOB

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download spaCy model for advanced NLP
python -m spacy download en_core_web_sm

# 6. Run the application
python backend/app.py
```

### Option 2: With Live Job Data (Optional)

For real-time job fetching, set up Indeed API:

```bash
# 1. Follow basic setup above
# 2. Get RapidAPI key from https://rapidapi.com/indeed/api/indeed
# 3. Set environment variable
set RAPIDAPI_KEY=your_rapidapi_key_here  # Windows
export RAPIDAPI_KEY=your_rapidapi_key_here  # Linux/Mac

# 4. Run with live data
python backend/app.py
```

### 🌐 Access the Application

Open your browser and navigate to: **http://localhost:5000**

## 📈 Features Implemented

### ✅ Core Features

- **📄 Advanced Resume Parsing**: PDF/DOCX text extraction with PyMuPDF and python-docx
- **🧠 Dynamic Skill Learning**: AI learns new skills from job postings and trending technologies
- **🌐 Live Job Data Integration**: Real-time fetching from Indeed, RemoteOK, and USAJobs APIs
- **📊 TF-IDF Job Matching**: Advanced similarity scoring using cosine similarity
- **📈 Comprehensive Skill Gap Analysis**: Detailed missing skills analysis
- **💾 User History & Dashboard**: SQLite database for tracking analyses and matches
- **🎨 Modern Web Interface**: Responsive Bootstrap 5 design

### 🔧 Technical Features

- **🔄 Auto-updating Job Database**: Refreshes every 6 hours automatically
- **🎯 Multi-source Job Aggregation**: Combines data from multiple job APIs
- **📱 Mobile-responsive Design**: Works seamlessly on all devices
- **🔒 Secure File Handling**: Temporary file processing with automatic cleanup
- **⚡ Fast Text Processing**: Optimized NLP pipelines for quick analysis

## 🔧 Usage

1. Upload your resume (PDF or DOCX format)
2. Wait for the system to analyze your resume
3. View recommended jobs with match percentages
4. Check skill gaps and recommendations
5. Save interesting job matches

## 🚀 Future Enhancements

### 🎯 Planned Features

- **🔐 User Authentication**: Login system with personalized profiles
- **🤖 Advanced NLP**: BERT embeddings for better semantic understanding
- **📧 Email Notifications**: Automated alerts for new job matches
- **📝 Resume Improvement**: AI-powered suggestions for resume optimization
- **📊 Analytics Dashboard**: Detailed statistics and insights
- **🔗 LinkedIn Integration**: Direct profile import and job application
- **💼 Company Insights**: Detailed company information and culture fit analysis
- **🎨 Resume Templates**: Professional resume generation and formatting

### 🌟 Potential Integrations

- **Glassdoor API**: Salary insights and company reviews
- **GitHub Integration**: Automatic project portfolio analysis
- **Stack Overflow**: Developer skill verification
- **Coursera/Udemy**: Skill gap learning recommendations

## 🧪 Testing the Application

### Test with Sample Resume

```bash
# Use the provided sample resume
python backend/app.py
# Then upload sample_resume.txt through the web interface
```

### Test Live Job Fetching

```bash
# Test the job fetcher independently
python backend/live_job_fetcher.py
```

### Test Dynamic Skill Learning

```bash
# Test the skill learning system
python backend/dynamic_skill_learner.py
```

## 🔧 Troubleshooting

### Common Issues:

1. **"Module not found" errors**: Ensure virtual environment is activated
2. **spaCy model not found**: Run `python -m spacy download en_core_web_sm`
3. **Port already in use**: Change port in app.py or kill existing process
4. **File upload fails**: Check uploads directory exists and has write permissions
5. **API rate limits**: Indeed API has monthly limits on free tier

### Performance Tips:

- **Large resumes**: Processing may take 10-30 seconds for complex documents
- **Job data refresh**: First run may take longer as it fetches live job data
- **Skill learning**: Dynamic skill learning improves over time with more job data

### API Configuration:

- **Without API keys**: Application works with sample job data
- **With Indeed API**: Set `RAPIDAPI_KEY` environment variable
- **Rate limiting**: Free tier allows 100 requests/month

## 🤝 Contributing

We welcome contributions! Here are areas where you can help:

### 🎯 Priority Areas

- **🔧 Additional file format support** (RTF, TXT, HTML resumes)
- **🧠 Enhanced NLP algorithms** (BERT, GPT integration)
- **🌐 More job source integrations** (LinkedIn, Glassdoor, AngelList)
- **🎨 UI/UX improvements** (React frontend, better visualizations)
- **⚡ Performance optimizations** (caching, async processing)

### 🚀 How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - Feel free to use and modify for your projects!

## 🙏 Acknowledgments

- **🐍 Python Community**: For amazing libraries like spaCy, NLTK, and scikit-learn
- **🌐 Open APIs**: Indeed, RemoteOK, and USAJobs for providing job data
- **🎨 Bootstrap Team**: For the responsive design framework
- **🤖 AI/ML Community**: For advancing NLP and text similarity techniques
- **💼 Job Seekers**: Who inspired this tool to make job hunting more efficient

---

**⭐ If this project helped you, please give it a star! ⭐**
