from quart import Blueprint


main = Blueprint("maindir", __name__)


@main.route("/")
def get():
    return "up"
