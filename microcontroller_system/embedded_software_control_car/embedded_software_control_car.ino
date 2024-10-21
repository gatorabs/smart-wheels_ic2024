#include <ESP32Servo.h>
#include "BluetoothSerial.h"

Servo dir_servo;
BluetoothSerial SerialBT;


#define RPM_A 32
#define RPM_B 14


#define IN1 33
#define IN2 25
#define IN3 27
#define IN4 26
int speed = 80;
int angle = 0;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  SerialBT.begin("smartwheels_mini_kart");
  dir_servo.attach(35);

  pinMode(RPM_A, OUTPUT);
  pinMode(RPM_B, OUTPUT);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  analogWrite(RPM_A, speed);
  analogWrite(RPM_B, speed);
}

void loop() {
  
  if (Serial.available() > 0) {  
        String input = Serial.readStringUntil('\n'); 
        angle = input.toInt(); 

        
        if (angle < 60) angle = 60;
        if (angle > 140) angle = 140;

        dir_servo.write(angle); 
        Serial.print("Ângulo recebido: "); 
        Serial.println(angle);
    }
}


void motor_control(int m1_a, int m1_b, int m2_a, int m2_b){
  digitalWrite(IN1, m1_a);
  digitalWrite(IN2, m1_b);
  digitalWrite(IN3, m2_a);
  digitalWrite(IN4, m2_b);

    
  
}


void bluetooth_mode(){
  if(SerialBT.available()){
    char incomingByte = SerialBT.read();
    
    Serial.println(incomingByte);
    switch(incomingByte){
      case 'f':
        motor_control(1,0,1,0);
        
        
        break;
      case 'b':
        motor_control(0,1,0,1);
        break;
      case 'd':
        dir_servo.write(140);
        break;
      case 'a':
        dir_servo.write(60);
        break;
      case 'q':
        dir_servo.write(90);
        motor_control(0,0,0,0);
        break;
        
    }
  }
}