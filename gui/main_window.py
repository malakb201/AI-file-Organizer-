import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict
from core.organizer import FileOrganizer
from gui.widgets import PathSelector, ToggleSwitch, ProgressDialog, CollapsiblePane
from utils.config import save_config, load_config
import threading
import platform
import logging
from tkinter import font as tkfont

class MainWindow:
    def __init__(self, root, config, logger):
        self.root = root
        self.config = config
        self.logger = logger
        self.organizer = FileOrganizer(config, logger)
        
        # Window setup
        self._setup_window()
        self._setup_styles()
        self._setup_ui()
        self._load_config_values()
        
        # Bind events
        self._bind_events()
        
    def _setup_window(self):
        """Configure main window properties"""
        self.root.title(f"{self.config['app']['name']} v{self.config['app']['version']}")
        
        # Set window icon if available
        try:
            self.root.iconbitmap('assets/icon.ico')  # Provide your icon file
        except:
            pass
        
        # Set initial size based on screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Use 70% of screen width and 75% of height
        window_width = min(1200, int(screen_width * 0.7))
        window_height = min(800, int(screen_height * 0.75))
        
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 650)  # Minimum size
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def _setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        
        # Use clam theme as base
        style.theme_use('clam')
        
        # Custom colors
        bg_color = '#f5f5f5'
        accent_color = '#4a6da7'
        light_accent = '#e1e8f0'
        text_color = '#333333'
        
        # Configure colors
        style.configure('.', 
                      background=bg_color,
                      foreground=text_color,
                      font=('Segoe UI', 10))
        
        # Frame styling
        style.configure('TFrame', background=bg_color)
        style.configure('Header.TFrame', background=accent_color)
        
        # Label styling
        style.configure('Header.TLabel', 
                      background=accent_color,
                      foreground='white',
                      font=('Segoe UI', 11, 'bold'),
                      padding=5)
        
        # Button styling
        style.configure('TButton', 
                       padding=6,
                       relief='flat')
        style.map('TButton',
                background=[('active', light_accent)],
                relief=[('pressed', 'sunken')])
        
        style.configure('Accent.TButton', 
                       background=accent_color,
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       padding=8)
        style.map('Accent.TButton',
                background=[('active', '#3a5a8f')])
        
        # Entry styling
        style.configure('TEntry',
                       fieldbackground='white',
                       bordercolor='#cccccc',
                       lightcolor='#cccccc',
                       darkcolor='#cccccc',
                       padding=5)
        
        # Treeview styling
        style.configure('Treeview',
                      background='white',
                      fieldbackground='white',
                      foreground=text_color,
                      rowheight=28,
                      bordercolor='#dddddd',
                      lightcolor='#eeeeee',
                      darkcolor='#eeeeee')
        style.configure('Treeview.Heading',
                      background='#e0e0e0',
                      foreground=text_color,
                      font=('Segoe UI', 9, 'bold'),
                      padding=5)
        style.map('Treeview',
                 background=[('selected', accent_color)],
                 foreground=[('selected', 'white')])
        
        # Scrollbar styling
        style.configure('Vertical.TScrollbar',
                       background='#e0e0e0',
                       troughcolor=bg_color,
                       arrowcolor=text_color,
                       bordercolor=bg_color)
        
        # Configure fonts
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family='Segoe UI', size=10)
        
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family='Segoe UI', size=10)
        
        # Set background color
        self.root.configure(bg=bg_color)
    
    def _setup_ui(self):
        """Create and arrange all UI components"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="15 15 15 10")
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configure grid weights for main frame
        self.main_frame.columnconfigure(0, weight=1)
        for i in range(6):  # 6 rows
            self.main_frame.rowconfigure(i, weight=0 if i < 5 else 1)
        
        # Header
        self._create_header()
        
        # Create UI sections
        self._create_path_selectors(1)
        self._create_behavior_options(2)
        self._create_ai_options(3)
        self._create_file_type_settings(4)
        self._create_organize_button(5)
        self._create_results_area(6)
        self._create_status_bar(7)
        self._create_menu()
    
    def _create_header(self):
        """Create application header"""
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        
        # App title
        title_label = ttk.Label(
            header_frame,
            text=self.config['app']['name'],
            style='Header.TLabel'
        )
        title_label.pack(side='left', padx=10)
        
        # Version label
        version_label = ttk.Label(
            header_frame,
            text=f"v{self.config['app']['version']}",
            style='Header.TLabel'
        )
        version_label.pack(side='right', padx=10)
    
    def _bind_events(self):
        """Bind window events"""
        self.root.bind('<Configure>', self._on_window_resize)
        
    def _on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            # Adjust treeview columns
            if hasattr(self, 'results_tree'):
                new_width = self.root.winfo_width() - 200
                self.results_tree.column('message', width=max(400, new_width))
    
    def _create_path_selectors(self, row):
        """Create source/destination path selectors"""
        container = ttk.LabelFrame(
            self.main_frame,
            text=" Folder Selection ",
            padding=(15, 10, 15, 10)
        )
        container.grid(row=row, column=0, sticky='ew', pady=(0, 10))
        container.columnconfigure(0, weight=1)
        
        # Source selector
        self.source_selector = PathSelector(
            container,
            "Source Directory:",
            self.config['paths']['default_source'],
            is_dir=True,
            on_change=lambda p: self._update_config('paths', 'default_source', p)
        )
        self.source_selector.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        
        # Destination selector
        self.dest_selector = PathSelector(
            container,
            "Destination Directory:",
            self.config['paths']['default_dest'],
            is_dir=True,
            on_change=lambda p: self._update_config('paths', 'default_dest', p)
        )
        self.dest_selector.grid(row=1, column=0, sticky='ew')
    
    def _create_behavior_options(self, row):
        """Create behavior options section"""
        self.behavior_frame = CollapsiblePane(
            self.main_frame, 
            "Behavior Options",
            padding=(0, 5, 0, 5)
        )
        self.behavior_frame.grid(row=row, column=0, sticky='ew', pady=(0, 10))
        
        # Keep originals toggle
        self.keep_originals_var = tk.BooleanVar(value=self.config['behavior'].get('keep_originals', False))
        keep_orig_toggle = ToggleSwitch(
            self.behavior_frame.content,
            "Keep original files (Copy instead of Move)",
            self.keep_originals_var,
            command=lambda: self._update_config('behavior', 'keep_originals', self.keep_originals_var.get())
        )
        keep_orig_toggle.pack(anchor='w', fill='x', pady=2)
        
        # Expand by default
        self.behavior_frame.toggle()
    
    def _create_ai_options(self, row):
        """Create AI options section"""
        self.ai_frame = CollapsiblePane(
            self.main_frame, 
            "AI Options",
            padding=(0, 5, 0, 5)
        )
        self.ai_frame.grid(row=row, column=0, sticky='ew', pady=(0, 10))
        
        # Enable AI toggle
        self.ai_enabled_var = tk.BooleanVar(value=self.config['ai']['enable_suggestions'])
        ai_toggle = ToggleSwitch(
            self.ai_frame.content,
            "Enable AI Suggestions",
            self.ai_enabled_var,
            command=lambda: self._update_config('ai', 'enable_suggestions', self.ai_enabled_var.get())
        )
        ai_toggle.pack(anchor='w', fill='x', pady=2)
        
        # API Key entry
        api_frame = ttk.Frame(self.ai_frame.content)
        api_frame.pack(fill='x', pady=(8, 0))
        
        ttk.Label(api_frame, text="API Key:").pack(side='left', padx=(0, 5))
        
        self.api_key_var = tk.StringVar(value=self.config['ai']['api_key'])
        api_key_entry = ttk.Entry(
            api_frame,
            textvariable=self.api_key_var,
            show="•",
            width=40
        )
        api_key_entry.pack(side='left', expand=True, fill='x')
        api_key_entry.bind(
            "<FocusOut>", 
            lambda e: self._update_config('ai', 'api_key', self.api_key_var.get())
        )
        
        # Expand by default
        self.ai_frame.toggle()
    
    def _create_file_type_settings(self, row):
        """Create file type categories section"""
        self.types_frame = CollapsiblePane(
            self.main_frame, 
            "File Type Categories",
            padding=(0, 5, 0, 5)
        )
        self.types_frame.grid(row=row, column=0, sticky='ew', pady=(0, 15))
        
        container = ttk.Frame(self.types_frame.content)
        container.pack(fill='x')
        
        # Create a grid of file type entries
        for i, (category, extensions) in enumerate(self.config['file_types'].items()):
            frame = ttk.Frame(container)
            frame.grid(row=i, column=0, sticky='ew', pady=3)
            frame.columnconfigure(1, weight=1)
            
            ttk.Label(frame, text=f"{category.capitalize()}:").grid(row=0, column=0, sticky='w', padx=(0, 5))
            
            ext_var = tk.StringVar(value=", ".join(extensions))
            entry = ttk.Entry(
                frame,
                textvariable=ext_var,
                width=40
            )
            entry.grid(row=0, column=1, sticky='ew')
            entry.bind(
                "<FocusOut>", 
                lambda e, c=category, v=ext_var: self._update_file_types(c, v.get())
            )
        
        # Expand by default
        self.types_frame.toggle()
    
    def _create_organize_button(self, row):
        """Create organize button"""
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=row, column=0, sticky='ew', pady=(5, 15))
        btn_frame.columnconfigure(0, weight=1)
        
        self.organize_btn = ttk.Button(
            btn_frame,
            text="ORGANIZE FILES", 
            command=self._organize_files_threaded,
            style='Accent.TButton'
        )
        self.organize_btn.grid(row=0, column=0, sticky='ew')
    
    def _create_results_area(self, row):
        """Create results display area"""
        self.results_frame = ttk.LabelFrame(
            self.main_frame, 
            text=" Results ",
            padding=(10, 10, 10, 10)
        )
        self.results_frame.grid(row=row, column=0, sticky='nsew')
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)
        
        # Treeview with scrollbar
        self.results_tree = ttk.Treeview(
            self.results_frame,
            columns=('status', 'message'),
            show='headings',
            selectmode='browse',
            height=10,
            style='Treeview'
        )
        
        # Configure headings
        self.results_tree.heading('status', text='STATUS', anchor='w')
        self.results_tree.heading('message', text='MESSAGE', anchor='w')
        self.results_tree.column('status', width=120, stretch=False, anchor='w')
        self.results_tree.column('message', width=500, stretch=True, anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.results_frame,
            orient='vertical',
            command=self.results_tree.yview,
            style='Vertical.TScrollbar'
        )
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
    
    def _create_status_bar(self, row):
        """Create status bar"""
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Frame(self.main_frame, relief='sunken')
        self.status_bar.grid(row=row, column=0, sticky='ew', pady=(5, 0))
        
        status_label = ttk.Label(
            self.status_bar,
            textvariable=self.status_var,
            anchor='w',
            padding=(8, 4, 8, 4)
        )
        status_label.pack(fill='x')
    
    def _create_menu(self):
        """Create modern menu bar"""
        menubar = tk.Menu(self.root, tearoff=0, bd=0)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Reset Defaults", command=self._reset_defaults)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _load_config_values(self):
        """Load configuration values into UI elements"""
        self.source_selector.set_path(self.config['paths']['default_source'])
        self.dest_selector.set_path(self.config['paths']['default_dest'])
        self.ai_enabled_var.set(self.config['ai']['enable_suggestions'])
        self.api_key_var.set(self.config['ai']['api_key'])
        self.keep_originals_var.set(self.config['behavior'].get('keep_originals', False))
    
    def _update_config(self, section, key, value):
        """Update configuration value"""
        self.config[section][key] = value
        save_config(self.config)
    
    def _update_file_types(self, category, extensions_str):
        """Update file type extensions in config"""
        extensions = [ext.strip().lower() for ext in extensions_str.split(',') if ext.strip()]
        self.config['file_types'][category] = extensions
        save_config(self.config)
    
    def _organize_files_threaded(self):
        """Run file organization in a separate thread"""
        # Disable button during operation
        self.organize_btn.config(state='disabled')
        self.status_var.set("Organizing files...")
        self.results_tree.delete(*self.results_tree.get_children())
        self.progress_dialog = ProgressDialog(self.root, "Organizing Files")
        
        thread = threading.Thread(target=self._organize_files, daemon=True)
        thread.start()
        
        self.root.after(100, self._check_thread, thread)
    
    def _organize_files(self):
        """Perform the file organization"""
        source = self.source_selector.get_path()
        dest = self.dest_selector.get_path()
        use_ai = self.ai_enabled_var.get()
        keep_originals = self.keep_originals_var.get()
        
        if not source or not dest:
            messagebox.showerror("Error", "Please select both source and destination directories")
            return
        
        try:
            # Validate paths
            is_valid, msg = self.organizer.validate_paths(source, dest)
            if not is_valid:
                messagebox.showerror("Error", msg)
                return
            
            # Perform organization
            results = self.organizer.organize(source, dest, use_ai, keep_originals)
            self._show_results(results)
            
        except Exception as e:
            self.logger.error(f"Organization error: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            if hasattr(self, 'progress_dialog'):
                self.progress_dialog.destroy()
    
    def _check_thread(self, thread):
        """Check if the organization thread is done"""
        if thread.is_alive():
            self.root.after(100, self._check_thread, thread)
        else:
            if hasattr(self, 'progress_dialog'):
                self.progress_dialog.destroy()
            self.organize_btn.config(state='normal')
    
    def _show_results(self, results: Dict):
        """Display organization results"""
        self.results_tree.delete(*self.results_tree.get_children())
        
        # Add summary
        self.results_tree.insert('', 'end', values=("COMPLETED", f"Processed {results['total_files']} files"))
        self.results_tree.insert('', 'end', values=("SUCCESS", f"{results['organized']} files organized"))
        
        if results['failures'] > 0:
            self.results_tree.insert('', 'end', values=("FAILED", f"{results['failures']} files could not be processed"))
        
        # Add mode info
        mode = "COPIED" if results['operation_mode'] == 'copy' else "MOVED"
        self.results_tree.insert('', 'end', values=("MODE", f"Files were {mode.lower()} to destination"))
        
        # Add AI suggestions if available
        if results.get('suggestions'):
            self.results_tree.insert('', 'end', values=("SUGGESTIONS", ""))
            for suggestion in results['suggestions']:
                self.results_tree.insert('', 'end', values=("", suggestion))
        
        # Update status
        self.status_var.set(f"Done. {results['organized']}/{results['total_files']} files processed in {results['execution_time']}s")
    
    def _reset_defaults(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to defaults?"):
            self.config = load_config()
            save_config(self.config)
            self._load_config_values()
            messagebox.showinfo("Success", "Settings have been reset to defaults")
    
    def _show_about(self):
        """Show modern about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.resizable(False, False)
        
        # Center about window
        window_width = 400
        window_height = 300
        screen_width = about_window.winfo_screenwidth()
        screen_height = about_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        about_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Header
        header_frame = ttk.Frame(about_window, style='Header.TFrame')
        header_frame.pack(fill='x')
        
        ttk.Label(
            header_frame,
            text=self.config['app']['name'],
            style='Header.TLabel',
            font=('Segoe UI', 12, 'bold')
        ).pack(pady=5)
        
        # Content
        content_frame = ttk.Frame(about_window, padding=20)
        content_frame.pack(fill='both', expand=True)
        
        # App icon/logo would go here
        # logo_label = ttk.Label(content_frame, image=app_logo)
        # logo_label.pack(pady=10)
        
        ttk.Label(
            content_frame,
            text=f"Version {self.config['app']['version']}",
            font=('Segoe UI', 9)
        ).pack(pady=5)
        
        ttk.Label(
            content_frame,
            text="AI-Powered File Organization OPEN SOURCE Tool",
            font=('Segoe UI', 10)
        ).pack(pady=10)
        
        ttk.Label(
            content_frame,
            text="© 2025 ZEESHAN PUBLIC",
            font=('Segoe UI', 8)
        ).pack(side='bottom', pady=10)
        
        # Close button
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(side='bottom', pady=10)
        
        ttk.Button(
            btn_frame,
            text="Close",
            command=about_window.destroy,
            width=10
        ).pack()