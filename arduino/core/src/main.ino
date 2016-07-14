#include <OneWire.h>
#include <dht.h>
#include <DallasTemperature.h>


//Pins definition
int tempPin = A0;
int lightPin = A1;
int waterFlowPin = 2;
int lightDevicePin = 7;
int pumpDevicePin = 8;
//int flashDevicePin = 6;
int waterTempPin = 10;

#define DHT11_PIN 4

//Handle cmd  vars
String charStream;
char defaultDelimiter = '/';
#define MAX_CMD_SIZE 10

int loopDelay = 60000;

dht DHT;

OneWire oneWire(waterTempPin);
DallasTemperature waterTempWrapper(&oneWire);

byte sensorInterrupt = 0;

typedef struct reading 
{
	String name;
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
  
	pinMode(lightDevicePin, OUTPUT);
	//In relay HIGH means no current
	digitalWrite(lightDevicePin, HIGH);
  
	pinMode(pumpDevicePin, OUTPUT);
	//In relay HIGH means no current
	digitalWrite(pumpDevicePin, HIGH);
	
	//pinMode(flashDevicePin, OUTPUT);
	//In relay HIGH means no current
	//digitalWrite(pumpDevicePin, HIGH);

	waterTempWrapper.begin();
}

void loop()
{
	if(Serial.available() > 0)
	{
		char received = Serial.read();
		if(received == '\n')
		{
			charStream.trim();
			handleInputStream(charStream);
			charStream = "";
		}
		
		charStream += received;
	}
  
}


void executeSensorCmd(String cmd[])
{
	if(cmd[1] == "get")
	{
		//Needed for generateJsonMessage, since there are exceptions like waterFlow sensor
		int numberOfReadings = 1;
		readings[0].name = cmd[2];
		
		//Regular readings
		if(cmd[2] == "temp")
		{
			readings[0].value = readTemperature();
		} else if(cmd[2] == "light")
		{
			readings[0].value = readLight();
		} else if(cmd[2] == "waterTemp")
		{
			readings[0].value = readWaterTemp();
		} 
		//Readings with multiple values
		else
		{
			if(cmd[2] == "DHT")
			{
				readings[0].name = "temp";
				readings[1].name = "humidity";

				readDHT(readings[0].value, readings[1].value);
			} else if(cmd[2] == "waterFlow")
			{
				readings[0].name = "current";
				readings[1].name = "total";

				readWaterFlow(readings[0].value, readings[1].value);  
			}
			numberOfReadings = 2;
		}

		String res = generateJsonMessage(cmd[2], readings, numberOfReadings);
		Serial.print(res);
		Serial.flush();
	}
}

void executeDeviceCmd(String cmd[])
{
	int pin;
	
	if(cmd[1] == "light")
	{
		pin = lightDevicePin;	
	}
	else if(cmd[1] == "water_pump")
	{
		pin = pumpDevicePin;
	}
	//else if(cmd[1] == "flash")
	//{
	//	pin = flashDevicePin;
	//}
	
	int value = cmd[2] == "on" ? 0 : 1;
	
	digitalWrite(pin, value);
}

void handleCommand(String cmd[])
{
	if(cmd[0] == "sensor")
	{
		executeSensorCmd(cmd);
	}
	else if(cmd[0] == "device")
	{
		executeDeviceCmd(cmd);
	}
}

void handleInputStream(String stream)
{
	int nextDelimiter = stream.indexOf(defaultDelimiter);

	String commands[MAX_CMD_SIZE];	
	int cmdCount = 0;

	while(nextDelimiter > -1)
	{
		commands[cmdCount] = stream.substring(0, nextDelimiter);
		/*Serial.print(commands[cmdCount]);
		Serial.print('\n');*/
	
		stream = stream.substring(nextDelimiter + 1);
		//nextDelimiter = stream.substring(defaultDelimiter);
		nextDelimiter = stream.indexOf(defaultDelimiter);
		cmdCount++;
	}
	commands[cmdCount] = stream;
	
	handleCommand(commands);
}

String generateJsonMessage(String fieldName, reading_t* readings, int n)
{
	String res = "";
 
	res += "{\"sensor\":{\"";
	res += fieldName;
	res += "\":{";
  
	for(int i = 0; i < n; i++)
	{
		if(i != 0)
	  	res += ",";

		res += "\"";

		res += readings[i].name;
		res += "\":";
		res += readings[i].value;
  	}

  	res += "}}}\n";

  	return res;

}

float readWaterTemp()
{
	waterTempWrapper.requestTemperatures();
	return waterTempWrapper.getTempCByIndex(0);
}

float readLight()
{
	return analogRead(lightPin);
}

void readDHT(float& temp, float& humidity)
{
	int chk = DHT.read11(DHT11_PIN);
  
  	temp = (float)DHT.temperature;
	humidity = (float)DHT.humidity;
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
  
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
  pulseCount = 0;
  
  currentFlowRate = flowRate;
  totalFlow = totalMilliLitres;
}

void pulseCounter()
{
  pulseCount++;
}
