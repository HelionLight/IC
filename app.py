from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuração do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'titi020205'
app.config['MYSQL_DB'] = 'bancoIC'
app.secret_key = 'sua_chave_secreta'  # Adicione uma chave secreta para usar o flash

mysql = MySQL(app)

# Função para verificar usuário no banco de dados
def verificar_usuario_no_banco(email, password):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    if user:
        print(f"Usuário encontrado: {user}")  # Debug
        if check_password_hash(user[3], password):  # Supondo que a senha seja a quarta coluna
            return user
        else:
            print("Senha incorreta.")  # Debug
    else:
        print("Usuário não encontrado.")  # Debug
    return None

# Função para carregar usuario
def carregar_usuario(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    return user

# Função para obter datasets
#def obter_datasets():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM datasets")  # Ajuste esta consulta conforme sua tabela
    datasets = cur.fetchall()
    cur.close()
    return datasets

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
            session['user_id'] = user[0]  # Supondo que o ID do usuário seja o primeiro elemento
            return redirect(url_for('dashboard'))
        else:
            flash('Login inválido. Verifique suas credenciais.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('As senhas não coincidem', 'danger')
            return redirect(url_for('register'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            flash('Este email já está em uso', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO usuarios (full_name, email, senha) VALUES (%s, %s, %s)", (full_name, email, hashed_password))
        mysql.connection.commit()
        cur.close()  # Fechar o cursor após a operação
        flash('Conta criada com sucesso', 'success')
        return redirect(url_for('login'))
    
    return render_template('registrar.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar o dashboard', 'warning')
        return redirect(url_for('login'))
    
    user = carregar_usuario(session['user_id'])
    #datasets = obter_datasets()  # Obter os datasets
    print(f"Usuário carregado: {user}")  # Debug
    return render_template('dashboard.html', user=user,)# Passar datasets para o template

@app.route('/usuarios')
def usuarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    all_users = cur.fetchall()
    cur.close()
    return render_template('usuarios.html', users=all_users)

@app.route('/excluir_usuario/<int:user_id>')
def excluir_usuario(user_id):
    cur = mysql.connection.cursor()
    cur .execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    flash('Usuário excluído com sucesso', 'success')
    return redirect(url_for('usuarios'))

@app.route('/editar_usuario/<int:user_id>', methods=['GET', 'POST'])
def editar_usuario(user_id):
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('As senhas não coincidem', 'danger')
            return redirect(url_for('editar_usuario', user_id=user_id))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s AND id != %s", (email, user_id))
        user = cur.fetchone()

        if user:
            flash('Este email já está em uso', 'danger')
            return redirect(url_for('editar_usuario', user_id=user_id))

        hashed_password = generate_password_hash(password)
        cur.execute("UPDATE usuarios SET full_name = %s, email = %s, senha = %s WHERE id = %s", (full_name, email, hashed_password, user_id))
        mysql.connection.commit()
        cur.close()  # Fechar o cursor após a operação
        flash('Usuário editado com sucesso', 'success')
        return redirect(url_for('usuarios'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    return render_template('editar_usuario.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)