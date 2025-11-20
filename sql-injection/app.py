from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'chave-super-secreta-workshop-2024'

# Configuração do banco de dados
DATABASE = 'banco.db'

def init_db():
    """Inicializa o banco de dados com dados de exemplo"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Cria tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            balance REAL NOT NULL
        )
    ''')
    
    # Limpa dados existentes
    cursor.execute('DELETE FROM users')
    
    # Insere usuários de exemplo - ADMIN PRIMEIRO!
    users = [
        ('admin', 'admin2024!', 'admin', 50000.00),
        ('eu', 'mypass123', 'user', 1500.00),
        ('pessoaMuitoMuitoRica', 'supersecret999', 'vip', 9850000.00)
    ]
    
    cursor.executemany(
        'INSERT INTO users (username, password, role, balance) VALUES (?, ?, ?, ?)',
        users
    )
    
    conn.commit()
    conn.close()
    print("✓ Banco de dados inicializado com sucesso!")

@app.route('/')
def index():
    """Redireciona para a página de login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login vulnerável a SQL Injection"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # VULNERÁVEL: Query SQL sem sanitização (propositalmente para o workshop)
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        
        print(f"\n🔍 Query SQL executada: {query}\n")
        
        try:
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Detecção de SQL Injection para mostrar alerta
            sql_injection_detected = (
                ("'" in username and ("OR" in username.upper() or "--" in username)) or
                ("--" in username)
            )
            
            # COMPORTAMENTO REALISTA: fetchone() retorna o primeiro resultado
            # Se for SQL Injection com OR 1=1, retorna o PRIMEIRO do banco (admin)
            user = cursor.fetchone()
            
            conn.close()
            
            if user:
                # Login bem-sucedido
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                session['sql_injected'] = sql_injection_detected
                
                if sql_injection_detected:
                    print(f"⚠️  SQL INJECTION DETECTADA! Retornou primeiro usuário: {user['username']}")
                
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Credenciais inválidas')
                
        except sqlite3.Error as e:
            print(f"❌ Erro SQL: {e}")
            return render_template('login.html', error=f'Erro no banco de dados: {str(e)}')
    
    return render_template('login.html', error=None)

@app.route('/dashboard')
def dashboard():
    """Dashboard principal - requer autenticação"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Se for admin, mostra todos os usuários
    if session.get('role') == 'admin':
        cursor.execute('SELECT * FROM users ORDER BY balance DESC')
    else:
        # Usuário comum vê apenas sua própria conta
        cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    
    users = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', 
                         users=users, 
                         current_user=session['username'],
                         role=session['role'],
                         sql_injected=session.get('sql_injected', False))

@app.route('/transfer', methods=['POST'])
def transfer():
    """Transfere dinheiro entre contas"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    amount = float(request.form.get('amount', 0))
    from_user = request.form.get('from_user', session['username'])
    to_user = request.form.get('to_user', '')
    
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Valor inválido'}), 400
    
    if not to_user:
        return jsonify({'success': False, 'message': 'Selecione um destinatário'}), 400
    
    if from_user == to_user:
        return jsonify({'success': False, 'message': 'Não pode transferir para si mesmo'}), 400
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Verifica se o usuário tem permissão para transferir desta conta
        if session.get('role') != 'admin' and from_user != session['username']:
            return jsonify({'success': False, 'message': 'Você só pode transferir da sua própria conta'}), 403
        
        # Verifica saldo do usuário de origem
        cursor.execute('SELECT balance FROM users WHERE username = ?', (from_user,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'success': False, 'message': 'Conta de origem não encontrada'}), 400
        
        source_balance = result[0]
        
        if amount > source_balance:
            return jsonify({'success': False, 'message': 'Saldo insuficiente'}), 400
        
        # Verifica se o destinatário existe
        cursor.execute('SELECT username FROM users WHERE username = ?', (to_user,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Destinatário não encontrado'}), 400
        
        # Realiza a transferência
        cursor.execute('UPDATE users SET balance = balance - ? WHERE username = ?', (amount, from_user))
        cursor.execute('UPDATE users SET balance = balance + ? WHERE username = ?', (amount, to_user))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'Transferência de R$ {amount:,.2f} realizada com sucesso!'})
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logout')
def logout():
    """Faz logout do usuário"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Inicializa o banco de dados
    if not os.path.exists(DATABASE):
        print("🔧 Criando banco de dados...")
        init_db()
    
    print("\n" + "="*50)
    print("🚀 SERVIDOR INICIADO!")
    print("="*50)
    print("📍 Acesse: http://127.0.0.1:5000")
    print("\n💡 CREDENCIAIS PARA TESTE:")
    print("   Normal: eu / mypass123")
    print("   Admin: admin / admin2024!")
    print("\n🎯 SQL INJECTION PAYLOAD:")
    print("   Usuário: admin' OR '1'='1' --")
    print("   Senha: (qualquer coisa)")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)