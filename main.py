#basic library imports
import tkinter as tk
import tkinter.messagebox
from time import sleep
from random import choice, shuffle
from PIL import ImageTk, Image
import threading # সাউন্ড এবং স্পিচ-এর জন্য নতুন ইম্পোর্ট
import pyttsx3   # স্পিচ-এর জন্য নতুন ইম্পোর্ট
from playsound import playsound # সাউন্ড-এর জন্য নতুন ইম্পোর্ট

# এই ফাইলগুলোর নাম settings.py এবং board.py হতেই হবে
from settings import *
from board import *

# --- নতুন গ্লোবাল ভ্যারিয়েবলস ---
engine = pyttsx3.init() # স্পিচ ইঞ্জিন শুরু করা হলো
bot_difficulty_level = "Medium" # ডিফল্ট বট লেভেল
player_scores = [{"wins": 0, "kills": 0}, {"wins": 0, "kills": 0}, {"wins": 0, "kills": 0}, {"wins": 0, "kills": 0}] # স্কোরবোর্ডের জন্য (এখনও ব্যবহৃত হয়নি)

# --- নতুন ফাংশন: সাউন্ড এবং স্পিচ (থ্রেডিং সহ) ---
def play_sound(sound_file):
    """একটি আলাদা থ্রেডে সাউন্ড প্লে করে যাতে গেমটি আটকে না যায়"""
    try:
        threading.Thread(target=playsound, args=(sound_file,), daemon=True).start()
    except Exception as e:
        print(f"Error playing sound {sound_file}: {e}")

def speak_text(text):
    """একটি আলাদা থ্রেডে টেক্সট স্পিক করে যাতে গেমটি আটকে না যায়"""
    try:
        engine.say(text)
        threading.Thread(target=engine.runAndWait, daemon=True).start()
    except Exception as e:
        print(f"Error speaking text: {e}")


