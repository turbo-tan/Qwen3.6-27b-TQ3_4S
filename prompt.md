Prompt:
Create a complete Space Invaders arcade game in Python using Pygame. The game should be a single file (space_invaders.py) with the following 
features:
Core Setup:
- 800x700 screen at 60 FPS using Pygame
- Black background with a parallax star field (50 animated stars drifting downward at different speeds and brightness)

Game States: Start screen, Playing, Paused, Game Over, and Level Complete (wave transition)
Player Ship:
- Drawn as a detailed ship with hull body, cockpit, wing accents, and flickering engine flames (cyan by default, green glow when "rapid" power-up is active)
- Move with arrow keys or WASD. Up/down constrained to lower portion of screen
- Shooting with SPACE key, 12-frame cooldown. Ship has a trailing particle effect behind it
- Health bar (5 max health) displayed at top center. Lives (3) shown as small ship icons
- When damaged, shows red particle flash
Enemy Types (4 types, drawn with detailed shapes):

1. Basic - Green alien with rounded body, large eyes with pupils, mouth slit, claws. 1 HP, 100 pts, slow speed (0.3)
2. Fast - Orange arrowhead-shaped enemy with speed streaks behind it. 1 HP, 150 pts, fast speed (0.8)
3. Tank - Purple armored beast with armor plating, cannon barrel, glowing eye sensor, and a health bar above it. 3 HP, 300 pts, very slow (0.2)
4. Shooter - Red UFO with dome and saucer body, pulsing side lights, glowing eye. 2 HP, 250 pts, slow speed (0.3). Can shoot red projectiles downward

Enemy Formation:
- Grid of enemies that move horizontally and slowly descend
- Bounce off screen edges and change direction, descending on each edge hit
- Wave scaling: rows increase from 3 to max 6. Columns from 6 to max 10
- Enemy types per wave: wave 1 = basic + shooter; wave 2+ adds fast; wave 3+ adds tank; wave 4+ adds extra shooters
- Enemy types randomly assigned from the unlocked pool

Enemy Shooting & Bombs:
- Enemies shoot red bullets downward at random intervals (30-80 frames). All enemy types can shoot
- Enemies occasionally drop bombs (red glowing spinning projectiles with particle trails) that destroy nearby player bullets on impact and deal double damage to player

Player Shooting:
- White bullets with a glowing outline
- Triple-shot power-up fires 3 bullets in a spread pattern

Power-Ups (25% drop chance from killed enemies, pulsing with letter symbol):
- R (Rapid Fire) - Green, enables faster shooting
- T (Triple Shot) - Cyan, enables 3-way bullet spread
- S (Shield) - Purple, prevents damage from enemy bullets, also heals 1 HP
- B (Bomb) - Red, destroys all enemies on screen instantly
- L (Life) - Yellow, heals 1 HP (no visual indicator)
- Power-ups last 600 frames (~10 seconds); active power-ups shown as timed indicators at bottom-left of screen

Particle System:
- Explosion particles with gravity and fade-out (default 15 particles per kill, 25 for enemy destruction)
- Impact particles when bullets hit enemies
- Engine trail behind player ship (cyan)
- Red trail when player is damaged

Floating Score Text:
- Points earned displayed as floating text that rises and fades upward from destroyed enemy positions
- "HIT!", "BOMB!", and power-up names pop up at player position

Screen Shake:
- 5 intensity for enemy kills, 10 for player hits, 15 for bomb impacts, 20-25 for game over
- Decays by 1 per frame

UI Elements:
- Score (top-left, large), High score (top-left, yellow, smaller)
- Wave number (top-right, cyan)
- Health bar (top center, red/green fill)
- Power-up timers (bottom-left)
- Lives as mini ship icons (top-right)

Start Screen: Title "SPACE INVADERS" in cyan with "ULTIMATE EDITION" subtitle in purple, controls listed, "Press SPACE to Start" in yellow
Level Up: Green "WAVE X" text centered, brief pause then spawns next wave
Game Over: Semi-transparent black overlay, "GAME OVER" in red, final score, "NEW HIGH SCORE!" if beaten, "Press SPACE to Restart" in green
Pause: White "PAUSED" text centered. P or ESC to resume

Controls:
- Arrow keys or WASD to move
- SPACE to shoot and to start/restart
- P or ESC to pause

High Score Tracking: Persists within the session (stored as instance variable)
The game loops in a standard Pygame event loop, processing events, calling update(), then draw(), capped at 60 FPS. Include a __main__ block that instantiates and runs the game.
