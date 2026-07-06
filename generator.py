# generator.py
import re
from pathlib import Path

def format_wml(raw_text):
    """Parses raw text templates and enforces standard Wesnoth 4-space indentation layout blocks."""
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
    """Scans the Wesnoth map coordinate data text grid to find starting slot numeric codes."""
    positions = set(re.findall(r'\b\d+\b', map_text))
    valid_teams = [int(p) for p in positions if int(p) > 0]
    return len(valid_teams) if valid_teams else 0


def generate_campaign_files(campaign_name, scenarios_list):
    """Loops through campaign criteria lists and outputs physical folders and config files onto the Desktop."""
    campaign_id = campaign_name.lower().replace(" ", "_")
    export_root = Path.home() / "Desktop" / f"wesnoth_addon_{campaign_id}"
    maps_dir = export_root / "maps"
    scenarios_dir = export_root / "scenarios"
    
    # Generate fresh file system paths cleanly
    maps_dir.mkdir(parents=True, exist_ok=True)
    scenarios_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Write core _main.cfg orchestrator file (UPDATED BRACKETS HERE)
    main_cfg_raw = f"""
[campaign]
    id={campaign_id}
    name=_"{campaign_name}"
    define=CAMPAIGN_{campaign_id.upper()}
    first_scenario={campaign_id}_01
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
        
    # 2. Iterate scenario layers and output their configurations
    for i, s in enumerate(scenarios_list):
        scen_num = f"{i+1:02d}"
        scen_id = f"{campaign_id}_{scen_num}"
        map_file_name = f"{scen_num}_map.map"
        
        # Save map text layout file if loaded, otherwise make an empty placeholder file
        if s["map_data"]:
            with open(maps_dir / map_file_name, "w", encoding="utf-8") as f:
                f.write(s["map_data"])
        else:
            # If no map was uploaded, create an empty placeholder file so Wesnoth doesn't crash on load
            with open(maps_dir / map_file_name, "w", encoding="utf-8") as f:
                f.write("border_size=1\nusage=map\n\nGg,Gg\nGg,Gg")
                
        # Generate side tags dynamically matching parsed map elements (default to 2 if map missing)
        sides_count = s["captains_count"] if s["map_name"] else 2
        side_blocks = ""
        for side_num in range(1, sides_count + 1):
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

        next_scen = f"{campaign_id}_{i+2:02d}" if (i + 1) < len(scenarios_list) else "null"
        
        # UPDATED BRACKETS HERE TOO
        scenario_cfg_raw = f"""
[scenario]
    id={scen_id}
    name=_"{s['title']}"
    map_data="{{~add-ons/{campaign_id}/maps/{map_file_name}}}"
    turns=30
    next_scenario={next_scen}
    
    {side_blocks}

    [event]
        name=start
        [message]
            speaker=narrator
            message=_"{s['dialogue']}"
        [/message]
    [/event]
[/scenario]
"""
        with open(scenarios_dir / f"{scen_id}.cfg", "w", encoding="utf-8") as f:
            f.write(format_wml(scenario_cfg_raw))
            
    return export_root
