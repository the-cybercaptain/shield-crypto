#!/usr/bin/env python3 
""" 
╔════════════════════════════════════════════════════════════════════════════════════════╗ 
║                                                                                        ║ 
║     ███████╗███████╗██╗   ██╗██████╗ ███████╗     ████████╗ ██████╗  ██████╗ ██╗       ║ 
║     ██╔════╝██╔════╝██║   ██║██╔══██╗██╔════╝     ╚══██╔══╝██╔═══██╗██╔═══██╗██║       ║ 
║     ███████╗█████╗  ██║   ██║██████╔╝█████╗          ██║   ██║   ██║██║   ██║██║       ║ 
║     ╚════██║██╔══╝  ██║   ██║██╔══██╗██╔══╝          ██║   ██║   ██║██║   ██║██║       ║ 
║     ███████║███████╗╚██████╔╝██║  ██║███████╗        ██║   ╚██████╔╝╚██████╔╝██║██████╔╝ 
║     ╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝        ╚═╝    ╚═════╝  ╚═════╝  ╚═╝═════╝ 
║                                                                                       ║ 
║                           🔐  SHIELD CRYPTO  🔐                                      ║ 
║                                                                                       ║ 
║                           ⚡ by CYBER CAPTAIN ⚡                                     ║ 
║                                                                                       ║ 
╚═══════════════════════════════════════════════════════════════════════════════════════╝ 
""" 
 
#!/usr/bin/env python3 
""" 
SHIELD CRYPTO - Main Application 
""" 
 
import tkinter as tk 
from tkinter import ttk 
from ui_components import THEME, FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_MONO 
from message_tab import MessageTab 
from file_tab import FileTab 
from history_tab import HistoryTab 
 
