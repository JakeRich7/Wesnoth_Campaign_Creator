import re
from pathlib import Path

def parse_captains_from_map(map_text):
    positions = set(re.findall(r'\b\d+\b', map_text))
    valid_teams = [int(p) for p in positions if int(p) > 0]
    return len(valid_teams) if valid_teams else 0

def import_campaign_folder(folder_path):
    root_path = Path(folder_path).absolute()
    scenarios_dir = None
    maps_dir = None
    
    if root_path.exists():
        for child in root_path.iterdir():
            if child.is_dir():
                if child.name.lower() == "scenarios":
                    scenarios_dir = child
                elif child.name.lower() == "maps":
                    maps_dir = child

    if not scenarios_dir:
        scenarios_dir = root_path / "scenarios"
    if not maps_dir:
        maps_dir = root_path / "maps"
    
    imported_scenarios = []
    
    if not scenarios_dir.exists():
        return imported_scenarios
        
    all_files = []
    try:
        all_files = list(scenarios_dir.iterdir())
    except Exception:
        return imported_scenarios

    cfg_files = sorted([f for f in all_files if f.is_file() and f.name.lower().endswith(".cfg")])
    
    for idx, cfg_path in enumerate(cfg_files):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            title_match = re.search(r'name\s*=\s*_\s*"([^"]+)"', content)
            if not title_match:
                title_match = re.search(r'name\s*=\s*"([^"]+)"', content)
            title = title_match.group(1) if title_match else cfg_path.stem
            
            map_name_match = re.search(r'map_data\s*=\s*"[^"]*/([^"/]+\.map)["}]', content)
            map_name = map_name_match.group(1) if map_name_match else f"{idx+1:02d}_map.map"
            
            map_data = ""
            captains_count = 0
            
            target_map_path = maps_dir / map_name
            if target_map_path.exists():
                with open(target_map_path, "r", encoding="utf-8") as mf:
                    map_data = mf.read()
                captains_count = parse_captains_from_map(map_data)
            else:
                map_name = None
                
            imported_scenarios.append({
                "title": title,
                "map_name": map_name,
                "map_data": map_data,
                "captains_count": captains_count
            })
            
        except Exception:
            continue
            
    return imported_scenarios
