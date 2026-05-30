from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import os

from extensions import db, login_manager
from models import User, Submission, Report, ModelVersion
from analyzer import analyze_code
from ml_module import predict_vulnerabilities, generate_corrected_code

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviewer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

db.init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
def setup_database():
    with app.app_context():
        db.create_all()
        # Create a mock model version if it doesn't exist
        if not ModelVersion.query.first():
            db.session.add(ModelVersion(VersionNumber="v1.0.0-mock"))
            db.session.commit()

# Ensure database is set up
setup_database()

# --- Auth Routes --- #

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(Email=email).first()
        if user_exists:
            flash('Email address already exists.', 'error')
            return redirect(url_for('register'))
        
        new_user = User(
            Name=name,
            Email=email,
            PasswordHash=generate_password_hash(password, method='scrypt')
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(Email=email).first()
        
        if not user or not check_password_hash(user.PasswordHash, password):
            flash('Please check your login details and try again.', 'error')
            return redirect(url_for('login'))
            
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page if next_page else url_for('index'))
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Main App Routes --- #

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Please log in to submit code for review.', 'warning')
            return redirect(url_for('login', next=request.url))
            
        source_code = ""
        filename = "pasted_code.py"
        
        # Check if file was uploaded
        if 'code_file' in request.files and request.files['code_file'].filename != '':
            file = request.files['code_file']
            allowed_extensions = ('.py', '.ipynb', '.pyw', '.pyi')
            if not file.filename.lower().endswith(allowed_extensions):
                flash('Invalid file type. Allowed formats: .py, .ipynb, .pyw, .pyi', 'error')
                return redirect(url_for('index'))
            
            # Read file content safely, max 1MB
            file_content = file.read(1024 * 1024)
            decoded_content = file_content.decode('utf-8', errors='replace')
            filename = file.filename
            
            if filename.lower().endswith('.ipynb'):
                import json
                try:
                    notebook_data = json.loads(decoded_content)
                    code_cells = []
                    for cell in notebook_data.get('cells', []):
                        if cell.get('cell_type') == 'code':
                            source = cell.get('source', [])
                            if isinstance(source, list):
                                code_cells.append("".join(source))
                            elif isinstance(source, str):
                                code_cells.append(source)
                    source_code = "\n\n# --- Jupyter Cell ---\n\n".join(code_cells)
                except Exception as e:
                    import logging
                    logging.error(f"Failed to parse ipynb: {str(e)}")
                    flash('Invalid or corrupt Jupyter Notebook (.ipynb) file.', 'error')
                    return redirect(url_for('index'))
            else:
                source_code = decoded_content
        else:
            # Check pasted code
            source_code = request.form.get('code_text', '')
            if not source_code.strip():
                flash('Please paste code or upload a file.', 'error')
                return redirect(url_for('index'))
                
        # 1. Save submission to DB
        submission = Submission(
            UserID=current_user.UserID,
            SourceCode=source_code,
            FileName=filename
        )
        db.session.add(submission)
        db.session.commit()
        
        # 2. Parse code and run analysis
        import ast
        import logging
        
        try:
            # Wrap AST parsing in try...except to catch SyntaxError and Exceptions
            ast.parse(source_code)
            
            # If parsing is successful, run our full analyzer
            analysis_results = analyze_code(source_code)
            
            # 3. Pass features to Mock ML module
            ml_predictions = predict_vulnerabilities(
                analysis_results["metrics"],
                analysis_results["issues"]
            )
            
            # 4. Combine results and save Report
            combined_issues = analysis_results["issues"] + ml_predictions["ml_detected_issues"]
            combined_suggestions = ml_predictions["suggestions"] + analysis_results["suggestions"]
            
            # Add risk score to metrics
            final_metrics = analysis_results["metrics"]
            final_metrics["risk_score"] = ml_predictions["risk_score"]
            
            corrected_code_text = generate_corrected_code(source_code, combined_issues)
            
            report = Report(
                SubmissionID=submission.SubmissionID,
                DetectedIssues=combined_issues,
                Metrics=final_metrics,
                Suggestions=combined_suggestions,
                CorrectedCode=corrected_code_text
            )
            
            db.session.add(report)
            db.session.commit()
            return redirect(url_for('view_report', report_id=report.ReportID))
            
        except SyntaxError as e:
            # Graceful Degradation: Skip AST metric extraction and reroute directly to LLM autocorrect
            logging.error(f"SyntaxError encountered inside submission {submission.SubmissionID}: {str(e)}")
            print(f"[ERROR] SyntaxError parsing code: {str(e)}")
            
            error_msg = f"SyntaxError: {str(e)}"
            detected_issues = [{"type": "SyntaxError", "severity": "error", "message": error_msg, "line": getattr(e, 'lineno', None)}]
            
            # Reroute directly to Auto-Correct
            corrected_code_text = generate_corrected_code(source_code, detected_issues)
            
            # Safe Return Payload
            report = Report(
                SubmissionID=submission.SubmissionID,
                DetectedIssues=detected_issues,
                Metrics={
                    "risk_score": 100, 
                    "cyclomatic_complexity": 0, 
                    "depth_of_nested_blocks": 0, 
                    "num_functions": 0, 
                    "num_loops": 0
                },
                Suggestions=["Structural metrics couldn't be calculated due to syntax errors."],
                CorrectedCode=corrected_code_text
            )
            db.session.add(report)
            db.session.commit()
            return redirect(url_for('view_report', report_id=report.ReportID))
            
        except Exception as e:
            # General Exception block just in case
            logging.error(f"Unexpected Exception encountered inside submission {submission.SubmissionID}: {str(e)}")
            print(f"[ERROR] Exception parsing code: {str(e)}")
            
            error_msg = f"Error: {str(e)}"
            detected_issues = [{"type": "Error", "severity": "error", "message": error_msg}]
            
            corrected_code_text = generate_corrected_code(source_code, detected_issues)
            
            report = Report(
                SubmissionID=submission.SubmissionID,
                DetectedIssues=detected_issues,
                Metrics={
                    "risk_score": 100, 
                    "cyclomatic_complexity": 0, 
                    "depth_of_nested_blocks": 0, 
                    "num_functions": 0, 
                    "num_loops": 0
                },
                Suggestions=["Structural metrics couldn't be calculated due to a parsing error."],
                CorrectedCode=corrected_code_text
            )
            db.session.add(report)
            db.session.commit()
            return redirect(url_for('view_report', report_id=report.ReportID))

    return render_template('index.html')

@app.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    report = Report.query.get_or_404(report_id)
    # Ensure user can only view their own reports
    if report.submission.UserID != current_user.UserID:
        flash('You do not have permission to view this report.', 'error')
        return redirect(url_for('index'))
        
    return render_template('report.html', report=report)

@app.route('/history')
@login_required
def history():
    submissions = Submission.query.filter_by(UserID=current_user.UserID).order_by(Submission.SubmissionDate.desc()).all()
    return render_template('history.html', submissions=submissions)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
 
