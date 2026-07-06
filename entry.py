from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk
import app_state
import generator
import importer

def save_active_inputs():
    idx = app_state.state["current_index"]
    if idx is not None and idx < len(app_state.state["scenarios"]):
        if app_state.state["scenario_title_input"]:
            app_state.state["scenarios"][idx]["title"] = app_state.state["scenario_title_input"].get()

def handle_add():
    save_active_inputs()
    blank_scenario = {
        "title": f"Scenario {len(app_state.state['scenarios']) + 1}",
        "map_name": None,
        "map_data": "",
        "captains_count": 0
    }
    app_state.state["scenarios"].append(blank_scenario)
    app_state.state["current_index"] = len(app_state.state["scenarios"]) - 1
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
        scenarios = importer.import_campaign_folder(selected_dir)
        if not scenarios:
            messagebox.showwarning("Import Failed", "No valid .cfg scenario files were found inside this folder.")
            return
            
        app_state.state["campaign_name"] = Path(selected_dir).name.replace("wesnoth_addon_", "").replace("_", " ").title()
        app_state.state["scenarios"] = scenarios
        app_state.state["current_index"] = 0
        refresh_sidebar()
        render_workspace()
        messagebox.showinfo("Import Success", f"Successfully imported {len(scenarios)} scenarios!")

def handle_export():
    save_active_inputs()
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

def render_workspace():
    for widget in app_state.state["center_content_frame"].winfo_children():
        widget.destroy()
        
    idx = app_state.state["current_index"]
    if idx is None or not app_state.state["scenarios"]:
        placeholder = ctk.CTkLabel(app_state.state["center_content_frame"], text="Wesnoth Campaign Maker\n\nClick '+ Add Scenario' on the left to start.", font=("Arial", 15))
        placeholder.pack(expand=True)
        return
        
    data = app_state.state["scenarios"][idx]
    
    ctk.CTkLabel(app_state.state["center_content_frame"], text="Scenario Title Name:", font=("Arial", 13, "bold")).pack(anchor="w", pady=(10, 2))
    app_state.state["scenario_title_input"] = ctk.CTkEntry(app_state.state["center_content_frame"], width=400)
    app_state.state["scenario_title_input"].insert(0, data["title"])
    app_state.state["scenario_title_input"].pack(anchor="w", pady=(0, 15))
    
    ctk.CTkLabel(app_state.state["center_content_frame"], text="Required Geographic Scenario Map (.map):", font=("Arial", 13, "bold")).pack(anchor="w", pady=(5, 2))
    status_text = f"Linked File: {data['map_name']}" if data["map_name"] else "Status: No Map Assigned"
    status_color = "#1f6aa5" if data["map_name"] else "#A83232"
    ctk.CTkLabel(app_state.state["center_content_frame"], text=status_text, text_color=status_color).pack(anchor="w")
    
    ctk.CTkButton(app_state.state["center_content_frame"], text="📂 Upload Map File", command=handle_upload).pack(anchor="w", pady=(5, 15))
    
    if data["map_name"]:
        ctk.CTkLabel(
            app_state.state["center_content_frame"], 
            text=f"✅ Map Verified: Extracted {data['captains_count']} Starting Team Slots.", 
            text_color="green", font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 15))
    else:
        ctk.CTkLabel(
            app_state.state["center_content_frame"], 
            text="⚠️ Missing Map: Defaulting scenario generation to 2 player sides (Team 1 vs Team 2).", 
            text_color="#D97706", font=("Arial", 12, "italic")
        ).pack(anchor="w", pady=(0, 15))

def boot():
    ctk.set_appearance_mode("Dark")
    root = ctk.CTk()
    root.title("Wesnoth Campaign Maker")
    root.geometry("850x550")
    
    sidebar = ctk.CTkFrame(root, width=250, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    ctk.CTkLabel(sidebar, text="Campaign Structure", font=("Arial", 15, "bold")).pack(pady=15, padx=10, anchor="w")
    
    ctk.CTkButton(sidebar, text="➕ Add Scenario", fg_color="#2eb85c", hover_color="#228b44", command=handle_add).pack(fill="x", padx=10, pady=(0, 5))
    ctk.CTkButton(sidebar, text="📂 Import Folder", fg_color="#2b2b2b", hover_color="#3b3b3b", command=handle_import).pack(fill="x", padx=10, pady=(0, 15))
    
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
