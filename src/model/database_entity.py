from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


# User Table data
class UserRole(Enum):
    ADMIN = "admin"
    GENERAL = "general"


class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class User:
    user_id: str | None = None
    role: UserRole | None = None
    uuid: str | None = None
    user_status: UserStatus | None = None

    def __post_init__(self):
        if isinstance(self.role, str):
            try:
                self.role = UserRole(self.role.lower())
            except ValueError:
                raise TypeError(f"Invalid role: {self.role}")

        if isinstance(self.user_status, str):
            try:
                self.user_status = UserStatus(self.user_status.lower())
            except ValueError:
                raise TypeError(f"Invalid status: {self.user_status}")

        if self.role is not None and not isinstance(self.role, UserRole):
            raise TypeError(f"Invalid role: {self.role}")
        if self.user_status is not None and not isinstance(self.user_status, UserStatus):
            raise TypeError(f"Invalid status: {self.user_status}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": (self.role.value if self.role else None),
            "uuid": self.uuid,
            "user_status": (self.user_status.value if self.user_status else None),
        }

# Store Table data


class StoreStatus(Enum):
    EMPTY = "empty"
    STORED = "stored"
    CHECKING = "checking"
    CHECKED = "checked"


@dataclass
class Store:
    store_id: int | None = None
    col: int | None = None
    row: int | None = None
    store_status: StoreStatus | None = None
    user_id: str | None = None

    def __post_init__(self):
        if isinstance(self.store_status, str):
            try:
                self.store_status = StoreStatus(self.store_status.lower())
            except ValueError:
                raise TypeError(f"Invalid role: {self.store_status}")

        if self.store_status is not None and not isinstance(self.store_status, StoreStatus):
            raise TypeError(f"Invalid status: {self.store_status}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "store_id": self.store_id,
            "col": self.col,
            "row": self.row,
            "store_status": (self.store_status.value if self.store_status else None),
            "user_id": self.user_id,
        }


# Inspection Table data
@dataclass
class Inspection:
    inspection_id: int | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    top_image_path: str | None = None
    bottom_image_path: str | None = None
    feedback: str | None = None
    user_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "inspection_id": self.inspection_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "top_image_path": self.top_image_path,
            "bottom_image_path": self.bottom_image_path,
            "feedback": self.feedback,
            "user_id": self.user_id,
        }

# InspectionRequest Table data


class InspectionRequestStatus(Enum):
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELED = "canceled"


@dataclass
class InspectionRequest:
    request_id: int | None = None
    request_status: InspectionRequestStatus | None = None

    def __post_init__(self):
        if isinstance(self.request_status, str):
            try:
                self.request_status = InspectionRequestStatus(self.request_status.lower())
            except ValueError:
                raise TypeError(f"Invalid role: {self.request_status}")

        if self.request_status is not None and not isinstance(self.request_status, InspectionRequestStatus):
            raise TypeError(f"Invalid status: {self.request_status}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "request_status": (self.request_status.value if self.request_status else None),
        }


# Defect Type Master Table data
@dataclass
class DefectType:
    defect_type_id: int | None = None
    defect_type: str | None = None


# Defect Table data
class BoardSide(Enum):
    TOP = "top"
    BOTTOM = "bottom"


@dataclass
class Defect:
    defect_id: int | None = None
    board_side: BoardSide | None = None
    point: str | None = None
    area: int | None = None
    defect_type_id: int | None = None
    inspection_id: int | None = None

    def __post_init__(self):
        if isinstance(self.board_side, str):
            try:
                self.board_side = BoardSide(self.board_side.lower())
            except ValueError:
                raise TypeError(f"Invalid board_side: {self.board_side}")

        if self.board_side is not None and not isinstance(self.board_side, BoardSide):
            raise TypeError(f"Invalid board_side: {self.board_side}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "defect_id": self.defect_id,
            "board_side": (self.board_side.value if self.board_side else None),
            "point": self.point,
            "area": self.area,
            "defect_type_id": self.defect_type_id,
            "inspection_id": self.inspection_id,
        }


# Image Table data
@dataclass
class Image:
    image_id: int | None = None
    defect_id: int | None = None
    defect_image_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "image_id": self.image_id,
            "defect_id": self.defect_id,
            "defect_image_path": self.defect_image_path,
        }
