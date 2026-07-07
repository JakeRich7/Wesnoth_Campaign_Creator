import customtkinter as ctk
import app_state

EVENT_TYPES = ["side", "prestart", "start", "die", "last_breath", "turn", "victory"]

def handle_add_event(event_type, container_frame):
    idx = app_state.state["current_index"]
    if idx is None:
        return
    scen = app_state.state["scenarios"][idx]
    if "events" not in scen:
        scen["events"] = []
        
    new_event = {
        "type": event_type,
        "turn_number": "1" if event_type == "turn" else "",
        "filter_id": "",
        "objectives": [],
        "messages": [],
        "side_number": "1",
        "controller": "human",
        "gold": "100",
        "income": "0",
        "team_name": "heroes"
    }
    
    if event_type == "prestart":
        new_event["objectives"] = [
            {"description": "Defeat the Enemy", "condition": "win"},
            {"description": "Death of your Hero", "condition": "lose"}
        ]
        
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

def add_objective_row(event_idx, container_frame):
    idx = app_state.state["current_index"]
    if idx is None:
        return
    app_state.state["scenarios"][idx]["events"][event_idx]["objectives"].append({"description": "New Objective", "condition": "win"})
    render_events_sidebar(container_frame)

def delete_objective_row(event_idx, obj_idx, container_frame):
    idx = app_state.state["current_index"]
    if idx is None:
        return
    del app_state.state["scenarios"][idx]["events"][event_idx]["objectives"][obj_idx]
    render_events_sidebar(container_frame)

def add_message_row(event_idx, container_frame):
    idx = app_state.state["current_index"]
    if idx is None:
        return
    app_state.state["scenarios"][idx]["events"][event_idx]["messages"].append({"speaker": "narrator", "message": ""})
    render_events_sidebar(container_frame)

def delete_message_row(event_idx, msg_idx, container_frame):
    idx = app_state.state["current_index"]
    if idx is None:
        return
    del app_state.state["scenarios"][idx]["events"][event_idx]["messages"][msg_idx]
    render_events_sidebar(container_frame)

