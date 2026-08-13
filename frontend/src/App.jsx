import { useState } from "react";
import "./App.css";

const API = {
  sendMessage: "http://localhost:8000/api/chat/send",
  getMessages: "http://localhost:8080/api/chat/messages",
};

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "bot",
      text: "Hello! How can I help you today?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const text = input.trim();

    if (!text || loading) return;

    const userMessage = {
      id: Date.now(),
      sender: "user",
      text,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(API.sendMessage, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
        }),
      });

      const data = await response.json();

      // ==========================================
      // Successful request
      // ==========================================

      let botText;

      if (data.isSuccessful === true) {
        botText = `
${data.message}

Department: ${data.department_name}
Manager: ${data.manager_name}
Manager Email: ${data.manager_email}
        `.trim();
      }

      // ==========================================
      // Unsuccessful request
      // ==========================================

      else {
        botText = data.message;
      }

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: "bot",
          text: botText,
        },
      ]);

    } catch (error) {
      console.error("Failed to send message:", error);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: "bot",
          text: "Something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo">PO Desk</div>

        <div className="status">
          <span className="status-dot"></span>
          Online
        </div>
      </header>

      <main className="chat-container">
        <div className="messages">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-row ${
                message.sender === "user" ? "user-row" : "bot-row"
              }`}
            >
              {message.sender === "bot" && (
                <div className="avatar bot-avatar">AI</div>
              )}

              <div
                className={`message ${
                  message.sender === "user"
                    ? "user-message"
                    : "bot-message"
                }`}
              >
                {message.text}
              </div>

              {message.sender === "user" && (
                <div className="avatar user-avatar">You</div>
              )}
            </div>
          ))}

          {loading && (
            <div className="message-row bot-row">
              <div className="avatar bot-avatar">AI</div>

              <div className="message bot-message typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
        </div>

        <div className="input-area">
          <div className="input-wrapper">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message PO Desk..."
              rows={1}
            />

            <button
              className="send-button"
              onClick={sendMessage}
              disabled={!input.trim() || loading}
            >
              ↑
            </button>
          </div>

          <p className="input-hint">
            Press Enter to send · Shift + Enter for a new line
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;