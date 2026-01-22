import pytest
from pykomfovent.parser import KomfoventParseError, parse_state


def test_parse_state_full() -> None:
    main_xml = b"""<?xml version="1.0"?>
    <data>
        <OMO>NORMALNY</OMO>
        <AI0>21.5</AI0>
        <AI1>23.0</AI1>
        <AI2>5.0</AI2>
        <ST>21.0</ST>
        <SAF>50</SAF>
        <EAF>50</EAF>
        <FCG>47</FCG>
        <VF>0</VF>
        <EC1>90</EC1>
        <EC2>1500</EC2>
        <EC3>150</EC3>
        <EC4>0</EC4>
        <EC5A>0.35</EC5A>
        <EC5D>0.32</EC5D>
        <EC6D>2.5</EC6D>
        <EC6M>75.0</EC6M>
        <EC6T>1500.0</EC6T>
        <EC7D>0.5</EC7D>
        <EC7M>15.0</EC7M>
        <EC7T>300.0</EC7T>
        <EC8D>5.0</EC8D>
        <EC8M>150.0</EC8M>
        <EC8T>3000.0</EC8T>
        <AQ>1</AQ>
        <AH>45</AH>
    </data>"""

    detail_xml = b"""<?xml version="1.0"?>
    <data>
        <SFI>50</SFI>
        <EFI>50</EFI>
        <HE>85</HE>
        <EH>0</EH>
    </data>"""

    state = parse_state(main_xml, detail_xml)

    assert state.mode == "NORMALNY"
    assert state.supply_temp == 21.5
    assert state.extract_temp == 23.0
    assert state.outdoor_temp == 5.0
    assert state.supply_temp_setpoint == 21.0
    assert state.supply_fan_percent == 50
    assert state.extract_fan_percent == 50
    assert state.filter_contamination == 47
    assert state.heat_exchanger_percent == 85
    assert state.heat_exchanger_efficiency == 90
    assert state.heat_recovery_power == 1500
    assert state.power_consumption == 150
    assert state.energy_consumed_daily == 2.5
    assert state.energy_recovered_total == 3000.0


def test_parse_state_minimal() -> None:
    main_xml = b"""<?xml version="1.0"?>
    <data>
        <OMO>OFF</OMO>
    </data>"""

    detail_xml = b"""<?xml version="1.0"?><data></data>"""

    state = parse_state(main_xml, detail_xml)

    assert state.mode == "OFF"
    assert state.supply_temp is None


def test_parse_state_invalid_xml() -> None:
    with pytest.raises(KomfoventParseError):
        parse_state(b"not xml", b"")
