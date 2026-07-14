import subprocess
import threading
import sys
import os
import signal
import time

# Warna ANSI buat mempercantik Terminal (Style Hacker)
COLOR_MATA = '\033[92m'  # Hijau (Buat YOLO)
COLOR_OTAK = '\033[96m'  # Cyan (Buat Autopilot)
COLOR_MARUK = '\033[93m' # Kuning (Buat MARUK System)
COLOR_RESET = '\033[0m'  # Reset warna

def stream_logs(process, prefix, color):
    """Membaca log dari subprocess (MATA/OTAK) dan nge-print barengan tanpa nyangkut."""
    # Baca per baris secara real-time
    for line in iter(process.stdout.readline, ''):
        sys.stdout.write(f"{color}[{prefix}]{COLOR_RESET} {line}")
        sys.stdout.flush()

def main():
    print(f"{COLOR_MARUK}=================================================={COLOR_RESET}")
    print(f"{COLOR_MARUK} 🔥 M.A.R.U.K. LAUNCHER (Zero-Bloatware System) 🔥{COLOR_RESET}")
    print(f"{COLOR_MARUK}=================================================={COLOR_RESET}")
    
    # Deteksi path (asumsi dijalankan dari dalam folder DRONE atau XLLE-01)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    vision_script = os.path.join(script_dir, "vision_daemon.py")
    autopilot_script = os.path.join(script_dir, "autopilot.py")
    
    # Cek apakah file kodingan aslinya ada
    if not os.path.exists(vision_script) or not os.path.exists(autopilot_script):
        print(f"{COLOR_MARUK}[MARUK ERROR] Waduh! vision_daemon.py atau autopilot.py gak ketemu di folder ini!{COLOR_RESET}")
        sys.exit(1)

    print(f"{COLOR_MARUK}[MARUK] Mengalokasikan Port UDP dan Saraf...{COLOR_RESET}")
    time.sleep(1)

    try:
        # Jalankan MATA dan OTAK di Background!
        # -u (unbuffered) penting banget biar log print() python gak ditahan di memori
        print(f"{COLOR_MARUK}[MARUK] Menyalakan Saraf [MATA] (Vision Daemon)...{COLOR_RESET}")
        mata_proc = subprocess.Popen([sys.executable, "-u", vision_script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        print(f"{COLOR_MARUK}[MARUK] Menyalakan Saraf [OTAK] (MMATS Autopilot)...{COLOR_RESET}")
        otak_proc = subprocess.Popen([sys.executable, "-u", autopilot_script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

        # Bikin Thread buat ngambil teks dari MATA dan OTAK terus ditampilin ke layar
        threading.Thread(target=stream_logs, args=(mata_proc, "MATA", COLOR_MATA), daemon=True).start()
        threading.Thread(target=stream_logs, args=(otak_proc, "OTAK", COLOR_OTAK), daemon=True).start()

        # MARUK diem aja di background jadi Mandor
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Kalo lo pencet Ctrl+C, MARUK bakal nge-kill MATA sama OTAK sekalian!
        print(f"\n{COLOR_MARUK}[MARUK] 🛑 Kill Switch Ditekan! Membunuh semua Node...{COLOR_RESET}")
        mata_proc.send_signal(signal.SIGINT)
        otak_proc.send_signal(signal.SIGINT)
        
        mata_proc.wait()
        otak_proc.wait()
        print(f"{COLOR_MARUK}[MARUK] Semua Saraf Mati. Goodbye Commander! 🦅{COLOR_RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
