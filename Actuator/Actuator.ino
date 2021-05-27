#include <Wire.h>
#include <stdlib.h>
#include "HX711.h"

#define SLAVE_ADDR  9
#define DOUT  2
#define CLK  3
#define HEXTEND  7
#define HRETRACT  6
#define EXTEND  10
#define RETRACT  9

float calibration_factor = -7050; //-7050 worked for my 440lb max scale setup

double positionF = 0;
int positionRead = A10;
HX711 scale;

const int speedFactor = 51;

int cycleCount = 0;

bool autoM = false;
bool manual = false;

bool cyclesDone = false;

bool starting = true;

bool ret = false;
bool ext = false;

bool seatHeightInc = false;
bool seatHeightDec = false;

bool autoExt = true;
bool autoRet = false;

bool maxReached = false;

String currentDir = "";
int speedVar = 0;
int cycle = 0;
int maxAngle = 0;
int startingPos = 0;
float a = 0.0;
int count = 0;
int byteArray[5] = {0, 0, 0, 0, 0};
  
void setup() {
Wire.begin(SLAVE_ADDR);
Wire.onRequest(requestEvent);
Wire.onReceive(receiveEvent);
pinMode(positionRead, INPUT);
pinMode(EXTEND, OUTPUT);
pinMode(RETRACT, OUTPUT);
pinMode(HEXTEND, OUTPUT);
pinMode(HRETRACT, OUTPUT);
//Serial.println("hello");
scale.begin(DOUT, CLK);
scale.set_scale();
scale.tare(); //Reset the scale to 0

long zero_factor = scale.read_average(); //Get a baseline reading
Serial.print("Zero factor: "); //This can be used to remove the need to tare the scale. Useful in permanent scale projects.
Serial.println(zero_factor);

positionF = analogRead(positionRead);
while(0.00679*(positionF - 31) > 1) {
    analogWrite(EXTEND, 0);
    analogWrite(RETRACT, 255);
    positionF = analogRead(positionRead);
}
Serial.begin(9600);
}

void receiveEvent(int a) {
  byte x;
  Serial.println("once");
  while(Wire.available()){
        byteArray[count] = Wire.read();
        //Serial.println(Wire.read());
        //Serial.println("while->");
        Serial.println(byteArray[count]);
        count++;
  }


    if (byteArray[0] == 21 && byteArray[4] != 0) {
    count = 0;
    starting = true;
    autoM = true;
    manual = false;
    //Serial.println("Here");
    cycle = byteArray[1];
    maxAngle = byteArray[2];
    speedVar = byteArray[3] * speedFactor;
    startingPos = byteArray[4]; 
    for(int i = 0; i < 5; i++) byteArray[i] = 0;
    //Serial.println(cycle);
    //Serial.println(maxAngle);
    //Serial.println(speedVar);
    //Serial.println(startingPos);          
  } else if(byteArray[0] == 21) {}
  else {
    Serial.println("yes");
    count = 0;
    manual = true;
    autoM = false;
    
    x = byteArray[0];
    for(int i = 0; i < 5; i++) byteArray[i] = 0;
    if (x == 1) {
      ext = false;
      ret = true;
      seatHeightDec = false;
      seatHeightInc = false;
    } else if (x == 2){
      ext = true;
      ret = false;
      seatHeightDec = false;
      seatHeightInc = false;
    } else if (x == 3){
      ext = false;
      ret = false;
    } else if (x == 4){
      if(ext) currentDir = "ext";
      else if(ret)currentDir = "flex";
      seatHeightDec = true;
      seatHeightInc = false;
      ext = false;
      ret = false;
    } else if (x == 5){
      if(ext) currentDir = "ext";
      else if(ret)currentDir = "flex";
      seatHeightInc = true;
      seatHeightDec = false;
      ext = false;
      ret = false;
    } else if (x == 6){
      seatHeightInc = false;
      seatHeightDec = false;
      if(currentDir == "ext"){
        ext = true;
        ret = false;
      }else if (currentDir == "flex") {
        ext = false;
        ret = true;
      }
    }
  }
}

