""" 
UI Components for SHIELD CRYPTO 
Contains themes, buttons, step boxes, password entries, and alert dialogs 
""" 
 
import tkinter as tk 
from tkinter import messagebox 
 
# Professional Dark Theme 
THEME = { 
    'bg':           '#0a0e1a', 
    'panel':        '#0f1420', 
    'card':         '#141925', 
    'card_hover':   '#1a2030', 
    'border':       '#1e2a3a', 
    'border_active': '#2d3a4a', 
    'primary':      '#4f46e5', 
    'primary_dark': '#4338ca', 
    'secondary':    '#0ea5e9', 
    'success':      '#10b981', 
    'warning':      '#f59e0b', 
    'danger':       '#ef4444', 
    'text':         '#e2e8f0', 
    'text_dim':     '#64748b', 
    'text_bright':  '#f8fafc', 
    'input_bg':     '#0a0f1a', 
    'input_border': '#1e2a3a', 
    'disabled':     '#1a2330', 
    'disabled_txt': '#475569', 
} 
 
FONT_HEADING = ('Segoe UI', 11, 'bold') 
FONT_BODY    = ('Segoe UI', 10) 
FONT_SMALL   = ('Segoe UI', 9) 
FONT_MONO    = ('Consolas', 10) 
 
class ModernButton(tk.Button): 
    """Modern button with hover effects and disabled state management""" 
    def __init__(self, parent, text, command=None, color=None, always_enabled=False, **kw): 
        self.color = color or THEME['primary'] 
        self.always_enabled = always_enabled 
        super().__init__( 
            parent, text=text, command=command, 
            font=FONT_BODY, fg=THEME['text_bright'], bg=self.color, 
            activebackground=self.color, activeforeground=THEME['text_bright'], 
            bd=0, padx=12, pady=5, cursor='hand2', 
            relief='flat', highlightthickness=0 
        ) 
        self._disabled = False 
        if always_enabled: 
            self.config(state='normal') 
 
    def set_disabled(self, state): 
        if self.always_enabled: 
            return 
        self._disabled = state 
        if state: 
            self.config(state='disabled', bg=THEME['disabled'], fg=THEME['disabled_txt'], cursor='arrow') 
        else: 
            self.config(state='normal', bg=self.color, fg=THEME['text_bright'], cursor='hand2') 
 
class StepBox(tk.Frame): 
    """Step-by-step wizard box component""" 
    def __init__(self, parent, step_num: int, title: str): 
        super().__init__(parent, bg=THEME['card'], bd=1, relief='solid') 
        self.config(highlightbackground=THEME['border'], highlightthickness=1) 
        self.state = 'locked' 
         
        hdr = tk.Frame(self, bg=THEME['card']) 
        hdr.pack(fill='x', padx=10, pady=(6, 2)) 
         
        self.badge = tk.Label(hdr, text=str(step_num), font=FONT_SMALL, width=2, 
                               fg=THEME['card'], bg=THEME['text_dim'], relief='flat') 
        self.badge.pack(side='left', padx=(0, 6)) 
         
        self.title_lbl = tk.Label(hdr, text=title, font=FONT_HEADING, 
                                   fg=THEME['text_dim'], bg=THEME['card']) 
        self.title_lbl.pack(side='left') 
         
        self.status_lbl = tk.Label(hdr, text='🔒', font=('Segoe UI', 9), 
                                    fg=THEME['text_dim'], bg=THEME['card']) 
        self.status_lbl.pack(side='right') 
         
        self.content_frame = tk.Frame(self, bg=THEME['card']) 
        self.content_frame.pack(fill='x', padx=10, pady=(0, 6)) 
         
        self._set_state('locked') 
 
    def _set_state(self, state): 
        self.state = state 
        if state == 'locked': 
            self.config(highlightbackground=THEME['border']) 
            self.title_lbl.config(fg=THEME['text_dim']) 
            self.badge.config(bg=THEME['text_dim']) 
            self.status_lbl.config(text='🔒') 
            for w in self.content_frame.winfo_children(): 
                try: 
                    w.config(state='disabled') 
                except: 
                    pass 
        elif state == 'active': 
            self.config(highlightbackground=THEME['secondary']) 
            self.title_lbl.config(fg=THEME['secondary']) 
            self.badge.config(bg=THEME['secondary'], fg='white') 
            self.status_lbl.config(text='⚡ ACTIVE', fg=THEME['secondary']) 
            for w in self.content_frame.winfo_children(): 
                try: 
                    w.config(state='normal') 
                except: 
                    pass 
        elif state == 'done': 
            self.config(highlightbackground=THEME['success']) 
            self.title_lbl.config(fg=THEME['success']) 
            self.badge.config(bg=THEME['success'], text='✓', fg='white') 
            self.status_lbl.config(text='✓ COMPLETE', fg=THEME['success']) 
 
    def activate(self): self._set_state('active') 
    def complete(self): self._set_state('done') 
    def reset(self): self._set_state('locked') 
 
