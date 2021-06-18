from PVL import db, create_app
from PVL.entidades import Amigo, Usuario, ForumIndividual, Mensagem
from sqlalchemy import desc, or_

meu = create_app()
with meu.app_context():
    teste = "EAE PESSOAS"

    forum = ForumIndividual.query.filter(or_(ForumIndividual.id_amigo == 1, ForumIndividual.id_amigo == 4)).filter(or_(ForumIndividual.id_usuario == 4, ForumIndividual.id_usuario == 1)).all()


    print(forum)