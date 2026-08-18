import { useState } from "react";
import { NavLink } from "react-router-dom";

import "./App.css";

const API = {
  sendMessage: "http://localhost:8000/api/chat/send",
  submitClarification: "http://localhost:8000/api/chat/clarification",
};

const REQUESTOR_EMPLOYEE_ID= 2436587;
const REQUESTOR_EMPLOYEE_EMAIL_ID= "sunnymishra9007689708@gmail.com";

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

  // ==========================================
  // Clarification state
  // ==========================================

  const [clarificationData, setClarificationData] = useState(null);
  const [clarificationAnswers, setClarificationAnswers] = useState({});
  const [clarificationLoading, setClarificationLoading] = useState(false);

  // ==========================================
  // Send initial message
  // ==========================================

  const sendMessage = async () => {
    const text = input.trim();

    // Do not allow a new query while clarification is pending
    if (!text || loading || clarificationData !== null) return;

    const userMessage = {
      id: Date.now(),
      sender: "user",
      text,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const requestData = {
        employee_id: REQUESTOR_EMPLOYEE_ID,
        employee_email: REQUESTOR_EMPLOYEE_EMAIL_ID,
        created_at: new Date().toISOString(),
        message: text,
      };

      const response = await fetch(API.sendMessage, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      // ==========================================
      // Required query
      // ==========================================

      if (data.isRelatedQuery === true) {
        // ----------------------------------------
        // Clarification required
        // ----------------------------------------

        if (data.need_clarification === true) {
            setClarificationData({
              status: data.status,
              tracking_id: data.tracking_id,
              department_name: data.department_name,
              manager_name: data.manager_name,
              manager_email: data.manager_email,
              clarified_requestor_message: data.clarified_requestor_message,
              user_query: data.user_query,
              message: data.server_message,
              employee_email: data.employee_email,
              isRelatedQuery: data.isRelatedQuery,
              need_clarification: data.need_clarification,

              clarifications_required: data.clarifications_required || [],
            });

          const initialAnswers = {};

          data.clarifications_required?.forEach((_, index) => {
            initialAnswers[index] = "";
          });

          setClarificationAnswers(initialAnswers);

          return;
        }

        // ----------------------------------------
        // No clarification required
        // ----------------------------------------

        const botText = `
${data.server_message}

Request ID: ${data.tracking_id}
Department: ${data.department_name}
Manager (Approver): ${data.manager_name}
Manager Email: ${data.manager_email}
Status: ${data.status}
Priority: ${data.priority}
        `.trim();

        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: "bot",
            text: botText,
          },
        ]);
      }

      // ==========================================
      // Not a required query
      // ==========================================

      else {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: "bot",
            text: data.server_message,
          },
        ]);
      }
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

  // ==========================================
  // Handle clarification answer
  // ==========================================

  const handleClarificationChange = (index, value) => {
    setClarificationAnswers((prev) => ({
      ...prev,
      [index]: value,
    }));
  };

  // ==========================================
  // Check whether all answers are filled
  // ==========================================

  const areAllClarificationsAnswered = () => {
    if (!clarificationData) return false;

    return clarificationData.clarifications_required.every(
      (_, index) =>
        clarificationAnswers[index]?.trim().length > 0
    );
  };

  // ==========================================
  // Submit clarifications
  // ==========================================

  const submitClarifications = async () => {
  if (
    !clarificationData ||
    !areAllClarificationsAnswered() ||
    clarificationLoading
  ) {
    return;
  }

  const answers =
    clarificationData.clarifications_required.map(
      (question, index) => ({
        question,
        answer: clarificationAnswers[index].trim(),
      })
    );

  const requestData = {
    answers,

    tracking_id: clarificationData.tracking_id,
    employee_email: clarificationData.employee_email,
    department_name: clarificationData.department_name,
    manager_name: clarificationData.manager_name,
    manager_email: clarificationData.manager_email,
    clarified_requestor_message: clarificationData.clarified_requestor_message,
    user_query: clarificationData.user_query,
    message: clarificationData.message,

    isRelatedQuery: clarificationData.isRelatedQuery,

    need_clarification:
      clarificationData.need_clarification,

    clarifications_required:
      clarificationData.clarifications_required,

    status: clarificationData.status,
  };

  console.log(
    "Sending clarification request:",
    requestData
  );

  setClarificationLoading(true);

  try {
    const response = await fetch(
      API.submitClarification,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      }
    );

    const data = await response.json();

    console.log(
      "Clarification API response:",
      data
    );

    if (!response.ok) {
      console.error(
        "Clarification API error:",
        data
      );

      throw new Error(
        data.detail ||
          "Failed to submit clarifications"
      );
    }

    // ==========================================
    // Success
    // ==========================================
const botText = `
${data.server_message}

Request ID: ${data.tracking_id}
Department: ${data.department_name}
Manager (Approver): ${data.manager_name}
Manager Email: ${data.manager_email}
Status: ${data.status}
Priority: ${data.priority}
`.trim();
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        sender: "bot",
        text: botText,
      },
    ]);

    // ==========================================
    // Enable new queries again
    // ==========================================

    setClarificationData(null);
    setClarificationAnswers({});
  } catch (error) {
    console.error(
      "Failed to submit clarifications:",
      error
    );

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        sender: "bot",
        text:
          "Unable to submit clarifications. Please try again.",
      },
    ]);
  } finally {
    setClarificationLoading(false);
  }
};

  // ==========================================
  // Keyboard handler
  // ==========================================

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      clarificationData === null
    ) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">

      {/* ======================================
          Header
      ====================================== */}

      <header className="header">

        <div className="logo">
          PO Desk
        </div>

        <nav className="nav-links">

          <NavLink
            to="/"
            className={({ isActive }) =>
              `nav-link ${isActive ? "active" : ""}`
            }
          >
            New Request
          </NavLink>

          <NavLink
            to="/requests"
            className={({ isActive }) =>
              `nav-link ${isActive ? "active" : ""}`
            }
          >
            My Requests
          </NavLink>

        </nav>

        <div className="status">
          <span className="status-dot"></span>
          Online
        </div>

      </header>

      {/* ======================================
          Chat
      ====================================== */}

      <main className="chat-container">

        <div className="messages">

          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-row ${
                message.sender === "user"
                  ? "user-row"
                  : "bot-row"
              }`}
            >
              {message.sender === "bot" && (
                <div className="avatar bot-avatar">
                  AI
                </div>
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
                <div className="avatar user-avatar">
                  You
                </div>
              )}
            </div>
          ))}

          {/* ==================================
              Clarification UI
          ================================== */}

          {clarificationData && (
            <div className="message-row bot-row">

              <div className="avatar bot-avatar">
                AI
              </div>

              <div className="message bot-message clarification-box">

                <div className="clarification-status">
                  Status: {clarificationData.status}
                </div>

                <div className="clarification-title">
                  Additional information is required:
                </div>

                {clarificationData.clarifications_required.map(
                  (question, index) => (
                    <div
                      className="clarification-question"
                      key={index}
                    >
                      <label>
                        {question}
                      </label>

                      <input
                        type="text"
                        value={
                          clarificationAnswers[index] || ""
                        }
                        onChange={(e) =>
                          handleClarificationChange(
                            index,
                            e.target.value
                          )
                        }
                        placeholder="Enter your answer..."
                        disabled={clarificationLoading}
                      />
                    </div>
                  )
                )}

                <button
                  className="clarification-submit"
                  onClick={submitClarifications}
                  disabled={
                    !areAllClarificationsAnswered() ||
                    clarificationLoading
                  }
                >
                  {clarificationLoading
                    ? "Submitting..."
                    : "Submit Clarifications"}
                </button>

              </div>

            </div>
          )}

          {/* ==================================
              Loading
          ================================== */}

          {loading && (
            <div className="message-row bot-row">

              <div className="avatar bot-avatar">
                AI
              </div>

              <div className="message bot-message typing">
                <span></span>
                <span></span>
                <span></span>
              </div>

            </div>
          )}

        </div>

        {/* ====================================
            Input
        ==================================== */}

        <div className="input-area">

          <div className="input-wrapper">

            <textarea
              value={input}
              onChange={(e) =>
                setInput(e.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder={
                clarificationData
                  ? "Please answer the required clarifications above..."
                  : "Message PO Desk..."
              }
              rows={1}

              // ==================================
              // IMPORTANT:
              // Disable new queries while
              // clarification is pending
              // ==================================

              disabled={
                clarificationData !== null ||
                loading ||
                clarificationLoading
              }
            />

            <button
              className="send-button"
              onClick={sendMessage}
              disabled={
                !input.trim() ||
                loading ||
                clarificationData !== null ||
                clarificationLoading
              }
            >
              ↑
            </button>

          </div>

          <p className="input-hint">
            {clarificationData
              ? "Please submit the requested clarifications before sending a new query."
              : "Press Enter to send · Shift + Enter for a new line"}
          </p>

        </div>

      </main>
    </div>
  );
}

export default App;