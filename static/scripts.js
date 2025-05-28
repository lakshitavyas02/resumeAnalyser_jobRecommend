// Resume Analyzer JavaScript

// Global variables
let currentSessionId = null;
let currentResumeData = null;

// DOM Elements
const resumeForm = document.getElementById('resumeForm');
const resumeFile = document.getElementById('resumeFile');
const uploadArea = document.getElementById('uploadArea');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSection = document.getElementById('loading');
const resultsSection = document.getElementById('results');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeDragAndDrop();
});

// Initialize all event listeners
function initializeEventListeners() {
    // File input change
    resumeFile.addEventListener('change', handleFileSelect);
    
    // Form submission
    resumeForm.addEventListener('submit', handleFormSubmit);
    
    // Upload area click
    uploadArea.addEventListener('click', () => resumeFile.click());
}

// Initialize drag and drop functionality
function initializeDragAndDrop() {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    uploadArea.addEventListener('drop', handleDrop, false);
}

// Prevent default drag behaviors
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Highlight upload area
function highlight(e) {
    uploadArea.classList.add('dragover');
}

// Remove highlight from upload area
function unhighlight(e) {
    uploadArea.classList.remove('dragover');
}

// Handle dropped files
function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
        resumeFile.files = files;
        handleFileSelect();
    }
}

// Handle file selection
function handleFileSelect() {
    const file = resumeFile.files[0];
    
    if (file) {
        // Validate file type
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        
        if (!allowedTypes.includes(file.type)) {
            showAlert('Please select a PDF or DOCX file.', 'danger');
            clearFile();
            return;
        }
        
        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            showAlert('File size must be less than 16MB.', 'danger');
            clearFile();
            return;
        }
        
        // Display file info
        fileName.textContent = file.name;
        fileInfo.classList.remove('d-none');
        analyzeBtn.disabled = false;
        
        // Add success styling to upload area
        uploadArea.style.borderColor = '#198754';
        uploadArea.style.backgroundColor = 'rgba(25, 135, 84, 0.05)';
    }
}

