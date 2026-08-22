# main.py
# Ghost DNS by Swir v6.0 APEX - JSON Database Edition
import os
import sys
import ctypes
import subprocess
import threading
import time
import re
import webbrowser
import json
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Flag to hide popping up black CMD windows in Windows
CREATE_NO_WINDOW = 0x08000000 
JSON_FILE = "custom_dns.json"

# --- STATIC FACTORY DNS DATABASE ---
DNS_PRESETS = {
    "■ PERFORMANCE & GAMING (Ultra-Fast)": [
        {"id": "cloudflare", "name": "Cloudflare DNS", "primary": "1.1.1.1", "secondary": "1.0.0.1", "desc": "Lowest latency and fastest response time."},
        {"id": "gcore", "name": "G-Core DNS", "primary": "95.85.95.85", "secondary": "2.56.220.2", "desc": "Optimized for CDN and online gaming stability."},
        {"id": "google_public", "name": "Google Public DNS", "primary": "8.8.8.8", "secondary": "8.8.4.4", "desc": "Universal, global, and reliable DNS server."},
        {"id": "level3", "name": "Level3 Core DNS", "primary": "4.2.2.1", "secondary": "4.2.2.2", "desc": "Tier-1 infrastructure, powerful network stability."}
    ],
    "■ PRIVACY & SECURITY": [
        {"id": "quad9", "name": "Quad9 Secure", "primary": "9.9.9.9", "secondary": "149.112.112.112", "desc": "Blocks access to malicious domains and phishing."},
        {"id": "mullvad", "name": "Mullvad DNS", "primary": "194.242.2.2", "secondary": "194.242.2.3", "desc": "Maximum privacy, no query logging."},
        {"id": "comodo", "name": "Comodo Secure", "primary": "8.26.56.26", "secondary": "8.20.247.20", "desc": "Advanced protection against malicious code on the fly."}
    ],
    "■ AD CONTROL & FILTERING": [
        {"id": "adguard_standard", "name": "AdGuard Standard", "primary": "94.140.14.14", "secondary": "94.140.15.15", "desc": "Automatically blocks ads and trackers on the web."},
        {"id": "adguard_family", "name": "AdGuard Family", "primary": "94.140.14.15", "secondary": "94.140.15.16", "desc": "Blocks ads and unverified/adult content."},
        {"id": "opendns_home", "name": "OpenDNS Home (Cisco)", "primary": "208.67.222.222", "secondary": "208.67.220.220", "desc": "Cloud filtering from Cisco, great home protection."},
        {"id": "cleanbrowsing", "name": "CleanBrowsing Security", "primary": "185.228.168.9", "secondary": "185.228.169.9", "desc": "Blocks phishing sites and malware."}
    ],
    "■ SYSTEM": [
        {"id": "dhcp_default", "name": "AUTOMATIC DNS (DHCP)", "primary": "DHCP", "secondary": "DHCP", "desc": "Restore default DNS settings assigned by your router."}
    ]
}

THEME_MODE = "dark"
COLOR_ACCENT = "#00bcff"  
COLOR_ACCENT_HOVER = "#3fbfff"
COLOR_ACTIVE_BG = "#0c1b26"   
COLOR_BG_MAIN = "#101010"
COLOR_BG_CARD = "#1a1a1a"
COLOR_TEXT_PRIMARY = "#ffffff"
COLOR_TEXT_SECONDARY = "#888888"
COLOR_SUCCESS = "#00ff00"
COLOR_WARNING = "#ffaa00"     
COLOR_DANGER = "#ff4444"

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

ctk.set_appearance_mode(THEME_MODE)
ctk.set_default_color_theme("blue") 

class DNSChangerProApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ghost DNS by Swir v6.0 PRO")
        self.geometry("440x920")  # Height adjusted for scroll and bottom panel
        self.resizable(False, False)
        
        if not is_admin():
            self.show_admin_warning()
            sys.exit()

        self.current_interface = "Searching for network..."
        self.active_id = None
        self.card_widgets = {}
        self.is_applying = False 
        self.custom_presets = [] # Storing dynamic user profiles
        
        # Loading JSON database from the disk next to EXE
        self.load_custom_dns_json()

        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color=COLOR_BG_MAIN, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

        # Header
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="GHOST DNS", font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"), text_color=COLOR_ACCENT)
        self.title_label.pack(side="left", anchor="s")

        self.author_label = ctk.CTkLabel(self.header_frame, text="by Swir", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=COLOR_TEXT_PRIMARY)
        self.author_label.pack(side="left", padx=5, anchor="s", pady=(0, 2))

        # Network status panel
        self.status_panel = ctk.CTkFrame(self.main_container, fg_color="#141414", corner_radius=10, border_width=1, border_color="#2a2a2a")
        self.status_panel.pack(fill="x", padx=15, pady=10)

        self.status_main_text = ctk.CTkLabel(self.status_panel, text="Fetching current configuration...", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT_PRIMARY)
        self.status_main_text.pack(pady=(12, 2))

        self.status_ips_text = ctk.CTkLabel(self.status_panel, text="Reading system...", font=ctk.CTkFont(family="Consolas", size=11), text_color=COLOR_ACCENT)
        self.status_ips_text.pack(pady=(0, 10))
        
        self.refresh_btn = ctk.CTkButton(
            self.status_panel, text="↺ Refresh connection status and ping", height=28, 
            fg_color="#1f1f1f", hover_color="#2b2b2b", text_color=COLOR_TEXT_PRIMARY, 
            font=ctk.CTkFont(weight="bold", size=11), corner_radius=6, command=self.refresh_all
        )
        self.refresh_btn.pack(fill="x", padx=15, pady=(0, 12))

        # DNS scrollable list
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent", height=420)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Rendering tiles (Factory)
        self.render_dns_cards()
        
        # Rendering header and tiles from JSON file (User)
        self.custom_section_label = None
        self.render_custom_dns_cards()

        # Panel for creating and saving custom DNS to JSON file
        self.custom_dns_frame = ctk.CTkFrame(self.main_container, fg_color=COLOR_BG_CARD, corner_radius=10, border_width=1, border_color="#222222")
        self.custom_dns_frame.pack(fill="x", padx=15, pady=10)

        self.custom_title = ctk.CTkLabel(self.custom_dns_frame, text="⚡ SAVE NEW DNS SERVER TO FILE", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_ACCENT)
        self.custom_title.pack(anchor="w", padx=15, pady=(10, 5))

        self.custom_name_entry = ctk.CTkEntry(self.custom_dns_frame, placeholder_text="Profile name (e.g. My DNS)", height=30)
        self.custom_name_entry.pack(fill="x", padx=15, pady=3)

        ip_row = ctk.CTkFrame(self.custom_dns_frame, fg_color="transparent")
        ip_row.pack(fill="x", padx=15, pady=3)
        
        self.custom_primary_entry = ctk.CTkEntry(ip_row, placeholder_text="Primary IPv4", height=30, font=ctk.CTkFont(family="Consolas"))
        self.custom_primary_entry.pack(side="left", fill="x", expand=True, padx=(0, 3))
        
        self.custom_secondary_entry = ctk.CTkEntry(ip_row, placeholder_text="Secondary IPv4", height=30, font=ctk.CTkFont(family="Consolas"))
        self.custom_secondary_entry.pack(side="right", fill="x", expand=True, padx=(3, 0))

        self.custom_apply_btn = ctk.CTkButton(
            self.custom_dns_frame, text="SAVE AND ADD TO LIST", height=32, corner_radius=8,
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color="#000000",
            font=ctk.CTkFont(weight="bold"), command=self.add_and_save_custom_dns
        )
        self.custom_apply_btn.pack(fill="x", padx=15, pady=(5, 12))

        # Author footer with link
        self.footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.footer_frame.pack(fill="x", side="bottom", pady=(0, 10))

        self.github_link = ctk.CTkLabel(self.footer_frame, text="🔗 GitHub.com/Swir", font=ctk.CTkFont(size=11, underline=True), text_color=COLOR_TEXT_SECONDARY, cursor="hand2")
        self.github_link.pack(anchor="center")
        self.github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Swir"))

        self.refresh_all()

    def show_admin_warning(self):
        root = tk.Tk(); root.withdraw()
        tk.messagebox.showwarning("Insufficient Permissions", "Run the program as ADMINISTRATOR!")
        root.destroy()

    # --- JSON DATABASE HANDLING ---
    
    def load_custom_dns_json(self):
        """Loads user server database from JSON file."""
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    self.custom_presets = json.load(f)
            except:
                self.custom_presets = []
        else:
            self.custom_presets = []

    def save_custom_dns_json(self):
        """Saves the current user server list to a JSON file on disk."""
        try:
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(self.custom_presets, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Save error", f"Cannot save JSON configuration: {e}")

    # --- UI BUILDING ---

    def update_ui_state(self, active_name="Unknown", active_ips="None"):
        if self.active_id == "dhcp_default":
            self.status_main_text.configure(text=f"Active: {active_name}", text_color=COLOR_TEXT_PRIMARY)
            self.status_ips_text.configure(text=f"Adapter: {self.current_interface}", text_color=COLOR_TEXT_SECONDARY)
        else:
            self.status_main_text.configure(text=f"Active: {active_name}", text_color=COLOR_SUCCESS)
            self.status_ips_text.configure(text=f"IP Addresses: {active_ips}", text_color=COLOR_ACCENT)

        for server_id, widgets in self.card_widgets.items():
            card = widgets['card']
            btn = widgets['apply_btn']
            
            if server_id == self.active_id:
                card.configure(border_color=COLOR_ACCENT, border_width=2, fg_color=COLOR_ACTIVE_BG)
                btn.configure(text="ACTIVE", fg_color="#1a1a1a", text_color="#555", state="disabled")
            else:
                card.configure(border_color="#222222", border_width=1, fg_color=COLOR_BG_CARD)
                btn.configure(text="APPLY", fg_color=COLOR_ACCENT, text_color="#000000", state="normal")

        self.custom_apply_btn.configure(text="SAVE AND ADD TO LIST", fg_color=COLOR_ACCENT, state="normal")

    def render_dns_cards(self):
        """Renders rigid, factory DNS servers."""
        for category, servers in DNS_PRESETS.items():
            cat_label = ctk.CTkLabel(self.scrollable_frame, text=category, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_SECONDARY)
            cat_label.pack(anchor="w", padx=5, pady=(10, 2))

            for server in servers:
                self.create_single_card(server)

    def render_custom_dns_cards(self):
        """Dynamically builds or refreshes the server section from the JSON file."""
        if not self.custom_presets:
            return

        if not self.custom_section_label:
            self.custom_section_label = ctk.CTkLabel(self.scrollable_frame, text="■ YOUR CUSTOM DNS SERVERS (From JSON file)", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_ACCENT)
            self.custom_section_label.pack(anchor="w", padx=5, pady=(20, 2))

        for server in self.custom_presets:
            if server["id"] not in self.card_widgets:
                self.create_single_card(server)

    def create_single_card(self, server):
        """Creates a unified tile for any DNS type."""
        server_id = server["id"]
        
        card = ctk.CTkFrame(self.scrollable_frame, fg_color=COLOR_BG_CARD, corner_radius=8, border_width=1, border_color="#222222")
        card.pack(fill="x", padx=5, pady=4)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=12, pady=10)

        left_col = ctk.CTkFrame(content, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True)

        name_lbl = ctk.CTkLabel(left_col, text=server["name"], font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT_PRIMARY)
        name_lbl.pack(anchor="w")

        ips_text = f"{server['primary']} | {server['secondary']}" if server_id != "dhcp_default" else "Auto IP (DHCP)"
        ips_lbl = ctk.CTkLabel(left_col, text=ips_text, font=ctk.CTkFont(family="Consolas", size=11), text_color=COLOR_ACCENT)
        ips_lbl.pack(anchor="w")

        right_col = ctk.CTkFrame(content, fg_color="transparent")
        right_col.pack(side="right", anchor="e")

        ping_lbl = ctk.CTkLabel(right_col, text="⚡ -- ms", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_TEXT_SECONDARY)
        if server_id != "dhcp_default":
            ping_lbl.pack(anchor="e", pady=(0, 2))

        apply_btn = ctk.CTkButton(
            right_col, text="APPLY", width=75, height=26, corner_radius=6,
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color="#000000",
            font=ctk.CTkFont(size=11, weight="bold"), command=lambda s=server: self.apply_dns_profile(s)
        )
        apply_btn.pack(anchor="e")

        self.card_widgets[server_id] = {'card': card, 'apply_btn': apply_btn, 'ping_lbl': ping_lbl}

    # --- NETWORK AND OPERATIONAL LOGIC ---

    def refresh_all(self):
        if self.is_applying: return
        threading.Thread(target=self.detect_current_dns, daemon=True).start()
        
        # Ping refresh loop gathers data from both factory and user-added profiles
        for server_id, widgets in self.card_widgets.items():
            if server_id != "dhcp_default":
                widgets['ping_lbl'].configure(text="⚡ testing...", text_color=COLOR_TEXT_SECONDARY)
                threading.Thread(target=self.ping_server_worker, args=(server_id,), daemon=True).start()

    def ping_server_worker(self, server_id):
        primary_ip = None
        # First search in factory presets
        for cat in DNS_PRESETS.values():
            for s in cat:
                if s["id"] == server_id: primary_ip = s["primary"]
        # If not found, search in custom JSON profiles
        if not primary_ip:
            for s in self.custom_presets:
                if s["id"] == server_id: primary_ip = s["primary"]

        if not primary_ip or primary_ip == "DHCP": return

        try:
            output = subprocess.check_output(f"ping -n 2 -w 600 {primary_ip}", shell=True, creationflags=CREATE_NO_WINDOW).decode("cp852")
            match = re.search(r'(Średnia|Average)\s*=\s*(\d+)\s*ms', output)
            if match:
                ping_val = int(match.group(2))
                color = COLOR_SUCCESS if ping_val < 25 else (COLOR_WARNING if ping_val < 70 else COLOR_DANGER)
                self.after(0, lambda: self.card_widgets[server_id]['ping_lbl'].configure(text=f"⚡ {ping_val} ms", text_color=color))
            else:
                self.after(0, lambda: self.card_widgets[server_id]['ping_lbl'].configure(text="⚡ Timeout", text_color=COLOR_DANGER))
        except:
            self.after(0, lambda: self.card_widgets[server_id]['ping_lbl'].configure(text="⚡ Error", text_color=COLOR_DANGER))

    def detect_current_dns(self):
        try:
            cmd_adapter = "Get-NetAdapter | Where-Object {$_.Status -eq 'Up' -and $_.Virtual -eq $false} | Select-Object -ExpandProperty Name"
            raw_interface_output = subprocess.check_output(["powershell", "-Command", cmd_adapter], creationflags=CREATE_NO_WINDOW)
            try: interface = raw_interface_output.decode("utf-8").strip().split('\n')[0].strip()
            except: interface = raw_interface_output.decode("cp852").strip().split('\n')[0].strip()

            if not interface:
                self.current_interface = "No connection"
                self.active_id = None
                self.after(0, self.update_ui_state)
                return

            self.current_interface = interface
            cmd_dns = f"Get-DnsClientServerAddress -InterfaceAlias '{interface}' -AddressFamily IPv4 | Select-Object -ExpandProperty ServerAddresses"
            raw_dns_output = subprocess.check_output(["powershell", "-Command", cmd_dns], creationflags=CREATE_NO_WINDOW).decode("ascii").strip()
            
            if not raw_dns_output:
                self.active_id = "dhcp_default"
                active_name = "AUTOMATIC DNS (DHCP)"
                active_ips = "Automatic"
            else:
                ips = raw_dns_output.replace('\r', '').split('\n')
                primary_found = ips[0].strip()
                active_ips = f"{primary_found}, {ips[1].strip()}" if len(ips) > 1 else primary_found
                
                self.active_id = "custom_user"
                active_name = "Custom / Unknown DNS"

                # Mapping with factory servers
                for cat in DNS_PRESETS.values():
                    for server in cat:
                        if server["primary"] == primary_found:
                            self.active_id = server["id"]
                            active_name = server["name"]
                
                # Scanning and matching with your JSON database
                for server in self.custom_presets:
                    if server["primary"] == primary_found:
                        self.active_id = server["id"]
                        active_name = server["name"]

            self.after(0, lambda: self.update_ui_state(active_name, active_ips))
        except:
            self.after(0, lambda: self.status_main_text.configure(text="Configuration read error", text_color=COLOR_DANGER))

    def add_and_save_custom_dns(self):
        """Fetches input data, validates it, saves to JSON and creates a new tile in the list."""
        if self.is_applying: return
        name = self.custom_name_entry.get().strip()
        primary = self.custom_primary_entry.get().strip()
        secondary = self.custom_secondary_entry.get().strip()

        if not name or not primary or not secondary:
            messagebox.showwarning("Missing data", "Fill in all fields: Name, Primary and Secondary IP!")
            return

        ip_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not re.match(ip_pattern, primary) or not re.match(ip_pattern, secondary):
            messagebox.showerror("Invalid format", "The provided IP addresses are not valid IPv4 addresses!")
            return

        # Generating a safe ID based on time to avoid naming conflicts
        unique_id = f"json_dns_{int(time.time())}"

        new_server = {
            "id": unique_id,
            "name": f"★ {name}",
            "primary": primary,
            "secondary": secondary,
            "desc": "User: Profile loaded from the custom_dns.json database file"
        }

        # Injecting into RAM and saving to disk
        self.custom_presets.append(new_server)
        self.save_custom_dns_json()

        # Rendering the new tile live on screen without restarting the program
        self.render_custom_dns_cards()

        # Clearing text fields for convenience
        self.custom_name_entry.delete(0, tk.END)
        self.custom_primary_entry.delete(0, tk.END)
        self.custom_secondary_entry.delete(0, tk.END)

        # Firing ping automatically only for the newly added tile
        self.card_widgets[unique_id]['ping_lbl'].configure(text="⚡ testing...", text_color=COLOR_TEXT_SECONDARY)
        threading.Thread(target=self.ping_server_worker, args=(unique_id,), daemon=True).start()

        # Immediate update of frame state
        self.detect_current_dns()

    def apply_dns_profile(self, server_config):
        if self.is_applying: return
        self.is_applying = True
        
        target_id = server_config["id"]
        
        for s_id, widgets in self.card_widgets.items():
            widgets['apply_btn'].configure(state="disabled")
            if s_id == target_id:
                widgets['card'].configure(border_color=COLOR_WARNING, border_width=2)
                widgets['apply_btn'].configure(text="⏳", fg_color="#333")
                
        self.custom_apply_btn.configure(state="disabled")
        
        threading.Thread(target=self._execute_dns_system_commands, args=(server_config,), daemon=True).start()

    def _execute_dns_system_commands(self, server_config):
        try:
            time.sleep(0.3)
            if not self.current_interface or "No connection" in self.current_interface: raise Exception()

            subprocess.run("ipconfig /flushdns", shell=True, creationflags=CREATE_NO_WINDOW)

            if server_config["id"] == "dhcp_default":
                subprocess.run(f'netsh interface ip set dns name="{self.current_interface}" source=dhcp', shell=True, creationflags=CREATE_NO_WINDOW)
            else:
                pri = server_config["primary"]
                sec = server_config["secondary"]
                subprocess.run(f'netsh interface ip set dns name="{self.current_interface}" source=static address={pri}', shell=True, creationflags=CREATE_NO_WINDOW)
                subprocess.run(f'netsh interface ip add dns name="{self.current_interface}" addr={sec} index=2', shell=True, creationflags=CREATE_NO_WINDOW)
            
            subprocess.run("ipconfig /flushdns", shell=True, creationflags=CREATE_NO_WINDOW)
            time.sleep(0.5)
        except:
            self.after(0, lambda: messagebox.showerror("Error", "Failed to change DNS."))
        finally:
            self.is_applying = False
            self.detect_current_dns()


if __name__ == "__main__":
    app = DNSChangerProApp()
    app.mainloop()
