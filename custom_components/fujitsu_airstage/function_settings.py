"""Descriptions of indoor unit function settings (installer settings).

Source: Fujitsu service manual for ASEH..KMCG wall-mounted units, chapter
"Function settings", plus functions 43 and 95 from other Airstage manuals
(95: AUU..RLF service manual; setting it resets 30, 31, 92 and 93 to
"No correction"), and function 33 from the Fujitsu General Australia note
for the ARTG..LHTA ducted range (same meaning observed on wall units).
Other Airstage indoor units use the same numbers for the same functions,
but not every unit supports every value.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FunctionSetting:
    """A function setting and the meaning of its values."""

    name: str
    values: dict[int, str]


# Room temperature correction. The service manual defines
# corrected = sensor - correction, relative to the Standard setting (00):
# a negative value makes the unit read higher (more cooling, less heating).
_CORRECTION: dict[int, str] = {
    0: "Standard setting",
    1: "No correction 0.0 °C",
    **{
        n: f"-{(n - 1) * 0.5:.1f} °C (more cooling, less heating)"
        for n in range(2, 10)
    },
    **{
        n: f"+{(n - 9) * 0.5:.1f} °C (less cooling, more heating)"
        for n in range(10, 18)
    },
}

FUNCTION_SETTING_INFO: dict[int, FunctionSetting] = {
    0: FunctionSetting(
        "Remote controller address",
        {n: f"Unit no. {n}" for n in range(16)},
    ),
    11: FunctionSetting(
        "Filter sign",
        {
            0: "Standard interval",
            1: "Long interval",
            2: "Short interval",
            3: "No indication",
        },
    ),
    30: FunctionSetting(
        "Room temperature correction indoor unit sensor (cooling)", _CORRECTION
    ),
    31: FunctionSetting(
        "Room temperature correction indoor unit sensor (heating)", _CORRECTION
    ),
    33: FunctionSetting(
        "Heating thermostat-off indoor fan control",
        {
            0: "Intermittent, stop 6/10/17 min",
            1: "Intermittent, stop 6 min",
            2: "Intermittent short, stop 4/6/10 min",
            3: "Intermittent long, stop 8/15/27 min",
            4: "Fan stop",
            5: "Continuous",
        },
    ),
    35: FunctionSetting(
        "Room temperature correction wired remote sensor (cooling)", _CORRECTION
    ),
    36: FunctionSetting(
        "Room temperature correction wired remote sensor (heating)", _CORRECTION
    ),
    40: FunctionSetting("Auto restart", {0: "Enable", 1: "Disable"}),
    42: FunctionSetting(
        "Room temperature sensor switching", {0: "Indoor unit", 1: "Both"}
    ),
    43: FunctionSetting("Cold air prevention", {0: "Enable", 1: "Disable"}),
    44: FunctionSetting(
        "Remote controller custom code", {0: "A", 1: "B", 2: "C", 3: "D"}
    ),
    46: FunctionSetting(
        "External input control",
        {
            0: "Operation/Stop mode 1 (remote controller enabled)",
            1: "Setting prohibited",
            2: "Forced stop mode",
            3: "Operation/Stop mode 2 (remote controller disabled)",
        },
    ),
    48: FunctionSetting(
        "Room temperature sensor switching (Aux.)",
        {0: "Both", 1: "Wired remote controller"},
    ),
    49: FunctionSetting(
        "Indoor fan control for energy saving (cooling)",
        {0: "Disable", 1: "Enable", 2: "Remote controller"},
    ),
    60: FunctionSetting(
        "External output terminal function",
        {
            0: "Operation status",
            **{n: "Setting prohibited" for n in range(1, 9)},
            9: "Error status",
            10: "Indoor unit fan operation status",
            11: "Setting prohibited",
        },
    ),
    95: FunctionSetting(
        "Heat insulation condition (building insulation)",
        {
            0: "Standard insulation",
            1: "High insulation (less overshoot at start-up)",
        },
    ),
}


def describe_value(number: int, value: int | None) -> str | None:
    """Return 'NN - meaning' for a function setting value, code always shown."""
    if value is None:
        return None
    info = FUNCTION_SETTING_INFO.get(number)
    meaning = info.values.get(value) if info else None
    return f"{value:02d} - {meaning}" if meaning else f"{value:02d}"
