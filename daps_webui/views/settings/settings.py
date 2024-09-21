from flask import Blueprint, render_template, request, jsonify
from daps_webui import db, models
import requests
import sys

settings = Blueprint("settings", __name__)


@settings.route("/settings", methods=["GET"])
def settings_route():
    existing_settings = models.Settings.query.first()
    radarr_instances = models.RadarrInstance.query.all()
    sonarr_instances = models.SonarrInstance.query.all()
    plex_instances = models.PlexInstance.query.all()

    radarr_instance_data = [{
        'instance_name': instance.instance_name,
        'url': instance.url,
        'api_key': instance.api_key
        } for instance in radarr_instances]
    
    sonarr_instance_data = [{
        'instance_name': instance.instance_name,
        'url': instance.url,
        'api_key': instance.api_key
        } for instance in sonarr_instances]    
    
    plex_instance_data = [{
        'instance_name': instance.instance_name,
        'url': instance.url,
        'api_key': instance.api_key
        } for instance in plex_instances]    
    
    if radarr_instance_data or sonarr_instance_data or plex_instance_data or existing_settings:
        return render_template(
            "settings/settings.html",
            target_path=existing_settings.target_path,
            source_dirs=existing_settings.source_dirs.split(','),
            library_names=existing_settings.library_names.split(','),
            instances=existing_settings.instances.split(','),
            asset_folders=existing_settings.asset_folders,
            border_replacerr=existing_settings.border_replacerr,
            radarr_instances=radarr_instance_data,
            sonarr_instances=sonarr_instance_data,
            plex_instances=plex_instance_data
        )
    else:
        return render_template(
            "settings/settings.html",
            target_path='',
            source_dirs=[],
            library_names=[],
            instances=[],
            asset_folders=False,
            border_replacerr=False,
            radarr_instances=[],
            sonarr_instances=[],
            plex_instances=[]
        )

@settings.route("/save-settings", methods=["POST"])
def save_settings():
    try:
        data = request.get_json()

        target_path = data.get('targetPath', '')
        source_dirs = ','.join(data.get('sourceDirs', []))
        library_names = ','.join(data.get('libraryNames', []))
        instances = ','.join(data.get('instances', []))
        asset_folders = data.get('assetFolders', False)
        border_replacerr = data.get('borderReplacerr', False)
        radarr_instances = data.get('radarrInstances', [])
        sonarr_instances = data.get('sonarrInstances', [])
        plex_instances = data.get('plexInstances', [])

        models.Settings.query.delete()
        
        new_settings = models.Settings(
            target_path=target_path,
            source_dirs=source_dirs,
            library_names=library_names,
            instances=instances,
            asset_folders=asset_folders,
            border_replacerr=border_replacerr
        )
        db.session.add(new_settings)
        
        models.RadarrInstance.query.delete()
        models.SonarrInstance.query.delete()
        models.PlexInstance.query.delete()

        for instance in radarr_instances:
            new_instance = models.RadarrInstance(
                instance_name=instance.get('instanceName'),
                url=instance.get('url'),
                api_key=instance.get('apiKey')
            )
            db.session.add(new_instance)
        for instance in sonarr_instances:
            new_instance = models.SonarrInstance(
                instance_name=instance.get('instanceName'),
                url=instance.get('url'),
                api_key=instance.get('apiKey')
            )
            db.session.add(new_instance)
        for instance in plex_instances:
            new_instance = models.PlexInstance(
                instance_name=instance.get('instanceName'),
                url=instance.get('url'),
                api_key=instance.get('apiKey')
            )
            db.session.add(new_instance)       
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Settings saved successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings.route("/test-connection", methods=["POST"])
def test_connection():
    
    data=request.get_json() 
    
    url = data.get('url')
    api_key = data.get('apiKey')
    instance_type = data.get('instanceType')
    if instance_type in ['radarr', 'sonarr']:
        headers = {
            'X-Api-Key': api_key
        }
    elif instance_type == 'plex':
        headers = {
            'X-Plex-Token': api_key
        }
    else:
        return jsonify({'success': False, 'message': 'Invalid instance type'}), 400  
    try:
        if instance_type == 'radarr':
            response = requests.get(f'{url}/api/v3/system/status', headers=headers, timeout=5)
        elif instance_type == 'sonarr':
            response = requests.get(f'{url}/api/v3/system/status', headers=headers, timeout=5)
        elif instance_type == 'plex':
            response = requests.get(f'{url}/status/sessions', headers=headers, timeout=5)
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Connection successful!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to connect!'}), 400
    except requests.RequestException as e:
        return jsonify({'success': False, 'message': str(e)}), 400