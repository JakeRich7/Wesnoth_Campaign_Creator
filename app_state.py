# app_state.py

# Global procedural data store
state = {
    "campaign_name": "My Epic Campaign",
    "scenarios": [],           # Array of dictionary objects tracking each scenario's data
    "current_index": None,     # Tracks which scenario index is currently visible in the editor
    
    # UI Object memory locations used for reading and updating text inputs dynamically
    "scenario_list_frame": None,
    "center_content_frame": None,
    "scenario_title_input": None,
    "dialogue_input": None
}
