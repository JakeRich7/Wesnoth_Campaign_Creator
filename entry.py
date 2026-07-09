from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk
import app_state
import generator
import importer
import event_manager


def save_active_inputs():
    idx = app_state.state["current_index"]
    if idx is not None and idx < len(app_state.state["scenarios"]):
        if app_state.state["scenario_title_input"]:
            app_state.state["scenarios"][idx]["title"] = app_state.state["scenario_title_input"].get()


def switch_to_global():
        app_state.state["view_mode"] = "campaign"
        app_state.state["current_index"] = None
        refresh_sidebar()
        render_campaign_settings_panel()


def handle_add():
    save_active_inputs()
    blank_scenario = {
        "title": f"Scenario {len(app_state.state['scenarios']) + 1}",
        "map_name": None,
        "map_data": "",
        "captains_count": 0,
        "turns_easy": "24",
        "turns_normal": "22",
        "turns_hard": "20",
        "story_parts": [],
        "events": []
    }
    app_state.state["scenarios"].append(blank_scenario)
    app_state.state["current_index"] = len(app_state.state["scenarios"]) - 1
    app_state.state["view_mode"] = "scenario"
    refresh_sidebar()
    render_workspace()
    

def handle_delete(idx):
    if 0 <= idx < len(app_state.state["scenarios"]):
        del app_state.state["scenarios"][idx]
        if not app_state.state["scenarios"]:
            app_state.state["current_index"] = None
        else:
            app_state.state["current_index"] = max(0, idx - 1)
        refresh_sidebar()
        render_workspace()


def handle_select(idx):
    save_active_inputs()
    app_state.state["current_index"] = idx
    refresh_sidebar()
    render_workspace()


def handle_upload():
    idx = app_state.state["current_index"]
    if idx is None:
        return

    file_path = filedialog.askopenfilename(
        title="Select a Battle for Wesnoth Map",
        filetypes=[("Wesnoth Map Files", "*.map")]
    )
    
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            teams = importer.parse_captains_from_map(content)
            app_state.state["scenarios"][idx]["map_name"] = Path(file_path).name
            app_state.state["scenarios"][idx]["map_data"] = content
            app_state.state["scenarios"][idx]["captains_count"] = teams
            refresh_sidebar()
            render_workspace()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to ingest map file:\n{str(e)}")

