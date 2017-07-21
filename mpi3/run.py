from _old_main import Player
import time

DELAY = 0.5
p = Player()

for _ in range(20):
    p.move_cursor(1)
    p.screen.render()
    time.sleep(DELAY)

for _ in range(20):
    p.move_cursor(-1)
    p.screen.render()
    time.sleep(DELAY)
