"""
Cita telemetriju s robota i ispisuje SVE dostupne vrijednosti:
kutove tijela (Main Body) i penduluma, bateriju, temperaturu, status, itd.

Pokreni iz python-gui/:
    cd python-gui
    python read_robot_telemetry.py
"""
import time
import dataclasses

import serial_comm
import packet_sender
from config import BAUD_RATE
from telemetry_parser import TelemetryParser, TelemetryData

PORT = "/dev/ttyUSB0"
ROBOT_ID = 1
MODE = 1   # samo za heartbeat; ne pomicemo se (saljemo 0,0,0)

parser = TelemetryParser()


def latest_telemetry():
    """Procitaj sve pristigle bajtove i vrati zadnji TelemetryData za naseg robota."""
    raw = serial_comm.read_all()
    last = None
    if raw:
        for pkt in parser.process_bytes(raw):
            if isinstance(pkt, TelemetryData) and getattr(pkt, "robot_id", ROBOT_ID) == ROBOT_ID:
                last = pkt
    return last


def dump(t):
    """Ispisi SVA polja TelemetryData, bez obzira na tocne nazive."""
    if dataclasses.is_dataclass(t):
        fields = [f.name for f in dataclasses.fields(t)]
    elif hasattr(t, "__dict__"):
        fields = list(vars(t))
    else:
        fields = [a for a in dir(t) if not a.startswith("_")]

    print("---- SVA POLJA ----")
    for name in fields:
        try:
            val = getattr(t, name)
        except Exception:
            continue
        if callable(val):
            continue
        print(f"  {name:24s} = {val}")

    # Izvedeni sazetak (imena iz packets.h / Live View); g() proba vise varijanti
    def g(*names):
        for n in names:
            if hasattr(t, n):
                return getattr(t, n)
        return None

    print("---- SAZETAK ----")
    status = g("status")
    if status is not None:
        print(f"  E-STOP aktivan?   {bool(status & 0x80)}   (status=0x{status:02X})")
    print(f"  Mode:             {g('mode')}")
    print(f"  Baterija:         {g('battery_mv','battery')}")
    print(f"  Temperatura:      {g('motor_temp','temp','temperature')}")
    print(f"  Error flags:      {g('error_flags','error')}")
    print(f"  Body  Roll/Pitch: {g('body_roll','main_roll')} / {g('body_pitch','main_pitch')}")
    print(f"  Pend. Roll/Pitch: {g('pend_roll','pendulum_roll')} / {g('pend_pitch','pendulum_pitch')}")
    print()


def main():
    if not serial_comm.connect(PORT, BAUD_RATE):
        print("Ne mogu se spojiti na", PORT)
        return
    print("Spojen na", PORT, "- citam telemetriju (Ctrl+C za stop)\n")
    time.sleep(0.3)
    try:
        last_print = 0
        while True:
            packet_sender.send_control(ROBOT_ID, MODE, 0.0, 0.0, 0.0)  # heartbeat
            t = latest_telemetry()
            now = time.time()
            if t is not None and (now - last_print) > 0.5:
                dump(t)
                last_print = now
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStop.")
    finally:
        serial_comm.disconnect()


if __name__ == "__main__":
    main()