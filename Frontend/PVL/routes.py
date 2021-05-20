from flask import current_app as app, render_template, request, redirect, url_for, session
from PVL.entidades import Usuario, Livros, Postagem
from PVL import db, login_manager
from flask_login import login_user, logout_user, login_required
from sqlalchemy import desc
import os
from werkzeug.utils import secure_filename

livros = []

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(user_id)

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/feed')
def feed():

    posts = {}
    postagens = Postagem.query.order_by(desc(Postagem.id)).all()

    for post in postagens:
        pessoa = Usuario.query.get(post.usuario_id)
        posts[post] = {'nome': pessoa.nome, 'sobrenome': pessoa.sobrenome, 'conteudo': post.conteudo, 'data': post.data}


    return render_template('feed.html', postagem = posts)


@app.route('/feed-post', methods=['POST'])
def feed_post():
    comentario = request.form['comentario']
    usu = Usuario.query.filter_by(email=session['user_email']).first()

    postagem = Postagem()
    postagem.conteudo = comentario
    postagem.usuario_id = usu.id

    file = request.files['imagemsel']

    if file is not None:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            imgs = os.listdir(app.config['UPLOAD_FOLDER'])
            filename = f'{len(imgs)+1:08}.{filename.rsplit(".", 1)[1].lower()}'

            file.save(app.config['UPLOAD_FOLDER']+'/'+filename) # era aqui o problema. Tava "app.config['UPLOAD_FOLDER'], filename" aí ele tentava salvar na pasta PVL com o nome de uploads e dizia que uploads já é um diretório.
            postagem.imagem = filename

    if postagem.conteudo is not None:
        db.session.add(postagem)
        db.session.commit()


    return redirect('/feed')


@app.route('/cadastro')
def cadastro():
    return render_template("cadastro.html")


@app.route('/perfil-usuario', methods=['POST'])
def perfil_log():
    nome = request.form ['name']
    sobrenome = request.form ['lastname']
    email = request.form ['email']
    senha = request.form ['password']
    confirma_senha = request.form ['passconfirmation']

    if (Usuario.query.filter_by(email=email).first() is None):
        if (senha == confirma_senha):
            novo = Usuario()
            novo.nome = nome
            novo.sobrenome = sobrenome
            novo.email = email
            novo.senha = senha
            session['user_email'] = email

            db.session.add(novo)
            db.session.commit()

            login_user(novo)
            session['user_id'] = novo.id

            return render_template("perfil.html")
        else:
            erro = 'Senha no campo de confirmação escrita incorretamente!'

            return render_template('cadastro.html', erro = erro)
    else:
        erro = 'Email já cadastrado!'

        return render_template('cadastro.html', erro = erro)


@app.route('/dom-quixote')
def item1():
    return render_template("item1.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/feed-usuario', methods=['POST'])
def feed_log():
    email = request.form ['email']
    password = request.form['senha']

    usu = Usuario.query.filter_by(email=email).first()

    if (usu is None):
        erro = 'Usuário não encontrado'

        return render_template('login.html', erro = erro)
    else:
        if (usu.senha == password):
            login_user(usu)
            session['user_id'] = usu.id
            session['user_email'] = email
            return redirect('/feed')
        else:
            erro = 'Senha incorreta'
            return render_template('login.html', erro = erro)



@app.route('/perfil')
def perfil():
    return render_template("perfil.html")


@app.route('/pequeno-principe')
def item2():
    return render_template("item2.html")


@app.route('/estante')
def estante():
    livros = Livros.query.all()
    exemplar = {}
    livro_id = {}

    for livro in livros:
        if(livro.usuario_id==session['user_id']):
            #pessoa = Usuario.query.get(livro.usuario_id)
            exemplar[livro] = {'titulo': livro.titulo, 'autor': livro.autor, 'genero': livro.genero}
            livro_id[livro] = livro.id
    return render_template("estante.html", livros = exemplar, livroid = livro_id)


@app.route('/livro-cadastrado', methods=['POST'])
def livro_cadastrado():
    titulo = request.form["titulo"]
    autor = request.form["autor"]
    genero = request.form["genero"]
    resumo = request.form["resumo"]

    usu = Usuario.query.filter_by(email=session['user_email']).first()


    novo = Livros()
    novo.titulo = titulo
    novo.autor = autor
    novo.genero = genero
    novo.resumo = resumo
    novo.usuario_id = usu.id

    db.session.add(novo)
    db.session.commit()

    return redirect('/estante')

#return render_template("estante.html", livros = livros[:8], titulo = titulo)

@app.route('/livros/<id_usuario>/<id_livro>')
def paglivros(id_usuario, id_livro):
    livro = Livros.query.filter_by(id=id_livro).first()
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    return render_template('item1.html', livro = livro, usuario = usuario)


@app.route('/cadastrolivros')
def cadlivros():
    return render_template("cadastrolivros.html")


@app.route('/buscas')
def buscas():
    existe = 0
    busca = request.args.get('pesquisass')
    buscaz = busca.lower()
    sites = ["página inicial", "feed", "estante", "meu perfil", "dom quixote", "pequeno príncipe", "cadastro", "login"]
    links = ["/", "/feed", "/estante", "/perfil", "/dom-quixote", "/pequeno-principe", "/cadastro", "/login"]

    for item in range(8):
        if buscaz == sites[item]:
            existe = 1
            break

    return render_template('buscas.html', busca = buscaz, sites = sites, links = links, existe = existe)

@app.route('/amigos')
def amigo():
    return render_template('amigos.html')

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('home'))

@app.route('/atualiza/<int:id>', methods=['POST'])
def atualiza(id):
    novo_nome = request.form['nome_novo']
    novo_sobrenome = request.form['sobrenome_novo']
    novo_email = request.form['email_novo']
    nova_senha = request.form['senha_nova']
    senha_inserida = request.form['senha_atual']

    quem = Usuario.query.get(id)

    if(quem.senha==senha_inserida):

        if(novo_nome!=""):
            quem.nome = novo_nome
            db.session.add(quem)
            db.session.commit()

        if(novo_sobrenome!=""):
            quem.sobrenome = novo_sobrenome
            db.session.add(quem)
            db.session.commit()

        if(novo_email!=""):
            quem.email = novo_email
            db.session.add(quem)
            db.session.commit()

        if(nova_senha!=""):
            quem.senha = nova_senha
            db.session.add(quem)
            db.session.commit()
        return redirect ('/perfil')

    else:
        erro = 'Alterações não concluídas pois a senha inserida é inválida!'
        return render_template('perfil.html', erro=erro)






