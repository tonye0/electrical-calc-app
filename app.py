import streamlit as st
from PIL import Image
import math

st.set_page_config(page_title="Engineering Toolkit", layout="wide")

# --- Sidebar Navigation ---
logo = Image.open("logo.png")
st.sidebar.image(logo, use_container_width=True)
st.sidebar.title("Engineering Toolkit")

tab_group = st.sidebar.radio("Select a Tool Group", [
    "Power & Protection", 
    "Conductor & Busbar Sizing", 
    "Energy & Backup Systems", 
    "AI Notes / Help"
])

st.title("⚙️ Engineering Design Calculator Toolkit")

# --- Tabs: Power & Protection ---
if tab_group == "Power & Protection":
    tabs = st.tabs(["🔌 Load Current", "🧯 Breaker Sizing", "⚡ Generator Breaker", "🧲 Contactor Sizing"])


    with tabs[0]:
        st.header("🔌 Load Current Calculator")

        # Unit selection dropdown
        unit = st.selectbox("Select Power Unit:", ["W", "kW", "HP"])

        # Input power value
        power = st.number_input(f"Enter Power ({unit}):", min_value=0.0, step=0.1)

        # Convert all to kW internally
        if unit == "W":
            power_kw = power / 1000  # W to kW
        elif unit == "HP":
            power_kw = power * 0.746  # HP to kW
        else:
            power_kw = power

        # Phase selection dropdown
        phase = st.selectbox("Select System Type:", ["Three-Phase", "Single-Phase"])

        # Set voltage input depending on phase selection
        if phase == "Three-Phase":
            voltage = st.number_input("Enter Voltage (V):", value=400.0)
            pf = st.slider("Power Factor (PF):", 0.1, 1.0, 0.8)
        else:
            voltage = st.number_input("Enter Voltage (V):", value=240.0)
            pf = 1  # No PF for single-phase (assumed unity)

        # Input validation and calculation
        if voltage <= 0:
            st.error("⚠️ Voltage must be greater than 0.")
        elif power_kw <= 0:
            st.error("⚠️ Power must be greater than 0.")
        else:
            if phase == "Three-Phase":
                current = (power_kw * 1000) / (math.sqrt(3) * voltage * pf)
            else:  # Single-phase
                current = (power_kw * 1000) / voltage

            st.success(f"Load Current: {current:.2f} A")


    with tabs[1]:
        st.header("🧯 Breaker Sizing Tool")

        unit = st.selectbox("Select Power Unit:", ["W", "kW", "kVA"])
        phase = st.selectbox("Select Phase:", ["Three-Phase", "Single-Phase"])

        # Voltage input first
        if phase == "Three-Phase":
            voltage = st.number_input("Enter Voltage (V):", value=400.0, key="voltage")
        else:
            voltage = st.number_input("Enter Voltage (V):", value=240.0, key="voltage")

        # Show PF slider only if unit is W or kW
        if unit in ["W", "kW"]:
            pf = st.slider("Power Factor (PF):", 0.1, 1.0, 0.8, key="pf")
        else:
            pf = 1  # Assume unity for kVA

        # Power input after voltage
        if unit == "W":
            power = st.number_input("Enter Power (W):", min_value=0.0, key="power_w")
        elif unit == "kW":
            power_kw = st.number_input("Enter Power (kW):", min_value=0.0, key="power_kw")
            power = power_kw * 1000
        else:  # kVA
            power_kva = st.number_input("Enter Power (kVA):", min_value=0.0, key="power_kva")
            power = power_kva * 1000

        margin = st.slider("Safety Margin (%):", 0, 100, 25, key="margin")

        if voltage <= 0:
            st.error("⚠️ Voltage must be greater than 0.")
        elif power <= 0:
            st.error("⚠️ Power must be greater than 0.")
        else:
            # Current calculation based on unit and phase
            if unit == "kVA":
                if phase == "Three-Phase":
                    current = power / (math.sqrt(3) * voltage)
                else:
                    current = power / voltage
            else:
                if phase == "Three-Phase":
                    current = power / (math.sqrt(3) * voltage * pf)
                else:
                    current = power / voltage

            current_margin = current * (1 + margin / 100)

            standard_breakers = [6,10,16,20,25,32,40,50,63,80,100,125,160,200,250,315,400,
                                500,630,800,1000,1250,1600,2000,2500,3200,4000,5000]

            # Find breakers for lower and upper band
            breaker_upper = next((b for b in standard_breakers if b >= current_margin), "Over 5000A")
            breaker_lower_candidates = [b for b in standard_breakers if b < current_margin]
            breaker_lower = breaker_lower_candidates[-1] if breaker_lower_candidates else None

            st.info(f"Full Load Current: {current:.2f} A")
            st.info(f"Current with {margin}% Safety Margin: {current_margin:.2f} A")

            if breaker_lower is not None:
                st.success(f"Recommended Breaker Size: {breaker_lower} A or {breaker_upper} A")
            else:
                st.success(f"Recommended Breaker Size: {breaker_upper} A")



    with tabs[2]:
        st.header("⚡ Generator Protection Breaker")
        
        unit = st.selectbox("Select Power Unit:", ["kVA", "kW", "W"], key="gen_unit")
        phase = st.selectbox("Select Phase:", ["Three-phase", "Single-phase"], key="gen_phase")
        

        if phase == "Three-phase":
            voltage = st.number_input("Enter Voltage (V):", value=400.0, key="voltage_three_phase")
        else:
            voltage = st.number_input("Enter Voltage (V):", value=240.0, key="voltage_single_phase")
        
        # Show PF only if three-phase AND unit is not kVA
        show_pf = (phase == "Three-phase") and (unit != "kVA")
        if show_pf:
            pf = st.slider("Power Factor:", 0.1, 1.0, 0.8, key="gen_pf")
        else:
            pf = 1.0  # assume pf = 1 if PF slider hidden
        
        margin = st.slider("Safety Margin (%):", 0, 100, 25, key="gen_margin")
        
        # Input power based on unit
        if unit == "kVA":
            gen_power = st.number_input("Generator Power (kVA):", min_value=0.0, key="gen_power_kva")
            power_w = gen_power * 1000 * pf  # pf used for completeness but will be 1 here anyway
        elif unit == "kW":
            gen_power = st.number_input("Generator Power (kW):", min_value=0.0, key="gen_power_kw")
            power_w = gen_power * 1000
        else:
            gen_power = st.number_input("Generator Power (W):", min_value=0.0, key="gen_power_w")
            power_w = gen_power
        
        if voltage > 0 and pf > 0 and power_w > 0:
            if phase == "Three-phase":
                gen_current = power_w / (math.sqrt(3) * voltage * pf)
            else:
                gen_current = power_w / (voltage * pf)
            
            gen_current_margin = gen_current * (1 + margin / 100)
            
            
            standard_breakers = [6,10,16,20,25,32,40,50,63,80,100,125,160,200,250,315,400,
                                500,630,800,1000,1250,1600,2000,2500,3200,4000,5000]

            # Find breakers for lower and upper band
            breaker_upper = next((b for b in standard_breakers if b >= gen_current_margin), "Over 5000A")
            breaker_lower_candidates = [b for b in standard_breakers if b < gen_current_margin]
            breaker_lower = breaker_lower_candidates[-1] if breaker_lower_candidates else None

            st.info(f"Full Load Current: {gen_current:.2f} A")
            st.info(f"Current with {margin}% Safety Margin: {gen_current_margin:.2f} A")

            if breaker_lower is not None:
                st.success(f"Breaker Size: {breaker_lower} A or {breaker_upper} A")
            else:
                st.success(f"Breaker Size: {breaker_upper} A")
    
    
    with tabs[3]:
        st.header("🧲 Contactor Sizing")

        unit = st.selectbox("Select Power Unit:", ["kW", "HP", "W"], index=0, key="contact_unit")
        phase = st.selectbox("Select Phase:", ["Three-phase", "Single-phase"], index=0, key="contact_phase")

        default_voltage = 240 if phase == "Single-phase" else 400
        voltage = st.number_input("Voltage (V):", value=default_voltage, key="contact_voltage")

        pf = st.slider("Power Factor:", 0.1, 1.0, 0.8, key="contact_pf")
        margin = st.slider("Safety Margin (%):", 0, 100, 25, key="contact_margin")

        if unit == "kW":
            motor_power = st.number_input("Motor Power (kW):", min_value=0.0, key="motor_power_kw")
            motor_power_w = motor_power * 1000
        elif unit == "HP":
            motor_power = st.number_input("Motor Power (HP):", min_value=0.0, key="motor_power_hp")
            motor_power_w = motor_power * 746
        else:
            motor_power = st.number_input("Motor Power (W):", min_value=0.0, key="motor_power_w")
            motor_power_w = motor_power

        if voltage > 0 and pf > 0 and motor_power_w > 0:
            if phase == "Three-phase":
                motor_current = motor_power_w / (math.sqrt(3) * voltage * pf)
            else:
                motor_current = motor_power_w / (voltage * pf)

            # Contactor sizing multiplier 1.5 times full load current
            contactor_current = motor_current * 1.5

            st.write(f"Full Load Motor Current: {motor_current:.2f} A")
            st.write(f"Motor Current with {margin}% Margin: {contactor_current:.2f} A")
            st.success(f"Recommended Contactor Current Rating (1.5 x FLC): {contactor_current:.2f} A")

        else:
            st.warning("Please enter valid motor power, voltage, and power factor.")






