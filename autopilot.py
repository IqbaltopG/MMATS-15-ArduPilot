import asyncio
import json
import math
from pymavlink import mavutil
from utils import clamp, calculate_distance, get_stutter_creep_speed
import flight
from comms import state, mavlink_router_task, start_udp_server

async def run_mission():
    print("[AUTOPILOT] Menyambungkan ke ArduPilot via PyMavlink...")
    # Pakai udp out dari MAVProxy (14550). 
    # Penting: source_system=254 biar nggak disangka MAVProxy (255) dan bikin bentrok ID!
    master = mavutil.mavlink_connection('udp:127.0.0.1:14550', source_system=254)
    master.wait_heartbeat()
    print("[AUTOPILOT] Terhubung!")

    # Jalankan task telemetry di background
    asyncio.create_task(mavlink_router_task(master))
    asyncio.create_task(start_udp_server())
    
    # 1. Tunggu Pilot Takeoff Manual dan Pindah ke GUIDED (Bypass semua keribetan Auto-Takeoff)
    await flight.wait_for_guided_mode(master)
    
    # 2. Enable position + attitude telemetry stream
    
    # Enable position telemetry stream
    master.mav.request_data_stream_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_POSITION, 10, 1
    )
    master.mav.request_data_stream_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_EXTRA1, 10, 1 # Attitude
    )

    print("[AUTOPILOT] AI Aktif! Hovering 3 detik untuk stabilisasi sebelum misi dimulai...")
    await flight.send_body_velocity(master, 0.0, 0.0, 0.0, 0.0)
    await asyncio.sleep(3)

    from states import STATE_REGISTRY, MissionContext

    # MMATS-15 STATE MACHINE (OOP)
    ctx = MissionContext()
    
    while True:
        current_state = STATE_REGISTRY.get(ctx.state_phase)
        if current_state:
            await current_state.execute(master, ctx)
            if ctx.state_phase == 'DONE':
                break
        else:
            print(f"[AUTOPILOT] UNKNOWN STATE: {ctx.state_phase}")
            break
        await asyncio.sleep(0.1) # Loop jalan 10 Hz

async def main():
    transport = await start_udp_server()
    try:
        await run_mission()
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())
