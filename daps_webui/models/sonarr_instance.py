from daps_webui import db

class SonarrInstance(db.Model):
    __tablename__ = 'sonarr_instances'
    id = db.Column(db.Integer, primary_key=True)
    instance_name = db.Column(db.String)
    url = db.Column(db.String)
    api_key = db.Column(db.String)