from flask import current_app as app, render_template, request, redirect, url_for, session
from PVL.entidades import Usuario, Livros, Postagem, Genero, categorizados, ForumLivro, Resposta, Amigo, ForumIndividual, Notificacao, Mensagem, ForumSolo, MensagemSolo
from PVL import db, login_manager
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc, or_
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta


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
@login_required
def feed():

    posts = {}
    postagens = Postagem.query.order_by(desc(Postagem.id)).all()

    for post in postagens:
        pessoa = Usuario.query.get(post.usuario_id)
        posts[post] = {'nome': pessoa.nome, 'sobrenome': pessoa.sobrenome, 'conteudo': post.conteudo, 'data': post.data, 'idpostagem': post.id, 'curtidas': post.curtidas, 'imagem': pessoa.imagem, 'idusuario': pessoa.id}


    return render_template('feed.html', postagem = posts)


@app.route('/feed-post', methods=['POST'])
@login_required
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

            file.save(app.config['UPLOAD_FOLDER']+'/'+filename)
            postagem.imagem = filename

    if postagem.conteudo is not None:
        db.session.add(postagem)
        db.session.commit()

    return redirect('/feed')

@app.route('/curtir/<idpostagem>')
@login_required
def curtir(idpostagem):

    postagem = Postagem.query.filter_by(id = idpostagem).first()

    postagem.curtidas += 1
    db.session.commit()

    return redirect('/feed')

@app.route('/descurtir/<idpostagem>')
@login_required
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
@login_required
def perfil():
    post = Postagem.query.filter_by(usuario_id=session['user_id']).order_by(desc(Postagem.id)).all()
    noti = Notificacao.query.filter_by(id_user = current_user.id).order_by(desc(Notificacao.id)).all()
    notificacoes = []

    for n in noti:
        usu = Usuario.query.get(n.usu_notificou)
        livro = Livros.query.get(n.id_livro)
        notificacoes.append({'usuario':usu, 'notificacao':n, 'livro':livro})


    return render_template("perfil.html", postagens = post, notificacoes = notificacoes)


@app.route('/perfil/<id_usuario>')
@login_required
def perfil_usu(id_usuario):
    amigo = Amigo.query.filter(Amigo.id_usuario == current_user.id).filter(Amigo.id_amigo == id_usuario).all()
    existe = 1

    if amigo == []:
        existe = 0


    usu = Usuario.query.filter_by(id=id_usuario).first()
    post = Postagem.query.filter_by(usuario_id=id_usuario).order_by(desc(Postagem.id)).all()

    return render_template("perfil.html", usuario = usu, postagens=post, existe = existe)


@app.route('/delete')
@login_required
def deletarUsuario():
    user = Usuario.query.get(current_user.id)
    mensagens = Mensagem.query.filter(Mensagem.id_usuario == current_user.id).all()
    amigos = Amigo.query.filter(Amigo.id_usuario == current_user.id).all()
    forumindividual = ForumIndividual.query.filter(ForumIndividual.id_usuario == current_user.id).all()
    resposta = Resposta.query.filter(Resposta.id_usuario == current_user.id).all()
    forumlivro = ForumLivro.query.filter(ForumLivro.usuario_id == current_user.id).all()
    forumsolo = ForumSolo.query.filter(ForumSolo.id_usuario == current_user.id).all()
    mensagem = MensagemSolo.query.filter(MensagemSolo.id_usuario == current_user.id).all()

    for postagem in user.postagens:
        db.session.delete(postagem)
        db.session.commit()

    for notificacao in user.notificacoes:
        db.session.delete(notificacao)
        db.session.commit()

    for forumlivro in forumlivro:
        forumlivro.respostas.clear()
        db.session.commit()

        db.session.delete(forumlivro)
        db.session.commit()

    for forum in forumsolo:
        db.session.delete(forum)
        db.session.commit()

    for msg in mensagem:
        db.session.delete(msg)
        db.session.commit()

    for resposta in resposta:
        db.session.delete(resposta)
        db.session.commit()


    for livro in user.livros:
        livro.generos.clear()
        db.session.commit()

        db.session.delete(livro)
        db.session.commit()

    for forumindividual in forumindividual:
        db.session.delete(forumindividual)
        db.session.commit()

    for amigo in amigos:
        db.session.delete(amigo)
        db.session.commit()

    for mensagem in mensagens:
        db.session.delete(mensagem)
        db.session.commit()

    db.session.delete(user)
    db.session.commit()

    return redirect('/login')


