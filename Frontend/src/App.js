import React, { useState } from "react";

function App() {
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState(1);
  const [message, setMessage] = useState("");

  const BACKEND_URL = "http://10.108.245.208:8000"; // <-- CHANGE TO FRIEND IP

  const sendOtp = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/auth/send-otp`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage("OTP sent successfully. Check your email.");
        setStep(2);
      } else {
        setMessage(data.detail);
      }
    } catch (error) {
      setMessage("Error connecting to backend.");
    }
  };

  const verifyOtp = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/auth/verify-otp`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, otp })
      });

      const data = await response.json();

      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        setMessage("Login Successful 🎉");
      } else {
        setMessage(data.detail || "Invalid OTP");
      }

    } catch (error) {
      setMessage("Error verifying OTP.");
    }
  };

  return (
    <div style={{ padding: "50px", fontFamily: "Arial" }}>
      <h2>Mediscan AI Login</h2>

      {step === 1 && (
        <>
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ padding: "8px", width: "250px" }}
          />
          <br /><br />
          <button onClick={sendOtp} style={{ padding: "8px 20px" }}>
            Send OTP
          </button>
        </>
      )}

      {step === 2 && (
        <>
          <input
            type="text"
            placeholder="Enter OTP"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            style={{ padding: "8px", width: "250px" }}
          />
          <br /><br />
          <button onClick={verifyOtp} style={{ padding: "8px 20px" }}>
            Verify OTP
          </button>
        </>
      )}

      <br />
      <p>{message}</p>
    </div>
  );
}

export default App;
