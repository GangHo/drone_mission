#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <Servo.h>
#include <WiFiClient.h>

#include "HUSKYLENS.h"
#include "SoftwareSerial.h"

// WEB
HTTPClient http;
WiFiClient client;

// HUSKYLENS
HUSKYLENS huskylens;

// HUSKYLENS 객체생성
void printResult(HUSKYLENSResult result);

// WiFi ID,PW
const char* ssid = "JSTWIFI";
const char* pass = "abc12345";

// Servo Motors
Servo servo1;
Servo servo2;
Servo servo3;

void Bucket1_open() {
  servo1.write(0);
  delay(100);
  Serial.println("s1Open");
}

void Bucket2_open() {
  servo2.write(0);
  delay(100);
  Serial.println("s2Open");
}

void Bucket3_open() {
  servo3.write(0);
  delay(100);
  Serial.println("s3Open");
}

void Bucket1_close() {
  servo1.write(180);
  delay(100);
  Serial.println("s1Close");
}

void Bucket2_close() {
  servo2.write(180);
  delay(100);
  Serial.println("s2Close");
}

void Bucket3_close() {
  servo3.write(180);
  delay(100);
  Serial.println("s3Close");
}

void Detect_Patient1(HUSKYLENSResult result) {
  if (result.command == COMMAND_RETURN_BLOCK) {
    Serial.println(String() + F("Block:xCenter=") + result.xCenter + F(",yCenter=") + result.yCenter + F(",width=") + result.width + F(",height=") + result.height + F(",ID=") + result.ID);
  }
  // 일정 범위 이상이 되면 감지 가능
  if ((String)result.width >= (String) "100" && (String)result.height >= (String) "120") {
    http.begin(client, "http://medicinedb.codedbyjst.com/PatientInfo/100");
    http.GET();
    DynamicJsonDocument doc(2048);
    deserializeJson(doc, http.getStream());
    http.end();
    if ((String)result.ID == (String)doc["FaceID"]) {
      Bucket1_open();
      http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo/update?BucketState=delivery_100_open");
      http.GET();
      http.end();
      while (1) {
        http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
        http.GET();
        deserializeJson(doc, http.getStream());
        http.end();
        delay(100);
        if (!strcmp("delivery_100_end", (const char*)doc["BucketState"])) {
          Bucket1_close();
          break;
        }
        Serial.println("Wait for touching");
      }
    }
  }
  Serial.println("Not in the Area");
}

void Detect_Patient2(HUSKYLENSResult result) {
  if (result.command == COMMAND_RETURN_BLOCK) {
    Serial.println(String() + F("Block:xCenter=") + result.xCenter + F(",yCenter=") + result.yCenter + F(",width=") + result.width + F(",height=") + result.height + F(",ID=") + result.ID);
  }
  // 일정 범위 이상이 되면 감지 가능
  if ((String)result.width >= (String) "100" && (String)result.height >= (String) "120") {
    http.begin(client, "http://medicinedb.codedbyjst.com/PatientInfo/101");
    http.GET();
    DynamicJsonDocument doc(2048);
    deserializeJson(doc, http.getStream());
    http.end();
    if ((String)result.ID == (String)doc["FaceID"]) {
      Bucket2_open();
      http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo/update?BucketState=delivery_101_open");
      http.GET();
      http.end();
      while (1) {
        http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
        http.GET();
        deserializeJson(doc, http.getStream());
        http.end();
        delay(100);
        if (!strcmp("delivery_101_end", (const char*)doc["BucketState"])) {
          Bucket2_close();
          break;
        }
        Serial.println("Wait for touching");
      }
    }
  }
  Serial.println("Not in the Area");
}

