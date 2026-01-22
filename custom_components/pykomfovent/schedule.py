from dataclasses import dataclass
from enum import IntEnum


class ScheduleMode(IntEnum):
    AWAY = 1
    NORMAL = 2
    INTENSIVE = 3
    BOOST = 4


@dataclass
class ScheduleEntry:
    mode: ScheduleMode
    start_hour: int
    start_minute: int
    stop_hour: int
    stop_minute: int

    @property
    def start_minutes(self) -> int:
        return self.start_hour * 60 + self.start_minute

    @property
    def stop_minutes(self) -> int:
        return self.stop_hour * 60 + self.stop_minute


@dataclass
class ScheduleRow:
    weekday_mask: int
    entries: list[ScheduleEntry]

    @property
    def weekdays(self) -> list[str]:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return [days[i] for i in range(7) if self.weekday_mask & (1 << i)]


@dataclass
class Schedule:
    program: int
    rows: list[ScheduleRow]


PROGRAMS = 4
ROWS_PER_PROGRAM = 4
ENTRIES_PER_ROW = 5
TOTAL_ROWS = PROGRAMS * ROWS_PER_PROGRAM
TOTAL_ENTRIES = TOTAL_ROWS * ENTRIES_PER_ROW


def parse_schedule_config(data: dict) -> list[Schedule]:
    schedules = []

    for prog in range(PROGRAMS):
        rows = []
        for row_idx in range(ROWS_PER_PROGRAM):
            global_row = prog * ROWS_PER_PROGRAM + row_idx
            wmask = data["wmask"][global_row]

            if wmask == 0:
                continue

            entries = []
            for entry_idx in range(ENTRIES_PER_ROW):
                global_entry = global_row * ENTRIES_PER_ROW + entry_idx
                mode = data["mode"][global_entry]
                start = data["start"][global_entry]
                stop = data["stop"][global_entry]

                if start == 0 and stop == 0 and mode == 1:
                    continue

                entries.append(
                    ScheduleEntry(
                        mode=ScheduleMode(mode),
                        start_hour=start // 60,
                        start_minute=start % 60,
                        stop_hour=stop // 60,
                        stop_minute=stop % 60,
                    )
                )

            if entries or wmask:
                rows.append(ScheduleRow(weekday_mask=wmask, entries=entries))

        schedules.append(Schedule(program=prog, rows=rows))

    return schedules


def build_schedule_commands(
    program: int,
    row: int,
    weekday_mask: int,
    entries: list[tuple[int, int, int, int, int]],
) -> dict[str, int]:
    commands: dict[str, int] = {}
    global_row = program * ROWS_PER_PROGRAM + row

    commands[str(700 + global_row)] = weekday_mask

    for i, (mode, start_h, start_m, stop_h, stop_m) in enumerate(entries):
        if i >= ENTRIES_PER_ROW:
            break
        global_entry = global_row * ENTRIES_PER_ROW + i
        commands[str(620 + global_entry)] = mode
        commands[str(300 + global_entry)] = start_h * 60 + start_m
        commands[str(380 + global_entry)] = stop_h * 60 + stop_m

    for i in range(len(entries), ENTRIES_PER_ROW):
        global_entry = global_row * ENTRIES_PER_ROW + i
        commands[str(620 + global_entry)] = 1
        commands[str(300 + global_entry)] = 0
        commands[str(380 + global_entry)] = 0

    return commands
