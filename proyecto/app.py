from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secret_key'  # Cambia esto a una clave secreta fuerte
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Asegúrate de que esta línea está en tu modelo
    loans = db.relationship('Loan', backref='user', lazy=True)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)


# Crear la base de datos
with app.app_context():
    db.create_all()

# Página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin'))

        # Verificación de usuarios normales
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('user_page', user_id=user.id))
        else:
            flash('Usuario o contraseña incorrectos. Intenta de nuevo.')
    return render_template('login.html')


# Página del superadministrador
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        loan_amount = request.form['loan_amount']
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        if loan_amount:
            new_loan = Loan(user_id=new_user.id, amount=float(loan_amount))
            db.session.add(new_loan)
            db.session.commit()

        flash('Usuario creado exitosamente.')
        return redirect(url_for('admin'))

    users = User.query.all()
    return render_template('admin.html', users=users)

# Página del usuario
@app.route('/user/<int:user_id>')
def user_page(user_id):
    user = User.query.get_or_404(user_id)
    loans = Loan.query.filter_by(user_id=user.id).all()
    return render_template('user.html', user=user, loans=loans)

if __name__ == '__main__':
    app.run(debug=True)
