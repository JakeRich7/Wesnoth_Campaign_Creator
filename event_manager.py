import customtkinter as ctk
import app_state
import importer

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
        "team_name": "heroes",
        "gold_easy": "200", "gold_normal": "150", "gold_hard": "100",
        "income_easy": "2", "income_normal": "1", "income_hard": "0"
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
        ctk.CTkLabel(num_row, text="Side Number:", font=("Arial", 12, "bold"), width=150, anchor="w").pack(side="left")
        num_ent = ctk.CTkEntry(num_row, width=80)
        num_ent.insert(0, event_data.get("side_number", "1"))
        num_ent.pack(side="left")
        num_ent.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "side_number", num_ent.get()))

        ctrl_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        ctrl_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(ctrl_row, text="Controller:", font=("Arial", 12, "bold"), width=150, anchor="w").pack(side="left")
        ctrl_menu = ctk.CTkOptionMenu(ctrl_row, values=["human", "ai"], width=100)
        ctrl_menu.set(event_data.get("controller", "human"))
        ctrl_menu.pack(side="left")
        ctrl_menu.configure(command=lambda val: save_event_inputs(event_idx, "controller", val))

        team_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        team_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(team_row, text="Team Name:", font=("Arial", 12, "bold"), width=150, anchor="w").pack(side="left")
        team_ent = ctk.CTkEntry(team_row, width=150)
        team_ent.insert(0, event_data.get("team_name", "heroes"))
        team_ent.pack(side="left")
        team_ent.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "team_name", team_ent.get()))

        gold_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        gold_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(gold_row, text="Gold (Easy/Norm/Hard):", font=("Arial", 12, "bold"), width=150, anchor="w").pack(side="left")
        ge = ctk.CTkEntry(gold_row, width=60); ge.insert(0, event_data.get("gold_easy", "200")); ge.pack(side="left", padx=2)
        ge.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "gold_easy", ge.get()))
        gn = ctk.CTkEntry(gold_row, width=60); gn.insert(0, event_data.get("gold_normal", "150")); gn.pack(side="left", padx=2)
        gn.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "gold_normal", gn.get()))
        gh = ctk.CTkEntry(gold_row, width=60); gh.insert(0, event_data.get("gold_hard", "100")); gh.pack(side="left", padx=2)
        gh.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "gold_hard", gh.get()))

        inc_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        inc_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(inc_row, text="Income (Easy/Norm/Hard):", font=("Arial", 12, "bold"), width=150, anchor="w").pack(side="left")
        ie = ctk.CTkEntry(inc_row, width=60); ie.insert(0, event_data.get("income_easy", "2")); ie.pack(side="left", padx=2)
        ie.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "income_easy", ie.get()))
        in_ = ctk.CTkEntry(inc_row, width=60); in_.insert(0, event_data.get("income_normal", "1")); in_.pack(side="left", padx=2)
        in_.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "income_normal", in_.get()))
        ih = ctk.CTkEntry(inc_row, width=60); ih.insert(0, event_data.get("income_hard", "0")); ih.pack(side="left", padx=2)
        ih.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "income_hard", ih.get()))
        
        unit_roster = importer.discover_local_units()

        type_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        type_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(type_row, text="Captain Type:", font=("Arial", 12, "bold"), width=150, anchor="w").pack(side="left")
        
        type_display = ctk.CTkLabel(type_row, text=event_data.get("captain_type", "Elvish Captain"), font=("Arial", 12, "bold"), text_color="#1f6aa5")
        
        def open_captain_selector():
            sel_win = ctk.CTkToplevel()
            sel_win.title("Select Captain Unit Type")
            sel_win.geometry("380x500")
            sel_win.attributes("-topmost", True)
            
            sub_scroll = ctk.CTkScrollableFrame(sel_win)
            sub_scroll.pack(fill="both", expand=True, padx=10, pady=10)
            
            def pick_unit(unit_name):
                save_event_inputs(event_idx, "captain_type", unit_name)
                type_display.configure(text=unit_name)
                sel_win.destroy()
                
            for folder_name, units_list in unit_roster.items():
                # Shared container frame ensures the items stay locked to this row
                row_wrapper = ctk.CTkFrame(sub_scroll, fg_color="transparent")
                row_wrapper.pack(fill="x", pady=2)
                
                folder_frame = ctk.CTkFrame(row_wrapper, fg_color="transparent")
                folder_frame.pack(fill="x")
                
                content_frame = ctk.CTkFrame(row_wrapper, fg_color="transparent")
                
                def toggle_folder(cf=content_frame):
                    if cf.winfo_manager():
                        cf.pack_forget()
                    else:
                        cf.pack(fill="x", padx=15, pady=2)
                        
                f_btn = ctk.CTkButton(folder_frame, text=f"📁 {folder_name} ({len(units_list)})", fg_color="#2b2b2b", hover_color="#3b3b3b", anchor="w", height=28, command=toggle_folder)
                f_btn.pack(fill="x")
                
                for raw_id, display_str in units_list:
                    u_btn = ctk.CTkButton(content_frame, text=display_str, fg_color="transparent", text_color="#b0b0b0", hover_color="#3b3b3b", anchor="w", height=24,
                                          command=lambda uid=raw_id: pick_unit(uid))
                    u_btn.pack(fill="x", pady=1)
                
        ctk.CTkButton(type_row, text="⚙️ Select Type", width=110, height=22, command=open_captain_selector).pack(side="left", padx=(0, 10))
        type_display.pack(side="left")

        id_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        id_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(id_row, text="Captain WML ID:", font=("Arial", 12, "bold"), width=150, anchor="w").pack(side="left")
        id_ent = ctk.CTkEntry(id_row, width=150)
        id_ent.insert(0, event_data.get("captain_id", "hero_leader"))
        id_ent.pack(side="left")
        id_ent.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "captain_id", id_ent.get()))

        name_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        name_row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(name_row, text="Display Name:", font=("Arial", 12, "bold"), width=150, anchor="w").pack(side="left")
        name_ent = ctk.CTkEntry(name_row, width=150)
        name_ent.insert(0, event_data.get("captain_name", "Erlornas"))
        name_ent.pack(side="left")
        name_ent.bind("<KeyRelease>", lambda e: save_event_inputs(event_idx, "captain_name", name_ent.get()))

        rec_row = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        rec_row.pack(fill="x", pady=(8, 2), anchor="w")
        ctk.CTkLabel(rec_row, text="Recruitment Options:", font=("Arial", 12, "bold"), width=150, anchor="w").pack(side="left")
        
        list_container = ctk.CTkFrame(scroll_pane, fg_color="transparent")
        list_container.pack(fill="x", pady=(0, 8), padx=(150, 0), anchor="w")
        
        def refresh_recruit_labels():
            for widget in list_container.winfo_children():
                widget.destroy()
            active_list = event_data.get("recruit_list", [])
            if not active_list:
                ctk.CTkLabel(list_container, text="None Selected", text_color="#b0b0b0", font=("Arial", 11, "italic")).pack(anchor="w")
            for unit in active_list:
                ctk.CTkLabel(list_container, text=f"• {unit}", font=("Arial", 11), height=14).pack(anchor="w", pady=0)

        def open_recruit_selector():
            selector_win = ctk.CTkToplevel()
            selector_win.title("Select Recruit Options")
            selector_win.geometry("380x500")
            selector_win.attributes("-topmost", True)
            
            sub_scroll = ctk.CTkScrollableFrame(selector_win)
            sub_scroll.pack(fill="both", expand=True, padx=10, pady=10)
            
            active_list = event_data.get("recruit_list", [])
            
            def toggle_unit(unit_name, var):
                if var.get() == 1:
                    if unit_name not in active_list: active_list.append(unit_name)
                else:
                    if unit_name in active_list: active_list.remove(unit_name)
                event_data["recruit_list"] = active_list
                refresh_recruit_labels()
                
            for folder_name, units_list in unit_roster.items():
                # Shared container frame ensures the items stay locked to this row
                row_wrapper = ctk.CTkFrame(sub_scroll, fg_color="transparent")
                row_wrapper.pack(fill="x", pady=2)
                
                folder_frame = ctk.CTkFrame(row_wrapper, fg_color="transparent")
                folder_frame.pack(fill="x")
                
                content_frame = ctk.CTkFrame(row_wrapper, fg_color="transparent")
                
                def toggle_folder(cf=content_frame):
                    if cf.winfo_manager():
                        cf.pack_forget()
                    else:
                        cf.pack(fill="x", padx=15, pady=2)
                        
                f_btn = ctk.CTkButton(folder_frame, text=f"📁 {folder_name} ({len(units_list)})", fg_color="#2b2b2b", hover_color="#3b3b3b", anchor="w", height=28, command=toggle_folder)
                f_btn.pack(fill="x")
                
                for raw_id, display_str in units_list:
                    u_row = ctk.CTkFrame(content_frame, fg_color="transparent")
                    u_row.pack(fill="x", pady=1)
                    chk_var = ctk.IntVar(value=1 if raw_id in active_list else 0)
                    chk = ctk.CTkCheckBox(u_row, text=display_str, variable=chk_var, font=("Arial", 11))
                    chk.configure(command=lambda uid=raw_id, v=chk_var: toggle_unit(uid, v))
                    chk.pack(side="left", padx=5)
                
        ctk.CTkButton(rec_row, text="⚙️ Choose Units", width=110, height=22, command=open_recruit_selector).pack(side="left")
        refresh_recruit_labels()

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
        available_speakers = get_available_speakers()
        
        for m_idx, msg in enumerate(event_data.get("messages", [])):
            m_box = ctk.CTkFrame(scroll_pane, fg_color="#1a1a1a")
            m_box.pack(fill="x", pady=4, padx=5)
            
            m_hdr = ctk.CTkFrame(m_box, fg_color="transparent")
            m_hdr.pack(fill="x", pady=(2, 2))
            ctk.CTkLabel(m_hdr, text="Speaker ID:", font=("Arial", 11, "bold")).pack(side="left", padx=(5, 5))
            
            spk_ent = ctk.CTkEntry(m_hdr, width=120, height=20, font=("Arial", 11))
            spk_ent.insert(0, msg["speaker"])
            spk_ent.pack(side="left")
            spk_ent.bind("<KeyRelease>", lambda e, mi=m_idx, se=spk_ent: event_data["messages"][mi].update({"speaker": se.get()}))
            
            def apply_speaker_select(val, target_entry=spk_ent, mi=m_idx):
                target_entry.delete(0, "end")
                target_entry.insert(0, val)
                event_data["messages"][mi].update({"speaker": val})
                
            spk_menu = ctk.CTkOptionMenu(m_hdr, values=available_speakers, width=110, height=20, font=("Arial", 10))
            spk_menu.set(msg["speaker"] if msg["speaker"] in available_speakers else "")
            spk_menu.pack(side="left", padx=5)
            spk_menu.configure(command=lambda val, target=spk_ent, mi=m_idx: apply_speaker_select(val, target, mi))
            
            del_btn = ctk.CTkButton(m_hdr, text="🗑️", width=24, height=18, fg_color="transparent", text_color="#A83232", hover_color="#4a1a1a", font=("Arial", 11), anchor="w")
            del_btn.configure(command=lambda mi=m_idx: delete_message_row(event_idx, mi, container_frame))
            del_btn.pack(side="left", padx=(5, 0))
            
            txt_box = ctk.CTkTextbox(m_box, width=420, height=55, font=("Arial", 13))
            txt_box.insert("1.0", msg["message"])
            txt_box.pack(fill="x", pady=(3, 5), padx=5)
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

def get_available_speakers():
    speakers = ["narrator"]
    idx = app_state.state["current_index"]
    if idx is not None:
        scen = app_state.state["scenarios"][idx]
        for ev in scen.get("events", []):
            if ev["type"] == "side" and ev.get("captain_id"):
                c_id = ev["captain_id"].strip()
                if c_id and c_id not in speakers:
                    speakers.append(c_id)
            elif ev["type"] in ["die", "last_breath"] and ev.get("filter_id"):
                f_id = ev["filter_id"].strip()
                if f_id and f_id not in speakers:
                    speakers.append(f_id)
    return speakers
