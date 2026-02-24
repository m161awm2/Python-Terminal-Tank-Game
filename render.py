import curses
from physics import calculate_path


def draw(stdscr, p1, p2, current, item, mines):

    stdscr.clear()
    height, width = stdscr.getmaxyx()
    ground_y = height - 2

    for trail in current.trails:
        for iy, ix in trail:
            try:
                stdscr.addstr(
                    iy, ix, ".",
                    curses.color_pair(5) | curses.A_DIM
                )
            except:
                pass

    stdscr.attron(curses.color_pair(4))
    stdscr.addstr(ground_y, 0, "_" * (width - 1))
    stdscr.attroff(curses.color_pair(4))

    for m in mines:
        stdscr.addstr(ground_y - 1, m.x,
                      "M", curses.color_pair(3))

    if item:
        stdscr.addstr(ground_y - 1, item.x,
                      "?", curses.color_pair(3) | curses.A_BLINK)

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
        try:
            stdscr.addstr(iy, ix, ".", curses.color_pair(3))
        except:
            pass

    if p1.hp > 0:
        stdscr.addstr(ground_y - 1, p1.x,
                      "[1]", curses.color_pair(1) | curses.A_BOLD)

    if p2.hp > 0:
        stdscr.addstr(ground_y - 1, p2.x,
                      "[2]", curses.color_pair(2) | curses.A_BOLD)

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

    stdscr.addstr(4, 0, f"P1 HP: {'♥'*max(0,p1.hp)}",
                  curses.color_pair(1))
    stdscr.addstr(5, 0, f"P2 HP: {'♥'*max(0,p2.hp)}",
                  curses.color_pair(2))

    stdscr.refresh()