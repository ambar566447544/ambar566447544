const express = require("express");
const axios = require("axios");

const app = express();
const PORT = process.env.PORT || 3000;

/* ========= ESP32 DETAILS ========= */
const ESP32_IP = "192.168.1.50";      // 🔴 ESP32 ka local IP
const SECRET_KEY = "SECRET123";       // 🔴 Same as ESP32

/* ========= FUNCTION ========= */
async function sendCommand(cmd) {
  const url = `http://${ESP32_IP}/control?key=${SECRET_KEY}&cmd=${cmd}`;
  return axios.get(url);
}

/* ========= ROUTES ========= */

// Light
app.get("/light/on", async (req, res) => {
  await sendCommand("LIGHT_ON");
  res.send("Light ON");
});

app.get("/light/off", async (req, res) => {
  await sendCommand("LIGHT_OFF");
  res.send("Light OFF");
});

// Fan
app.get("/fan/on", async (req, res) => {
  await sendCommand("FAN_ON");
  res.send("Fan ON");
});

app.get("/fan/off", async (req, res) => {
  await sendCommand("FAN_OFF");
  res.send("Fan OFF");
});

// TV
app.get("/tv/on", async (req, res) => {
  await sendCommand("TV_ON");
  res.send("TV ON");
});

app.get("/tv/off", async (req, res) => {
  await sendCommand("TV_OFF");
  res.send("TV OFF");
});

/* ========= HEALTH CHECK ========= */
app.get("/", (req, res) => {
  res.send("Render Home Automation API Running");
});

/* ========= START SERVER ========= */
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
