import turtle
import math
import random
import time


# ============================================================
# CONFIGURATION
# ============================================================
class Config:
    WIDTH = 900
    HEIGHT = 700
    BG_COLOR = "#0a0a1e"

    # Paddle
    PADDLE_W = 130
    PADDLE_H = 16
    PADDLE_Y_OFFSET = 70
    PADDLE_SPEED = 620
    PADDLE_EASE = 18

    # Ball
    BALL_RADIUS = 9
    BALL_BASE_SPEED = 380.0
    BALL_MAX_SPEED = 380.0 * 1.6
    BALL_SPEED_INCREMENT = 1.02
    BALL_LAUNCH_ANGLE = 25

    # Bricks
    BRICK_W = 72
    BRICK_H = 26
    BRICK_COLS = 10
    BRICK_ROWS = 6
    BRICK_GAP_X = 6
    BRICK_GAP_Y = 6
    BRICK_TOP_OFFSET = 120

    # Gameplay
    STARTING_LIVES = 3
    ROW_COLORS = ["#ff1744", "#ff9100", "#ffea00",
                  "#00e676", "#00b0ff", "#d500f9"]
    ROW_POINTS = [60, 50, 40, 30, 20, 10]

    # Visual
    PADDLE_COLOR = "#4fc3f7"
    PADDLE_GLOW = "#0f3550"
    BALL_COLOR = "#ffffff"
    TRAIL_COLOR = "#88ccff"
    TRAIL_LIFE = 10
    STAR_COUNT = 80