@app.route('/adicionar/<idamigo>')
@login_required
def amigo(idamigo):
    amigo = Amigo.query.filter(Amigo.id_amigo == idamigo).filter(Amigo.id_usuario == current_user.id).all()

    if current_user.id != idamigo:
        if amigo == []:
            novo = Amigo()
            novo.id_usuario = current_user.id
            novo.id_amigo = idamigo
            db.session.add(novo)
            db.session.commit()

    return redirect(f"/perfil/{idamigo}")

@app.route('/remover/<idamigo>')
@login_required
def removeramigo(idamigo):
    Amigo.query.filter(Amigo.id_amigo == idamigo).filter(Amigo.id_usuario == current_user.id).delete()

    db.session.commit()

    return redirect(f"/perfil/{idamigo}")


@app.route('/estante/<string:stt>/<id_user>')
@login_required
def estante(stt, id_user):
    session['status'] = stt

    usu = Usuario.query.get(id_user)
    livros = Livros.query.filter_by(usuario_id = id_user).filter(Livros.status==stt).all()

    exemplar = {}

    for livro in livros:
        exemplar[livro] = {'titulo': livro.titulo, 'autor': livro.autor, 'status':livro.status, 'genero': livro.generos, 'idlivro': livro.id, 'capa':livro.imagem}


    if usu.id != current_user.id:
        id_user = usu.id

        return render_template("estante.html", livros = exemplar, usuario = id_user, status = stt)
    else:
        return render_template("estante.html", livros = exemplar, status = stt)


@app.route('/delete/<id>')
@login_required
def deletarLivro(id):
    user = Usuario.query.get(current_user.id)
    livro = Livros.query.get(id)

    if livro.usuario_id == current_user.id:
        livro.generos.clear()
        db.session.commit()

        db.session.delete(livro)
        db.session.commit()

    return redirect(f"/estante/{session['status']}/{user.id}")


@app.route('/livro-cadastrado', methods=['POST'])
@login_required
def livro_cadastrado():
    titulo = request.form["titulo"]
    autor = request.form["autor"]
    genero = request.form.getlist('genero')
    resumo = request.form["resumo"]
    status = request.form["status"]
    preco = request.form["preco"]
    condicao = request.form["condicao"]

    usu = Usuario.query.get(current_user.id)

    livro = Livros()
    livro.titulo = titulo
    livro.autor = autor
    livro.resumo = resumo
    livro.usuario_id = usu.id
    livro.status = status
    livro.preco = preco
    livro.condicao = condicao

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


    file2 = request.files['imagemsel2']

    if file2 is not None:
        if file2 and allowed_file(file2.filename):
            filename2 = secure_filename(file2.filename)

            imgs2 = os.listdir(app.config['UPLOAD_FOLDER'])
            filename2 = f'{len(imgs2)+1:08}.{filename2.rsplit(".", 1)[1].lower()}'

            file2.save(app.config['UPLOAD_FOLDER']+'/'+filename2)
            livro.dano = filename2


    db.session.add(livro)
    db.session.commit()

    return redirect(f"/estante/{session['status']}/{usu.id}")

#return render_template("estante.html", livros = livros[:8], titulo = titulo)