def handle_import():
    save_active_inputs()
    selected_dir = filedialog.askdirectory(title="Select Wesnoth Campaign Add-on Folder")
    
    if selected_dir:
        app_state.state["imported_campaign_path"] = selected_dir
        app_state.state["export_directory"] = str(Path(selected_dir).parent)
        app_state.state["discovered_units"] = []
        
        try:
            scenarios = importer.import_campaign_folder(selected_dir)
            
            if not scenarios:
                app_state.state["campaign_name"] = "My Epic Campaign"
                app_state.state["campaign_description"] = "An epic adventure awaits..."
                app_state.state["campaign_rank"] = "15"
                app_state.state["campaign_icon"] = "units/elves-wood/lord.png"
                app_state.state["campaign_image"] = "wesnoth-icon.png"
                app_state.state["easy_img"] = "units/elves-wood/fighter.png"
                app_state.state["normal_img"] = "units/elves-wood/lord.png"
                app_state.state["hard_img"] = "units/elves-wood/high-lord.png"
                app_state.state["easy_label"] = "Beginner"
                app_state.state["normal_label"] = "Normal"
                app_state.state["hard_label"] = "Challenging"
                app_state.state["wesnoth_directory"] = "C:/Program Files/Battle for Wesnoth 1.18.3"
                app_state.state["imported_campaign_path"] = ""
                app_state.state["export_directory"] = str(Path.home() / "Desktop")
                app_state.state["extra_addon_path"] = ""
                app_state.state["discovered_units"] = []
                app_state.state["scenarios"] = []
                app_state.state["current_index"] = None
                app_state.state["view_mode"] = "scenario"
                app_state.state["generate_pbl"] = True
                app_state.state["pbl_type"] = "campaign"
                app_state.state["pbl_version"] = "1.0.0"
                app_state.state["pbl_author"] = ""
                app_state.state["pbl_email"] = ""
                app_state.state["pbl_passphrase"] = ""
                
                refresh_sidebar()
                render_workspace()
                messagebox.showwarning("Import Failed", "No valid .cfg scenario files were found inside this folder. Workspace reset to default.")
                return
                
            clean_name = Path(selected_dir).name.replace("wesnoth_addon_", "").replace("_", " ").title()
            app_state.state["campaign_name"] = clean_name
            app_state.state["scenarios"] = scenarios
            app_state.state["current_index"] = 0
            
            if hasattr(app_state, "campaign_name_input") and app_state.campaign_name_input:
                app_state.campaign_name_input.delete(0, "end")
                app_state.campaign_name_input.insert(0, clean_name)
                
            refresh_sidebar()
            render_workspace()
            messagebox.showinfo("Import Success", f"Successfully imported {len(scenarios)} scenarios!")
            
        except Exception as e:
            app_state.state["campaign_name"] = "My Epic Campaign"
            app_state.state["campaign_description"] = "An epic adventure awaits..."
            app_state.state["campaign_rank"] = "15"
            app_state.state["campaign_icon"] = "units/elves-wood/lord.png"
            app_state.state["campaign_image"] = "wesnoth-icon.png"
            app_state.state["easy_img"] = "units/elves-wood/fighter.png"
            app_state.state["normal_img"] = "units/elves-wood/lord.png"
            app_state.state["hard_img"] = "units/elves-wood/high-lord.png"
            app_state.state["easy_label"] = "Beginner"
            app_state.state["normal_label"] = "Normal"
            app_state.state["hard_label"] = "Challenging"
            app_state.state["wesnoth_directory"] = "C:/Program Files/Battle for Wesnoth 1.18.3"
            app_state.state["imported_campaign_path"] = ""
            app_state.state["export_directory"] = str(Path.home() / "Desktop")
            app_state.state["extra_addon_path"] = ""
            app_state.state["discovered_units"] = []
            app_state.state["scenarios"] = []
            app_state.state["current_index"] = None
            app_state.state["view_mode"] = "scenario"
            app_state.state["generate_pbl"] = True
            app_state.state["pbl_type"] = "campaign"
            app_state.state["pbl_version"] = "1.0.0"
            app_state.state["pbl_author"] = ""
            app_state.state["pbl_email"] = ""
            app_state.state["pbl_passphrase"] = ""
            
            refresh_sidebar()
            render_workspace()
            messagebox.showerror("Import Error", f"A critical error occurred while importing:\n{str(e)}\n\nWorkspace reset to default.")

def handle_reset():
    if messagebox.askyesno("Reset Project", "Are you sure you want to clear the current campaign? All unsaved work will be lost."):
        app_state.state["campaign_name"] = "My Epic Campaign"
        app_state.state["campaign_description"] = "An epic adventure awaits..."
        app_state.state["campaign_rank"] = "15"
        app_state.state["campaign_icon"] = "units/elves-wood/lord.png"
        app_state.state["campaign_image"] = "wesnoth-icon.png"
        app_state.state["easy_img"] = "units/elves-wood/fighter.png"
        app_state.state["normal_img"] = "units/elves-wood/lord.png"
        app_state.state["hard_img"] = "units/elves-wood/high-lord.png"
        app_state.state["easy_label"] = "Beginner"
        app_state.state["normal_label"] = "Normal"
        app_state.state["hard_label"] = "Challenging"
        app_state.state["wesnoth_directory"] = "C:/Program Files/Battle for Wesnoth 1.18.3"
        app_state.state["imported_campaign_path"] = ""
        app_state.state["export_directory"] = str(Path.home() / "Desktop")
        app_state.state["extra_addon_path"] = ""
        app_state.state["discovered_units"] = []
        app_state.state["scenarios"] = []
        app_state.state["current_index"] = None
        app_state.state["view_mode"] = "scenario"
        app_state.state["generate_pbl"] = True
        app_state.state["pbl_type"] = "campaign"
        app_state.state["pbl_version"] = "1.0.0"
        app_state.state["pbl_author"] = ""
        app_state.state["pbl_email"] = ""
        app_state.state["pbl_passphrase"] = ""
        
        refresh_sidebar()
        render_workspace()

