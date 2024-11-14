from flask import Flask, render_template, redirect, url_for, session, flash, request
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuração do banco de dados
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'ic'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'IC'
app.secret_key = 'sua_chave_secreta'  # Adicione uma chave secreta para usar o flash

# Função para conectar ao banco de dados
def conectar_banco():
    try:
        return pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
    except pymysql.MySQLError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
    
# Função para verificar usuário no banco de dados
def verificar_usuario_no_banco(email, senha):
    connection = conectar_banco()
    if connection is None:
        return None  # Retorna None se a conexão falhar

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
    finally:
        cursor.close()  # Fecha o cursor
        connection.close()  # Fecha a conexão

    if user and check_password_hash(user[3], senha):  # user[3] é a senha
        return user  # Retorna a tupla do usuário
    return None

# Função para carregar usuario
def carregar_usuario(user_id):
    connection = conectar_banco()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/funcionalidades')
def funcionalidades():
    return render_template('funcio.html')

@app.route('/ferramentas')
def ferramentas():
    return render_template('ferramentas.html')

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

        connection = conectar_banco()
        if connection is None:
            flash('Erro ao conectar ao banco de dados.', 'danger')
            return redirect(url_for('home'))  # Redireciona para a página inicial ou outra página

        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (full_name, email, senha, tipo_usuario) VALUES (%s, %s, %s, %s)", 
                           (full_name, email, hashed_password, 'aluno'))
            connection.commit()
            flash('Registro de aluno realizado com sucesso!', 'success')
            return redirect(url_for('login'))  # Redireciona para a página inicial ou outra página
        except Exception as e:
            connection.rollback()
            flash('Erro ao registrar aluno: {}'.format(str(e)), 'danger')
        finally:
            cursor.close()  # Fecha o cursor
            connection.close()  # Fecha a conexão

    return render_template('registrar_aluno.html')

@app.route('/register/administrador', methods=['GET', 'POST'])
def registrar_administrador():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request .form['password']
        hashed_password = generate_password_hash(password)

        connection = conectar_banco()
        if connection is None:
            flash('Erro ao conectar ao banco de dados.', 'danger')
            return redirect(url_for('home'))  # Redireciona para a página inicial ou outra página
        
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (full_name, email, senha, tipo_usuario) VALUES (%s, %s, %s, %s)", 
                           (full_name, email, hashed_password, 'administrador'))
            connection.commit()
            flash('Registro de administrador realizado com sucesso!', 'success')
            return redirect(url_for('login'))  # Redireciona para a página inicial ou outra página
        except Exception as e:
            connection.rollback()
            flash('Erro ao registrar administrador: {}'.format(str(e)), 'danger')
        finally:
            cursor.close()
            connection.close()
    
    return render_template('registrar_administrador.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = verificar_usuario_no_banco(email, password)
        if user:
            session['user_id'] = user[0]  # Supondo que o ID do usuário seja o primeiro elemento
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
    
    if user[4] == 'aluno':  # user[4] é o tipo de usuário
        return redirect(url_for('dashboard_aluno'))
    elif user[4] == 'administrador':
        return redirect(url_for('dashboard_administrador'))
    
    flash('Tipo de usuário desconhecido', 'danger')
    return redirect(url_for('home'))

@app.route('/dashboard/aluno')
def dashboard_aluno():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar o dashboard', 'warning')
        return redirect(url_for('login'))
    
    user = carregar_usuario(session['user_id'])
    return render_template('dashboard_aluno.html', user=user)

@app.route('/dashboard/administrador')
def dashboard_administrador():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar o dashboard', 'warning')
        return redirect(url_for('login'))
    
    user = carregar_usuario(session['user_id'])
    return render_template('dashboard_administrador.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você foi desconectado com sucesso!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)