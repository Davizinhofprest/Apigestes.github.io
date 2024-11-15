from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid

# Inicializando o Flask e o banco de dados
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///verify.db'  # Banco de dados SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definindo o modelo de dados para armazenar as verificações
class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    verified = db.Column(db.Boolean, default=False)

# Criar o banco de dados
# Se o banco já existir, não recriar.
with app.app_context():
    db.create_all()

# Rota para gerar o token de verificação e salvar no banco
@app.route('/generate_token', methods=['POST'])
def generate_token():
    user_id = request.json.get('user_id')  # Obtém o ID do usuário
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Gera um token único
    token = str(uuid.uuid4())

    # Cria um registro no banco de dados com o ID do usuário, token e status de verificação
    new_verification = Verification(user_id=user_id, token=token)
    db.session.add(new_verification)
    db.session.commit()

    return jsonify({"status": "success", "token": token}), 200

# Rota para verificar se o usuário foi verificado
@app.route('/verify', methods=['GET'])
def verify_user():
    token = request.args.get('token')  # Obtém o token fornecido
    if not token:
        return jsonify({"error": "Token is required"}), 400

    # Procura no banco pelo token
    verification = Verification.query.filter_by(token=token).first()

    if verification:
        if verification.verified:
            return jsonify({"status": "success", "user_id": verification.user_id, "verified": True}), 200
        else:
            return jsonify({"status": "pending", "user_id": verification.user_id, "verified": False}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid token"}), 400

# Rota para marcar o usuário como verificado
@app.route('/mark_verified', methods=['POST'])
def mark_verified():
    token = request.json.get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400

    # Encontra o usuário com o token fornecido
    verification = Verification.query.filter_by(token=token).first()

    if verification:
        verification.verified = True  # Marca como verificado
        db.session.commit()
        return jsonify({"status": "success", "user_id": verification.user_id, "verified": True}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid token"}), 400

# Inicia a aplicação Flask
if __name__ == '__main__':
    app.run(debug=True)
