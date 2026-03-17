import pygame
import socket
import pickle
from pieces import *
from massage import massage
from _thread import *
from input import AuthPage
# create the screen
WIDTH = 800
HIGHT = 1000
pygame.init()
screen = pygame.display.set_mode((WIDTH,HIGHT))
pygame.display.set_caption("clint")
#pygame settings
run = True
clock = pygame.time.Clock()
fps = 60
text_font = pygame.font.SysFont("Arial",30)
#game settings
square_size = 100
green_square_color = pygame.Color("#69923e")
white_square_color = pygame.Color("#eeeed2")
image_cache = {}
playable_pieces = []

def draw_text(text,font,color,x,y):
    surf_text = font.render(text,True,color)
    screen.blit(surf_text, (x,y))
class Button():
     def __init__(self,text,x,y,enabled = True):
          self.text = text
          self.x = x 
          self.y = y
          self.enabled = enabled
          self.rect = pygame.Rect(self.x,self.y,150,50)
          self.draw()
     def draw(self):
       if self.enabled:
        pygame.draw.rect(screen,"white",self.rect,0,5)
        draw_text(self.text, text_font,"green", (self.x + 15), (self.y + 10))
       else:
            pygame.draw.rect(screen,"gray",self.rect,0,5)
            draw_text(self.text, text_font,"black", (self.x + 15), (self.y + 10))
     def Check_clicked(self):
          mouse_pos = pygame.mouse.get_pos()
          left_click = pygame.mouse.get_pressed()[0]
          if left_click and self.rect.collidepoint(mouse_pos)and self.enabled:
               return True
          return False
class network():
    def __init__(self):
        self.clint = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server = socket.gethostbyname(socket.gethostname())
        self.port = 5555
        self.addr = (self.server,self.port)
        self.board =None
        self.color = None
        self.incoming_msg = []
        self.connect()
    def connect(self):
        try:
            self.clint.connect(self.addr)
            
        except:
            return None

    def send(self,data):
        try:
          self.clint.send(pickle.dumps(data))
          data = self.clint.recv(2048*7)
          return pickle.loads(data)
        except socket.error as e:
            print(e)
    def send_only(self,data):
        try:
          self.clint.send(pickle.dumps(data))
        except socket.error as e:
            print(e)
    def listen(self):
        while True:
             msg = self.clint.recv(2048*9)
             self.incoming_msg.append(pickle.loads(msg))
n = network()
def draw_board():
   for row in range(1,9):
        for Colum in range(8):
            if (row+Colum)%2 == 0:
                pygame.draw.rect(screen,green_square_color,(Colum*square_size,row*square_size,square_size,square_size))
            else:
                pygame.draw.rect(screen,white_square_color,(Colum*square_size,row*square_size,square_size,square_size))
            
def load_pieces(board):
     for row in (board):
        for  square in (row):
            if square != "":
               square.load_image(image_cache)
               if square.color == "white":
                   playable_pieces.append((square.x,square.y))
def draw_pieces(board):
    for row in (board):
        for  square in (row):
            if square != "":
               square.draw_piece(screen,image_cache)

def draw_valid_moves(valid_moves):
    for i in valid_moves:
        pygame.draw.circle(screen,"red",(i[0]*square_size+square_size//2,(i[1]+1)*square_size+square_size//2),15)
def handle_incoming_msgs(n):
    if n.incoming_msg:
        print(n.incoming_msg)
        msg = n.incoming_msg.pop()
        print(f"the massge {msg.type}")
        if msg.type == "BOARD":
             print(msg.content)

        if msg.type == "CONNECTED PLAYERS":
                print(msg.content)
        if msg.type =="ACCEPTED":
            print("CONNECTED")
board = n.board
#load_pieces(board)
valid_moves = []
undo = Button("undo_move",400,0)
selected_piece = None
class game_screen():
    def __init__(self,board):
        self.valid_moves = []
        self.selected_piece = None
        self.board = board
    def handle_game_click(self):
            if mouse_pos[0] in range(8) and mouse_pos[1] in range(8):
                print(mouse_pos)
                if mouse_pos in self.valid_moves:
                    msg = massage("MAKE_MOVE",(mouse_pos,self.selected_piece))
                    reply = n.send(msg)
                    if reply.type == "MADE_MOVE":
                        print("move should have been made")
                        self.board = reply.content
                        self.valid_moves = []
                        self.selected_piece = None
                elif self.board[mouse_pos[0]][ mouse_pos[1]] != "":
                    Piece =  self.board[mouse_pos[0]][ mouse_pos[1]]
                    if Piece.color == n.color:
                        msg = massage("VALID_GET",mouse_pos)
                        reply = n.send(msg)
                        if reply.type == "VALID_SEND":
                            print(reply.content)
                            self.valid_moves = reply.content
                            draw_valid_moves(reply.content)
                            self.selected_piece = mouse_pos
                else:
                    self.valid_moves = []
                    self.selected_piece = None
    def check_undo_button(self):
            if undo.Check_clicked():
                 print(self.selected_piece,self.valid_moves)
                 msg = massage("UNDO_MOVE",None)
                 reply = n.send(msg)
                 if reply.content:
                        self.board = reply.content
    def draw_board(self):
        for row in range(1,9):
            for Colum in range(8):
                if (row+Colum)%2 == 0:
                    pygame.draw.rect(screen,green_square_color,(Colum*square_size,row*square_size,square_size,square_size))
                else:
                    pygame.draw.rect(screen,white_square_color,(Colum*square_size,row*square_size,square_size,square_size))
    def draw(self):
        self.draw_board()
        draw_pieces(self.board)
        undo.draw()
        if self.valid_moves:
            draw_valid_moves(self.valid_moves)
class login():
    def __init__(self):
        self.test = Button("test",200,200)
        
game = game_screen(board)
game_started = False
menu_page = AuthPage(200,200)
start_new_thread(n.listen,())
action = "LOGIN"
while run:
    clock.tick(fps)
    screen.fill("black")
    handle_incoming_msgs(n)
    if game_started:
        game.draw()
    else:
        menu_page.draw(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        result = menu_page.handle_events(event)
        if result:
            action, username, password = result
            print(action, username, password)
            n.send_only(massage(f"{action}",(username, password)))
            print(action, username, password)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos_unfiltered = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos_unfiltered[0]//square_size,(mouse_pos_unfiltered[1]-100)//square_size)
            if game_started:
                game.check_undo_button()
                game.handle_game_click()

    pygame.display.flip()

pygame.quit()