def render_metadata_panel(parent_frame, event_idx, event_data, container_frame):
    scroll_pane = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
    scroll_pane.pack(fill="both", expand=True)

    ctk.CTkLabel(scroll_pane, text=f"Event Configuration: {event_data['type'].upper()}", font=("Arial", 14, "bold")).pack(anchor="w", pady=(5, 10))
    
    if event_data["type"] == "turn":
        row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(row, text="Turn Number:", font=("Arial", 12, "bold"), width=100, anchor="w").pack(side="left")
        turn_entry = ctk.CTkEntry(row, width=80)
        turn_entry.insert(0, event_data["turn_number"])
        turn_entry.pack(side="left")
        turn_entry.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "turn_number", turn_entry.get()))

    if event_data["type"] in ["die", "last_breath"]:
        row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(row, text="Filter Unit ID:", font=("Arial", 12, "bold"), width=100, anchor="w").pack(side="left")
        filter_entry = ctk.CTkEntry(row, width=150)
        filter_entry.insert(0, event_data.get("filter_id", ""))
        filter_entry.pack(side="left")
        filter_entry.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "filter_id", filter_entry.get()))

    if event_data["type"] == "side":
        num_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        num_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(num_row, text="Side Number:", font=("Arial", 12, "bold"), width=100, anchor="w").pack(side="left")
        num_ent = ctk.CTkEntry(num_row, width=80)
        num_ent.insert(0, event_data.get("side_number", "1"))
        num_ent.pack(side="left")
        num_ent.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "side_number", num_ent.get()))

        ctrl_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        ctrl_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(ctrl_row, text="Controller:", font=("Arial", 12, "bold"), width=100, anchor="w").pack(side="left")
        ctrl_menu = ctk.CTkOptionMenu(ctrl_row, values=["human", "ai"], width=100)
        ctrl_menu.set(event_data.get("controller", "human"))
        ctrl_menu.pack(side="left")
        ctrl_menu.configure(command=lambda val: save_event_inputs(event_idx, "controller", val))

        team_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        team_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(team_row, text="Team Name:", font=("Arial", 12, "bold"), width=100, anchor="w").pack(side="left")
        team_ent = ctk.CTkEntry(team_row, width=150)
        team_ent.insert(0, event_data.get("team_name", "heroes"))
        team_ent.pack(side="left")
        team_ent.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "team_name", team_ent.get()))

        gold_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        gold_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(gold_row, text="Starting Gold:", font=("Arial", 12, "bold"), width=100, anchor="w").pack(side="left")
        gold_ent = ctk.CTkEntry(gold_row, width=80)
        gold_ent.insert(0, event_data.get("gold", "100"))
        gold_ent.pack(side="left")
        gold_ent.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "gold", gold_ent.get()))

        inc_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        inc_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(inc_row, text="Base Income:", font=("Arial", 12, "bold"), width=100, anchor="w").pack(side="left")
        inc_ent = ctk.CTkEntry(inc_row, width=80)
        inc_ent.insert(0, event_data.get("income", "0"))
        inc_ent.pack(side="left")
        inc_ent.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "income", inc_ent.get()))

    if event_data["type"] == "prestart":
        ctk.CTkLabel(scroll_pane, text="Scenario Objectives:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        for o_idx, obj in enumerate(event_data.get("objectives", [])):
            o_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
            o_row.pack(fill="x", pady=3)
            
            desc_ent = ctk.CTkEntry(o_row, width=220)
            desc_ent.insert(0, obj["description"])
            desc_ent.pack(side="left", padx=(0, 5))
            desc_ent.bind("<KeyRelease>", lambda e, oi=o_idx, de=desc_ent: event_data["objectives"][oi].update({"description": de.get()}))
            
            cond_menu = ctk.CTkOptionMenu(o_row, values=["win", "lose"], width=70)
            cond_menu.set(obj["condition"])
            cond_menu.pack(side="left", padx=(0, 5))
            cond_menu.configure(command=lambda val, oi=o_idx: event_data["objectives"][oi].update({"condition": val}))
            
            ctk.CTkButton(o_row, text="🗑️", width=24, fg_color="transparent", text_color="#A83232", command=lambda oi=o_idx: delete_objective_row(event_idx, oi, container_frame)).pack(side="left")
        ctk.CTkButton(scroll_pane, text="➕ Add Objective", width=120, fg_color="#2b2b2b", command=lambda: add_objective_row(event_idx, container_frame)).pack(anchor="w", pady=5)

    if event_data["type"] != "side":
        ctk.CTkLabel(scroll_pane, text="Event Messages / Dialogue Stack:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 5))
        for m_idx, msg in enumerate(event_data.get("messages", [])):
            m_box = ctk.CTkFrame(scroll_pane, fg_color="#1a1a1a")
            m_box.pack(fill="x", pady=4, padx=5)
            
            m_hdr = ctk.CTkFrame(m_box, fg_color="transparent")
            m_hdr.pack(fill="x")
            ctk.CTkLabel(m_hdr, text="Speaker ID:", font=("Arial", 11, "bold")).pack(side="left")
            
            spk_ent = ctk.CTkEntry(m_hdr, width=120, height=20, font=("Arial", 11))
            spk_ent.insert(0, msg["speaker"])
            spk_ent.pack(side="left", padx=5)
            spk_ent.bind("<KeyRelease>", lambda e, mi=m_idx, se=spk_ent: event_data["messages"][mi].update({"speaker": se.get()}))
            
            ctk.CTkButton(m_hdr, text="🗑️ Message", width=60, height=18, fg_color="transparent", text_color="#A83232", command=lambda mi=m_idx: delete_message_row(event_idx, mi, container_frame)).pack(side="right")
            
            txt_box = ctk.CTkTextbox(m_box, width=420, height=45, font=("Arial", 11))
            txt_box.insert("1.0", msg["message"])
            txt_box.pack(fill="x", pady=(3, 0))
            txt_box.bind("<KeyRelease>", lambda e, mi=m_idx, tb=txt_box: event_data["messages"][mi].update({"message": tb.get("1.0", "end-1c")}))
            
        ctk.CTkButton(scroll_pane, text="➕ Add Message Block", width=140, fg_color="#2b2b2b", command=lambda: add_message_row(event_idx, container_frame)).pack(anchor="w", pady=5)

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
        render_metadata_panel(right_editor, active_idx, scen["events"][active_idx], parent_frame)
    else:
        placeholder = ctk.CTkLabel(right_editor, text="Select an event from the list\nor add a new one to configure metadata.", font=("Arial", 13, "italic"))
        placeholder.pack(expand=True)