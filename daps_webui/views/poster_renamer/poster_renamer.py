from flask import Blueprint, render_template

poster_renamer = Blueprint("poster_renamer", __name__)

@poster_renamer.route("/poster_renamer")
def poster_renamer_route():
    return render_template("poster_renamer/poster_renamer.html")
