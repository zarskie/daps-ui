import yaml
from pathlib import Path

class Config:
    def __init__(self, script_name: str, config_path: str):
        self.config_path = Path(config_path)
        self.script_name = script_name
        self.load_config()
    
    def load_config(self):       
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Config file not found at {self.config_path}")
            return
        except yaml.parser.ParserError as e:
            print(f"Error parsing config file: {e}")
            return      
        
        self.instances_config = config['instances']
        self.script_config = config.get(f"{self.script_name}")
        self.radarr_config = self.instances_config.get('radarr', {})
        self.sonarr_config = self.instances_config.get('sonarr', {})
        self.plex_config = self.instances_config.get('plex', {})

    def create_arr_instances(self, radarr_class: object, sonarr_class: object) -> tuple[dict[str, list[object], dict[str, list[object]]]]:
        radarr_instances = {}
        sonarr_instances = {}
        for key, value in self.radarr_config.items():
            if key in self.script_config['instances']:
                radarr_name = f'{key}'
                radarr_instances[radarr_name] = radarr_class(base_url=value['url'], api=value['api'])
        for key, value in self.sonarr_config.items():
            if key in self.script_config['instances']:
                sonarr_name = f'{key}'
                sonarr_instances[sonarr_name] = sonarr_class(base_url=value['url'], api=value['api'])                
        return radarr_instances, sonarr_instances
    
    def create_plex_instances(self, plex_class: object) -> dict[str, list[object]]:
        plex_instances = {}
        library_names = self.script_config['library_names']
        for key, value in self.plex_config.items():
            if key in self.script_config['instances']:
                plex_name = f'{key}'
                plex_instances[plex_name] = plex_class(plex_url=value['url'], plex_token=value['api'], library_names=library_names)
        return plex_instances

