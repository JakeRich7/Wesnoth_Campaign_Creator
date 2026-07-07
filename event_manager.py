import customtkinter as ctk
import app_state

EVENT_TYPES = ["start", "die", "last_breath", "turn"]

def handle_add_event(event_type, container_frame):
    idx = app_state.state["current_index"]
    if idx is None:
        return
    scen = app_state.state["scenarios"][idx]
    if "events" not in scen:
        scen["events"] = []
    new_event = {
        "type": event_type,
        "turn_number": "1" if event_type == "turn" else ""
    }
    scen["events"].append(new_event)
    scen["active_event_index"] = len(scen["events"]) - 1
    render_events_sidebar(container_frame)

def handle_delete_event(event_idx, container_frame):
    idx = app_state.state["current_index"]
    if idx is None:
        return
    scen = app_state.state["scenarios"][idx]
    del scen["events"][event_idx]
    if scen.get("active_event_index") == event_idx:
        scen["active_event_index"] = None
    elif scen.get("active_event_index", 0) > event_idx:
        scen["active_event_index"] -= 1
    render_events_sidebar(container_frame)

def handle_select_event(event_idx, container_frame):
    idx = app_state.state["current_index"]
    if idx is None:
        return
    app_state.state["scenarios"][idx]["active_event_index"] = event_idx
    render_events_sidebar(container_frame)

def save_event_inputs(event_idx, key, val):
    idx = app_state.state["current_index"]
    if idx is None:
        return
    app_state.state["scenarios"][idx]["events"][event_idx][key] = val

def render_metadata_panel(parent_frame, event_idx, event_data):
    ctk.CTkLabel(parent_frame, text=f"Event Configuration: {event_data['type'].upper()}", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 15))
    
    if event_data["type"] == "turn":
        row = ctk.CTkFrame(parent_frame, fg_color="transparent")
        row.pack(fill="x", pady=5, anchor="w")
        ctk.CTkLabel(row, text="Turn Number:", font=("Arial", 12, "bold"), width=100, anchor="w").pack(side="left")
        turn_entry = ctk.CTkEntry(row, width=100)
        turn_entry.insert(0, event_data["turn_number"])
        turn_entry.pack(side="left")
        turn_entry.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "turn_number", turn_entry.get()))
    else:
        ctk.CTkLabel(parent_frame, text="This event triggers dynamically during gameplay.\nNo additional parameters needed.", font=("Arial", 13, "italic"), text_color="#b0b0b0").pack(anchor="w", pady=10)

def render_events_sidebar(parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    idx = app_state.state["current_index"]
    if idx is None:
        return
        
    scen = app_state.state["scenarios"][idx]
    if "events" not in scen:
        scen["events"] = []
    if "active_event_index" not in scen:
        scen["active_event_index"] = None

    sidebar_frame = ctk.CTkFrame(parent_frame, width=250, fg_color="#2b2b2b")
    sidebar_frame.pack(side="left", fill="y", padx=(0, 15))
    sidebar_frame.pack_propagate(False)

    right_editor = ctk.CTkFrame(parent_frame, fg_color="transparent")
    right_editor.pack(side="right", fill="both", expand=True)

    ctk.CTkLabel(sidebar_frame, text="Scenario Events", font=("Arial", 14, "bold")).pack(pady=(15, 5), padx=10, anchor="w")

    control_row = ctk.CTkFrame(sidebar_frame, fg_color="transparent")
    control_row.pack(fill="x", padx=10, pady=5)
    
    add_combo = ctk.CTkOptionMenu(control_row, values=EVENT_TYPES, width=140)
    add_combo.pack(side="left", padx=(0, 5))
    
    add_btn = ctk.CTkButton(control_row, text="➕ Add", width=70, fg_color="#1f6aa5", hover_color="#144870", 
                             command=lambda: handle_add_event(add_combo.get(), parent_frame))
    add_btn.pack(side="right")

    list_frame = ctk.CTkScrollableFrame(sidebar_frame, fg_color="transparent")
    list_frame.pack(fill="both", expand=True, padx=5, pady=5)

    for i, ev in enumerate(scen["events"]):
        row = ctk.CTkFrame(list_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        is_active = (i == scen["active_event_index"])
        btn_color = "#1f6aa5" if is_active else "transparent"
        text_color = "white" if is_active else "#b0b0b0"
        
        lbl_text = f"⚙️ {ev['type']} ({ev['turn_number']})" if ev["type"] == "turn" else f"⚙️ {ev['type']}"
        
        ev_btn = ctk.CTkButton(row, text=lbl_text, fg_color=btn_color, text_color=text_color, hover_color="#3b3b3b", anchor="w", height=24, corner_radius=4,
                               command=lambda e_idx=i: handle_select_event(e_idx, parent_frame))
        ev_btn.pack(side="left", fill="x", expand=True)
        
        del_btn = ctk.CTkButton(row, text="🗑️", width=24, height=24, fg_color="transparent", text_color="#A83232", hover_color="#4a1a1a", corner_radius=4,
                                 command=lambda e_idx=i: handle_delete_event(e_idx, parent_frame))
        del_btn.pack(side="right", padx=(2, 0))

    active_idx = scen["active_event_index"]
    if active_idx is not None and active_idx < len(scen["events"]):
        render_metadata_panel(right_editor, active_idx, scen["events"][active_idx])
    else:
        placeholder = ctk.CTkLabel(right_editor, text="Select an event from the list\nor add a new one to configure metadata.", font=("Arial", 13, "italic"))
        placeholder.pack(expand=True)
