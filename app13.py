from flask import Flask, redirect, url_for, session, flash, render_template, request, jsonify
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import datetime, timedelta
import traceback

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Saurabh_Agrahari@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SQLALCHEMY_ECHO'] = True

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Enable insecure transport for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Google OAuth configuration
google_bp = make_google_blueprint(
    client_id="937501692060-um02o9hulkt2njtcejh9ps5avllfa3ov.apps.googleusercontent.com",
    client_secret="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",
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

# Models
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(120), nullable=False)
    semester = db.Column(db.String(80), nullable=False)
    semester_number = db.Column(db.Integer, nullable=False)
    enrolled_students = db.Column(db.Integer, nullable=False)
    faculty_name = db.Column(db.String(120), nullable=False)
    faculty_email = db.Column(db.String(120), nullable=False)

class Grade(db.Model):
    __tablename__ = 'grades'
    grade_id = db.Column(db.Integer, primary_key=True)
    student_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    upload_id = db.Column(db.Integer, db.ForeignKey('grade_uploads.id'), nullable=False)
    assessment_type = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=True)
    out_of = db.Column(db.Integer, nullable=False)
    hidden = db.Column(db.Boolean, default=False)
    notified = db.Column(db.Boolean, default=False)

class GradeUpload(db.Model):
    __tablename__ = 'grade_uploads'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    professor_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)

# Helper functions
def generate_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    date = datetime.now().strftime("%Y%m%d")
    return f"{base}_{date}{ext}"