class PasswordEntry(tk.Frame): 
    """Password entry widget with show/hide toggle""" 
    def __init__(self, parent, on_change=None): 
        super().__init__(parent, bg=THEME['card']) 
        self._show = False 
        self.var = tk.StringVar() 
        self.on_change = on_change 
        self.entry = tk.Entry(self, textvariable=self.var, show='●', 
                               font=FONT_BODY, bg=THEME['input_bg'], 
                               fg=THEME['secondary'], insertbackground=THEME['secondary'], 
                               bd=1, relief='solid') 
        self.entry.pack(side='left', fill='x', expand=True, ipady=3) 
        self.entry.bind('<KeyRelease>', lambda e: self._on_change()) 
        self.toggle_btn = tk.Label(self, text='👁', font=FONT_SMALL, 
                                    bg=THEME['input_bg'], fg=THEME['text_dim'], 
                                    cursor='hand2', padx=5) 
        self.toggle_btn.pack(side='right') 
        self.toggle_btn.bind('<Button-1>', self._toggle) 
 
    def _toggle(self, e=None): 
        self._show = not self._show 
        self.entry.config(show='' if self._show else '●') 
        self.toggle_btn.config(text='🙈' if self._show else '👁') 
 
    def _on_change(self): 
        if self.on_change: 
            self.on_change() 
 
    def get(self): return self.var.get() 
    def set(self, v): self.var.set(v) 
    def clear(self): self.var.set('') 
    def config(self, **kw): self.entry.config(**kw) 
 