@app.route('/livros/<id_livro>')
@login_required
def paglivros(id_livro):
    livro = Livros.query.filter_by(id=id_livro).first()
    usuario = Usuario.query.filter_by(id= livro.usuario_id).first()
    forum = ForumLivro.query.filter_by(id_livro = id_livro).order_by(desc(ForumLivro.id)).all()
    respostas = Resposta.query.filter_by(id_livro = id_livro).order_by(desc(Resposta.data)).all()
    posts = {}
    respostass = {}

    for resposta in respostas:
        usu = Usuario.query.get(resposta.id_usuario)
        respostass[resposta] = {'texto' : resposta.texto, 'idforum' : resposta.id_forum, 'usuario' : usu, 'data' : resposta.data}


    for comentario in forum:
        pessoa = Usuario.query.get(comentario.usuario_id)
        posts[comentario] = {'nome': pessoa.nome, 'sobrenome': pessoa.sobrenome, 'conteudo': comentario.texto, 'id': comentario.id, 'data': comentario.data, 'idlivro': comentario.id_livro, 'imagem': pessoa.imagem, 'idusuario': pessoa.id}


    return render_template('item1.html', livro = livro, usuario = usuario, posts = posts, respostas = respostass)

@app.route('/livros/<id_livro>/resenha', methods=['POST'])
@login_required
def livroresenha(id_livro):
    comentario = request.form['resenha']
    livro = Livros.query.get(id_livro)
    usu = Usuario.query.filter_by(email=session['user_email']).first()

    postagem = Postagem()
    postagem.conteudo = f'Resenha do livro "{livro.titulo}": {comentario}'
    postagem.usuario_id = usu.id
    postagem.imagem = livro.imagem

    if postagem.conteudo is not None:
        db.session.add(postagem)
        db.session.commit()

    return redirect(f'/livros/{id_livro}')



@app.route('/forum/cadastro/<id_li>', methods=['POST'])
@login_required
def Forum(id_li):
    comentario = request.form['comentario']

    if comentario != '':
        novo = ForumLivro()
        novo.usuario_id = current_user.id
        novo.id_livro = id_li
        novo.texto = comentario

        db.session.add(novo)
        db.session.commit()

    return redirect(f'/livros/{id_li}')

@app.route('/delete/forum/<idcomentario>/<idliv>', methods=['POST'])
@login_required
def deletarforum(idcomentario, idliv):

    respostas = Resposta.query.filter(Resposta.id_forum == idcomentario).all()

    for resposta in respostas:
        db.session.delete(resposta)
        db.session.commit()

    ForumLivro.query.filter_by(id = idcomentario).delete()

    db.session.commit()

    return redirect(f'/livros/{idliv}')



@app.route('/forum/cadastro/resposta/<id_livro>/<usu_post>', methods=['POST'])
@login_required
def resposta(id_livro, usu_post):
    resposta = request.form['resposta']

    if resposta != '':
        novo = Resposta()
        novo.id_usuario = current_user.id
        novo.id_livro = id_livro
        novo.id_forum = usu_post
        novo.texto = resposta

        db.session.add(novo)
        db.session.commit()

    return redirect(f'/livros/{id_livro}')


@app.route('/buscas')
@login_required
def buscas():
    busca = request.args.get('pesquisass')
    livros = Livros.query.filter(or_(Livros.titulo.ilike(f'%{busca}%'), Livros.autor.ilike(f'%{busca}%'))).all()
    usuarios = Usuario.query.filter(Usuario.nome_completo.ilike(f'%{busca}%')).all()

    return render_template('buscas.html', busca = busca, livros = livros, usuarios = usuarios)


@app.route('/amigos/<id_usu>')
@login_required
def amigos(id_usu):
    amigos = Amigo.query.filter(Amigo.id_usuario == id_usu).all()
    amigoss = []

    for amigo in amigos:
        if amigo != []:
            usu = Usuario.query.get(amigo.id_amigo)
            amigoss.append({'usuario' : usu})

    return render_template('amigos.html', amigos = amigoss)

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('home'))

