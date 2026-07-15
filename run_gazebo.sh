#!/bin/bash
echo "============================================================"
echo "🚁 MMATS-15 ArduPilot SITL - Gazebo Harmonic Launcher"
echo "============================================================"

echo "[+] Resource paths dikonfigurasi..."
export PX4_MODELS=/home/ambatron/PX4-Autopilot/Tools/simulation/gz/models
export ARDU_MODELS=/home/ambatron/ardupilot_gazebo/models
export ARDU_PLUGIN=/home/ambatron/ardupilot_gazebo/build

export GZ_SIM_RESOURCE_PATH=$PX4_MODELS:$ARDU_MODELS:$GZ_SIM_RESOURCE_PATH
export IGN_GAZEBO_RESOURCE_PATH=$PX4_MODELS:$ARDU_MODELS:$IGN_GAZEBO_RESOURCE_PATH
export SDF_PATH=$PX4_MODELS:$ARDU_MODELS:$SDF_PATH
export GZ_SIM_SYSTEM_PLUGIN_PATH=$ARDU_PLUGIN:$GZ_SIM_SYSTEM_PLUGIN_PATH

echo "[+] Resource paths set!"
echo "[+] Memulai Gazebo Harmonic dengan arena KRTI 2026..."
echo "[!] Tunggu Gazebo fully loaded, BARU jalanin run_ardu.sh!"
echo "============================================================"

gz sim -v4 -r /home/ambatron/DRONE_ARDU/KRTI_2026_ArduPilot.sdf