class PasswordAlert(tk.Toplevel): 
    """Critical password alert dialog - Fixed Version""" 
    def __init__(self, parent, password: str, on_confirm): 
        super().__init__(parent) 
        self.title("⚠️ CRITICAL") 
        self.configure(bg=THEME['bg']) 
        self.resizable(False, False) 
        self.grab_set() 
        self.focus_set() 
        self.overrideredirect(True) 
        self._on_confirm = on_confirm 
        self._password = password 
        self._visible = False 
        self._parent = parent  # Store parent reference 
        self._build(password) 
         
        self.update_idletasks() 
        w, h = 500, 420 
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2 
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2 
        self.geometry(f'{w}x{h}+{x}+{y}') 
         
        # Bind escape key to close 
        self.bind('<Escape>', lambda e: self.destroy()) 
         
        # Ensure window stays on top 
        self.lift() 
        self.attributes('-topmost', True) 
        self.after(100, lambda: self.attributes('-topmost', False)) 
 
    def _build(self, password): 
        outer = tk.Frame(self, bg=THEME['danger'], bd=2) 
        outer.pack(fill='both', expand=True, padx=3, pady=3) 
        inner = tk.Frame(outer, bg=THEME['bg']) 
        inner.pack(fill='both', expand=True, padx=2, pady=2) 
 
        hdr = tk.Frame(inner, bg=THEME['danger']) 
        hdr.pack(fill='x') 
        tk.Label(hdr, text='⚠️  CRITICAL WARNING  ⚠️', font=('Segoe UI', 13, 'bold'), 
                 fg='white', bg=THEME['danger'], pady=8).pack() 
 
        body = tk.Frame(inner, bg=THEME['bg']) 
        body.pack(fill='both', expand=True, padx=20, pady=12) 
 
        tk.Label(body, text='SAVE YOUR MASTER PASSWORD', font=FONT_HEADING, 
                 fg=THEME['warning'], bg=THEME['bg']).pack() 
 
        tk.Label(body, text='Without this password, your data is\nLOST FOREVER!', 
                 font=FONT_BODY, fg=THEME['danger'], bg=THEME['bg'], justify='center').pack(pady=5) 
 
        pw_frame = tk.Frame(body, bg=THEME['primary'], bd=1) 
        pw_frame.pack(fill='x', pady=12, padx=20) 
        tk.Label(pw_frame, text='MASTER PASSWORD', font=FONT_SMALL, 
                 fg=THEME['text_dim'], bg=THEME['primary'], pady=2).pack() 
         
        self.pw_lbl = tk.Label(pw_frame, text='●' * len(password), font=('Consolas', 15, 'bold'), 
                                fg='white', bg=THEME['primary'], pady=6) 
        self.pw_lbl.pack() 
         
        self.reveal_btn = tk.Label(pw_frame, text='👁 Reveal', font=FONT_SMALL, 
                                    fg=THEME['secondary'], bg=THEME['primary'], cursor='hand2', pady=2) 
        self.reveal_btn.pack() 
        self.reveal_btn.bind('<Button-1>', lambda e: self._toggle_pw(password)) 
 
        # ✅ Fixed copy button - using lambda with proper error handling 
        copy_btn = ModernButton(body, '📋 Copy Password',  
                                 command=self._copy_password,  # Changed to method reference 
                                 color=THEME['secondary']) 
        copy_btn.pack(pady=6) 
        self._password_to_copy = password  # Store password for copying 
 
        # Checkbox 
        self.check_var = tk.BooleanVar() 
        self.chk = tk.Checkbutton(body, text='✅ I have saved my password securely', 
                                   variable=self.check_var, font=FONT_SMALL, 
                                   fg=THEME['text'], bg=THEME['bg'], 
                                   selectcolor=THEME['card'], 
                                   command=self._check_enable) 
        self.chk.pack(pady=4) 
 
        # Confirm button 
        self.confirm_btn = ModernButton(body, '🔐 Confirm & Continue', command=self._confirm, 
                                         color=THEME['success']) 
        self.confirm_btn.pack(pady=10) 
        self.confirm_btn.config(state='disabled') 
        self.confirm_btn.set_disabled(True) 
 
    def _toggle_pw(self, password): 
        self._visible = not self._visible 
        self.pw_lbl.config(text=password if self._visible else '●' * len(password)) 
        self.reveal_btn.config(text='🙈 Hide' if self._visible else '👁 Reveal') 
 
    def _copy_password(self): 
        """Copy password to clipboard without causing errors""" 
        try: 
            # Clear clipboard and copy new text 
            self.clipboard_clear() 
            self.clipboard_append(self._password_to_copy) 
             
            # ✅ Use a temporary messagebox that doesn't conflict with dialog 
            # Instead of messagebox, create a small temporary label that shows "Copied!" 
            self._show_temp_message("✅ Copied!") 
        except Exception as e: 
            print(f"Copy error: {e}") 
 
    def _show_temp_message(self, message): 
        """Show a temporary message that disappears""" 
        # Create a small label that appears and fades 
        temp_label = tk.Label(self, text=message, font=('Segoe UI', 10, 'bold'), 
                               fg=THEME['success'], bg=THEME['bg']) 
        temp_label.place(relx=0.5, rely=0.85, anchor='center') 
        self.after(1500, temp_label.destroy) 
 
    def _check_enable(self): 
        """Enable confirm button when checkbox is checked""" 
        if self.check_var.get(): 
            self.confirm_btn.config(state='normal') 
            self.confirm_btn.set_disabled(False) 
        else: 
            self.confirm_btn.config(state='disabled') 
            self.confirm_btn.set_disabled(True) 
 
    def _confirm(self): 
        """Confirm and close the dialog""" 
        if self.check_var.get(): 
            # Release grab before destroying 
            try: 
                self.grab_release() 
            except: 
                pass 
            self.destroy() 
            if self._on_confirm: 
                self._on_confirm()
