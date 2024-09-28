import logging
from time import sleep
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from daps_webui.config.config import Config
from concurrent.futures import ThreadPoolExecutor, wait
from DapsEX.poster_renamerr import PosterRenamerr
from daps_webui.utils import webui_utils
from daps_webui.utils.webui_utils import *
from progress import *

# all globals needs to be defined here
global_config = Config()
db = SQLAlchemy()
progress_dict = {}
executor = ThreadPoolExecutor(max_workers=2)

# define all loggers
daps_logger = logging.getLogger("daps")


def create_app() -> Flask:
    # init flask app
    app = Flask(__name__)
    app.config.from_object(global_config)

    # initiate logger(s)
    from daps_webui.utils.logger_utils import init_logger

    init_logger(daps_logger, global_config.logs, "daps_log.log", logging.INFO)

    # initiate database
    db.init_app(app)

    # import needed blueprints
    from daps_webui.views.home.home import home
    from daps_webui.views.settings.settings import settings
    from daps_webui.views.poster_renamer.poster_renamer import poster_renamer

    # register blueprints
    app.register_blueprint(home)
    app.register_blueprint(settings)
    app.register_blueprint(poster_renamer)

    return app


app = create_app()
with app.app_context():
    db.create_all()

@app.route("/run-renamer-job", methods=["POST"])
def run_renamer():
    from daps_webui.models import RadarrInstance, SonarrInstance, PlexInstance
    try:
        radarr = get_instances(RadarrInstance())
        sonarr = get_instances(SonarrInstance())
        plex = get_instances(PlexInstance())
        payload = webui_utils.create_poster_renamer_payload(radarr, sonarr, plex)

        job_id = progress_instance.add_job()
        print(f"{job_id}")

        renamer = PosterRenamerr(
            payload.target_path, payload.source_dirs, payload.asset_folders
        )
        future = executor.submit(renamer.run, payload, progress_instance, job_id)
        
        def remove_job_cb(fut):
            sleep(2)
            progress_instance.remove_job(job_id)
            print(f"Job {job_id} has been removed", flush=True)

        future.add_done_callback(remove_job_cb)

        return jsonify({"message": "Poster renamer started", "job_id": job_id}), 202
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/progress/<job_id>", methods=['GET'])
def get_progress(job_id):
    job_progress = progress_instance.get_progress(job_id)
    if job_progress:
        value, state = job_progress
        return jsonify({
            'job_id': job_id,
            'state': state,
            'value': value 
        })
    else:
        return jsonify({'error': 'Job not found'}), 404
