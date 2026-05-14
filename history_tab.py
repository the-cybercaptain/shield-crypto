""" 
History Tab for SHIELD CRYPTO 
Displays encryption/decryption history 
""" 
 
import tkinter as tk 
from tkinter import messagebox, scrolledtext 
from ui_components import THEME, FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_MONO, ModernButton 
 
# Import core logic 
try: 
    from core_code import load_history, clear_history 
except ImportError: 
    messagebox.showerror("Import Error", "core_code.py not found!\nPlace core_code.py in the same folder.") 
    import sys 
    sys.exit(1) 
 
class HistoryTab(tk.Frame): 
    def __init__(self, parent): 
        super().__init__(parent, bg=THEME['bg']) 
        self._build() 
 
    def _build(self): 
        top = tk.Frame(self, bg=THEME['panel']) 
        top.pack(fill='x') 
        tk.Label(top, text='ENCRYPTION HISTORY', font=FONT_HEADING, 
                 fg=THEME['warning'], bg=THEME['panel']).pack(side='left', padx=12, pady=5) 
        ModernButton(top, 'Refresh', command=self._load, color=THEME['secondary']).pack(side='right', padx=5, pady=3) 
        ModernButton(top, 'Clear', command=self._clear, color=THEME['danger']).pack(side='right', padx=5, pady=3) 
 
        self.text = scrolledtext.ScrolledText(self, font=FONT_MONO, bg=THEME['input_bg'], 
                                               fg=THEME['success'], wrap='word', bd=1, relief='solid', height=20) 
        self.text.pack(fill='both', expand=True, padx=8, pady=8) 
        self._load() 
 
    def _load(self): 
        content = load_history() 
        self.text.config(state='normal') 
        self.text.delete('1.0', 'end') 
        self.text.insert('1.0', content if content.strip() else '\n   No history yet.\n') 
        self.text.config(state='disabled') 
 
    def _clear(self): 
        if messagebox.askyesno('Clear', 'Clear all history?'): 
            clear_history() 
            self._load()
