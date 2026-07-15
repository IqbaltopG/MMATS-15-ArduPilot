# 🚁 MMATS-15 (ArduPilot Edition)
*Microservice Multisensor Autonomous Targeting System*

> [!WARNING]  
> **🚨 HIGHLY EXPERIMENTAL - DO NOT FLASH TO HARDWARE YET 🚨**  
> This ArduPilot branch is currently under heavy development and optimization. The State Machine, YOLO vision integration, and UDP Microservices are tuned explicitly for **Gazebo SITL at 30-40% Real-Time Factor (RTF)**. If you flash this to a physical Jetson/Raspberry Pi and fly it right now, the timeout scalers and pitch-coupling parameters will cause the drone to behave erratically or crash. **USE IN SIMULATION ONLY** until this warning is removed.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![PX4](https://img.shields.io/badge/PX4_Autopilot-SITL-blueviolet?style=for-the-badge)
![MAVSDK](https://img.shields.io/badge/MAVSDK-Enabled-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-Unlicense-black?style=for-the-badge)

## 📌 Executive Summary
Listen up. This repo contains **MMATS-15**, a highly aggressive, brute-force autonomous targeting architecture for precision payload delivery (X500 frame). We didn't build this to look pretty. We built it following the **KISS (Keep It Simple, Stupid)** principle because the hardware we are running on (budget laptops for SITL, Raspberry Pi 5 for Edge) will literally melt if you try to shove a bloated ROS2 framework down its throat. 

This is raw UDP microservices. It's got time-dilation physics compensation, "Tunnel Blind Charge" memory buffers, and zero-cost sensor fusion. The legacy spaghetti code has been entirely rewritten into a robust Object-Oriented State Machine. It's clean, it's decoupled, and it lands the drone flawlessly. 

## 🛠️ Tech Stack
* **Core Logic (Autopilot):** Python 3.10, MAVSDK, asyncio, UDP Sockets
* **Computer Vision (Daemon):** YOLOv8 (Ultralytics), PyTorch, OpenCV
* **Flight Stack:** PX4 Autopilot
* **Simulation Engine:** Gazebo Harmonic (gz_x500)
* **Ground Control Station:** QGroundControl (QGC)
* **OS Environment:** Xubuntu 22.04 LTS / Windows 11 (via WSL2)

---

## 🚀 Environment Setup & Hardware Acceleration (The Nvidia Bypass)
If you're running Gazebo on a Linux machine with hybrid graphics, your OS is probably stupid enough to default to Integrated Graphics. Your system will bottleneck, hang, and crash. 

To force Gazebo to pull from the **Dedicated GPU (Nvidia)** and stop acting like a potato, run this exact command:

```bash
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json make px4_sitl gz_x500_depth
```

---

## 🐧 ArduPilot Setup (Ubuntu 22.04 LTS / WSL2)
For you bare-metal dual-booters or WSL2 users. Run this. Don't skip steps.

### 1. System Provisioning & Environment Setup
Execute the custom setup script. This configures Gazebo environment variables, GPU rendering bypass, and spawns the drone in the Gazebo world.

```bash
cd /home/ambatron/DRONE_ARDU
./setup_ardu.sh
```
⚠️ **Note:** Wait for Gazebo to fully load the 3D world and spawn the drone before moving to the next step.

### 2. Connect Ground Control Integration (QGC)
1. Download **QGroundControl** for Windows/Linux from the [Official Site](https://docs.qgroundcontrol.com/).
2. **Network Bypass:** Allow **Private & Public Networks** in Firewall. If you misclick this, QGC will be completely blind.
3. Keep QGC open in the background. It will auto-connect once MAVProxy starts.

---

## ⚠️ Rules of Engagement (READ BEFORE ASKING STUPID QUESTIONS)
Before you dump a stack trace in the group chat, use your brain:

1. **"My Gazebo screen is black / UI is glitching!"** -> Update your GPU drivers. Ensure `__NV_PRIME_RENDER_OFFLOAD=1` is set if using hybrid graphics.
2. **"QGC won't connect!"** -> Fix your Firewall. 99% of you blocked the UDP packets.
3. **"ArduCopter won't arm!"** -> Wait for the EKF to become healthy. It takes ~15 seconds after launch.

> **RTFM (Read The Fucking Manual):** These instructions are tested. Execute them exactly as written.

---

## ⚡ HOW TO RUN (THE ANTI-BLOATWARE WAY)
Forget the ritual of opening a dozen terminals or compiling a massive ROS workspace that takes 10 minutes. MMATS-15 is built for speed.

**Terminal 1 (The Matrix - Physics Engine):**
Start Gazebo Harmonic with the KRTI 2026 Arena.
```bash
./run_gazebo.sh
```
*(Wait until the UI loads and you see the blue landing pad).*

**Terminal 2 (The Brain - Flight Controller):**
Start ArduCopter SITL (JSON mode) and MAVProxy. This connects Gazebo to the flight controller and forces GUIDED mode.
```bash
./run_ardu.sh
```

**Terminal 3 (The Assassin - Logic & Vision):**
Ignite the circuit by executing the Python logic.
```bash
python3 autopilot.py
```
*(Or use `python3 maruk_launcher.py` if you want to spawn both vision and autopilot in parallel).*

> **⚠️ NOTE:** `autopilot.py` will continuously attempt to arm the drone until the EKF (Extended Kalman Filter) is healthy. Once healthy, it auto-arms, takes off, and executes the state machine.
> 
> However, it's completely up to you. You can either use the launcher for a fast deployment, or you can manually run `vision_daemon.py` and `autopilot.py` in separate terminals to treat them as clean, isolated microservices.

---

## 👁️ The MMATS-15 Architecture

### 1. Zero-Cost Sensor Fusion (LiDAR + Bounding Box Area)
Processing 3D point clouds from a depth camera uses way too much CPU and network I/O. We threw that out. Instead, MMATS-15 extracts the pixel area of the YOLO bounding box `(bx2 - bx1) * (by2 - by1)` as a dirt-cheap pseudo-depth metric. On the physical drone, we slam this together with a downward LiDAR for 2-way verification. It’s cheap, it’s fast, and it works.

### 2. The Microservice Split & OOP State Machine
We don't cram neural network inference and flight controls into the same loop. `vision_daemon.py` aggressively processes frames and blasts UDP packets containing bounding boxes to `autopilot.py`. This ensures the flight controller loop runs at a strict 10Hz without waiting for YOLO to finish thinking.

The core flight logic has been decoupled into a pure **Object-Oriented Programming (OOP) State Machine** (`states.py`). We burned the old 900-line monolithic `if-elif` spaghetti code to the ground. Every phase of the mission (Takeoff, Line Follow, Gate Centering, Landing) is now an isolated class inheriting from `BaseState`, ensuring that memory buffers (`ctx`) and transitions are bulletproof and hardware-agnostic.

### 3. Simulation Time-Dilation (RTF Scaling Hack)
If you run Gazebo SITL on a potato laptop, the physics engine will choke and run at **30-40% Real-Time Factor (RTF)**. That means 10 real seconds is only 3-4 physical seconds in the simulator.

Because of this, the `timeout_counter` thresholds in our `autopilot.py` state machine are **massively inflated**. If we didn't do this, the drone would time out and abort before it physically crossed a blind spot.

**WARNING:** If you have a beefy PC that actually hits 100% RTF, or when we flash this to the real drone, you **MUST SCALE DOWN THE TIMEOUTS**. If you run this 30% RTF code in the real world, the drone is going to hang in the air for 15 seconds waiting for a timeout. Adjust your shit before you fly IRL.

### 4. "Stutter Creep" Physics Hack
We use raw physics to solve our camera FOV problems. When the drone flies forward, the nose pitches down, aiming the downward camera backward (creating a massive blind spot). Instead of praying it sees the ArUco pad, we implemented a "stutter creep." The drone flies forward for 1 second, then slams the brakes for 1 second. The braking violently levels the pitch, forcing the downward camera to point perfectly vertical like a spotlight, guaranteeing we sweep the floor. It's brute-force engineering.

### 5. Blind Spot Memory & Safe Reversing
When traversing complex geometries (like Drop Boxes or Landing Pads), the drone enters a camera blind spot between the Front and Down cameras. If the YOLO vision drops, the drone executes a **Safe Reversing Fallback**. Instead of reversing blindly and crashing into obstacles behind it, it tracks physical GPS displacement. If it reverses more than 2.0 meters without re-acquiring the target, it will abort the reverse and execute a safe Hover lock, demanding manual or secondary logic override.

## 🏆 MILESTONE ACHIEVED: 🎯 Final Milestone: Full Trajectory Cleared!
- 🟩 **Status:** **COMPLETED** (July 2026).
- 🏆 **Achievement:** The drone successfully completed the entire KRTI trajectory end-to-end (Takeoff -> Single Gates -> Triple Gate -> Red Drop Box -> Final Gates -> Precision Landing).
- 🛠️ **Resolution:** The legacy monolithic `if-elif` code was entirely refactored into a modular OOP State Machine. Deep architectural bugs, including the "Triple Gate Internal Wall Shrinkage" illusion and the "Infinite Reverse Kebablasan" bug, were successfully patched using persistent GPS/Lidar memory buffering.

---
> *"Terinspirasi dari misil AAM, AGM. LSRG, Strider Squadron, Galm Team. GeoHot, Tyler Durden, Saul Goodman. Anduril, Lockheed Martin, dan Pak Gusti (dosen Machine Learning-ku), Pak Thor juga sebagai dospem krti yang membebaskanku untuk bikin program seaneh ini."*