def handle_export():
    save_active_inputs()
    
    if hasattr(app_state, "campaign_name_input") and app_state.campaign_name_input:
        app_state.state["campaign_name"] = app_state.campaign_name_input.get()

    if not app_state.state["scenarios"]:
        messagebox.showwarning("Warning", "Add at least one scenario before generating your campaign!")
        return
        
    errors = []
    for i, s in enumerate(app_state.state["scenarios"]):
        if not s["map_name"]:
            errors.append(f"• Scenario {i+1} ('{s['title']}') is missing a .map file.")
            
    if errors:
        error_msg = "Cannot generate campaign due to the following errors:\n\n" + "\n".join(errors)
        messagebox.showerror("Validation Error", error_msg)
        return
        
    if app_state.state.get("generate_pbl", True):
        pbl_errors = []
        if not app_state.state.get("pbl_author", "").strip(): pbl_errors.append("• Author Name is required.")
        if not app_state.state.get("pbl_email", "").strip(): pbl_errors.append("• Public Email is required.")
        if not app_state.state.get("pbl_passphrase", "").strip(): pbl_errors.append("• Server Passphrase is required.")
        if not app_state.state.get("pbl_version", "").strip(): pbl_errors.append("• Version string is required.")
        
        if pbl_errors:
            error_msg = "PBL Generation Error:\n\n" + "\n".join(pbl_errors) + "\n\nFill these fields out in 'Global Campaign Configs' or uncheck the PBL file option."
            messagebox.showerror("Validation Error", error_msg)
            return

    try:
        dest = generator.generate_campaign_files(
            app_state.state["campaign_name"], 
            app_state.state["scenarios"]
        )
        messagebox.showinfo("Success", f"WML Campaign Successfully Built!\nSaved to: {dest}")
    except Exception as e:
        messagebox.showerror("Error", f"Generation Error Occurred:\n{str(e)}")


def refresh_sidebar():
    for widget in app_state.state["scenario_list_frame"].winfo_children():
        widget.destroy()
        
    for i, s in enumerate(app_state.state["scenarios"]):
        row = ctk.CTkFrame(app_state.state["scenario_list_frame"], fg_color="transparent")
        row.pack(fill="x", pady=4, padx=5)
        
        is_active = (i == app_state.state["current_index"])
        btn_color = "#1f6aa5" if is_active else "#2b2b2b"
        
        lbl = f"⚙️ {s['title']}" if s['map_name'] else f"❌ {s['title']}"
        
        del_btn = ctk.CTkButton(
            row, text="🗑️", width=30, fg_color="#A83232", hover_color="#822525", 
            command=lambda idx=i: handle_delete(idx)
        )
        del_btn.pack(side="right", padx=(5, 0))
        
        nav_btn = ctk.CTkButton(
            row, text=lbl, fg_color=btn_color, anchor="w", 
            command=lambda idx=i: handle_select(idx)
        )
        nav_btn.pack(side="left", fill="x", expand=True)

def handle_img_upload(key, entry_widget):
    file_path = filedialog.askopenfilename(
        title="Select Image File",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")]
    )
    if file_path:
        filename = Path(file_path).name
        campaign_id = app_state.state["campaign_name"].strip().replace(" ", "_")
        
        if key == "campaign_image":
            formatted_path = f"data/add-ons/{campaign_id}/images/{filename}"
        elif key in ["campaign_icon", "easy_img", "normal_img", "hard_img"]:
            formatted_path = f"units/{filename}"
        else:
            formatted_path = filename
            
        app_state.state[key] = formatted_path
        entry_widget.delete(0, "end")
        entry_widget.insert(0, formatted_path)

