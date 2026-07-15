#!/bin/bash
# ==========================================================
# ARDUPILOT SITL & GAZEBO LAUNCHER (KRTI 2026 EDITION)
# ==========================================================

echo "[*] Initiating ArduPilot SITL Simulation Environment for KRTI 2026..."

# Export path untuk model-model dan plugin ArduPilot Gazebo
export GZ_SIM_RESOURCE_PATH=/home/ambatron/DRONE_ARDU:/usr/local/share/ardupilot_gazebo/models:/home/ambatron/PX4-Autopilot/Tools/simulation/gz/models:/home/ambatron/PX4-Autopilot/Tools/simulation/gz/worlds:$GZ_SIM_RESOURCE_PATH
export GZ_SIM_SYSTEM_PLUGIN_PATH=/home/ambatron/PX4-Autopilot/build/px4_sitl_default/src/modules/simulation/gz_plugins:/usr/local/lib/ardupilot_gazebo:/usr/local/lib/ardupilot_gazebo/plugins:$GZ_SIM_SYSTEM_PLUGIN_PATH

# Eksekusi dengan GPU Rendering Bypass (Nvidia Optimus / WSL2)
export MESA_GL_VERSION_OVERRIDE=4.5
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
export IGN_IP=127.0.0.1

echo "[+] Launching KRTI 2026 World di Gazebo..."
# Jalanin Gazebo dan biarin dia kebuka di background
gz sim -r KRTI_2026_ardu.sdf &
GZ_PID=$!

echo "[+] Menunggu 7 detik biar Gazebo kelar render dunia 3D-nya..."
sleep 7

echo "[+] Nge-Spawn Drone MMATS-15 (ArduPilot Edition) di titik Start (Landing Pad Biru)..."
gz service -s /world/KRTI_2026/create \
--reqtype gz.msgs.EntityFactory \
--reptype gz.msgs.Boolean \
--timeout 3000 \
--req 'sdf_filename: "/home/ambatron/PX4-Autopilot/Tools/simulation/gz/models/iris_krti_ardu/model.sdf", name: "drone", pose: {position: {x: -30, y: 0, z: 0.2}}'

echo "[+] BOOM! Drone udah ke-Spawn. Buka terminal lain buat nyalain sim_vehicle.py!"
echo "[+] Tekan Ctrl+C di terminal ini buat nutup Gazebo."
wait $GZ_PID
