from PVL import db
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta

categorizados = db.Table(
    'categorizados',
    db.Column('livro_id', db.Integer, db.ForeignKey('livros.id')),
    db.Column('genero_id', db.Integer, db.ForeignKey('genero.id')))

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=False)
    nome_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(20), nullable=False)
    imagem = db.Column(db.String(100), default= 'padrao.png')
    postagens = db.relationship("Postagem", backref='usuario', lazy=True)
    biografia = db.Column(db.String(200), default='Alterar biografia')
    livros = db.relationship("Livros", backref='usuario',lazy=True)
    amigos = db.relationship("Amigo", backref='usuario', lazy=True)
    notificacoes = db.relationship("Notificacao", backref='usuario', lazy=True)

class Livros(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    imagem = db.Column(db.String(100), default= '')
    status = db.Column(db.String(100), nullable=True)
    preco = db.Column(db.Float, default = 0.0)
    dano = db.Column(db.String(150), nullable=True)
    condicao = db.Column(db.String(500), nullable=True)
    resumo = db.Column(db.String(500), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable = False)
    generos = db.relationship('Genero', secondary=categorizados, backref=db.backref('livros', lazy='dynamic'))

class Postagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.String(400), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable = False)
    imagem = db.Column(db.String(100), default= '')
    curtidas = db.Column(db.Integer, default = 0)
    data = db.Column(db.DateTime, default=datetime.now(tz=timezone(-timedelta(hours=3))))

class ForumLivro(db.Model):
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable = False)
    id = db.Column(db.Integer, primary_key=True)
    id_livro = db.Column(db.Integer, db.ForeignKey('livros.id'), nullable = False)
    texto = db.Column(db.String(250), nullable = False)
    respostas = db.relationship("Resposta", backref='forumlivro',lazy=True)
    data = db.Column(db.DateTime, default=datetime.now(tz=timezone(-timedelta(hours=3))))

class Genero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable = False)
    livro = db.relationship('Livros', secondary=categorizados, backref=db.backref('genero', lazy='dynamic'))

class Resposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_forum = db.Column(db.Integer, db.ForeignKey(ForumLivro.id), nullable = False)
    id_usuario = db.Column(db.Integer, db.ForeignKey(Usuario.id), nullable = False)
    id_livro = db.Column(db.Integer, db.ForeignKey(Livros.id), nullable = False)
    texto = db.Column(db.String(250), nullable = False)
    data = db.Column(db.DateTime, default=datetime.now(tz=timezone(-timedelta(hours=3))))

class Amigo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey(Usuario.id), nullable = False)
    id_amigo = db.Column(db.Integer, nullable = False)

class ForumIndividual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey(Usuario.id), nullable = False)
    id_amigo = db.Column(db.Integer, nullable = False)
    last_post = db.Column(db.DateTime)

class ForumSolo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, nullable = False)

class MensagemSolo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(250), nullable = False)
    data = db.Column(db.DateTime, default=datetime.now(tz=timezone(-timedelta(hours=3))))
    imagem = db.Column(db.String(100), default= '')
    id_usuario = db.Column(db.Integer, nullable = False)


class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable = False)
    usu_notificou = db.Column(db.Integer, nullable = False)
    id_livro = db.Column(db.Integer, nullable=False)
    conteudo = db.Column(db.String(100), nullable = False)

class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_forumind = db.Column(db.Integer, db.ForeignKey(ForumIndividual.id), nullable = False)
    id_usuario = db.Column(db.Integer, nullable = False)
    texto = db.Column(db.String(250), nullable = False)
    data = db.Column(db.DateTime, default=datetime.now(tz=timezone(-timedelta(hours=3))))
    imagem = db.Column(db.String(100), default= '')