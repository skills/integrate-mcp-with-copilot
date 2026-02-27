document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Manage activity form elements
  const manageForm = document.getElementById("manage-form");
  const manageTitle = document.getElementById("manage-title");
  const manageMessage = document.getElementById("manage-message");
  const manageSubmitBtn = document.getElementById("manage-submit-btn");
  const manageCancelBtn = document.getElementById("manage-cancel-btn");
  const editModeInput = document.getElementById("edit-mode");
  const originalNameInput = document.getElementById("original-name");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;

        // Create participants HTML with delete icons instead of bullet points
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <div class="activity-card-header">
            <h4>${name}</h4>
            <div class="activity-actions">
              <button class="edit-activity-btn btn-icon" data-name="${name}" title="Edit activity">✏️</button>
              <button class="delete-activity-btn btn-icon btn-danger" data-name="${name}" title="Delete activity">🗑️</button>
            </div>
          </div>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners to participant delete buttons
      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });

      // Add event listeners to activity edit buttons
      document.querySelectorAll(".edit-activity-btn").forEach((button) => {
        button.addEventListener("click", handleEditActivity);
      });

      // Add event listeners to activity delete buttons
      document.querySelectorAll(".delete-activity-btn").forEach((button) => {
        button.addEventListener("click", handleDeleteActivity);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle unregister functionality
  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  }

  // Handle edit activity — populate manage form
  async function handleEditActivity(event) {
    const name = event.currentTarget.getAttribute("data-name");
    const response = await fetch("/activities");
    const activities = await response.json();
    const details = activities[name];

    if (!details) return;

    document.getElementById("activity-name").value = name;
    document.getElementById("activity-description").value = details.description;
    document.getElementById("activity-schedule").value = details.schedule;
    document.getElementById("activity-max").value = details.max_participants;

    editModeInput.value = "edit";
    originalNameInput.value = name;
    manageTitle.textContent = `Edit Activity: ${name}`;
    manageSubmitBtn.textContent = "Save Changes";
    manageCancelBtn.classList.remove("hidden");

    document.getElementById("manage-container").scrollIntoView({ behavior: "smooth" });
  }

  // Handle delete activity
  async function handleDeleteActivity(event) {
    const name = event.currentTarget.getAttribute("data-name");

    if (!confirm(`Are you sure you want to delete "${name}"? This cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(`/activities/${encodeURIComponent(name)}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (response.ok) {
        showManageMessage(result.message, "success");
        fetchActivities();
      } else {
        showManageMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showManageMessage("Failed to delete activity. Please try again.", "error");
      console.error("Error deleting activity:", error);
    }
  }

  // Reset manage form to create mode
  function resetManageForm() {
    manageForm.reset();
    editModeInput.value = "create";
    originalNameInput.value = "";
    manageTitle.textContent = "Add New Activity";
    manageSubmitBtn.textContent = "Create Activity";
    manageCancelBtn.classList.add("hidden");
    document.getElementById("activity-name").disabled = false;
  }

  // Show message in manage section
  function showManageMessage(text, type) {
    manageMessage.textContent = text;
    manageMessage.className = type;
    manageMessage.classList.remove("hidden");
    setTimeout(() => manageMessage.classList.add("hidden"), 5000);
  }

  // Cancel edit — go back to create mode
  manageCancelBtn.addEventListener("click", resetManageForm);

  // Handle manage form submission (create or edit)
  manageForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const mode = editModeInput.value;
    const name = document.getElementById("activity-name").value.trim();
    const body = {
      description: document.getElementById("activity-description").value.trim(),
      schedule: document.getElementById("activity-schedule").value.trim(),
      max_participants: parseInt(document.getElementById("activity-max").value, 10),
    };

    try {
      let response;

      if (mode === "create") {
        response = await fetch(
          `/activities?activity_name=${encodeURIComponent(name)}`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          }
        );
      } else {
        const original = originalNameInput.value;
        response = await fetch(`/activities/${encodeURIComponent(original)}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
      }

      const result = await response.json();

      if (response.ok) {
        showManageMessage(result.message, "success");
        resetManageForm();
        fetchActivities();
      } else {
        showManageMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showManageMessage("Request failed. Please try again.", "error");
      console.error("Error managing activity:", error);
    }
  });

  // Handle sign-up form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