def render_campaign_settings_panel():
    for widget in app_state.state["center_content_frame"].winfo_children():
        widget.destroy()
        
    canvas = ctk.CTkScrollableFrame(app_state.state["center_content_frame"], fg_color="transparent")
    canvas.pack(fill="both", expand=True)
        
    ctk.CTkLabel(canvas, text="Global Campaign Settings", font=("Arial", 16, "bold")).pack(anchor="w", pady=(10, 15))
    
    rank_row = ctk.CTkFrame(canvas, fg_color="transparent")
    rank_row.pack(fill="x", pady=4, anchor="w")
    ctk.CTkLabel(rank_row, text="Rank:", font=("Arial", 12, "bold"), width=130, anchor="w").pack(side="left")
    rank_ent = ctk.CTkEntry(rank_row, width=60)
    rank_ent.insert(0, app_state.state.get("campaign_rank", "15"))
    rank_ent.pack(side="left", padx=5)
    rank_ent.bind("<KeyRelease>", lambda e: app_state.state.update({"campaign_rank": rank_ent.get()}))
    
    media_fields = [
        ("Campaign Icon:", "campaign_icon"),
        ("Campaign Image:", "campaign_image")
    ]
    
    for label_text, state_key in media_fields:
        row = ctk.CTkFrame(canvas, fg_color="transparent")
        row.pack(fill="x", pady=4, anchor="w")
        ctk.CTkLabel(row, text=label_text, font=("Arial", 12, "bold"), width=130, anchor="w").pack(side="left")
        
        ent = ctk.CTkEntry(row, width=300)
        ent.insert(0, app_state.state.get(state_key, ""))
        ent.pack(side="left", padx=5)
        ent.bind("<KeyRelease>", lambda e, k=state_key, widget=ent: app_state.state.update({k: widget.get()}))
        
        up_btn = ctk.CTkButton(row, text="📂 Upload", width=70, command=lambda k=state_key, widget=ent: handle_img_upload(k, widget))
        up_btn.pack(side="left", padx=5)

    dir_row = ctk.CTkFrame(canvas, fg_color="transparent")
    dir_row.pack(fill="x", pady=4, anchor="w")
    ctk.CTkLabel(dir_row, text="Wesnoth Path:", font=("Arial", 12, "bold"), width=130, anchor="w").pack(side="left")
    dir_ent = ctk.CTkEntry(dir_row, width=300)
    dir_ent.insert(0, app_state.state.get("wesnoth_directory", ""))
    dir_ent.pack(side="left", padx=5)
    
    def browse_dir():
        d = filedialog.askdirectory(title="Select Wesnoth Installation Folder")
        if d:
            app_state.state["wesnoth_directory"] = d
            app_state.state["discovered_units"] = []
            dir_ent.delete(0, "end")
            dir_ent.insert(0, d)
            
    ctk.CTkButton(dir_row, text="📂 Browse", width=70, command=browse_dir).pack(side="left", padx=5)

    extra_row = ctk.CTkFrame(canvas, fg_color="transparent")
    extra_row.pack(fill="x", pady=4, anchor="w")
    ctk.CTkLabel(extra_row, text="Units Add-on Root:", font=("Arial", 12, "bold"), width=130, anchor="w").pack(side="left")
    extra_ent = ctk.CTkEntry(extra_row, width=300)
    extra_ent.insert(0, app_state.state.get("extra_addon_path", ""))
    extra_ent.pack(side="left", padx=5)
    
    def browse_extra():
        d = filedialog.askdirectory(title="Select Optional Extra Unit Add-on Folder")
        if d:
            app_state.state["extra_addon_path"] = d
            app_state.state["discovered_units"] = []
            extra_ent.delete(0, "end")
            extra_ent.insert(0, d)
            
    ctk.CTkButton(extra_row, text="📂 Browse", width=70, command=browse_extra).pack(side="left", padx=5)
        
    exp_row = ctk.CTkFrame(canvas, fg_color="transparent")
    exp_row.pack(fill="x", pady=4, anchor="w")
    ctk.CTkLabel(exp_row, text="Campaign Export Path:", font=("Arial", 12, "bold"), width=100, anchor="w").pack(side="left")
    
    exp_ent = ctk.CTkEntry(exp_row, width=300)
    exp_ent.insert(0, app_state.state.get("export_directory", ""))
    exp_ent.pack(side="left", padx=5)
    exp_ent.bind("<KeyRelease>", lambda e: app_state.state.update({"export_directory": exp_ent.get()}))
    
    def browse_export():
        d = filedialog.askdirectory(title="Select Folder Where Campaign Directory Will Be Created")
        if d:
            app_state.state["export_directory"] = d
            exp_ent.delete(0, "end")
            exp_ent.insert(0, d)
            
    ctk.CTkButton(exp_row, text="📂 Browse", width=70, command=browse_export).pack(side="left", padx=5)

    ctk.CTkLabel(canvas, text="Campaign Description:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 2))
    desc_box = ctk.CTkTextbox(canvas, width=500, height=80)
    desc_box.insert("1.0", app_state.state["campaign_description"])
    desc_box.pack(anchor="w", pady=(0, 15))
    desc_box.bind("<KeyRelease>", lambda e: app_state.state.update({"campaign_description": desc_box.get("1.0", "end-1c")}))
    
    ctk.CTkLabel(canvas, text="Campaign Difficulties:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(5, 5))
    
    modes = [("Easy", "easy_label", "easy_img"), ("Normal", "normal_label", "normal_img"), ("Hard", "hard_label", "hard_img")]
    for title, lbl_key, img_key in modes:
        row = ctk.CTkFrame(canvas, fg_color="#2b2b2b")
        row.pack(fill="x", pady=4)
        
        ctk.CTkLabel(row, text=f"{title}:", font=("Arial", 12, "bold"), width=70, anchor="w").pack(side="left", padx=10, pady=8)
        
        lbl_ent = ctk.CTkEntry(row, width=120)
        lbl_ent.insert(0, app_state.state[lbl_key])
        lbl_ent.pack(side="left", padx=5, pady=8)
        lbl_ent.bind("<KeyRelease>", lambda e, k=lbl_key, widget=lbl_ent: app_state.state.update({k: widget.get()}))
        
        img_ent = ctk.CTkEntry(row, width=250)
        img_ent.insert(0, app_state.state[img_key])
        img_ent.pack(side="left", padx=5, pady=8)
        img_ent.bind("<KeyRelease>", lambda e, k=img_key, widget=img_ent: app_state.state.update({k: widget.get()}))
        
        up_btn = ctk.CTkButton(row, text="📂 Upload", width=70, command=lambda k=img_key, widget=img_ent: handle_img_upload(k, widget))
        up_btn.pack(side="left", padx=5, pady=8)
        
        pbl_toggle_row = ctk.CTkFrame(canvas, fg_color="transparent")
    pbl_toggle_row.pack(fill="x", pady=(15, 5), anchor="w")
    
    pbl_var = ctk.IntVar(value=1 if app_state.state.get("generate_pbl", True) else 0)
    pbl_panel_frame = ctk.CTkFrame(canvas, fg_color="#222222")
    
    def render_pbl_fields():
        for widget in pbl_panel_frame.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(pbl_panel_frame, text="Server Upload Parameters:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(8, 4))
        
        pbl_fields = [
            ("Version:", "pbl_version"),
            ("Author Name:", "pbl_author"),
            ("Public Email:", "pbl_email"),
            ("Server Passphrase:", "pbl_passphrase")
        ]
        
        for label_text, state_key in pbl_fields:
            row = ctk.CTkFrame(pbl_panel_frame, fg_color="transparent")
            row.pack(fill="x", pady=3, anchor="w")
            ctk.CTkLabel(row, text=label_text, font=("Arial", 11, "bold"), width=140, anchor="w").pack(side="left", padx=10)
            
            ent = ctk.CTkEntry(row, width=220, height=22, font=("Arial", 11))
            ent.insert(0, app_state.state.get(state_key, ""))
            ent.pack(side="left")
            ent.bind("<KeyRelease>", lambda e, k=state_key, w=ent: app_state.state.update({k: w.get()}))
            
        icon_row = ctk.CTkFrame(pbl_panel_frame, fg_color="transparent")
        icon_row.pack(fill="x", pady=3, anchor="w")
        ctk.CTkLabel(icon_row, text="PBL Upload Icon:", font=("Arial", 11, "bold"), width=140, anchor="w").pack(side="left", padx=10)
        
        icon_ent = ctk.CTkEntry(icon_row, width=220, height=22, font=("Arial", 11))
        icon_ent.insert(0, app_state.state.get("campaign_icon", "units/elves-wood/lord.png"))
        icon_ent.pack(side="left")
        icon_ent.bind("<KeyRelease>", lambda e: app_state.state.update({"campaign_icon": icon_ent.get()}))
        
        def browse_pbl_icon():
            canvas.master.master.attributes("-topmost", False)
            file_path = filedialog.askopenfilename(
                title="Select Server Publication Icon Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")]
            )
            canvas.master.master.attributes("-topmost", True)
            if file_path:
                filename = Path(file_path).name
                formatted_path = f"units/{filename}"
                app_state.state["campaign_icon"] = formatted_path
                icon_ent.delete(0, "end")
                icon_ent.insert(0, formatted_path)
                
        ctk.CTkButton(icon_row, text="📂 Browse", width=70, height=20, font=("Arial", 11), command=browse_pbl_icon).pack(side="left", padx=5)

    def toggle_pbl_view():
        is_checked = (pbl_var.get() == 1)
        app_state.state["generate_pbl"] = is_checked
        if is_checked:
            pbl_panel_frame.pack(fill="x", pady=5, padx=5)
            render_pbl_fields()
        else:
            pbl_panel_frame.pack_forget()
            
    pbl_chk = ctk.CTkCheckBox(pbl_toggle_row, text="Create Add-on Server Publication File (_server.pbl)", variable=pbl_var, font=("Arial", 12, "bold"), command=toggle_pbl_view)
    pbl_chk.pack(side="left", padx=5)
    
    toggle_pbl_view()

    def render_pbl_fields():
        for widget in pbl_panel_frame.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(pbl_panel_frame, text="Server Upload Parameters:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(8, 4))
        
        pbl_fields = [
            ("Version:", "pbl_version"),
            ("Author Name:", "pbl_author"),
            ("Public Email:", "pbl_email"),
            ("Server Passphrase:", "pbl_passphrase")
        ]
        
        for label_text, state_key in pbl_fields:
            row = ctk.CTkFrame(pbl_panel_frame, fg_color="transparent")
            row.pack(fill="x", pady=3, anchor="w")
            ctk.CTkLabel(row, text=label_text, font=("Arial", 11, "bold"), width=140, anchor="w").pack(side="left", padx=10)
            
            ent = ctk.CTkEntry(row, width=220, height=22, font=("Arial", 11))
            ent.insert(0, app_state.state.get(state_key, ""))
            ent.pack(side="left")
            ent.bind("<KeyRelease>", lambda e, k=state_key, w=ent: app_state.state.update({k: w.get()}))
            
        icon_row = ctk.CTkFrame(pbl_panel_frame, fg_color="transparent")
        icon_row.pack(fill="x", pady=3, anchor="w")
        ctk.CTkLabel(icon_row, text="PBL Upload Icon:", font=("Arial", 11, "bold"), width=140, anchor="w").pack(side="left", padx=10)
        
        icon_ent = ctk.CTkEntry(icon_row, width=220, height=22, font=("Arial", 11))
        icon_ent.insert(0, app_state.state.get("campaign_icon", "units/elves-wood/lord.png"))
        icon_ent.pack(side="left")
        icon_ent.bind("<KeyRelease>", lambda e: app_state.state.update({"campaign_icon": icon_ent.get()}))
        
        def browse_pbl_icon():
            canvas.master.master.attributes("-topmost", False)
            file_path = filedialog.askopenfilename(
                title="Select Server Publication Icon Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")]
            )
            canvas.master.master.attributes("-topmost", True)
            if file_path:
                filename = Path(file_path).name
                formatted_path = f"units/{filename}"
                app_state.state["campaign_icon"] = formatted_path
                icon_ent.delete(0, "end")
                icon_ent.insert(0, formatted_path)
                
        ctk.CTkButton(icon_row, text="📂 Browse", width=70, height=20, font=("Arial", 11), command=browse_pbl_icon).pack(side="left", padx=5)