class Coin:

    def __init__(self, master, x, y, color, path_list, flag):
        self.canvas = master
        self.curr_x = x
        self.curr_y = y
        self.home_x = x
        self.home_y = y
        self.color = color
        self.curr_index = -1
        
        image_name = color
        if color == 'blue':
            image_name = 'blue2'  # আপনার ফাইলের নাম 'blue2.png'
        
        COIN_SIZE = (30, 30) # বোর্ডে ঘুঁটির সাইজ
        img_path = f'{image_name}.png'
        
        try:
            original_image = Image.open(img_path)
            resized_image = original_image.resize(COIN_SIZE, Image.LANCZOS)
            self.coin = ImageTk.PhotoImage(resized_image)
            self.img =  self.canvas.create_image(x, y, anchor=tk.NW, image=self.coin)
            self.canvas.tag_bind(self.img, '<1>', self.moveCoin)
        except Exception as e:
            print(f"Error loading/resizing image {img_path}: {e}")
            self.coin = None
            self.img = self.canvas.create_oval(x, y, x + COIN_SIZE[0], y + COIN_SIZE[1], fill=color, outline=color)
            self.canvas.tag_bind(self.img, '<1>', self.moveCoin)
        
        self.disable = True
        self.path_list = path_list
        self.flag = flag
        self.win = 0
        self.pad_x = 0
    
    def moveCoin(self, event=None):

        if self.disable:
            if event is None: return False 
            return 

        roll = Dice.roll
        if len(roll) == 0:
            if event is None: return False
            return

        if roll[-1] == 6 and event is not None: 
            tkinter.messagebox.showerror('Error', 'You got 6, Please Roll Again')
            return

        if len(roll) != 0 :
            n = len(self.path_list)
            max_moves = n - self.curr_index - 1
            if max_moves < roll[0]:
                if event is None: return False
                return
                
        check = (False, 0, 0)
        congrats = False 
        
        if self.is_at_home():
            if 6 in roll:
                check = self.can_attack(0)
                self.canvas.coords(self.img, self.path_list[0][0] + 4 + self.pad_x, self.path_list[0][1] + 4)
                self.curr_x = self.path_list[0][0]
                self.curr_y = self.path_list[0][1]
                self.curr_index = 0
                Dice.remove_by_index(6)
            else:
                if event is None: return False
                return 
                
        else:
            check = self.can_attack(self.curr_index + roll[0])
            for i in range(roll[0] - 1):
                self.curr_index += 1
                self.canvas.coords(self.img, self.path_list[self.curr_index][0] + 4, self.path_list[self.curr_index][1] + 4)
                self.curr_x = self.path_list[self.curr_index][0]
                self.curr_y = self.path_list[self.curr_index][1]
                self.canvas.update()
                sleep(0.05)

            self.curr_index += 1
            self.canvas.coords(self.img, self.path_list[self.curr_index][0] + 4 + self.pad_x, self.path_list[self.curr_index][1] + 4)
            self.curr_x = self.path_list[self.curr_index][0]
            self.curr_y = self.path_list[self.curr_index][1]
            if check[0]:
                colors[check[1]][check[2]].goto_home()

            self.canvas.update()
            sleep(0.05)
            Dice.remove()
           
            if self.curr_index == len(self.path_list) - 1: # ঘুঁটি জিতলে
                self.win = 1
                if event is not None: 
                    tkinter.messagebox.showinfo('INFO','!! Congratulations !!\nPlease Roll Dice Again')
                # play_sound('cheer.wav') # নতুন: উইন সাউন্ড (ফাইলটি নেই)
                congrats = True 

            if check[0]: # ঘুঁটি কাটলে
                if event is not None: 
                    tkinter.messagebox.showinfo('INFO','You killed another coin! ...')
                # play_sound('attack.wav') # নতুন: অ্যাটাক সাউন্ড (ফাইলটি নেই)
                congrats = True 

        if self.is_player_won():
            tkinter.messagebox.showinfo('INFO','{} Wins'.format(self.color.title()))
            position.append(self.player.title())
            Dice.roll = []
            Dice.set(self.flag)

        if self.is_gameover():
            root.quit()
        
        if event is not None: # যদি মানুষ খেলে
            if congrats:
                self.congratulations() 
            elif len(Dice.roll) == 0:
                self.next_turn()
        
        if event is None: # যদি বট খেলে
            return congrats 
            
    def congratulations(self):
        Dice.update_state()
        Dice.set(self.flag - 1)
        return True

    def change_state(self, flag):
        if flag == -1:
            self.disable = True
        elif flag == self.flag:
            self.disable = False 
        else:
            self.disable = True
    
    def is_at_home(self):
        return self.curr_x == self.home_x and self.curr_y == self.home_y

    def check_home(self):
        count = 0
        for goti in colors[self.flag]:
            if goti.is_at_home():
                count += 1
        return count

    def is_player_won(self):
        reached = 0
        for goti in colors[self.flag]:
            if goti.win:
                reached += 1
        return reached is 4
        
    def is_gameover(self):
        color_reached = 0
        for i in range(4):
            game = 0
            for color in colors[i]:
                if color.win:
                    game += 1
            if game is 4:
                color_reached += 1

        if color_reached is 3:
            tkinter.messagebox.showinfo('Game Over', '\n\n1. {}\n\n2. {}\n\n3. {}'.format(*position))
        else:
            return False
        return True

    def can_attack(self, idx):
        if idx >= len(self.path_list):
            return (False, 0, 0)
            
        max_pad = 0
        count_a = 0
        x = self.path_list[idx][0]
        y = self.path_list[idx][1]
        for i in range(4):
            for j in range(4):
                if colors[i][j].curr_x == x and colors[i][j].curr_y == y:
                        if colors[i][j].pad_x > max_pad:
                            max_pad = colors[i][j].pad_x
                        count_a += 1

        if not self.path_list[idx][2]:
            for i in range(4):
                count = 0
                jdx = 0
                for j in range(4):
                    if (colors[i][j].curr_x == x and colors[i][j].curr_y == y 
                        and colors[i][j].color != self.color):
                        count += 1
                        jdx = j
                        
                if count is not 0 and count is not 2:
                    self.pad_x = max_pad + 4
                    return (True, i, jdx)

        if count_a is not 0:
            self.pad_x = max_pad + 4
        else:
            self.pad_x = 0
        return (False, 0, 0)

    def goto_home(self):
        self.canvas.coords(self.img, self.home_x, self.home_y)
        self.curr_x = self.home_x
        self.curr_y = self.home_y
        self.curr_index = -1
        
    def next_turn(self):
        if len(Dice.roll) == 0:
            Dice.set(self.flag)

    def set_playername(self, player):
        self.player = player