# --- Tabs: Conductor & Busbar Sizing ---
elif tab_group == "Conductor & Busbar Sizing":
    tabs = st.tabs(["🔗 Cable Sizing", "🔩 Busbar Sizing", "🔥 Heat Loss Calculator"])

    with tabs[0]:
        st.header("🔗 Cable Sizing")
        current = st.number_input("Current Load (A):", min_value=0.0)
        length = st.number_input("Cable Length (m):", min_value=0.0)
        derating = st.slider("Derating Factor (%):", 0, 100, 20)
        cable_sizes = {1.5: 18, 2.5: 24, 4: 32, 6: 41, 10: 57, 16: 76, 25: 101, 35: 125,
                       50: 150, 70: 190, 95: 230, 120: 265, 150: 300, 185: 340, 240: 380}
        if current > 0:
            adj = current / ((100 - derating) / 100)
            size = next((s for s, a in cable_sizes.items() if a >= adj), None)
            st.write(f"Adjusted Current: {adj:.2f} A")
            st.success(f"Recommended Cable Size: {size} mm²" if size else "No suitable cable found.")

    with tabs[1]:
        st.header("🔩 Busbar Sizing")
        current = st.number_input("Busbar Current (A):", min_value=0.0)
        if current > 0:
            if current <= 100:
                bar = "25x3 mm"
            elif current <= 250:
                bar = "25x5 mm"
            elif current <= 630:
                bar = "40x6 mm"
            elif current <= 1000:
                bar = "50x10 mm"
            else:
                bar = "Multiple Busbars Needed"
            st.success(f"Suggested Busbar Size: {bar}")

    with tabs[2]:
        st.header("🔥 Heat Loss in Panel")
        devices = st.number_input("Number of Devices:", min_value=1)
        power_loss = st.number_input("Average Power Loss per Device (W):", min_value=0.0)
        if devices > 0 and power_loss > 0:
            total_loss = devices * power_loss
            st.success(f"Total Panel Heat Loss: {total_loss:.2f} W")

