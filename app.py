from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(200), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)

class StudentScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

@app.route('/')
def home():
    is_admin = request.args.get('admin') == 'true'
    return render_template('home.html', is_admin=is_admin)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        name = request.form['name']
        score = 0
        for question in Question.query.all():
            selected_option = request.form.get(str(question.id))
            if selected_option == question.correct_option:
                score += 1
        student_score = StudentScore(name=name, score=score)
        db.session.add(student_score)
        db.session.commit()
        return redirect(url_for('result', name=name))

    questions = Question.query.all()
    return render_template('quiz.html', questions=questions)

@app.route('/result')
def result():
    name = request.args.get('name')
    student = StudentScore.query.filter_by(name=name).first()
    return render_template('result.html', name=student.name, score=student.score)

@app.route('/scores', methods=['GET', 'POST'])
def scores():
    if request.method == 'POST':
        if 'reset' in request.form:
            StudentScore.query.delete()
            db.session.commit()
        return redirect(url_for('scores'))

    students = StudentScore.query.all()
    return render_template('scores.html', students=students)

@app.route('/manage_questions', methods=['GET', 'POST'])
def manage_questions():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            question_text = request.form['question_text']
            option_a = request.form['option_a']
            option_b = request.form['option_b']
            option_c = request.form['option_c']
            option_d = request.form['option_d']
            correct_option = request.form['correct_option']
            new_question = Question(
                question_text=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option
            )
            db.session.add(new_question)
            db.session.commit()
        elif action == 'edit':
            question_id = int(request.form['question_id'])
            question = Question.query.get(question_id)
            question.question_text = request.form['question_text']
            question.option_a = request.form['option_a']
            question.option_b = request.form['option_b']
            question.option_c = request.form['option_c']
            question.option_d = request.form['option_d']
            question.correct_option = request.form['correct_option']
            db.session.commit()
        elif action == 'delete':
            question_id = int(request.form['question_id'])
            question = Question.query.get(question_id)
            db.session.delete(question)
            db.session.commit()

    questions = Question.query.all()
    return render_template('manage_questions.html', questions=questions)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Question.query.first():
            sample_questions = [
                Question(question_text='What is the keyword used to define a function in Python?', option_a='func', option_b='def', option_c='function', option_d='define', correct_option='B'),
                Question(question_text='Which of the following is a mutable data type in Python?', option_a='tuple', option_b='string', option_c='list', option_d='int', correct_option='C'),
                Question(question_text='What is the output of print(2 ** 3)?', option_a='6', option_b='8', option_c='9', option_d='None of the above', correct_option='B'),
                Question(question_text='Which of the following is used to handle exceptions in Python?', option_a='try-except', option_b='if-else', option_c='for-while', option_d='do-while', correct_option='A'),
                Question(question_text='What is the correct file extension for Python files?', option_a='.pyth', option_b='.pt', option_c='.py', option_d='.p', correct_option='C')
            ]
            db.session.bulk_save_objects(sample_questions)
            db.session.commit()
    app.run(debug=True)