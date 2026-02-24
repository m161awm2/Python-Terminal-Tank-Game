import math
from config import GRAVITY, MAX_PREVIEW_DIST


def calculate_path(shooter, angle_deg, power, width, ground_y,
                   bounce=False, preview=False, full_preview=False):

    angle = math.radians(angle_deg)
    direction = 1 if shooter.x < width // 2 else -1

    vx = power * math.cos(angle) * direction
    vy = power * math.sin(angle)

    x = shooter.x + 1
    y = ground_y - 1

    dt = 0.08
    points = []
    bounce_count = 0

    while True:
        vy -= GRAVITY * dt
        x += vx * dt
        y -= vy * dt

        ix, iy = int(x), int(y)

        if iy < 0:
            break

        if bounce:
            if ix <= 0 or ix >= width - 1:
                vx = -vx * 0.9
                bounce_count += 1
        else:
            if ix < 0 or ix >= width:
                break

        if iy >= ground_y - 1:
            if bounce and bounce_count < 10:
                vy = -vy * 0.9
                y = ground_y - 1
                bounce_count += 1
            else:
                break

        if preview and not full_preview:
            dist = math.sqrt((x - shooter.x) ** 2 +
                             (y - (ground_y - 1)) ** 2)
            if dist > MAX_PREVIEW_DIST:
                break

        points.append((iy, ix))

    return points