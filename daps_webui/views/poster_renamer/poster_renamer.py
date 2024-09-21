from flask import Blueprint, render_template, request, jsonify
from daps_webui import db, models
from DapsEX.payload import Payload
from DapsEX.poster_renamerr import PosterRenamerr

poster_renamer = Blueprint("poster_renamer", __name__)


def get_instances(model: models) -> dict[str, list[str]]:
    instances = model.query.all()
    model_dict = {
        item.instance_name: {"url": item.url, "api": item.api_key} for item in instances
    }
    return model_dict


def create_poster_renamer_payload() -> Payload:
    radarr = get_instances(models.RadarrInstance())
    sonarr = get_instances(models.SonarrInstance())
    plex = get_instances(models.PlexInstance())

    settings = models.Settings.query.first()

    return Payload(
        source_dirs=settings.source_dirs.split(","),
        target_path=settings.target_path,
        asset_folders=settings.asset_folders,
        library_names=settings.library_names.split(","),
        instances=settings.instances.split(","),
        radarr=radarr,
        sonarr=sonarr,
        plex=plex,
    )


@poster_renamer.route("/poster_renamer", methods=["GET", "POST"])
def poster_renamer_route():
    return render_template("poster_renamer/poster_renamer.html")


@poster_renamer.route("/run-renamer", methods=["POST"])
def run_route():
    try:
        payload = create_poster_renamer_payload()
        print(f"{payload}", flush=True)
        renamer = PosterRenamerr(
            payload.target_path, payload.source_dirs, payload.asset_folders
        )
        renamer.run(payload)
        return jsonify({"success": True, "message": "Poster renamerr was successfull!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
