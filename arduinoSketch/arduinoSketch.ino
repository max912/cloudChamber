void setup() {
  Serial.begin(9600);
};

int i = 0;

void loop() {
  if(Serial.available()) {
    char x = Serial.read();
    if(x == 'r') {
      String json = "'{\"count\":\"1\",\"par1\":\"10\",\"par2\":\"15\",\"par3\":\"-14\",\"par4\":\"4\"}'";
      Serial.println(json);
      i++;
    }
  }
};
