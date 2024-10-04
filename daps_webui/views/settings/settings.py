from flask import Blueprint, render_template, request, jsonify
from daps_webui import db, models
import requests

settings = Blueprint("settings", __name__)


@settings.route("/settings", methods = ["GET"])
def settings_route():
    return render_template("settings/settings.html")

@settings.route("/get-settings", methods=["GET"])
def get_settings():
    try:
        settings = models.Settings.query.first()
        radarr_instances = models.RadarrInstance.query.all()
        sonarr_instances = models.SonarrInstance.query.all()
        plex_instances = models.PlexInstance.query.all()

        data = {
            "targetPath": getattr(settings, "target_path", ""),
            "sourceDirs": getattr(settings, "source_dirs", "").split(",") if getattr(settings, "source_dirs", "") else [],
            "libraryNames": getattr(settings, "library_names", "").split(",") if getattr(settings, "library_names", "") else [],
            "instances": getattr(settings, "instances", "").split(",") if getattr(settings, "instances", "") else [],
            "assetFolders": getattr(settings, "asset_folders", False), 
            "borderReplacer": getattr(settings, "border_replacerr", False), 

            "radarrInstances": [
                {
                    "instanceName": instance.instance_name,
                    "url": instance.url,
                    "apiKey": instance.api_key,
                }
                for instance in radarr_instances
            ],

            "sonarrInstances": [
                {
                    "instanceName": instance.instance_name,
                    "url": instance.url,
                    "apiKey": instance.api_key,
                }
                for instance in sonarr_instances
            ],

            "plexInstances": [
                {
                    "instanceName": instance.instance_name,
                    "url": instance.url,
                    "apiKey": instance.api_key,
                }
                for instance in plex_instances
            ],
        }
        return jsonify({"success": True, "settings": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@settings.route("/save-settings", methods=["POST"])
def save_settings():
    try:
        data = request.get_json()

        target_path = data.get("targetPath", "")
        source_dirs = ",".join(data.get("sourceDirs", []))
        library_names = ",".join(data.get("libraryNames", []))
        instances = ",".join(data.get("instances", []))
        asset_folders = data.get("assetFolders", False)
        border_replacerr = data.get("borderReplacerr", False)
        radarr_instances = data.get("radarrInstances", [])
        sonarr_instances = data.get("sonarrInstances", [])
        plex_instances = data.get("plexInstances", [])

        models.Settings.query.delete()

        new_settings = models.Settings(
            target_path=target_path,
            source_dirs=source_dirs,
            library_names=library_names,
            instances=instances,
            asset_folders=asset_folders,
            border_replacerr=border_replacerr,
        )
        print(f"target path: {target_path}", flush=True)
        db.session.add(new_settings)

        models.RadarrInstance.query.delete()
        models.SonarrInstance.query.delete()
        models.PlexInstance.query.delete()

        for instance in radarr_instances:
            new_instance = models.RadarrInstance(
                instance_name=instance.get("instanceName"),
                url=instance.get("url"),
                api_key=instance.get("apiKey"),
            )
            db.session.add(new_instance)
        for instance in sonarr_instances:
            new_instance = models.SonarrInstance(
                instance_name=instance.get("instanceName"),
                url=instance.get("url"),
                api_key=instance.get("apiKey"),
            )
            db.session.add(new_instance)
        for instance in plex_instances:
            new_instance = models.PlexInstance(
                instance_name=instance.get("instanceName"),
                url=instance.get("url"),
                api_key=instance.get("apiKey"),
            )
            db.session.add(new_instance)

        db.session.commit()
        return jsonify({"success": True, "message": "Settings saved successfully!"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@settings.route("/test-connection", methods=["POST"])
def test_connection():

    data = request.get_json()

    url = data.get("url")
    api_key = data.get("apiKey")
    instance_type = data.get("instanceType")
    if instance_type in ["radarr", "sonarr"]:
        headers = {"X-Api-Key": api_key}
    elif instance_type == "plex":
        headers = {"X-Plex-Token": api_key}
    else:
        return jsonify({"success": False, "message": "Invalid instance type"}), 400
    try:
        if instance_type == "radarr":
            response = requests.get(
                f"{url}/api/v3/system/status", headers=headers, timeout=5
            )
        elif instance_type == "sonarr":
            response = requests.get(
                f"{url}/api/v3/system/status", headers=headers, timeout=5
            )
        elif instance_type == "plex":
            response = requests.get(
                f"{url}/status/sessions", headers=headers, timeout=5
            )

        if response.status_code == 200:
            return jsonify({"success": True, "message": "Connection successful!"})
        else:
            return jsonify({"success": False, "message": "Failed to connect!"}), 400
    except requests.RequestException as e:
        return jsonify({"success": False, "message": str(e)}), 400
