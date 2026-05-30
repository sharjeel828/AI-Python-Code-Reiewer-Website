from datetime import datetime
from flask_login import UserMixin
from extensions import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    UserID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(150), nullable=False)
    Email = db.Column(db.String(150), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(256), nullable=False)
    Role = db.Column(db.String(50), default='user')
    submissions = db.relationship('Submission', backref='author', lazy=True)

    def get_id(self):
        return str(self.UserID)

class Submission(db.Model):
    __tablename__ = 'submissions'
    SubmissionID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    SourceCode = db.Column(db.Text, nullable=False)
    SubmissionDate = db.Column(db.DateTime, default=datetime.utcnow)
    FileName = db.Column(db.String(255), nullable=True)
    report = db.relationship('Report', backref='submission', uselist=False, lazy=True)

class Report(db.Model):
    __tablename__ = 'reports'
    ReportID = db.Column(db.Integer, primary_key=True)
    SubmissionID = db.Column(db.Integer, db.ForeignKey('submissions.SubmissionID'), nullable=False)
    DetectedIssues = db.Column(db.JSON, nullable=True)
    Metrics = db.Column(db.JSON, nullable=True)
    Suggestions = db.Column(db.JSON, nullable=True)
    CorrectedCode = db.Column(db.Text, nullable=True)

class ModelVersion(db.Model):
    __tablename__ = 'model_versions'
    ModelID = db.Column(db.Integer, primary_key=True)
    VersionNumber = db.Column(db.String(50), nullable=False)
    DeploymentDate = db.Column(db.DateTime, default=datetime.utcnow)