// Clear selected file
function clearFile() {
    resumeFile.value = '';
    fileInfo.classList.add('d-none');
    analyzeBtn.disabled = true;
    
    // Reset upload area styling
    uploadArea.style.borderColor = '#dee2e6';
    uploadArea.style.backgroundColor = '#f8f9fa';
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const file = resumeFile.files[0];
    if (!file) {
        showAlert('Please select a file first.', 'warning');
        return;
    }
    
    // Show loading
    showLoading();
    
    try {
        // Upload and analyze resume
        const formData = new FormData();
        formData.append('resume', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSessionId = data.session_id;
            currentResumeData = data.data;
            
            // Store session ID in localStorage
            localStorage.setItem('sessionId', currentSessionId);
            
            // Display resume analysis results
            displayResumeAnalysis(data.data);
            
            // Get job matches
            await getJobMatches(data.data, currentSessionId, data.resume_id);
            
        } else {
            showAlert(data.error || 'Error analyzing resume. Please try again.', 'danger');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showAlert('Network error. Please check your connection and try again.', 'danger');
    } finally {
        hideLoading();
    }
}

// Get job matches for the analyzed resume
async function getJobMatches(resumeData, sessionId, resumeId) {
    try {
        const response = await fetch('/api/match-jobs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_data: resumeData,
                session_id: sessionId,
                resume_id: resumeId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayJobMatches(data.matches);
        } else {
            showAlert('Error finding job matches: ' + (data.error || 'Unknown error'), 'warning');
        }
        
    } catch (error) {
        console.error('Error getting job matches:', error);
        showAlert('Error finding job matches. Please try again.', 'warning');
    }
}

// Display resume analysis results
function displayResumeAnalysis(data) {
    // Update statistics
    document.getElementById('skillsCount').textContent = data.skills ? data.skills.length : 0;
    document.getElementById('experienceCount').textContent = data.experience && data.experience.job_titles ? data.experience.job_titles.length : 0;
    document.getElementById('educationCount').textContent = data.education && data.education.degrees ? data.education.degrees.length : 0;
    
    // Display skills
    displaySkills(data.skills || []);
    
    // Show results section
    resultsSection.classList.remove('d-none');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Show success message
    showAlert(`Resume analyzed successfully! Found ${data.skills ? data.skills.length : 0} skills.`, 'success');
}

// Display extracted skills
function displaySkills(skills) {
    const skillsList = document.getElementById('skillsList');
    
    if (skills.length === 0) {
        skillsList.innerHTML = '<p class="text-muted">No skills detected in the resume.</p>';
        return;
    }
    
    const skillsHtml = skills.map(skill => 
        `<span class="skill-tag">${skill}</span>`
    ).join('');
    
    skillsList.innerHTML = skillsHtml;
}

// Display job matches
function displayJobMatches(matches) {
    const container = document.getElementById('jobRecommendations');
    
    if (matches.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-search fa-3x mb-3"></i>
                <h4>No job matches found</h4>
                <p>Try updating your resume with more relevant skills.</p>
            </div>
        `;
        return;
    }
    
    const jobsHtml = matches.map((job, index) => `
        <div class="job-card fade-in" style="animation-delay: ${index * 0.1}s">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h5 class="mb-2">
                        <i class="fas fa-briefcase me-2 text-primary"></i>
                        ${job.title}
                    </h5>
                    <p class="text-muted mb-2">
                        <i class="fas fa-building me-2"></i>
                        ${job.company}
                    </p>
                    <p class="text-muted mb-2">
                        <i class="fas fa-map-marker-alt me-2"></i>
                        ${job.location}
                    </p>
                    <p class="mb-3">${job.description.substring(0, 150)}...</p>
                    <div class="d-flex flex-wrap gap-2 mb-3">
                        ${job.requirements.split(',').slice(0, 5).map(req => 
                            `<span class="badge bg-secondary">${req.trim()}</span>`
                        ).join('')}
                    </div>
                    <div class="row text-muted small">
                        <div class="col-md-6">
                            <i class="fas fa-dollar-sign me-1"></i>
                            ${job.salary_range}
                        </div>
                        <div class="col-md-6">
                            <i class="fas fa-clock me-1"></i>
                            ${job.job_type} • ${job.experience_level}
                        </div>
                    </div>
                </div>
                <div class="col-md-4 text-center">
                    <div class="match-score ${getMatchScoreClass(job.match_score)}">
                        ${job.match_score}%
                    </div>
                    <p class="small text-muted mb-3">Match Score</p>
                    <button class="btn btn-primary btn-sm" onclick="analyzeSkillGap('${job.title}', '${job.requirements}')">
                        <i class="fas fa-chart-line me-1"></i>
                        Skill Gap
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = jobsHtml;
}

// Get match score CSS class
function getMatchScoreClass(score) {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

// Analyze skill gap for a specific job
async function analyzeSkillGap(jobTitle, jobRequirements) {
    if (!currentResumeData || !currentResumeData.skills) {
        showAlert('No resume data available for skill gap analysis.', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/skill-gap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_skills: currentResumeData.skills,
                job_description: jobRequirements
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSkillGapModal(jobTitle, data.gap_analysis);
        } else {
            showAlert('Error analyzing skill gap: ' + (data.error || 'Unknown error'), 'warning');
        }
        
    } catch (error) {
        console.error('Error analyzing skill gap:', error);
        showAlert('Error analyzing skill gap. Please try again.', 'warning');
    }
}

// Show skill gap analysis in modal
function showSkillGapModal(jobTitle, gapAnalysis) {
    const modalHtml = `
        <div class="modal fade" id="skillGapModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-chart-line me-2"></i>
                            Skill Gap Analysis - ${jobTitle}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-4">
                            <div class="col-md-4 text-center">
                                <h3 class="text-success">${gapAnalysis.matching_skills.length}</h3>
                                <p class="text-muted">Matching Skills</p>
                            </div>
                            <div class="col-md-4 text-center">
                                <h3 class="text-danger">${gapAnalysis.missing_skills.length}</h3>
                                <p class="text-muted">Missing Skills</p>
                            </div>
                            <div class="col-md-4 text-center">
                                <h3 class="text-primary">${gapAnalysis.match_percentage}%</h3>
                                <p class="text-muted">Match Rate</p>
                            </div>
                        </div>
                        
                        ${gapAnalysis.matching_skills.length > 0 ? `
                            <h6 class="text-success">✅ Skills You Have:</h6>
                            <div class="mb-3">
                                ${gapAnalysis.matching_skills.map(skill => 
                                    `<span class="badge bg-success me-1 mb-1">${skill}</span>`
                                ).join('')}
                            </div>
                        ` : ''}
                        
                        ${gapAnalysis.missing_skills.length > 0 ? `
                            <h6 class="text-danger">❌ Skills to Develop:</h6>
                            <div class="mb-3">
                                ${gapAnalysis.missing_skills.map(skill => 
                                    `<span class="badge bg-danger me-1 mb-1">${skill}</span>`
                                ).join('')}
                            </div>
                        ` : ''}
                        
                        ${gapAnalysis.extra_skills.length > 0 ? `
                            <h6 class="text-info">💡 Additional Skills You Have:</h6>
                            <div class="mb-3">
                                ${gapAnalysis.extra_skills.map(skill => 
                                    `<span class="badge bg-info me-1 mb-1">${skill}</span>`
                                ).join('')}
                            </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('skillGapModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('skillGapModal'));
    modal.show();
}

// Show loading state
function showLoading() {
    loadingSection.classList.remove('d-none');
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
    
    // Scroll to loading section
    loadingSection.scrollIntoView({ behavior: 'smooth' });
}

// Hide loading state
function hideLoading() {
    loadingSection.classList.add('d-none');
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = '<i class="fas fa-cogs me-2"></i>Analyze Resume';
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Find a good place to show the alert
    const alertContainer = document.querySelector('.container');
    if (alertContainer) {
        alertContainer.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const alert = alertContainer.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
}

// Get alert icon based on type
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Smooth scroll functions
function scrollToUpload() {
    document.getElementById('upload').scrollIntoView({ behavior: 'smooth' });
}

function scrollToFeatures() {
    document.getElementById('features').scrollIntoView({ behavior: 'smooth' });
}

// Utility function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