class Dice:

    chance = 0
    roll = []
    append_state = False
    current_turn_label = None 

    @classmethod
    def rolling(cls):
        temp = choice(range(1, 9))
        if temp > 6:
            temp = 6

        play_sound('Dice.wav')
        speak_text(str(temp))

        if len(cls.roll) == 0 or cls.roll[-1] == 6 or cls.append_state:
            cls.roll.append(temp)
            cls.append_state = False
        
        dice_image_name = {
            1: 'de1.png', 2: 'de2.png', 3: 'de3.png',
            4: 'de4.png', 5: 'de5.png', 6: 'de6.png',
        }.get(cls.roll[-1], 'trans.png')

        try:
            img = ImageTk.PhotoImage(Image.open(dice_image_name))
            image_label = tk.Label(ludo.get_frame(), width=100, height=100, image=img, bg=Color.CYAN)
            image_label.image = img
            image_label.place(x=250, y=300)
        except Exception as e:
            print(f"Error loading dice image {dice_image_name}: {e}")
            if not is_bot[Dice.chance]: 
                tkinter.messagebox.showerror('Image Error', f'Could not load image: {dice_image_name}\nMake sure de1.png to de6.png exist.')

        roll_label = tk.Label(ludo.get_frame(), text='{}'.format(' | '.join([str(x) for x in cls.roll])),
                                 font=(None, 20), width=30, height=3, borderwidth=3, relief=tk.RAISED)
        roll_label.place(x=100, y=200)

    @classmethod
    def start(cls):
        Dice.rolling()
        if cls.roll.count(6) >= 3:
            if len(cls.roll) >= 3 and [cls.roll[-1], cls.roll[-2], cls.roll[-3]] == [6, 6, 6]:
                for i in range(3):
                   Dice.remove_by_index(6)
            if cls.roll == []:
                Dice.update_panel()
                return
        Dice.check_move_possibility()

    @classmethod
    def update_panel(cls):
        root.update()
        sleep(0.5)
        Dice.set(cls.chance)
        cls.roll = []

    # --- START: NEW GLOW LOGIC (আপডেটেড) ---
    @classmethod
    def set(cls, flag):
        flag += 1
        cls.chance = flag
        if flag == 4:
            cls.chance = flag = 0
        
        if cls.chance < len(colors) and colors[cls.chance] and colors[cls.chance][0].is_player_won():
            Dice.set(cls.chance) 
            return 

        # ১. পুরনো লেবেলকে স্বাভাবিক করা
        if cls.current_turn_label:
            try:
                # ডানদিকের প্যানেলের ডিফল্ট রঙ (Color.CYAN) ব্যবহার করা হলো
                cls.current_turn_label.config(relief=tk.SUNKEN, bg=Color.CYAN, fg='black')
            except tk.TclError:
                pass 

        # --- নতুন: প্লেয়ারের রঙ অনুযায়ী গ্লো ---
        player_colors = [Color.GREEN, Color.RED, Color.BLUE, Color.YELLOW]
        current_color = player_colors[flag] # flag = cls.chance

        # ৩. লেখার রঙ সেট করা (হলুদ ছাড়া বাকিগুলোয় সাদা লেখা)
        text_color = 'white'
        if current_color == Color.YELLOW:
            text_color = 'black'
            
        glow_style = {'relief': tk.RAISED, 'bg': current_color, 'fg': text_color}
        # --- শেষ: নতুন গ্লো ---


        if is_bot[cls.chance]:
            player_name_short = turn[flag].split(' ')[0] 
            
            next_label = tk.Label(ludo.get_frame(), text=f'{player_name_short} turn (Bot)', font=(None, 20), width=30, height=3,
                            borderwidth=3, **glow_style)
            next_label.place(x=100, y=100)
            
            button.config(state=tk.DISABLED)
            for i in range(4):
                for j in range(4):
                    colors[i][j].change_state(-1) 
            
            root.after(1000, run_bot_turn) 
            
        else:
            button.config(state=tk.NORMAL) 
            for i in range(4):
                for j in range(4):
                    colors[i][j].change_state(flag) 
            
            next_label = tk.Label(ludo.get_frame(), text='{} turn'.format(turn[flag]), font=(None, 20), width=30, height=3,
                            borderwidth=3, **glow_style)
            next_label.place(x=100, y=100)

        cls.current_turn_label = next_label
        # --- END: NEW GLOW LOGIC ---

        roll_label = tk.Label(ludo.get_frame(), text='ROLL PLEASE', font=(None, 20), width=30, height=3, borderwidth=3, relief=tk.RAISED)
        roll_label.place(x=100, y=200)

        try:
            img = ImageTk.PhotoImage(Image.open('trans.png'))
            image_label = tk.Label(ludo.get_frame(), width=100, height=100, image=img, bg=Color.CYAN)
            image_label.image = img
            image_label.place(x=250, y=300)
        except Exception as e:
            print(f"Error loading trans.png: {e}")
            if not is_bot[Dice.chance]:
                tkinter.messagebox.showerror('Image Error', 'Could not load image: trans.png\nMake sure trans.png exists.')

    @classmethod
    def remove(cls):
        if cls.roll:
            cls.roll.pop(0)

    @classmethod
    def remove_by_index(cls, ex):
        if ex in cls.roll:
            del cls.roll[cls.roll.index(ex)]

    @classmethod
    def update_state(cls):
        cls.append_state = True

    @classmethod
    def check_move_possibility(cls):
        if is_bot[cls.chance]:
            return 

        if not cls.roll:
            Dice.update_panel()
            return

        check_1 = 0 
        check_2 = 0 
        
        total_coins = 0
        if cls.chance < len(colors):
             total_coins = len(colors[cls.chance])
        else:
            Dice.update_panel() 
            return

        for goti in colors[cls.chance]:
            if goti.is_at_home():
                check_1 += 1
            else:
                max_moves = len(goti.path_list) - goti.curr_index - 1
                if max_moves < cls.roll[0]:
                    check_2 += 1

        if 6 not in cls.roll:
            if check_1 == total_coins:
                Dice.update_panel()
            elif check_1 == 0 and check_2 == total_coins:
                 Dice.update_panel()
            elif check_1 + check_2 == total_coins:
                 Dice.update_panel()
        else:
            if check_1 > 0 and (check_1 + check_2 == total_coins):
                 pass 
            elif check_1 == 0 and check_2 == total_coins:
                 Dice.update_panel()


