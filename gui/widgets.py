import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Callable, Optional
from core.file_operations import FileOperations

class PathSelector(tk.Frame):
    def __init__(self, master, label_text: str, initial_path: str = "", 
                 is_dir: bool = True, button_text: str = "Browse...", 
                 on_change: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.is_dir = is_dir
        self.on_change = on_change
        
        # Label
        self.label = ttk.Label(self, text=label_text)
        self.label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        
        # Entry
        self.path_var = tk.StringVar(value=initial_path)
        self.entry = ttk.Entry(self, textvariable=self.path_var, width=40)
        self.entry.grid(row=0, column=1, sticky="ew")
        
        # Browse button
        self.browse_btn = ttk.Button(self, text=button_text, command=self._browse)
        self.browse_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Bind changes if callback provided
        if on_change:
            self.path_var.trace_add("write", lambda *_: on_change(self.path_var.get()))
        
        self.columnconfigure(1, weight=1)
    
    def _browse(self):
        if self.is_dir:
            path = filedialog.askdirectory(initialdir=self.path_var.get())
        else:
            path = filedialog.askopenfilename(initialdir=self.path_var.get())
        
        if path:
            self.path_var.set(path)
    
    def get_path(self) -> str:
        return self.path_var.get()
    
    def set_path(self, path: str):
        self.path_var.set(path)

class ToggleSwitch(ttk.Checkbutton):
    def __init__(self, master, text: str, variable: tk.BooleanVar, command: Optional[Callable] = None, **kwargs):
        super().__init__(master, text=text, variable=variable, command=command, **kwargs)
        self.style = ttk.Style()
        self.style.configure("Toggle.TCheckbutton", padding=5)

class ProgressDialog(tk.Toplevel):
    def __init__(self, master, title: str = "Processing", width: int = 300, height: int = 100):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Center the dialog
        self._center_on_parent(master, width, height)
        
        # Progress bar
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.progress.pack(pady=20, padx=20, fill='x')
        
        # Label
        self.label = ttk.Label(self, text="Please wait...")
        self.label.pack(pady=(0, 20))
        
        self.progress.start()
    
    def _center_on_parent(self, parent, width, height):
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def update_message(self, message: str):
        self.label.config(text=message)
        self.update()

class CollapsiblePane(ttk.Frame):
    def __init__(self, master, title: str, **kwargs):
        super().__init__(master, **kwargs)
        self.expanded = False
        self.title = title
        
        # Toggle button
        self.toggle_btn = ttk.Button(self, text=f"▼ {title}", command=self.toggle, style='Toggle.TButton')
        self.toggle_btn.pack(fill='x', pady=(0, 5))
        
        # Content frame
        self.content = ttk.Frame(self)
        
    def toggle(self):
        if self.expanded:
            self.content.pack_forget()
            self.toggle_btn.config(text=f"▼ {self.title}")
        else:
            self.content.pack(fill='x', expand=True)
            self.toggle_btn.config(text=f"▲ {self.title}")
        self.expanded = not self.expanded