void Detect_Patient3(HUSKYLENSResult result) {
  if (result.command == COMMAND_RETURN_BLOCK) {
    Serial.println(String() + F("Block:xCenter=") + result.xCenter + F(",yCenter=") + result.yCenter + F(",width=") + result.width + F(",height=") + result.height + F(",ID=") + result.ID);
  }
  // 일정 범위 이상이 되면 감지 가능
  if ((String)result.width >= (String) "100" && (String)result.height >= (String) "120") {
    http.begin(client, "http://medicinedb.codedbyjst.com/PatientInfo/102");
    http.GET();
    DynamicJsonDocument doc(2048);
    deserializeJson(doc, http.getStream());
    http.end();
    if ((String)result.ID == (String)doc["FaceID"]) {
      Bucket3_open();
      http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo/update?BucketState=delivery_102_open");
      http.GET();
      http.end();
      while (1) {
        http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
        http.GET();
        deserializeJson(doc, http.getStream());
        http.end();
        delay(100);
        if (!strcmp("delivery_102_end", (const char*)doc["BucketState"])) {
          Bucket3_close();
          break;
        }
        Serial.println("Wait for touching");
      }
    }
  }
  Serial.println("Not in the Area");
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);
  Wire.begin();

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  while (!huskylens.begin(Wire)) {
    Serial.println(F("Begin failed!"));
    Serial.println(F("1.Please recheck the \"Protocol Type\" in HUSKYLENS (General Settings>>Protocol Type>>I2C)"));
    Serial.println(F("2.Please recheck the connection."));
    delay(100);
  }
  servo1.attach(D5);
  servo2.attach(D4);
  servo3.attach(D3);
  servo1.write(180);
  servo2.write(180);
  servo3.write(180);
  Serial.printf("\nConnected, IP Address : ");
  Serial.println(WiFi.localIP());
  http.useHTTP10(true);
}