def align(x, y, color, path_list, flag):
    container = []
    for i in range(2):
        test = Coin(ludo.get_canvas(), x, y + i*2*Board.SQUARE_SIZE, color=color, path_list=path_list, flag=flag)
        container.append(test)
    for i in range(2):
        test = Coin(ludo.get_canvas(), x + 2*Board.SQUARE_SIZE, y + i*2*Board.SQUARE_SIZE, color=color, path_list=path_list, flag=flag)
        container.append(test)
    return container

# --- START: NEW GLOW LOGIC (startgame) ---
def startgame():
    global is_bot, bot_difficulty_level
    
    bot_difficulty_level = difficulty_var.get()
    print(f"Bot Difficulty set to: {bot_difficulty_level}")

    for i in range(4):
        player_name = players[i].get()
        if player_name:
            turn[i] = player_name
            is_bot[i] = False 
        else:
            turn[i] = f'{turn[i]} (Bot)' 
            is_bot[i] = True 
            
    for i in range(4):
        for j in range(4):
            colors[i][j].set_playername(turn[i])

    # --- নতুন: গ্লো স্টাইল (সবুজ দিয়ে শুরু) ---
    glow_style = {'relief': tk.RAISED, 'bg': Color.GREEN, 'fg': 'white'}
    start_label = tk.Label(ludo.get_frame(), text='! START ! Let\'s Begin with {}'.format(turn[0]), font=(None, 20),
                         width=30, height=3, borderwidth=3, **glow_style)
    start_label.place(x=100, y=100)
    
    Dice.current_turn_label = start_label
    # --- END: NEW GLOW LOGIC ---
    
    top.destroy()
    
    if is_bot[0]:
        button.config(state=tk.DISABLED) 
        for i in range(4):
            for j in range(4):
                colors[i][j].change_state(-1) 
        root.after(1000, run_bot_turn) 