# --- Tabs: Energy Systems ---
elif tab_group == "Energy & Backup Systems":
    tabs = st.tabs(["🔋 Capacitor Bank Sizing", "🔌 UPS/Inverter Sizing"])

    with tabs[0]:
        st.header("🔋 Capacitor Bank Sizing")
        kvar_required = st.number_input("Reactive Power to Compensate (kVAR):", min_value=0.0)
        voltage = st.number_input("Voltage (V):", value=400, key="cap_voltage")
        if voltage > 0:
            cap_current = (kvar_required * 1000) / (math.sqrt(3) * voltage)
            st.success(f"Required Capacitor Bank Current: {cap_current:.2f} A")

    with tabs[1]:
        st.header("🔌 UPS/Inverter Sizing")
        load_kw = st.number_input("Total Load (kW):", min_value=0.0)
        backup_time = st.number_input("Backup Time (hours):", min_value=0.0)
        efficiency = st.slider("UPS Efficiency:", 0.5, 1.0, 0.9)
        battery_volt = st.number_input("Battery Voltage (V):", value=48)
        if load_kw > 0 and backup_time > 0:
            load_kva = load_kw / efficiency
            energy_needed = load_kva * 1000 * backup_time
            battery_ah = energy_needed / battery_volt
            st.write(f"Required Apparent Power: {load_kva:.2f} kVA")
            st.success(f"Recommended Battery Capacity: {battery_ah:.0f} Ah")

# --- Tabs: AI Notes / Help ---
elif tab_group == "AI Notes / Help":
    st.header("💬 AI Notes / Help Tab")
    st.info("🧠 This section can be used to integrate AI-generated notes, design suggestions, reminders, or even ChatGPT-style prompts for internal documentation help.")

    prompt = st.text_area("Write a note or question:")
    if prompt:
        st.success(f"📝 You wrote:\n\n{prompt}")