# ============================================================
# STARFIELD
# ============================================================
class Starfield:
    def __init__(self, cfg):
        self.cfg = cfg
        self.stars = []
        for _ in range(cfg.STAR_COUNT):
            s = turtle.Turtle()
            s.hideturtle()
            s.penup()
            s.shape("circle")
            s.shapesize(random.choice([0.1, 0.15, 0.2]))
            s.color(random.choice(["#ffffff", "#aaccff",
                                   "#ffddaa", "#8888cc"]))
            s.goto(random.randint(-cfg.WIDTH // 2, cfg.WIDTH // 2),
                   random.randint(-cfg.HEIGHT // 2, cfg.HEIGHT // 2))
            s.showturtle()
            self.stars.append(s)

    def twinkle(self):
        if random.random() < 0.15:
            s = random.choice(self.stars)
            s.shapesize(random.choice([0.1, 0.15, 0.2]))


# ============================================================
# TRAIL
# ============================================================
class TrailParticle:
    def __init__(self, x, y, cfg):
        self.cfg = cfg
        self.life = cfg.TRAIL_LIFE
        self.max_life = cfg.TRAIL_LIFE
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.penup()
        self.t.shape("circle")
        self.t.shapesize(0.5)
        self.t.color(cfg.TRAIL_COLOR)
        self.t.goto(x, y)
        self.t.showturtle()

    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.t.hideturtle()
            return False
        self.t.shapesize(0.5 * self.life / self.max_life)
        return True


class Trail:
    def __init__(self, cfg):
        self.cfg = cfg
        self.particles = []

    def spawn(self, x, y):
        self.particles.append(TrailParticle(x, y, self.cfg))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def clear(self):
        for p in self.particles:
            p.t.hideturtle()
        self.particles.clear()


# ============================================================
# PADDLE
# ============================================================
class Paddle:
    def __init__(self, cfg):
        self.cfg = cfg

        self.glow = turtle.Turtle()
        self.glow.shape("square")
        self.glow.shapesize(stretch_wid=(cfg.PADDLE_H + 8) / 20,
                            stretch_len=(cfg.PADDLE_W + 8) / 20)
        self.glow.color(cfg.PADDLE_GLOW)
        self.glow.penup()

        self.body = turtle.Turtle()
        self.body.shape("square")
        self.body.shapesize(stretch_wid=cfg.PADDLE_H / 20,
                            stretch_len=cfg.PADDLE_W / 20)
        self.body.color(cfg.PADDLE_COLOR)
        self.body.penup()

        self.target_x = 0.0
        self.smooth_x = 0.0
        self.reset()

    @property
    def x(self):
        return self.body.xcor()

    @property
    def y(self):
        return self.body.ycor()

    @property
    def half_w(self):
        return self.cfg.PADDLE_W / 2

    @property
    def half_h(self):
        return self.cfg.PADDLE_H / 2

    def reset(self):
        y = -self.cfg.HEIGHT // 2 + self.cfg.PADDLE_Y_OFFSET
        self.target_x = 0.0
        self.smooth_x = 0.0
        self.body.goto(0, y)
        self.glow.goto(0, y)

    def move(self, direction, dt):
        if direction:
            self.target_x += direction * self.cfg.PADDLE_SPEED * dt
            limit = self.cfg.WIDTH // 2 - self.half_w - 25
            self.target_x = max(-limit, min(limit, self.target_x))

    def update(self, dt):
        ease = min(1, dt * self.cfg.PADDLE_EASE)
        self.smooth_x += (self.target_x - self.smooth_x) * ease
        self.body.setx(self.smooth_x)
        self.glow.setx(self.smooth_x)

    def hit_offset(self, ball_x):
        off = (ball_x - self.x) / self.half_w
        return max(-1, min(1, off))


# ============================================================
# BALL
# ============================================================
class Ball:
    def __init__(self, cfg, trail):
        self.cfg = cfg
        self.trail = trail
        self.t = turtle.Turtle()
        self.t.shape("circle")
        self.t.shapesize(cfg.BALL_RADIUS / 10)
        self.t.color(cfg.BALL_COLOR)
        self.t.penup()

        self.vx = 0.0
        self.vy = 0.0
        self.speed = cfg.BALL_BASE_SPEED
        self.reset()

    @property
    def x(self):
        return self.t.xcor()

    @property
    def y(self):
        return self.t.ycor()

    @property
    def radius(self):
        return self.cfg.BALL_RADIUS

    def reset(self):
        self.t.goto(0, -self.cfg.HEIGHT // 2 + 120)
        angle = random.uniform(-self.cfg.BALL_LAUNCH_ANGLE,
                                self.cfg.BALL_LAUNCH_ANGLE)
        rad = math.radians(angle)
        self.vx = self.speed * math.sin(rad)
        self.vy = self.speed * math.cos(rad)

    def bounce_x(self):
        self.vx = -self.vx

    def bounce_y(self):
        self.vy = -self.vy

    def reflect_off_paddle(self, offset):
        angle = offset * math.radians(70)
        self.speed = min(self.speed * self.cfg.BALL_SPEED_INCREMENT,
                         self.cfg.BALL_MAX_SPEED)
        self.vx = self.speed * math.sin(angle)
        self.vy = self.speed * math.cos(angle)
        if self.vy < 0:
            self.vy = -self.vy

    def update(self, dt):
        old_x, old_y = self.t.xcor(), self.t.ycor()
        self.t.setx(old_x + self.vx * dt)
        self.t.sety(old_y + self.vy * dt)
        self.trail.spawn(old_x, old_y)


# ============================================================
# BRICK
# ============================================================
class Brick:
    def __init__(self, x, y, color, points, cfg):
        self.cfg = cfg
        self.points = points
        self.w = cfg.BRICK_W
        self.h = cfg.BRICK_H

        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.shape("square")
        self.t.shapesize(stretch_wid=self.h / 20,
                         stretch_len=self.w / 20)
        self.t.color(color)
        self.t.penup()
        self.t.goto(x, y)
        self.t.showturtle()

    @property
    def x(self):
        return self.t.xcor()

    @property
    def y(self):
        return self.t.ycor()

    def destroy(self):
        self.t.hideturtle()

    def intersects_circle(self, cx, cy, r):
        hw, hh = self.w / 2, self.h / 2
        closest_x = max(self.x - hw, min(cx, self.x + hw))
        closest_y = max(self.y - hh, min(cy, self.y + hh))
        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) <= (r * r)



# HUD
# ============================================================
# HUD
# ============================================================
class HUD:
    def __init__(self, cfg):
        self.cfg = cfg

        self.score = turtle.Turtle()
        self.score.hideturtle()
        self.score.penup()
        self.score.color("#ffffff")
        self.score.goto(-cfg.WIDTH // 2 + 40, cfg.HEIGHT // 2 - 40)

        self.lives = turtle.Turtle()
        self.lives.hideturtle()
        self.lives.penup()
        self.lives.color("#ff6b6b")
        self.lives.goto(cfg.WIDTH // 2 - 40, cfg.HEIGHT // 2 - 40)

        self.title = turtle.Turtle()
        self.title.hideturtle()
        self.title.penup()
        self.title.color("#7c4dff")
        self.title.goto(0, cfg.HEIGHT // 2 - 40)
        self.title.write("B R E A K O U T", align="center",
                         font=("Courier New", 18, "bold"))

        # Create overlay LAST so it has the highest draw priority
        self.overlay = turtle.Turtle()
        self.overlay.hideturtle()
        self.overlay.penup()

    def update_score(self, score):
        self.score.clear()
        self.score.write(f"SCORE  {score}", align="left",
                         font=("Courier New", 18, "bold"))

    def update_lives(self, lives):
        self.lives.clear()
        hearts = "♥ " * lives if lives > 0 else "—"
        self.lives.write(hearts.strip(), align="right",
                         font=("Courier New", 18, "bold"))

    def show_overlay(self, message, color, game_instance):
        # 1. Hide all bricks so they don't cover the text
        for brick in game_instance.bricks:
            brick.t.hideturtle()

        # 2. Clear previous overlay text
        self.overlay.clear()
        self.overlay.clearstamps()

        # 3. Draw a solid background panel to hide the ball/trail behind text
        self.overlay.goto(0, 0)
        self.overlay.shape("square")
        self.overlay.shapesize(stretch_wid=6, stretch_len=22)  # Panel size
        self.overlay.color("#0a0a1e")
        self.overlay.stamp()
        self.overlay.shape("arrow")  # reset shape

        # 4. Draw Main Message
        self.overlay.goto(0, 60)
        self.overlay.color(color)
        self.overlay.write(message, align="center",
                           font=("Courier New", 48, "bold"))

        # 5. Draw Sub-message
        self.overlay.goto(0, -20)
        self.overlay.color("#cccccc")
        self.overlay.write("Press  SPACE  to play again",
                           align="center",
                           font=("Courier New", 18, "bold"))

    def clear_overlay(self):
        self.overlay.clear()
        self.overlay.clearstamps()


# GAME
class Breakout:
    def __init__(self, cfg):
        self.cfg = cfg
        self._setup_screen()
        self._setup_borders()

        self.starfield = Starfield(cfg)
        self.trail = Trail(cfg)
        self.paddle = Paddle(cfg)
        self.ball = Ball(cfg, self.trail)
        self.hud = HUD(cfg)

        self.bricks = []
        self._build_bricks()

        self.score = 0
        self.lives = cfg.STARTING_LIVES
        self.game_over = False

        self.left_pressed = False
        self.right_pressed = False

        self._bind_keys()

        self.hud.update_score(self.score)
        self.hud.update_lives(self.lives)

        # Play bounds
        self.LEFT = -cfg.WIDTH // 2 + 22
        self.RIGHT = cfg.WIDTH // 2 - 22
        self.TOP = cfg.HEIGHT // 2 - 70
        self.BOTTOM = -cfg.HEIGHT // 2 + 22

    # ---------- SETUP ----------
    def _setup_screen(self):
        self.screen = turtle.Screen()
        self.screen.title("BREAKOUT ✦ Enhanced Edition")
        self.screen.bgcolor(self.cfg.BG_COLOR)
        self.screen.setup(width=self.cfg.WIDTH, height=self.cfg.HEIGHT)
        self.screen.tracer(0)
        self.screen.listen()

    def _setup_borders(self):
        cfg = self.cfg
        b = turtle.Turtle()
        b.hideturtle()
        b.penup()
        b.color("#3a3a6a")
        b.goto(-cfg.WIDTH // 2 + 10, -cfg.HEIGHT // 2 + 10)
        b.pendown()
        b.pensize(4)
        for _ in range(2):
            b.forward(cfg.WIDTH - 20)
            b.left(90)
            b.forward(cfg.HEIGHT - 20)
            b.left(90)
        b.penup()

        line = turtle.Turtle()
        line.hideturtle()
        line.penup()
        line.color("#2a2a4a")
        line.pensize(2)
        line.goto(-cfg.WIDTH // 2 + 15, cfg.HEIGHT // 2 - 55)
        line.pendown()
        line.forward(cfg.WIDTH - 30)
        line.penup()

    def _build_bricks(self):
        cfg = self.cfg
        total_w = cfg.BRICK_COLS * cfg.BRICK_W + (cfg.BRICK_COLS - 1) * cfg.BRICK_GAP_X
        start_x = -total_w / 2 + cfg.BRICK_W / 2
        for r in range(cfg.BRICK_ROWS):
            for c in range(cfg.BRICK_COLS):
                x = start_x + c * (cfg.BRICK_W + cfg.BRICK_GAP_X)
                y = cfg.BRICK_TOP_OFFSET - r * (cfg.BRICK_H + cfg.BRICK_GAP_Y)
                y = (cfg.HEIGHT // 2) - cfg.BRICK_TOP_OFFSET - r * (cfg.BRICK_H + cfg.BRICK_GAP_Y)
                self.bricks.append(
                    Brick(x, y, cfg.ROW_COLORS[r], cfg.ROW_POINTS[r], cfg)
                )

    def _bind_keys(self):
        s = self.screen
        s.onkeypress(lambda: setattr(self, "left_pressed", True), "Left")
        s.onkeyrelease(lambda: setattr(self, "left_pressed", False), "Left")
        s.onkeypress(lambda: setattr(self, "right_pressed", True), "Right")
        s.onkeyrelease(lambda: setattr(self, "right_pressed", False), "Right")
        s.onkeypress(lambda: setattr(self, "left_pressed", True), "a")
        s.onkeyrelease(lambda: setattr(self, "left_pressed", False), "a")
        s.onkeypress(lambda: setattr(self, "right_pressed", True), "d")
        s.onkeyrelease(lambda: setattr(self, "right_pressed", False), "d")
        s.onkey(self._restart, "space")

    # ---------- RESET ----------
    def _restart(self):
        if not self.game_over:
            return
        for brick in self.bricks:
            brick.destroy()
        self.bricks.clear()
        self._build_bricks()

        self.score = 0
        self.lives = self.cfg.STARTING_LIVES
        self.game_over = False
        self.hud.clear_overlay()
        self.hud.update_score(self.score)
        self.hud.update_lives(self.lives)
        self.trail.clear()
        self.paddle.reset()
        self.ball.reset()

    def _lose_life(self):
        self.lives -= 1
        self.hud.update_lives(self.lives)
        if self.lives <= 0:
            self.game_over = True
            self.hud.show_overlay("GAME OVER", "#ff1744",self)
        else:
            self.paddle.reset()
            self.ball.reset()
            self.screen.update()
            time.sleep(0.4)

    def _win(self):
        self.game_over = True
        self.hud.show_overlay("YOU WIN!", "#00e676",self)

    # ---------- COLLISION ----------
    def _handle_paddle_collision(self):
        if self.ball.vy >= 0:
            return
        if not self._aabb_circle_overlap(
            self.paddle.x, self.paddle.y,
            self.paddle.half_w, self.paddle.half_h,
            self.ball.x, self.ball.y, self.ball.radius
        ):
            return

        # Reposition ball on top of paddle
        self.ball.t.sety(self.paddle.y + self.paddle.half_h + self.ball.radius + 1)
        offset = self.paddle.hit_offset(self.ball.x)
        self.ball.reflect_off_paddle(offset)

    def _handle_brick_collisions(self):
        for brick in self.bricks[:]:
            if brick.intersects_circle(self.ball.x, self.ball.y, self.ball.radius):
                # Determine bounce axis by penetration depth
                overlap_x = (brick.w / 2 + self.ball.radius) - abs(self.ball.x - brick.x)
                overlap_y = (brick.h / 2 + self.ball.radius) - abs(self.ball.y - brick.y)
                if overlap_x < overlap_y:
                    self.ball.bounce_x()
                else:
                    self.ball.bounce_y()

                brick.destroy()
                self.bricks.remove(brick)
                self.score += brick.points
                self.hud.update_score(self.score)
                break

    @staticmethod
    def _aabb_circle_overlap(rx, ry, hw, hh, cx, cy, r):
        closest_x = max(rx - hw, min(cx, rx + hw))
        closest_y = max(ry - hh, min(cy, ry + hh))
        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) <= (r * r)

    # ---------- WALLS ----------
    def _handle_walls(self):
        r = self.ball.radius
        if self.ball.x < self.LEFT + r:
            self.ball.t.setx(self.LEFT + r)
            self.ball.bounce_x()
        elif self.ball.x > self.RIGHT - r:
            self.ball.t.setx(self.RIGHT - r)
            self.ball.bounce_x()
        if self.ball.y > self.TOP - r:
            self.ball.t.sety(self.TOP - r)
            self.ball.bounce_y()

    # ---------- FRAME ----------
    def _update(self, dt):
        direction = 0
        if self.left_pressed and not self.right_pressed:
            direction = -1
        elif self.right_pressed and not self.left_pressed:
            direction = 1

        self.paddle.move(direction, dt)
        self.paddle.update(dt)

        self.ball.update(dt)
        self._handle_walls()
        self._handle_paddle_collision()
        self._handle_brick_collisions()
        self.trail.update()

        if self.ball.y < self.BOTTOM - 20:
            self._lose_life()

        if not self.bricks and not self.game_over:
            self._win()

    def run(self):
        last = time.perf_counter()
        while True:
            now = time.perf_counter()
            dt = min(now - last, 1 / 30)
            last = now

            if not self.game_over:
                self._update(dt)

            self.starfield.twinkle()
            self.screen.update()



# ENTRY POINT
if __name__ == "__main__":
    config = Config()
    game = Breakout(config)
    game.run()