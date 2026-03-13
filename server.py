import socket
from _thread import *
import pickle
from pieces import *
from massage import massage


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = socket.gethostbyname(socket.gethostname())
port = 5555
connected = []
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
        last_move = piece.check_legal_moves(board,piece_pos,mouse_pos)
        last_played_piece = piece
        return last_move,last_played_piece
def Undo_move_request(last_move,last_played_piece,board):
      if  not last_move:
         msg = massage("nothing to undo",None)
         conn.send(pickle.dumps(msg))
      else:
        print("not here")
        last_played_piece.undo_move(board,last_move)
        return None,None
def threaded_clint(conn,):
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
                           
                           last_played_piece,last_move = Undo_move_request(last_move,last_played_piece,board)
                           msg = massage("UNDID_MOVE",board)
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
try:
    while running:
        conn,addr = s.accept()
        connected.append((conn,addr))
        print("Connected to:", addr)
        start_new_thread(threaded_clint,(conn,))
except KeyboardInterrupt:
    running = False
    s.close()
