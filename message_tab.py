""" 
Message Tab for SHIELD CRYPTO 
Handles message encryption and decryption 
""" 
 
import tkinter as tk 
from tkinter import filedialog, messagebox, scrolledtext 
import threading 
import os 
import sys 
from ui_components import THEME, FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_MONO, ModernButton, StepBox, PasswordEntry, PasswordAlert 
 
# Import core logic 
try: 
    from core_code import ( 
        encrypt_message, decrypt_message, 
        save_to_history, load_history, clear_history, 
        validate_password, validate_message, 
        read_enc_file, write_file, write_binary_file 
    ) 
except ImportError: 
    messagebox.showerror("Import Error", "core_code.py not found!\nPlace core_code.py in the same folder.") 
    sys.exit(1) 
 
class MessageTab(tk.Frame): 
    def __init__(self, parent): 
        super().__init__(parent, bg=THEME['bg']) 
        self._build() 
        self._temp_password = None 
        self._dec_attempts = 3 
 
    def _build(self): 
        tab_bar = tk.Frame(self, bg=THEME['panel'], height=32) 
        tab_bar.pack(fill='x') 
        tab_bar.pack_propagate(False) 
         
        self._enc_btn = tk.Label(tab_bar, text='🔒 ENCRYPT', font=FONT_HEADING, 
                                  fg=THEME['text_bright'], bg=THEME['primary'], 
                                  cursor='hand2', padx=20, pady=4) 
        self._enc_btn.pack(side='left') 
        self._dec_btn = tk.Label(tab_bar, text='🔓 DECRYPT', font=FONT_HEADING, 
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
         
        tk.Label(card, text='ENCRYPT MESSAGE', font=FONT_HEADING, 
                 fg=THEME['primary'], bg=THEME['card'], pady=4).pack() 
 
        clear_frame = tk.Frame(card, bg=THEME['card']) 
        clear_frame.pack(fill='x', padx=8, pady=(4, 0)) 
        clear_all_btn = ModernButton(clear_frame, '🗑 Clear All', command=self._reset_enc, 
                                      color=THEME['danger'], always_enabled=True) 
        clear_all_btn.pack(side='right') 
 
        self.enc_step1 = StepBox(card, 1, 'Your Message') 
        self.enc_step1.pack(fill='x', padx=8, pady=3) 
        self.enc_msg = scrolledtext.ScrolledText(self.enc_step1.content_frame, height=12, 
                                                   font=FONT_BODY, bg=THEME['input_bg'], 
                                                   fg=THEME['text'], wrap=tk.WORD, 
                                                   insertbackground=THEME['secondary'], 
                                                   bd=1, relief='solid') 
        self.enc_msg.pack(fill='x', ipady=4) 
        self.enc_msg.config(state='normal') 
        btn1 = ModernButton(self.enc_step1.content_frame, 'Next →', command=self._enc_step1_done, 
                             color=THEME['secondary']) 
        btn1.pack(pady=5) 
 
        self.enc_step2 = StepBox(card, 2, 'Padding Length') 
        self.enc_step2.pack(fill='x', padx=8, pady=3) 
        tk.Label(self.enc_step2.content_frame, text='Enter Padding Length :', font=FONT_SMALL, 
                 fg=THEME['text_dim'], bg=THEME['card']).pack(anchor='w') 
        self.enc_pad = tk.Entry(self.enc_step2.content_frame, width=10, font=FONT_BODY, 
                                 bg=THEME['input_bg'], fg=THEME['secondary'], bd=1, relief='solid', 
                                 insertbackground=THEME['secondary'], insertwidth=2) 
        self.enc_pad.insert(0, '3') 
        self.enc_pad.pack(anchor='w', pady=2) 
        self.enc_pad.config(state='disabled') 
        btn2 = ModernButton(self.enc_step2.content_frame, 'Next →', command=self._enc_step2_done, 
                             color=THEME['secondary']) 
        btn2.pack(pady=5) 
 
        self.enc_step3 = StepBox(card, 3, 'Master Password') 
        self.enc_step3.pack(fill='x', padx=8, pady=3) 
         
        def check_enc_pass(): 
            pw1 = self.enc_pw1.get() 
            pw2 = self.enc_pw2.get() 
            valid, _ = validate_password(pw1) 
             
            if valid and pw1 == pw2: 
                self.enc_step3.complete() 
                self.enc_step4.activate() 
                self.enc_out.config(state='normal') 
                self.enc_go.set_disabled(False) 
                self.enc_status.config(text='✓ Password validated', fg=THEME['success']) 
            else: 
                self.enc_step3.activate() 
                self.enc_step4.reset() 
                self.enc_out.config(state='disabled') 
                self.enc_go.set_disabled(True) 
                if pw1 != pw2 and len(pw1) > 0: 
                    self.enc_status.config(text='Passwords do not match!', fg=THEME['danger']) 
                elif len(pw1) < 6 and len(pw1) > 0: 
                    self.enc_status.config(text='Password must be at least 6 characters!', fg=THEME['danger']) 
                else: 
                    self.enc_status.config(text='') 
         
        self.enc_pw1 = PasswordEntry(self.enc_step3.content_frame, on_change=check_enc_pass) 
        self.enc_pw1.pack(fill='x', pady=2) 
        self.enc_pw1.config(state='disabled') 
         
        self.enc_pw2 = PasswordEntry(self.enc_step3.content_frame, on_change=check_enc_pass) 
        self.enc_pw2.pack(fill='x', pady=2) 
        self.enc_pw2.config(state='disabled') 
         
        btn3 = ModernButton(self.enc_step3.content_frame, 'Next →', command=self._enc_step3_done, 
                             color=THEME['secondary']) 
        btn3.pack(pady=5) 
 
        self.enc_step4 = StepBox(card, 4, 'Save File') 
        self.enc_step4.pack(fill='x', padx=8, pady=3) 
        row = tk.Frame(self.enc_step4.content_frame, bg=THEME['card']) 
        row.pack(fill='x') 
        self.enc_out = tk.Entry(row, font=FONT_BODY, bg=THEME['input_bg'], 
                                 fg=THEME['success'], bd=1, relief='solid') 
        self.enc_out.insert(0, 'encrypted_msg') 
        self.enc_out.pack(side='left', fill='x', expand=True, ipady=2) 
        self.enc_out.config(state='disabled') 
        browse_btn = ModernButton(row, 'Browse', command=self._enc_browse, color=THEME['primary']) 
        browse_btn.pack(side='right', padx=3) 
        self.enc_go = ModernButton(self.enc_step4.content_frame, 'ENCRYPT', command=self._do_encrypt, 
                                    color=THEME['primary']) 
        self.enc_go.pack(pady=5) 
        self.enc_go.set_disabled(True) 
 
        self.enc_status = tk.Label(card, text='', font=FONT_SMALL, 
                                    fg=THEME['success'], bg=THEME['card']) 
        self.enc_status.pack(pady=3) 
 
    def _build_decrypt(self): 
        card = tk.Frame(self._dec_frame, bg=THEME['card'], bd=1, relief='solid') 
        card.pack(fill='both', expand=True) 
        card.config(highlightbackground=THEME['border'], highlightthickness=1) 
         
        tk.Label(card, text='DECRYPT MESSAGE', font=FONT_HEADING, 
                 fg=THEME['secondary'], bg=THEME['card'], pady=4).pack() 
 
        clear_frame = tk.Frame(card, bg=THEME['card']) 
        clear_frame.pack(fill='x', padx=8, pady=(4, 0)) 
        clear_all_btn = ModernButton(clear_frame, '🗑 Clear All', command=self._reset_dec, 
                                      color=THEME['danger'], always_enabled=True) 
        clear_all_btn.pack(side='right') 
 
        self.dec_step1 = StepBox(card, 1, 'Select Encrypted File') 
        self.dec_step1.pack(fill='x', padx=8, pady=3) 
        row = tk.Frame(self.dec_step1.content_frame, bg=THEME['card']) 
        row.pack(fill='x') 
        self.dec_file = tk.Entry(row, font=FONT_BODY, bg=THEME['input_bg'], 
                                  fg=THEME['text_bright'], bd=1, relief='solid') 
        self.dec_file.pack(side='left', fill='x', expand=True, ipady=2) 
        browse_dec = ModernButton(row, 'Browse', command=self._dec_browse, color=THEME['warning']) 
        browse_dec.pack(side='right', padx=3) 
        btn1d = ModernButton(self.dec_step1.content_frame, 'Next →', command=self._dec_step1_done, 
                              color=THEME['secondary']) 
        btn1d.pack(pady=5) 
 
        self.dec_step2 = StepBox(card, 2, 'Master Password') 
        self.dec_step2.pack(fill='x', padx=8, pady=3) 
         
        self.dec_attempts = 3 
        self.dec_attempts_lbl = tk.Label(self.dec_step2.content_frame, text='Attempts remaining: 3', 
                                          font=FONT_SMALL, fg=THEME['warning'], bg=THEME['card']) 
        self.dec_attempts_lbl.pack(anchor='center', pady=(0, 5)) 
         
        self.dec_pw = PasswordEntry(self.dec_step2.content_frame) 
        self.dec_pw.pack(fill='x', pady=5) 
        self.dec_pw.config(state='disabled') 
         
        self.dec_step3 = StepBox(card, 3, 'Enter Padding') 
        self.dec_step3.pack(fill='x', padx=8, pady=3) 
         
        tk.Label(self.dec_step3.content_frame, text='Enter Padding Length:', font=FONT_SMALL, 
                 fg=THEME['text_dim'], bg=THEME['card']).pack(anchor='center') 
        self.dec_padding_entry = tk.Entry(self.dec_step3.content_frame, width=10, font=FONT_BODY, 
                                           bg=THEME['input_bg'], fg=THEME['secondary'],  
                                           bd=1, relief='solid', state='disabled', justify='center', 
                                           insertbackground=THEME['secondary'],insertwidth=2) 
         
        self.dec_padding_entry.insert(0, '3') 
        self.dec_padding_entry.pack(pady=5) 
         
        self.dec_go = ModernButton(self.dec_step3.content_frame, 'DECRYPT',  
                                    command=self._do_decrypt, color=THEME['secondary']) 
        self.dec_go.pack(pady=5) 
        self.dec_go.set_disabled(True) 
 
        self.dec_step4 = StepBox(card, 4, 'Decrypted Message') 
        self.dec_step4.pack(fill='x', padx=8, pady=3) 
         
        self.dec_result = scrolledtext.ScrolledText(self.dec_step4.content_frame, height=10, 
                                                     font=FONT_MONO, bg=THEME['input_bg'], 
                                                     fg=THEME['success'], wrap=tk.WORD, 
                                                     insertbackground=THEME['secondary'], 
                                                     bd=1, relief='solid') 
        self.dec_result.pack(fill='x', pady=5) 
        self.dec_result.config(state='disabled') 
         
        save_frame = tk.Frame(self.dec_step4.content_frame, bg=THEME['card']) 
        save_frame.pack(fill='x', pady=5) 
 
        tk.Label(save_frame, text='Save to:', font=FONT_SMALL, 
                fg=THEME['text_dim'], bg=THEME['card']).pack(side='left') 
 
        self.dec_save = tk.Entry(save_frame, font=FONT_BODY, bg=THEME['input_bg'], 
                                fg=THEME['success'], bd=1, relief='solid') 
        self.dec_save.insert(0, 'decrypted_msg') 
        self.dec_save.pack(side='left', fill='x', expand=True, ipady=2, padx=(5, 5)) 
        self.dec_save.config(state='disabled') 
 
        save_browse_btn = ModernButton(save_frame, 'Browse', command=self._dec_browse_save, 
                                        color=THEME['primary']) 
        save_browse_btn.pack(side='left', padx=2) 
 
        save_btn = ModernButton(save_frame, 'Save', command=self._save_decrypted, 
                                 color=THEME['success']) 
        save_btn.pack(side='left', padx=2) 
        save_btn.set_disabled(True) 
        self.dec_save_btn = save_btn 
 
        self.dec_status = tk.Label(card, text='', font=FONT_SMALL, 
                                    fg=THEME['success'], bg=THEME['card']) 
        self.dec_status.pack(pady=3) 
 
        self._dec_content = None 
        self._stored_padding = None 
 
    def _enc_browse(self): 
        path = filedialog.asksaveasfilename(defaultextension='.enc', 
                                              filetypes=[('Encrypted', '*.enc'), ('All', '*.*')]) 
        if path: 
            if path.endswith('.enc'): 
                path = path[:-4] 
            self.enc_out.delete(0, 'end') 
            self.enc_out.insert(0, path) 
 
    def _enc_step1_done(self): 
        msg = self.enc_msg.get('1.0', 'end-1c').strip() 
        valid, _ = validate_message(msg) 
        if not valid: 
            self.enc_status.config(text='Message cannot be empty!', fg=THEME['danger']) 
            return 
        self.enc_step1.complete() 
        self.enc_step2.activate() 
        self.enc_pad.config(state='normal') 
        self.enc_status.config(text='') 
 
    def _enc_step2_done(self): 
        try: 
            pad = int(self.enc_pad.get()) 
            if 1 <= pad <= 1000: 
                self.enc_step2.complete() 
                self.enc_step3.activate() 
                self.enc_pw1.config(state='normal') 
                self.enc_pw2.config(state='normal') 
                self.enc_status.config(text='') 
            else: 
                self.enc_status.config(text='Padding must be 1-1000', fg=THEME['danger']) 
        except: 
            self.enc_status.config(text='Invalid padding!', fg=THEME['danger']) 
 
    def _enc_step3_done(self): 
        pw1 = self.enc_pw1.get() 
        pw2 = self.enc_pw2.get() 
        valid, msg = validate_password(pw1) 
         
        if not valid: 
            self.enc_status.config(text=msg, fg=THEME['danger']) 
            return 
        if pw1 != pw2: 
            self.enc_status.config(text='Passwords do not match!', fg=THEME['danger']) 
            return 
         
        self.enc_step3.complete() 
        self.enc_step4.activate() 
        self.enc_out.config(state='normal') 
        self.enc_go.set_disabled(False) 
        self.enc_status.config(text='Password validated!', fg=THEME['success']) 
 
    def _do_encrypt(self): 
        msg = self.enc_msg.get('1.0', 'end-1c').strip() 
        pad = int(self.enc_pad.get()) 
        pw = self.enc_pw1.get() 
        out = self.enc_out.get().strip() or 'encrypted_msg' 
        if not out.endswith('.enc'): 
            out += '.enc' 
 
        self.enc_go.set_disabled(True) 
        self.enc_status.config(text='Encrypting...', fg=THEME['secondary']) 
 
        def run(): 
            res = encrypt_message(msg, pw, pad) 
            if res['success']: 
                if isinstance(res['output_data'], str): 
                    data_to_write = res['output_data'].encode() 
                else: 
                    data_to_write = res['output_data'] 
                ok, _ = write_binary_file(out, data_to_write) 
                if ok: 
                    save_to_history(out, 'MESSAGE', pad) 
                    self.after(0, lambda: self._enc_done(out, pw)) 
                else: 
                    self.after(0, lambda: self.enc_status.config(text='Save failed!', fg=THEME['danger'])) 
            else: 
                self.after(0, lambda: self.enc_status.config(text=f'Failed: {res["error"]}', fg=THEME['danger'])) 
            self.after(0, lambda: self.enc_go.set_disabled(False)) 
 
        threading.Thread(target=run, daemon=True).start() 
 
    def _enc_done(self, filename, password): 
        self.enc_step4.complete() 
        self.enc_status.config(text=f'Encrypted → {filename}', fg=THEME['success']) 
        PasswordAlert(self.winfo_toplevel(), password, self._reset_enc) 
 
    def _reset_enc(self): 
        self.enc_step1.reset() 
        self.enc_step1.activate() 
        self.enc_msg.config(state='normal') 
        self.enc_msg.delete('1.0', 'end') 
        self.enc_step2.reset() 
        self.enc_step3.reset() 
        self.enc_step4.reset() 
        self.enc_pad.config(state='disabled') 
        self.enc_pad.delete(0, 'end') 
        self.enc_pad.insert(0, '3') 
        self.enc_pw1.set('') 
        self.enc_pw2.set('') 
        self.enc_pw1.config(state='disabled') 
        self.enc_pw2.config(state='disabled') 
        self.enc_out.delete(0, 'end') 
        self.enc_out.insert(0, 'encrypted_msg') 
        self.enc_out.config(state='disabled') 
        self.enc_go.set_disabled(True) 
        self.enc_status.config(text='') 
 
    def _dec_browse(self): 
        path = filedialog.askopenfilename(filetypes=[('Encrypted', '*.enc'), ('All', '*.*')]) 
        if path: 
            self.dec_file.delete(0, 'end') 
            self.dec_file.insert(0, path) 
 
    def _dec_step1_done(self): 
        path = self.dec_file.get().strip() 
        if not path or not os.path.exists(path): 
            self.dec_status.config(text='File not found!', fg=THEME['danger']) 
            return 
        content, _ = read_enc_file(path) 
        if content is None: 
            self.dec_status.config(text='Cannot read file!', fg=THEME['danger']) 
            return 
        self._dec_content = content 
        self.dec_attempts = 3 
        self.dec_attempts_lbl.config(text='Attempts remaining: 3', fg=THEME['warning']) 
        self.dec_step1.complete() 
        self.dec_step2.activate() 
        self.dec_pw.config(state='normal') 
        self.dec_padding_entry.config(state='normal') 
        self.dec_go.set_disabled(False) 
        self.dec_status.config(text='File loaded, enter password and padding') 
 
    def _do_decrypt(self): 
        pw = self.dec_pw.get() 
        if len(pw) < 6: 
            self.dec_status.config(text='Password must be at least 6 characters!', fg=THEME['danger']) 
            return 
         
        try: 
            user_padding = int(self.dec_padding_entry.get()) 
            if user_padding < 1 or user_padding > 1000: 
                self.dec_status.config(text='Padding must be between 1 and 1000!', fg=THEME['danger']) 
                return 
        except: 
            self.dec_status.config(text='Invalid padding! Enter a number.', fg=THEME['danger']) 
            return 
         
        self.dec_go.set_disabled(True) 
        self.dec_status.config(text='Decrypting...', fg=THEME['secondary']) 
         
        def run(): 
            res = decrypt_message(self._dec_content, pw, user_padding) 
             
            if res['success']: 
                self.after(0, lambda: self._dec_done(res['message'])) 
            else: 
                self.dec_attempts -= 1 
                self.after(0, lambda: self._dec_fail(res.get('error', 'Decryption failed'))) 
         
        threading.Thread(target=run, daemon=True).start() 
 
    def _dec_done(self, msg): 
        self.dec_step2.complete() 
        self.dec_step3.complete() 
        self.dec_step4.activate() 
        self.dec_result.config(state='normal') 
        self.dec_result.delete('1.0', 'end') 
        self.dec_result.insert('1.0', msg) 
        self.dec_result.config(state='disabled') 
        self.dec_save.config(state='normal') 
        self.dec_save_btn.set_disabled(False) 
        self.dec_status.config(text='Decrypted successfully!', fg=THEME['success']) 
        self.dec_go.set_disabled(False) 
        self.dec_attempts = 3 
        self.dec_attempts_lbl.config(text='Attempts remaining: 3', fg=THEME['warning']) 
        self.dec_pw.clear() 
        self.dec_pw.config(state='disabled') 
 
    def _dec_fail(self, error): 
        self.dec_go.set_disabled(False) 
        self.dec_attempts_lbl.config(text=f'Attempts remaining: {self.dec_attempts}', fg=THEME['danger']) 
         
        if self.dec_attempts <= 0: 
            self.dec_status.config(text='Too many failed attempts! Resetting...', fg=THEME['danger']) 
            self.after(1500, self._reset_dec) 
        else: 
            self.dec_status.config(text=f'Wrong password! {self.dec_attempts} attempts left', fg=THEME['danger']) 
            self.dec_pw.clear() 
            self.dec_pw.entry.focus() 
 
    def _reset_dec(self): 
        self.dec_step1.reset() 
        self.dec_step1.activate() 
        self.dec_step2.reset() 
        self.dec_step3.reset() 
        self.dec_step4.reset() 
        self.dec_file.delete(0, 'end') 
        self.dec_pw.clear() 
        self.dec_pw.config(state='disabled') 
        self.dec_padding_entry.config(state='normal') 
        self.dec_padding_entry.delete(0, 'end') 
        self.dec_padding_entry.insert(0, '3') 
        self.dec_padding_entry.config(state='disabled') 
        self.dec_result.config(state='normal') 
        self.dec_result.delete('1.0', 'end') 
        self.dec_result.config(state='disabled') 
        self.dec_save.delete(0, 'end') 
        self.dec_save.insert(0, 'decrypted_msg') 
        self.dec_save.config(state='disabled') 
        self.dec_save_btn.set_disabled(True) 
        self.dec_status.config(text='') 
        self.dec_attempts = 3 
        self.dec_attempts_lbl.config(text='Attempts remaining: 3', fg=THEME['warning']) 
        self.dec_go.set_disabled(True) 
        self._dec_content = None 
        self._stored_padding = None 
        self._temp_password = None 
 
    def _dec_browse_save(self): 
        path = filedialog.asksaveasfilename(defaultextension='.txt', 
                                              filetypes=[('Text files', '*.txt'), ('All files', '*.*')]) 
        if path: 
            if path.endswith('.txt'): 
                path = path[:-4] 
            self.dec_save.delete(0, 'end') 
            self.dec_save.insert(0, path) 
 
    def _save_decrypted(self): 
        fname = self.dec_save.get().strip() or 'decrypted_msg' 
        if not fname.endswith('.txt'): 
            fname += '.txt' 
        text = self.dec_result.get('1.0', 'end-1c').strip() 
        ok, _ = write_file(fname, text) 
        if ok: 
            self.dec_status.config(text=f'Saved → {fname}', fg=THEME['success']) 
            self.dec_step4.complete() 
        else: 
            self.dec_status.config(text='Save failed!', fg=THEME['danger'])