# --- END: NEW GLOW LOGIC (startgame) ---


def create_enterpage():
    top.config(bg='#333333') 
    enter_label = tk.Label(top, text='Enter Your Nickname! (Leave blank for Bot)', font=(None, 20), width=30, height=3,
                            borderwidth=3, relief=tk.RAISED, bg='#444444', fg='white')
    enter_label.place(x=20, y=20)
    
    global difficulty_var
    difficulty_label = tk.Label(top, text='Bot Difficulty:', font=(None, 16), bg='#333333', fg='white')
    difficulty_label.place(x=150, y=430)
    
    difficulty_var = tk.StringVar(top)
    difficulty_options = ["Easy", "Medium", "Hard"]
    difficulty_var.set("Medium") 
    
    difficulty_menu = tk.OptionMenu(top, difficulty_var, *difficulty_options)
    difficulty_menu.config(width=10, bg='#555555', fg='white', activebackground='#666666', activeforeground='white')
    difficulty_menu["menu"].config(bg='#555555', fg='white')
    difficulty_menu.place(x=300, y=430)

    enter_button = tk.Button(top, text='Enter', command=startgame, width=15, height=2,
                             bg='#555555', fg='white', activebackground='#666666', activeforeground='white')
    enter_button.place(x=230, y=500)

    entry_style = {
        'width': 15, 'bg': 'white', 'fg': 'black', 'relief': tk.SUNKEN, 
        'borderwidth': 2, 'insertbackground': 'black', 'selectbackground': '#0078D7',
        'selectforeground': 'white', 'highlightthickness': 1, 
        'highlightbackground': '#888888', 'highlightcolor': '#0078D7'
    }
    
    for i in range(2):
        temp = tk.Entry(top, **entry_style)
        temp.place(x=87, y=220 + i*180)
        players.append(temp)
    for i in range(2):
        temp = tk.Entry(top, **entry_style)
        temp.place(x=387, y=400 - i*180)
        players.append(temp)

    global greenimg, redimg, blueimg, yellowimg
    
    try:
        NICKNAME_COIN_SIZE = (40, 40) 
        WINDOW_BG = '#333333' 
        green_orig = Image.open('green.png')
        greenimg = ImageTk.PhotoImage(green_orig.resize(NICKNAME_COIN_SIZE, Image.LANCZOS))
        green_label = tk.Label(top, image=greenimg, bg=WINDOW_BG) 
        green_label.place(x=107, y=130)
        red_orig = Image.open('red.png')
        redimg = ImageTk.PhotoImage(red_orig.resize(NICKNAME_COIN_SIZE, Image.LANCZOS))
        red_label = tk.Label(top, image=redimg, bg=WINDOW_BG)
        red_label.place(x=107, y=310)
        blue_orig = Image.open('blue2.png')
        blueimg = ImageTk.PhotoImage(blue_orig.resize(NICKNAME_COIN_SIZE, Image.LANCZOS))
        blue_label = tk.Label(top, image=blueimg, bg=WINDOW_BG)
        blue_label.place(x=407, y=310)
        yellow_orig = Image.open('yellow.png')
        yellowimg = ImageTk.PhotoImage(yellow_orig.resize(NICKNAME_COIN_SIZE, Image.LANCZOS))
        yellow_label = tk.Label(top, image=yellowimg, bg=WINDOW_BG)
        yellow_label.place(x=407, y=130)
    except Exception as e:
        print(f"Error loading player images in nickname window: {e}")
        tkinter.messagebox.showerror('Image Error', f'Could not load player images (green.png, red.png, etc.)')

