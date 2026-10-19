import turtle
import random
import math

# Set up the screen
screen = turtle.Screen()
screen.title("Breakout Clone")
screen.bgcolor("black")
screen.setup(width=800, height=600)
screen.tracer(0)  # Turn off automatic animation for smoother gameplay

# Game variables
score = 0
lives = 3
game_over = False

# Create paddle
paddle = turtle.Turtle()
paddle.shape("square")
paddle.color("white")
paddle.shapesize(stretch_wid=1, stretch_len=8)
paddle.penup()
paddle.goto(0, -250)

# Create ball
ball = turtle.Turtle()
ball.shape("circle")
ball.color("white")
ball.penup()
ball.goto(0, -200)
ball.dx = 3  # Ball's x movement speed
ball.dy = 3  # Ball's y movement speed
ball.speed = 1  # Speed multiplier

# Create score display
score_display = turtle.Turtle()
score_display.color("white")
score_display.penup()
score_display.hideturtle()
score_display.goto(-350, 270)
score_display.write(f"Score: {score}", align="left", font=("Courier", 16, "bold"))

# Create lives display
lives_display = turtle.Turtle()
lives_display.color("white")
lives_display.penup()
lives_display.hideturtle()
lives_display.goto(350, 270)
lives_display.write(f"Lives: {lives}", align="right", font=("Courier", 16, "bold"))

# Create game over display
game_over_display = turtle.Turtle()
game_over_display.color("red")
game_over_display.penup()
game_over_display.hideturtle()
game_over_display.goto(0, 0)

# Create restart display
restart_display = turtle.Turtle()
restart_display.color("yellow")
restart_display.penup()
restart_display.hideturtle()
restart_display.goto(0, -50)

# Create bricks
bricks = []
brick_colors = ["red", "orange", "yellow", "green", "blue", "purple"]
brick_width = 60
brick_height = 20
brick_rows = 6
brick_cols = 10
brick_padding = 5
brick_offset_x = -(brick_cols * (brick_width + brick_padding)) / 2 + 30
brick_offset_y = 200

for row in range(brick_rows):
    for col in range(brick_cols):
        brick = turtle.Turtle()
        brick.shape("square")
        brick.color(brick_colors[row % len(brick_colors)])
        brick.shapesize(stretch_wid=brick_height / 20, stretch_len=brick_width / 20)
        brick.penup()
        x = brick_offset_x + col * (brick_width + brick_padding)
        y = brick_offset_y - row * (brick_height + brick_padding)
        brick.goto(x, y)
        bricks.append(brick)

# Paddle movement flags
left_pressed = False
right_pressed = False


# Key press functions
def move_left():
    global left_pressed
    left_pressed = True


def move_right():
    global right_pressed
    right_pressed = True


def stop_left():
    global left_pressed
    left_pressed = False


def stop_right():
    global right_pressed
    right_pressed = False


def restart_game():
    global game_over, score, lives
    if game_over:
        # Reset game variables
        score = 0
        lives = 3
        game_over = False

        # Clear game over displays
        game_over_display.clear()
        restart_display.clear()

        # Reset ball position
        ball.goto(0, -200)
        ball.dx = 3
        ball.dy = 3
        ball.speed = 1

        # Reset paddle position
        paddle.goto(0, -250)

        # Recreate bricks
        for brick in bricks:
            brick.hideturtle()
        bricks.clear()

        for row in range(brick_rows):
            for col in range(brick_cols):
                brick = turtle.Turtle()
                brick.shape("square")
                brick.color(brick_colors[row % len(brick_colors)])
                brick.shapesize(stretch_wid=brick_height / 20, stretch_len=brick_width / 20)
                brick.penup()
                x = brick_offset_x + col * (brick_width + brick_padding)
                y = brick_offset_y - row * (brick_height + brick_padding)
                brick.goto(x, y)
                bricks.append(brick)

        # Update displays
        score_display.clear()
        score_display.write(f"Score: {score}", align="left", font=("Courier", 16, "bold"))
        lives_display.clear()
        lives_display.write(f"Lives: {lives}", align="right", font=("Courier", 16, "bold"))


# Bind keys
screen.listen()
screen.onkeypress(move_left, "Left")
screen.onkeypress(move_right, "Right")
screen.onkeyrelease(stop_left, "Left")
screen.onkeyrelease(stop_right, "Right")
screen.onkey(restart_game, "space")

# Keep the game running
while True:
    screen.update()

    if not game_over:
        # Move paddle based on key state
        if left_pressed and paddle.xcor() > -340:
            paddle.setx(paddle.xcor() - 5)
        if right_pressed and paddle.xcor() < 340:
            paddle.setx(paddle.xcor() + 5)

        # Move ball
        ball.setx(ball.xcor() + ball.dx * ball.speed)
        ball.sety(ball.ycor() + ball.dy * ball.speed)

        # Ball collision with top wall
        if ball.ycor() > 280:
            ball.sety(280)
            ball.dy *= -1

        # Ball collision with bottom wall (lose life)
        if ball.ycor() < -290:
            lives -= 1
            lives_display.clear()
            lives_display.write(f"Lives: {lives}", align="right", font=("Courier", 16, "bold"))

            if lives <= 0:
                game_over = True
                game_over_display.write("GAME OVER", align="center", font=("Courier", 36, "bold"))
                restart_display.write("Press SPACE to restart", align="center", font=("Courier", 20, "bold"))
            else:
                # Reset ball position
                ball.goto(0, -200)
                ball.dx = 3
                ball.dy = 3
                ball.speed = 1
                paddle.goto(0, -250)
                screen.update()
                turtle.time.sleep(0.5)

        # Ball collision with left wall
        if ball.xcor() < -390:
            ball.setx(-390)
            ball.dx *= -1

        # Ball collision with right wall
        if ball.xcor() > 390:
            ball.setx(390)
            ball.dx *= -1

        # Ball collision with paddle
        if (ball.ycor() < -230 and ball.ycor() > -260 and
                ball.xcor() > paddle.xcor() - 80 and
                ball.xcor() < paddle.xcor() + 80):
            # Calculate new ball direction based on where it hits the paddle
            hit_position = (ball.xcor() - paddle.xcor()) / 80  # -1 to 1

            # Adjust ball angle based on hit position
            angle = hit_position * 60  # Max 60 degree angle
            angle_rad = math.radians(angle)

            # Calculate new velocities
            speed = math.sqrt(ball.dx ** 2 + ball.dy ** 2)
            ball.dx = speed * math.sin(angle_rad)
            ball.dy = abs(speed * math.cos(angle_rad))  # Always go up

            ball.sety(-230)

            # Increase speed slightly with each paddle hit
            ball.speed = min(ball.speed * 1.02, 2)  # Cap speed at 2x

        # Ball collision with bricks
        for brick in bricks[:]:
            if ball.distance(brick) < 35:
                # Remove brick
                brick.hideturtle()
                bricks.remove(brick)

                # Update score
                score += 10
                score_display.clear()
                score_display.write(f"Score: {score}", align="left", font=("Courier", 16, "bold"))

                # Bounce ball
                ball.dy *= -1

                # Increase difficulty
                ball.speed = min(ball.speed * 1.01, 2)
                break

        # Check win condition
        if len(bricks) == 0:
            game_over = True
            game_over_display.color("green")
            game_over_display.write("YOU WIN!", align="center", font=("Courier", 36, "bold"))
            restart_display.write("Press SPACE to restart", align="center", font=("Courier", 20, "bold"))