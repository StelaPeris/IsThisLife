#ifdef ROLE_CONTROLLER

#include <esp_now.h>
#include <WiFi.h>
#include "esp_wifi.h"
#include "packets.h"
#include "controller_config.h"
#include "robot_telemetry.h"
#include "python_comm.h"
#include "robot_commands.h"
#include "serial_parser.h"
#include "espnow_handler.h"
#include "peer_management.h"
// #include "heartbeat_manager.h" // Removed to stop auto-heartbeats

// Robot MAC addresses (defined in controller_config.h)
uint8_t robotMacs[NUM_ROBOTS][6] = {
    {0x28, 0x05, 0XA5, 0X6F, 0x3B, 0xF8}
};

// Heartbeat counter
uint8_t heartbeatCounter = 0;

// Heartbeat timing tracking
uint32_t heartbeatSentTime[NUM_ROBOTS][MAX_HEARTBEAT];

// -------------------- Setup --------------------
void roleSetup() {
    Serial.begin(115200);
    Serial.setTimeout(5);
    delay(500);
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    delay(100);
    esp_wifi_set_channel(CHANNEL, WIFI_SECOND_CHAN_NONE);

    if (esp_now_init() != ESP_OK) return;
    esp_now_register_recv_cb(onRobotReceive);
    delay(100);

    // Print own MAC address
    Serial.print("Controller MAC address: ");
    Serial.println(WiFi.macAddress());

    // Connect to all robots as peers
    connectToAllPeers();

    Serial.println("Controller setup complete. Periodic heartbeats DISABLED.");
}

// -------------------- Loop --------------------
void roleLoop() {
    // Read commands from Python
    readSerialCommands();

    // Check for Python timeout and handle disconnection
    checkPythonTimeout();

    // REMOVED: Periodic heartbeat sending
    // sendPeriodicHeartbeat(); 
}

#endif // ROLE_CONTROLLER