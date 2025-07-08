#!/usr/bin/env python3
"""
WS2812 LED Strip Controller for Raspberry Pi

This program controls a WS2812 LED strip connected to GPIO 21 (BCM).
The strip should be powered with 5V and data connected to GPIO 21.

Features:
- Individual LED control
- Color patterns and animations
- Brightness control
- Rainbow effects
- Chase patterns

Author: Raspberry Pi LED Racer Project
"""

import time
import sys
import signal
import random
from typing import Tuple

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n🛑 Program stopped by user')
    cleanup()
    sys.exit(0)

def cleanup():
    """Clean up LED strip and GPIO resources"""
    try:
        if 'strip' in globals():
            strip.clear()
            strip.show()
        print("✅ LED strip cleared and GPIO cleanup completed")
    except:
        pass

def check_ws281x_library():
    """Check if rpi_ws281x library is available"""
    try:
        from rpi_ws281x import PixelStrip, Color
        print("✅ rpi_ws281x library is available")
        return PixelStrip, Color
    except ImportError:
        print("❌ rpi_ws281x library not found")
        print("Install it with: pip install rpi_ws281x")
        sys.exit(1)

class WS2812Controller:
    def __init__(self, led_count=240, pin=21, freq_hz=800000, dma=10, 
                 invert=False, brightness=255, channel=0):
        """
        Initialize WS2812 LED strip controller
        
        Args:
            led_count: Number of LEDs in the strip
            pin: GPIO pin number (BCM)
            freq_hz: LED signal frequency in Hz
            dma: DMA channel to use
            invert: Invert signal (required for some strips)
            brightness: LED brightness (0-255)
            channel: PWM channel (0 or 1)
        """
        self.led_count = led_count
        self.brightness = brightness
        
        # Import libraries
        PixelStrip, Color = check_ws281x_library()
        self.Color = Color
        
        # Initialize the strip
        self.strip = PixelStrip(
            led_count, pin, freq_hz, dma, invert, brightness, channel
        )
        self.strip.begin()
        
        print(f"✅ WS2812 LED strip initialized")
        print(f"   LEDs: {led_count}")
        print(f"   Pin: GPIO {pin}")
        print(f"   Brightness: {brightness}")
    
    def set_pixel(self, pixel_id: int, color: Tuple[int, int, int]):
        """Set a single pixel to a specific color"""
        if 0 <= pixel_id < self.led_count:
            r, g, b = color
            self.strip.setPixelColor(pixel_id, self.Color(r, g, b))
    
    def set_all_pixels(self, color: Tuple[int, int, int]):
        """Set all pixels to the same color"""
        r, g, b = color
        for i in range(self.led_count):
            self.strip.setPixelColor(i, self.Color(r, g, b))
    
    def clear(self):
        """Turn off all LEDs"""
        self.set_all_pixels((0, 0, 0))
        self.strip.show()
    
    def show(self):
        """Update the LED strip with current pixel values"""
        self.strip.show()
    
    def set_brightness(self, brightness: int):
        """Set the brightness of all LEDs (0-255)"""
        self.brightness = max(0, min(255, brightness))
        self.strip.setBrightness(self.brightness)
    
    def color_wipe(self, color: Tuple[int, int, int], wait_ms=50):
        """Wipe color across display a pixel at a time"""
        for i in range(self.led_count):
            self.set_pixel(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
    
    def theater_chase(self, color: Tuple[int, int, int], wait_ms=50, iterations=10):
        """Movie theater light style chaser animation"""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.led_count, 3):
                    self.set_pixel(i + q, color)
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.led_count, 3):
                    self.set_pixel(i + q, (0, 0, 0))
    
    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once"""
        for j in range(256 * iterations):
            for i in range(self.led_count):
                self.set_pixel(i, self.wheel((i + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
    
    def rainbow_cycle(self, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels"""
        for j in range(256 * iterations):
            for i in range(self.led_count):
                self.set_pixel(i, self.wheel((int(i * 256 / self.led_count) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
    
    def wheel(self, pos: int) -> Tuple[int, int, int]:
        """Generate rainbow colors across 0-255 positions"""
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)
    
    def breathing_effect(self, color: Tuple[int, int, int], cycles=3):
        """Create a breathing effect with the specified color"""
        for cycle in range(cycles):
            # Fade in
            for brightness in range(0, 255, 5):
                self.set_brightness(brightness)
                self.set_all_pixels(color)
                self.strip.show()
                time.sleep(0.02)
            
            # Fade out
            for brightness in range(255, 0, -5):
                self.set_brightness(brightness)
                self.set_all_pixels(color)
                self.strip.show()
                time.sleep(0.02)
        
        # Reset brightness
        self.set_brightness(255)
    
    def random_colors(self, duration=10):
        """Display random colors for specified duration"""
        start_time = time.time()
        while time.time() - start_time < duration:
            for i in range(self.led_count):
                color = (random.randint(0, 255), 
                        random.randint(0, 255), 
                        random.randint(0, 255))
                self.set_pixel(i, color)
            self.strip.show()
            time.sleep(0.1)
    
    def police_lights(self, duration=10):
        """Simulate police lights (red and blue alternating)"""
        start_time = time.time()
        while time.time() - start_time < duration:
            # Red
            self.set_all_pixels((255, 0, 0))
            self.strip.show()
            time.sleep(0.2)
            
            # Off
            self.set_all_pixels((0, 0, 0))
            self.strip.show()
            time.sleep(0.1)
            
            # Blue
            self.set_all_pixels((0, 0, 255))
            self.strip.show()
            time.sleep(0.2)
            
            # Off
            self.set_all_pixels((0, 0, 0))
            self.strip.show()
            time.sleep(0.1)

def demo_sequence(controller: WS2812Controller):
    """Run a demo sequence of various LED effects"""
    print("\n🎭 Running LED Demo Sequence")
    print("=" * 40)
    
    # Color wipe effects
    print("🔴 Red wipe...")
    controller.color_wipe((255, 0, 0), 50)
    
    print("🟢 Green wipe...")
    controller.color_wipe((0, 255, 0), 50)
    
    print("🔵 Blue wipe...")
    controller.color_wipe((0, 0, 255), 50)
    
    # Theater chase
    print("🎬 Theater chase...")
    controller.theater_chase((127, 127, 127), 50, 3)
    
    # Rainbow effects
    print("🌈 Rainbow...")
    controller.rainbow(20, 1)
    
    print("🌈 Rainbow cycle...")
    controller.rainbow_cycle(20, 2)
    
    # Breathing effect
    print("💨 Breathing effect...")
    controller.breathing_effect((255, 100, 100), 2)
    
    # Random colors
    print("🎲 Random colors...")
    controller.random_colors(3)
    
    # Police lights
    print("🚔 Police lights...")
    controller.police_lights(3)
    
    # Clear
    controller.clear()
    print("✅ Demo complete!")

def main():
    """Main program"""
    print("🎨 WS2812 LED Strip Controller")
    print("=" * 35)
    print("Press Ctrl+C to exit")
    print()
    
    # Register signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize LED controller
        # Adjust led_count based on your strip length
        controller = WS2812Controller(led_count=30, pin=21, brightness=128)
        
        # Run demo sequence
        demo_sequence(controller)
        
        print("\n🎮 Interactive Mode")
        print("Commands:")
        print("  'demo' - Run demo sequence")
        print("  'clear' - Turn off all LEDs")
        print("  'red', 'green', 'blue' - Set all LEDs to color")
        print("  'rainbow' - Start rainbow effect")
        print("  'police' - Police lights effect")
        print("  'random' - Random colors")
        print("  'brightness <0-255>' - Set brightness")
        print("  'quit' - Exit program")
        print("-" * 40)
        
        while True:
            try:
                command = input("Enter command: ").strip().lower()
                
                if command == 'quit':
                    break
                elif command == 'demo':
                    demo_sequence(controller)
                elif command == 'clear':
                    controller.clear()
                    print("✅ LEDs cleared")
                elif command == 'red':
                    controller.set_all_pixels((255, 0, 0))
                    controller.show()
                    print("🔴 All LEDs set to red")
                elif command == 'green':
                    controller.set_all_pixels((0, 255, 0))
                    controller.show()
                    print("🟢 All LEDs set to green")
                elif command == 'blue':
                    controller.set_all_pixels((0, 0, 255))
                    controller.show()
                    print("🔵 All LEDs set to blue")
                elif command == 'rainbow':
                    print("🌈 Starting rainbow effect (Ctrl+C to stop)")
                    controller.rainbow_cycle(20, 10)
                elif command == 'police':
                    print("🚔 Starting police lights (Ctrl+C to stop)")
                    controller.police_lights(10)
                elif command == 'random':
                    print("🎲 Starting random colors (Ctrl+C to stop)")
                    controller.random_colors(10)
                elif command.startswith('brightness '):
                    try:
                        brightness = int(command.split()[1])
                        controller.set_brightness(brightness)
                        print(f"💡 Brightness set to {brightness}")
                    except (IndexError, ValueError):
                        print("❌ Invalid brightness value. Use: brightness <0-255>")
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n🛑 Stopping current effect...")
                controller.clear()
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main() 