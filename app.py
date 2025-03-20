from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Thread, Comment
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
db.init_app(app)

# Инициализация базы данных (создание таблиц)
with app.app_context():
    db.create_all()

# Главная страница
@app.route('/')
def index():
    threads = Thread.query.all()
    return render_template('index.html', threads=threads)

# Страница для создания нового треда
@app.route('/create_thread', methods=['GET', 'POST'])
def create_thread():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']  # Получаем ник

        # Проверка, что ник не пустой и не равен "Admin"
        if not author:
            return render_template('create_thread.html', error="Ник не может быть пустым!")
        if author.lower() == 'admin':
            return render_template('create_thread.html', error="Ник 'Admin' нельзя использовать!")

        thread = Thread(title=title, content=content, author=author, created_at=datetime.now())
        db.session.add(thread)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('create_thread.html')


# Страница для просмотра треда и добавления комментариев
@app.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
def thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    comments = Comment.query.filter_by(thread_id=thread.id).all()

    if request.method == 'POST':
        content = request.form['content']
        author = 'Аноним'
        new_comment = Comment(content=content, author=author, created_at=datetime.now(), thread_id=thread.id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('thread', thread_id=thread.id))  # Перезагружаем страницу с новыми комментариями

    return render_template('thread.html', thread=thread, comments=comments)

# Страница для входа в админку
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'Admin1456':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Неверный логин или пароль!', 'danger')
    
    return render_template('admin_login.html')

# Страница админ-панели
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('admin_login'))  # Если не авторизован, перенаправляем на страницу логина

    threads = Thread.query.all()
    comments = Comment.query.all()  # Получаем все комментарии, чтобы отображать их в админке
    return render_template('admin_dashboard.html', threads=threads, comments=comments)


# Удаление треда
@app.route('/delete_thread/<int:id>')
def delete_thread(id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))  # Если не авторизован, перенаправляем на страницу логина
    thread = Thread.query.get(id)
    db.session.delete(thread)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


# Логика выхода из админки
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)  # Удаляем информацию о том, что админ авторизован
    return redirect(url_for('index'))  # Перенаправляем на главную страницу

# Создание комментария
@app.route('/create_comment/<int:thread_id>', methods=['POST'])
def create_comment(thread_id):
    content = request.form['content']
    author = request.form['author']  # Получаем ник автора

    # Проверка, что ник не равен "Admin"
    if author.lower() == 'admin':
        return redirect(url_for('thread', thread_id=thread_id))  # Перенаправляем на тред без создания комментария

    comment = Comment(content=content, author=author, created_at=datetime.now(), thread_id=thread_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('thread', thread_id=thread_id))  # Перезагружаем страницу с новыми комментариями


@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('admin_login'))  # Если не авторизован, перенаправляем на страницу логина

    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))  # Перенаправляем обратно на панель админа



if __name__ == '__main__':
    app.run(debug=True)

