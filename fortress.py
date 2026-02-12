import curses
import math
import time
import random

GRAVITY = 9.8
MAX_HP = 5
MAX_FUEL = 100
FUEL_COST = 5
CHAR_WIDTH = 3
MAX_POWER = 60
MIN_POWER = 5
MAX_PREVIEW_DIST = 20


class Player:
    def __init__(self, name, x, color):
        self.name = name
        self.x = x
        self.hp = MAX_HP
        self.angle = 45
        self.power = 25
        self.fuel = MAX_FUEL
        self.color = color
        self.item_id = None
        self.active_item = None
        self.trails = []   # 🔥 발사 후 탄도 저장


class Item:
    def __init__(self, x, itype):
        self.x = x
        self.itype = itype


class Mine:
    def __init__(self, x, owner):
        self.x = x
        self.turns_left = 3
        self.owner = owner


# ================= 탄도 계산 =================
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

        # 벽 반사
        if bounce:
            if ix <= 0 or ix >= width - 1:
                vx = -vx * 0.9
                bounce_count += 1
        else:
            if ix < 0 or ix >= width:
                break

        # 바닥 반사
        if iy >= ground_y - 1:
            if bounce and bounce_count < 10:
                vy = -vy * 0.9
                y = ground_y - 1
                bounce_count += 1
            else:
                break

        # 일반 미리보기 거리 제한
        if preview and not full_preview:
            dist = math.sqrt((x - shooter.x) ** 2 +
                             (y - (ground_y - 1)) ** 2)
            if dist > MAX_PREVIEW_DIST:
                break

        points.append((iy, ix))

    return points


# ================= 폭발 =================
def explosion(stdscr, y, x):
    for r in range(2):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                try:
                    stdscr.addstr(y + dy, x + dx, "*",
                                  curses.color_pair(3))
                except:
                    pass
        stdscr.refresh()
        time.sleep(0.05)


# ================= 발사 =================
def shoot(stdscr, shooter, target, width, ground_y, mines):

    item = shooter.item_id
    damage = 1
    paths = []

    # 멀티샷 (각도 그대로, 파워만 ±3씩 변화)
    if item == 1:
        power_offsets = [-3, -2, -1, 0, 1, 2, 3]  # 파워 변형
        for po in power_offsets:
            paths.append(
                calculate_path(
                    shooter,
                    shooter.angle,       # 각도는 그대로
                    shooter.power + po,  # 파워만 조정
                    width,
                    ground_y
                )
            )
    else:
        bounce = (item == 2)
        paths.append(
            calculate_path(
                shooter,
                shooter.angle,
                shooter.power,
                width,
                ground_y,
                bounce=bounce
            )
        )

    if not paths:
        return

    max_len = max(len(p) for p in paths)

    for i in range(max_len):
        for path in paths:
            if i < len(path):
                iy, ix = path[i]
                try:
                    stdscr.addstr(
                        iy, ix, "*",
                        curses.color_pair(3) | curses.A_BOLD
                    )
                except:
                    pass

                # 명중 판정
                if ground_y - 2 <= iy <= ground_y:
                    for ex in [ix - 1, ix, ix + 1]:
                        if target.x <= ex < target.x + CHAR_WIDTH:
                            explosion(stdscr, iy, ix)
                            target.hp -= damage
                            shooter.trails = paths
                            shooter.item_id = None
                            shooter.active_item = None
                            return

        stdscr.refresh()
        time.sleep(0.02)

        for path in paths:
            if i < len(path):
                iy, ix = path[i]
                try:
                    stdscr.addstr(iy, ix, " ")
                except:
                    pass

    # 지뢰 설치
    if item == 3 and paths[0]:
        mines.append(Mine(paths[0][-1][1], shooter.name))

    shooter.trails = paths
    shooter.item_id = None
    shooter.active_item = None


