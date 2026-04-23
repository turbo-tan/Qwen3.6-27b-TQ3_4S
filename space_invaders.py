#!/usr/bin/env python3
"""Space Invaders Ultimate Edition - A complete Pygame arcade game."""

import pygame
import random
import math

# ── Constants ────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 800, 700
FPS = 60
BG_COLOR = (0, 0, 0)

COLORS = {
    'cyan': (0, 255, 255),
    'green': (0, 255, 0),
    'red': (255, 0, 0),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'yellow': (255, 255, 0),
    'white': (255, 255, 255),
    'dark_red': (150, 0, 0),
    'gray': (100, 100, 100),
}

class Star:
    """A single star in the parallax background."""
    def __init__(self):
        self.reset(True)
    def reset(self, init=False):
        self.x = random.randint(0, SCREEN_W - 1)
        self.y = random.randint(0, SCREEN_H - 1) if init else -2
        self.speed = random.uniform(0.2, 1.5)
        self.brightness = random.uniform(50, 200)
        self.size = random.choice((1, 1, 2))
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_H:
            self.reset()

class StarField:
    def __init__(self):
        self.stars = [Star() for _ in range(50)]
    def update(self):
        for s in self.stars:
            s.update()
    def draw(self, screen):
        for s in self.stars:
            c = min(255, int(s.brightness))
            color = (c, c, c)
            pygame.draw.circle(screen, color, (int(s.x), int(s.y)), s.size)

class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, life=30, size=2, gravity=0):
        self.x, self.y = x, y
        self.color = color
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.size = size
        self.gravity = gravity
    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
    def draw(self, screen):
        alpha = self.life / self.max_life
        size = max(1, int(self.size * alpha))
        if size > 0:
            pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), size, size))
    def alive(self):
        return self.life > 0

class FloatingText:
    def __init__(self, x, y, text, color=COLORS['yellow'], size=18):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, size)
        self.life = 60
    def update(self):
        self.y -= 0.8
        self.life -= 1
    def draw(self, screen):
        alpha = min(1, self.life / 20)
        surf = self.font.render(self.text, True, self.color)
        alpha_surf = surf.get_alpha()
        if alpha_surf:
            surf.set_alpha(int(255 * alpha))
        screen.blit(surf, (self.x, self.y))
    def alive(self):
        return self.life > 0

class PlayerBullet:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = -8
        self.width, self.height = 4, 12
        self.alive = True
    def update(self):
        self.y += self.speed
        if self.y < -20:
            self.alive = False
    def draw(self, screen):
        pygame.draw.rect(screen, COLORS['white'], (self.x, self.y, self.width, self.height))
        glow = pygame.Rect(self.x - 1, self.y, self.width + 2, self.height)
        pygame.draw.rect(screen, (200, 200, 255), glow, 1, 1)
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class EnemyBullet:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 4
        self.width, self.height = 4, 10
        self.alive = True
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_H + 20:
            self.alive = False
    def draw(self, screen):
        pygame.draw.rect(screen, COLORS['red'], (self.x, self.y, self.width, self.height))
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Bomb:
    """Enemy bomb that destroys nearby player bullets and deals double damage."""
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 2.5
        self.radius = 8
        self.alive = True
        self.angle = 0
        self.particles = []
    def update(self, particles_list):
        self.y += self.speed
        self.angle += 0.2
        if self.y > SCREEN_H + 20:
            self.alive = False
        if random.random() < 0.4:
            px = self.x + random.uniform(-4, 4)
            py = self.y + random.uniform(-4, 4)
            vx = random.uniform(-1, 1)
            vy = random.uniform(-1.5, 0.5)
            particles_list.append(Particle(px, py, COLORS['red'], vx, vy, 15, 2))
    def draw(self, screen):
        for a in range(0, 360, 30):
            ax = self.x + math.cos(a * math.pi / 180 + self.angle) * 5
            ay = self.y + math.sin(a * math.pi / 180 + self.angle) * 5
            pygame.draw.circle(screen, COLORS['red'], (int(ax), int(ay)), 2)
        pygame.draw.circle(screen, (255, 100, 100), (int(self.x), int(self.y)), self.radius)
    def get_rect(self):
        r = self.radius + 2
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

