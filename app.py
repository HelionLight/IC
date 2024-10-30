from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:titi020205@localhost/bancoIC'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sua_chave_secreta'  # Adicione uma chave secreta para usar o flash

db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.Enum('aluno', 'administrador'), nullable=False)

# Função para verificar usuário no banco de dados
def verificar_usuario_no_banco(email, password):
    user = Usuario.query.filter_by(email=email).first()
    if user:
        if check_password_hash(user.password, password):
            return user
    return None

# Função para carregar usuario
def carregar_usuario(user_id):
    return Usuario.query.get(user_id)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/funcionalidades')
def funcionalidades():
    return render_template('funcio.html')

@app.route('/ferramentas')
def ferramentas():
    return render_template('ferramentas.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = verificar_usuario_no_banco(email, password)
        if user:
            session['user_id'] = user.id  # Supondo que o ID do usuário seja o primeiro elemento
            return redirect(url_for('dashboard'))  # Redireciona para a nova rota de dashboard
        else:
            flash('Login inválido. Verifique suas credenciais.', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar o dashboard', 'warning')
        return redirect(url_for('login'))
    
    user = carregar_usuario(session['user_id'])
    
    if user.tipo_usuario == 'aluno':
        return redirect(url_for('dashboard_aluno'))
    elif user.tipo_usuario == 'administrador':
        return redirect(url_for('dashboard_administrador'))
    
    flash('Tipo de usuário desconhecido', 'danger')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('registrar.html')

@app.route('/register/aluno', methods=['GET', 'POST'])
def registrar_aluno():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        novo_usuario = Usuario(full_name=full_name, email=email, password=hashed_password, tipo_usuario='aluno')

        try:
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Registro de aluno realizado com sucesso!', 'success')
            return redirect(url_for('home'))  # Redireciona para a página inicial ou outra página
        except Exception as e:
            db.session.rollback()
            flash('Erro ao registrar aluno: {}'.format(str(e)), 'danger')
    
    return render_template('registrar_aluno.html')

@app.route('/register/administrador', methods=['GET', 'POST'])
def registrar_administrador():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        novo_usuario = Usuario(full_name=full_name, email=email, password=hashed_password, tipo_usuario='administrador')

        try:
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Registro de administrador realizado com sucesso!', 'success')
            return redirect(url_for('home'))  # Redireciona para a página inicial ou outra página
        except Exception as e:
            db.session.rollback()
            flash('Erro ao registrar administrador: {}'.format(str(e)), 'danger')
    
    return render_template('registrar_administrador.html')

@app.route('/dashboard/aluno')
def dashboard_aluno():
    return render_template('dashboard_aluno.html')

@app.route('/dashboard/administrador')
def dashboard_administrador():
    return render_template('dashboard_administrador.html')

@app.route('/editar_usuario/<int:user_id>', methods=['GET', 'POST'])
def editar_usuario(user_id):
    user = carregar_usuario(user_id)
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        user.full_name = full_name
        user.email = email
        user.password = hashed_password

        try:
            db.session.commit()
            flash('Usuário editado com sucesso!', 'success')
            return redirect(url_for('dashboard'))  # Redireciona para a página de dashboard
        except Exception as e:
            db.session.rollback()
            flash('Erro ao editar usuário: {}'.format(str(e)), 'danger')
    
    return render_template('editar_usuario.html', user=user)

@app.route('/excluir_usuario/<int:user_id>')
def excluir_usuario(user_id):
    user = carregar_usuario(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Usuário excluído com sucesso!', 'success')
        return redirect(url_for('dashboard'))  # Redireciona para a página de dashboard
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir usuário: {}'.format(str(e)), 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você foi desconectado com sucesso!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)