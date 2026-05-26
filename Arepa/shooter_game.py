from pygame import *
from random import *

ANCHO, ALTO = 500, 800
FPS = 60
WHITE, RED, GREEN, CYAN, GRAY, YELLOW, PURPLE = (255,255,255), (255,0,0), (0,255,0), (0,255,255), (100,100,100), (255,255,0), (200,0,255)

PLAYER_IMG, ENEMY_IMG, BULLET_IMG, ASTEROID_IMG, BACKGROUND_IMG = "rocket.png", "ufo.png", "bullet.png", "asteroid.png", "galaxy.jpg"

init()
font.init()

PACTOS_INFO = {
    1: {"nombre": "Bala Gigante", "desc": "Balas perforantes / 1 Vida"},
    2: {"nombre": "Lluvia de Láser", "desc": "Disparo ultra rápido / Mov. Lento"},
    3: {"nombre": "Doble o Nada", "desc": "Puntos x3 / Meta 150 / Velocidad Extrema"},
    4: {"nombre": "Escudo de Cristal", "desc": "10 Vidas / Nave Gigante"},
    5: {"nombre": "Imán de Chatarra", "desc": "Asteroides ++Puntos / Lluvia de Rocas"},
    6: {"nombre": "Carga Fantasma", "desc": "Súper Veloz / 30% Evasión / Disparo Lento"}
}

class GameSprite(sprite.Sprite):
    def __init__(self, sprite_img, x, y, w, h, speed):
        super().__init__()
        try: 
            self.image = image.load(sprite_img).convert_alpha()
            self.image = transform.scale(self.image, (w, h))
        except: 
            self.image = Surface((w, h)); self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y, self.speed = x, y, speed
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > ALTO:
            self.rect.y = -50
            self.rect.x = randint(0, ANCHO - self.rect.width)

    def reset(self, surface): 
        surface.blit(self.image, (self.rect.x, self.rect.y))

class PlayerBullet(GameSprite):
    def __init__(self, sprite_img, x, y, w, h, speed, pierce):
        super().__init__(sprite_img, x, y, w, h, speed)
        self.pierce = pierce
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= -50: self.kill()

