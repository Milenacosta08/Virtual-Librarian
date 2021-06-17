from PVL import db, create_app
from PVL.entidades import Amigo, Usuario, ForumIndividual, Mensagem

meu = create_app()
with meu.app_context():
    teste = "EAE PESSOAS"

    novo = ForumIndividual()
    novo.id_usuario = 123
    novo.id_amigo = 321
    novo.texto = "teste"
    db.session.add(novo)
    db.session.commit()

    msg = Mensagem()
    msg.texto = teste
    db.session.add(msg)
    db.session.commit()

    novo.mensagens.append(msg)
    novo.mensagens.append(ForumIndividual())
    db.session.commit()

    teste = ForumIndividual.query.filter(ForumIndividual.id_usuario == 123).first()


    print(teste.mensagens[0].texto)