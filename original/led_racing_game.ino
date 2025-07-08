/*
 * LED Racing Game
 * 
 * A multiplayer racing game using a WS2812B LED strip.
 * 
 * Features:
 * - 4 players racing around a circular track
 * - Each player has a unique color (Red, Blue, Green, Yellow)
 * - The number of LEDs in a player's trail indicates their lap number
 * - Players move forward by random amounts each turn
 * - First player to complete 3 laps wins
 * - Game ends after 60 seconds if no player completes all laps
 * 
 * Game Rules:
 * - Each player starts at the beginning of the track (position 0)
 * - In each turn, players move forward 0-5 steps randomly
 * - When a player reaches the end of the LED strip, they start a new lap
 * - The player's trail length increases with each lap (up to 5 LEDs maximum)
 * - The winner is the first player to complete 3 laps
 * - If time runs out before anyone completes 3 laps, the player who has
 *   advanced the furthest (most laps and position) wins
 * - After a winner is determined, their color flashes for 10 seconds
 * 
 * Hardware:
 * - ESP32 microcontroller
 * - WS2812B LED strip (60 LEDs)
 * - Connect the LED data pin to GPIO 13
 * - Connect the button pin for Player 1 to GPIO 12
 * 
 * Created for ESP32 with FastLED library
 */

#include <FastLED.h>

// Define the data pin connected to the WS2812B strip
#define DATA_PIN 13

// Define the button pins for Player 1, 2, and 3
#define BUTTON_PIN_1 5   // Changed from 12 to 5
#define BUTTON_PIN_2 2   // Changed from 14 to 2
#define BUTTON_PIN_3 39  // Changed from 27 to 39

// Define the number of LEDs in the strip
#define NUM_LEDS 60

// Define the LED type and color order
#define LED_TYPE WS2812B
#define COLOR_ORDER GRB

// Game settings
#define GAME_DURATION 60000           // 1 minute in milliseconds
#define VICTORY_BLINK_DURATION 10000  // 10 seconds in milliseconds
#define BLINK_INTERVAL 250            // Blink every 250ms
#define NUM_PLAYERS 4
#define MAX_PLAYER_SIZE 5  // Maximum number of LEDs per player (for lap indication)
#define LAPS_TO_WIN 3      // Number of laps to win the game

// Create an array to hold the LED data
CRGB leds[NUM_LEDS];

// Player colors
CRGB playerColors[NUM_PLAYERS] = {
  CRGB::Red,
  CRGB::Blue,
  CRGB::Green,
  CRGB::Yellow
};

// Player positions (the leading LED of each player)
int playerPositions[NUM_PLAYERS] = { 0, 0, 0, 0 };
// Player laps
int playerLaps[NUM_PLAYERS] = { 0, 0, 0, 0 };

// Function prototypes
void startNewGame();
void updateGame();
void displayPlayers();
void celebrateWinner(int winner);
int determineWinner();
bool checkForWinner();
void handlePlayerButton(int playerIndex, int buttonPin);
void movePlayer(int playerIndex, int steps);

void setup() {
  // Initialize serial communication for debugging
  Serial.begin(921600);
  Serial.println("ESP32 WS2812B LED Racing Game");

  // Initialize the LED strip
  FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS)
    .setCorrection(TypicalLEDStrip)
    .setDither(true);

  // Set brightness (0-255)
  FastLED.setBrightness(100);

  // Initialize button pins as input with pull-up resistor
  pinMode(BUTTON_PIN_1, INPUT_PULLUP);
  pinMode(BUTTON_PIN_2, INPUT_PULLUP);
  pinMode(BUTTON_PIN_3, INPUT_PULLUP);  // Initialize Player 3 button

  // Initialize random seed
  randomSeed(analogRead(0));

  // Clear all LEDs (turn them off)
  FastLED.clear();
  FastLED.show();

  delay(1000);  // Wait a second before starting

  // Start the first game
  startNewGame();
}

void loop() {
  static unsigned long gameStartTime = millis();
  static bool gameInProgress = true;

  if (gameInProgress) {
    // Check if game time is up or if someone won by completing all laps
    if (millis() - gameStartTime >= GAME_DURATION || checkForWinner()) {
      // Game over, determine winner
      int winner = determineWinner();
      Serial.print("Game over! Winner: Player ");
      Serial.println(winner + 1);

      // Celebrate the winner
      celebrateWinner(winner);

      // Start a new game
      startNewGame();
      gameStartTime = millis();
    } else {
      // Update game state
      updateGame();

      // Display players
      displayPlayers();

      // Small delay between updates
      delay(50);
    }
  }
}