class Enemy:
    TYPES = {
        'basic': {'hp': 1, 'pts': 100, 'speed': 0.3, 'color': COLORS['green'], 'shoot_rate': 0.002},
        'fast': {'hp': 1, 'pts': 150, 'speed': 0.8, 'color': COLORS['orange'], 'shoot_rate': 0.003},
        'tank': {'hp': 3, 'pts': 300, 'speed': 0.2, 'color': COLORS['purple'], 'shoot_rate': 0.001},
        'shooter': {'hp': 2, 'pts': 250, 'speed': 0.3, 'color': COLORS['red'], 'shoot_rate': 0.008},
    }

    def __init__(self, etype, x, y):
        info = self.TYPES[etype]
        self.type = etype
        self.hp = info['hp']
        self.max_hp = info['hp']
        self.pts = info['pts']
        self.base_speed = info['speed']
        self.color = info['color']
        self.shoot_rate = info['shoot_rate']
        self.x, self.y = x, y
        self.width, self.height = 30, 24
        self.alive = True
        self.pulse = 0
    def update(self, dx, dy):
        self.x += dx
        self.y += dy
        self.pulse += 0.05
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        if self.type == 'basic':
            self._draw_basic(screen, x, y)
        elif self.type == 'fast':
            self._draw_fast(screen, x, y)
        elif self.type == 'tank':
            self._draw_tank(screen, x, y)
        elif self.type == 'shooter':
            self._draw_shooter(screen, x, y)
    def _draw_basic(self, screen, x, y):
        pygame.draw.ellipse(screen, self.color, (x, y, 30, 20))
        pygame.draw.circle(screen, (255, 255, 255), (x + 8, y + 6), 4)
        pygame.draw.circle(screen, (255, 255, 255), (x + 22, y + 6), 4)
        pygame.draw.circle(screen, (0, 0, 0), (x + 9, y + 6), 2)
        pygame.draw.circle(screen, (0, 0, 0), (x + 23, y + 6), 2)
        pygame.draw.line(screen, self.color, (x + 10, y + 14), (x + 20, y + 14), 2)
        for cx in [2, 28]:
            pygame.draw.circle(screen, self.color, (x + cx, y + 18), 2)
    def _draw_fast(self, screen, x, y):
        pts = [(x + 30, y + 12), (x, y), (x + 5, y + 12), (x, y + 24), (x + 30, y + 12)]
        pygame.draw.polygon(screen, self.color, pts)
        for sy in range(3):
            pygame.draw.line(screen, (255, 200, 0), (x - 5 - sy * 4, y + 8 + sy * 4),
                            (x - 10 - sy * 4, y + 8 + sy * 4), 1)
    def _draw_tank(self, screen, x, y):
        pygame.draw.rect(screen, (60, 0, 60), (x, y, 34, 22), 2)
        pygame.draw.rect(screen, self.color, (x + 2, y + 2, 30, 18), 1)
        pygame.draw.rect(screen, (255, 255, 100), (x + 12, y + 4, 6, 6))
        pygame.draw.rect(screen, (200, 200, 200), (x + 28, y + 8, 8, 4))
        if self.max_hp > 1:
            bar_w = 30
            fill = max(0, bar_w * self.hp // self.max_hp)
            pygame.draw.rect(screen, (50, 0, 0), (x + 2, y - 6, bar_w, 3))
            pygame.draw.rect(screen, COLORS['green'], (x + 2, y - 6, fill, 3))
    def _draw_shooter(self, screen, x, y):
        pulse = 8 + int(3 * math.sin(self.pulse))
        pygame.draw.ellipse(screen, self.color, (x - 2, y, 34, 10))
        pygame.draw.ellipse(screen, (180, 0, 0), (x, y + 6, 30, 14))
        for sx in [x, x + 28]:
            pygame.draw.circle(screen, (255, 100, 100), (sx, y + 8), 3)
        pygame.draw.circle(screen, (255, 200, 200), (x + 15, y + 8), 3)
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class EnemyFormation:
    """Grid of enemies that move horizontally and descend."""
    def __init__(self, wave, on_kill_callback):
        self.wave = wave
        self.enemies = []
        self.spacing_x = 50
        self.spacing_y = 36
        self.dx = 0.6
        self.dy = 0
        self.direction = 1
        self.on_kill = on_kill_callback
        self._build(wave)
    def _build(self, wave):
        rows = min(3 + wave // 2, 6)
        cols = min(6 + wave // 2, 10)
        pool = ['basic']
        if wave >= 1:
            pool.append('shooter')
        if wave >= 2:
            pool.append('fast')
        if wave >= 3:
            pool.append('tank')
        if wave >= 4:
            pool.append('shooter')
        start_x = (SCREEN_W - (cols * self.spacing_x)) // 2 + 10
        for r in range(rows):
            for c in range(cols):
                etype = random.choice(pool)
                ex = start_x + c * self.spacing_x
                ey = 60 + r * self.spacing_y
                enemy = Enemy(etype, ex, ey)
                self.enemies.append(enemy)
    def update(self):
        any_edge = False
        for e in self.enemies:
            e.update(self.dx, self.dy)
            if e.x <= 5:
                any_edge = True
                self.direction = 1
                break
            if e.x + e.width >= SCREEN_W - 5:
                any_edge = True
                self.direction = -1
                break
        if any_edge:
            self.dy = 12
            self.dx = 0.6 * self.direction
            for e in self.enemies:
                e.y += 12
            self.dy = 0
    def draw(self, screen):
        for e in self.enemies:
            e.draw(screen)
    def kill(self, target, particles, floating_texts):
        if target.alive:
            target.alive = False
            for _ in range(15):
                vx = random.uniform(-3, 3)
                vy = random.uniform(-4, -1)
                particles.append(Particle(target.x + 15, target.y + 12, target.color, vx, vy, 25, 2, 0.05))
            floating_texts.append(FloatingText(target.x, target.y, str(target.pts)))
            self.on_kill(target)
            self.enemies.remove(target)
    def all_dead(self):
        return len(self.enemies) == 0

class PowerUp:
    TYPES = {
        'rapid': {'symbol': 'R', 'color': COLORS['green'], 'name': 'RAPID FIRE', 'dur': 600},
        'triple': {'symbol': 'T', 'color': COLORS['cyan'], 'name': 'TRIPLE SHOT', 'dur': 600},
        'shield': {'symbol': 'S', 'color': COLORS['purple'], 'name': 'SHIELD', 'dur': 600},
        'bomb': {'symbol': 'B', 'color': COLORS['red'], 'name': 'BOMB', 'dur': 0},
        'life': {'symbol': 'L', 'color': COLORS['yellow'], 'name': 'LIFE', 'dur': 0},
    }
    def __init__(self, x, y, ptype):
        info = self.TYPES[ptype]
        self.ptype = ptype
        self.symbol = info['symbol']
        self.color = info['color']
        self.name = info['name']
        self.dur = info['dur']
        self.x, self.y = x, y
        self.width, self.height = 20, 20
        self.alive = True
        self.life = 400
        self.pulse = 0
    def update(self):
        self.y += 0.8
        self.pulse += 0.1
        self.life -= 1
        if self.life <= 0 or self.y > SCREEN_H:
            self.alive = False
    def draw(self, screen):
        size = self.width + int(4 * math.sin(self.pulse))
        font = pygame.font.Font(None, 18)
        surf = font.render(self.symbol, True, self.color)
        screen.blit(surf, (self.x, self.y))
        pygame.draw.circle(screen, self.color, (int(self.x + 8), int(self.y + 6)), size // 2, 1)
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Player:
    def __init__(self):
        self.x = SCREEN_W // 2 - 15
        self.y = SCREEN_H - 80
        self.width, self.height = 36, 28
        self.speed = 5
        self.max_health = 5
        self.health = self.max_health
        self.lives = 3
        self.cooldown = 0
        self.cooldown_max = 12
        self.alive = True
        self.pulse = 0
        self.has_rapid = False
        self.has_triple = False
        self.has_shield = False
    def update(self, keys, particles):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
        self.x += dx
        self.y += dy
        self.x = max(0, min(self.x, SCREEN_W - self.width))
        self.y = max(SCREEN_H * 0.35, min(self.y, SCREEN_H - 40))
        self.pulse += 0.2
        if self.cooldown > 0:
            self.cooldown -= 1
        flame_color = COLORS['green'] if self.has_rapid else COLORS['cyan']
        if random.random() < 0.6:
            fx = self.x + self.width // 2 + random.uniform(-4, 4)
            fy = self.y + self.height + random.uniform(0, 6)
            particles.append(Particle(fx, fy, flame_color, 0, random.uniform(0.3, 1), 10, 1))
    def shoot(self):
        if self.cooldown > 0:
            return []
        self.cooldown = self.cooldown_max
        cx = self.x + self.width // 2
        bullets = [PlayerBullet(cx - 2, self.y)]
        if self.has_triple:
            bullets.append(PlayerBullet(cx - 10, self.y + 4))
            bullets.append(PlayerBullet(cx + 2, self.y + 4))
        return bullets
    def take_damage(self):
        if self.has_shield:
            self.has_shield = False
            return False
        self.health -= 1
        if self.health <= 0:
            self.lives -= 1
            if self.lives <= 0:
                self.alive = False
            else:
                self.health = self.max_health
        return True
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        hull = COLORS['cyan'] if not self.has_rapid else (0, 200, 100)
        pygame.draw.polygon(screen, hull, [(x, y + 14), (x + 36, y + 14), (x + 18, y)])
        pygame.draw.circle(screen, (100, 200, 255), (x + 18, y + 8), 5)
        for wx in [2, 34]:
            pygame.draw.polygon(screen, (0, 150, 200),
                [(x + wx, y + 14), (x + wx + (wx < 18 and -6 or 6), y + 20),
                 (x + wx, y + 24)])
        flicker = abs(math.sin(self.pulse)) * 4
        flame = COLORS['green'] if self.has_rapid else COLORS['cyan']
        pygame.draw.circle(screen, flame, (x + 18, y + 22), 3 + flicker)
        if self.has_shield:
            pygame.draw.circle(screen, COLORS['purple'], (x + 18, y + 12), 22, 2)
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    def draw_lives(self, screen):
        for i in range(self.lives):
            x = SCREEN_W - 120 + i * 30
            y = 10
            mini = [(x, y + 8), (x + 14, y + 8), (x + 7, y)]
            pygame.draw.polygon(screen, COLORS['cyan'], mini)

class SpaceInvaders:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Space Invaders Ultimate Edition")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)
        self.high_score = 0
        self.reset_game()
    def reset_game(self):
        self.state = 'start'
        self.score = 0
        self.wave = 1
        self.shake = 0
        self.shake_intensity = 0
        self.starfield = StarField()
        self.particles = []
        self.floating_texts = []
        self.power_ups = []
        self.active_powerups = {}
        self.enemy_bullets = []
        self.bombs = []
        self.player_bullets = []
        self.player = Player()
        self.enemies = EnemyFormation(self.wave, self._on_enemy_kill)
    def _on_enemy_kill(self, enemy):
        if random.random() < 0.25:
            types = ['rapid', 'triple', 'shield', 'bomb', 'life']
            ptype = random.choice(types)
            self.power_ups.append(PowerUp(enemy.x, enemy.y, ptype))
    def handle_event(self, event):
        from pygame import QUIT, KEYDOWN, KEYUP
        if event.type == QUIT:
            return 'quit'
        if event.type == KEYDOWN:
            if self.state == 'start':
                if event.key == pygame.K_SPACE:
                    self.state = 'playing'
                    return None
            elif self.state == 'playing':
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = 'paused'
                    return None
                if event.key == pygame.K_SPACE:
                    bullets = self.player.shoot()
                    self.player_bullets.extend(bullets)
            elif self.state == 'paused':
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = 'playing'
                    return None
            elif self.state == 'game_over':
                if event.key == pygame.K_SPACE:
                    self.reset_game()
                    self.state = 'playing'
            elif self.state == 'level_complete':
                pass
        return None
    def update(self):
        keys = pygame.key.get_pressed()
        self.starfield.update()
        if self.state == 'playing':
            self.player.update(keys, self.particles)
            for e in self.enemies.enemies:
                if random.random() < e.shoot_rate:
                    self.enemy_bullets.append(EnemyBullet(e.x + e.width // 2, e.y + e.height))
                if random.random() < 0.0003:
                    self.bombs.append(Bomb(e.x + e.width // 2, e.y + e.height))
            self.enemies.update()
            for pb in self.player_bullets[:]:
                pb.update()
                if not pb.alive:
                    self.player_bullets.remove(pb)
            for eb in self.enemy_bullets[:]:
                eb.update()
                if not eb.alive:
                    self.enemy_bullets.remove(eb)
            for b in self.bombs[:]:
                b.update(self.particles)
                if not b.alive:
                    self.bombs.remove(b)
            for pu in self.power_ups[:]:
                pu.update()
                if not pu.alive:
                    self.power_ups.remove(pu)
            for p in self.particles[:]:
                p.update()
                if not p.alive():
                    self.particles.remove(p)
            for ft in self.floating_texts[:]:
                ft.update()
                if not ft.alive():
                    self.floating_texts.remove(ft)
            self._check_collisions()
            if self.enemies.all_dead():
                self.state = 'level_complete'
                self._wave_pause = 120
            for k, v in self.active_powerups.items():
                v['timer'] -= 1
                if v['timer'] <= 0:
                    del self.active_powerups[k]
                    if k == 'rapid':
                        self.player.has_rapid = False
                    elif k == 'triple':
                        self.player.has_triple = False
                    elif k == 'shield':
                        self.player.has_shield = False
            if self.shake > 0:
                self.shake -= 1
        elif self.state == 'level_complete':
            self._wave_pause -= 1
            if self._wave_pause <= 0:
                self.wave += 1
                self.enemies = EnemyFormation(self.wave, self._on_enemy_kill)
                self.state = 'playing'
    def _check_collisions(self):
        for pb in self.player_bullets[:]:
            if not pb.alive:
                continue
            for e in self.enemies.enemies[:]:
                if e.alive and pb.get_rect().colliderect(e.get_rect()):
                    pb.alive = False
                    e.hp -= 1
                    if e.hp <= 0:
                        e.alive = False
                        for _ in range(25):
                            vx = random.uniform(-4, 4)
                            vy = random.uniform(-5, -1)
                            self.particles.append(Particle(e.x + 15, e.y + 12, e.color, vx, vy, 30, 3, 0.05))
                        self.floating_texts.append(FloatingText(e.x, e.y, str(e.pts)))
                        self.score += e.pts
                        if random.random() < 0.25:
                            types = ['rapid', 'triple', 'shield', 'bomb', 'life']
                            ptype = random.choice(types)
                            self.power_ups.append(PowerUp(e.x, e.y, ptype))
                        self.enemies.enemies.remove(e)
                        self.shake = 5
                    else:
                        for _ in range(4):
                            vx = random.uniform(-2, 2)
                            vy = random.uniform(-2, 2)
                            self.particles.append(Particle(pb.x, pb.y, (200, 200, 200), vx, vy, 10, 1))
                    break
        for eb in self.enemy_bullets[:]:
            if not eb.alive:
                continue
            pr = self.player.get_rect()
            if eb.get_rect().colliderect(pr) and self.player.alive:
                eb.alive = False
                if self.player.take_damage():
                    self.floating_texts.append(FloatingText(self.player.x, self.player.y, "HIT!", COLORS['red']))
                    for _ in range(10):
                        vx = random.uniform(-3, 3)
                        vy = random.uniform(-3, 3)
                        self.particles.append(Particle(self.player.x + 18, self.player.y + 14, COLORS['red'], vx, vy, 20, 2))
                    self.shake = 10
                    if not self.player.alive:
                        self.state = 'game_over'
                        self.shake = 25
                        if self.score > self.high_score:
                            self.high_score = self.score
        for b in self.bombs[:]:
            if not b.alive:
                continue
            pr = self.player.get_rect()
            if b.get_rect().colliderect(pr) and self.player.alive:
                b.alive = False
                self.floating_texts.append(FloatingText(self.player.x, self.player.y, "BOMB!", COLORS['red']))
                for _ in range(20):
                    vx = random.uniform(-5, 5)
                    vy = random.uniform(-5, 5)
                    self.particles.append(Particle(self.player.x + 18, self.player.y + 14, COLORS['red'], vx, vy, 25, 3))
                for p in self.player_bullets[:]:
                    p.alive = False
                if self.player.take_damage():
                    self.shake = 15
                    if not self.player.alive:
                        self.state = 'game_over'
                        self.shake = 25
                        if self.score > self.high_score:
                            self.high_score = self.score
            else:
                for e in self.enemies.enemies[:]:
                    if e.alive and b.get_rect().colliderect(e.get_rect()):
                        b.alive = False
                        e.hp -= 2
                        if e.hp <= 0:
                            e.alive = False
                            self.floating_texts.append(FloatingText(e.x, e.y, str(e.pts)))
                            self.score += e.pts
                            self.enemies.enemies.remove(e)
            for pb in self.player_bullets[:]:
                if pb.alive and b.get_rect().colliderect(pb.get_rect()):
                    pb.alive = False
        for pu in self.power_ups[:]:
            if pu.alive and pu.get_rect().colliderect(self.player.get_rect()):
                pu.alive = False
                self.active_powerups[pu.ptype] = {'timer': pu.dur}
                if pu.ptype == 'rapid':
                    self.player.has_rapid = True
                elif pu.ptype == 'triple':
                    self.player.has_triple = True
                elif pu.ptype == 'shield':
                    self.player.has_shield = True
                    self.player.health = min(self.player.max_health, self.player.health + 1)
                elif pu.ptype == 'bomb':
                    for e in self.enemies.enemies[:]:
                        if e.alive:
                            e.hp = 0
                            self.score += e.pts
                    self.enemies.enemies.clear()
                    self.floating_texts.append(FloatingText(self.player.x, self.player.y, "BOMB!", COLORS['red']))
                    self.shake = 20
                elif pu.ptype == 'life':
                    self.player.health = min(self.player.max_health, self.player.health + 1)
                self.floating_texts.append(FloatingText(self.player.x, self.player.y, pu.name, pu.color))
    def draw(self):
        shake_offset = (0, 0)
        if self.shake > 0:
            shake_offset = (random.randint(-self.shake, self.shake), random.randint(-self.shake, self.shake))
        screen = self.screen
        self.screen.fill(BG_COLOR)
        self.starfield.draw(self.screen)
        if self.state == 'start':
            self._draw_start()
            return
        self.player_bullets = [b for b in self.player_bullets if b.alive]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]
        self.bombs = [b for b in self.bombs if b.alive]
        self.power_ups = [p for p in self.power_ups if p.alive]
        if self.state in ('playing', 'paused', 'level_complete'):
            self.player.draw(self.screen)
            self.player.draw_lives(self.screen)
            self.enemies.draw(self.screen)
        for pb in self.player_bullets:
            pb.draw(self.screen)
        for eb in self.enemy_bullets:
            eb.draw(self.screen)
        for b in self.bombs:
            b.draw(self.screen)
        for pu in self.power_ups:
            pu.draw(self.screen)
        for p in self.particles:
            if p.alive():
                p.draw(self.screen)
        for ft in self.floating_texts:
            if ft.alive():
                ft.draw(self.screen)
        self._draw_ui()
        if self.state == 'paused':
            self._draw_pause()
        elif self.state == 'level_complete':
            self._draw_level_complete()
        elif self.state == 'game_over':
            self._draw_game_over()
        if shake_offset[0] != 0 or shake_offset[1] != 0:
            screen.blit(self.screen, shake_offset)
    def _draw_ui(self):
        score_surf = self.font.render(f"Score: {self.score}", True, COLORS['white'])
        self.screen.blit(score_surf, (10, 10))
        hs_surf = self.small_font.render(f"High: {self.high_score}", True, COLORS['yellow'])
        self.screen.blit(hs_surf, (10, 40))
        wave_surf = self.small_font.render(f"Wave: {self.wave}", True, COLORS['cyan'])
        self.screen.blit(wave_surf, (SCREEN_W - 120, 10))
        bar_x, bar_y, bar_w, bar_h = SCREEN_W // 2 - 75, 8, 150, 14
        pygame.draw.rect(self.screen, (50, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        fill = max(0, bar_w * self.player.health // self.player.max_health)
        fill_color = COLORS['green'] if fill > bar_w * 0.3 else COLORS['red']
        pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill, bar_h))
        pygame.draw.rect(self.screen, COLORS['white'], (bar_x, bar_y, bar_w, bar_h), 1)
        py = 55
        for k, v in self.active_powerups.items():
            info = PowerUp.TYPES.get(k, {})
            sym = info.get('symbol', '?')
            color = info.get('color', COLORS['white'])
            name = info.get('name', k)
            surf = self.small_font.render(f"{sym} {name}: {v['timer']//60}s", True, color)
            self.screen.blit(surf, (10, py))
            py += 18
    def _draw_start(self):
        title = self.title_font.render("SPACE INVADERS", True, COLORS['cyan'])
        sub = self.font.render("ULTIMATE EDITION", True, COLORS['purple'])
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 3))
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 3 + 60))
        controls = [
            "Arrow Keys / WASD - Move",
            "SPACE - Shoot / Start",
            "P / ESC - Pause",
        ]
        cy = SCREEN_H // 2
        for line in controls:
            surf = self.small_font.render(line, True, COLORS['gray'])
            self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, cy))
            cy += 25
        start_surf = self.font.render("Press SPACE to Start", True, COLORS['yellow'])
        self.screen.blit(start_surf, (SCREEN_W // 2 - start_surf.get_width() // 2, SCREEN_H - 100))
    def _draw_pause(self):
        surf = self.title_font.render("PAUSED", True, COLORS['white'])
        self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, SCREEN_H // 2 - 40))
    def _draw_level_complete(self):
        surf = self.title_font.render(f"WAVE {self.wave} COMPLETE!", True, COLORS['green'])
        self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, SCREEN_H // 2 - 40))
    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        surf = self.title_font.render("GAME OVER", True, COLORS['red'])
        self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, SCREEN_H // 3))
        score_surf = self.font.render(f"Score: {self.score}", True, COLORS['white'])
        self.screen.blit(score_surf, (SCREEN_W // 2 - score_surf.get_width() // 2, SCREEN_H // 2))
        if self.score >= self.high_score and self.score > 0:
            hs_surf = self.font.render("NEW HIGH SCORE!", True, COLORS['yellow'])
            self.screen.blit(hs_surf, (SCREEN_W // 2 - hs_surf.get_width() // 2, SCREEN_H // 2 + 50))
        restart = self.font.render("Press SPACE to Restart", True, COLORS['green'])
        self.screen.blit(restart, (SCREEN_W // 2 - restart.get_width() // 2, SCREEN_H - 100))
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                result = self.handle_event(event)
                if result == 'quit':
                    running = False
                    break
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == '__main__':
    game = SpaceInvaders()
    game.run()
