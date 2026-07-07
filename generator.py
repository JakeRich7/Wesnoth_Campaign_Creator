import re
import shutil
from pathlib import Path
import app_state

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

def compile_event_to_wml(ev):
    ev_type = ev["type"]
    wml = ""
    
    if ev_type == "turn":
        wml += f"[event]\nname=turn {ev.get('turn_number', '1')}\n"
    else:
        wml += f"[event]\nname={ev_type}\n"
        
    if ev_type in ["die", "last_breath"] and ev.get("filter_id"):
        wml += f"[filter]\nid={ev['filter_id']}\n[/filter]\n"
        
    if ev_type == "prestart":
        wml += "[objectives]\n"
        for obj in ev.get("objectives", []):
            wml += f"[objective]\ndescription= _ \"{obj['description']}\"\ncondition={obj['condition']}\n[/objective]\n"
        wml += "{TURNS_RUN_OUT}\n[gold_carryover]\nbonus=yes\ncarryover_percentage=40\n[/gold_carryover]\n[/objectives]\n"
        
    for msg in ev.get("messages", []):
        if msg.get("speaker") or msg.get("message"):
            wml += f"[message]\nspeaker={msg.get('speaker', 'narrator')}\nmessage= _ \"{msg.get('message', '')}\"\n[/message]\n"
            
    if ev_type in ["die", "victory"]:
        wml += "[endlevel]\nresult=victory\nbonus=yes\n{NEW_GOLD_CARRYOVER 40}\n[/endlevel]\n"
        
    wml += "[/event]\n"
    return wml

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
    rank={app_state.state.get('campaign_rank', '15')}
    icon="{app_state.state.get('campaign_icon', '')}"
    image="{app_state.state.get('campaign_image', '')}"
    first_scenario={first_scen_id}
    define=CAMPAIGN_{campaign_id.upper()}
    description=_"{app_state.state.get('campaign_description', '')}"
    
    {{CAMPAIGN_DIFFICULTY EASY "{app_state.state.get('easy_img', '')}" ( _ "{app_state.state.get('easy_label', '')}") ( _ "Easy")}}
    {{CAMPAIGN_DIFFICULTY NORMAL "{app_state.state.get('normal_img', '')}" ( _ "{app_state.state.get('normal_label', '')}") ( _ "Normal")}}
    {{CAMPAIGN_DIFFICULTY HARD "{app_state.state.get('hard_img', '')}" ( _ "{app_state.state.get('hard_label', '')}") ( _ "Hard")}}
    {{DEFAULT_DIFFICULTY}}
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
        events_wml = ""
        
        for ev in s.get("events", []):
            if ev["type"] == "side":
                side_blocks += f"""
[side]
    side={ev.get('side_number', '1')}
    controller={ev.get('controller', 'human')}
    team_name={ev.get('team_name', 'heroes')}
    user_team_name=_"{ev.get('team_name', 'heroes')}"
    {{GOLD {ev.get('gold_easy', '200')} {ev.get('gold_normal', '150')} {ev.get('gold_hard', '100')}}}
    {{INCOME {ev.get('income_easy', '2')} {ev.get('income_normal', '1')} {ev.get('income_hard', '0')}}}
    type="Elvish Captain"
    canrecruit=yes
[/side]"""
            else:
                events_wml += compile_event_to_wml(ev) + "\n"

        if not side_blocks:
            side_blocks = """
[side]
    side=1
    controller=human
    team_name=heroes
    user_team_name=_"heroes"
    type="Elvish Captain"
    canrecruit=yes
[/side]
[side]
    side=2
    controller=ai
    team_name=villains
    user_team_name=_"villains"
    type="Orcish Warrior"
    canrecruit=yes
[/side]"""

        next_scen = f"{campaign_id}_{i+2:02d}" if (i + 1) < len(scenarios_list) else "null"
        
        scenario_cfg_raw = f"""
[scenario]
    id={scen_id}
    name=_"{s['title']}"
    map_data="{{~add-ons/{campaign_id}/maps/{map_file_name}}}"
    {{TURNS {s.get('turns_easy', '24')} {s.get('turns_normal', '22')} {s.get('turns_hard', '20')}}}
    next_scenario={next_scen}
    
    {side_blocks}
    
    {events_wml}
[/scenario]
"""
        with open(scenarios_dir / f"{scen_id}.cfg", "w", encoding="utf-8") as f:
            f.write(format_wml(scenario_cfg_raw))
            
    return export_root
