from pathlib import Path
import tempfile
import unittest

from tools.validate_native_backup import current_user_sid, private_dacl_matches_current_user, validate


class NativeBackupValidationTests(unittest.TestCase):
    def test_actual_current_user_and_system_are_accepted(self):
        sid = current_user_sid()
        self.assertTrue(private_dacl_matches_current_user(
            "D:P(A;OICI;FA;;;SY)(A;OICI;FA;;;"+sid+")", require_protected=True))

    def test_extra_everyone_grant_is_rejected(self):
        sid = current_user_sid()
        self.assertFalse(private_dacl_matches_current_user(
            "D:P(A;OICI;FA;;;SY)(A;OICI;FA;;;"+sid+")(A;;FR;;;WD)", require_protected=True))

    def test_unprotected_root_is_rejected(self):
        sid = current_user_sid()
        self.assertFalse(private_dacl_matches_current_user(
            "D:(A;OICI;FA;;;SY)(A;OICI;FA;;;"+sid+")", require_protected=True))

    def test_wrong_user_is_rejected(self):
        self.assertFalse(private_dacl_matches_current_user(
            "D:P(A;OICI;FA;;;SY)(A;OICI;FA;;;S-1-5-21-1-2-3-1000)", require_protected=True))

    def test_wrong_access_mask_is_rejected(self):
        sid = current_user_sid()
        self.assertFalse(private_dacl_matches_current_user(
            "D:P(A;OICI;FA;;;SY)(A;OICI;FR;;;"+sid+")", require_protected=True))

    def test_null_dacl_is_rejected(self):
        self.assertFalse(private_dacl_matches_current_user("D:NO_ACCESS_CONTROL", require_protected=True))

    def test_relative_fixture_parent_is_rejected_before_driver_access(self):
        with self.assertRaisesRegex(ValueError, "absolute directory"):
            validate(Path("unused.exe"), fixture_parent=Path("relative"))

    def test_missing_fixture_parent_is_rejected_before_driver_access(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "absolute directory"):
                validate(Path("unused.exe"), fixture_parent=Path(folder)/"missing")


if __name__ == "__main__":
    unittest.main()
