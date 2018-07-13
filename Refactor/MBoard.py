import tkinter as tk

PHASES = ("Day","Night")
MAFIA_ROLES = [ "MAFIA" , "GODFATHER", "STRIPPER"]
TOWN_ROLES    = [ "TOWN", "COP", "DOCTOR", "CELEB", "MILLER", "MILKY"]
ROGUE_ROLES = ["IDIOT"]
ALL_ROLES = TOWN_ROLES + MAFIA_ROLES + ROGUE_ROLES

class MBoard(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        
    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World!"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")
        
        self.quit = tk.Button(self, text="QUIT", fg="red", command=root.destroy)
        self.quit.pack(side="bottom")
        
    def say_hi(self):
        print("Hello!")
        
class MBoardgame_state(tk.Frame):
    def __init__(self, master=None, game_state=None):
        super().__init__(master)
        self.game_state = game_state
        
        self.create_widgets()
        
        self.pack()
        
    def create_widgets(self):
    
        day_phase_frame = tk.Frame()
        
        self.day_box = tk.Entry(day_phase_frame, width=3)
        self.day_box.insert(0,str(self.game_state.day))
        self.day_box.bind('<Return>', self.day_phase_send)
        self.day_box.pack(side="left")
        
        self.phase_box = tk.Entry(day_phase_frame, width=5)
        self.phase_box.insert(0,self.game_state.phase)
        self.phase_box.bind('<Return>', self.day_phase_send)
        self.phase_box.pack(side="left")
        
        #day_phase_button = tk.Button(day_phase_frame, bg="green", text=">", command=self.day_phase_send)
        #day_phase_button.pack(side="right")
        
        self.player_frame = tk.Frame()
        
        self.player_var = tk.StringVar()
        
        player_list = [(p.id+":"+p.name) for p in self.game_state.players]
        
        self.player_option = tk.OptionMenu(self.player_frame, self.player_var,
                                           None, *player_list, 
                                           command=self.update_player_view)
        self.player_option.pack(side="left")
        
        
        view_frame = tk.Frame()
        self.view_id = tk.Label(view_frame, text="")
        self.view_id.pack(side="top")
        self.view_name = tk.Entry(view_frame)
        self.view_name.bind('<Return>', self.player_view_send)
        self.view_name.pack(side="top")
        
        self.view_role_var = tk.StringVar()
        self.view_role = tk.OptionMenu(view_frame, self.view_role_var, *ALL_ROLES)
        self.view_role.pack(side="top")
        
        self.view_vote_var = tk.StringVar()
        self.view_vote = tk.OptionMenu(view_frame, self.view_vote_var, None)
        self.view_vote.pack(side="top")
        
        self.view_target = tk.StringVar()
        self.view_target = tk.OptionMenu(view_frame, self.view_vote_var, None)
        self.view_target.pack(side="top")
        
        day_phase_frame.pack(side="top", fill="x")
        self.player_frame.pack(side="top", fill="x")
        view_frame.pack(side="top", fill = "x")
        
    def update_widgets(self):
    
        self.day_box.delete(0,tk.END)
        self.day_box.insert(0,str(self.game_state.day))
        self.phase_box.delete(0,tk.END)
        self.phase_box.insert(0,self.game_state.phase)
        
        self.player_option.destroy()
        
        player_list = [(p.id+":"+p.name) for p in self.game_state.players]
        self.player_option = tk.OptionMenu(self.player_frame, self.player_var,
                                           None, *player_list, 
                                           command=self.update_player_view)
        self.player_option.pack(side="left")                                           
        self.update_player_view()
        
        print(self.game_state)
        
    def update_player_view(self, arg=None):
        player_info = self.player_var.get()
        player_id = player_info.split(":")[0]
        try:
            player = [p for p in self.game_state.players if p.id == player_id][0]
        except IndexError as e:
            self.view_id["text"] = ""
            self.view_name.delete(0,tk.END)
            return

        self.player_var.set(player.id+":"+player.name)
            
        self.view_id["text"] = player.id
        self.view_name.delete(0,tk.END)
        self.view_name.insert(0,player.name)
        
        self.view_role_var.set(player.role)
        
        
    def day_phase_send(self, args=None):
        try:
            day = int(self.day_box.get())
            if day <= 0:
                day = self.game_state.day
        except ValueError as e:
            day = self.game_state.day
            
        phase = self.phase_box.get()
        if not phase in PHASES:
            phase = self.game_state.phase
            
        self.game_state.day = day
        self.game_state.phase = phase
        
        self.update_widgets()
        
    def player_view_send(self, args=None):
        player_id = self.view_id.cget("text")
        
        try:
            player = [p for p in self.game_state.players if p.id == player_id][0]
        except IndexError as e:
            self.update_widgets()
            return
        
        player.name = self.view_name.get()
        
        role = self.view_role_var.get()
        if not role in ALL_ROLES:
            role = player.role
        player.role = role
        
        self.update_widgets()
        
        
class testMState():
    def __init__(self):
        self.day = 1
        self.phase = "Day"
        self.players = []
        
    def __str__(self):
        m = str(self.day) + "\n"
        m += self.phase + "\n"
        for player in self.players:
            m += player.__str__()
        return m
        
class testPlayer():
    def __init__(self, id, name, role):
        self.id = id
        self.name = name
        self.role = role
    
    def __str__(self):
        return "{} - {}".format(self.id, self.name)
        
root = tk.Tk()
state = testMState()
state.players = [testPlayer("1","Alph", "COP"), testPlayer("2","Brit", "DOCTOR"), testPlayer("3","Charlie","MAFIA")]
board = MBoardgame_state(master=root, game_state=state)
board.mainloop()