import copy
import unittest

from fastapi import HTTPException

from src.app import (
    ActivityCreate,
    ActivityUpdate,
    activities,
    create_activity,
    professors,
    signup_for_activity,
    update_activity,
)


class ActivityManagementTests(unittest.TestCase):
    def setUp(self):
        self.original_activities = copy.deepcopy(activities)

    def tearDown(self):
        activities.clear()
        activities.update(self.original_activities)

    def create_test_club(self, name="Test Club", capacity=2):
        return create_activity(ActivityCreate(
            name=name,
            description="A club for tests",
            schedule="Mondays at 3 PM",
            location="Room 1",
            advisor_email=professors[0]["email"],
            max_participants=capacity,
        ))

    def test_create_club_uses_selected_professor_and_starts_active(self):
        self.create_test_club()

        club = activities["Test Club"]
        self.assertEqual(club["advisor"], professors[0])
        self.assertEqual(club["location"], "Room 1")
        self.assertTrue(club["is_active"])
        self.assertEqual(club["participants"], [])

    def test_duplicate_club_name_is_rejected(self):
        self.create_test_club()

        with self.assertRaises(HTTPException) as error:
            self.create_test_club()

        self.assertEqual(error.exception.status_code, 409)

    def test_inactive_and_full_clubs_reject_signups(self):
        self.create_test_club(capacity=1)
        update_activity("Test Club", ActivityUpdate(is_active=False))

        with self.assertRaises(HTTPException) as error:
            signup_for_activity("Test Club", "student@example.edu")
        self.assertEqual(error.exception.status_code, 400)

        update_activity("Test Club", ActivityUpdate(is_active=True))
        signup_for_activity("Test Club", "student@example.edu")
        with self.assertRaises(HTTPException) as error:
            signup_for_activity("Test Club", "another@example.edu")
        self.assertEqual(error.exception.status_code, 400)

    def test_invalid_capacity_update_does_not_apply_other_changes(self):
        self.create_test_club(capacity=2)
        signup_for_activity("Test Club", "one@example.edu")
        signup_for_activity("Test Club", "two@example.edu")

        with self.assertRaises(HTTPException) as error:
            update_activity("Test Club", ActivityUpdate(
                advisor_email=professors[1]["email"],
                max_participants=1,
            ))

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(activities["Test Club"]["advisor"], professors[0])
        self.assertEqual(activities["Test Club"]["max_participants"], 2)


if __name__ == "__main__":
    unittest.main()