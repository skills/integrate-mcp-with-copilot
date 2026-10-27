# Improvement Issues for the Student Activity Management Project

This document captures the improvement work identified during the project review. Each item is written as a GitHub-ready issue draft and can be copied into the repository issue tracker once access is available.

---

## 1) Add persistent storage for activities and enrollment data

Title: Add persistent storage for activities and enrollment data

Body:

```md
## Summary
Store activity and participant data in a durable backend instead of in-memory dictionaries so signups survive restarts and multiple users can rely on consistent state.

## Problem
The current application keeps all data in memory inside the FastAPI app. That makes the project simple to demo, but it loses all data whenever the server restarts and does not scale to real usage.

## Proposed solution
- Introduce a database layer (SQLite is a good first step)
- Persist activity definitions and participant records
- Add migration support or seed data management
- Keep the API behavior the same while making the data durable

## Acceptance criteria
- Activity data remains available after restarting the app
- Signups persist across server restarts
- Data model separates activities, participants, and enrollment records
- Existing UI continues to work without major frontend changes
```

Labels: enhancement, backend

---

## 2) Implement authentication and role-based access control

Title: Implement authentication and role-based access control

Body:

```md
## Summary
Add login and authorization so students, teachers, and admins have different permissions and the activity roster is protected from unauthorized changes.

## Problem
The current app exposes signup and unregister actions without any identity or permissions model. This is acceptable for a demo, but it is not suitable for real school use.

## Proposed solution
- Add user authentication
- Define roles such as student, teacher, and admin
- Restrict signup/unregister actions based on role
- Track who performed what action

## Acceptance criteria
- Only authenticated users can interact with activity data
- Students can sign up or leave activities only for themselves
- Admins can manage activities and rosters
- Sensitive actions are logged or auditable
```

Labels: enhancement, security

---

## 3) Enforce capacity limits and add waitlist support

Title: Enforce capacity limits and add waitlist support

Body:

```md
## Summary
The app already tracks max_participants, but it does not fully enforce that limit across all paths or provide a waitlist experience.

## Problem
The current implementation exposes a max participant count in the data model but does not consistently prevent over-enrollment or provide a waitlist workflow.

## Proposed solution
- Validate signup requests against the remaining capacity
- Block registration when the activity is full
- Add a waitlist feature for oversubscribed activities
- Display remaining seats and waitlist status in the UI

## Acceptance criteria
- Signup is rejected after capacity is reached
- Waitlist members are tracked separately from active participants
- UI shows whether a club is full or waitlisted
- Capacity rules are enforced on the backend
```

Labels: enhancement, feature

---

## 4) Add admin dashboard for managing activities and rosters

Title: Add admin dashboard for managing activities and rosters

Body:

```md
## Summary
Provide a management interface for staff to create, update, and monitor extracurricular activities and student enrollment.

## Problem
The project currently has no admin tooling. A school or district user cannot manage activity rosters, add new activities, or review participation trends.

## Proposed solution
- Create an admin dashboard for activity management
- Allow staff to add/edit/delete activities
- Show roster details and attendance-related metadata
- Support filtering and bulk organization operations

## Acceptance criteria
- Admins can create and update activities from the UI
- Rosters can be reviewed by activity
- Staff can export or inspect current participation
- Basic admin-only authorization is enforced
```

Labels: enhancement, admin

---

## 5) Add scheduling conflict detection and eligibility rules

Title: Add scheduling conflict detection and eligibility rules

Body:

```md
## Summary
Introduce more realistic student-system rules so activities cannot be chosen in conflict with other commitments or policy constraints.

## Problem
The current application treats each activity independently and does not account for scheduling conflicts, prerequisites, or eligibility rules.

## Proposed solution
- Add time conflict detection across selected activities
- Support activity prerequisites or grade-level restrictions
- Validate student eligibility before signup
- Display clear error feedback when a student cannot enroll

## Acceptance criteria
- Students cannot enroll in overlapping activities
- Eligibility rules are enforced on the backend
- Error messages explain why signup failed
- The UI surfaces the constraint before submission
```

Labels: enhancement, logic

---

## 6) Add notifications and reminders for enrollment changes

Title: Add notifications and reminders for enrollment changes

Body:

```md
## Summary
Notify students when they enroll, are waitlisted, or are removed from an activity so the system feels more complete and useful to real users.

## Problem
The app currently relies on simple inline messages only. There is no notification flow for changing enrollment state.

## Proposed solution
- Send confirmation emails or in-app notifications on signup
- Notify waitlisted students when a spot opens
- Support reminder notifications before activity events
- Add a notification preferences model

## Acceptance criteria
- Students receive a confirmation after successful signup
- Waitlist updates are communicated to affected users
- Reminder flow can be configured for upcoming events
- Notifications are traceable in the app logs
```

Labels: enhancement, notifications

---

## 7) Add reporting and analytics for activity participation

Title: Add reporting and analytics for activity participation

Body:

```md
## Summary
Provide analytics so staff can see which clubs are popular, under-enrolled, and trending over time.

## Problem
The current app provides only a static catalog and simple roster display. It has no reporting layer or trend analysis.

## Proposed solution
- Add summary metrics for each activity
- Track enrollment trends over time
- Highlight under-enrolled or over-subscribed activities
- Expose reports through an admin view or export endpoint

## Acceptance criteria
- Staff can view activity occupancy and utilization metrics
- Report data is derived from real enrollment records
- Popular and under-enrolled clubs are easy to identify
- Reports remain useful across multiple sign-up cycles
```

Labels: enhancement, analytics

---

## Notes
These drafts cover the highest-value gaps identified in the project review and are ordered from foundational backend improvements to broader feature and reporting capabilities.
