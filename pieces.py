import pygame
square_size = 100
class piece():
     white_king_pos = None
     black_king_pos = None
     def __init__(self,color,x,y,directory,name,move_directions = []):
          self.color = color
          self.x = x
          self.y = y
          self.possiton = (x,y)
          self.move_directions = move_directions
          self.name = name
          self.directory = directory
     def load_image(self,image_cache):
          self.piece = pygame.image.load(f"{self.directory}").convert_alpha()
          self.piece = pygame.transform.smoothscale(self.piece,(square_size, square_size)) 
          image_cache[self.directory] = self.piece
     def draw_piece(self,screen,image_cache):
          piece = image_cache[self.directory]
          screen.blit(piece,(self.x*square_size,(self.y+1)*square_size))
          #return self.piece
     def get_position(self):
          return (self.x,self.y)
     def get_king_pos(self):
          return piece.black_king_pos if self.color == "black" else piece.white_king_pos
          
     def check_valid(self,piece_list):
          self.valid_moves = []
          self.capture = []
          for i in self.move_directions:
               for square in range(1,8):
                    nx = self.x + i[0]*square
                    ny = self.y + i[1]*square
                    if nx<0 or nx>7 or ny<0 or ny>7:
                         break
                    if piece_list[nx][ny] != "":
                        checked = piece_list[nx][ny].color
                        if checked != self.color:
                           self.capture.append((nx,ny))
                           self.valid_moves.append((nx,ny))
                           break
                        elif checked == self.color:
                            break
                    else:
                            self.valid_moves.append((nx,ny ))
          return self.valid_moves,self.capture
     def check_legal_moves(self,piece_list,current_pos):
          valid_moves = self.check_valid(piece_list)[0]
          capture_moves= self.check_valid(piece_list)[1]
          temp_valid_moves = valid_moves.copy()
          for move in temp_valid_moves:
               illegal_move = False
               undo_data = self.make_move(piece_list,current_pos,move)
               for row in piece_list:
                    if illegal_move:
                         break
                    for square in row:
                         if square != "" :
                              temp_piece = square
                              if temp_piece.color != self.color:
                                   attacking_square = temp_piece.check_valid(piece_list)[0]
                                   kings_pos = self.get_king_pos()
                                   print("the white king ",kings_pos)
                                   if kings_pos in attacking_square:
                                             valid_moves.remove(move)
                                             illegal_move = True
                                             break
               self.undo_move(piece_list,undo_data)
          
          return valid_moves,capture_moves
     def make_move(self,board,form_pos,to_pos):
            selected_piece = board[form_pos[0]][form_pos[1]]
            captured =  board[to_pos[0]][to_pos[1]]
            prev_state = {"from_pos":form_pos,
                  "to_pos": to_pos,
                  "piece":selected_piece,
                  "captured":captured,
                  "white_king_pos" : piece.white_king_pos,
                  "black_king_pos" : piece.black_king_pos}
            if self.name == "king":
                 if self.color =="white":
                      piece.white_king_pos = to_pos
                 else:
                     piece.black_king_pos = to_pos
            # change the X Y data of the piece
            selected_piece.x = to_pos[0]
            selected_piece.y = to_pos[1]
            board[to_pos[0]][to_pos[1]] = selected_piece
            board[form_pos[0]][form_pos[1]] =""
            return prev_state
     def undo_move(self,board,prev_state):
          undo_square = prev_state["captured"]
          to_pos = prev_state["to_pos"]
          form_pos = prev_state["from_pos"]
          moved_piece = prev_state["piece"]
          moved_piece.x = form_pos[0]
          moved_piece.y = form_pos[1]
          piece.black_king_pos = prev_state["black_king_pos"]
          piece.white_king_pos = prev_state["white_king_pos"]
          board[to_pos[0]][to_pos[1]] = undo_square
          board[form_pos[0]][form_pos[1]] =moved_piece
class pawn(piece):
     def __init__(self,color,x,y,directory):
          self.first_move_done = False
          self.color = color
          move_directions = [(0,-1),(1,-1),(-1,-1)] if self.color == "white" else [(0,1),(1,1),(-1,1)]
          super().__init__(color,x,y,directory,"pawn",move_directions)

class queen(piece):
     def __init__(self,color,x,y,directory):
          move_directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
          super().__init__(color,x,y,directory,"queen",move_directions)
     
class king(piece):
     def __init__(self,color,x,y,directory):
          self.check = False
          self.moved = False
          self.move_directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
          if color == "white":
               piece.white_king_pos  = (x,y)
          else:
               piece.black_king_pos  = (x,y)
          super().__init__(color,x,y,directory,"king",self.move_directions)
     def check_valid(self,piece_list):
               self.valid_moves = []
               self.capture = []
               for i in self.move_directions:
                    for square in range(1,2):
                         nx = self.x + i[0]*square
                         ny = self.y + i[1]*square
                         if nx<0 or nx>7 or ny<0 or ny>7:
                              break
                         if piece_list[nx][ny] != "":
                             checked = piece_list[nx][ny].color
                             if checked != self.color:
                                self.capture.append((nx,ny))
                                self.valid_moves.append((nx,ny))
                                break
                             elif checked == self.color:
                                 break
                         else:
                                 self.valid_moves.append((nx,ny ))
               return self.valid_moves,self.capture