def render_workspace():
    for widget in app_state.state["center_content_frame"].winfo_children():
        widget.destroy()
        
    idx = app_state.state["current_index"]
    if idx is None or not app_state.state["scenarios"]:
        placeholder = ctk.CTkLabel(app_state.state["center_content_frame"], text="Wesnoth Campaign Maker\n\nClick '+ Add Scenario' on the left to start.", font=("Arial", 15))
        placeholder.pack(expand=True)
        return
        
    data = app_state.state["scenarios"][idx]
    
    title_row = ctk.CTkFrame(app_state.state["center_content_frame"], fg_color="transparent")
    title_row.pack(fill="x", pady=(15, 10), anchor="w")
    
    title_lbl = ctk.CTkLabel(title_row, text="Scenario Name: ", font=("Arial", 13, "bold"), width=130, anchor="w")
    title_lbl.pack(side="left")
    
    app_state.state["scenario_title_input"] = ctk.CTkEntry(title_row, width=400)
    app_state.state["scenario_title_input"].insert(0, data["title"])
    app_state.state["scenario_title_input"].pack(side="left", padx=10)
    
    map_row = ctk.CTkFrame(app_state.state["center_content_frame"], fg_color="transparent")
    map_row.pack(fill="x", pady=10, anchor="w")
    
    map_lbl = ctk.CTkLabel(map_row, text="Scenario Map File: ", font=("Arial", 13, "bold"), width=130, anchor="w")
    map_lbl.pack(side="left")
    
    upload_btn = ctk.CTkButton(map_row, text="📂 Upload Map File", command=handle_upload, width=150)
    upload_btn.pack(side="left", padx=(10, 0))
    
    if data["map_name"]:
        turns_row = ctk.CTkFrame(app_state.state["center_content_frame"], fg_color="transparent")
        turns_row.pack(fill="x", pady=10, anchor="w")
        ctk.CTkLabel(turns_row, text="Turn Limits (E/N/H):", font=("Arial", 13, "bold"), width=130, anchor="w").pack(side="left")
        
        t_easy = ctk.CTkEntry(turns_row, width=50)
        t_easy.insert(0, data.get("turns_easy", "24"))
        t_easy.pack(side="left", padx=2)
        t_easy.bind("<KeyRelease>", lambda e: data.update({"turns_easy": t_easy.get()}))
        
        t_norm = ctk.CTkEntry(turns_row, width=50)
        t_norm.insert(0, data.get("turns_normal", "22"))
        t_norm.pack(side="left", padx=2)
        t_norm.bind("<KeyRelease>", lambda e: data.update({"turns_normal": t_norm.get()}))
        
        t_hard = ctk.CTkEntry(turns_row, width=50)
        t_hard.insert(0, data.get("turns_hard", "20"))
        t_hard.pack(side="left", padx=2)
        t_hard.bind("<KeyRelease>", lambda e: data.update({"turns_hard": t_hard.get()}))

        def open_story_editor():
            win = ctk.CTkToplevel()
            win.title(f"Story Prologue: {data['title']}")
            win.geometry("500x500")
            win.attributes("-topmost", True)
            
            sub_scroll = ctk.CTkScrollableFrame(win)
            sub_scroll.pack(fill="both", expand=True, padx=10, pady=10)
            
            parts_list = data.get("story_parts", [])
            
            def handle_bg_browse(p_idx, bge_widget):
                win.attributes("-topmost", False)
                file_path = filedialog.askopenfilename(
                    title="Select Story Background Image",
                    filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")]
                )
                win.attributes("-topmost", True)
                if file_path:
                    filename = Path(file_path).name
                    parts_list[p_idx]["background"] = filename
                    bge_widget.delete(0, "end")
                    bge_widget.insert(0, filename)
            
            def render_parts():
                for widget in sub_scroll.winfo_children():
                    widget.destroy()
                for p_idx, part in enumerate(parts_list):
                    box = ctk.CTkFrame(sub_scroll, fg_color="#1a1a1a")
                    box.pack(fill="x", pady=4, padx=5)
                    
                    hdr = ctk.CTkFrame(box, fg_color="transparent")
                    hdr.pack(fill="x", pady=2)
                    ctk.CTkLabel(hdr, text=f"Slide {p_idx+1}", font=("Arial", 11, "bold")).pack(side="left", padx=5)
                    
                    del_btn = ctk.CTkButton(hdr, text="🗑️", width=28, height=18, fg_color="transparent", text_color="#A83232", hover_color="#4a1a1a",
                                             command=lambda idx=p_idx: [parts_list.pop(idx), render_parts()])
                    del_btn.pack(side="right", padx=5)
                    
                    bg_row = ctk.CTkFrame(box, fg_color="transparent")
                    bg_row.pack(fill="x", pady=2)
                    ctk.CTkLabel(bg_row, text="Background asset:", font=("Arial", 11), width=110, anchor="w").pack(side="left", padx=5)
                    
                    bge = ctk.CTkEntry(bg_row, width=150, height=20, font=("Arial", 11))
                    bge.insert(0, part.get("background", ""))
                    bge.pack(side="left")
                    bge.bind("<KeyRelease>", lambda e, idx=p_idx, widget=bge: parts_list[idx].update({"background": widget.get()}))
                    
                    bg_btn = ctk.CTkButton(bg_row, text="📂 Browse", width=70, height=20, font=("Arial", 11), 
                                            command=lambda idx=p_idx, widget=bge: handle_bg_browse(idx, widget))
                    bg_btn.pack(side="left", padx=5)
                    
                    ctk.CTkLabel(box, text="Narration Text:", font=("Arial", 11)).pack(anchor="w", padx=5, pady=(4, 2))
                    tb = ctk.CTkTextbox(box, width=440, height=50, font=("Arial", 12))
                    tb.insert("1.0", part.get("story", ""))
                    tb.pack(fill="x", padx=5, pady=(0, 5))
                    tb.bind("<KeyRelease>", lambda e, idx=p_idx, widget=tb: parts_list[idx].update({"story": widget.get("1.0", "end-1c")}))
                    
                ctk.CTkButton(sub_scroll, text="➕ Add Story Slide", width=140, fg_color="#2b2b2b", 
                               command=lambda: [parts_list.append({"background": "story.jpg", "story": ""}), render_parts()]).pack(pady=10)
                               
            render_parts()

        ctk.CTkButton(turns_row, text="📖 Manage Story Intro", width=130, height=24, fg_color="#2b2b2b", command=open_story_editor).pack(side="left", padx=15)

    events_container = ctk.CTkFrame(app_state.state["center_content_frame"], fg_color="transparent")
    events_container.pack(fill="both", expand=True, pady=(15, 0))
    event_manager.render_events_sidebar(events_container)



