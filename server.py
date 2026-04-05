import socket
from _thread import *
import pickle
from pieces import *
from massage import massage
import uuid
from board import Board
import sqlite3
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


connected = {}
pending_challenges = {}
class game():
     def __init__(self,p1,p2):
          #p1 and p2 are a tuple ex:(opp_client,opp_name) 
          self.clients = [p1[0],p2[0]]
          self.turn = "white"
          self.board_class = Board()
          self.board =  self.board_class.board
          self.board_class.load_FEN("4k3/8/8/8/8/8/8/4KQ1q")
          self.player_2_color = {p1[0]:"white",p2[0]:"black"}
          self.player_names = [p1[1],p2[1]]
     def send_board(self):
          for c in self.clients:
              # c.send(pickle.dumps(massage("BOARD",self.board)))
               c.send(pickle.dumps(massage("GAME_STARTED",(self.board,self.player_2_color[c]))))
               c.send(pickle.dumps(massage("PLAYER_NAMES",self.player_names)))
     def send_info(self,msg):
        for c in self.clients:
             c.send(pickle.dumps(msg))
def Valid_moves_request(data,board):
        piece_pos = data.content
        piece = board[piece_pos[0]][piece_pos[1]]
        valid_moves,capture=piece.check_legal_moves(board,piece_pos)
        #returning the content as a tuple so i can update valid moves AND selected piece
        return (valid_moves,piece_pos)
def Make_move_request(data,game):
        print(game.turn)
     # the content is a tuple of 0:mouse_pos or the to_pos and the 1: the piece 
        piece_pos = data.content[1]
        mouse_pos = data.content[0]
        board = game.board
        piece = board[piece_pos[0]][piece_pos[1]]
        print(piece.color)
        if piece.color == game.turn:
          last_move = piece.make_move(board,piece_pos,mouse_pos)
          last_played_piece = piece
          if piece.color == "white":
               print("now is black's turn")
               game.turn = "black"

          else:
               print("the turns should turn")
               game.turn = "white"
               print(game.turn)
          return last_move,last_played_piece 
        else:
             return None,None
def Undo_move_request(last_move,last_played_piece,board):
        print("not here")
        last_played_piece.undo_move(board,last_move)
        return None,None
      
def send_play_request(client,opponent,opp_name,sender):
     #this func makes a temp challenge in a dict and sends the id to the player so if he accepts/decline i can find it
     challenge_id = str(uuid.uuid4())[:5]
     print(challenge_id)
     pending_challenges[challenge_id] = {
          "opponent":{"client":opponent,"name":opp_name},
          "sender": {"client":client,"name":sender}
     }
     print(f"THE SENDER {sender}")
     opponent.send(pickle.dumps(massage("GAME?",challenge_id,opp_name,sender)))
def accept_request(id):
     data =pending_challenges[id]
     opp_client = data["opponent"]["client"]
     opp_name = data["opponent"]["name"]

     challenger_client = data["sender"]["client"]
     challenger_name =  data["sender"]["name"]

     new_game = game((challenger_client,challenger_name),(opp_client,opp_name))

     connected[challenger_name]["state"] = "in game" 
     connected[opp_name]["state"] = "in game" 

     connected[challenger_name]["game"] = new_game
     connected[opp_name]["game"] = new_game

     print(f"{challenger_client} challenges {opp_client} to a chess game !!!!")
     del pending_challenges[id]
     new_game.send_board()
     return new_game

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
def handle_messages(conn,name):
    try:
         while True:
                if connected[name]["state"] == "lobby":
                     handle_menu(conn,name)
                elif connected[name]["state"] =="in game":
                     handle_threaded_game(conn, connected[name]["game"])
    except Exception as err:
         print(f"the handle msg error is {err}")

    conn.close()
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
       
                


def handle_threaded_game(conn,game):

    last_played_piece = None
    last_move = None
    try:
            data =pickle.loads(conn.recv(2048))
            print(data.type)
            if not data:
                print("Disconnected")
                
            else:
                try:
                   if data.type == "VALID_GET":
                         valid_moves = Valid_moves_request(data, game.board)
                         msg = massage("VALID_SEND",valid_moves)
                         print(msg.type)
                         conn.send(pickle.dumps(msg))
                        
                   elif data.type == "MAKE_MOVE":
                       
                       last_move,last_played_piece = Make_move_request(data,game)
                       if last_move == None or last_played_piece == None:
                            msg = massage("not your turn",None)
                       else:
                         msg = massage("MADE_MOVE",game.board)
                       game.send_info(msg)

                   elif data.type =="UNDO_MOVE":
                           if last_played_piece and last_move:
                                last_played_piece,last_move = Undo_move_request(last_move,last_played_piece,game.board)
                                msg = massage("UNDID_MOVE",game.board)
                                conn.send(pickle.dumps(msg))

                           else:
                                 msg = massage("nothing to undo",None)
                                 conn.send(pickle.dumps(msg))

                   elif data.type =="REFRESH":
                        conn.send(pickle.dumps(massage("CONNECTED PLAYERS",connected)))
                   else:
                         msg = massage("UNKNOWN MASSAGE",None)
                         conn.send(pickle.dumps(msg))
                except Exception as e:
                    msg = massage("UNKNOWN ERROR",None)
                    conn.send(pickle.dumps(msg))
                    print("the exp",e)
                #conn.send(pickle.dumps(board))
    except Exception as e:
            print(f"the exeption = {e}")
            print("Lost connection")
            for n in connected:
                 if connected[n] == conn:
                      print(n)
                      del connected[n]
            raise Exception

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