def on_closing():
    if tkinter.messagebox.askokcancel("Quit", "Do you want to quit the game? If you want to continue the game, press Enter in the Nickname window"):
        try:
            top.destroy()
        except tk.TclError: pass 
        try:
            root.destroy()
        except tk.TclError: pass 

def on_closingroot():
    if tkinter.messagebox.askokcancel("Quit", "Do you want to quit the game?"):
        try:
            root.destroy()
        except tk.TclError: pass 

# --- START: BOT FUNCTIONS (আপডেটেড) ---

def make_bot_move(coin):
    """বটের পক্ষ থেকে ঘুঁটি চালনা করার একটি হেল্পার ফাংশন"""
    if not root.winfo_exists(): return False

    roll_to_be_used = 0
    if coin.is_at_home():
        if 6 in Dice.roll:
            roll_to_be_used = 6
        else:
            print("Bot Error: Tried to move coin from home without a 6.")
            Dice.update_panel()
            return False
    else:
        if len(Dice.roll) > 0:
            roll_to_be_used = Dice.roll[0]
        else:
            print("Bot Error: Tried to move coin but no rolls left.")
            Dice.update_panel()
            return False
            
    coin.disable = False
    got_bonus_turn = coin.moveCoin(None) # বট চাল দিলো (True/False)
    coin.disable = True
    
    if got_bonus_turn:
        print(f"Bot {turn[Dice.chance]} got a bonus turn (kill/win).")
        Dice.update_state()
        Dice.set(Dice.chance - 1) 
    
    elif roll_to_be_used == 6:
        print(f"Bot {turn[Dice.chance]} used a 6, rolling again.")
        Dice.update_state() 
        Dice.set(Dice.chance - 1) 
        
    elif len(Dice.roll) > 0:
        print(f"Bot {turn[Dice.chance]} has more moves: {Dice.roll}")
        root.after(1000, decide_bot_move) 
    
    else:
        print(f"Bot {turn[Dice.chance]}'s turn is over.")
        Dice.update_panel() 
    
    return True


def run_bot_turn():
    """বটের চাল শুরু করে (ডাইস রোল)"""
    if not root.winfo_exists(): return
    print(f"Bot {turn[Dice.chance]} is rolling...")
    Dice.start() # ডাইস রোল করা হলো
    
    root.after(1500, decide_bot_move) 

def decide_bot_move():
    """বটের 'AI' - কোন ঘুঁটি চালবে তা ঠিক করে"""
    if not root.winfo_exists(): return
    
    bot_flag = Dice.chance
    bot_coins = colors[bot_flag]
    current_rolls = Dice.roll.copy()

    if not current_rolls:
        print(f"Bot {turn[bot_flag]} has no rolls left.")
        if not Dice.roll: 
            Dice.update_panel()
        return

    print(f"Bot {turn[bot_flag]} (Level: {bot_difficulty_level}) deciding move with rolls: {current_rolls}")

    if bot_difficulty_level == "Easy":
        easy_bot_logic(bot_flag, bot_coins, current_rolls)
    elif bot_difficulty_level == "Medium":
        medium_bot_logic(bot_flag, bot_coins, current_rolls)
    else: # Hard
        hard_bot_logic(bot_flag, bot_coins, current_rolls)

