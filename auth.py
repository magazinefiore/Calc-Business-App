import bcrypt
import database as db

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_initial_admin():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        admin_pass = hash_password("admin123")
        cursor.execute("""
        INSERT INTO users (username, password_hash, name, email, role)
        VALUES (?, ?, ?, ?, ?)
        """, ("admin", admin_pass, "Administrador LM", "contato@lmimporting2u.com", "Administrador"))
        conn.commit()
        db.log_audit("Sistema", "Criação de Usuário Padrão", "Usuário 'admin' criado com sucesso.")
    conn.close()

def authenticate_user(username, password):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password(password, user['password_hash']):
        return dict(user)
    return None

def register_user(username, password, name, email, role, admin_username):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        hashed_p = hash_password(password)
        cursor.execute("""
        INSERT INTO users (username, password_hash, name, email, role)
        VALUES (?, ?, ?, ?, ?)
        """, (username, hashed_p, name, email, role))
        conn.commit()
        db.log_audit(admin_username, "Novo Usuário Cadastrado", f"Usuário: {username} ({role})")
        return True, "Usuário cadastrado com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar usuário (Nome de usuário já existe?): {str(e)}"
    finally:
        conn.close()