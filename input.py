import pygame


def draw_text(screen, font, text, color, x, y):
    screen.blit(font.render(text, True, color), (x, y))


class Button:
    def __init__(self, text, x, y, w=150, h=50, enabled=True):
        self.text    = text
        self.x, self.y = x, y
        self.enabled = enabled
        self.rect    = pygame.Rect(x, y, w, h)

    def draw(self, screen, font):
        color      = "white" if self.enabled else "gray"
        text_color = "green" if self.enabled else "black"
        pygame.draw.rect(screen, color, self.rect, 0, 5)
        draw_text(screen, font, self.text, text_color, self.x + 15, self.y + 12)

    def is_clicked(self):
        return (pygame.mouse.get_pressed()[0]
                and self.rect.collidepoint(pygame.mouse.get_pos())
                and self.enabled)


class InputBox:
    def __init__(self, x, y, w, h, placeholder="", hidden=False):
        self.rect        = pygame.Rect(x, y, w, h)
        self.text        = ""
        self.placeholder = placeholder
        self.hidden      = hidden
        self.active      = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def draw(self, screen, font):
        border_color = "white" if self.active else pygame.Color("#888888")
        pygame.draw.rect(screen, pygame.Color("#1a1a2e"), self.rect, 0, 6)
        pygame.draw.rect(screen, border_color, self.rect, 2, 6)
        if self.text:
            display = "*" * len(self.text) if self.hidden else self.text
            surf = font.render(display, True, "white")
        else:
            surf = font.render(self.placeholder, True, pygame.Color("#555577"))
        screen.blit(surf, (self.rect.x + 12, self.rect.y + 10))


class AuthPage:
    """
    Draw this page and call handle_events() each frame.
    Returns ("login", username, password) or ("register", username, password) on submit.
    Returns None otherwise.
    """
    def __init__(self, x, y):
        self.font     = pygame.font.SysFont("consolas", 18)
        self.username = InputBox(x, y,      220, 40, "Username")
        self.password = InputBox(x, y + 60, 220, 40, "Password", hidden=True)
        self.login_btn    = Button("Login",    x,       y + 120, w=105, h=40)
        self.register_btn = Button("Register", x + 115, y + 120, w=105, h=40)
        self._guard = False

    def handle_events(self, event):
        self.username.handle_event(event)
        self.password.handle_event(event)

        if not pygame.mouse.get_pressed()[0]:
            self._guard = False

        if not self._guard:
            if self.login_btn.is_clicked():
                self._guard = True
                return ("LOGIN", self.username.text, self.password.text)
            if self.register_btn.is_clicked():
                self._guard = True
                return ("CREATE", self.username.text, self.password.text)
        return None

    def draw(self, screen):
        self.username.draw(screen, self.font)
        self.password.draw(screen, self.font)
        self.login_btn.draw(screen, self.font)
        self.register_btn.draw(screen, self.font)

class challenge_box():
    def __init__(self,screen,x,y,connected_player,challenged = False):
        #connected_players =(name,clint_conn)
        #if you press the button it sends the server the name so it gets the client and send a challenge
        self.x = x
        self.y = y
        self.name = connected_player
        self.screen = screen
        self.challenged = challenged
        self.font= pygame.font.SysFont("consolas", 24)
        self.game_id = None
        if not challenged:
            self.challenge_button = Button("challenge",self.x+300,self.y-19)
        else:
            self.challenge_button = Button("accept",self.x+300,self.y-19)
    def draw_challenge_box(self):
        draw_text(self.screen,self.font,f"{self.name}","white",self.x,self.y)
        self.challenge_button.draw(self.screen,self.font)