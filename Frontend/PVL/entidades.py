from PVL import db
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(20), nullable=False)
    postagens = db.relationship("Postagem", backref='usuario', lazy=True)
    livros = db.relationship("Livros", backref='usuario',lazy=True)

class Livros(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    genero = db.Column(db.String(50), nullable=False)
    resumo = db.Column(db.String(500), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable = False)

class Postagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.String(250), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable = False)
    imagem = db.Column(db.String(100), default= '')
    data = db.Column(db.DateTime, default=datetime.now(tz=timezone(-timedelta(hours=3))))