def validate_csv(df):
    expected_columns = ['email', 'course_name', 'semester', 'semester_number', 'faculty_name', 'faculty_email', 'assessment_type', 'score', 'out_of', 'enrolled_students']
    if not all(col in df.columns for col in expected_columns):
        missing_columns = [col for col in expected_columns if col not in df.columns]
        raise ValueError(f"CSV is missing required columns: {', '.join(missing_columns)}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash('Failed to fetch user information from Google.', 'danger')
        return redirect(url_for('index'))

    info = resp.json()
    email = info['email']
    full_name = info['name']
    role = 'student' if 'su-' in email else 'professor'

    user = User.query.filter_by(email=email).first()

    if user:
        user.full_name = full_name
        user.role = role
    else:
        user = User(role=role, full_name=full_name, email=email)
        db.session.add(user)

    db.session.commit()

    session['user'] = {
        'email': email,
        'full_name': full_name,
        'role': role
    }

    if role == 'student':
        return redirect(url_for('student_dashboard'))
    else:
        return redirect(url_for('professor_dashboard'))

@app.route('/professor_dashboard', methods=['GET', 'POST'])
def professor_dashboard():
    if 'user' not in session or session['user']['role'] != 'professor':
        flash('Please log in as a professor to access the dashboard.', 'warning')
        return redirect(url_for('index'))

    uploads = GradeUpload.query.filter_by(professor_email=session['user']['email']).all()

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(file)
                validate_csv(df)
                
                unique_filename = generate_unique_filename(file.filename)
                new_upload = GradeUpload(filename=unique_filename, professor_email=session['user']['email'])
                db.session.add(new_upload)
                db.session.flush()

                for index, row in df.iterrows():
                    app.logger.info(f"Processing row {index}: {row}")
                    
                    student = User.query.filter_by(email=row['email']).first()
                    if not student:
                        student = User(email=row['email'], full_name="Unknown", role="student")
                        db.session.add(student)
                        app.logger.info(f"Created new student: {student.email}")

                    course = Course.query.filter_by(
                        course_name=row['course_name'], 
                        semester=row['semester'],
                        semester_number=int(row['semester_number']),
                        faculty_email=row['faculty_email']
                    ).first()

                    if not course:
                        course = Course(
                            course_name=row['course_name'],
                            semester=row['semester'],
                            semester_number=int(row['semester_number']),
                            enrolled_students=int(row['enrolled_students']),
                            faculty_name=row['faculty_name'],
                            faculty_email=row['faculty_email']
                        )
                        db.session.add(course)
                        app.logger.info(f"Created new course: {course.course_name}")
                    else:
                        course.enrolled_students = int(row['enrolled_students'])
                        app.logger.info(f"Updated existing course: {course.course_name}")

                    db.session.flush()

                    grade = Grade(
                        student_email=student.email,
                        course_id=course.id,
                        upload_id=new_upload.id,
                        assessment_type=row['assessment_type'],
                        score=int(row['score']) if row['score'] else None,
                        out_of=int(row['out_of']),
                        notified=False
                    )
                    db.session.add(grade)
                    app.logger.info(f"Created grade for student {student.email}, course {course.course_name}")

                db.session.commit()
                app.logger.info(f"Successfully uploaded and processed file: {file.filename}")
                app.logger.info("Database session committed successfully")
                flash('File successfully uploaded and grades saved.', 'success')
            
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error processing file: {str(e)}")
                app.logger.error(traceback.format_exc())
                flash(f"An error occurred while processing the file: {str(e)}", 'danger')

            return redirect(url_for('professor_dashboard'))

    return render_template('professor_dashboard.html', uploads=uploads)

@app.route('/semester_grades')
def semester_grades():
    if 'user' not in session or session['user']['role'] != 'student':
        flash('Please log in as a student to access the grades.', 'warning')
        return redirect(url_for('index'))

    semester = request.args.get('semester')
    email = session['user']['email']
    
    grades = Grade.query.join(Course).filter(
        Grade.student_email == email,
        Grade.hidden == False,
        Course.semester == semester
    ).all()
    
    grade_data = []
    total_score = 0
    total_out_of = 0
    
    for grade in grades:
        course = Course.query.get(grade.course_id)
        percentage = (grade.score / grade.out_of) * 100 if grade.score is not None else 0
        grade_data.append({
            'course_name': course.course_name,
            'assessment_type': grade.assessment_type,
            'score': grade.score,
            'out_of': grade.out_of,
            'percentage': percentage
        })
        total_score += grade.score if grade.score is not None else 0
        total_out_of += grade.out_of
    
    student_average = (total_score / total_out_of) * 100 if total_out_of > 0 else 0

    # Calculate class average and student ranking
    class_grades = Grade.query.join(Course).filter(
        Course.semester == semester,
        Grade.hidden == False
    ).all()
    
    class_total_score = sum(g.score for g in class_grades if g.score is not None)
    class_total_out_of = sum(g.out_of for g in class_grades)
    class_average = (class_total_score / class_total_out_of) * 100 if class_total_out_of > 0 else 0

    # Calculate how many students the current student is performing better than
    better_than_count = sum(1 for g in class_grades if (g.score / g.out_of) * 100 < student_average)
    total_students = len(set(g.student_email for g in class_grades))

    return render_template('semester_grades.html', 
                           semester=semester, 
                           grades=grade_data, 
                           student_average=student_average, 
                           class_average=class_average,
                           better_than_count=better_than_count,
                           total_students=total_students)

@app.route('/display_grades')
def display_grades():
    if 'user' not in session or session['user']['role'] != 'professor':
        flash('Please log in as a professor to access this page.', 'warning')
        return redirect(url_for('index'))

    upload_id = request.args.get('upload_id')
    app.logger.info(f"Displaying grades for upload ID: {upload_id}")

    if upload_id:
        grades = Grade.query.filter_by(upload_id=upload_id).all()
        app.logger.info(f"Number of grades retrieved: {len(grades)}")
        grade_data = []
        for grade in grades:
            student = User.query.filter_by(email=grade.student_email).first()
            course = Course.query.filter_by(id=grade.course_id).first()
            grade_data.append({
                'student_name': student.full_name if student else 'Unknown',
                'student_email': grade.student_email,
                'course_name': course.course_name if course else 'Unknown',
                'assessment_type': grade.assessment_type,
                'score': grade.score,
                'out_of': grade.out_of
            })
            app.logger.info(f"Processed grade for student: {grade.student_email}")
        
        app.logger.info(f"Total processed grades: {len(grade_data)}")
        return render_template('display_grades.html', grades=grade_data)
    else:
        app.logger.warning("No upload ID provided")
        flash('No upload ID provided', 'warning')
        return redirect(url_for('professor_dashboard'))

@app.route('/student_dashboard')
def student_dashboard():
    if 'user' not in session or session['user']['role'] != 'student':
        flash('Please log in as a student to access the dashboard.', 'warning')
        return redirect(url_for('index'))

    return render_template('student_dashboard.html', user=session['user'])

@app.route('/get_grades')
def get_grades():
    if 'user' not in session or session['user']['role'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401

    email = session['user']['email']
    grades = Grade.query.filter_by(student_email=email, hidden=False).all()
    grade_data = []
    for grade in grades:
        course = Course.query.filter_by(id=grade.course_id).first()
        grade_data.append({
            'grade_id': grade.grade_id,
            'course_name': course.course_name if course else 'Unknown',
            'assessment_type': grade.assessment_type,
            'score': grade.score,
            'out_of': grade.out_of,
            'semester': course.semester if course else 'Unknown',
            'semester_number': course.semester_number if course else 0
        })
    
    return jsonify({'data': grade_data})

@app.route('/get_notifications')
def get_notifications():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    email = session['user']['email']
    latest_grade = Grade.query.filter_by(student_email=email, notified=False).order_by(Grade.upload_id.desc()).first()
    
    if latest_grade:
        course = Course.query.get(latest_grade.course_id)
        notification = {
            'id': latest_grade.grade_id,
            'message': f"A new grade for {course.course_name} ({latest_grade.assessment_type}) has been uploaded.",
            'timestamp': latest_grade.upload_id  # Using upload_id as a proxy for timestamp
        }
        return jsonify({'notification': notification})
    else:
        return jsonify({'notification': None})

@app.route('/mark_grade_notified', methods=['POST'])
def mark_grade_notified():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    grade_id = data.get('grade_id')

    grade = Grade.query.get(grade_id)
    if grade and grade.student_email == session['user']['email']:
        grade.notified = True
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Grade not found'}), 404

@app.route('/hide_grade', methods=['POST'])
def hide_grade():
    if 'user' not in session or session['user']['role'] != 'student':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    grade_id = data.get('grade_id')

    if not grade_id:
        return jsonify({'success': False, 'message': 'Invalid grade ID'}), 400

    grade = Grade.query.filter_by(grade_id=grade_id, student_email=session['user']['email']).first()

    if not grade:
        return jsonify({'success': False, 'message': 'Grade not found or not authorized to hide'}), 404

    try:
        grade.hidden = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Grade hidden successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logout')
def logout():
    if google.authorized:
        token = google_bp.token["access_token"]
        resp = google.post(
            "https://accounts.google.com/o/oauth2/revoke",
            params={"token": token},
            headers={"content-type": "application/x-www-form-urlencoded"}
        )
        if resp.ok:
            flash('Successfully logged out of Google account.', 'success')
        else:
            flash('Failed to revoke token. You may need to manually log out from Google.', 'danger')

    session.pop('user', None)
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Internal Server Error: {str(e)}")
    app.logger.error(traceback.format_exc())
    flash('An internal error occurred. Please try again later.', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)