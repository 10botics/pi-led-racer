#!/usr/bin/env python3
"""
Simple LED Control Program
Turns an LED on and off using Raspberry Pi GPIO

Hardware Setup:
- LED anode (+) -> GPIO 18
- LED cathode (-) -> GND
"""

import time
from gpiozero import LED

def main():
    print("Simple LED Control Program")
    print("=========================")
    print("Hardware Setup:")
    print("- LED anode (+) -> GPIO 18")
    print("- LED cathode (-) -> GND")
    print()
    
    # Create LED object on GPIO 18
    led = LED(18)
    
    try:
        # Test 1: Turn LED on
        print("1. Turning LED ON...")
        led.on()
        print("   LED is now ON")
        time.sleep(2)  # Keep on for 2 seconds
        
        # Test 2: Turn LED off
        print("2. Turning LED OFF...")
        led.off()
        print("   LED is now OFF")
        time.sleep(2)  # Keep off for 2 seconds
        
        # Test 3: Blinking pattern
        print("3. Blinking LED 5 times...")
        for i in range(5):
            print(f"   Blink {i+1}/5")
            led.on()
            time.sleep(0.5)
            led.off()
            time.sleep(0.5)
        
        print("\n✅ LED control test completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Clean up
        print("Cleaning up...")
        led.off()  # Make sure LED is off
        led.close()  # Release GPIO resources
        print("✅ Resources cleaned up")

if __name__ == "__main__":
    main() 