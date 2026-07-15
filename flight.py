import asyncio
import math
from pymavlink import mavutil
from comms import state

async def wait_for_guided_mode(master):
    print("[FLIGHT] =========================================")
    print("[FLIGHT] MMATS-15 STANDBY MODE AKTIF!")
    print("[FLIGHT] Menunggu Pilot nerbangin drone secara manual...")
    print("[FLIGHT] Silakan Takeoff, lalu ubah mode ke GUIDED/OFFBOARD!")
    print("[FLIGHT] =========================================")
    
    # Tunggu sampai mode berubah jadi GUIDED
    master.wait_heartbeat()
    while True:
        # Kita baca state mode dari comms.py yang udah dipantau di mavlink_router_task
        msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=1.0)
        if msg:
            mode = mavutil.mode_string_v10(msg)
            if mode == 'GUIDED':
                print("[FLIGHT] 🚨 MODE GUIDED TERDETEKSI! 🚨")
                print("[FLIGHT] KENDALI DIAMBIL ALIH OLEH AI CYBORG!")
                break
            
        await asyncio.sleep(0.5)

    print("[FLIGHT] Offboard Mode AKTIF! AI mulai bekerja...")
    await asyncio.sleep(1)

async def hover(master):
    """
    Berhenti di udara (Brake / Hover).
    """
    await send_body_velocity(master, 0.0, 0.0, 0.0, 0.0)

async def send_body_velocity(master, forward_m_s, right_m_s, down_m_s, yaw_deg_s):
    """
    Fungsi modular utama untuk bermanuver di Body Frame.
    """
    yaw_rad_s = math.radians(yaw_deg_s)
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_BODY_NED, # Target frame
        0x07C7, # type_mask (0b0000_0111_1100_0111): Ignore Pos, Accel, Yaw. Use Vel, YawRate.
        0, 0, 0, # Position (ignored)
        forward_m_s, right_m_s, down_m_s, # Velocity
        0, 0, 0, # Accel (ignored)
        0, yaw_rad_s # Yaw (ignored), Yaw rate
    )

async def land(master):
    print("[FLIGHT] Mendarat...")
    master.set_mode('LAND')
