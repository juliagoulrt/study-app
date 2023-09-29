from flask import Flask

def create_app(): #cria a função
    app = Flask(__name__)
    app.config['SECRET KEY'] = 'lahskw2374yrj' #proteger os cookies e dados da aplicação
    
    #importando os blueprints
    from .auth import auth
    from .models import models
    
    #registrando os blueprints
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(models, url_prefix="/")
    
    return app