void startNewGame() {
  Serial.println("Starting new game!");

  // Reset player positions and laps
  for (int i = 0; i < NUM_PLAYERS; i++) {
    playerPositions[i] = 0;
    playerLaps[i] = 0;
  }

  // Clear the LED strip
  FastLED.clear();
  FastLED.show();

  // Enhanced countdown animation - count from 10 to 1
  for (int count = 10; count > 0; count--) {
    Serial.print("Starting in ");
    Serial.println(count);

    // Clear previous LEDs
    FastLED.clear();
    
    // Light up LEDs corresponding to the countdown number
    for (int led = 0; led < count; led++) {
      leds[led] = CRGB::White; // Using white color for countdown
    }
    
    FastLED.show();
    delay(500); // Half second per number in countdown
  }

  Serial.println("GO!");
}

void updateGame() {
  // Handle button inputs for Players 1, 2, and 3
  handlePlayerButton(0, BUTTON_PIN_1);
  handlePlayerButton(1, BUTTON_PIN_2);
  handlePlayerButton(2, BUTTON_PIN_3);  // Handle Player 3 button

  // Move other players (only Player 4 now) forward by a random amount
  for (int i = 3; i < NUM_PLAYERS; i++) {
    int steps = random(1, 3);
    movePlayer(i, steps);
  }
}

// Helper function to handle button press for a player
void handlePlayerButton(int playerIndex, int buttonPin) {
  static int lastButtonStates[3] = {HIGH, HIGH, HIGH}; // Store button states for Players 1, 2 & 3
  
  int buttonState = digitalRead(buttonPin);
  
  // Check if button was just pressed (transition from HIGH to LOW with INPUT_PULLUP)
  if (buttonState == LOW && lastButtonStates[playerIndex] == HIGH) {
    // Move player forward by a fixed amount when button is pressed
    int steps = 3; // Changed from 3 to 1 step when button is pressed
    movePlayer(playerIndex, steps);
  }
  
  // Update lastButtonState for next iteration
  lastButtonStates[playerIndex] = buttonState;
}

// Helper function to move a player and handle lap completion
void movePlayer(int playerIndex, int steps) {
  int newPosition = playerPositions[playerIndex] + steps;

  // Check if player completed a lap
  if (newPosition >= NUM_LEDS) {
    playerLaps[playerIndex]++;
    newPosition = newPosition % NUM_LEDS;
    Serial.print("Player ");
    Serial.print(playerIndex + 1);
    Serial.print(" completed lap ");
    Serial.println(playerLaps[playerIndex]);
  }

  playerPositions[playerIndex] = newPosition;

  Serial.print("Player ");
  Serial.print(playerIndex + 1);
  Serial.print(" moved ");
  Serial.print(steps);
  Serial.print(" steps. Now at position ");
  Serial.print(playerPositions[playerIndex]);
  Serial.print(" on lap ");
  Serial.println(playerLaps[playerIndex] + 1);
}

void displayPlayers() {
  // Clear the LED strip
  FastLED.clear();

  // Display each player
  for (int i = 0; i < NUM_PLAYERS; i++) {
    // Calculate player size based on lap (minimum 3, maximum MAX_PLAYER_SIZE)
    int playerSize = min(playerLaps[i] + 3, MAX_PLAYER_SIZE);

    for (int j = 0; j < playerSize; j++) {
      // Calculate position with wrap-around
      int pos = (playerPositions[i] - j + NUM_LEDS) % NUM_LEDS;

      // Fade the trailing LEDs
      int brightness = 255 - (j * 50);
      if (brightness < 0) brightness = 0;

      leds[pos] = playerColors[i];
      leds[pos].fadeToBlackBy(255 - brightness);
    }
  }

  FastLED.show();
}

bool checkForWinner() {
  // Check if any player has completed the required number of laps
  for (int i = 0; i < NUM_PLAYERS; i++) {
    if (playerLaps[i] >= LAPS_TO_WIN) {
      return true;
    }
  }
  return false;
}

int determineWinner() {
  int winnerIndex = 0;
  int maxLaps = playerLaps[0];
  int maxPosition = playerPositions[0];

  // Find the player who completed the most laps
  for (int i = 1; i < NUM_PLAYERS; i++) {
    if (playerLaps[i] > maxLaps || (playerLaps[i] == maxLaps && playerPositions[i] > maxPosition)) {
      maxLaps = playerLaps[i];
      maxPosition = playerPositions[i];
      winnerIndex = i;
    }
  }

  return winnerIndex;
}

void celebrateWinner(int winner) {
  unsigned long startTime = millis();
  bool ledState = true;
  unsigned long lastToggleTime = startTime;

  Serial.print("Celebrating Player ");
  Serial.print(winner + 1);
  Serial.println(" victory!");

  while (millis() - startTime < VICTORY_BLINK_DURATION) {
    // Check if it's time to toggle the LEDs
    if (millis() - lastToggleTime >= BLINK_INTERVAL) {
      lastToggleTime = millis();
      ledState = !ledState;

      if (ledState) {
        // Fill the strip with the winner's color
        fill_solid(leds, NUM_LEDS, playerColors[winner]);
      } else {
        // Turn off all LEDs
        FastLED.clear();
      }

      FastLED.show();
    }
  }

  // Clear the strip after celebration
  FastLED.clear();
  FastLED.show();
}