void requestEvent() {
  Serial.println(0.00679*(positionF - 31));
  double positionInAngle = 15.5709343*0.00679*(positionF - 31);
  //Serial.println(positionInAngle);
  Serial.println(positionInAngle);
  int num = positionInAngle*100;
  char str[3];
  
  sprintf(str, "%d", num);

  int result = atoi(str);
  Serial.println(result);
  if (num == 0) str[0] = 'x';
  Wire.write(str);
}

void loop() {
 // adjust position to 0 for the main linear actuator
 
  scale.set_scale(calibration_factor);
  Serial.print("Reading: ");
  a = scale.get_units();
  Serial.print(a, 1);
  Serial.print(" lbs"); //Change this to kg and re-adjust the calibration factor if you follow SI units like a sane person
  Serial.print(" calibration_factor: ");
  Serial.print(calibration_factor);
  Serial.println();

  if(a > 40) {
     analogWrite(EXTEND, 0);
     analogWrite(RETRACT, 0);
     manual = false;
     autoM = false;
    }
  if (manual) {
    if (!seatHeightInc && !seatHeightDec) {
            analogWrite(HEXTEND, 0);
            analogWrite(HRETRACT, 0);
          }

       if (!ext && !ret) {
            analogWrite(EXTEND, 0);
            analogWrite(RETRACT, 0);
          }
   
      if(ext) {
        analogWrite(EXTEND, 255);
        analogWrite(RETRACT, 0);
      } else if(ret) {
        analogWrite(EXTEND, 0);
        analogWrite(RETRACT, 255);
      }  else if(seatHeightDec) {
        analogWrite(HEXTEND, 0);
        analogWrite(HRETRACT, 255);
      } else if(seatHeightInc) {
        analogWrite(HRETRACT, 0);
        analogWrite(HEXTEND, 255);        
      }else {       
        analogWrite(HEXTEND, 0);
        analogWrite(HRETRACT, 0);
        analogWrite(EXTEND, 0);
        analogWrite(RETRACT, 0);
      }
  } else if (autoM) {
    // write automatic movement here 
    //Serial.println("1*");  
    if(starting) cycleCount = 0;
    if (cycleCount == cycle) {
       autoExt = false;
       autoRet = false;
       cyclesDone = true;
        while(0.00679*(positionF - 31) > 0) {
          analogWrite(EXTEND, 0);
          analogWrite(RETRACT, speedVar);
          positionF = analogRead(positionRead);
        }
    }
    
    if(startingPos < int(15.5709343*0.00679*(positionF - 31)) && starting) {
      while(startingPos < int(15.5709343*0.00679*(positionF - 31))) {
        analogWrite(EXTEND, 0);
        analogWrite(RETRACT, speedVar);
        positionF = analogRead(positionRead);
      }
      starting = false;
    } else if (startingPos > int(15.5709343*0.00679*(positionF - 31)) && starting) {
      while(startingPos > int(15.5709343*0.00679*(positionF - 31))) {
        analogWrite(EXTEND, speedVar);
        analogWrite(RETRACT, 0);
        positionF = analogRead(positionRead);
      }
      starting = false;
    }

    if(startingPos == int(15.5709343*0.00679*(positionF - 31)) && !cyclesDone && maxReached) {
       autoExt = true;
       autoRet = false;
       maxReached = false;
       cycleCount++;
    }

    if(startingPos + maxAngle == int(15.5709343*0.00679*(positionF - 31)) && !cyclesDone) {
       autoExt = false;
       autoRet = true;
       maxReached = true;
    }
    
    if(autoExt) {
      analogWrite(EXTEND, speedVar);
      analogWrite(RETRACT, 0);
    }

    if(autoRet) {
      analogWrite(EXTEND, 0);
      analogWrite(RETRACT, speedVar);
    }   
  }  
      Serial.println(cycleCount);
      positionF = analogRead(positionRead);
     // Serial.println(positionF);
     // Serial.println(0.00679*(positionF - 31));
      delay(250);    
}
