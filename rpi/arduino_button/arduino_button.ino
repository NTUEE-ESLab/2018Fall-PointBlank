int buttonPin = A0;
int interruptPin = 3;
int ackPin = 4;
int statePins[3] = {5, 6, 7}; //statePins[0] is MSB

int voltage = 0;
byte state = 0;
byte prevState = 0;

void setup() {
  // put your setup code here, to run once:
  pinMode(interruptPin, OUTPUT);
  digitalWrite(interruptPin, LOW);
  pinMode(ackPin, INPUT_PULLUP);
  for(int i=0; i<3; ++i)
  {
    pinMode(statePins[i], OUTPUT);
    digitalWrite(statePins[i], LOW);
  }
  
  Serial.begin(9600);
  voltage = analogRead(buttonPin);
}

void loop() {
  // put your main code here, to run repeatedly:

  /* No button pressed = 5V => 1023
   * Button1 = 0V => 0
   * Button2 = 0.15V => 30
   * Button3 = 0.43V => 87
   * Button4 = 0.82V => 165
   * Button5 = 1.74V => 350
   */
   
  prevState = state;
  voltage = analogRead(buttonPin);
  
  if(voltage >= 400)
    state = 0;
  else if( voltage < 400 && voltage >= 300 )
    state = 5;
  else if( voltage < 200 && voltage >= 120 )
    state = 4;
  else if( voltage < 100 && voltage >= 60 )
    state = 3;
  else if( voltage < 50 && voltage >= 15 )
    state = 2;
  else if( voltage < 15 )
    state = 1;
  
  
  if(state != prevState) 
    Serial.write(state);
    
  delay(50);
}
