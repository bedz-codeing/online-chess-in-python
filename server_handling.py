import socket
from _thread import *
import pickle
from pieces import *
from massage import massage
from board import Board
import globals

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
    
def handle_move_request(data,game):
          last_move,last_played_piece = Make_move_request(data,game)
          if last_move == None or last_played_piece == None:
               msg = massage("not your turn",None)
          else:
            msg = massage("MADE_MOVE",game.board)

          return last_move,last_played_piece,msg

def check_for_checks(game,last_played_piece,color):
      #this code is for checkmate/check detection after a move is made
      opp_color = "white" if color == "black" else "black"
      opp_king_poss = last_played_piece.white_king_pos if color == "black" else last_played_piece.black_king_pos
      #this func check if this square is attacked by the piece that is not your color thats why i putted white
      opp_is_checked = is_square_attacked(game.board,opp_king_poss,opp_color)
      print(f"the {color} king is checked {opp_is_checked}")
      if opp_is_checked:
           game.send_info(massage(f"CHECK ON THE {color.upper()} KING ",opp_is_checked))
           return True
      return False

def detect_game_end(game,color):
       opp_color = "white" if color == "black" else "black"
       is_checked = detect_checkmate(game.board,opp_color)
       if is_checked:
         return True
       return False

def ending_game(game):
     game.send_info(massage("GAME_ENDED",None))
    
     for name in game.player_names:
          print(f"returning {name} to lobby")
          return_to_lobby(name)


def return_to_lobby(name):
    """
    Transition a player back to the lobby state after a game ends.
    handle_messages will loop and call handle_menu, which sends LIST OF PLAYER
    automatically — so we don't need to send it here.
    """
    globals.connected[name]["state"] = "lobby"
    print(f"returning {name} to lobby")
    globals.connected[name]["game"] = None
    globals.connected[name]["challenges_ids"] = []
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
                        last_move,last_played_piece,msg = handle_move_request(data,game)
                        # this code is for checkmate/check detection after a move is made
                        game.send_info(msg)
                        if check_for_checks(game,last_played_piece,last_played_piece.color):
                             print("the king is checked")
                             if detect_game_end(game,last_played_piece.color):
                                   ending_game(game)

                   elif data.type =="UNDO_MOVE":
                           if last_played_piece and last_move:
                                last_played_piece,last_move = Undo_move_request(last_move,last_played_piece,game.board)
                                msg = massage("UNDID_MOVE",game.board)
                                conn.send(pickle.dumps(msg))
                           else:
                                 msg = massage("nothing to undo",None)
                                 conn.send(pickle.dumps(msg))

                   elif data.type =="GAME_ENDED":
            # Client acknowledged the game end. return_to_lobby was already called
            # by whichever player's thread ran ending_game, so state is already
            # "lobby". We just need to return so handle_messages can loop to
            # handle_menu and send a fresh LIST OF PLAYER.
                         print("client acknowledged GAME_ENDED — returning to lobby loop")
                         ending_game(game)
                         return
                   else:
                         msg = massage("UNKNOWN MASSAGE",None)
                         conn.send(pickle.dumps(msg))
                except Exception as ex:
                    msg = massage("UNKNOWN ERROR",None)
                    conn.send(pickle.dumps(msg))
                    print("the exp",ex)
                #conn.send(pickle.dumps(board))
    except Exception as e:
            print(f"the exeption = {e}")
            print("Lost connection")
            raise Exception
    