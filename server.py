import socket
from _thread import *
import pickle
from pieces import *
from massage import massage
import uuid
import random
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
board = []
for i in range(8):
    row = []
    for j in range(8):
        row.append("")
    board.append(row)

conn = sqlite3.connect("DATABASE.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT UNIQUE,
    password TEXT
)
""")


class game():
    def __init__(self):
        self.players = []
    def add_member(self,player):
          self.players.append(player)
    def send_board(self,msg):
        for conn in self.players:
             conn.send(pickle.dumps(msg))
board[2][3] = queen("white",2,3,"chess pieces/white_qween.png")
board[2][2] = king("white",2,2,"chess pieces/white_king.png")

board[3][2] = queen("black",3,2,"chess pieces/black_queen.png")

board[2][5] = queen("black",2,5,"chess pieces/black_queen.png")
board[3][5] = king("black",3,5,"chess pieces/black_king.png")


connected = []
pending_challenges = {}
class game():
     def __init__(self,p1,p2):
          #this class is makes it possible to send board to more than 1 player
          # it takes the player as (connection and addr) FOR NOW TODO change it
          self.clients = [p1[0],p2[0]]
          self.board =  []
          for i in range(8):
              row = []
              for j in range(8):
                  row.append("")
              board.append(row)
     def send_board(self,board):
          for c in self.clients:
               c.send(pickle.dumps(massage("BOARD",board)))
         
def Valid_moves_request(data,board):
        piece_pos = data.content
        piece = board[piece_pos[0]][piece_pos[1]]
        valid_moves,capture=piece.check_legal_moves(board,piece_pos)
        return valid_moves
def Make_move_request(data,board):
     # the content is a tuple of 0:mouse_pos or the to_pos and the 1: the piece 
        piece_pos = data.content[1]
        mouse_pos = data.content[0]
        piece = board[piece_pos[0]][piece_pos[1]]
        last_move = piece.make_move(board,piece_pos,mouse_pos)
        last_played_piece = piece
        return last_move,last_played_piece
def Undo_move_request(last_move,last_played_piece,board):
        print("not here")
        last_played_piece.undo_move(board,last_move)
        return None,None
      
def send_play_request(client,opponent):
     #this func makes a temp challenge in a dict and sends the id to the player so if he accepts/decline i can find it
     challenge_id = str(uuid.uuid4())[:5]
     print(challenge_id)
     pending_challenges[challenge_id] = {
          "opponent":opponent,
          "sender": client
     }
     opponent.pickle.dumps(massage("GAME?",challenge_id))
def accept_request(id):
     data =pending_challenges[id]
     opp = data["opponent"]
     challenger = ["sender"]
     #new_game = game(challenger,opp)

    # del pending_challenges[id]
def type_access(client):
     # the access data comes as the from n.send_only(massage(f"{action}",(username, password)))
     logging = True
     while logging:
         msg =pickle.loads(client.recv(2048))
         print(msg.type)
         if msg.type == "LOGIN":
             logging= verify_user(client,msg.content)
         elif msg.type == "CREATE":
              logging=crating_account(client,msg.content)

def verify_user(client,info):
     conn = sqlite3.connect("DATABASE.db")
     cursor = conn.cursor()
     verifying = True
     name=info[0]
     password=info[1]
     cursor.execute("SELECT * FROM users WHERE username =?",(name,))
     db_name = cursor.fetchone()
     if  not db_name:
          client.send(pickle.dumps(massage("INVALID",None)))
          return True
     else:
        if db_name[1] == password:
           client.send(pickle.dumps(massage("ACCEPTED",None)))
           print(f"the user {name} has connected ")
           verifying = False
           connected[name] = client
           handle_threaded_game(client)
           return False
        else:
              client.send(pickle.dumps(massage("INVALID",None)))
              return True
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
def handle_threaded_game(conn,new_game):
    conn.send(pickle.dumps(board))
    conn.send(pickle.dumps("white"))
    last_played_piece = None
    last_move = None
    while True:
        try:
            data =pickle.loads(conn.recv(2048))
            print(data.type)
            if not data:
                print("Disconnected")
                break
            else:
                try:
                   if data.type == "VALID_GET":
                        
                         valid_moves = Valid_moves_request(data,board)
                         msg = massage("VALID_SEND",valid_moves)
                         conn.send(pickle.dumps(msg))
                         
                   elif data.type == "MAKE_MOVE":
                       
                       last_move,last_played_piece = Make_move_request(data,board)
                       msg = massage("MADE_MOVE",board)
                       conn.send(pickle.dumps(msg))

                   elif data.type =="UNDO_MOVE":
                           if last_played_piece and last_move:
                                last_played_piece,last_move = Undo_move_request(last_move,last_played_piece,board)
                                msg = massage("UNDID_MOVE",board)
                                conn.send(pickle.dumps(msg))

                           else:
                                 msg = massage("nothing to undo",None)
                                 conn.send(pickle.dumps(msg))
                   elif data.type =="GAME?":
                        rands = ["test test ttttttest",1234,3333,"ITS THE MAN HIM SELF BADRRRRRRRRR","NOTHING BUT A BUETFAL MOON"]
                        new_game.send_board(random.choice(rands))

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
            break
    print("Lost connection")
    conn.close()
running = True
con_count = 0
new_game = None
try:
    while running:
        conn,addr = s.accept()
        connected.append((conn,addr))
        print("Connected to:", addr)
        con_count +=1
        if con_count == 2:
             new_game = game(connected[0],connected[1])

        print(con_count)
        start_new_thread(type_access,(conn,))
except KeyboardInterrupt:
    running = False
    s.close()
