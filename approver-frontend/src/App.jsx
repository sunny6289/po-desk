import { useEffect, useState } from "react";
import "./App.css";

const API = {
  requestsByDepartment:
    "http://localhost:8000/api/requests/department",

  updateRequestStatus:
    "http://localhost:8000/api/requests/update-status",
};

// ============================================
// Departments
// ============================================

const departments = [
  {
    id: 101,
    name: "Notification Team",
  },
  {
    id: 102,
    name: "Data Team",
  },
  {
    id: 103,
    name: "Payment Team",
  },
  {
    id: 104,
    name: "User Management Team",
  },
  {
    id: 105,
    name: "Order Management Team",
  },
  {
    id: 106,
    name: "Product Team",
  },
  {
    id: 107,
    name: "Infrastructure Team",
  },
];


// ============================================
// App
// ============================================

function App() {

  // ============================================
  // State
  // ============================================

  const [selectedDepartment, setSelectedDepartment] =
    useState(departments[0].id);

  const [requests, setRequests] = useState([]);

  const [expandedRequest, setExpandedRequest] =
    useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState(null);

  // ============================================
  // Approval State
  // ============================================

  const [approvalStatus, setApprovalStatus] =
    useState({});

  const [approverMessage, setApproverMessage] =
    useState({});

  const [submittingRequest, setSubmittingRequest] =
    useState(null);

  // ============================================
  // Fetch Requests
  // ============================================

  const fetchRequests = async (departmentId) => {

    setLoading(true);
    setError(null);
    setExpandedRequest(null);

    try {

      const response = await fetch(
        API.requestsByDepartment,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            department_id: departmentId,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to fetch requests"
        );
      }

      setRequests(data);

    } catch (error) {

      console.error(
        "Failed to fetch requests:",
        error
      );

      setError(
        "Unable to load requests. Please try again."
      );

      setRequests([]);

    } finally {

      setLoading(false);

    }
  };


  // ============================================
  // Initial load
  // ============================================

  useEffect(() => {

    fetchRequests(selectedDepartment);

  }, []);


  // ============================================
  // Department change
  // ============================================

  const handleDepartmentChange = (event) => {

    const departmentId = Number(
      event.target.value
    );

    setSelectedDepartment(departmentId);

    fetchRequests(departmentId);
  };


  // ============================================
  // Expand / collapse request
  // ============================================

  const toggleRequest = (id) => {

    setExpandedRequest((previous) =>
      previous === id ? null : id
    );

  };


  // ============================================
  // Format date
  // ============================================

  const formatDate = (date) => {

    if (!date) return "-";

    return new Date(date).toLocaleString();

  };


  // ============================================
  // Get selected department name
  // ============================================

  const selectedDepartmentName =
    departments.find(
      (department) =>
        department.id === selectedDepartment
    )?.name || "";


  // ============================================
  // Handle approval status selection
  // ============================================

  const handleApprovalStatusChange = (
    requestId,
    status
  ) => {

    setApprovalStatus((previous) => ({
      ...previous,
      [requestId]: status,
    }));

  };


  // ============================================
  // Handle approver message
  // ============================================

  const handleApproverMessageChange = (
    requestId,
    message
  ) => {

    setApproverMessage((previous) => ({
      ...previous,
      [requestId]: message,
    }));

  };


  // ============================================
  // Submit approval / rejection
  // ============================================

  const handleSubmitDecision = async (request) => {

    const status =
      approvalStatus[request.id];

    const message =
      approverMessage[request.id]?.trim() || "";

    // ------------------------------------------
    // Validate status
    // ------------------------------------------

    if (!status) {

      alert(
        "Please select APPROVED or REJECTED."
      );

      return;
    }


    // ------------------------------------------
    // Validate reason
    // ------------------------------------------

    if (!message) {

      alert(
        "Please enter a reason."
      );

      return;
    }


    setSubmittingRequest(request.id);


    try {

      const response = await fetch(
        API.updateRequestStatus,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            tracking_id: request.tracking_id,

            status: status,

            approver_message: message,

            approved_by: request.approver_employee_id,

            approved_at: new Date().toISOString(),
          }),
        }
      );


      const data = await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to update request status"
        );

      }


      console.log(
        "Request status updated:",
        data
      );


      // ----------------------------------------
      // Update request locally
      // ----------------------------------------

      setRequests((previous) =>
        previous.map((item) =>
          item.id === request.id
            ? {
                ...item,

                status,

                approver_message:
                  message,

                approved_at:
                  status === "APPROVED"
                    ? new Date().toISOString()
                    : item.approved_at,
              }
            : item
        )
      );


      // ----------------------------------------
      // Clear approval controls
      // ----------------------------------------

      setApprovalStatus((previous) => {

        const updated = {
          ...previous,
        };

        delete updated[request.id];

        return updated;

      });


      setApproverMessage((previous) => {

        const updated = {
          ...previous,
        };

        delete updated[request.id];

        return updated;

      });


      alert(
        `Request ${status.toLowerCase()} successfully.`
      );


    } catch (error) {

      console.error(
        "Failed to update request:",
        error
      );

      alert(
        error.message ||
        "Unable to update request."
      );

    } finally {

      setSubmittingRequest(null);

    }

  };


  // ============================================
  // Render
  // ============================================

  return (

    <div className="app">

      {/* ======================================
          Header
      ====================================== */}

      <header className="header">

        <div className="logo">
          PO Desk
        </div>

        <div className="header-title">
          Approval Dashboard
        </div>

        <div className="status">

          <span className="status-dot"></span>

          Online

        </div>

      </header>


      {/* ======================================
          Main
      ====================================== */}

      <main className="container">


        {/* ====================================
            Department selector
        ==================================== */}

        <div className="department-section">

          <label htmlFor="department">
            Department
          </label>


          <select
            id="department"
            value={selectedDepartment}
            onChange={
              handleDepartmentChange
            }
          >

            {departments.map(
              (department) => (

                <option
                  key={department.id}
                  value={department.id}
                >
                  {department.name}
                </option>

              )
            )}

          </select>

        </div>


        {/* ====================================
            Request heading
        ==================================== */}

        <div className="requests-header">

          <h1>
            {selectedDepartmentName}
          </h1>

          <p>
            {requests.length} request
            {requests.length !== 1
              ? "s "
              : " "}
            found
          </p>

        </div>


        {/* ====================================
            Loading
        ==================================== */}

        {loading && (

          <div className="loading">
            Loading requests...
          </div>

        )}


        {/* ====================================
            Error
        ==================================== */}

        {!loading && error && (

          <div className="error">
            {error}
          </div>

        )}


        {/* ====================================
            No requests
        ==================================== */}

        {!loading &&
          !error &&
          requests.length === 0 && (

            <div className="empty">
              No requests found for this
              department.
            </div>

          )}


        {/* ====================================
            Requests
        ==================================== */}

        {!loading &&
          !error &&
          requests.length > 0 && (

            <div className="requests-list">

              {requests.map((request) => {

                const isExpanded =
                  expandedRequest ===
                  request.id;

                const isApprovalPending =
                  request.status ===
                  "APPROVAL_PENDING";

                const selectedApprovalStatus =
                  approvalStatus[
                    request.id
                  ];

                const currentMessage =
                  approverMessage[
                    request.id
                  ] || "";

                const isSubmitting =
                  submittingRequest ===
                  request.id;


                return (

                  <div
                    className={`request-card ${
                      isExpanded
                        ? "expanded"
                        : ""
                    }`}
                    key={request.id}
                  >

                    {/* ==================================
                        Summary
                    ================================== */}

                    <div
                      className="request-summary"
                      onClick={() =>
                        toggleRequest(
                          request.id
                        )
                      }
                    >

                      {/* Tracking ID */}

                      <div className="tracking">

                        <span className="label">
                          Tracking ID
                        </span>

                        <span className="tracking-id">
                          {request.tracking_id}
                        </span>

                      </div>


                      {/* Priority */}

                      <div className="priority">

                        <span className="label">
                          Priority
                        </span>

                        <span
                          className={`priority-badge ${String(
                            request.priority ||
                            ""
                          ).toLowerCase()}`}
                        >
                          {request.priority ||
                            "-"}
                        </span>

                      </div>


                      {/* Status */}

                      <div className="request-status">

                        <span className="label">
                          Status
                        </span>

                        <span
                          className={`status-badge ${String(
                            request.status ||
                            ""
                          )
                            .toLowerCase()
                            .replace(
                              /_/g,
                              "-"
                            )}`}
                        >
                          {request.status ||
                            "-"}
                        </span>

                      </div>


                      {/* Expand icon */}

                      <div className="expand-icon">

                        {isExpanded
                          ? "−"
                          : "+"}

                      </div>

                    </div>


                    {/* ==================================
                        Expanded Details
                    ================================== */}

                    {isExpanded && (

                      <div className="request-details">

                        <h2>
                          Request Details
                        </h2>


                        {/* ==================================
                            Requestor
                        ================================== */}

                        <section>

                          <h3>
                            Requestor
                          </h3>


                          <Detail
                            label="Requestor ID"
                            value={
                              request.requestor_id
                            }
                          />


                          <Detail
                            label="Requestor Email"
                            value={
                              request.requestor_email
                            }
                          />


                          <Detail
                            label="Created At"
                            value={formatDate(
                              request.created_at
                            )}
                          />


                          <Detail
                            label="Request"
                            value={
                              request.requestor_message
                            }
                            fullWidth
                          />


                          {request.clarified_requestor_message && (

                            <Detail
                              label="Clarified Request"
                              value={
                                request.clarified_requestor_message
                              }
                              fullWidth
                            />

                          )}

                        </section>


                        {/* ==================================
                            Tracking
                        ================================== */}

                        <section>

                          <h3>
                            Tracking
                          </h3>


                          <Detail
                            label="Tracking ID"
                            value={
                              request.tracking_id
                            }
                          />


                          <Detail
                            label="Status"
                            value={
                              request.status
                            }
                          />

                        </section>


                        {/* ==================================
                            Department
                        ================================== */}

                        <section>

                          <h3>
                            Department
                          </h3>


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


                        {/* ==================================
                            Approver
                        ================================== */}

                        <section>

                          <h3>
                            Approver
                          </h3>


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


                        {/* ==================================
                            Senior Manager
                        ================================== */}

                        <section>

                          <h3>
                            Senior Manager
                          </h3>


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


                        {/* ==================================
                            Priority
                        ================================== */}

                        <section>

                          <h3>
                            Priority
                          </h3>


                          <Detail
                            label="Priority"
                            value={
                              request.priority
                            }
                          />


                          <Detail
                            label="Average Probability"
                            value={
                              request.average_probability !==
                                null &&
                              request.average_probability !==
                                undefined
                                ? `${request.average_probability}%`
                                : "-"
                            }
                          />

                        </section>


                        {/* ==================================
                            Approval
                        ================================== */}

                        <section>

                          <h3>
                            Approval
                          </h3>


                          <Detail
                            label="Approved By"
                            value={
                              request.approved_by
                            }
                          />


                          <Detail
                            label="Approved At"
                            value={formatDate(
                              request.approved_at
                            )}
                          />


                          <Detail
                            label="Approver Message"
                            value={
                              request.approver_message
                            }
                            fullWidth
                          />

                        </section>


                        {/* ==================================
                            Approval Controls
                        ================================== */}

                        {isApprovalPending && (

                          <div className="approval-controls">

                            <h3>
                              Take Action
                            </h3>


                            {/* Radio buttons */}
                          
                            <div className="approval-options">

                              <label>

                                <input
                                  type="radio"
                                  name={`decision-${request.id}`}
                                  value="APPROVED"
                                  checked={
                                    selectedApprovalStatus ===
                                    "APPROVED"
                                  }
                                  onChange={() =>
                                    handleApprovalStatusChange(
                                      request.id,
                                      "APPROVED"
                                    )
                                  }
                                />

                                <span>
                                  APPROVED
                                </span>

                              </label>


                              <label>

                                <input
                                  type="radio"
                                  name={`decision-${request.id}`}
                                  value="REJECTED"
                                  checked={
                                    selectedApprovalStatus ===
                                    "REJECTED"
                                  }
                                  onChange={() =>
                                    handleApprovalStatusChange(
                                      request.id,
                                      "REJECTED"
                                    )
                                  }
                                />

                                <span>
                                  REJECTED
                                </span>

                              </label>

                            </div>


                            {/* Reason */}

                            <textarea
                              value={
                                currentMessage
                              }
                              onChange={(event) =>
                                handleApproverMessageChange(
                                  request.id,
                                  event.target.value
                                )
                              }
                              placeholder="Enter reason..."
                              rows={4}
                            />


                            {/* Submit */}

                            <button
                              type="button"
                              disabled={
                                isSubmitting
                              }
                              onClick={() =>
                                handleSubmitDecision(
                                  request
                                )
                              }
                            >

                              {isSubmitting
                                ? "Submitting..."
                                : "Submit"}

                            </button>

                          </div>

                        )}

                      </div>

                    )}

                  </div>

                );

              })}

            </div>

          )}

      </main>

    </div>
  );
}


// ============================================
// Detail Component
// ============================================

function Detail({
  label,
  value,
  fullWidth = false,
}) {

  return (

    <div
      className={`detail ${
        fullWidth
          ? "full-width"
          : ""
      }`}
    >

      <span className="detail-label">
        {label}
      </span>


      <span className="detail-value">

        {value === null ||
        value === undefined ||
        value === ""
          ? "-"
          : String(value)}

      </span>

    </div>

  );
}


export default App;