class EnemyBullet(sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = Surface((4, 12)); self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.top, self.speed = x, y, speed
    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= ALTO + 20: self.kill()

class Player(GameSprite):
    def __init__(self, *args):
        super().__init__(*args)
        self.cooldown = 0
        self.invul_timer = 0

    def update(self, vow):
        keys = key.get_pressed()
        speed_mult = 0.7 if vow == 2 else (2.2 if vow == 6 else 1.0)
        current_speed = self.speed * speed_mult
        if keys[K_a] and self.rect.x > 0: self.rect.x -= current_speed
        if keys[K_d] and self.rect.x < ANCHO - self.rect.width: self.rect.x += current_speed
        if keys[K_w]: self.fire(vow)
        
        if self.cooldown > 0: self.cooldown -= 1
        
        if self.invul_timer > 0:
            self.invul_timer -= 1
            self.image.set_alpha(115)
            if self.invul_timer <= 0:
                self.image.set_alpha(255)

    def fire(self, vow):
        if vow == 1: f_rate, b_speed, b_size = 28, 8, (40, 50) 
        elif vow == 2: f_rate, b_speed, b_size = 5, 15, (8, 18)
        elif vow == 6: f_rate, b_speed, b_size = 35, 16, (12, 22)
        else: f_rate, b_speed, b_size = 15, 12, (10, 20)
        if self.cooldown <= 0:
            balas.add(PlayerBullet(BULLET_IMG, self.rect.centerx - b_size[0]//2, self.rect.top, b_size[0], b_size[1], b_speed, (vow==1)))
            self.cooldown = f_rate

class Enemy(GameSprite):
    def update(self, vow):
        global fallos
        drop_speed = self.speed * 2.5 if vow == 3 else self.speed
        self.rect.y += drop_speed
        if randint(1, 150) == 1: self.fire()
        if self.rect.y >= ALTO:
            self.rect.y, self.rect.x, fallos = -self.rect.height, randint(0, ANCHO - 45), fallos + 1
    def fire(self): enemy_bullets.add(EnemyBullet(self.rect.centerx, self.rect.bottom, 6))

window = display.set_mode((ANCHO, ALTO))
clock = time.Clock()
background = Surface((ANCHO, ALTO)); background.fill((5, 5, 20))

font_ui = font.Font(None, 28); font_msg = font.Font(None, 50); font_sub = font.Font(None, 20)
balas, enemy_bullets, aliens, asteroids = sprite.Group(), sprite.Group(), sprite.Group(), sprite.Group()
player = Player(PLAYER_IMG, ANCHO//2 - 25, ALTO - 70, 50, 50, 8)

def reset_data(vow_choice):
    global vidas, puntos, fallos, finish, active_vow, vow_text, meta_puntos
    active_vow = vow_choice
    meta_puntos = 150 if active_vow == 3 else 80
    vow_text = f"PACTO: {PACTOS_INFO[active_vow]['nombre']}"
    vidas = 1 if active_vow == 1 else (10 if active_vow == 4 else 5)
    
    img_w, img_h = (90, 90) if active_vow == 4 else (50, 50)
    player.image = transform.scale(image.load(PLAYER_IMG).convert_alpha(), (img_w, img_h))
    player.rect = player.image.get_rect(x=ANCHO//2-25, y=ALTO - (110 if active_vow == 4 else 70))
    player.invul_timer = 0
    player.image.set_alpha(255)

    puntos, fallos, finish = 0, 0, False
    aliens.empty(); asteroids.empty(); balas.empty(); enemy_bullets.empty()
    
    for i in range(10 if active_vow == 3 else 6):
        aliens.add(Enemy(ENEMY_IMG, randint(0, ANCHO-45), randint(-500, -50), 45, 35, uniform(1.8, 3.0)))
    for i in range(7 if active_vow == 5 else 3):
        ast = GameSprite(ASTEROID_IMG, randint(0, ANCHO-40), randint(-600, -100), 40, 40, uniform(1.5, 2.5))
        ast.hp = 3 if active_vow == 5 else 2
        asteroids.add(ast)

game_state, options, run = "MENU", [], True

while run:
    window.blit(background, (0, 0))
    for e in event.get():
        if e.type == QUIT: run = False
        if e.type == KEYDOWN:
            if game_state == "MENU" and e.key == K_RETURN:
                options = sample(list(PACTOS_INFO.keys()), 3)
                game_state = "SELECT"
            elif game_state == "SELECT":
                if e.key == K_1: reset_data(options[0]); game_state = "PLAYING"
                if e.key == K_2: reset_data(options[1]); game_state = "PLAYING"
                if e.key == K_3: reset_data(options[2]); game_state = "PLAYING"
            elif game_state == "PLAYING" and finish and e.key == K_r: game_state = "MENU"

    if game_state == "MENU":
        t1 = font_msg.render("ACE INVADERS", True, CYAN)
        t3 = font_sub.render("ENTER para ver opciones de Pacto", True, GREEN)
        window.blit(t1, (ANCHO//2 - t1.get_width()//2, 250))
        window.blit(t3, (ANCHO//2 - t3.get_width()//2, 310))

    elif game_state == "SELECT":
        t1 = font_msg.render("ELIGE TU DESTINO", True, YELLOW)
        window.blit(t1, (ANCHO//2 - t1.get_width()//2, 80))
        for i, v_id in enumerate(options):
            color = GREEN if i == 0 else (CYAN if i == 1 else PURPLE)
            txt_n = font_ui.render(f"{i+1}. {PACTOS_INFO[v_id]['nombre']}", True, color)
            txt_d = font_sub.render(f"   {PACTOS_INFO[v_id]['desc']}", True, WHITE)
            window.blit(txt_n, (40, 200 + i*110))
            window.blit(txt_d, (40, 230 + i*110))

    elif game_state == "PLAYING":
        if not finish:
            player.update(active_vow)
            aliens.update(active_vow); asteroids.update(); balas.update(); enemy_bullets.update()

            for b in balas:
                if active_vow == 1: sprite.spritecollide(b, enemy_bullets, True)
                for a in sprite.spritecollide(b, aliens, True):
                    puntos += 3 if active_vow == 3 else 1
                    aliens.add(Enemy(ENEMY_IMG, randint(0, ANCHO-45), -50, 45, 35, uniform(2.0, 3.5)))
                    if not b.pierce: b.kill(); break
                for ast in sprite.spritecollide(b, asteroids, False):
                    ast.hp -= 2 if active_vow == 1 else 1
                    if ast.hp <= 0:
                        puntos += 12 if active_vow == 5 else (6 if active_vow == 3 else 2)
                        ast.rect.y, ast.rect.x, ast.hp = -50, randint(0, ANCHO-40), (3 if active_vow == 5 else 2)
                    if not b.pierce: b.kill(); break

            col_enemies = sprite.spritecollide(player, aliens, True)
            col_bullets = sprite.spritecollide(player, enemy_bullets, True)
            col_ast = sprite.spritecollide(player, asteroids, True)
            
            if col_enemies or col_bullets or col_ast:
                if player.invul_timer <= 0:
                    if not (active_vow == 6 and randint(1, 100) <= 30):
                        vidas -= 1
                        player.invul_timer = 108 
                
                if col_enemies: aliens.add(Enemy(ENEMY_IMG, randint(0, ANCHO-45), -50, 45, 35, uniform(2.0, 3.5)))
                if col_ast: 
                    new_ast = GameSprite(ASTEROID_IMG, randint(0, ANCHO-40), -50, 40, 40, uniform(1.5, 2.5))
                    new_ast.hp = 3 if active_vow == 5 else 2
                    asteroids.add(new_ast)

        player.reset(window); aliens.draw(window); asteroids.draw(window); balas.draw(window); enemy_bullets.draw(window)
        window.blit(font_sub.render(vow_text, True, YELLOW), (ANCHO//2 - 90, 10))
        window.blit(font_ui.render(f"Vidas: {vidas}", True, RED if vidas <= 1 else GREEN), (10, 40))
        window.blit(font_ui.render(f"Puntos: {puntos}/{meta_puntos}", True, WHITE), (10, 65))
        window.blit(font_ui.render(f"Fallos: {fallos}/10", True, RED if fallos > 7 else WHITE), (10, 90))

        if vidas <= 0 or fallos >= 10:
            finish = True
            msg = font_msg.render("¡DERROTA!", True, RED)
            window.blit(msg, (ANCHO//2 - msg.get_width()//2, ALTO//2 - 20))
        elif puntos >= meta_puntos:
            finish = True
            msg = font_msg.render("¡VICTORIA!", True, GREEN)
            window.blit(msg, (ANCHO//2 - msg.get_width()//2, ALTO//2 - 20))

    display.update()
    clock.tick(FPS)
quit()