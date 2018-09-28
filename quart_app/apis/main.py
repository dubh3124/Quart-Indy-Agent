from quart import Blueprint


main = Blueprint('main', __name__)

@main.route('/')
def get():
    return "up"