#!/usr/bin/env python3
"""
Button Debug Program - Test button state step by step
"""

import time
import sys

def check_gpio_library():
    """Check if RPi.GPIO library is available"""
    try:
        import RPi.GPIO as GPIO
        print("✅ RPi.GPIO library is available")
        print(f"Version: {GPIO.VERSION}")
        return GPIO
    except ImportError:
        print("❌ RPi.GPIO library not found")
        sys.exit(1)

def main():
    print("🔍 Button Debug Program")
    print("=" * 30)
    
    # Check GPIO library
    GPIO = check_gpio_library()
    
    # Setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("✅ GPIO configured for button input")
    print(f"Button pin: GPIO 5 (BCM)")
    print(f"Pull-up resistor: Enabled")
    
    print("\n📊 Testing Button States")
    print("-" * 30)
    
    # Test initial state
    initial_state = GPIO.input(5)
    print(f"Initial button state: {initial_state}")
    print(f"GPIO.HIGH = {GPIO.HIGH}, GPIO.LOW = {GPIO.LOW}")
    print(f"Button should be NOT pressed (HIGH) initially")
    
    if initial_state == GPIO.HIGH:
        print("✅ Initial state is correct (HIGH = not pressed)")
    else:
        print("❌ Initial state is wrong (should be HIGH)")
    
    print("\n🔘 Now test button press...")
    print("Press the button and watch the state change...")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            current_state = GPIO.input(5)
            if current_state == GPIO.LOW:
                print("🔘 Button is PRESSED (LOW)")
            else:
                print("🔘 Button is NOT pressed (HIGH)")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Debug stopped")
    finally:
        GPIO.cleanup()
        print("✅ GPIO cleanup completed")

if __name__ == "__main__":
    main() 