@app.route('/atualiza', methods=['POST'])
@login_required
def atualiza():
    novo_nome = request.form['nome_novo']
    novo_sobrenome = request.form['sobrenome_novo']
    novo_email = request.form['email_novo']
    nova_senha = request.form['senha_nova']
    senha_inserida = request.form['senha_atual']

    quem = Usuario.query.get(current_user.id)

    if(quem.senha==senha_inserida):

        if(novo_nome!=""):
            quem.nome = novo_nome


        if(novo_sobrenome!=""):
            quem.sobrenome = novo_sobrenome


        if(novo_email!=""):
            quem.email = novo_email


        if(nova_senha!=""):
            quem.senha = nova_senha

        db.session.add(quem)
        db.session.commit()
        return redirect ('/perfil')

    else:
        erro = 'Alterações não concluídas pois a senha inserida é inválida!'
        return render_template('perfil.html', erro=erro)

@app.route('/atualizardg', methods=['POST'])
@login_required
def atualizardg():
    biografia = request.form['biografia']
    file = request.files['imagemsel']

    usuario = Usuario.query.get(current_user.id)
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

@app.route("/forum")
@login_required
def forumsolo():
    forum = ForumSolo.query.filter(ForumSolo.id_usuario == current_user.id).all()

    if forum == []:
        novo = ForumSolo()
        novo.id_usuario = current_user.id
        db.session.add(novo)
        db.session.commit()

    mensagens = MensagemSolo.query.filter(MensagemSolo.id_usuario == current_user.id).all()
    posts = []
    for mensagem in mensagens:
        usuario = Usuario.query.get(mensagem.id_usuario)
        posts.append({'usuario' : usuario, 'postagem' : mensagem})

    lista = ForumIndividual.query.filter(ForumIndividual.id_usuario == current_user.id).all()
    listamg = []
    amigoreal = 0
    idamigo = 0


    for resultado in lista:
        if resultado.id != "":
            if resultado.id_usuario == current_user.id:
                pessoa = Usuario.query.get(resultado.id_amigo)
                listamg.append({'usuario' : pessoa})

    return render_template('forumind.html', amigo = amigoreal, idamigo = idamigo, amigos = listamg, posts = posts)

@app.route("/forum/post", methods=['POST'])
@login_required
def postsolo():
    comentario = request.form['comentario']
    forum = ForumSolo.query.filter(ForumSolo.id_usuario == current_user.id).all()

    if forum != []:
        msg = MensagemSolo()
        msg.id_usuario = current_user.id
        msg.texto = comentario
        msg.data = datetime.now(tz=timezone(-timedelta(hours=3)))

        file = request.files['imagemsel']

        if file is not None:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                imgs = os.listdir(app.config['UPLOAD_FOLDER'])
                filename = f'{len(imgs)+1:08}.{filename.rsplit(".", 1)[1].lower()}'

                file.save(app.config['UPLOAD_FOLDER']+'/'+filename)
                msg.imagem = filename

        if msg.texto is not None:
            db.session.add(msg)
            db.session.commit()

            return redirect(f'/forum')

        else:
            return redirect('/feed')
    else:
        return redirect('/feed')


