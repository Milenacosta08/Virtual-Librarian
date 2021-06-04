from flask import current_app as app, render_template, request, redirect, url_for, session
from PVL.entidades import Usuario, Livros, Postagem, Genero, categorizados, ForumLivro, Resposta
from PVL import db, login_manager
from flask_login import login_user, logout_user, login_required
from sqlalchemy import desc
import os
from werkzeug.utils import secure_filename


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
        posts[post] = {'nome': pessoa.nome, 'sobrenome': pessoa.sobrenome, 'conteudo': post.conteudo, 'data': post.data, 'idpostagem': post.id, 'curtidas': post.curtidas, 'imagem': pessoa.imagem, 'idusuario': pessoa.id}


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

@app.route('/<idusuario>/<idpostagem>')
def curtir(idusuario, idpostagem):

    postagem = Postagem.query.filter_by(id = idpostagem).first()

    postagem.curtidas += 1
    db.session.commit()

    return redirect('/feed')

@app.route('/<idpostagem>')
def descurtir(idpostagem):

    postagem = Postagem.query.filter_by(id = idpostagem).first()

    postagem.curtidas -= 1
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
            novo.nome_completo = '{} {}'.format(nome, sobrenome)
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
    post = Postagem.query.filter_by(usuario_id=session['user_id']).order_by(desc(Postagem.id)).all()

    return render_template("perfil.html", postagens = post)


@app.route('/perfil/<id_usuario>')
def perfil_usu(id_usuario):
    usu = Usuario.query.filter_by(id=id_usuario).first()
    post = Postagem.query.filter_by(usuario_id=id_usuario).order_by(desc(Postagem.id)).all()

    return render_template("perfil.html", usuario = usu, postagens=post)


@app.route('/pequeno-principe')
def item2():
    return render_template("item2.html")


@app.route('/estante/<user_id>')
def estante(user_id):
    livros = Livros.query.filter_by(usuario_id = user_id).all()

    exemplar = {}
    livro_id = {}

    for livro in livros:
        #if(livro.usuario_id==session['user_id']):
        exemplar[livro] = {'titulo': livro.titulo, 'autor': livro.autor, 'genero': livro.generos, 'idlivro': livro.id, 'capa':livro.imagem}
        livro_id[livro] = livro.id

    usu = Usuario.query.get(user_id)

    if usu.id != session['user_id']:
        id_user = usu.id

        return render_template("estante.html", livros = exemplar, livroid = livro_id, usuario = id_user)
    else:
        return render_template("estante.html", livros = exemplar, livroid = livro_id)


@app.route('/delete/<id_user>/<id>')
def deletarLivro(id_user, id):
    user = Usuario.query.get(id_user)
    livro = Livros.query.get(id)

    livro.generos.clear()
    db.session.commit()

    db.session.delete(livro)
    db.session.commit()

    return redirect(f'/estante/{user.id}')


@app.route('/livro-cadastrado/<id>', methods=['POST'])
def livro_cadastrado(id):
    titulo = request.form["titulo"]
    autor = request.form["autor"]
    genero = request.form.getlist('genero')
    resumo = request.form["resumo"]

    usu = Usuario.query.get(id)

    livro = Livros()
    livro.titulo = titulo
    livro.autor = autor
    livro.resumo = resumo
    livro.usuario_id = usu.id

    # percorre a lista "genero" que contém os gêneros selecionados pelo usuário
    for g in genero:
        genero1 = db.session.query(Genero).filter(Genero.nome == g).first()

        if genero1 is None:
            genero1 = Genero()
            genero1.nome = g
            db.session.add(genero1)
            db.session.commit()

        livro.generos.append(genero1)


    file = request.files['imagemsel']

    if file is not None:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            imgs = os.listdir(app.config['UPLOAD_FOLDER'])
            filename = f'{len(imgs)+1:08}.{filename.rsplit(".", 1)[1].lower()}'

            file.save(app.config['UPLOAD_FOLDER']+'/'+filename)
            livro.imagem = filename


        db.session.add(livro)
        db.session.commit()

    return redirect(f'/estante/{usu.id}')

#return render_template("estante.html", livros = livros[:8], titulo = titulo)

@app.route('/livros/<id_usuario>/<id_livro>')
def paglivros(id_usuario, id_livro):
    livro = Livros.query.filter_by(id=id_livro).first()
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    forum = ForumLivro.query.filter_by(id_livro = id_livro).order_by(desc(ForumLivro.id)).all()
    respostas = Resposta.query.all()
    posts = {}
    respostas = {}

    for resposta in respostas:
        respostas[resposta] = {'texto' : resposta.texto, 'idforum' : resposta.id_forum}


    for comentario in forum:
        pessoa = Usuario.query.get(comentario.usuario_id)
        posts[comentario] = {'nome': pessoa.nome, 'sobrenome': pessoa.sobrenome, 'conteudo': comentario.texto, 'id': comentario.id, 'data': comentario.data, 'idlivro': comentario.id_livro, 'imagem': pessoa.imagem, 'idusuario': pessoa.id}


    return render_template('item1.html', livro = livro, usuario = usuario, posts = posts, respostas = respostas)

@app.route('/forum/cadastro/<id_usu>/<id_li>', methods=['POST'])
def Forum(id_usu, id_li):
    comentario = request.form['comentario']
    livro = Livros.query.filter_by(usuario_id = id_usu).first()

    if comentario != '':
        novo = ForumLivro()
        novo.usuario_id = id_usu
        novo.id_livro = id_li
        novo.texto = comentario

        db.session.add(novo)
        db.session.commit()

    return redirect(f'/livros/{id_usu}/{id_li}')

@app.route('/forum/cadastro/resposta/<id_usu>/<id_livro>/<usu_post>', methods=['POST'])
def resposta(id_usu, id_livro, usu_post):
    resposta = request.form['resposta']

    if resposta != '':
        novo = Resposta()
        novo.id_forum = usu_post
        novo.texto = resposta

        db.session.add(novo)
        db.session.commit()

    return redirect(f'/livros/{id_usu}/{id_livro}')


@app.route('/buscas')
def buscas():
    existe = 0
    busca = request.args.get('pesquisass')
    nomes = Usuario.query.filter_by(nome = busca).all()
    sobrenomes = Usuario.query.filter_by(sobrenome = busca).all()
    livros = Livros.query.filter_by(titulo = busca).all()
    nomecomp = Usuario.query.filter_by(nome_completo = busca).all()

    if nomes or sobrenomes or livros or nomecomp:
        existe = 1

    return render_template('buscas.html', busca = busca, nomes = nomes, sobrenomes = sobrenomes, livros = livros, nomecomp = nomecomp, existe = existe)


@app.route('/amigos/<id>')
def amigo(id):
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

@app.route('/atualizardg/<int:id>', methods=['POST'])
def atualizardg(id):
    biografia = request.form['biografia']
    file = request.files['imagemsel']

    usuario = Usuario.query.get(id)
    if biografia != '':
        usuario.biografia = biografia

    if file is not None:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            imgs = os.listdir(app.config['UPLOAD_FOLDER'])
            filename = f'{len(imgs)+1:08}.{filename.rsplit(".", 1)[1].lower()}'

            file.save(app.config['UPLOAD_FOLDER']+'/'+filename)
            usuario.imagem = filename

    else:
        usuario.imagem = 'padrao'

    db.session.commit()

    return redirect ('/perfil')




