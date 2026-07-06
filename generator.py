import re
import shutil
from pathlib import Path

def format_wml(raw_text):
    formatted_lines = []
    indent_level = 0
    indent_space = "    "

    for line in raw_text.splitlines():
        cleaned_line = line.strip()
        if not cleaned_line:
            formatted_lines.append("")
            continue

        if cleaned_line.startswith("[/"):
            indent_level = max(0, indent_level - 1)

        formatted_lines.append((indent_space * indent_level) + cleaned_line)

        if cleaned_line.startswith("[") and not cleaned_line.startswith("[/"):
            indent_level += 1

    return "\n".join(formatted_lines)

def parse_captains_from_map(map_text):
    positions = set(re.findall(r'\b\d+\b', map_text))
    valid_teams = [int(p) for p in positions if int(p) > 0]
    return len(valid_teams) if valid_teams else 0

def generate_campaign_files(campaign_name, scenarios_list):
    campaign_id = campaign_name.strip().replace(" ", "_")
    export_root = Path.home() / "Desktop" / campaign_id
    
    if export_root.exists():
        shutil.rmtree(export_root)
        
    maps_dir = export_root / "maps"
    scenarios_dir = export_root / "scenarios"
    
    maps_dir.mkdir(parents=True, exist_ok=True)
    scenarios_dir.mkdir(parents=True, exist_ok=True)
    
    first_clean = re.sub(r'[^a-zA-Z0-9\s_]', '', scenarios_list[0]["title"])
    first_scen_id = f"01_{first_clean.strip().replace(' ', '_')}"

    main_cfg_raw = f"""
[campaign]
    id={campaign_id}
    name=_"{campaign_name}"
    define=CAMPAIGN_{campaign_id.upper()}
    first_scenario={first_scen_id}
[/campaign]

#ifdef CAMPAIGN_{campaign_id.upper()}
[binary_path]
    path=data/add-ons/{campaign_id}
[/binary_path]
{{~add-ons/{campaign_id}/scenarios}}
#endif
"""
    with open(export_root / "_main.cfg", "w", encoding="utf-8") as f:
        f.write(format_wml(main_cfg_raw))
        
    for i, s in enumerate(scenarios_list):
        scen_num = f"{i+1:02d}"
        
        clean_title = re.sub(r'[^a-zA-Z0-9\s_]', '', s["title"])
        title_slug = clean_title.strip().replace(" ", "_")
        scen_id = f"{scen_num}_{title_slug}"
        
        map_file_name = f"{scen_id}.map"
        
        if s["map_data"]:
            with open(maps_dir / map_file_name, "w", encoding="utf-8") as f:
                f.write(s["map_data"])
                
        side_blocks = ""
        for side_num in range(1, s["captains_count"] + 1):
            side_blocks += f"""
[side]
    side={side_num}
    controller={"human" if side_num == 1 else "ai"}
    team_name={"heroes" if side_num == 1 else "villains"}
    user_team_name=_"{"Team " + str(side_num)}"
    type={"Elvish Captain" if side_num == 1 else "Orcish Warrior"}
    id=captain_{side_num}
    canrecruit=yes
[/side]"""

        if (i + 1) < len(scenarios_list):
            next_s = scenarios_list[i+1]
            next_clean = re.sub(r'[^a-zA-Z0-9\s_]', '', next_s["title"])
            next_slug = next_clean.strip().replace(" ", "_")
            next_scen = f"{i+2:02d}_{next_slug}"
        else:
            next_scen = "null"
        
        scenario_cfg_raw = f"""
[scenario]
    id={scen_id}
    name=_"{s['title']}"
    map_data="{{~add-ons/{campaign_id}/maps/{map_file_name}}}"
    turns=30
    next_scenario={next_scen}
    
    {side_blocks}
[/scenario]
"""
        with open(scenarios_dir / f"{scen_id}.cfg", "w", encoding="utf-8") as f:
            f.write(format_wml(scenario_cfg_raw))
            
    return export_root
