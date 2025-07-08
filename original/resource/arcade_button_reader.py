#!/usr/bin/env python3
"""
Simple Arcade Button Reader for Raspberry Pi

This program reads a 100mm arcade button connected to GPIO 6 (BCM).
The button should be wired as follows:
- Button COM (Common) -> Raspberry Pi GND
- Button NO (Normally Open) -> Raspberry Pi GPIO 6

Author: Raspberry Pi LED Racer Project
"""

import time
import sys
import signal

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n🛑 Program stopped by user')
    cleanup()
    sys.exit(0)

def cleanup():
    """Clean up GPIO resources"""
    try:
        GPIO.cleanup()
        print("✅ GPIO cleanup completed")
    except:
        pass

def check_gpio_library():
    """Check if RPi.GPIO library is available"""
    try:
        import RPi.GPIO as GPIO
        print("✅ RPi.GPIO library is available")
        print(f"Version: {GPIO.VERSION}")
        return GPIO
    except ImportError:
        print("❌ RPi.GPIO library not found")
        print("Install it with: pip install RPi.GPIO")
        print("Or update Raspberry Pi OS")
        sys.exit(1)

def setup_gpio():
    """Setup GPIO for button input"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("✅ GPIO configured for button input")
    print(f"Button pin: GPIO 6 (BCM)")
    print(f"Pull-up resistor: Enabled")

def read_button_state():
    """Read and return the current button state"""
    button_state = GPIO.input(6)
    return button_state

def main():
    """Main program loop"""
    print("🎮 Arcade Button Reader")
    print("=" * 30)
    print("Press Ctrl+C to exit")
    print()
    
    # Check GPIO library
    global GPIO
    GPIO = check_gpio_library()
    
    # Setup GPIO
    setup_gpio()
    
    # Register signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n📊 Button State Monitor")
    print("Press the button to see state changes...")
    print("-" * 40)
    
    last_state = GPIO.HIGH  # Start with button not pressed (HIGH)
    press_count = 0
    
    try:
        while True:
            current_state = read_button_state()
            
            # Detect button press (transition from HIGH to LOW)
            if current_state == GPIO.LOW and last_state == GPIO.HIGH:
                press_count += 1
                print(f"🔘 Button PRESSED! (Press #{press_count})")
            
            # Detect button release (transition from LOW to HIGH)
            elif current_state == GPIO.HIGH and last_state == GPIO.LOW:
                print("🔘 Button RELEASED")
            
            last_state = current_state
            
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            
    except KeyboardInterrupt:
        print('\n🛑 Program stopped by user')
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main() 