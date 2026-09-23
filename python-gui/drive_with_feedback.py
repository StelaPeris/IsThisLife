"""
Slanje brzine + čitanje telemetrije, da vidiš ZAŠTO se robot (ne) miče.

Pokreni iz python-gui/:
    cd python-gui
    python drive_with_feedback.py

Robot izvršava brzinu SAMO ako je (iz packet_handler.cpp):
  not E-STOP  AND  heartbeat valid  AND  calibrated  AND  not in sequence.
Ako se ne miče, telemetrija ispod će ti pokazati status (E-STOP bit, mode, error).

Status bajt (packets.h):
  bit 0x80 = E-STOP aktivan
  donjih 7 bita: 0=NORMAL, 2=WAITING_CONFIRM, 3=SEQUENCE, 4=CALIBRATION_REQUIRED
"""
import time
import serial_comm
import packet_sender
from config import BAUD_RATE
from telemetry_parser import TelemetryParser, TelemetryData

PORT = "/dev/ttyUSB0"
ROBOT_ID = 1
MODE = 1   # 0 = DIRECT (vx -> glavni motor), 1 = STABILIZED

parser = TelemetryParser()

def pump_telemetry():
    """Pročitaj sve što je stiglo i vrati zadnji TelemetryData (ili None)."""
    raw = serial_comm.read_all()
    last = None
    if raw:
        for pkt in parser.process_bytes(raw):
            if isinstance(pkt, TelemetryData) and pkt.robot_id == ROBOT_ID:
                last = pkt
    return last

def describe(t):
    estop = "E-STOP" if (t.status & 0x80) else "clear"
    state = {0:"NORMAL",2:"WAIT_CONFIRM",3:"SEQUENCE",4:"CALIB_REQ"}.get(t.status & 0x7F, t.status & 0x7F)
    return (f"status={estop}/{state} mode={t.mode} "
            f"batt={t.battery_mv/1000:.2f}V temp={t.motor_temp}C err=0x{t.error_flags:02X}")

def main():
    if not serial_comm.connect(PORT, BAUD_RATE):
        print("Ne mogu se spojiti na", PORT); return
    print("Spojen.")
    time.sleep(0.3)

    # 1) Prvo par sekundi šalji NULU da heartbeat postane valjan (bez ovoga
    #    robot ostane u E-STOP-u od gubitka veze pri odspajanju GUI-a).
    print("Uspostavljam heartbeat (šaljem 0)...")
    t_end = time.time() + 1.5
    while time.time() < t_end:
        packet_sender.send_control(ROBOT_ID, MODE, 0.0, 0.0, 0.0)
        pump_telemetry()
        time.sleep(0.05)

    # 2) Očisti E-STOP (arm), pa nastavi slati 0 da clear "sjedne"
    packet_sender.send_arm(ROBOT_ID)
    print("Poslan ARM (E-STOP clear).")
    t_end = time.time() + 1.5
    last = None
    while time.time() < t_end:
        packet_sender.send_control(ROBOT_ID, MODE, 0.0, 0.0, 0.0)
        got = pump_telemetry()
        if got: last = got
        time.sleep(0.05)

    if last:
        print("Stanje nakon arma:", describe(last))
        if last.status & 0x80:
            print(">>> ROBOT JE JOŠ U E-STOP-u. Neće se micati.")
            print(">>> Provjeri: je li kalibriran? error flags? baterija 14.8-17.0V?")
    else:
        print(">>> Ne stiže telemetrija - provjeri vezu kontroler<->robot.")

    # 3) Sad stvarno vozi naprijed (vx). Gledaj mode/status uz svaki paket.
    print("Naprijed 0.4 (3 s)...")
    t_end = time.time() + 3.0
    while time.time() < t_end:
        packet_sender.send_control(ROBOT_ID, MODE, -0.4, 0.0, 0.0)
        got = pump_telemetry()
        if got:
            print("  ", describe(got))
        time.sleep(0.1)

    # 4) Stop + E-STOP
    for _ in range(10):
        packet_sender.send_control(ROBOT_ID, MODE, 0.0, 0.0, 0.0)
        time.sleep(0.02)
    packet_sender.send_estop(ROBOT_ID)
    serial_comm.disconnect()
    print("Gotovo, zaustavljeno.")

if __name__ == "__main__":
    main()
