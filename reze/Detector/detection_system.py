from pymodbus.client import ModbusTcpClient
import time
from datetime import datetime

TARGET = '127.0.0.1'
PORT = 502
POLL_INTERVAL = 0.05
TANK_JUMP_THRESHOLD = 50

client = ModbusTcpClient(TARGET, port=PORT)
client.connect()

print("=" * 40)
print("    ICS DETECTOR - KAVACH")
print("=" * 40)
print("\n[*] Monitoring OpenPLC registers...")
print("    Press Ctrl+C to stop\n")

print("    [!] Capturing baseline in 2s... ensure system is clean")
time.sleep(2)

baseline_regs = client.read_holding_registers(address=0, count=8).registers
baseline_coils = client.read_coils(address=0, count=8).bits[:8]
print(f"    Baseline Registers: {list(baseline_regs)}")
print(f"    Baseline Coils:     {list(baseline_coils)}\n")

prev_regs = list(baseline_regs)
active_coil_alerts = set()
active_reg_alerts = set()

try:
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        regs = client.read_holding_registers(address=0, count=8).registers
        coils = client.read_coils(address=0, count=8).bits[:8]

        # Coil detection
        for i, (current, base) in enumerate(zip(coils, baseline_coils)):
            if current != base:
                if i not in active_coil_alerts:
                    print(f"\n[{timestamp}] [ATTACK] Coil {i} manipulated: {base} → {current}")
                    active_coil_alerts.add(i)

        # Register jump detection
        for i, (current, prev) in enumerate(zip(regs, prev_regs)):
            jump = abs(current - prev)
            if jump > TANK_JUMP_THRESHOLD:
                if i not in active_reg_alerts:
                    print(f"\n[{timestamp}] [ATTACK] Register {i} jumped by {jump}: {prev} → {current}")
                    active_reg_alerts.add(i)

        prev_regs = list(regs)

        if active_coil_alerts or active_reg_alerts:
            print(f"[{timestamp}] \033[91m[ATTACK] ⚠ INTRUSION ACTIVE | Coils: {list(active_coil_alerts)} | State: {list(coils[:8])}\033[0m", end='\r')
        else:
            print(f"[{timestamp}] [OK] Regs={list(regs[:4])} Coils={list(coils[:4])}          ", end='\r')

        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    print("\n\n[*] Detector stopped.")
    client.close()
