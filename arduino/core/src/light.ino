#include<math.h>
#include<stdio.h>

int tempPin = 0;
int lightPin = 1;
int waterFlowPin = 2;

byte sensorInterrupt = 0;

typedef struct reading 
{
  char* name;
  float value;
} reading_t;

reading_t readings[2];

void setup()
{
  Serial.begin(9600);
  
  //Setup the water flow sensor
  pinMode(waterFlowPin, INPUT);
  digitalWrite(waterFlowPin, HIGH);
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
}

void loop()
{
  readings[0].name = "temp"; 
  readings[0].value = readTemperature();
  generateJsonMessage("temp", readings, 1);

  readings[0].name = "light"; 
  readings[0].value = readLight();
  generateJsonMessage("light", readings, 1);

    
  float currentFlowRate, totalFlow;
  
  readWaterFlow(currentFlowRate, totalFlow);
  
  readings[0].name = "current";
  readings[1].name = "total";

  readWaterFlow(readings[0].value, readings[1].value);  

  generateJsonMessage("waterFlow", readings, 2);

  delay(60000);
}


void generateJsonMessage(char* fieldName, reading_t* readings, int n)
{
  Serial.print("{\"sensor\":{\"");
  Serial.print(fieldName);
  Serial.print("\":{");
  //Serial.print("\":[");
 
  for(int i = 0; i < n; i++)
  {
    if(i != 0)
      Serial.print(",");

    Serial.print("\"");
    //Serial.print("{\"");

    Serial.print(readings[i].name);
    Serial.print("\":");
    Serial.print(readings[i].value);

    //Serial.print("}");
  }

  Serial.print("}}}\n");
 
  //Serial.print("]}}\n");
  
  Serial.flush();
}

float readLight()
{
  return analogRead(lightPin);
}

float readTemperature()
{
  int reading = analogRead(tempPin);
  
  float voltage = reading * 5.0;
  voltage /= 1024.0;
  
  float temperature = (voltage - 0.5) * 100;
  
  return temperature;
}

unsigned long lastReadTime = 0;
volatile byte pulseCount = 0;
float calibrationFactor = 7.2; //8.55;
float flowRate = 0;
float flowMilliLitres = 0;
float totalMilliLitres = 0;

void readWaterFlow(float& currentFlowRate, float& totalFlow)
{
  detachInterrupt(sensorInterrupt);
  
  flowRate = ((1000.0 / (millis() - lastReadTime)) * pulseCount) / calibrationFactor;
  lastReadTime = millis();
  
  if(isnan(flowRate) == 1)
  {
    flowRate = 0;
  }
  
  flowMilliLitres = (flowRate / 60) * 1000;
  
  totalMilliLitres += flowMilliLitres;
  
  //Serial.print('flowRate='); Serial.println(flowRate);
  //Serial.print('lastReadTime='); Serial.println(lastReadTime);
  //Serial.print('flowMl='); Serial.println(flowMilliLitres);
  
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
  pulseCount = 0;
  
  //Serial.print("totalFlow="); Serial.println(totalMilliLitres);
  
  currentFlowRate = flowRate;
  totalFlow = totalMilliLitres;
  
  //return flowRate;
}

void pulseCounter()
{
  pulseCount++;
}


// vim: tabstop=2 expandtab
