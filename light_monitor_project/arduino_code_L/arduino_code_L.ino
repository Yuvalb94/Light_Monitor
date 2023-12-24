//18.12.2023 this code will read the input out of a photoresistor and send it to RasPi it in order to monitor light conditions.
const int ldrPin = A0;  //the number of the LDR pin
int sampelRate = 1000; //sample rate - 1 sample every 1000ms
void setup() {

 Serial.begin(9600);
  pinMode(ldrPin, INPUT);   //initialize the LDR pin as an input

}

void loop() {
 int ldrStatus = analogRead(ldrPin);   //read the status of the LDR value
 
Serial.println(ldrStatus);
delay(sampelRate); // sample rate, of 1 sample every 100ms



}
