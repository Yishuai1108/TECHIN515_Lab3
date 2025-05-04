#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// OLED settings
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Button pin definitions
#define BUTTON_A 14
#define BUTTON_B 27
#define BUTTON_C 26
#define BUTTON_D 25

// Array to store responses (1=A, 2=B, 3=C, 4=D)
int userResponses[10] = {0}; // Initialize with zeros
int currentQuestion = 0;
bool quizCompleted = false;
bool quizStarted = false;

// Questions for the sorting quiz
const char* questions[] = {
    "1. What do you value?",
    "2. What to do if someone cheats?",
    "3. Favorite subject?",
    "4. How do you face challenges?",
    "5. How do friends describe you?",
    "6. What to do with a mystery book?",
    "7. Preferred pet?",
    "8. How do you solve problems?",
    "9. What kind of friends do you like?",
    "10. Dream career?"
};

// Answer Options
const char* options[][4] = {
    {"A) Bravery", "B) Loyalty", "C) Intelligence", "D) Ambition"},
    {"A) Call them out", "B) Let them be", "C) Inform teacher", "D) Gain from it"},
    {"A) Defense Arts", "B) Herbology", "C) Charms", "D) Potions"},
    {"A) Face head-on", "B) Team up", "C) Plan first", "D) Outsmart it"},
    {"A) Bold", "B) Kind", "C) Smart", "D) Resourceful"},
    {"A) Read it now", "B) Check safety", "C) Study it", "D) Use for gain"},
    {"A) Owl", "B) Toad", "C) Cat", "D) Phoenix"},
    {"A) Act fast", "B) Find a compromise", "C) Analyze first", "D) Outsmart"},
    {"A) Adventurous", "B) Loyal", "C) Thoughtful", "D) Powerful"},
    {"A) Auror", "B) Healer", "C) Scholar", "D) Minister"}
};

// House names
const char* houses[] = {"Gryffindor", "Hufflepuff", "Ravenclaw", "Slytherin"};

// Function prototypes
void displayWelcome();
void displayQuestion(int questionNum);
void checkButtons();
String determineHouse();
void displayResult(String house);
void resetQuiz();

void setup() {
  Serial.begin(115200);
  
  // Initialize OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED init failed!");
    for (;;);
  }
  
  // Set buttons as input with internal pull-up
  pinMode(BUTTON_A, INPUT_PULLUP);
  pinMode(BUTTON_B, INPUT_PULLUP);
  pinMode(BUTTON_C, INPUT_PULLUP);
  pinMode(BUTTON_D, INPUT_PULLUP);
  
  // Display welcome screen
  displayWelcome();
}

void loop() {
  // Start quiz when any button is pressed
  if (!quizStarted && !quizCompleted) {
    if (digitalRead(BUTTON_A) == LOW || digitalRead(BUTTON_B) == LOW || 
        digitalRead(BUTTON_C) == LOW || digitalRead(BUTTON_D) == LOW) {
      delay(300); // Debounce
      quizStarted = true;
      displayQuestion(currentQuestion);
    }
  }
  // Check for button presses during the quiz
  else if (quizStarted && !quizCompleted) {
    checkButtons();
  }
  // After quiz is complete, check for restart
  else if (quizCompleted) {
    if (digitalRead(BUTTON_A) == LOW || digitalRead(BUTTON_B) == LOW || 
        digitalRead(BUTTON_C) == LOW || digitalRead(BUTTON_D) == LOW) {
      delay(300); // Debounce
      resetQuiz();
    }
  }
}

void displayWelcome() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Hogwarts House");
  display.println("Sorting Quiz");
  display.println();
  display.println("Press any button");
  display.println("to begin");
  display.display();
}

void displayQuestion(int questionNum) {
  display.clearDisplay();
  display.setCursor(0, 0);
  display.setTextSize(1);
  
  // Display question
  display.println(questions[questionNum]);
  display.println();
  
  // Display options
  for (int i = 0; i < 4; i++) {
    display.println(options[questionNum][i]);
  }
  
  display.display();
}

void checkButtons() {
  static unsigned long lastDebounceTime = 0;
  unsigned long debounceDelay = 300; // Debounce time in milliseconds
  
  // Only check for a new button press if enough time has passed
  if ((millis() - lastDebounceTime) > debounceDelay) {
    int buttonPressed = 0;
    
    // Check each button (1=A, 2=B, 3=C, 4=D)
    if (digitalRead(BUTTON_A) == LOW) buttonPressed = 1;
    else if (digitalRead(BUTTON_B) == LOW) buttonPressed = 2;
    else if (digitalRead(BUTTON_C) == LOW) buttonPressed = 3;
    else if (digitalRead(BUTTON_D) == LOW) buttonPressed = 4;
    
    // If a button was pressed
    if (buttonPressed > 0) {
      lastDebounceTime = millis(); // Reset debounce timer
      
      // Store the response (1-4)
      userResponses[currentQuestion] = buttonPressed;
      
      // Debug output
      Serial.print("Question ");
      Serial.print(currentQuestion + 1);
      Serial.print(" answered: ");
      Serial.println(buttonPressed);
      
      // Move to next question or show result
      currentQuestion++;
      
      if (currentQuestion < 10) {
        displayQuestion(currentQuestion);
      } else {
        // All questions answered, determine the house
        String house = determineHouse();
        displayResult(house);
        quizCompleted = true;
        quizStarted = false;
      }
    }
  }
}

String determineHouse() {
  // Count responses for each house tendency
  int counts[4] = {0}; // [Gryffindor, Hufflepuff, Ravenclaw, Slytherin]
  
  for (int i = 0; i < 10; i++) {
    // Increment the counter for the house corresponding to the answer
    // A answers (1) increment Gryffindor counter
    // B answers (2) increment Hufflepuff counter 
    // C answers (3) increment Ravenclaw counter
    // D answers (4) increment Slytherin counter
    if (userResponses[i] > 0 && userResponses[i] <= 4) {
      counts[userResponses[i] - 1]++;
    }
  }
  
  // Find the house with the most answers
  int maxCount = 0;
  int maxHouse = 0;
  
  for (int i = 0; i < 4; i++) {
    if (counts[i] > maxCount) {
      maxCount = counts[i];
      maxHouse = i;
    }
  }
  
  // Return the house name
  return String(houses[maxHouse]);
}

void displayResult(String house) {
  display.clearDisplay();
  display.setCursor(0, 0);
  
  display.setTextSize(1);
  display.println("The Sorting Hat says:");
  display.println();
  
  display.setTextSize(2);
  display.println(house);
  display.println();
  
  display.setTextSize(1);
  display.println("Press any button");
  display.println("to restart");
  
  display.display();
  
  // Send result to Serial
  Serial.print("Sorted into house: ");
  Serial.println(house);
  
  // Print all answers
  Serial.println("User responses:");
  for (int i = 0; i < 10; i++) {
    Serial.print("Q");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.println(userResponses[i]);
  }
}

void resetQuiz() {
  // Reset all responses
  for (int i = 0; i < 10; i++) {
    userResponses[i] = 0;
  }
  
  currentQuestion = 0;
  quizCompleted = false;
  quizStarted = false;
  
  // Return to welcome screen
  displayWelcome();
}