def boot():
    ctk.set_appearance_mode("Dark")
    root = ctk.CTk()
    root.title("Wesnoth Campaign Maker")
    root.geometry("1150x750")
    
    sidebar = ctk.CTkFrame(root, width=250, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    
    campaign_name_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    campaign_name_frame.pack(fill="x", pady=(15, 10), padx=10)
    ctk.CTkButton(sidebar, text="⚙️ Global Campaign Configs", fg_color="#3b3b3b", command=switch_to_global).pack(fill="x", padx=10, pady=(5, 10))

    app_state.campaign_name_input = ctk.CTkEntry(campaign_name_frame, font=("Arial", 14, "bold"))
    app_state.campaign_name_input.insert(0, app_state.state["campaign_name"])
    app_state.campaign_name_input.pack(fill="x")
    
    top_button_row = ctk.CTkFrame(sidebar, fg_color="transparent")
    top_button_row.pack(fill="x", padx=10, pady=(0, 5))
    
    import_btn = ctk.CTkButton(top_button_row, text="📂 Import", fg_color="#1f6aa5", hover_color="#144870", command=handle_import)
    import_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    reset_btn = ctk.CTkButton(top_button_row, text="🔄 Reset", fg_color="#A83232", hover_color="#822525", command=handle_reset)
    reset_btn.pack(side="right", fill="x", expand=True)
    
    ctk.CTkButton(sidebar, text="➕ Add Scenario", fg_color="#2eb85c", hover_color="#228b44", command=handle_add).pack(fill="x", padx=10, pady=(0, 15))
    
    app_state.state["scenario_list_frame"] = ctk.CTkScrollableFrame(sidebar, width=230)
    app_state.state["scenario_list_frame"].pack(fill="both", expand=True, padx=5, pady=5)
    
    footer = ctk.CTkFrame(root, height=50, corner_radius=0)
    footer.pack(side="bottom", fill="x")
    ctk.CTkButton(footer, text="🚀 Generate Campaign", font=("Arial", 13, "bold"), command=handle_export).pack(side="right", padx=20, pady=10)
    
    app_state.state["center_content_frame"] = ctk.CTkFrame(root, fg_color="transparent")
    app_state.state["center_content_frame"].pack(side="right", fill="both", expand=True, padx=20, pady=10)
    
    render_workspace()
    root.mainloop()


if __name__ == "__main__":
    boot()

