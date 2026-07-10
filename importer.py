import re
from pathlib import Path
import app_state

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

def discover_local_units():
    if app_state.state["discovered_units"] and isinstance(app_state.state["discovered_units"], dict):
        return app_state.state["discovered_units"]
        
    grouped_units = {}
    base_dir = Path(app_state.state["wesnoth_directory"])
    scan_tasks = [
        ("Core", base_dir / "data" / "core" / "units")
    ]
    
    if app_state.state["imported_campaign_path"]:
        scan_tasks.append(("Campaign", Path(app_state.state["imported_campaign_path"]) / "units"))
        scan_tasks.append(("Campaign", Path(app_state.state["imported_campaign_path"]) / "Units"))
        
    if app_state.state["extra_addon_path"]:
        scan_tasks.append(("Addon", Path(app_state.state["extra_addon_path"]) / "units"))
        scan_tasks.append(("Addon", Path(app_state.state["extra_addon_path"]) / "Units"))
        
    for origin_type, path in scan_tasks:
        if path.exists():
            for cfg_file in path.glob("**/*.cfg"):
                try:
                    uid, lvl = None, "0"
                    with open(cfg_file, "r", encoding="utf-8") as f:
                        for line in f:
                            cleaned = line.strip()
                            if cleaned.startswith("id=") and not cleaned.startswith("#"):
                                uid = cleaned.split("=")[1].strip().strip('"').strip("'")
                            elif cleaned.startswith("level=") and not cleaned.startswith("#"):
                                lvl = cleaned.split("=")[1].strip().strip('"').strip("'")
                                
                            if uid and "level=" in line:
                                break
                                
                    if uid and not uid.startswith("$") and uid not in ["unit", "second_unit"]:
                        folder_name = cfg_file.parent.name.replace("-", " ").title()
                        
                        if origin_type == "Core":
                            category = f"Core: {folder_name}"
                        elif origin_type == "Campaign":
                            category = f"Campaign: {folder_name}"
                        else:
                            category = f"Addon: {folder_name}"
                            
                        if category not in grouped_units:
                            grouped_units[category] = set()
                        
                        display_string = f"{uid} [{lvl}]"
                        grouped_units[category].add((uid, display_string))
                except Exception:
                    continue
                    
    final_dict = {}
    for cat, u_set in sorted(grouped_units.items()):
        if u_set:
            final_dict[cat] = sorted(list(u_set), key=lambda x: x[0])
            
    if not final_dict:
        final_dict["Default Units"] = [
            ("Orcish Archer", "Orcish Archer [1]"),
            ("Orcish Grunt", "Orcish Grunt [1]"),
            ("Wolf Rider", "Wolf Rider [1]"),
            ("Elvish Captain", "Elvish Captain [2]"),
            ("Orcish Warrior", "Orcish Warrior [2]")
        ]
        
    app_state.state["discovered_units"] = final_dict
    return final_dict

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

    pbl_file = root_path / "_server.pbl"
    if pbl_file.exists():
        try:
            with open(pbl_file, "r", encoding="utf-8") as pf:
                pbl_content = pf.read()
            app_state.state["generate_pbl"] = True
            
            type_match = re.search(r'type\s*=\s*"([^"]+)"', pbl_content)
            ver_match = re.search(r'version\s*=\s*"([^"]+)"', pbl_content)
            auth_match = re.search(r'author\s*=\s*"([^"]+)"', pbl_content)
            email_match = re.search(r'email\s*=\s*"([^"]+)"', pbl_content)
            pass_match = re.search(r'passphrase\s*=\s*"([^"]+)"', pbl_content)
            
            if type_match: app_state.state["pbl_type"] = type_match.group(1)
            if ver_match: app_state.state["pbl_version"] = ver_match.group(1)
            if auth_match: app_state.state["pbl_author"] = auth_match.group(1)
            if email_match: app_state.state["pbl_email"] = email_match.group(1)
            if pass_match: app_state.state["pbl_passphrase"] = pass_match.group(1)
        except Exception:
            pass
    else:
        app_state.state["generate_pbl"] = False

    main_cfg = root_path / "_main.cfg"
    if main_cfg.exists():
        try:
            with open(main_cfg, "r", encoding="utf-8") as mf:
                main_content = mf.read()
            img_match = re.search(r'\bimage\s*=\s*"([^"]+)"', main_content)
            if img_match:
                app_state.state["campaign_image"] = img_match.group(1)
        except Exception:
            pass
    
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
                side_m = re.search(r'\bside\s*=\s*(\d+)', s_block)
                ctrl_m = re.search(r'\bcontroller\s*=\s*(\w+)', s_block)
                team_m = re.search(r'\bteam_name\s*=\s*(\w+)', s_block)
                
                type_m = re.search(r'type\s*=\s*"([^"]+)"', s_block)
                if not type_m: type_m = re.search(r'type\s*=\s*([a-zA-Z0-9_\s]+)', s_block)
                
                id_m = re.search(r'\bid\s*=\s*"([^"]+)"', s_block)
                if not id_m: id_m = re.search(r'\bid\s*=\s*([a-zA-Z0-9_]+)', s_block)
                
                name_m = re.search(r'\bname\s*=\s*(?:_\s*)?"([^"]+)"', s_block)
                if not name_m: name_m = re.search(r'\bname\s*=\s*(?:_\s*)?([a-zA-Z0-9_]+)', s_block)
                
                rec_m = re.search(r'\brecruit\s*=\s*"([^"]+)"', s_block)
                if not rec_m: rec_m = re.search(r'\brecruit\s*=\s*([a-zA-Z0-9_\s,]+)', s_block)
                
                gold_m = re.search(r'GOLD\s+(\d+)\s+(\d+)\s+(\d+)', s_block, re.IGNORECASE)
                inc_m = re.search(r'INCOME\s+(\d+)\s+(\d+)\s+(\d+)', s_block, re.IGNORECASE)
                
                rec_list = [r.strip() for r in rec_m.group(1).split(",")] if rec_m else []
                
                if side_m:
                    scen_events.append({
                        "type": "side",
                        "side_number": side_m.group(1),
                        "controller": ctrl_m.group(1) if ctrl_m else "human",
                        "team_name": team_m.group(1) if team_m else "heroes",
                        "captain_type": type_m.group(1).strip() if type_m else "Elvish Captain",
                        "captain_id": id_m.group(1).strip() if id_m else "hero_leader",
                        "captain_name": name_m.group(1).strip() if name_m else "Erlornas",
                        "recruit_list": rec_list,
                        "gold_easy": gold_m.group(1) if gold_m else "200",
                        "gold_normal": gold_m.group(2) if gold_m else "150",
                        "gold_hard": gold_m.group(3) if gold_m else "100",
                        "income_easy": inc_m.group(1) if inc_m else "2",
                        "income_normal": inc_m.group(2) if inc_m else "1",
                        "income_hard": inc_m.group(3) if inc_m else "0",
                        "turn_number": "", "filter_id": "", "objectives": [], "messages": []
                    })
                    
            scen_events.extend(parse_events_from_wml(content))
            
            story_parts = []
            story_match = re.search(r'\[story\](.*?)\[/story\]', content, re.DOTALL)
            if story_match:
                part_blocks = re.findall(r'\[part\](.*?)\[/part\]', story_match.group(1), re.DOTALL)
                for p_block in part_blocks:
                    m_match = re.search(r'music\s*=\s*([^\s\n]+)', p_block)
                    bg_match = re.search(r'background\s*=\s*([^\s\n]+)', p_block)
                    st_match = re.search(r'story\s*=\s*(?:_\s*)?"([^"]+)"', p_block)
                    if st_match:
                        story_parts.append({
                            "music": m_match.group(1) if m_match else "",
                            "background": bg_match.group(1) if bg_match else "",
                            "story":  st_match.group(1)
                        })

            imported_scenarios.append({
                "title": title,
                "map_name": map_name,
                "map_data": map_data,
                "captains_count": captains_count,
                "events": scen_events,
                "story_parts": story_parts,
                "active_event_index": None

            })
        except Exception:
            continue
    return imported_scenarios