def get_possible_moves(bot_flag, bot_coins, roll_value, has_6):
    """বটের জন্য সব ধরনের চালের একটি তালিকা তৈরি করে"""
    moves = {
        "winning": [], "attack": [], "safe": [],
        "regular": [], "get_out": [], "vulnerable": []
    }
    
    if has_6:
        for coin in bot_coins:
            if coin.is_at_home():
                start_x, start_y, _ = coin.path_list[0]
                block_count = 0
                for p_idx in range(4):
                    for o_coin in colors[p_idx]:
                        if o_coin.curr_x == start_x and o_coin.curr_y == start_y:
                            block_count += 1
                if block_count < 2: 
                    moves["get_out"].append(coin)
                    break 
        
    for coin in bot_coins:
        if coin.is_at_home(): continue 

        target_index = coin.curr_index + roll_value
        if target_index >= len(coin.path_list): continue 

        target_x, target_y, is_safe_square = coin.path_list[target_index]

        if target_index == len(coin.path_list) - 1:
            moves["winning"].append(coin)
            continue 

        if is_safe_square:
            moves["safe"].append(coin)
            continue 

        is_attack = False
        for p_idx in range(4):
            if p_idx == bot_flag: continue 
            for o_coin in colors[p_idx]:
                if o_coin.curr_x == target_x and o_coin.curr_y == target_y and not o_coin.is_at_home():
                    is_attack = True 
                    break
            if is_attack: break
        
        if is_attack:
            moves["attack"].append(coin)
            continue
        
        is_vulnerable = False
        # (এখানে আরও উন্নত 'vulnerable' লজিক যোগ করা যেতে পারে)
        
        if is_vulnerable:
            moves["vulnerable"].append(coin)
        else:
            moves["regular"].append(coin)

    return moves

def easy_bot_logic(bot_flag, bot_coins, current_rolls):
    """Easy AI: র‍্যান্ডমভাবে যেকোনো একটি বৈধ চাল দেয়"""
    roll_value = current_rolls[0]
    has_6 = 6 in current_rolls
    
    possible_moves = []
    if has_6:
        for coin in bot_coins:
            if coin.is_at_home():
                possible_moves.append(coin)
    
    for coin in bot_coins:
        if not coin.is_at_home():
            target_index = coin.curr_index + roll_value
            if target_index < len(coin.path_list):
                possible_moves.append(coin)

    if possible_moves:
        shuffle(possible_moves) # চালগুলোকে এলোমেলো করা
        print(f"Bot strategy (Easy): Making a random move.")
        if make_bot_move(possible_moves[0]): return
    
    print(f"Bot (Easy) could not find a valid move for roll {roll_value}.")
    if Dice.roll: 
         Dice.update_panel()

def medium_bot_logic(bot_flag, bot_coins, current_rolls):
    """Medium AI: Win > Attack > Get Out > Safe > Regular"""
    roll_value = current_rolls[0]
    has_6 = 6 in current_rolls
    moves = get_possible_moves(bot_flag, bot_coins, roll_value, has_6)
    
    if moves["winning"]:
        print(f"Bot strategy (Medium): Winning a coin.")
        if make_bot_move(moves["winning"][0]): return 
    if moves["attack"]:
        print(f"Bot strategy (Medium): Attacking opponent.")
        if make_bot_move(moves["attack"][0]): return 
    if moves["get_out"]:
        print(f"Bot strategy (Medium): Getting coin out of home.")
        if make_bot_move(moves["get_out"][0]): return
    if moves["safe"]:
        print(f"Bot strategy (Medium): Landing on a safe square.")
        if make_bot_move(moves["safe"][0]): return
    if moves["regular"]:
        print(f"Bot strategy (Medium): Making a regular move.")
        if make_bot_move(moves["regular"][0]): return
    
    print(f"Bot (Medium) could not find a valid move for roll {roll_value}.")
    if Dice.roll: 
         Dice.update_panel()

