import curses
import time
from physics import calculate_path
from entities import Mine
from config import CHAR_WIDTH


# ================= 폭발 이펙트 =================
def explosion(stdscr, y, x):
    for r in range(2):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                try:
                    stdscr.addstr(
                        y + dy,
                        x + dx,
                        "*",
                        curses.color_pair(3)
                    )
                except:
                    pass

        stdscr.refresh()
        time.sleep(0.05)


# ================= 발사 로직 =================
def shoot(stdscr, shooter, target, width, ground_y, mines):

    item = shooter.item_id
    damage = 1
    paths = []

    # ⭐ Trigger Drop 아이템
    trigger_mode = (item == 5)

    # ================= 멀티샷 =================
    if item == 1:
        for po in [-3, -2, -1, 0, 1, 2, 3]:
            paths.append(
                calculate_path(
                    shooter,
                    shooter.angle,
                    shooter.power + po,
                    width,
                    ground_y
                )
            )

    # ================= 일반 / 바운스 =================
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

    # ================= 탄 이동 루프 =================
    for i in range(max_len):

        # ===== Trigger Drop 입력 감지 =====
        if trigger_mode:
            key = stdscr.getch()

            if key == ord(' '):
                if i < len(paths[0]):

                    drop_y, drop_x = paths[0][i]

                    # 수직 낙하
                    while drop_y < ground_y:
                        drop_y += 1
                        try:
                            stdscr.addstr(
                                drop_y,
                                drop_x,
                                "|",
                                curses.color_pair(3) | curses.A_BOLD
                            )
                        except:
                            pass

                        stdscr.refresh()
                        time.sleep(0.01)

                    #explosion(stdscr, drop_y, drop_x)

                    # 데미지 판정
                    DROP_RADIUS = 3   # ← 원하는 범위

                    for ex in range(drop_x - DROP_RADIUS, drop_x + DROP_RADIUS + 1):
                        if target.x <= ex < target.x + CHAR_WIDTH:
                            target.hp -= 1
                            break
                        

                    shooter.trails = paths
                    shooter.item_id = None
                    shooter.active_item = None
                    return

        # ===== 탄 그리기 =====
        for path in paths:
            if i < len(path):
                iy, ix = path[i]

                try:
                    stdscr.addstr(
                        iy,
                        ix,
                        "*",
                        curses.color_pair(3) | curses.A_BOLD
                    )
                except:
                    pass

                # ===== 충돌 판정 =====
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

        # ===== 탄 지우기 =====
        for path in paths:
            if i < len(path):
                iy, ix = path[i]
                try:
                    stdscr.addstr(iy, ix, " ")
                except:
                    pass

    # ================= 지뢰 아이템 =================
    if item == 3 and paths[0]:
        mines.append(Mine(paths[0][-1][1], shooter.name))

    shooter.trails = paths
    shooter.item_id = None
    shooter.active_item = None