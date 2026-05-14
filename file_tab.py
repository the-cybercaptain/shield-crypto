""" 
File Tab for SHIELD CRYPTO 
Handles file encryption and decryption 
""" 
 
import tkinter as tk 
from tkinter import filedialog, messagebox 
import threading 
import os 
import sys 
from ui_components import THEME, FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_MONO, ModernButton, StepBox, PasswordEntry, PasswordAlert 
 
# Import core logic 
try: 
    from core_code import ( 
        encrypt_file_data, decrypt_file_data, 
        save_to_history, load_history, clear_history, 
        validate_password, 
        read_enc_file, write_file, write_binary_file, get_file_size 
    ) 
except ImportError: 
    messagebox.showerror("Import Error", "core_code.py not found!\nPlace core_code.py in the same folder.") 
    sys.exit(1) 
 
class FileTab(tk.Frame): 
    def __init__(self, parent): 
        super().__init__(parent, bg=THEME['bg']) 
        self._build() 
        self._temp_password = None 
        self._fd_attempts = 3 
 
    def _build(self): 
        tab_bar = tk.Frame(self, bg=THEME['panel'], height=32) 
        tab_bar.pack(fill='x') 
        tab_bar.pack_propagate(False) 
         
        self._enc_btn = tk.Label(tab_bar, text='📁 ENCRYPT FILE', font=FONT_HEADING, 
                                  fg=THEME['text_bright'], bg=THEME['primary'], 
                                  cursor='hand2', padx=20, pady=4) 
        self._enc_btn.pack(side='left') 
        self._dec_btn = tk.Label(tab_bar, text='📂 DECRYPT FILE', font=FONT_HEADING, 
                                  fg=THEME['text_dim'], bg=THEME['panel'], 
                                  cursor='hand2', padx=20, pady=4) 
        self._dec_btn.pack(side='left') 
        self._enc_btn.bind('<Button-1>', lambda e: self._switch('enc')) 
        self._dec_btn.bind('<Button-1>', lambda e: self._switch('dec')) 
 
        self._enc_frame = tk.Frame(self, bg=THEME['bg']) 
        self._dec_frame = tk.Frame(self, bg=THEME['bg']) 
         
        self._build_encrypt() 
        self._build_decrypt() 
         
        self._enc_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5) 
        self._active = 'enc' 
 
    def _switch(self, mode): 
        if mode == self._active: 
            return 
        self._active = mode 
        if mode == 'enc': 
            self._dec_frame.pack_forget() 
            self._enc_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5) 
            self._enc_btn.config(bg=THEME['primary'], fg=THEME['text_bright']) 
            self._dec_btn.config(bg=THEME['panel'], fg=THEME['text_dim']) 
        else: 
            self._enc_frame.pack_forget() 
            self._dec_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5) 
            self._dec_btn.config(bg=THEME['primary'], fg=THEME['text_bright']) 
            self._enc_btn.config(bg=THEME['panel'], fg=THEME['text_dim']) 
 
    def _build_encrypt(self): 
        card = tk.Frame(self._enc_frame, bg=THEME['card'], bd=1, relief='solid') 
        card.pack(fill='both', expand=True) 
        card.config(highlightbackground=THEME['border'], highlightthickness=1) 
        tk.Label(card, text='ENCRYPT FILE', font=FONT_HEADING, 
                 fg=THEME['primary'], bg=THEME['card'], pady=4).pack() 
 
        clear_frame = tk.Frame(card, bg=THEME['card']) 
        clear_frame.pack(fill='x', padx=8, pady=(4, 0)) 
        clear_all_btn = ModernButton(clear_frame, '🗑 Clear All', command=self._reset_fe, 
                                      color=THEME['danger'], always_enabled=True) 
        clear_all_btn.pack(side='right') 
 
        s1 = StepBox(card, 1, 'Select File') 
        s1.pack(fill='x', padx=8, pady=3) 
        row = tk.Frame(s1.content_frame, bg=THEME['card']) 
        row.pack(fill='x') 
        self.fe_path = tk.Entry(row, font=FONT_BODY, bg=THEME['input_bg'], fg=THEME['text_bright'], bd=1, relief='solid') 
        self.fe_path.pack(side='left', fill='x', expand=True, ipady=2) 
        ModernButton(row, 'Browse', command=self._fe_browse, color=THEME['primary']).pack(side='right', padx=3) 
        self.fe_info = tk.Label(s1.content_frame, text='', font=FONT_SMALL, fg=THEME['text_dim'], bg=THEME['card']) 
        self.fe_info.pack(anchor='w', pady=2) 
        btn1 = ModernButton(s1.content_frame, 'Next →', command=lambda: self._fe_step1(s1), color=THEME['secondary']) 
        btn1.pack(pady=5) 
 
        s2 = StepBox(card, 2, 'Master Password') 
        s2.pack(fill='x', padx=8, pady=3) 
         
        def check_fe_pass(): 
            pw1 = self.fe_pw1.get() 
            pw2 = self.fe_pw2.get() 
            valid, _ = validate_password(pw1) 
             
            if valid and pw1 == pw2: 
                s2.complete() 
                s3.activate() 
                self.fe_out.config(state='normal') 
                self.fe_go.set_disabled(False) 
                self.fe_status.config(text='✓ Password validated', fg=THEME['success']) 
            else: 
                s2.activate() 
                s3.reset() 
                self.fe_out.config(state='disabled') 
                self.fe_go.set_disabled(True) 
                if pw1 != pw2 and len(pw1) > 0: 
                    self.fe_status.config(text='Passwords do not match!', fg=THEME['danger']) 
                elif len(pw1) < 6 and len(pw1) > 0: 
                    self.fe_status.config(text='Password must be at least 6 characters!', fg=THEME['danger']) 
         
        self.fe_pw1 = PasswordEntry(s2.content_frame, on_change=check_fe_pass) 
        self.fe_pw1.pack(fill='x', pady=2) 
        self.fe_pw1.config(state='disabled') 
        self.fe_pw2 = PasswordEntry(s2.content_frame, on_change=check_fe_pass) 
        self.fe_pw2.pack(fill='x', pady=2) 
        self.fe_pw2.config(state='disabled') 
        btn2 = ModernButton(s2.content_frame, 'Next →', command=self._fe_step2, color=THEME['secondary']) 
        btn2.pack(pady=5) 
 
        s3 = StepBox(card, 3, 'Save File') 
        s3.pack(fill='x', padx=8, pady=3) 
        row2 = tk.Frame(s3.content_frame, bg=THEME['card']) 
        row2.pack(fill='x') 
        self.fe_out = tk.Entry(row2, font=FONT_BODY, bg=THEME['input_bg'], fg=THEME['success'], bd=1, relief='solid') 
        self.fe_out.pack(side='left', fill='x', expand=True, ipady=2) 
        self.fe_out.config(state='disabled') 
        ModernButton(row2, 'Browse', command=self._fe_browse_save, color=THEME['primary']).pack(side='right', padx=3) 
        self.fe_go = ModernButton(s3.content_frame, 'ENCRYPT', command=self._do_fe_encrypt, color=THEME['primary']) 
        self.fe_go.pack(pady=5) 
        self.fe_go.set_disabled(True) 
 
        self.fe_status = tk.Label(card, text='', font=FONT_SMALL, fg=THEME['success'], bg=THEME['card']) 
        self.fe_status.pack(pady=3) 
 
        self.s1, self.s2, self.s3 = s1, s2, s3 
        self._fe_src = None 
 
    def _build_decrypt(self): 
        card = tk.Frame(self._dec_frame, bg=THEME['card'], bd=1, relief='solid') 
        card.pack(fill='both', expand=True) 
        card.config(highlightbackground=THEME['border'], highlightthickness=1) 
        tk.Label(card, text='DECRYPT FILE', font=FONT_HEADING, 
                 fg=THEME['secondary'], bg=THEME['card'], pady=4).pack() 
 
        clear_frame = tk.Frame(card, bg=THEME['card']) 
        clear_frame.pack(fill='x', padx=8, pady=(4, 0)) 
        clear_all_btn = ModernButton(clear_frame, '🗑 Clear All', command=self._reset_fd, 
                                      color=THEME['danger'], always_enabled=True) 
        clear_all_btn.pack(side='right') 
 
        ds1 = StepBox(card, 1, 'Select File') 
        ds1.pack(fill='x', padx=8, pady=3) 
        row = tk.Frame(ds1.content_frame, bg=THEME['card']) 
        row.pack(fill='x') 
        self.fd_path = tk.Entry(row, font=FONT_BODY, bg=THEME['input_bg'], fg=THEME['text_bright'], bd=1, relief='solid') 
        self.fd_path.pack(side='left', fill='x', expand=True, ipady=2) 
        ModernButton(row, 'Browse', command=self._fd_browse, color=THEME['primary']).pack(side='right', padx=3) 
        btn1 = ModernButton(ds1.content_frame, 'Next →', command=lambda: self._fd_step1(ds1), color=THEME['secondary']) 
        btn1.pack(pady=5) 
 
        ds2 = StepBox(card, 2, 'Master Password') 
        ds2.pack(fill='x', padx=8, pady=3) 
         
        self.fd_attempts = 3 
        self.fd_attempts_lbl = tk.Label(ds2.content_frame, text='Attempts: 3', font=FONT_SMALL, 
                                         fg=THEME['warning'], bg=THEME['card']) 
        self.fd_attempts_lbl.pack(anchor='center', pady=(0, 5)) 
         
        self.fd_pw = PasswordEntry(ds2.content_frame, on_change=None) 
        self.fd_pw.pack(fill='x', pady=5) 
        self.fd_pw.config(state='disabled') 
         
        self.fd_pw.entry.bind('<Return>', lambda e: self._do_fd_decrypt_with_password()) 
         
        self.fd_go_btn = ModernButton(ds2.content_frame, 'DECRYPT',  
                                       command=self._do_fd_decrypt_with_password, color=THEME['secondary']) 
        self.fd_go_btn.pack(pady=5) 
 
        ds3 = StepBox(card, 3, 'Save Decrypted File') 
        ds3.pack(fill='x', padx=8, pady=3) 
        ext_lbl = tk.Label(ds3.content_frame, text='Original extension: —', font=FONT_SMALL, 
                            fg=THEME['secondary'], bg=THEME['card']) 
        ext_lbl.pack(anchor='center', pady=5) 
         
        row2 = tk.Frame(ds3.content_frame, bg=THEME['card']) 
        row2.pack(fill='x', pady=5) 
        self.fd_out = tk.Entry(row2, font=FONT_BODY, bg=THEME['input_bg'], fg=THEME['success'], bd=1, relief='solid') 
        self.fd_out.pack(side='left', fill='x', expand=True, ipady=2) 
        self.fd_out.config(state='disabled') 
        ModernButton(row2, 'Browse', command=self._fd_browse_save, color=THEME['primary']).pack(side='right', padx=3) 
         
        self.fd_save = ModernButton(ds3.content_frame, 'SAVE', command=self._fd_save_file, color=THEME['success']) 
        self.fd_save.pack(pady=5) 
        self.fd_save.set_disabled(True) 
 
        self.fd_status = tk.Label(card, text='', font=FONT_SMALL, fg=THEME['success'], bg=THEME['card']) 
        self.fd_status.pack(pady=3) 
 
        self.ds1, self.ds2, self.ds3 = ds1, ds2, ds3 
        self.ext_lbl = ext_lbl 
        self._fd_content = None 
        self._fd_data = None 
        self._fd_ext = '' 
 
    def _fe_browse(self): 
        path = filedialog.askopenfilename() 
        if path: 
            self.fe_path.delete(0, 'end') 
            self.fe_path.insert(0, path) 
            size = get_file_size(path) 
            ext = os.path.splitext(path)[1] 
            self.fe_info.config(text=f'{os.path.basename(path)} | {size:,} bytes | {ext}') 
            self._fe_src = path 
            base = os.path.splitext(os.path.basename(path))[0] 
            self.fe_out.delete(0, 'end') 
            self.fe_out.insert(0, base) 
 
    def _fe_step1(self, s1): 
        if self._fe_src: 
            s1.complete() 
            self.s2.activate() 
            self.fe_pw1.config(state='normal') 
            self.fe_pw2.config(state='normal') 
 
    def _fe_step2(self): 
        pw1 = self.fe_pw1.get() 
        pw2 = self.fe_pw2.get() 
        valid, msg = validate_password(pw1) 
         
        if not valid: 
            self.fe_status.config(text=msg, fg=THEME['danger']) 
            return 
        if pw1 != pw2: 
            self.fe_status.config(text='Passwords do not match!', fg=THEME['danger']) 
            return 
         
        self.s2.complete() 
        self.s3.activate() 
        self.fe_out.config(state='normal') 
        self.fe_go.set_disabled(False) 
        self.fe_status.config(text='Password validated!', fg=THEME['success']) 
 
    def _fe_browse_save(self): 
        path = filedialog.asksaveasfilename(defaultextension='.enc', filetypes=[('Encrypted', '*.enc'), ('All', '*.*')]) 
        if path: 
            if path.endswith('.enc'): 
                path = path[:-4] 
            self.fe_out.delete(0, 'end') 
            self.fe_out.insert(0, path) 
 
    def _do_fe_encrypt(self): 
        pw = self.fe_pw1.get() 
        out = self.fe_out.get().strip() 
        if not out: 
            out = os.path.splitext(os.path.basename(self._fe_src))[0] 
        if not out.endswith('.enc'): 
            out += '.enc' 
 
        self.fe_go.set_disabled(True) 
        self.fe_status.config(text='Encrypting...', fg=THEME['secondary']) 
 
        def run(): 
            try: 
                with open(self._fe_src, 'rb') as f: 
                    data = f.read() 
                ext = os.path.splitext(self._fe_src)[1] 
                res = encrypt_file_data(data, pw, ext) 
                if res['success']: 
                    if isinstance(res['output_data'], str): 
                        data_to_write = res['output_data'].encode() 
                    else: 
                        data_to_write = res['output_data'] 
                    ok, _ = write_binary_file(out, data_to_write) 
                    if ok: 
                        save_to_history(out, f'FILE:{os.path.basename(self._fe_src)}', original_ext=ext) 
                        self.after(0, lambda: self._fe_done(out, pw)) 
                    else: 
                        self.after(0, lambda: self.fe_status.config(text='Save failed!', fg=THEME['danger'])) 
                else: 
                    self.after(0, lambda: self.fe_status.config(text=f'Failed: {res["error"]}', fg=THEME['danger'])) 
            except Exception as e: 
                self.after(0, lambda: self.fe_status.config(text=f'Error: {e}', fg=THEME['danger'])) 
            self.after(0, lambda: self.fe_go.set_disabled(False)) 
 
        threading.Thread(target=run, daemon=True).start() 
 
    def _fe_done(self, fname, pw): 
        self.s3.complete() 
        self.fe_status.config(text=f'Encrypted → {fname}', fg=THEME['success']) 
        PasswordAlert(self.winfo_toplevel(), pw, self._reset_fe) 
 
    def _reset_fe(self): 
        self.s1.reset(); self.s1.activate() 
        self.s2.reset(); self.s3.reset() 
        self.fe_path.delete(0, 'end') 
        self.fe_pw1.set(''); self.fe_pw2.set('') 
        self.fe_out.delete(0, 'end') 
        self.fe_info.config(text='') 
        self.fe_pw1.config(state='disabled'); self.fe_pw2.config(state='disabled') 
        self.fe_out.config(state='disabled') 
        self.fe_go.set_disabled(True) 
        self.fe_status.config(text='') 
        self._fe_src = None 
 
    def _fd_browse(self): 
        path = filedialog.askopenfilename(filetypes=[('Encrypted', '*.enc'), ('All', '*.*')]) 
        if path: 
            self.fd_path.delete(0, 'end') 
            self.fd_path.insert(0, path) 
 
    def _fd_step1(self, ds1): 
        path = self.fd_path.get().strip() 
        if not path or not os.path.exists(path): 
            self.fd_status.config(text='File not found!', fg=THEME['danger']) 
            return 
        content, _ = read_enc_file(path) 
        if content is None: 
            self.fd_status.config(text='Cannot read file!', fg=THEME['danger']) 
            return 
        self._fd_content = content 
        self.fd_attempts = 3 
        self.fd_attempts_lbl.config(text='Attempts: 3', fg=THEME['warning']) 
        ds1.complete() 
        self.ds2.activate() 
        self.fd_pw.config(state='normal') 
        self.fd_status.config(text='File loaded, enter password') 
 
    def _do_fd_decrypt_with_password(self): 
        pw = self.fd_pw.get() 
        if len(pw) < 6: 
            self.fd_status.config(text='Password must be at least 6 characters!', fg=THEME['danger']) 
            return 
         
        self.fd_go_btn.set_disabled(True) 
        self.fd_status.config(text='Decrypting...', fg=THEME['secondary']) 
         
        def run(): 
            res = decrypt_file_data(self._fd_content, pw) 
             
            if res['success']: 
                self.after(0, lambda: self._fd_done(res['data'], res['original_ext'])) 
            else: 
                self.fd_attempts -= 1 
                self.after(0, lambda: self._fd_fail(res.get('error', 'Decryption failed'))) 
         
        threading.Thread(target=run, daemon=True).start() 
 
    def _fd_done(self, data, ext): 
        self._fd_data = data 
        self._fd_ext = ext 
        self.ds2.complete() 
        self.ds3.activate() 
        self.ext_lbl.config(text=f'Original extension: {ext or "unknown"}') 
        base = os.path.splitext(os.path.basename(self.fd_path.get()))[0] 
        if base.endswith('.enc'): 
            base = base[:-4] 
        self.fd_out.config(state='normal') 
        self.fd_out.delete(0, 'end') 
        self.fd_out.insert(0, base + ext) 
        self.fd_save.set_disabled(False) 
        self.fd_status.config(text='Decrypted! Ready to save.', fg=THEME['success']) 
        self.fd_go_btn.set_disabled(False) 
        self.fd_pw.clear() 
        self.fd_pw.config(state='disabled') 
 
    def _fd_fail(self, error): 
        self.fd_go_btn.set_disabled(False) 
        self.fd_attempts_lbl.config(text=f'Attempts: {self.fd_attempts}', fg=THEME['danger']) 
         
        if self.fd_attempts <= 0: 
            self.fd_status.config(text='Too many failed attempts! Resetting...', fg=THEME['danger']) 
            self.after(1500, self._reset_fd) 
        else: 
            self.fd_status.config(text=f'Wrong password! {self.fd_attempts} attempts left', fg=THEME['danger']) 
            self.fd_pw.clear() 
            self.fd_pw.entry.focus() 
 
    def _reset_fd(self): 
        self.ds1.reset() 
        self.ds1.activate() 
        self.ds2.reset() 
        self.ds3.reset() 
        self.fd_path.delete(0, 'end') 
        self.fd_pw.clear() 
        self.fd_pw.config(state='disabled') 
        self.fd_out.delete(0, 'end') 
        self.fd_out.insert(0, '') 
        self.fd_out.config(state='disabled') 
        self.fd_save.set_disabled(True) 
        self.ext_lbl.config(text='Original extension: —') 
        self.fd_status.config(text='') 
        self.fd_attempts = 3 
        self.fd_attempts_lbl.config(text='Attempts: 3', fg=THEME['warning']) 
        self.fd_go_btn.set_disabled(False) 
        self._fd_content = None 
        self._fd_data = None 
        self._fd_ext = '' 
        self._temp_password = None 
 
    def _fd_browse_save(self): 
        path = filedialog.asksaveasfilename(defaultextension=self._fd_ext, filetypes=[('All', '*.*')]) 
        if path: 
            self.fd_out.delete(0, 'end') 
            self.fd_out.insert(0, path) 
 
    def _fd_save_file(self): 
        fname = self.fd_out.get().strip() 
        if not fname: 
            self.fd_status.config(text='Enter filename!', fg=THEME['danger']) 
            return 
        ok, _ = write_binary_file(fname, self._fd_data) 
        if ok: 
            self.fd_status.config(text=f'Saved → {fname}', fg=THEME['success']) 
            self.ds3.complete() 
        else: 
            self.fd_status.config(text='Save failed!', fg=THEME['danger'])