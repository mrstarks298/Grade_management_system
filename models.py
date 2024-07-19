# from datetime import datetime
# from extensions import db

# class User(db.Model):
#     __tablename__ = 'users'
#     user_id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True)
#     role = db.Column(db.String(20), nullable=False)
#     full_name = db.Column(db.String(120), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)

#     def __init__(self, username=None, role=None, full_name=None, email=None):
#         self.username = username or f'user_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
#         self.role = role
#         self.full_name = full_name
#         self.email = email

#     def __repr__(self):
#         return f'<User {self.username}>'

# class Course(db.Model):
#     __tablename__ = 'courses'
#     id = db.Column(db.Integer, primary_key=True)
#     course_name = db.Column(db.String(120), nullable=False)
#     semester = db.Column(db.String(80), nullable=False)
#     semester_number = db.Column(db.Integer, nullable=False)
#     enrolled_students = db.Column(db.Integer, nullable=False)
#     faculty_name = db.Column(db.String(120), nullable=False)
#     faculty_email = db.Column(db.String(120), unique=True, nullable=False)

#     def __repr__(self):
#         return f'<Course {self.course_name}>'

# class Grade(db.Model):
#     __tablename__ = 'grades'
#     grade_id = db.Column(db.Integer, primary_key=True)
#     student_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
#     course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
#     marks = db.Column(db.String(20), nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)

#     student = db.relationship('User', backref='grades')
#     course = db.relationship('Course', backref='grades')

#     def __repr__(self):
#         return f'<Grade {self.grade_id}>'



# from datetime import datetime
# from extensions import db

# class User(db.Model):
#     __tablename__ = 'users'
#     user_id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True)
#     role = db.Column(db.String(20), nullable=False)
#     full_name = db.Column(db.String(120), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)

#     def __init__(self, username=None, role=None, full_name=None, email=None):
#         self.username = username or f'user_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
#         self.role = role
#         self.full_name = full_name
#         self.email = email

#     def __repr__(self):
#         return f'<User {self.username}>'

# class Course(db.Model):
#     __tablename__ = 'courses'
#     id = db.Column(db.Integer, primary_key=True)
#     course_name = db.Column(db.String(120), nullable=False)
#     semester = db.Column(db.String(80), nullable=False)
#     semester_number = db.Column(db.Integer, nullable=False)
#     enrolled_students = db.Column(db.Integer, nullable=False)
#     faculty_name = db.Column(db.String(120), nullable=False)
#     faculty_email = db.Column(db.String(120), nullable=False)

#     def __repr__(self):
#         return f'<Course {self.course_name}>'

# class Grade(db.Model):
#     __tablename__ = 'grades'
#     grade_id = db.Column(db.Integer, primary_key=True)
#     student_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
#     course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
#     marks = db.Column(db.String(20), nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)

#     student = db.relationship('User', backref='grades')
#     course = db.relationship('Course', backref='grades')

#     def __repr__(self):
#         return f'<Grade {self.grade_id}>'


# class Grade(db.Model):
#     __tablename__ = 'grades'
#     grade_id = db.Column(db.Integer, primary_key=True)
#     student_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
#     course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
#     assessment_type = db.Column(db.String(100), nullable=False)  # 'internal' or 'final'
#     score = db.Column(db.Integer, nullable=True)  # For internal assessments
#     grade = db.Column(db.String(2), nullable=True)  # For final grades
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)

#     student = db.relationship('User', backref='grades')
#     course = db.relationship('Course', backref='grades')

#     def __repr__(self):
#         return f'<Grade {self.grade_id}>'


from datetime import datetime
from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, username=None, role=None, full_name=None, email=None):
        self.username = username or f'user_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
        self.role = role
        self.full_name = full_name
        self.email = email

    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(120), nullable=False)
    semester = db.Column(db.String(80), nullable=False)
    semester_number = db.Column(db.Integer, nullable=False)
    enrolled_students = db.Column(db.Integer, nullable=False)
    faculty_name = db.Column(db.String(120), nullable=False)
    faculty_email = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<Course {self.course_name}>'

class Grade(db.Model):
    __tablename__ = 'grades'
    grade_id = db.Column(db.Integer, primary_key=True)
    student_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    assessment_type = db.Column(db.String(100), nullable=False)  # 'internal' or 'final'
    score = db.Column(db.Integer, nullable=True)  # For internal assessments
    grade = db.Column(db.String(2), nullable=True)  # For final grades
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref='grades')
    course = db.relationship('Course', backref='grades')

    def __repr__(self):
        return f'<Grade {self.grade_id}>'
