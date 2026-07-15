#!/bin/bash
echo "[+] Menyalakan Jantung ArduCopter MMATS-15 (JSON Edition)..."
echo "[+] Mode GUIDED & Bypass ARMING_CHECK otomatis diaktifkan!"
echo "============================================================"
echo "⚠️ PERHATIAN ⚠️"
echo "Setelah MAVProxy kebuka dan muncul map, lo cuma perlu RUN autopilot.py di terminal lain."
echo "autopilot.py bakal nyoba nge-ARM berulang-ulang sampai EKF sehat (sekitar 15 detik)."
echo "Begitu EKF sehat, drone langsung AUTO-ARM dan TAKEOFF!"
echo "============================================================"

# Bersihkan zombie process biar port nggak tabrakan
pkill -f arducopter 2>/dev/null
pkill -f mavproxy 2>/dev/null

# Aktifkan virtual environment bawaan ArduPilot
source /home/ambatron/venv-ardupilot/bin/activate 2>/dev/null

echo "[+] Memulai ArduCopter SITL Engine (JSON Mode)..."
/home/ambatron/ardupilot/build/sitl/bin/arducopter -w --model JSON --speedup 1 --slave 0 --sim-address=127.0.0.1 -I0 --home -7.2652,112.7425,10,0 --defaults /home/ambatron/ardupilot/Tools/autotest/default_params/gazebo-iris.parm &
ARDU_PID=$!

# Kasih napas 3 detik buat ArduCopter ngebuka port TCP 5760
sleep 3

echo "[+] Menyambungkan Ground Control Station (MAVProxy)..."
mavproxy.py --retries 5 --out 127.0.0.1:14550 --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --map --console --cmd="param set ARMING_CHECK 0; param set SYSID_MYGCS 254; mode guided"

# Kalau lo nutup MAVProxy (Ctrl+C), matiin sekalian ArduCopter-nya
echo "[+] MAVProxy ditutup. Mematikan mesin ArduCopter..."
kill $ARDU_PID 2>/dev/null
