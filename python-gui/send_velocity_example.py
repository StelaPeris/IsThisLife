"""
Primjer: slanje brzine robotu izvan GUI-a.

Pokreni iz python-gui/ direktorija (da nađe config, serial_comm, packet_sender):
    cd python-gui
    python send_velocity_example.py

VAŽNO: robot mora biti KALIBRIRAN i ARMED (E-STOP očišćen) da bi se motori
pomaknuli. Skripta zato prvo šalje 'arm' (PACKET_ESTOP_CLEAR).
Robot iz sigurnosti zaustavlja motore ako ne prima pakete ~stalno, pa se
brzina mora slati u petlji (ne jednom).
"""
import time
import serial_comm
import packet_sender
from config import BAUD_RATE

PORT = "/dev/ttyUSB0"   # tvoj kontroler
ROBOT_ID = 1            # isti ID koji vidiš u Live View (Robot 1)
MODE = 1               # 0 = DIRECT, 1 = STABILIZED

def main():
    # 1) Spoji se na kontroler
    if not serial_comm.connect(PORT, BAUD_RATE):
        print("Ne mogu se spojiti na", PORT)
        return
    print("Spojen na", PORT)
    time.sleep(0.5)

    # 2) Armiraj (očisti E-STOP). Robot mora biti prethodno kalibriran!
    packet_sender.send_arm(ROBOT_ID)
    print("Poslan ARM (E-STOP clear). Provjeri da Live View pokazuje ARMED.")
    time.sleep(1.0)

    try:
        # 3) Vozi naprijed pola gasa 3 sekunde.
        #    vx/vy/omega su u rasponu -1.0 .. +1.0 (0.0 = stop)
        #    vx=naprijed/nazad, vy=strafe, omega=rotacija
        print("Naprijed 0.5 ...")
        t_end = time.time() + 3.0
        while time.time() < t_end:
            packet_sender.send_control(ROBOT_ID, MODE, vx=0.5, vy=0.0, omega=0.0)
            time.sleep(0.05)   # ~20 Hz; šalji stalno, ne jednom


    finally:
        # 5) UVIJEK zaustavi na kraju (i pri prekidu Ctrl+C)
        for _ in range(10):
            packet_sender.send_control(ROBOT_ID, MODE, 0.0, 0.0, 0.0)
            time.sleep(0.02)
        print("Zaustavljeno.")
        # Po želji ponovno u E-STOP radi sigurnosti:
        packet_sender.send_estop(ROBOT_ID)
        serial_comm.disconnect()

if __name__ == "__main__":
    main()