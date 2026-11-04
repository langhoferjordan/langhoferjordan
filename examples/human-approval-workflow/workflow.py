"""Approval-gated workflow example. In-memory, no external side effects."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Status(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"


@dataclass
class Publication:
    item_id: str
    author: str
    content: str
    status: Status = Status.DRAFT
    approver: str | None = None
    audit: list[str] = field(default_factory=list)


class ApprovalWorkflow:
    """Tracks transitions; publishing only changes local state for demonstration."""

    def __init__(self) -> None:
        self.items: dict[str, Publication] = {}

    def create(self, item_id: str, author: str, content: str) -> Publication:
        if not item_id or not author or not content:
            raise ValueError("item_id, author and content are required")
        if item_id in self.items:
            raise ValueError("item_id already exists")
        item = Publication(item_id=item_id, author=author, content=content)
        item.audit.append(f"created:{author}")
        self.items[item_id] = item
        return item

    def request_review(self, item_id: str, actor: str) -> Publication:
        item = self.items[item_id]
        if item.status != Status.DRAFT or actor != item.author:
            raise PermissionError("only the author may submit a draft for review")
        item.status = Status.IN_REVIEW
        item.audit.append(f"review_requested:{actor}")
        return item

    def approve(self, item_id: str, reviewer: str) -> Publication:
        item = self.items[item_id]
        if item.status != Status.IN_REVIEW:
            raise ValueError("item is not awaiting review")
        if not reviewer or reviewer == item.author:
            raise PermissionError("a different named reviewer is required")
        item.approver = reviewer
        item.status = Status.APPROVED
        item.audit.append(f"approved:{reviewer}")
        return item

    def publish(self, item_id: str) -> str:
        item = self.items[item_id]
        if item.status == Status.PUBLISHED:
            return f"Already published: {item.item_id}"
        if item.status != Status.APPROVED:
            raise PermissionError("publication requires approval")
        item.status = Status.PUBLISHED
        item.audit.append("published:simulated")
        return f"Simulated publication: {item.item_id}"


if __name__ == "__main__":
    flow = ApprovalWorkflow()
    flow.create("release-note-01", author="writer", content="Announcing a new product feature")
    flow.request_review("release-note-01", actor="writer")
    flow.approve("release-note-01", reviewer="editor")
    print(flow.publish("release-note-01"))
    print("Audit:", " -> ".join(flow.items["release-note-01"].audit))
