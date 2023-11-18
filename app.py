from flask import Flask
from views import views

app = Flask(__name__)

secret_key = "d62ce1e2e4a17b84cc3d6171f3dcfe81"
app.secret_key =secret_key

app.static_folder = 'static' 
app.static_url_path = '/static'

app.register_blueprint(views)

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)