# ================= 화면 출력 =================
def draw(stdscr, p1, p2, current, item, mines):

    stdscr.clear()
    height, width = stdscr.getmaxyx()
    ground_y = height - 2

    # 🔥 이전 발사 트레일 (은색)
    for trail in current.trails:
        for iy, ix in trail:
            if 0 <= iy < height and 0 <= ix < width:
                try:
                    stdscr.addstr(
                        iy, ix, ".",
                        curses.color_pair(5) | curses.A_DIM
                    )
                except:
                    pass

    # 땅
    stdscr.attron(curses.color_pair(4))
    stdscr.addstr(ground_y, 0, "_" * (width - 1))
    stdscr.attroff(curses.color_pair(4))

    # 지뢰
    for m in mines:
        if 0 <= m.x < width:
            stdscr.addstr(
                ground_y - 1, m.x,
                "M", curses.color_pair(3)
            )

    # 아이템
    if item and 0 <= item.x < width:
        stdscr.addstr(
            ground_y - 1, item.x,
            "?", curses.color_pair(3) | curses.A_BLINK
        )

    # 🔥 탄도 미리보기
    preview = calculate_path(
        current,
        current.angle,
        current.power,
        width,
        ground_y,
        bounce=(current.item_id == 2),
        preview=True,
        full_preview=(current.item_id == 4)
    )

    for iy, ix in preview:
        if 0 <= iy < height and 0 <= ix < width:
            try:
                stdscr.addstr(
                    iy, ix, ".",
                    curses.color_pair(3)
                )
            except:
                pass

    # 플레이어
    if p1.hp > 0:
        stdscr.addstr(
            ground_y - 1, p1.x,
            "[1]", curses.color_pair(1) | curses.A_BOLD
        )

    if p2.hp > 0:
        stdscr.addstr(
            ground_y - 1, p2.x,
            "[2]", curses.color_pair(2) | curses.A_BOLD
        )

    # UI
    stdscr.addstr(
        0, 0,
        f"{current.name} TURN",
        curses.color_pair(current.color) | curses.A_BOLD
    )

    stdscr.addstr(
        1, 0,
        f"Angle: {current.angle} | Power: {current.power}"
    )

    stdscr.addstr(
        2, 0,
        f"Fuel: {current.fuel} | Item: {current.active_item or 'None'}"
    )

    stdscr.addstr(
        4, 0,
        f"P1 HP: {'♥' * max(0, p1.hp)}",
        curses.color_pair(1)
    )

    stdscr.addstr(
        5, 0,
        f"P2 HP: {'♥' * max(0, p2.hp)}",
        curses.color_pair(2)
    )

    stdscr.refresh()


# ================= 메인 =================
def main(stdscr):

    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 🔥 은색

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    height, width = stdscr.getmaxyx()

    p1 = Player("Player 1", 5, 1)
    p2 = Player("Player 2", width - 8, 2)

    turn = 0
    item = None
    mines = []

    while p1.hp > 0 and p2.hp > 0:

        current = p1 if turn % 2 == 0 else p2
        opponent = p2 if turn % 2 == 0 else p1
        current.fuel = MAX_FUEL

        if not item:
            item = Item(
                random.randint(10, width - 10),
                random.randint(1, 4)
            )

        while True:
            draw(stdscr, p1, p2, current, item, mines)
            key = stdscr.getch()

            # 이동
            if key in [ord('a'), ord('d')] and current.fuel >= FUEL_COST:
                move = -1 if key == ord('a') else 1
                current.x = max(
                    1,
                    min(width - CHAR_WIDTH - 1,
                        current.x + move)
                )
                current.fuel -= FUEL_COST

                # 아이템 획득
                if item and current.x <= item.x < current.x + CHAR_WIDTH:
                    current.item_id = item.itype
                    current.active_item = {
                        1: "Multi-Shot",
                        2: "Bouncy",
                        3: "Landmine",
                        4: "Full Guide"
                    }[item.itype]
                    item = None

                # 지뢰 밟기
                for m in mines[:]:
                    if current.x <= m.x < current.x + CHAR_WIDTH:
                        current.hp -= 1
                        mines.remove(m)

            elif key == curses.KEY_UP:
                current.power = min(MAX_POWER, current.power + 1)
            elif key == curses.KEY_DOWN:
                current.power = max(MIN_POWER, current.power - 1)
            elif key == curses.KEY_LEFT:
                current.angle = max(0, current.angle - 1)
            elif key == curses.KEY_RIGHT:
                current.angle = min(180, current.angle + 1)

            elif key == ord(' '):
                shoot(stdscr, current, opponent,
                      width, height - 2, mines)
                break

            time.sleep(0.01)

        turn += 1

    stdscr.clear()
    winner = "Player 1" if p1.hp > 0 else "Player 2"
    stdscr.addstr(
        height // 2,
        width // 2 - 10,
        f"{winner} WINS!",
        curses.A_BOLD
    )
    stdscr.refresh()
    time.sleep(3)


if __name__ == "__main__":
    curses.wrapper(main)
