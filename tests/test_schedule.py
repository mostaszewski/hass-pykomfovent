from custom_components.pykomfovent.schedule import (
    ScheduleEntry,
    ScheduleMode,
    ScheduleRow,
    build_schedule_commands,
    parse_schedule_config,
)


def test_schedule_entry() -> None:
    entry = ScheduleEntry(
        mode=ScheduleMode.NORMAL,
        start_hour=8,
        start_minute=30,
        stop_hour=22,
        stop_minute=0,
    )
    assert entry.start_minutes == 510
    assert entry.stop_minutes == 1320


def test_schedule_row_weekdays() -> None:
    row = ScheduleRow(weekday_mask=127, entries=[])
    assert row.weekdays == ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    row2 = ScheduleRow(weekday_mask=31, entries=[])  # Mon-Fri
    assert row2.weekdays == ["Mon", "Tue", "Wed", "Thu", "Fri"]


def test_parse_schedule_config() -> None:
    data = {
        "current_program": 0,
        "wmask": [127] + [0] * 15,
        "mode": [2, 3, 1, 1, 1] + [1] * 75,
        "start": [480, 1080, 0, 0, 0] + [0] * 75,  # 8:00, 18:00
        "stop": [1080, 1320, 0, 0, 0] + [0] * 75,  # 18:00, 22:00
    }

    schedules = parse_schedule_config(data)

    assert len(schedules) == 4
    assert len(schedules[0].rows) == 1
    assert schedules[0].rows[0].weekday_mask == 127
    assert len(schedules[0].rows[0].entries) == 2
    assert schedules[0].rows[0].entries[0].mode == ScheduleMode.NORMAL
    assert schedules[0].rows[0].entries[0].start_hour == 8
    assert schedules[0].rows[0].entries[1].mode == ScheduleMode.INTENSIVE


def test_build_schedule_commands() -> None:
    entries = [
        (2, 8, 0, 18, 0),  # normal 08:00-18:00
        (3, 18, 0, 22, 0),  # intensive 18:00-22:00
    ]

    commands = build_schedule_commands(0, 0, 127, entries)

    assert commands["700"] == 127  # weekday mask
    assert commands["620"] == 2  # mode entry 0
    assert commands["300"] == 480  # start entry 0 (8*60)
    assert commands["380"] == 1080  # stop entry 0 (18*60)
    assert commands["621"] == 3  # mode entry 1
    assert commands["301"] == 1080  # start entry 1
    assert commands["381"] == 1320  # stop entry 1 (22*60)
    # Remaining entries cleared
    assert commands["622"] == 1
    assert commands["302"] == 0
