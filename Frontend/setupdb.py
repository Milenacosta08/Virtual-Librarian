from PVL import db, create_app

meu = create_app()
with meu.app_context():
    db.drop_all(app=meu)
    db.create_all(app=meu)
