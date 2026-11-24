document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const clubForm = document.getElementById("club-form");
  const advisorSelect = document.getElementById("club-advisor");
  const messageDiv = document.getElementById("message");

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (character) => {
      const entities = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      };
      return entities[character];
    });
  }

  function showMessage(message, type) {
    messageDiv.textContent = message;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");
    setTimeout(() => messageDiv.classList.add("hidden"), 5000);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const [activitiesResponse, professorsResponse] = await Promise.all([
        fetch("/activities"),
        fetch("/professors"),
      ]);
      if (!activitiesResponse.ok || !professorsResponse.ok) {
        throw new Error("Failed to load club data");
      }
      const [activities, professors] = await Promise.all([
        activitiesResponse.json(),
        professorsResponse.json(),
      ]);

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';
      advisorSelect.innerHTML = '<option value="">-- Select a professor --</option>';

      professors.forEach((professor) => {
        const option = document.createElement("option");
        option.value = professor.email;
        option.textContent = professor.name;
        advisorSelect.appendChild(option);
      });

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;
        const escapedName = escapeHtml(name);
        const escapedAdvisor = escapeHtml(details.advisor.name);

        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) => `<li><span class="participant-email">${escapeHtml(
                      email
                    )}</span><button class="delete-btn" data-activity="${escapedName}" data-email="${escapeHtml(
                      email
                    )}" aria-label="Remove ${escapeHtml(email)}">Remove</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${escapedName}</h4>
          <span class="activity-status ${details.is_active ? "" : "inactive"}">${details.is_active ? "Active" : "Inactive"}</span>
          <p>${escapeHtml(details.description)}</p>
          <p><strong>Advisor:</strong> ${escapedAdvisor}</p>
          <p><strong>Schedule:</strong> ${escapeHtml(details.schedule)}</p>
          <p><strong>Location:</strong> ${escapeHtml(details.location)}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
          <div class="club-management-controls">
            <select class="advisor-update" data-activity="${escapedName}" aria-label="Change advisor for ${escapedName}">
              ${professors
                .map(
                  (professor) =>
                    `<option value="${escapeHtml(professor.email)}" ${
                      professor.email === details.advisor.email ? "selected" : ""
                    }>${escapeHtml(professor.name)}</option>`
                )
                .join("")}
            </select>
            <button class="toggle-active-btn" data-activity="${escapedName}" data-active="${details.is_active}">${details.is_active ? "Deactivate" : "Activate"}</button>
            <input class="capacity-update" type="number" min="${details.participants.length}" value="${details.max_participants}" aria-label="Membership capacity for ${escapedName}" />
            <button class="save-capacity-btn" data-activity="${escapedName}">Update Capacity</button>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        if (details.is_active) {
          const option = document.createElement("option");
          option.value = name;
          option.textContent = name;
          activitySelect.appendChild(option);
        }
      });

      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
      document.querySelectorAll(".toggle-active-btn").forEach((button) => {
        button.addEventListener("click", handleToggleActive);
      });
      document.querySelectorAll(".advisor-update").forEach((select) => {
        select.addEventListener("change", handleAdvisorChange);
      });
      document.querySelectorAll(".save-capacity-btn").forEach((button) => {
        button.addEventListener("click", handleCapacityChange);
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
        showMessage(result.message, "success");
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to unregister. Please try again.", "error");
      console.error("Error unregistering:", error);
    }
  }

  async function handleToggleActive(event) {
    const button = event.currentTarget;
    const activity = button.getAttribute("data-activity");
    const isActive = button.getAttribute("data-active") === "true";

    try {
      const response = await fetch(`/activities/${encodeURIComponent(activity)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !isActive }),
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || "Unable to update club status");
      }
      showMessage(`${activity} is now ${isActive ? "inactive" : "active"}.`, "success");
      await fetchActivities();
    } catch (error) {
      showMessage(error.message, "error");
    }
  }

  async function handleAdvisorChange(event) {
    const select = event.currentTarget;
    const activity = select.getAttribute("data-activity");

    try {
      const response = await fetch(`/activities/${encodeURIComponent(activity)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ advisor_email: select.value }),
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || "Unable to update club advisor");
      }
      showMessage(`Advisor updated for ${activity}.`, "success");
      await fetchActivities();
    } catch (error) {
      showMessage(error.message, "error");
    }
  }

  async function handleCapacityChange(event) {
    const button = event.currentTarget;
    const activity = button.getAttribute("data-activity");
    const capacity = Number(
      button.parentElement.querySelector(".capacity-update").value
    );

    try {
      const response = await fetch(`/activities/${encodeURIComponent(activity)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ max_participants: capacity }),
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || "Unable to update club capacity");
      }
      showMessage(`Capacity updated for ${activity}.`, "success");
      await fetchActivities();
    } catch (error) {
      showMessage(error.message, "error");
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
        showMessage(result.message, "success");
        signupForm.reset();
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  clubForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const newClub = {
      name: document.getElementById("club-name").value,
      description: document.getElementById("club-description").value,
      schedule: document.getElementById("club-schedule").value,
      location: document.getElementById("club-location").value,
      advisor_email: advisorSelect.value,
      max_participants: Number(document.getElementById("club-capacity").value),
    };

    try {
      const response = await fetch("/activities", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newClub),
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || "Unable to create club");
      }
      clubForm.reset();
      showMessage(result.message, "success");
      await fetchActivities();
    } catch (error) {
      showMessage(error.message, "error");
    }
  });

  // Initialize app
  fetchActivities();
});
