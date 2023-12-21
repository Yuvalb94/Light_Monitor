//28.02.2023 this code will read the input out of a photoresistor and write it.
// this code controls a led according to a sensed threshold. below it the led will turn on.
const int ledPin = 13;   //the number of the LED pin
const int ldrPin = A0;  //the number of the LDR pin
int LightThreshold = 725; //threshold for led turn on
 int sampelRate = 100;
void setup() {

 Serial.begin(9600);
  pinMode(ledPin, OUTPUT);  //initialize the LED pin as an output
  pinMode(ldrPin, INPUT);   //initialize the LDR pin as an input

}

void loop() {
 int ldrStatus = analogRead(ldrPin);   //read the status of the LDR value
 
Serial.println(ldrStatus);
delay(sampelRate); // sample rate, of 1 sample every 100ms

  //check if the LDR status is <= 300
  //if it is, the LED is HIGH

   if (ldrStatus <=LightThreshold) {

    digitalWrite(ledPin, HIGH);               //turn LED on
    Serial.println("LDR is DARK, LED is ON");
    
   }
  else {

    digitalWrite(ledPin, LOW);          //turn LED off
    Serial.println("---------------");
  }


}