@app.route("/forum/<idamigo>/<idusuario>")
@login_required
def forumind(idamigo, idusuario):
    amigo = Usuario.query.filter(Usuario.id == idamigo).first()
    usuarioo = Usuario.query.filter(Usuario.id == idusuario).first()

    forum = ForumIndividual.query.filter(or_(ForumIndividual.id_amigo == amigo.id, ForumIndividual.id_amigo == usuarioo.id)).filter(or_(ForumIndividual.id_usuario == usuarioo.id, ForumIndividual.id_usuario == amigo.id)).all()

    if amigo is not None and usuarioo is not None and idamigo != idusuario:
        if forum == []:
            post = ForumIndividual()
            post.id_usuario = current_user.id
            post.id_amigo = amigo.id
            db.session.add(post)
            db.session.commit()

            novo = ForumIndividual()
            novo.id_usuario = amigo.id
            novo.id_amigo = current_user.id
            db.session.add(novo)
            db.session.commit()

        if amigo.id == current_user.id or usuarioo.id == current_user.id:
            #lista = Amigo.query.filter(Amigo.id_usuario == idusuario).order_by(Amigo.id).all()
            #lista = ForumIndividual.query.filter(ForumIndividual.id_usuario == current_user.id).all()
            amigoreal = Usuario.query.filter(Usuario.id == idamigo).first()
            forumteste = ForumIndividual.query.filter(or_(ForumIndividual.id_usuario == current_user.id, ForumIndividual.id_usuario == amigo.id)).order_by(desc(ForumIndividual.last_post)).all()
            listamg = []
            posts = []


            if forum != []:
                for foru in forum:
                    mensagens = Mensagem.query.filter(Mensagem.id_forumind == foru.id).all()

                    for postagem in mensagens:
                        usuario = Usuario.query.get(postagem.id_usuario)
                        posts.append({'usuario' : usuario, 'postagem' : postagem})




            for amigos in forumteste:
                if amigos.id != "":
                    if amigos.id_usuario == current_user.id:
                        pessoa = Usuario.query.get(amigos.id_amigo)
                        listamg.append({'usuario' : pessoa})


            if amigo is not None:
                return render_template('forumind.html', amigo = amigoreal, idamigo = idamigo, posts = posts, amigos = listamg)
            else:
                return redirect('/feed')
        else:
            return redirect('/feed')
    else:
        return redirect('/feed')



@app.route("/forum/<idamigo>/post", methods=['POST'])
@login_required
def forumpost(idamigo):
    comentario = request.form['comentario']
    amigo = Usuario.query.get(idamigo)

    forum = ForumIndividual.query.filter(or_(ForumIndividual.id_amigo == amigo.id, ForumIndividual.id_amigo == current_user.id)).filter(or_(ForumIndividual.id_usuario == current_user.id, ForumIndividual.id_usuario == amigo.id)).all()

    if forum != []:
        msg = Mensagem()

        for foru in forum:
            if foru.id != msg.id_forumind:
                msg.id_forumind = foru.id

            foru.last_post = datetime.now(tz=timezone(-timedelta(hours=3)))
            db.session.commit()


        msg.id_usuario = current_user.id
        msg.texto = comentario
        msg.data = datetime.now(tz=timezone(-timedelta(hours=3)))

        file = request.files['imagemsel']

        if file is not None:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                imgs = os.listdir(app.config['UPLOAD_FOLDER'])
                filename = f'{len(imgs)+1:08}.{filename.rsplit(".", 1)[1].lower()}'

                file.save(app.config['UPLOAD_FOLDER']+'/'+filename)
                msg.imagem = filename

        if msg.texto is not None:
            db.session.add(msg)
            db.session.commit()

            return redirect(f'/forum/{idamigo}/{current_user.id}')

        else:
            return redirect('/feed')
    else:
        return redirect('/feed')



@app.route("/notificacao/<string:noti>/<idlivro>")
@login_required
def notificar(noti, idlivro):
    livro = Livros.query.filter_by(id=idlivro).first()
    user_notificou = Usuario.query.get(current_user.id)
    usu = Usuario.query.filter_by(id=livro.usuario_id).first()

    if noti == "Desejo":
        notificacao = f'deseja o livro'
    else:
        notificacao = f'sinalizou que tem o livro'

    nova = Notificacao()
    nova.id_user = usu.id
    nova.usu_notificou = user_notificou.id
    nova.conteudo = notificacao
    nova.id_livro = livro.id

    db.session.add(nova)
    db.session.commit()

    return redirect(f'/livros/{livro.id}')

@app.route('/delete/notificacao/<id>')
@login_required
def deletar_notificacao(id):
    notificacao = Notificacao.query.get(id)

    if notificacao.id_user == current_user.id:
        db.session.delete(notificacao)
        db.session.commit()

    return redirect("/perfil")


