import re
from pathlib import Path

def parse_captains_from_map(map_text):
    positions = set(re.findall(r'\b\d+\b', map_text))
    valid_teams = [int(p) for p in positions if int(p) > 0]
    return len(valid_teams) if valid_teams else 0

def parse_events_from_wml(content):
    events = []
    allowed_types = ["prestart", "start", "die", "last_breath", "turn", "victory"]
    event_blocks = re.findall(r'\[event\](.*?)\[/event\]', content, re.DOTALL)
    
    for block in event_blocks:
        name_match = re.search(r'name\s*=\s*([a-zA-Z0-9_\s]+?)(?:\s+(\d+))?(?:\n|$)', block)
        if not name_match:
            name_match = re.search(r'name\s*=\s*"([^"]+)"', block)
        if not name_match:
            continue
            
        raw_type = name_match.group(1).strip().replace(" ", "_")
        ev_type = raw_type
        
        if ev_type not in allowed_types:
            continue
            
        turn_num = name_match.group(2) if len(name_match.groups()) > 1 and name_match.group(2) else "1"
        if ev_type == "turn" and not turn_num:
            turn_match = re.search(r'name\s*=\s*turn\s+(\d+)', block)
            if turn_match:
                turn_num = turn_match.group(1)
                
        filter_match = re.search(r'\[filter\]\s*id\s*=\s*(\w+)\s*\[/filter\]', block)
        filter_id = filter_match.group(1) if filter_match else ""
        
        objectives = []
        obj_blocks = re.findall(r'\[objective\](.*?)\[/objective\]', block, re.DOTALL)
        for obj_b in obj_blocks:
            desc_m = re.search(r'description\s*=\s*_\s*"([^"]+)"', obj_b)
            if not desc_m:
                desc_m = re.search(r'description\s*=\s*"([^"]+)"', obj_b)
            cond_m = re.search(r'condition\s*=\s*(\w+)', obj_b)
            if desc_m and cond_m:
                objectives.append({"description": desc_m.group(1), "condition": cond_m.group(1)})
                
        messages = []
        msg_blocks = re.findall(r'\[message\](.*?)\[/message\]', block, re.DOTALL)
        for msg_b in msg_blocks:
            spk_m = re.search(r'speaker\s*=\s*(\w+)', msg_b)
            txt_m = re.search(r'message\s*=\s*_\s*"([^"]+)"', msg_b)
            if not txt_m:
                txt_m = re.search(r'message\s*=\s*"([^"]+)"', msg_b)
            if spk_m and txt_m:
                messages.append({"speaker": spk_m.group(1), "message": txt_m.group(1)})
                
        events.append({
            "type": ev_type,
            "turn_number": turn_num,
            "filter_id": filter_id,
            "objectives": objectives,
            "messages": messages
        })
    return events

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
        
    cfg_files = sorted([f for f in list(scenarios_dir.iterdir()) if f.is_file() and f.name.lower().endswith(".cfg")])
    
    for idx, cfg_path in enumerate(cfg_files):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            title_match = re.search(r'name\s*=\s*_\s*"([^"]+)"', content)
            if not title_match:
                title_match = re.search(r'name\s*=\s*"([^"]+)"', content)
            
            if title_match:
                title = title_match.group(1)
            else:
                title = re.sub(r'^\d+_+', '', cfg_path.stem).replace("_", " ").title()
            
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
                
            scen_events = []
            
            side_blocks = re.findall(r'\[side\](.*?)\[/side\]', content, re.DOTALL)
            for s_block in side_blocks:
                side_m = re.search(r'side\s*=\s*(\d+)', s_block)
                ctrl_m = re.search(r'controller\s*=\s*(\w+)', s_block)
                team_m = re.search(r'team_name\s*=\s*(\w+)', s_block)
                gold_m = re.search(r'gold\s*=\s*(\d+)', s_block)
                inc_m = re.search(r'income\s*=\s*(\d+)', s_block)
                
                if side_m:
                    scen_events.append({
                        "type": "side",
                        "side_number": side_m.group(1),
                        "controller": ctrl_m.group(1) if ctrl_m else "human",
                        "team_name": team_m.group(1) if team_m else "heroes",
                        "gold": gold_m.group(1) if gold_m else "100",
                        "income": inc_m.group(1) if inc_m else "0",
                        "turn_number": "",
                        "filter_id": "",
                        "objectives": [],
                        "messages": []
                    })
                    
            scen_events.extend(parse_events_from_wml(content))
            
            imported_scenarios.append({
                "title": title,
                "map_name": map_name,
                "map_data": map_data,
                "captains_count": captains_count,
                "events": scen_events,
                "active_event_index": None
            })
        except Exception:
            continue
    return imported_scenarios