def hard_bot_logic(bot_flag, bot_coins, current_rolls):
    """Hard AI: Medium AI + অতিরিক্ত সতর্কতা (Vulnerable চাল এড়িয়ে চলা)"""
    roll_value = current_rolls[0]
    has_6 = 6 in current_rolls
    moves = get_possible_moves(bot_flag, bot_coins, roll_value, has_6)
    
    if moves["winning"]:
        print(f"Bot strategy (Hard): Winning a coin.")
        if make_bot_move(moves["winning"][0]): return 
    if moves["attack"]:
        print(f"Bot strategy (Hard): Attacking opponent.")
        if make_bot_move(moves["attack"][0]): return 
    if moves["get_out"]:
        print(f"Bot strategy (Hard): Getting coin out of home.")
        if make_bot_move(moves["get_out"][0]): return
    if moves["safe"]:
        print(f"Bot strategy (Hard): Landing on a safe square.")
        if make_bot_move(moves["safe"][0]): return
    
    if moves["regular"]: # প্রথমে ভালো 'regular' চাল খোঁজা
        print(f"Bot strategy (Hard): Making a regular (non-vulnerable) move.")
        if make_bot_move(moves["regular"][0]): return
    elif moves["vulnerable"]: # যদি কোনো ভালো চাল না থাকে, তবেই 'vulnerable' চাল দেওয়া
        print(f"Bot strategy (Hard): Making a vulnerable move (no other choice).")
        if make_bot_move(moves["vulnerable"][0]): return
    
    print(f"Bot (Hard) could not find a valid move for roll {roll_value}.")
    if Dice.roll: 
         Dice.update_panel()

# --- END: NEW BOT FUNCTIONS ---


# --- গ্লোবাল ভ্যারিয়েবলস ---
players = []
is_bot = [False, False, False, False] 
difficulty_var = None 

root = tk.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry('{}x{}'.format(width, height))
root.title('Ludo')

ludo = LudoBoard(root)
ludo.create()

turn = ['Green', 'Red', 'Blue', 'Yellow'] 
position = []
colors = []

try:
    colors.append(align(2.1*Board.SQUARE_SIZE, 2.1*Board.SQUARE_SIZE, color='green', path_list=path.green_path, flag=0))
    colors.append(align(2.1*Board.SQUARE_SIZE, 11.1*Board.SQUARE_SIZE, color='red', path_list=path.red_path, flag=1))
    colors.append(align(11.1*Board.SQUARE_SIZE, 11.1*Board.SQUARE_SIZE, color='blue', path_list=path.blue_path, flag=2))
    colors.append(align(11.1*Board.SQUARE_SIZE, 2.1*Board.SQUARE_SIZE, color='yellow', path_list=path.yellow_path, flag=3))
except AttributeError as e:
    tkinter.messagebox.showerror('Settings Error', "Error in settings.py file. 'path' object seems broken.")
    root.destroy()
except Exception as e:
    tkinter.messagebox.showerror('Fatal Error', f'An unexpected error occurred: {e}')
    root.destroy()

if not root.winfo_exists():
    exit()

colors[0][0].change_state(0) 
for i in range(4):
    for j in range(4):
        colors[i][j].change_state(0)

button = tk.Button(ludo.get_frame(), text='ROLL', command=Dice.start, width=20, height=2)
button.place(x=210, y=470)

welcome_msg = ''' Welcome Champs let's get into the game of LUDO :-) \n
        Rules of the game:
- The players roll a six-sided die in turns and can advance any of their coins on the track by the number of steps as displayed by the dice.\n
- Once you get a six in a dice throw, you to roll the dice again, and must use all scores while making the final selection of what coins to move where.\n
- If you get a six three times in a row, your throws are reset and you will lose that chance.\n
- The coin can advance in the home run only if it reaches exactly inside the home pocket, or moves closer to it through the home run. 
For example, if the coin is four squares away from the home pocket and the player rolls a five, he must apply the throw to some other coin. \
However, if you roll a two, you can advance the coin by two squares and then it rests there until the next move.\n 
    
    Enjoy the game and have fun.
        # Best of luck #
'''
tkinter.messagebox.showinfo('Welcome', welcome_msg)

top = tk.Toplevel(root)
top.geometry('600x600')
top.title('Nickname')
top.protocol("WM_DELETE_WINDOW", on_closing)
root.protocol("WM_DELETE_WINDOW", on_closingroot)
create_enterpage()
root.mainloop()