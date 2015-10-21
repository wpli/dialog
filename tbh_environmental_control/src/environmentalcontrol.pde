/***********************************************************************/
/*   Listens for command over serial port, either 1,2,3,4,5,6 or N     */
/*   Numbers turn a pin(see below) and N turns all to LOW              */
/*   Email snowak77@gmail.com if you have questions                    */
/*   Created by Sebastian Nowak for CSAIL, July 2011                   */
/***********************************************************************/
int oneOn = 13;  // output pins 
int oneOff = 12;
int twoOn = 11;
int twoOff = 10;
int threeOn = 9;
int threeOff = 8;

int val = 0;      // variable for reading the pin status  
char msg = '  ';   // variable to hold data from serial  

void setup() {  // acctivates output pins
  pinMode(oneOn, OUTPUT); 
  pinMode(oneOff, OUTPUT); 
  pinMode(twoOn, OUTPUT);
  pinMode(twoOff, OUTPUT);
  pinMode(threeOn, OUTPUT);
  pinMode(threeOff, OUTPUT);


  Serial.begin(9600);  
  Serial.print("Program Initiated\n");  
}  

void loop(){  
  // While data is sent over serial assign it to the msg  
  while (Serial.available()>0){  
    msg=Serial.read();  
    digitalWrite(oneOn, LOW);
    digitalWrite(oneOff, LOW); 
    digitalWrite(twoOn, LOW); 
    digitalWrite(twoOff, LOW); 
    digitalWrite(threeOn, LOW); 
    digitalWrite(threeOff, LOW);   

  }  

  // Turn LED on/off if we recieve 'Y'/'N' over serial  
  if (msg=='1') {  
    digitalWrite(oneOn, HIGH);              
    msg==' '; 
  } 
  else if (msg=='2') {  
    digitalWrite(oneOff, HIGH);
    msg==' ';
  } 
  else if (msg=='3') {  
    digitalWrite(twoOn, HIGH);
    msg==' ';
  } 
  else if (msg=='4') {  
    digitalWrite(twoOff, HIGH);
    msg==' ';
  }
     
  else if (msg=='5') {  
    digitalWrite(threeOn, HIGH);
    msg==' ';
  } 
  else if (msg=='6') {  
    digitalWrite(threeOff, HIGH);
    msg==' ';
  }
  else if (msg=='N') {  
    digitalWrite(oneOn, LOW);
    digitalWrite(oneOff, LOW); 
    digitalWrite(twoOn, LOW); 
    digitalWrite(twoOff, LOW); 
    digitalWrite(threeOn, LOW); 
    digitalWrite(threeOff, LOW);
 
    msg==' ';
  } 
} 


