import socket
from _thread import *
import pickle
from pieces import *
from massage import massage
import uuid
from board import Board
import sqlite3
from server_handling import *
import globals
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = socket.gethostbyname(socket.gethostname())
port = 5555
try:
    s.bind((ip,port))
except Exception as e:
    print(e)
s.listen(2)
print("Waiting for a connection, Server Started")

conn = sqlite3.connect("DATABASE.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT UNIQUE,
    password TEXT
)
""")


connected = globals.connected
pending_challenges = globals.pending_challenges
class game():
     def __init__(self,p1,p2):
          #p1 and p2 are a tuple ex:(opp_client,opp_name) 
          self.clients = [p1[0],p2[0]]
          self.turn = "white"
          self.board_class = Board()
          self.board =  self.board_class.board
          self.board_class.load_FEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
          self.player_2_color = {p1[0]:"white",p2[0]:"black"}
          self.player_names = [p1[1],p2[1]]
     def send_board(self):
          for c in self.clients:
              # c.send(pickle.dumps(massage("BOARD",self.board)))
               c.send(pickle.dumps(massage("GAME_STARTED",(self.board,self.player_2_color[c]))))
               c.send(pickle.dumps(massage("PLAYER_NAMES",self.player_names)))
     def send_info(self,msg):
        print(f"sending info to {self.player_names} with msg {msg.type}")
        for c in self.clients:
             c.send(pickle.dumps(msg))

     

def type_access(client):
     # the access data comes as the from n.send_only(massage(f"{action}",(username, password)))
     name = None
     while name == None:
         msg =pickle.loads(client.recv(2048))
         print(msg.type)
         if msg.type == "LOGIN":
             name= verify_user(client,msg.content)
         elif msg.type == "CREATE":
              name=crating_account(client,msg.content)

     handle_messages(client,name)
#THOSE ARE AUTH ENTICATION FUNCTIONS PUT THEM IN auth.py
def send_play_request(client,opponent,opp_name,sender):
     #this func makes a temp challenge in a dict and sends the id to the player so if he accepts/decline i can find it
     #TODO if somebody in game don't send them invite
     #FIXED A BUG where the ids where stored for the opp not the sender
     challenge_id = str(uuid.uuid4())[:5]
     print(challenge_id)
     pending_challenges[challenge_id] = {
          "opponent":{"client":opponent,"name":opp_name},
          "sender": {"client":client,"name":sender}
     }
     print(f"THE SENDER {sender}")
     connected[sender]["challenges_ids"].append(challenge_id)
     opponent.send(pickle.dumps(massage("GAME?",challenge_id,opp_name,sender)))
def accept_request(id):
     try:
          data =pending_challenges[id]
     except:
          return None
     opp_client = data["opponent"]["client"]
     opp_name = data["opponent"]["name"]
     challenger_client = data["sender"]["client"]
     challenger_name =  data["sender"]["name"]
     #this makes sure if somebody send a challenge but is now is already in a game to cancel the acceptance
     print(f" all ops challenges {connected[opp_name]["challenges_ids"]}")
     print(f" all sender challenges {connected[challenger_name]["challenges_ids"]}")
     if connected[opp_name]["state"] != "in game" and  connected[challenger_name]["state"] != "in game" :
          new_game = game((challenger_client,challenger_name),(opp_client,opp_name))

          connected[challenger_name]["state"] = "in game" 
          connected[opp_name]["state"] = "in game" 

          connected[challenger_name]["game"] = new_game
          connected[opp_name]["game"] = new_game

          print(f"{challenger_client} challenges {opp_client} to a chess game !!!!")
          del pending_challenges[id]
          new_game.send_board()
          return new_game
     else:
          if connected[opp_name]["challenges_ids"] !=[]:
               clear_pending_challenges(opp_name)
          if connected[challenger_name]["challenges_ids"] !=[]:
               clear_pending_challenges(challenger_name)
          return None
def verify_user(client,info):
     conn = sqlite3.connect("DATABASE.db")
     cursor = conn.cursor()
     name=info[0]
     password=info[1]
     cursor.execute("SELECT * FROM users WHERE username =?",(name,))
     db_name = cursor.fetchone()
     if  not db_name:
          client.send(pickle.dumps(massage("INVALID",None)))
          return None
     else:
        if db_name[1] == password:
           client.send(pickle.dumps(massage("ACCEPTED",None)))
           print(f"the user {name} has connected ")
           if name not in connected:
                connected[name] = {}
           connected[name]["client"] = client
           connected[name]["state"] = "lobby"
           connected[name]["game"] = None
           connected[name]["challenges_ids"] = []
           return name
        else:
              client.send(pickle.dumps(massage("INVALID",None)))
              return None
def crating_account(client,info):
    conn = sqlite3.connect("DATABASE.db")
    cursor = conn.cursor()
    crating = True
    name=info[0]
    password=info[1]
    cursor.execute(
            "SELECT 1 FROM users WHERE username = ?",
            (name,)
        )
    exists = cursor.fetchone()
    if not exists:
               client.send("ACC".encode())
               crating = False
               connected[name] = client
               cursor.execute("INSERT INTO users (username, password)VALUES (?, ?) ",(name,password))
               conn.commit()
               print(f"the NEW user {name} has connected ")
               
    else:
            client.send("TAKEN".encode())



# THOSE ARE THE MAIN FUNCTIONS THAT HANDLE THE GAME AND MENU STATES OF THE PLAYER PUT THEM IN handle_messages.py
      
def handle_messages(conn,name):
    try:
         while True:
                if connected[name]["state"] == "lobby":
                     print(f"the player {name} is in the lobby")
                     handle_menu(conn,name)
                elif connected[name]["state"] =="in game":
                     print(f"the player {name} is in a game")
                     handle_threaded_game(conn, connected[name]["game"])
    except Exception as err:
        cleanup_player(name)

    conn.close()
#THOSE HANDLE THE LOBBY LOGIC 
def clear_pending_challenges(name):
     ids = list(connected[name]["challenges_ids"]) 
     print(f"clearing pending challenges for {name} with ids {ids}")
     for id in ids:
          try:
               pending_challenges.pop(id, None)
               print("deletion complelete")
          except Exception as e:
              print(f"the name {name}, the id {id}, the ids {connected[name]['challenges_ids']}, the exp {e}")
     connected[name]["challenges_ids"].clear()
def cleanup_player(name):
          print(f"cleaning up {name}")
          if name not in connected:
               return
          player = connected[name]
          print(f"the player {name} is in state {player['state']}")
          if player["state"] == "lobby":
              clear_pending_challenges(name)
              del connected[name]
          elif player["state"] =="in game":
               clear_pending_challenges(name)
               game = player["game"]
               if player["client"] in game.clients:
                    game.clients.remove(player["client"])
               if name in game.player_names:
                    game.player_names.remove(name)
               del connected[name]
              
def handle_menu(conn,name):
     connected_p = list(connected.keys())
     connected_p.remove(name)
     print(connected_p)
     conn.send(pickle.dumps(massage("LIST OF PLAYER",connected_p)))
     data =pickle.loads(conn.recv(2048))
     print(data.type)
     if data.type =="GAME?":
        opp = connected[data.content]["client"]
        send_play_request(conn,opp,data.content,data.sender)
     elif data.type == "ACCEPTED_CHALLENGE":
        new_game= accept_request(data.content)
        print(f" GAMMMMMMMMMMMME{new_game}")

running = True
con_count = 0
new_game = None
try:
    while running:
        conn,addr = s.accept()
        print("Connected to:", addr)
        print(con_count)
        start_new_thread(type_access,(conn,))
except KeyboardInterrupt:
    running = False
    s.close()
