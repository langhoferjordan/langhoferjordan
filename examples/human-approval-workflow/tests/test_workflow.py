from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow import ApprovalWorkflow, Status


class ApprovalWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.flow = ApprovalWorkflow()
        self.flow.create("release", author="writer", content="Important update")

    def test_publish_requires_approval(self):
        with self.assertRaises(PermissionError):
            self.flow.publish("release")

    def test_only_author_requests_review(self):
        with self.assertRaises(PermissionError):
            self.flow.request_review("release", actor="intruder")

    def test_cannot_self_approve(self):
        self.flow.request_review("release", actor="writer")
        with self.assertRaises(PermissionError):
            self.flow.approve("release", reviewer="writer")

    def test_valid_workflow(self):
        self.flow.request_review("release", actor="writer")
        self.flow.approve("release", reviewer="editor")
        self.assertEqual(self.flow.publish("release"), "Simulated publication: release")
        self.assertEqual(self.flow.items["release"].status, Status.PUBLISHED)

    def test_repeat_publish_is_idempotent(self):
        self.flow.request_review("release", actor="writer")
        self.flow.approve("release", reviewer="editor")
        self.flow.publish("release")
        self.flow.publish("release")
        self.assertEqual(self.flow.items["release"].audit.count("published:simulated"), 1)

    def test_duplicate_id_not_accepted(self):
        with self.assertRaises(ValueError):
            self.flow.create("release", author="writer", content="Second")


if __name__ == "__main__":
    unittest.main()
