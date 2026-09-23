import time
import vgamepad as vg

class VirtualRobotController:
    def __init__(self):
        print("Initializing Virtual Xbox 360 Controller...")
        self.gamepad = vg.VX360Gamepad()
        # Give the OS a moment to register the new virtual hardware
        time.sleep(1.0) 
        print("Virtual Controller Ready! You can now assign it in the Dashboard.")

    def update(self):
        """Pushes the current state to the virtual gamepad."""
        self.gamepad.update()

    def set_movement(self, vx=0.0, vy=0.0, omega=0.0):
        """
        Sets the joystick axes for movement.
        Values must be floats between -1.0 and 1.0.
        """
        def to_int(val):
            return int(max(-1.0, min(1.0, val)) * 32767)

        # Left joystick: X controls Omega (Rotation), Y controls VX (Forward/Back)
        self.gamepad.left_joystick(x_value=to_int(omega), y_value=to_int(vx))
  
        # Right joystick: X controls VY (Strafe)
        self.gamepad.right_joystick(x_value=to_int(vy), y_value=0)
        self.update()

    def press_button(self, button_name, duration=0.1):
        """Presses a specific button mapped to the robot's functions."""
        buttons = self._get_button_map()
        if button_name in buttons:
            self.gamepad.press_button(button=buttons[button_name])
            self.update()
            time.sleep(duration)
            self.gamepad.release_button(button=buttons[button_name])
            self.update()
        else:
            print(f"Unknown button: {button_name}")

    def hold_button(self, button_name):
        """Holds a button down (e.g., for Cruise Control)."""
        buttons = self._get_button_map()
        if button_name in buttons:
            self.gamepad.press_button(button=buttons[button_name])
            self.update()

    def release_button(self, button_name):
        """Releases a held button."""
        buttons = self._get_button_map()
        if button_name in buttons:
            self.gamepad.release_button(button=buttons[button_name])
            self.update()
    
    def _get_button_map(self):
        return {
            "ESTOP": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            "ARM": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            "CRUISE": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            "MODE_SWITCH": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER
        }

# ==========================================
# Example Usage / Test Sequence
# ==========================================
if __name__ == "__main__":
    controller = VirtualRobotController()
  
    print("Arming robot...")
    controller.press_button("ARM")
    time.sleep(5)

    print("Driving Forward...")
    controller.set_movement(vx=0.5, vy=0.0, omega=0.0)
    time.sleep(5)

    print("Stopping...")
    controller.set_movement(vx=0.0, vy=0.0, omega=0.0)
    time.sleep(5)
  
    print("Disarming...")
    controller.press_button("ARM")

    while True:
        time.sleep(1)
