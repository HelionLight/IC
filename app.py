from flask import Flask, render_template, redirect, url_for, session, flash, request

app = Flask(__name__)

# Função para verificar usuário no banco de dados
def verificar_usuario_no_banco(email, password):
    # Simulando uma consulta ao banco de dados
    usuarios = [
        {'id': 1, 'email': 'user1@example.com', 'senha': 'password1'},
        {'id': 2, 'email': 'user2@example.com', 'senha': 'password2'}
    ]
    for user in usuarios:
        if user['email'] == email and user['senha'] == password:
            return user
    return None

# Função para carregar usuario
def carregar_usuario(user_id):
    # Simulando uma consulta ao banco de dados
    usuarios = [
        {'id': 1, 'email': 'user1@example.com'},
        {'id': 2, 'email': 'user2@example.com'}
    ]
    for user in usuarios:
        if user['id'] == user_id:
            return user
    return None

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
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash('Login inválido. Verifique suas credenciais.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Simulando a inserção de dados no banco de dados
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))
    return render_template('registrar.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar o dashboard', 'warning')
        return redirect(url_for('login'))
    
    user = carregar_usuario(session['user_id'])
    return render_template('dashboard.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
