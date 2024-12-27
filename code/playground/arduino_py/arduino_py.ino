#include <Servo.h>

Servo servoX; // Servo for pan (horizontal)
Servo servoY; // Servo for tilt (vertical)

void setup() {
  Serial.begin(9600);
  servoX.attach(9); // Connect to pin D9
  servoY.attach(10); // Connect to pin D10
  servoX.write(90);  // Initial position
  servoY.write(90);  // Initial position
}


void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n'); // Read data from Python
    int delimiterIndex = data.indexOf(',');    // Find the comma delimiter
    if (delimiterIndex > 0) {
      int angleX = data.substring(0, delimiterIndex).toInt();
      int angleY = data.substring(delimiterIndex + 1).toInt();

      // Constrain angles to servo limits (0-180)
      angleX = constrain(angleX, 0, 180);
      angleY = constrain(angleY, 0, 180);

      servoX.write(angleX);
      servoY.write(angleY);
    }
  }
}