class SecureToolApp(tk.Tk): 
    def __init__(self): 
        super().__init__() 
        self.title('🛡️🔐 SHIELD CRYPTO 🔒⚡') 
        self.geometry('1200x750') 
        self.minsize(800, 600) 
        self.configure(bg=THEME['bg']) 
         
        self._build() 
 
    def _build(self): 
        # ========== HEADER (Fixed) ========== 
        header = tk.Frame(self, bg=THEME['panel'], height=60) 
        header.pack(fill='x', side='top') 
        header.pack_propagate(False) 
 
        logo = tk.Label(header, text='🔐 SHIELD CRYPTO', font=('Segoe UI', 20, 'bold'), 
                        fg=THEME['primary'], bg=THEME['panel']) 
        logo.pack(side='left', padx=20) 
         
        captain = tk.Label(header, text='⚡ by CYBER CAPTAIN ⚡', font=('Segoe UI', 10, 'bold'), 
                           fg=THEME['secondary'], bg=THEME['panel']) 
        captain.pack(side='right', padx=20) 
 
        # ========== TAB BAR (Fixed) ========== 
        tab_bar = tk.Frame(self, bg=THEME['card'], height=32) 
        tab_bar.pack(fill='x', side='top') 
        tab_bar.pack_propagate(False) 
 
        self.tabs = {} 
        self.active_tab = None 
 
        for label, key in [('MESSAGES', 'msg'), ('FILES', 'file'), ('HISTORY', 'hist')]: 
            btn = tk.Label(tab_bar, text=label, font=FONT_HEADING, fg=THEME['text_dim'], 
                           bg=THEME['card'], cursor='hand2', padx=25, pady=4) 
            btn.pack(side='left') 
            btn.bind('<Button-1>', lambda e, k=key: self._switch_tab(k)) 
            self.tabs[key] = btn 
 
        # ========== MAIN CONTENT AREA (Auto-Scroll) ========== 
        # Create a frame that will hold everything between tab_bar and footer 
        self.main_container = tk.Frame(self, bg=THEME['bg']) 
        self.main_container.pack(fill='both', expand=True) 
        self.main_container.pack_propagate(False) 
         
        # Create canvas with scrollbar INSIDE main_container 
        self.canvas = tk.Canvas(self.main_container, bg=THEME['bg'], highlightthickness=0) 
         
        # Minimal scrollbar - only visible when needed 
        self.scrollbar = ttk.Scrollbar(self.main_container, orient='vertical',  
                                        command=self.canvas.yview) 
         
        # Scrollable frame inside canvas 
        self.scrollable_frame = tk.Frame(self.canvas, bg=THEME['bg']) 
        self.scrollable_frame.bind( 
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")) 
        ) 
         
        # Add scrollable frame to canvas 
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame,  
                                                        anchor="nw", width=self.canvas.winfo_width()) 
         
        # Configure canvas scrolling 
        self.canvas.configure(yscrollcommand=self._on_scrollbar_update) 
         
        # Pack canvas and scrollbar 
        self.canvas.pack(side='left', fill='both', expand=True) 
         
        # Function to show/hide scrollbar based on content size 
        def _configure_canvas(event): 
            # Update scrollregion 
            self.canvas.configure(scrollregion=self.canvas.bbox("all")) 
            # Check if scrollbar is needed 
            self._update_scrollbar_visibility() 
         
        def _on_frame_configure(event): 
            # Set canvas window width to match canvas width 
            self.canvas.itemconfig(self.canvas_window, width=event.width) 
         
        self.scrollable_frame.bind('<Configure>', _configure_canvas) 
        self.canvas.bind('<Configure>', _on_frame_configure) 
         
        # Mousewheel scrolling 
        def _on_mousewheel(event): 
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units") 
         
        def _bind_mousewheel(event): 
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel) 
         
        def _unbind_mousewheel(event): 
            self.canvas.unbind_all("<MouseWheel>") 
         
        self.canvas.bind('<Enter>', _bind_mousewheel) 
        self.canvas.bind('<Leave>', _unbind_mousewheel) 
         
        # Store reference for visibility update 
        self._last_height = 0 
         
        # ========== TABS FRAMES ========== 
        self.msg_frame = MessageTab(self.scrollable_frame) 
        self.file_frame = FileTab(self.scrollable_frame) 
        self.hist_frame = HistoryTab(self.scrollable_frame) 
 
        # ========== FOOTER (Fixed) ========== 
        footer = tk.Frame(self, bg=THEME['panel'], height=28) 
        footer.pack(fill='x', side='bottom') 
        footer.pack_propagate(False) 
 
        tk.Label(footer, text='💻 Developed by MUHAMMAD HAMAD ⚡', font=FONT_SMALL, 
                 fg=THEME['text_dim'], bg=THEME['panel']).pack(side='right', padx=15) 
        tk.Label(footer, text='🔐 Double Encryption | Master Password Protected', font=FONT_SMALL, 
                 fg=THEME['text_dim'], bg=THEME['panel']).pack(side='left', padx=15) 
         
        # Start with messages tab 
        self._switch_tab('msg') 
         
        # Bind resize event to check scrollbar visibility 
        self.bind('<Configure>', lambda e: self._update_scrollbar_visibility()) 
     
    def _on_scrollbar_update(self, *args): 
        """Update scrollbar position and visibility""" 
        self.scrollbar.set(*args) 
        self._update_scrollbar_visibility() 
     
    def _update_scrollbar_visibility(self): 
        """Show scrollbar only when content exceeds visible area""" 
        try: 
            # Get canvas height and scrollable frame height 
            canvas_height = self.canvas.winfo_height() 
            frame_height = self.scrollable_frame.winfo_reqheight() 
             
            # Show scrollbar only if content is taller than canvas 
            if frame_height > canvas_height and canvas_height > 0: 
                if not self.scrollbar.winfo_ismapped(): 
                    self.scrollbar.pack(side='right', fill='y') 
            else: 
                if self.scrollbar.winfo_ismapped(): 
                    self.scrollbar.pack_forget() 
        except: 
            pass 
 
    def _switch_tab(self, key): 
        if self.active_tab: 
            if self.active_tab == 'msg':  
                self.msg_frame.pack_forget() 
            elif self.active_tab == 'file':  
                self.file_frame.pack_forget() 
            elif self.active_tab == 'hist':  
                self.hist_frame.pack_forget() 
            self.tabs[self.active_tab].config(fg=THEME['text_dim'], bg=THEME['card']) 
 
        self.active_tab = key 
        colors = {'msg': THEME['primary'], 'file': THEME['secondary'], 'hist': THEME['warning']} 
        self.tabs[key].config(fg=THEME['text_bright'], bg=colors.get(key, THEME['primary'])) 
 
        # Pack the selected tab 
        if key == 'msg':  
            self.msg_frame.pack(fill='both', expand=True, padx=10, pady=10) 
        elif key == 'file':  
            self.file_frame.pack(fill='both', expand=True, padx=10, pady=10) 
        elif key == 'hist':  
            self.hist_frame.pack(fill='both', expand=True, padx=10, pady=10) 
            self.hist_frame._load() 
         
        # Update scrollbar visibility after tab switch 
        self.after(100, self._update_scrollbar_visibility) 
         
        # Scroll to top 
        self.canvas.yview_moveto(0) 
 
if __name__ == '__main__': 
    app = SecureToolApp() 
    app.mainloop()
