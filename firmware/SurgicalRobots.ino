
// Adafruit Motor Shield V2 Library - Version: Latest 
#include <Adafruit_MotorShield.h>

#include <Wire.h>
// #include "utility/Adafruit_PWMServoDriver.h"

#define NUM_SENSORS 3
int const sensorPins[3] = {A0, A1, A2};
long const samplingTimeInUs = 2;

Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
Adafruit_StepperMotor *loadMotor;
int position = 0;

int force = 0;

void setup() {
  
  // TODO: Permorm ADC Calibration
  Serial.begin(115200);
  loadMotor = AFMS.getStepper(200, 2);
}

void move(int increments){
  
  if(increments > 0)
    loadMotor.step(increments, FORWARD);
  else
    loadMotor.step(-increments, BACKWARD)
}

void loop() {
  
  auto startTime =  micros();
  
  auto sensorValues[NUM_SENSORS] = {0}; 
  for(auto i = 0; i < NUM_SENSORS; i++){
    sensorValues[i] = analogRead(sensorPins[i]);
  }
  
  while (Serial.available() > 0) {
    increments = Serial.parseInt();
    move(increments);
  }
  
  Serial.print(startTime);
  Serial.print(" ");
  Serial.print(force);
  Serial.print(" ")
  for(auto i = 0; i < NUM_SENSORS; i++){
    Serial.print(sensorValues[i]);
    Serial.print(" ");
  }
  
  auto sleepTime =  samplingTimeInUs - (micros() - startTime);
  if(sleepTime > 0){
    delayMicroseconds(sleepTime);
  }
  
}
