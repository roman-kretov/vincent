from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pN8YdLyM42OCA4eTXp73lA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Doctor.query.get(int(user_id))

class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(200), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Doctor.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    patients = Patient.query.filter_by(doctor_id=current_user.id).all()
    return render_template('dashboard.html', patients=patients)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if username already exists
        user_exists = Doctor.query.filter_by(username=username).first() is not None

        if user_exists:
            flash('Username already exists.')
            return redirect(url_for('register'))
        else:
            new_doctor = Doctor(username=username)
            new_doctor.set_password(password)
            db.session.add(new_doctor)
            db.session.commit()
            flash('Doctor registered successfully.')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        condition = request.form.get('condition')

        new_patient = Patient(name=name, age=age, condition=condition, doctor_id=current_user.id)
        db.session.add(new_patient)
        db.session.commit()
        flash('New patient added successfully.')
        return redirect(url_for('dashboard'))

    return render_template('add_patient.html')



with app.app_context():
    db.create_all()