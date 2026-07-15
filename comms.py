import asyncio
import json
from pymavlink import mavutil
import math

class DroneState:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.yaw = 0.0
        self.lidar_left = 5.0
        self.lidar_right = 5.0
        self.target_front = {"status": "LOST", "class": "none", "error_x": 0, "error_y": 0, "area": 0, "confident": 0.0}
        self.target_down = {"status": "LOST", "class": "none", "error_x": 0, "error_y": 0, "area": 0, "confident": 0.0}

state = DroneState()

async def mavlink_router_task(master):
    guided_achieved = False
    last_heartbeat_time = 0
    
    while True:
        current_time = asyncio.get_event_loop().time()
        
        # Kirim detak jantung (HEARTBEAT) tiap 1 detik biar ArduPilot nggak ngira kita mati!
        if current_time - last_heartbeat_time > 1.0:
            master.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                0, 0, 0
            )
            last_heartbeat_time = current_time

        # Kuras semua antrean pesan biar realtime!
        while True:
            # Baca APAPUN pesannya tanpa filter type!
            msg = master.recv_match(blocking=False)
            if not msg:
                break # Antrean kosong
                
            msg_type = msg.get_type()
            
            if msg_type == 'LOCAL_POSITION_NED':
                state.x = msg.x
                state.y = msg.y
                state.z = msg.z
            elif msg_type == 'ATTITUDE':
                state.yaw = math.degrees(msg.yaw)
            elif msg_type == 'HEARTBEAT':
                # Jangan kill switch kalau yang dibaca HEARTBEAT dari diri sendiri/MAVProxy
                mode = mavutil.mode_string_v10(msg)
                if mode == 'GUIDED':
                    guided_achieved = True
                elif guided_achieved and mode and mode != 'GUIDED' and mode != 'STABILIZE':
                    # Pengecualian buat STABILIZE karena kita pakai buat hack Takeoff
                    print(f"[KILL SWITCH] MANUAL OVERRIDE DETECTED! (Flight Mode changed to {mode}). Exiting Autopilot...")
                    import os
                    os._exit(0)
                    
        await asyncio.sleep(0.01)

class UDPReceiverProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        try:
            message = data.decode('utf-8')
            parsed = json.loads(message)
            
            if parsed.get("camera") == "lidar":
                side = parsed.get("side")
                if side == "left":
                    state.lidar_left = float(parsed.get("range", 5.0))
                elif side == "right":
                    state.lidar_right = float(parsed.get("range", 5.0))
            elif parsed.get("camera") == "down":
                state.target_down.update(parsed)
            else:
                state.target_front.update(parsed)
        except Exception as e:
            pass

async def start_udp_server(ip="127.0.0.1", port=5005):
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPReceiverProtocol(),
        local_addr=(ip, port),
        reuse_port=True
    )
    return transport
