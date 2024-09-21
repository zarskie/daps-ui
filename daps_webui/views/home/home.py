from flask import Blueprint, render_template

# from daps_webui import daps_logger


home = Blueprint("home", __name__)


@home.route("/", methods=["GET", "POST"])
def home_route():
    my_name = "Jack"

    # daps_logger.info("REFRESHING RIGHT NOW!")

    return render_template("home/index.html", my_name=my_name)

