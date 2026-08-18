import { useEffect, useState } from "react";
import './Requests.css';
import { NavLink } from "react-router-dom";

const API_BASE_URL = "http://localhost:8000";
const REQUESTOR_EMPLOYEE_ID= 2436587;

function Requests() {
  const requestorId=REQUESTOR_EMPLOYEE_ID;
  const [requests, setRequests] = useState([]);
  const [expandedRequest, setExpandedRequest] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ============================================
  // Fetch Requests
  // ============================================

  useEffect(() => {
    if (!requestorId) {
      return;
    }

    const fetchRequests = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `${API_BASE_URL}/api/requests/requestor/${requestorId}`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch requests");
        }

        const data = await response.json();

        setRequests(data);
      } catch (error) {
        console.error("Error fetching requests:", error);

        setError(
          "Unable to load your requests. Please try again."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchRequests();
  }, [requestorId]);

  // ============================================
  // Expand / Collapse
  // ============================================

  const toggleRequest = (trackingId) => {
    setExpandedRequest((current) =>
      current === trackingId
        ? null
        : trackingId
    );
  };

  // ============================================
  // Priority Class
  // ============================================

  const getPriorityClass = (priority) => {
    if (!priority) {
      return "";
    }

    return priority.toLowerCase();
  };

  // ============================================
  // Status Class
  // ============================================

  const getStatusClass = (status) => {
    if (!status) {
      return "";
    }

    return status.toLowerCase();
  };

  // ============================================
  // Loading
  // ============================================

  if (loading) {
    return (
      <div className="requests-container">
        <div className="requests-loading">
          Loading requests...
        </div>
      </div>
    );
  }

  // ============================================
  // Error
  // ============================================

  if (error) {
    return (
      <div className="requests-container">
        <div className="requests-error">
          {error}
        </div>
      </div>
    );
  }

  // ============================================
  // Empty
  // ============================================

  if (requests.length === 0) {
    return (
      <div className="requests-container">

        <div className="requests-header">
          <h2>My Requests</h2>
        </div>

        <div className="requests-empty">
          You haven't submitted any requests yet.
        </div>

      </div>
    );
  }

  // ============================================
  // Render
  // ============================================

  return (
    <div className="requests-container">
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


      {/* Request List */}

      <div className="requests-list">

        {requests.map((request) => {

          const isExpanded =
            expandedRequest ===
            request.tracking_id;

          return (
            <div
              key={request.tracking_id}
              className={`request-card ${
                isExpanded
                  ? "expanded"
                  : ""
              }`}
            >

              {/* ====================================
                  Summary
              ==================================== */}

              <div
                className="request-summary"
                onClick={() =>
                  toggleRequest(
                    request.tracking_id
                  )
                }
              >

                {/* Tracking ID */}

                <div>
                  <span className="request-label">
                    Tracking ID
                  </span>

                  <span className="tracking-id">
                    {request.tracking_id}
                  </span>
                </div>


                {/* Priority */}

                <div>
                  <span className="request-label">
                    Priority
                  </span>

                  <span
                    className={`priority-badge ${getPriorityClass(
                      request.priority
                    )}`}
                  >
                    {request.priority || "N/A"}
                  </span>
                </div>


                {/* Status */}

                <div>
                  <span className="request-label">
                    Status
                  </span>

                  <span
                    className={`status-badge ${getStatusClass(
                      request.status
                    )}`}
                  >
                    {request.status}
                  </span>
                </div>


                {/* Expand icon */}

                <div className="expand-icon">
                  {isExpanded ? "−" : "+"}
                </div>

              </div>


              {/* ====================================
                  Details
              ==================================== */}

              {isExpanded && (

                <div className="request-details">

                  <h3>
                    Request Details
                  </h3>


                  {/* Request Information */}

                  <section>

                    <h4>
                      Request Information
                    </h4>

                    <Detail
                      label="Tracking ID"
                      value={request.tracking_id}
                    />

                    <Detail
                      label="Requestor ID"
                      value={request.requestor_id}
                    />

                    <Detail
                      label="Requestor Email"
                      value={request.requestor_email}
                    />

                    <Detail
                      label="Created At"
                      value={formatDate(
                        request.created_at
                      )}
                    />

                    <Detail
                      label="Department"
                      value={
                        request.department_name
                      }
                    />

                    <Detail
                      label="Status"
                      value={request.status}
                    />

                    <Detail
                      label="Priority"
                      value={
                        request.priority || "N/A"
                      }
                    />

                    <Detail
                      label="Average Probability"
                      value={
                        request.average_probability != null
                          ? `${request.average_probability}%`
                          : "N/A"
                      }
                    />

                  </section>


                  {/* Request Message */}

                  <section>

                    <h4>
                      Request Message
                    </h4>

                    <Detail
                      label="Original Message"
                      value={
                        request.requestor_message
                      }
                      fullWidth
                    />

                  </section>


                  {/* Department */}

                  <section>

                    <h4>
                      Department
                    </h4>

                    <Detail
                      label="Department ID"
                      value={
                        request.department_id
                      }
                    />

                    <Detail
                      label="Department Name"
                      value={
                        request.department_name
                      }
                    />

                  </section>


                  {/* Approver */}

                  <section>

                    <h4>
                      Approver
                    </h4>

                    <Detail
                      label="Employee ID"
                      value={
                        request.approver_employee_id
                      }
                    />

                    <Detail
                      label="Name"
                      value={
                        request.approver_name
                      }
                    />

                    <Detail
                      label="Email"
                      value={
                        request.approver_email
                      }
                    />

                  </section>


                  {/* Senior Manager */}

                  {(request.senior_manager_employee_id ||
                    request.senior_manager_name ||
                    request.senior_manager_email) && (

                    <section>

                      <h4>
                        Senior Manager
                      </h4>

                      <Detail
                        label="Employee ID"
                        value={
                          request.senior_manager_employee_id
                        }
                      />

                      <Detail
                        label="Name"
                        value={
                          request.senior_manager_name
                        }
                      />

                      <Detail
                        label="Email"
                        value={
                          request.senior_manager_email
                        }
                      />

                    </section>

                  )}


                  {/* Approval */}

                  <section>

                    <h4>
                      Approval
                    </h4>

                    <Detail
                      label="Status"
                      value={
                        request.status
                      }
                    />

                    <Detail
                      label="Approved By"
                      value={
                        request.approved_by ||
                        "Not approved yet"
                      }
                    />

                    <Detail
                      label="Approved At"
                      value={
                        request.approved_at
                          ? formatDate(
                              request.approved_at
                            )
                          : "Not approved yet"
                      }
                    />

                    {request.approver_message && (

                      <Detail
                        label="Approver Message"
                        value={
                          request.approver_message
                        }
                        fullWidth
                      />

                    )}

                  </section>

                </div>

              )}

            </div>
          );
        })}

      </div>

    </div>
  );
}


// ============================================
// Detail Component
// ============================================

function Detail({
  label,
  value,
  fullWidth = false
}) {

  return (
    <div
      className={`request-detail ${
        fullWidth
          ? "full-width"
          : ""
      }`}
    >

      <span className="request-detail-label">
        {label}
      </span>

      <span className="request-detail-value">
        {value ?? "N/A"}
      </span>

    </div>
  );
}


// ============================================
// Date Formatter
// ============================================

function formatDate(value) {

  if (!value) {
    return "N/A";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}


export default Requests;