void loop() {
  // Document
  DynamicJsonDocument doc(2048);
  http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
  http.GET();

  // Parse to JSON
  deserializeJson(doc, http.getStream());
  Serial.println((String)doc["RobotState"]);
  Serial.println((String)doc["BucketState"]);
  Serial.println((String)doc["CabinetState"]);
  // Disconnect
  http.end();

  // internet signal을 계속해서 받아오면 DataBase에 무리가 너무가기 때문에 delay를 해줌
  delay(1000);

  // 1번 환자의 약을 약통에서 받는상태일 때
  if (!strcmp("med_100_start", (const char*)doc["BucketState"])) {
    Bucket1_open();
    http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo/update?BucketState=med_100_end");
    http.GET();
    http.end();
    while (1) {
      http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
      http.GET();
      deserializeJson(doc, http.getStream());
      http.end();
      if (!strcmp("med_100_end", (const char*)doc["CabinetState"])) {
        Bucket1_close();
        break;
      }
      Serial.println((String)doc["CabinetState"]);
      Serial.println("Waiting...Medicine Drop");
    }
  }

  // 2번 환자의 약을 약통에서 받는상태일 때
  else if (!strcmp("med_101_start", (const char*)doc["BucketState"])) {
    Bucket2_open();
    http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo/update?BucketState=med_101_end");
    http.GET();
    http.end();
    while (1) {
      http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
      http.GET();
      deserializeJson(doc, http.getStream());
      http.end();
      if (!strcmp("med_101_end", (const char*)doc["CabinetState"])) {
        Bucket2_close();
        break;
      }
      Serial.println((String)doc["CabinetState"]);
      Serial.println("Waiting...Medicine Drop");
    }
  }

  // 3번 환자의 약을 약통에서 받는상태일 때
  else if (!strcmp("med_102_start", (const char*)doc["BucketState"])) {
    Bucket3_open();
    http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo/update?BucketState=med_102_end");
    http.GET();
    http.end();
    while (1) {
      http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
      http.GET();
      deserializeJson(doc, http.getStream());
      http.end();
      if (!strcmp("med_102_end", (const char*)doc["CabinetState"])) {
        Bucket3_close();
        break;
      }
      Serial.println((String)doc["CabinetState"]);
      Serial.println("Waiting...Medicine Drop");
    }
  }

  // 로봇이 1번 환자를 인식하고 터치스크린 대기
  else if (!strcmp("delivery_100_detect", (const char*)doc["RobotState"]) == 1 && !strcmp("delivery_100_start", (const char*)doc["BucketState"]) == 0 && !strcmp("delivery_100_open", (const char*)doc["BucketState"]) == 0 && !strcmp("delivery_100_end", (const char*)doc["BucketState"]) == 0) {
    http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo/update?BucketState=delivery_100_start");
    http.GET();
    http.end();
    while (1) {
      http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
      http.GET();
      deserializeJson(doc, http.getStream());
      http.end();
      if (!strcmp("delivery_100_start", (const char*)doc["BucketState"])) {
        if (!huskylens.request())
          Serial.println(F("Fail to request data from HUSKYLENS, recheck the connection!"));
        else if (!huskylens.isLearned())
          Serial.println(F("Nothing learned, press learn button on HUSKYLENS to learn one!"));
        else if (!huskylens.available())
          Serial.println(F("No block or arrow appears on the screen!"));
        else {
          Serial.println(F("###########"));
          if (huskylens.available()) {
            HUSKYLENSResult result = huskylens.read();
            Detect_Patient1(result);

            http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
            http.GET();
            deserializeJson(doc, http.getStream());
            http.end();
          }
          if (!strcmp("delivery_100_end", (const char*)doc["BucketState"])) {
            break;
          }
        }
      }
      Serial.println("Searching...");
    }
  }

  // 로봇이 2번 환자를 인식하고 터치스크린 대기
  else if (!strcmp("delivery_101_detect", (const char*)doc["RobotState"]) == 1 && !strcmp("delivery_101_start", (const char*)doc["BucketState"]) == 0 && !strcmp("delivery_101_open", (const char*)doc["BucketState"]) == 0 && !strcmp("delivery_101_end", (const char*)doc["BucketState"]) == 0) {
    http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo/update?BucketState=delivery_101_start");
    http.GET();
    http.end();
    while (1) {
      http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
      http.GET();
      deserializeJson(doc, http.getStream());
      http.end();
      if (!strcmp("delivery_101_start", (const char*)doc["BucketState"])) {
        if (!huskylens.request())
          Serial.println(F("Fail to request data from HUSKYLENS, recheck the connection!"));
        else if (!huskylens.isLearned())
          Serial.println(F("Nothing learned, press learn button on HUSKYLENS to learn one!"));
        else if (!huskylens.available())
          Serial.println(F("No block or arrow appears on the screen!"));
        else {
          Serial.println(F("###########"));
          if (huskylens.available()) {
            HUSKYLENSResult result = huskylens.read();
            Detect_Patient2(result);
            http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
            http.GET();
            deserializeJson(doc, http.getStream());
            http.end();
          }
          if (!strcmp("delivery_101_end", (const char*)doc["BucketState"])) {
            break;
          }
        }
      }
      Serial.println("Searching...");
    }
  }

  // 로봇이 3번 환자를 인식하고 터치스크린 대기
  else if (!strcmp("delivery_102_detect", (const char*)doc["RobotState"]) == 1 && !strcmp("delivery_102_start", (const char*)doc["BucketState"]) == 0 && !strcmp("delivery_102_open", (const char*)doc["BucketState"]) == 0 && !strcmp("delivery_102_end", (const char*)doc["BucketState"]) == 0) {
    http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo/update?BucketState=delivery_102_start");
    http.GET();
    http.end();
    while (1) {
      http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
      http.GET();
      deserializeJson(doc, http.getStream());
      http.end();
      if (!strcmp("delivery_102_start", (const char*)doc["BucketState"])) {
        if (!huskylens.request())
          Serial.println(F("Fail to request data from HUSKYLENS, recheck the connection!"));
        else if (!huskylens.isLearned())
          Serial.println(F("Nothing learned, press learn button on HUSKYLENS to learn one!"));
        else if (!huskylens.available())
          Serial.println(F("No block or arrow appears on the screen!"));
        else {
          Serial.println(F("###########"));
          if (huskylens.available()) {
            HUSKYLENSResult result = huskylens.read();
            Detect_Patient3(result);
            http.begin(client, "http://medicinedb.codedbyjst.com/StateInfo");
            http.GET();
            deserializeJson(doc, http.getStream());
            http.end();
          }
          if (!strcmp("delivery_102_end", (const char*)doc["BucketState"])) {
            break;
          }
        }
      }
      Serial.println("Searching...");
    }
  }

}  // loop마지막