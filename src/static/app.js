document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const adminForm = document.getElementById("admin-form");
  const adminActivitySelect = document.getElementById("admin-activity-select");
  const adminMessageDiv = document.getElementById("admin-message");
  const resetAdminFormButton = document.getElementById("reset-admin-form");
  const adminDeleteButton = document.getElementById("admin-delete-button");
  const adminSaveButton = document.getElementById("admin-save-button");

  let cachedActivities = {};
  let editingActivityName = null;

  function showMessage(target, text, type) {
    target.textContent = text;
    target.className = type;
    target.classList.remove("hidden");

    setTimeout(() => {
      target.classList.add("hidden");
    }, 5000);
  }

  function resetAdminForm() {
    editingActivityName = null;
    adminForm.reset();
    adminActivitySelect.value = "";
    adminSaveButton.textContent = "Create Activity";
    adminDeleteButton.classList.add("hidden");
  }

  function populateAdminForm(activityName) {
    const activity = cachedActivities[activityName];

    if (!activity) {
      resetAdminForm();
      return;
    }

    editingActivityName = activityName;
    document.getElementById("admin-name").value = activityName;
    document.getElementById("admin-description").value = activity.description;
    document.getElementById("admin-schedule").value = activity.schedule;
    document.getElementById("admin-max-participants").value =
      activity.max_participants;
    adminActivitySelect.value = activityName;
    adminSaveButton.textContent = "Update Activity";
    adminDeleteButton.classList.remove("hidden");
  }

  function createActivityCard(name, details) {
    const activityCard = document.createElement("div");
    activityCard.className = "activity-card";

    const spotsLeft = details.max_participants - details.participants.length;

    const participantsHTML =
      details.participants.length > 0
        ? `<div class="participants-section">
            <h5>Participants:</h5>
            <ul class="participants-list">
              ${details.participants
                .map(
                  (email) =>
                    `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">Remove</button></li>`
                )
                .join("")}
            </ul>
          </div>`
        : `<p><em>No participants yet</em></p>`;

    activityCard.innerHTML = `
      <div class="card-header">
        <h4>${name}</h4>
        <button type="button" class="edit-btn" data-activity="${name}">Edit</button>
      </div>
      <p>${details.description}</p>
      <p><strong>Schedule:</strong> ${details.schedule}</p>
      <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
      <div class="participants-container">
        ${participantsHTML}
      </div>
    `;

    return activityCard;
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      cachedActivities = activities;

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML =
        '<option value="">-- Select an activity --</option>';
      adminActivitySelect.innerHTML =
        '<option value="">-- Create a new activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = createActivityCard(name, details);
        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);

        const adminOption = document.createElement("option");
        adminOption.value = name;
        adminOption.textContent = name;
        adminActivitySelect.appendChild(adminOption);
      });

      if (editingActivityName && cachedActivities[editingActivityName]) {
        populateAdminForm(editingActivityName);
      } else if (editingActivityName) {
        resetAdminForm();
      }

      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });

      document.querySelectorAll(".edit-btn").forEach((button) => {
        button.addEventListener("click", () => {
          populateAdminForm(button.getAttribute("data-activity"));
          document
            .getElementById("admin-container")
            .scrollIntoView({ behavior: "smooth", block: "start" });
        });
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
        showMessage(messageDiv, result.message, "success");
        await fetchActivities();
      } else {
        showMessage(messageDiv, result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage(messageDiv, "Failed to unregister. Please try again.", "error");
      console.error("Error unregistering:", error);
    }
  }

  // Handle form submission
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
        showMessage(messageDiv, result.message, "success");
        signupForm.reset();
        await fetchActivities();
      } else {
        showMessage(messageDiv, result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage(messageDiv, "Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  adminActivitySelect.addEventListener("change", (event) => {
    const selectedActivity = event.target.value;

    if (!selectedActivity) {
      resetAdminForm();
      return;
    }

    populateAdminForm(selectedActivity);
  });

  resetAdminFormButton.addEventListener("click", () => {
    resetAdminForm();
  });

  adminDeleteButton.addEventListener("click", async () => {
    if (!editingActivityName) {
      showMessage(adminMessageDiv, "Select an activity to delete.", "error");
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(editingActivityName)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(adminMessageDiv, result.message, "success");
        resetAdminForm();
        await fetchActivities();
      } else {
        showMessage(
          adminMessageDiv,
          result.detail || "Unable to delete activity.",
          "error"
        );
      }
    } catch (error) {
      showMessage(adminMessageDiv, "Failed to delete activity.", "error");
      console.error("Error deleting activity:", error);
    }
  });

  adminForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      name: document.getElementById("admin-name").value,
      description: document.getElementById("admin-description").value,
      schedule: document.getElementById("admin-schedule").value,
      max_participants: Number(
        document.getElementById("admin-max-participants").value
      ),
    };

    const isEditing = Boolean(editingActivityName);
    const endpoint = isEditing
      ? `/activities/${encodeURIComponent(editingActivityName)}`
      : "/activities";
    const method = isEditing ? "PUT" : "POST";

    try {
      const response = await fetch(endpoint, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (response.ok) {
        showMessage(adminMessageDiv, result.message, "success");
        editingActivityName = payload.name.trim();
        await fetchActivities();

        if (!isEditing) {
          populateAdminForm(payload.name.trim());
        }
      } else {
        showMessage(
          adminMessageDiv,
          result.detail || "Unable to save activity.",
          "error"
        );
      }
    } catch (error) {
      showMessage(adminMessageDiv, "Failed to save activity.", "error");
      console.error("Error saving activity:", error);
    }
  });

  // Initialize app
  fetchActivities();
  resetAdminForm();
});
