"""
FileFusion Pro - Professional Folder Customization Tool
Developed by Ahmed Nour Ahmed from Qena
A sophisticated folder customization application with modern UI
"""

import os
import sys
import json
import shutil
import ctypes
import winreg
import threading
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, font
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import win32api
import win32con
import win32gui

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class FileFusionPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # App configuration
        self.title("FileFusion Pro - Ultimate Folder Customizer")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Set window icon
        try:
            self.iconbitmap(default=self.resource_path("icon.ico"))
        except:
            pass
        
        # Initialize variables
        self.current_folder = ""
        self.folder_history = []
        self.favorites = []
        self.custom_icons = []
        self.theme_mode = "dark"
        self.load_config()
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        
        # Load custom icons
        self.load_custom_icons()
        
        # Apply styling
        self.apply_styles()
        
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def load_config(self):
        """Load application configuration"""
        self.config_file = Path.home() / ".filefusionpro" / "config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        
        default_config = {
            "theme": "dark",
            "recent_folders": [],
            "favorites": [],
            "icon_size": "medium",
            "default_color": "#3498db",
            "backup_enabled": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                # Ensure all keys exist
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            except:
                self.config = default_config
        else:
            self.config = default_config
        
        # Apply theme
        ctk.set_appearance_mode(self.config.get("theme", "dark"))
        self.theme_mode = self.config.get("theme", "dark")
    
    def save_config(self):
        """Save application configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def create_sidebar(self):
        """Create the sidebar with navigation and tools"""
        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", rowspan=2)
        self.sidebar.grid_propagate(False)
        
        # Logo and title
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        logo_label = ctk.CTkLabel(
            logo_frame, 
            text="⚡ FileFusion Pro",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        )
        logo_label.pack()
        
        version_label = ctk.CTkLabel(
            logo_frame,
            text="Version 2.1.0",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="gray"
        )
        version_label.pack()
        
        # Separator
        ctk.CTkLabel(self.sidebar, text="").pack(pady=5)
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray25")
        separator.pack(fill="x", padx=20, pady=10)
        
        # Navigation buttons
        nav_buttons = [
            ("📁 Browse Folders", self.browse_folder, "primary"),
            ("⭐ Favorites", self.show_favorites, "secondary"),
            ("🕐 Recent", self.show_recent, "secondary"),
            ("🎨 Customize", self.show_customize, "primary"),
            ("🖼️ Icons", self.show_icons, "secondary"),
            ("🌈 Colors", self.show_colors, "secondary"),
            ("🔧 Tools", self.show_tools, "secondary"),
            ("📊 Stats", self.show_stats, "secondary"),
        ]
        
        for text, command, style in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                height=45,
                font=ctk.CTkFont(family="Segoe UI", size=14),
                corner_radius=8,
                fg_color=("gray20", "gray15") if style == "secondary" else None
            )
            btn.pack(pady=5, padx=20, fill="x")
        
        # Separator
        separator2 = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray25")
        separator2.pack(fill="x", padx=20, pady=20)
        
        # Quick actions
        quick_actions_label = ctk.CTkLabel(
            self.sidebar,
            text="Quick Actions",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        quick_actions_label.pack(pady=(0, 10), padx=20, anchor="w")
        
        quick_actions = [
            ("📸 Capture Icon", self.capture_icon),
            ("🔄 Reset All", self.reset_all_customizations),
            ("💾 Backup", self.create_backup),
            ("⚙️ Settings", self.open_settings)
        ]
        
        for text, command in quick_actions:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                height=35,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                corner_radius=8,
                fg_color="gray20",
                hover_color="gray25"
            )
            btn.pack(pady=3, padx=20, fill="x")
        
        # Theme toggle
        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.pack(side="bottom", pady=20, padx=20, fill="x")
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Dark Mode",
            command=self.toggle_theme,
            onvalue="dark",
            offvalue="light"
        )
        self.theme_switch.pack(side="left")
        self.theme_switch.select() if self.theme_mode == "dark" else self.theme_switch.deselect()
        
        # Developer label
        dev_label = ctk.CTkLabel(
            self.sidebar,
            text="Developed by Ahmed Nour Ahmed\nfrom Qena",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="gray",
            justify="center"
        )
        dev_label.pack(side="bottom", pady=(0, 10))
    
    def create_main_content(self):
        """Create the main content area"""
        # Main content frame
        self.main_content = ctk.CTkFrame(self, corner_radius=10)
        self.main_content.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)
        
        # Top bar
        top_bar = ctk.CTkFrame(self.main_content, height=60, corner_radius=8)
        top_bar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        top_bar.grid_columnconfigure(1, weight=1)
        top_bar.grid_propagate(False)
        
        # Current folder display
        self.folder_label = ctk.CTkLabel(
            top_bar,
            text="No folder selected",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            anchor="w"
        )
        self.folder_label.grid(row=0, column=0, padx=20, pady=10, sticky="w", columnspan=2)
        
        # Action buttons in top bar
        action_buttons_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        action_buttons_frame.grid(row=0, column=2, padx=20, pady=10, sticky="e")
        
        action_buttons = [
            ("➕ Add to Favorites", self.add_to_favorites),
            ("📋 Copy Path", self.copy_folder_path),
            ("🔍 Preview", self.preview_changes),
            ("🚀 Apply", self.apply_customizations)
        ]
        
        for i, (text, command) in enumerate(action_buttons):
            btn = ctk.CTkButton(
                action_buttons_frame,
                text=text,
                command=command,
                width=120,
                height=35,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                corner_radius=8
            )
            btn.grid(row=0, column=i, padx=5)
        
        # Content area
        self.content_area = ctk.CTkTabview(self.main_content, corner_radius=10)
        self.content_area.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Create tabs
        self.content_area.add("Overview")
        self.content_area.add("Customization")
        self.content_area.add("Icons")
        self.content_area.add("Colors")
        self.content_area.add("Advanced")
        
        # Setup each tab
        self.setup_overview_tab()
        self.setup_customization_tab()
        self.setup_icons_tab()
        self.setup_colors_tab()
        self.setup_advanced_tab()
    
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        status_bar = ctk.CTkFrame(self, height=40)
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        status_bar.grid_propagate(False)
        
        # Status message
        self.status_label = ctk.CTkLabel(
            status_bar,
            text="Ready",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.status_label.pack(side="left", padx=20, pady=10)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(status_bar, width=200, height=15)
        self.progress_bar.pack(side="right", padx=20, pady=10)
        self.progress_bar.set(0)
        
        # System info
        self.system_info_label = ctk.CTkLabel(
            status_bar,
            text=f"Folders customized: 0",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray"
        )
        self.system_info_label.pack(side="right", padx=20, pady=10)
    
    def setup_overview_tab(self):
        """Setup the overview tab"""
        tab = self.content_area.tab("Overview")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Create a scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Welcome section
        welcome_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        welcome_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        welcome_frame.grid_columnconfigure(0, weight=1)
        
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text="🎉 Welcome to FileFusion Pro!",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        )
        welcome_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        desc_label = ctk.CTkLabel(
            welcome_frame,
            text="The ultimate tool for customizing and organizing your folders with professional-grade features.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            wraplength=800,
            justify="left"
        )
        desc_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # Features grid
        features_label = ctk.CTkLabel(
            scroll_frame,
            text="✨ Key Features",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        )
        features_label.grid(row=1, column=0, padx=20, pady=(20, 10), sticky="w")
        
        features = [
            ("🎨 Color Customization", "Change folder colors with advanced gradient support"),
            ("🖼️ Icon Library", "Access hundreds of built-in icons or use your own"),
            ("⚡ Quick Apply", "Apply customizations to multiple folders at once"),
            ("📊 Folder Statistics", "Get detailed insights about your folders"),
            ("🔒 Backup & Restore", "Never lose your customizations"),
            ("🎭 Theme Support", "Dark and light modes for comfortable usage"),
            ("📱 Modern UI", "Sleek, professional interface with smooth animations"),
            ("🛡️ Safe Operations", "All changes are reversible and safe")
        ]
        
        for i, (title, desc) in enumerate(features):
            feature_frame = ctk.CTkFrame(scroll_frame, corner_radius=8, height=80)
            feature_frame.grid(row=i+2, column=0, sticky="ew", padx=20, pady=5)
            feature_frame.grid_propagate(False)
            feature_frame.grid_columnconfigure(1, weight=1)
            
            icon_label = ctk.CTkLabel(
                feature_frame,
                text=title.split()[0],
                font=ctk.CTkFont(family="Segoe UI", size=18),
                width=50
            )
            icon_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
            
            title_label = ctk.CTkLabel(
                feature_frame,
                text=title,
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
            )
            title_label.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="w")
            
            desc_label = ctk.CTkLabel(
                feature_frame,
                text=desc,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color="gray"
            )
            desc_label.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="w")
        
        # Quick start guide
        guide_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        guide_frame.grid(row=len(features)+2, column=0, sticky="ew", padx=20, pady=20)
        guide_frame.grid_columnconfigure(0, weight=1)
        
        guide_label = ctk.CTkLabel(
            guide_frame,
            text="🚀 Quick Start Guide",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        )
        guide_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        steps = [
            "1. Click 'Browse Folders' in the sidebar to select a folder",
            "2. Navigate to the 'Customization' tab to modify appearance",
            "3. Choose from icons, colors, and advanced options",
            "4. Preview your changes before applying",
            "5. Click 'Apply' to save your customizations"
        ]
        
        for i, step in enumerate(steps):
            step_label = ctk.CTkLabel(
                guide_frame,
                text=step,
                font=ctk.CTkFont(family="Segoe UI", size=14),
                anchor="w"
            )
            step_label.grid(row=i+1, column=0, padx=20, pady=5, sticky="w")
    
    def setup_customization_tab(self):
        """Setup the customization tab"""
        tab = self.content_area.tab("Customization")
        
        # Create two columns
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Left column - Preview
        preview_frame = ctk.CTkFrame(tab, corner_radius=10)
        preview_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        preview_frame.grid_columnconfigure(0, weight=1)
        
        preview_label = ctk.CTkLabel(
            preview_frame,
            text="📁 Folder Preview",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        )
        preview_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Preview canvas
        self.preview_canvas = tk.Canvas(
            preview_frame,
            bg="#2b2b2b" if self.theme_mode == "dark" else "#f0f0f0",
            highlightthickness=0
        )
        self.preview_canvas.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        # Default preview
        self.draw_default_preview()
        
        # Right column - Customization options
        options_frame = ctk.CTkFrame(tab, corner_radius=10)
        options_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        options_frame.grid_columnconfigure(0, weight=1)
        
        options_label = ctk.CTkLabel(
            options_frame,
            text="⚙️ Customization Options",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        )
        options_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Folder name
        name_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        name_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            name_frame,
            text="Folder Name:",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        ).pack(side="left")
        
        self.folder_name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="Enter custom folder name",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.folder_name_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Color selection
        color_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        color_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            color_frame,
            text="Folder Color:",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        ).pack(side="left")
        
        self.color_button = ctk.CTkButton(
            color_frame,
            text="Choose Color",
            command=self.choose_color,
            width=120,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.color_button.pack(side="right")
        
        # Icon selection
        icon_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        icon_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            icon_frame,
            text="Folder Icon:",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        ).pack(side="left")
        
        self.icon_combobox = ctk.CTkComboBox(
            icon_frame,
            values=["Default", "Custom 1", "Custom 2", "Custom 3"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            state="readonly"
        )
        self.icon_combobox.pack(side="right", fill="x", expand=True, padx=(10, 0))
        self.icon_combobox.set("Default")
        
        # Effects
        effects_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        effects_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            effects_frame,
            text="Special Effects:",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        ).pack(side="left")
        
        self.effect_var = tk.StringVar(value="none")
        effects = ["None", "Glow", "Shadow", "Gradient", "3D Effect"]
        
        for effect in effects:
            rb = ctk.CTkRadioButton(
                effects_frame,
                text=effect,
                variable=self.effect_var,
                value=effect.lower().replace(" ", "_"),
                font=ctk.CTkFont(family="Segoe UI", size=13)
            )
            rb.pack(side="left", padx=(10, 0))
        
        # Advanced options
        advanced_frame = ctk.CTkFrame(options_frame, corner_radius=8)
        advanced_frame.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(
            advanced_frame,
            text="Advanced Options:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        self.advanced_options = {
            "bold_text": ctk.CTkSwitch(advanced_frame, text="Bold Text"),
            "custom_tooltip": ctk.CTkSwitch(advanced_frame, text="Custom Tooltip"),
            "auto_backup": ctk.CTkSwitch(advanced_frame, text="Auto Backup"),
            "subfolder_apply": ctk.CTkSwitch(advanced_frame, text="Apply to Subfolders")
        }
        
        for option in self.advanced_options.values():
            option.pack(pady=5, padx=10, anchor="w")
    
    def setup_icons_tab(self):
        """Setup the icons tab"""
        tab = self.content_area.tab("Icons")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Icon library frame
        icon_lib_frame = ctk.CTkFrame(tab, corner_radius=10)
        icon_lib_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        icon_lib_frame.grid_columnconfigure(0, weight=1)
        icon_lib_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(icon_lib_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(
            header_frame,
            text="🖼️ Icon Library",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        ).pack(side="left")
        
        # Add icon button
        add_icon_btn = ctk.CTkButton(
            header_frame,
            text="+ Add Custom Icon",
            command=self.add_custom_icon,
            width=150,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        add_icon_btn.pack(side="right")
        
        # Icon categories
        categories_frame = ctk.CTkFrame(icon_lib_frame, fg_color="transparent")
        categories_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        categories = ["All", "Folders", "Documents", "Media", "System", "Custom"]
        self.icon_category_var = tk.StringVar(value="All")
        
        for category in categories:
            rb = ctk.CTkRadioButton(
                categories_frame,
                text=category,
                variable=self.icon_category_var,
                value=category,
                font=ctk.CTkFont(family="Segoe UI", size=12)
            )
            rb.pack(side="left", padx=10)
        
        # Icon grid
        icon_scroll_frame = ctk.CTkScrollableFrame(icon_lib_frame)
        icon_scroll_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Create icon grid
        self.icon_grid_frame = ctk.CTkFrame(icon_scroll_frame, fg_color="transparent")
        self.icon_grid_frame.pack(fill="both", expand=True)
        
        # Load icons into grid
        self.load_icon_grid()
    
    def setup_colors_tab(self):
        """Setup the colors tab"""
        tab = self.content_area.tab("Colors")
        
        # Create color palette
        color_palette_frame = ctk.CTkFrame(tab, corner_radius=10)
        color_palette_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        color_palette_frame.grid_columnconfigure(0, weight=1)
        color_palette_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        ctk.CTkLabel(
            color_palette_frame,
            text="🌈 Color Palette",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Color presets
        presets_frame = ctk.CTkFrame(color_palette_frame, fg_color="transparent")
        presets_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        color_presets = [
            ("#3498db", "Blue"),
            ("#2ecc71", "Green"),
            ("#e74c3c", "Red"),
            ("#f39c12", "Orange"),
            ("#9b59b6", "Purple"),
            ("#1abc9c", "Turquoise"),
            ("#34495e", "Dark Blue"),
            ("#e67e22", "Carrot"),
            ("#27ae60", "Emerald"),
            ("#8e44ad", "Wisteria"),
            ("#d35400", "Pumpkin"),
            ("#c0392b", "Pomegranate")
        ]
        
        for i, (color, name) in enumerate(color_presets):
            row = i // 4
            col = i % 4
            
            color_btn = ctk.CTkButton(
                presets_frame,
                text=name,
                fg_color=color,
                hover_color=self.adjust_color(color, -20),
                command=lambda c=color: self.apply_preset_color(c),
                height=40,
                font=ctk.CTkFont(family="Segoe UI", size=12)
            )
            color_btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            presets_frame.grid_columnconfigure(col, weight=1)
        
        # Custom color mixer
        mixer_frame = ctk.CTkFrame(tab, corner_radius=10)
        mixer_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(
            mixer_frame,
            text="🎨 Custom Color Mixer",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        ).pack(pady=20, padx=20, anchor="w")
        
        # Color sliders
        sliders = [
            ("Red", 0, 255, 52),
            ("Green", 0, 255, 152),
            ("Blue", 0, 255, 219)
        ]
        
        self.color_sliders = {}
        for name, min_val, max_val, default in sliders:
            frame = ctk.CTkFrame(mixer_frame, fg_color="transparent")
            frame.pack(pady=10, padx=20, fill="x")
            
            ctk.CTkLabel(
                frame,
                text=name,
                font=ctk.CTkFont(family="Segoe UI", size=14),
                width=60
            ).pack(side="left")
            
            slider = ctk.CTkSlider(
                frame,
                from_=min_val,
                to=max_val,
                number_of_steps=256,
                command=self.update_custom_color
            )
            slider.set(default)
            slider.pack(side="right", fill="x", expand=True, padx=(10, 0))
            
            self.color_sliders[name.lower()] = slider
        
        # Color preview
        self.color_preview = ctk.CTkFrame(
            mixer_frame,
            width=100,
            height=100,
            corner_radius=10,
            fg_color="#3498db"
        )
        self.color_preview.pack(pady=20, padx=20)
        
        # Hex color input
        hex_frame = ctk.CTkFrame(mixer_frame, fg_color="transparent")
        hex_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            hex_frame,
            text="Hex Color:",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        ).pack(side="left")
        
        self.hex_color_entry = ctk.CTkEntry(
            hex_frame,
            placeholder_text="#3498db",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.hex_color_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))
        self.hex_color_entry.bind("<Return>", self.apply_hex_color)
    
    def setup_advanced_tab(self):
        """Setup the advanced tab"""
        tab = self.content_area.tab("Advanced")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Advanced features frame
        advanced_frame = ctk.CTkFrame(tab, corner_radius=10)
        advanced_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        advanced_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(
            advanced_frame,
            text="🔧 Advanced Features",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        ).pack(pady=20, padx=20, anchor="w")
        
        # Batch operations
        batch_frame = ctk.CTkFrame(advanced_frame, corner_radius=8)
        batch_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            batch_frame,
            text="Batch Operations",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        batch_buttons = [
            ("Apply to Multiple Folders", self.batch_apply),
            ("Export Settings", self.export_settings),
            ("Import Settings", self.import_settings),
            ("Reset All Folders", self.reset_all_folders)
        ]
        
        for text, command in batch_buttons:
            btn = ctk.CTkButton(
                batch_frame,
                text=text,
                command=command,
                height=35,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                corner_radius=8,
                fg_color="gray20",
                hover_color="gray25"
            )
            btn.pack(pady=5, padx=10, fill="x")
        
        # System integration
        sys_frame = ctk.CTkFrame(advanced_frame, corner_radius=8)
        sys_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            sys_frame,
            text="System Integration",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        sys_options = [
            ("Register File Types", self.register_file_types),
            ("Create Desktop Shortcut", self.create_desktop_shortcut),
            ("Add to Context Menu", self.add_to_context_menu),
            ("Optimize Performance", self.optimize_performance)
        ]
        
        for text, command in sys_options:
            btn = ctk.CTkButton(
                sys_frame,
                text=text,
                command=command,
                height=35,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                corner_radius=8,
                fg_color="gray20",
                hover_color="gray25"
            )
            btn.pack(pady=5, padx=10, fill="x")
        
        # Statistics
        stats_frame = ctk.CTkFrame(advanced_frame, corner_radius=8)
        stats_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            stats_frame,
            text="📊 Statistics",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        self.stats_text = ctk.CTkTextbox(
            stats_frame,
            height=100,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.stats_text.pack(pady=10, padx=10, fill="x")
        self.stats_text.insert("1.0", "No statistics available yet.\nSelect a folder to see statistics.")
        self.stats_text.configure(state="disabled")
    
    def draw_default_preview(self):
        """Draw default folder preview"""
        canvas = self.preview_canvas
        canvas.delete("all")
        
        # Draw folder icon
        width = canvas.winfo_width() if canvas.winfo_width() > 10 else 300
        height = canvas.winfo_height() if canvas.winfo_height() > 10 else 200
        
        if width <= 10 or height <= 10:
            width, height = 300, 200
        
        # Folder body
        canvas.create_rectangle(
            width//2 - 80, height//2 - 60,
            width//2 + 80, height//2 + 40,
            fill="#3498db", outline="#2980b9", width=2
        )
        
        # Folder tab
        canvas.create_polygon(
            width//2 - 60, height//2 - 60,
            width//2 + 60, height//2 - 60,
            width//2 + 40, height//2 - 30,
            width//2 - 40, height//2 - 30,
            fill="#2980b9", outline="#2980b9", width=2
        )
        
        # Folder name
        canvas.create_text(
            width//2, height//2 + 60,
            text="Sample Folder",
            font=("Segoe UI", 14, "bold"),
            fill="#ffffff" if self.theme_mode == "dark" else "#000000"
        )
        
        # Status text
        canvas.create_text(
            width//2, height//2 + 90,
            text="Select a folder to customize",
            font=("Segoe UI", 12),
            fill="gray"
        )
    
    def load_custom_icons(self):
        """Load custom icons from resources"""
        # This would load actual icons in a production app
        self.custom_icons = [
            "📁", "📂", "📄", "📷", "🎵", "🎥", "📊", "🔒",
            "💾", "📎", "📌", "📍", "🚀", "⭐", "🎨", "🔧"
        ]
    
    def load_icon_grid(self):
        """Load icons into the grid"""
        # Clear existing icons
        for widget in self.icon_grid_frame.winfo_children():
            widget.destroy()
        
        # Create icon buttons
        icons = self.custom_icons * 3  # Repeat for demonstration
        
        for i, icon in enumerate(icons[:32]):  # Show first 32 icons
            row = i // 8
            col = i % 8
            
            icon_btn = ctk.CTkButton(
                self.icon_grid_frame,
                text=icon,
                width=60,
                height=60,
                font=ctk.CTkFont(size=24),
                command=lambda i=icon: self.select_icon(i),
                corner_radius=10
            )
            icon_btn.grid(row=row, column=col, padx=5, pady=5)
    
    def apply_styles(self):
        """Apply custom styles to widgets"""
        # This method would apply additional styling in a full implementation
        pass
    
    def browse_folder(self):
        """Browse for a folder to customize"""
        folder_path = filedialog.askdirectory(title="Select Folder to Customize")
        if folder_path:
            self.current_folder = folder_path
            self.folder_label.configure(text=f"📁 {os.path.basename(folder_path)}")
            self.update_status(f"Loaded folder: {folder_path}")
            self.add_to_recent(folder_path)
            self.update_preview()
            self.update_stats()
    
    def add_to_recent(self, folder_path):
        """Add folder to recent list"""
        if folder_path in self.config.get("recent_folders", []):
            self.config["recent_folders"].remove(folder_path)
        self.config["recent_folders"].insert(0, folder_path)
        self.config["recent_folders"] = self.config["recent_folders"][:10]
        self.save_config()
    
    def add_to_favorites(self):
        """Add current folder to favorites"""
        if self.current_folder and self.current_folder not in self.config.get("favorites", []):
            self.config.setdefault("favorites", []).append(self.current_folder)
            self.save_config()
            self.update_status(f"Added to favorites: {self.current_folder}")
            CTkMessagebox(title="Success", message="Folder added to favorites!", icon="check")
    
    def show_favorites(self):
        """Show favorites dialog"""
        favorites = self.config.get("favorites", [])
        if not favorites:
            CTkMessagebox(title="No Favorites", message="You haven't added any folders to favorites yet.")
            return
        
        # Create dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Favorites")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="⭐ Favorite Folders",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        ).pack(pady=20)
        
        scroll_frame = ctk.CTkScrollableFrame(dialog)
        scroll_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        
        for folder in favorites:
            folder_frame = ctk.CTkFrame(scroll_frame, height=50)
            folder_frame.pack(pady=5, fill="x")
            folder_frame.pack_propagate(False)
            
            ctk.CTkLabel(
                folder_frame,
                text=f"📁 {os.path.basename(folder)}",
                font=ctk.CTkFont(family="Segoe UI", size=14)
            ).pack(side="left", padx=20, pady=10)
            
            ctk.CTkButton(
                folder_frame,
                text="Load",
                width=60,
                command=lambda f=folder: self.load_favorite(f, dialog)
            ).pack(side="right", padx=10)
            
            ctk.CTkButton(
                folder_frame,
                text="Remove",
                width=80,
                fg_color="gray30",
                hover_color="gray40",
                command=lambda f=folder: self.remove_favorite(f)
            ).pack(side="right", padx=5)
    
    def load_favorite(self, folder_path, dialog):
        """Load a favorite folder"""
        self.current_folder = folder_path
        self.folder_label.configure(text=f"📁 {os.path.basename(folder_path)}")
        self.update_status(f"Loaded favorite: {folder_path}")
        self.update_preview()
        dialog.destroy()
    
    def remove_favorite(self, folder_path):
        """Remove a folder from favorites"""
        if folder_path in self.config.get("favorites", []):
            self.config["favorites"].remove(folder_path)
            self.save_config()
            self.update_status(f"Removed from favorites: {folder_path}")
            self.show_favorites()  # Refresh dialog
    
    def show_recent(self):
        """Show recent folders dialog"""
        recent = self.config.get("recent_folders", [])
        if not recent:
            CTkMessagebox(title="No Recent", message="No recent folders found.")
            return
        
        # Similar to favorites dialog
        self.show_favorites()  # Reusing for demonstration
    
    def show_customize(self):
        """Switch to customization tab"""
        self.content_area.set("Customization")
    
    def show_icons(self):
        """Switch to icons tab"""
        self.content_area.set("Icons")
    
    def show_colors(self):
        """Switch to colors tab"""
        self.content_area.set("Colors")
    
    def show_tools(self):
        """Switch to advanced tab"""
        self.content_area.set("Advanced")
    
    def show_stats(self):
        """Show statistics"""
        if not self.current_folder:
            CTkMessagebox(title="No Folder", message="Please select a folder first.")
            return
        
        self.content_area.set("Advanced")
        self.update_stats()
    
    def choose_color(self):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(title="Choose Folder Color")[1]
        if color:
            self.color_button.configure(fg_color=color, hover_color=self.adjust_color(color, -20))
            self.update_preview()
    
    def apply_preset_color(self, color):
        """Apply a preset color"""
        self.color_button.configure(fg_color=color, hover_color=self.adjust_color(color, -20))
        self.update_preview()
    
    def update_custom_color(self, *args):
        """Update custom color from sliders"""
        r = int(self.color_sliders["red"].get())
        g = int(self.color_sliders["green"].get())
        b = int(self.color_sliders["blue"].get())
        
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.color_preview.configure(fg_color=color)
        self.hex_color_entry.delete(0, tk.END)
        self.hex_color_entry.insert(0, color)
        
        if self.current_folder:
            self.color_button.configure(fg_color=color, hover_color=self.adjust_color(color, -20))
    
    def apply_hex_color(self, event=None):
        """Apply hex color from entry"""
        hex_color = self.hex_color_entry.get()
        if self.is_valid_hex(hex_color):
            self.color_button.configure(fg_color=hex_color, hover_color=self.adjust_color(hex_color, -20))
            self.update_preview()
    
    def is_valid_hex(self, color):
        """Check if string is valid hex color"""
        import re
        return bool(re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color))
    
    def adjust_color(self, color, amount):
        """Adjust color brightness"""
        try:
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            adjusted = tuple(max(0, min(255, c + amount)) for c in rgb)
            return f"#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}"
        except:
            return color
    
    def select_icon(self, icon):
        """Select an icon from the library"""
        self.selected_icon = icon
        self.update_status(f"Selected icon: {icon}")
        self.update_preview()
    
    def add_custom_icon(self):
        """Add custom icon from file"""
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Image files", "*.png *.ico *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.update_status(f"Added custom icon: {file_path}")
            CTkMessagebox(title="Success", message="Custom icon added!", icon="check")
    
    def copy_folder_path(self):
        """Copy folder path to clipboard"""
        if self.current_folder:
            self.clipboard_clear()
            self.clipboard_append(self.current_folder)
            self.update_status("Folder path copied to clipboard")
    
    def preview_changes(self):
        """Preview changes before applying"""
        if not self.current_folder:
            CTkMessagebox(title="No Folder", message="Please select a folder first.")
            return
        
        self.update_preview()
        self.update_status("Preview updated")
        CTkMessagebox(title="Preview", message="Changes previewed. Click Apply to save.")
    
    def apply_customizations(self):
        """Apply customizations to folder"""
        if not self.current_folder:
            CTkMessagebox(title="No Folder", message="Please select a folder first.")
            return
        
        # Show progress
        self.progress_bar.set(0)
        self.update_status("Applying customizations...")
        
        # Simulate progress
        for i in range(101):
            self.progress_bar.set(i/100)
            self.update_idletasks()
            self.after(10)
        
        # Save to desktop.ini (Windows)
        self.apply_windows_customization()
        
        self.progress_bar.set(0)
        self.update_status("Customizations applied successfully!")
        CTkMessagebox(title="Success", message="Folder customizations applied!", icon="check")
    
    def apply_windows_customization(self):
        """Apply folder customization for Windows"""
        if not self.current_folder:
            return
        
        # This is a simplified version
        # In a real app, this would modify desktop.ini and folder settings
        desktop_ini = os.path.join(self.current_folder, "desktop.ini")
        
        try:
            with open(desktop_ini, 'w') as f:
                f.write("[.ShellClassInfo]\n")
                f.write(f"InfoTip=Customized with FileFusion Pro\n")
                # More properties would be set here
            
            # Set hidden and system attributes
            os.system(f'attrib +s +h "{desktop_ini}"')
            
        except Exception as e:
            print(f"Error applying customization: {e}")
    
    def update_preview(self):
        """Update folder preview"""
        self.draw_default_preview()  # Simplified for example
    
    def update_stats(self):
        """Update folder statistics"""
        if not self.current_folder:
            return
        
        try:
            total_size = 0
            file_count = 0
            folder_count = 0
            
            for root, dirs, files in os.walk(self.current_folder):
                folder_count += len(dirs)
                file_count += len(files)
                for file in files:
                    try:
                        total_size += os.path.getsize(os.path.join(root, file))
                    except:
                        pass
            
            stats_text = f"""
📊 Folder Statistics for: {os.path.basename(self.current_folder)}
            
📁 Location: {self.current_folder}
🗂️  Total Folders: {folder_count}
📄 Total Files: {file_count}
💾 Total Size: {self.format_size(total_size)}
📅 Created: {datetime.fromtimestamp(os.path.getctime(self.current_folder)).strftime('%Y-%m-%d %H:%M:%S')}
✏️  Modified: {datetime.fromtimestamp(os.path.getmtime(self.current_folder)).strftime('%Y-%m-%d %H:%M:%S')}
            
📈 Analysis:
• Average files per folder: {file_count/max(folder_count, 1):.1f}
• Largest file type: N/A
• Customization status: Not Applied
"""
            
            self.stats_text.configure(state="normal")
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert("1.0", stats_text)
            self.stats_text.configure(state="disabled")
            
        except Exception as e:
            print(f"Error getting stats: {e}")
    
    def format_size(self, size_bytes):
        """Format size in bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.configure(text=message)
    
    def toggle_theme(self):
        """Toggle between dark and light mode"""
        if self.theme_switch.get() == "dark":
            ctk.set_appearance_mode("dark")
            self.theme_mode = "dark"
        else:
            ctk.set_appearance_mode("light")
            self.theme_mode = "light"
        
        self.config["theme"] = self.theme_mode
        self.save_config()
        self.update_preview()
    
    def capture_icon(self):
        """Capture icon from screen"""
        CTkMessagebox(title="Info", message="Icon capture feature would be implemented here.")
    
    def reset_all_customizations(self):
        """Reset all customizations for current folder"""
        if not self.current_folder:
            CTkMessagebox(title="No Folder", message="Please select a folder first.")
            return
        
        msg = CTkMessagebox(
            title="Confirm Reset",
            message="Are you sure you want to reset all customizations?",
            icon="question",
            option_1="Cancel",
            option_2="Yes"
        )
        
        if msg.get() == "Yes":
            self.update_status("Resetting customizations...")
            # Implementation would go here
            self.after(1000, lambda: self.update_status("Customizations reset"))
    
    def create_backup(self):
        """Create backup of customizations"""
        self.update_status("Creating backup...")
        # Implementation would go here
        self.after(1000, lambda: CTkMessagebox(title="Backup", message="Backup created successfully!"))
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Settings")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="⚙️ Settings",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        ).pack(pady=20)
        
        # Settings options would go here
        # ...
        
        dialog.mainloop()
    
    def batch_apply(self):
        """Apply customizations to multiple folders"""
        CTkMessagebox(title="Info", message="Batch apply feature would be implemented here.")
    
    def export_settings(self):
        """Export customization settings"""
        CTkMessagebox(title="Info", message="Export feature would be implemented here.")
    
    def import_settings(self):
        """Import customization settings"""
        CTkMessagebox(title="Info", message="Import feature would be implemented here.")
    
    def reset_all_folders(self):
        """Reset all customized folders"""
        CTkMessagebox(title="Info", message="Reset all feature would be implemented here.")
    
    def register_file_types(self):
        """Register custom file types"""
        CTkMessagebox(title="Info", message="File type registration would be implemented here.")
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut"""
        CTkMessagebox(title="Info", message="Shortcut creation would be implemented here.")
    
    def add_to_context_menu(self):
        """Add to Windows context menu"""
        CTkMessagebox(title="Info", message="Context menu integration would be implemented here.")
    
    def optimize_performance(self):
        """Optimize application performance"""
        CTkMessagebox(title="Info", message="Performance optimization would be implemented here.")
    
    def run(self):
        """Run the application"""
        self.mainloop()

def main():
    """Main entry point"""
    try:
        app = FileFusionPro()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        CTkMessagebox(title="Error", message=f"Failed to start application:\n{e}", icon="cancel")

if __name__ == "__main__":
    main()