# STM32F401RE – ESP32 FOTA System (Jenkins-Driven, STM32-Verified CRC)

A robust Firmware Over-The-Air (FOTA) update system designed for embedded devices using an **STM32F401RE** microcontroller with an **ESP32** acting as a Wi-Fi gateway. The update process is **automated via Jenkins**, which responds to binary file pushes to GitHub, calculates the CRC32 checksum, and publishes MQTT notifications to trigger the ESP32 to download and transfer firmware. The STM32 is responsible for validating the firmware’s integrity before flashing, ensuring secure and reliable updates.

## Features

* **Automated Jenkins pipeline** that triggers on GitHub binary pushes, calculates CRC32, and sends MQTT update messages.  
* **MQTT-based signaling** using Mosquitto broker for update notifications.  
* **ESP32 gateway** downloads firmware over Wi-Fi and streams it via UART to STM32.  
* **STM32 performs CRC32 verification** on the received firmware before flashing.  
* Secure, reliable firmware updates without physical access.  
* Supports integration with existing GitHub workflows and CI/CD pipelines.

## Project Structure

.
├── esp32/ # ESP32 firmware

├── stm32f401re/ # STM32 firmware (STM32CubeIDE)
│ ├── Src/
│ ├── Inc/
│ └── .ioc # STM32CubeMX config
│
├── jenkins/ # Jenkins scripts and pipeline config
│ ├── Jenkinsfile
│ └── crc_script.py # Example CRC calculation script
│
└── README.md

## Hardware Requirements

* **STM32F401RE Nucleo board** (or equivalent STM32F4 series).  
* **ESP32 development board** with Wi-Fi.  
* **Mosquitto MQTT broker** (local or cloud).  
* USB cables and jumpers for UART and programming.  
* ST-Link or compatible programmer for STM32.  
* Power supply for boards (usually 5V).

## How It Works

### 1. Binary Push to GitHub

* The developer builds the STM32 firmware binary (`new_application.bin`) locally or in any environment and pushes it to a **dedicated GitHub repository** (e.g., this Fota_Project repo).

### 2. Jenkins Pipeline Trigger

* Jenkins monitors the GitHub repository via webhook.  
* When a new binary is pushed, Jenkins:  
  * Downloads the `.bin` file.  
  * Calculates the **CRC32 checksum** using the `crc_script.py` or equivalent method.  
  * Publishes two MQTT messages to the Mosquitto broker:  
    * Firmware availability (`fota/firmware/status`: `"available"`)  
    * CRC checksum (`fota/firmware/crc`: e.g., `"FED78FB8"`)

### 3. ESP32 Receives MQTT Notification

* ESP32 subscribes to the relevant MQTT topics.  
* On receiving `"available"`, ESP32 fetches the new firmware `.bin` from GitHub raw URL or another HTTP server.

### 4. ESP32 Transfers Firmware via UART

* ESP32 streams the downloaded firmware in chunks over UART to STM32.

### 5. STM32 Performs CRC Verification

* STM32 computes CRC32 on the received data.  
* Compares it to the CRC sent by Jenkins (relayed via ESP32 or MQTT).  
* Only if CRC matches, STM32 writes the firmware to flash memory.  
* STM32 then safely reboots into the updated firmware.

## Jenkins Pipeline Overview

* **Trigger:** Push binary firmware `.bin` file to GitHub.  
* **Steps:**  
  * Retrieve the latest binary `.bin` pushed to GitHub.  
  * Calculate CRC32 checksum on `.bin`.  
  * Publish MQTT messages to signal firmware availability and CRC.

![Pipeline Overview](https://github.com/user-attachments/assets/c055a836-e8fb-42a2-8ba6-1680aa520eec)

---

## MQTT Topics and Messages

| Topic                  | Payload      | Description                                               |
| ---------------------- | ------------ | --------------------------------------------------------- |
| `fota/firmware/status` | `available`  | Signals new firmware availability.                        |
| `fota/firmware/crc`    | `FED78FB8`   | CRC32 checksum (hex) for integrity check.                 |
| `update_status`        | `success`    | Indicates the firmware was successfully sent to the STM32.|

![MQTT Topics](https://github.com/user-attachments/assets/36b7d4cb-3901-42cd-b4c8-d6a8417e49cd)

---

## STM32 Firmware Responsibilities

* Receive firmware bytes over UART from ESP32 and write them to a dedicated **update memory area** (not directly to the main application flash).  
* Calculate the **CRC32 checksum** on the entire received firmware stored in the update area.  
* Compare the calculated CRC with the Jenkins-published checksum received (relayed through ESP32).  
* Only if the CRC matches, copy or move the verified firmware from the update area to the **application flash area** to replace the running firmware.  
* If the CRC does not match, discard the update and keep the current firmware intact to prevent bricking.  
* Handle a **safe reboot** into the updated application after successful flashing.  
* Optionally provide status feedback (e.g., via UART, GPIO signals, or MQTT) about update success or failure for monitoring.

---

## ESP32 Firmware Responsibilities

* Connect to Wi-Fi and MQTT broker.  
* Subscribe to firmware update MQTT topics.  
* On receiving `"available"` status:  
  * Download new firmware `.bin` from HTTP server or GitHub raw URL.  
  * Stream firmware over UART to STM32 in proper chunk sizes.

---

Created and maintained by **Melek Khadhraoui** – Embedded Systems & IoT Engineering Student.  
For questions, collaborations, or support, feel free to reach out!
