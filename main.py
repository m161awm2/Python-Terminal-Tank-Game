import curses
import random
import time

from entities import Player, Item
from render import draw
from combat import shoot
from config import *


def main(stdscr):

    # ================= curses 설정 =================
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    height, width = stdscr.getmaxyx()

    # ================= 플레이어 생성 =================
    p1 = Player("Player 1", 5, 1)
    p2 = Player("Player 2", width - 8, 2)

    turn = 0
    item = None
    mines = []

    # ================= 게임 루프 =================
    while p1.hp > 0 and p2.hp > 0:

        current = p1 if turn % 2 == 0 else p2
        opponent = p2 if turn % 2 == 0 else p1

        current.fuel = MAX_FUEL

        # 아이템 스폰
        if not item:
            item = Item(
                random.randint(10, width - 10),
                random.randint(1, 5)
            )

        # ================= 턴 루프 =================
        while True:
            draw(stdscr, p1, p2, current, item, mines)

            key = stdscr.getch()

            # ===== 이동 =====
            if key in [ord('a'), ord('d')] and current.fuel >= FUEL_COST:

                move = -1 if key == ord('a') else 1

                current.x = max(
                    1,
                    min(width - CHAR_WIDTH - 1,
                        current.x + move)
                )

                current.fuel -= FUEL_COST

                # ⭐ 아이템 획득
                if item and current.x <= item.x < current.x + CHAR_WIDTH:
                    current.item_id = item.itype
                    current.active_item = {
                        1: "Multi-Shot",
                        2: "Bouncy",
                        3: "Landmine",
                        4: "Full Guide",
                        5: "Trigger Drop"
                    }[item.itype]
                    item = None

                # ⭐ 지뢰 밟기
                for m in mines[:]:
                    if current.x <= m.x < current.x + CHAR_WIDTH:
                        current.hp -= 1
                        mines.remove(m)

            # ===== 파워 조절 =====
            elif key == curses.KEY_UP:
                current.power = min(MAX_POWER, current.power + 1)

            elif key == curses.KEY_DOWN:
                current.power = max(MIN_POWER, current.power - 1)

            # ===== 각도 조절 =====
            elif key == curses.KEY_LEFT:
                current.angle = max(0, current.angle - 1)

            elif key == curses.KEY_RIGHT:
                current.angle = min(180, current.angle + 1)

            # ===== 발사 =====
            elif key == ord(' '):
                shoot(
                    stdscr,
                    current,
                    opponent,
                    width,
                    height - 2,
                    mines
                )
                break

            time.sleep(0.01)

        turn += 1

    # ================= 게임 종료 =================
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


# ================= 실행 =================
if __name__ == "__main__":
    curses.wrapper(main)