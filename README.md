# 🌱 AI-Enabled Smart Agriculture System using IoT, MQTT, and Machine Learning

An intelligent smart farming solution that integrates **IoT sensors, MQTT cloud communication, and Machine Learning** to provide real-time environmental monitoring, irrigation intelligence, and crop recommendation.

---

# 📌 Project Overview

Traditional farming methods often rely on manual monitoring and experience-based decision making, which can lead to:

- Water wastage
- Over-irrigation or under-irrigation
- Poor crop selection
- Lack of real-time monitoring

This project solves these problems by combining:

- 🌡️ Environmental sensing using IoT
- ☁️ Real-time cloud communication using MQTT
- 🤖 Machine Learning-based crop recommendation
- 📊 Live monitoring dashboard using Streamlit

The system continuously collects environmental data such as:

- Temperature
- Humidity
- Soil Moisture

The collected data is transmitted using the **MQTT protocol** through a **HiveMQ broker**, processed using Python, and visualized on a Streamlit dashboard.

---

# 🚀 Features

✅ Real-time temperature and humidity monitoring  
✅ Soil moisture monitoring  
✅ Intelligent irrigation alerts  
✅ MQTT cloud communication using HiveMQ  
✅ ESP32-based IoT integration  
✅ Machine Learning-based crop recommendation  
✅ Streamlit dashboard visualization  
✅ Low-cost and scalable architecture  
✅ Real-time data analytics  

---

# 🛠️ Technologies Used

## Hardware
- ESP32
- DHT11 Sensor
- Capacitive Soil Moisture Sensor
- LED Indicator

## Software
- Arduino IDE
- Python
- Streamlit
- MQTT Protocol
- HiveMQ Cloud Broker

## Libraries
- WiFi.h
- WiFiClientSecure.h
- PubSubClient.h
- DHT.h

---

# 📡 System Architecture

```text
DHT11 + Soil Moisture Sensor
            ↓
         ESP32
            ↓
      WiFi Connection
            ↓
       MQTT Protocol
            ↓
      HiveMQ Broker
            ↓
    Python Data Collector
            ↓
   Machine Learning Model
            ↓
     Streamlit Dashboard
            ↓
Crop Recommendation & Irrigation Alerts

## Author
Pratishtha Takjharia


