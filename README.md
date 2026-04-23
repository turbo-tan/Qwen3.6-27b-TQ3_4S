# Space Invaders — Ultimate Edition

A full-featured **Space Invaders** arcade game built with **Pygame** (Python 3).

## Features

- **4 enemy types**: Basic, Fast, Tank (3 HP), Shooter — each with unique visuals and behaviour
- **5 power-ups**: Rapid Fire, Triple Shot, Shield, Bomb, Extra Life
- **Parallax starfield** background
- **Particle effects** on destruction
- **Floating score text** on kills
- **Screen shake** on hits
- **Progressive wave system** — enemies get tougher each wave
- **High score** tracking per session

## Requirements

- Python 3.x
- Pygame (`pip install pygame`)

## How to Run

```bash
python3 space_invaders.py
```

## Controls

| Key          | Action            |
|--------------|-------------------|
| Arrow Keys / WASD | Move ship    |
| SPACE        | Shoot / Start     |
| P / ESC      | Pause / Resume    |

## Enemy Types

| Type    | HP | Points | Colour   | Notes              |
|---------|----|--------|----------|--------------------|
| Basic   | 1  | 100    | Green    | Slow, low threat   |
| Shooter | 2  | 250    | Red      | Shoots frequently  |
| Fast    | 1  | 150    | Orange   | Speedy, leaves trail |
| Tank    | 3  | 300    | Purple   | Takes multiple hits |

## Power-Ups

| Symbol | Name        | Effect                              |
|--------|-------------|-------------------------------------|
| R      | Rapid Fire  | Doubles fire rate (10s)             |
| T      | Triple Shot | Fires 3 bullets at once (10s)       |
| S      | Shield      | Absorbs next hit, heals 1 HP (10s)  |
| B      | Bomb        | Destroys all enemies on screen      |
| L      | Life        | Restores 1 HP                        |

Power-ups drop from killed enemies with a **25% chance**.
