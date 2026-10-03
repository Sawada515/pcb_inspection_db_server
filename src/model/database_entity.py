"""データベースエンティティ定義モジュール。

PCB検査データベースの各テーブル（ユーザー、保管庫、検査、検査要求、欠陥種別、欠陥、画像）
に対応するデータクラスおよびEnumを定義します。
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


# User Table data
class UserRole(Enum):
    """ユーザー権限を表す列挙型。

    Attributes:
        ADMIN: 管理者権限。
        GENERAL: 一般作業者権限。
    """

    ADMIN = "admin"
    GENERAL = "general"


class UserStatus(Enum):
    """ユーザーのアカウント状態を表す列挙型。

    Attributes:
        ACTIVE: 有効。
        INACTIVE: 無効。
    """

    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class User:
    """ユーザー情報を表すデータクラス。

    Attributes:
        user_id (str | None): ユーザーID。
        role (UserRole | None): ユーザー権限。
        uuid (str | None): ユーザーUUID。
        user_status (UserStatus | None): ユーザー状態。
    """

    user_id: str | None = None
    role: UserRole | None = None
    uuid: str | None = None
    user_status: UserStatus | None = None

    def __post_init__(self):
        """文字列で渡されたEnum値を適切なEnumインスタンスに正規化・検証する。

        Raises:
            TypeError: role または user_status の値が無効な場合。
        """
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
        """オブジェクトを辞書形式に変換する。

        Returns:
            dict[str, Any]: 属性値を格納した辞書。
        """
        return {
            "user_id": self.user_id,
            "role": (self.role.value if self.role else None),
            "uuid": self.uuid,
            "user_status": (self.user_status.value if self.user_status else None),
        }

# Store Table data


class StoreStatus(Enum):
    """保管庫スロットの状態を表す列挙型。

    Attributes:
        EMPTY: 空。
        STORED: 格納中。
        CHECKING: 検査中。
        CHECKED: 検査完了。
    """

    EMPTY = "empty"
    STORED = "stored"
    CHECKING = "checking"
    CHECKED = "checked"


@dataclass
class Store:
    """保管庫情報を表すデータクラス。

    Attributes:
        store_id (int | None): 保管庫ID。
        col (int | None): 列位置。
        row (int | None): 行位置。
        store_status (StoreStatus | None): スロット状態。
        user_id (str | None): 関連ユーザーID。
    """

    store_id: int | None = None
    col: int | None = None
    row: int | None = None
    store_status: StoreStatus | None = None
    user_id: str | None = None

    def __post_init__(self):
        """文字列で渡されたEnum値を適切なEnumインスタンスに正規化・検証する。

        Raises:
            TypeError: store_status の値が無効な場合。
        """
        if isinstance(self.store_status, str):
            try:
                self.store_status = StoreStatus(self.store_status.lower())
            except ValueError:
                raise TypeError(f"Invalid role: {self.store_status}")

        if self.store_status is not None and not isinstance(self.store_status, StoreStatus):
            raise TypeError(f"Invalid status: {self.store_status}")

    def to_dict(self) -> dict[str, Any]:
        """オブジェクトを辞書形式に変換する。

        Returns:
            dict[str, Any]: 属性値を格納した辞書。
        """
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
    """検査情報を表すデータクラス。

    Attributes:
        inspection_id (int | None): 検査ID。
        started_at (datetime | None): 検査開始日時。
        finished_at (datetime | None): 検査終了日時。
        top_image_path (str | None): 表面画像パス。
        bottom_image_path (str | None): 裏面画像パス。
        feedback (str | None): 検査フィードバック。
        user_id (str | None): 担当ユーザーID。
    """

    inspection_id: int | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    top_image_path: str | None = None
    bottom_image_path: str | None = None
    feedback: str | None = None
    user_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """オブジェクトを辞書形式に変換する。

        Returns:
            dict[str, Any]: 属性値を格納した辞書。
        """
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
    """検査要求の状態を表す列挙型。

    Attributes:
        WAITING: 検査待ち。
        RUNNING: 検査実行中。
        COMPLETED: 完了。
        CANCELED: キャンセル。
    """

    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELED = "canceled"


@dataclass
class InspectionRequest:
    """検査要求情報を表すデータクラス。

    Attributes:
        request_id (int | None): 要求ID。
        request_status (InspectionRequestStatus | None): 要求状態。
    """

    request_id: int | None = None
    request_status: InspectionRequestStatus | None = None

    def __post_init__(self):
        """文字列で渡されたEnum値を適切なEnumインスタンスに正規化・検証する。

        Raises:
            TypeError: request_status の値が無効な場合。
        """
        if isinstance(self.request_status, str):
            try:
                self.request_status = InspectionRequestStatus(self.request_status.lower())
            except ValueError:
                raise TypeError(f"Invalid role: {self.request_status}")

        if self.request_status is not None and not isinstance(self.request_status, InspectionRequestStatus):
            raise TypeError(f"Invalid status: {self.request_status}")

    def to_dict(self) -> dict[str, Any]:
        """オブジェクトを辞書形式に変換する。

        Returns:
            dict[str, Any]: 属性値を格納した辞書。
        """
        return {
            "request_id": self.request_id,
            "request_status": (self.request_status.value if self.request_status else None),
        }


# Defect Type Master Table data
@dataclass
class DefectType:
    """欠陥種別マスタ情報を表すデータクラス。

    Attributes:
        defect_type_id (int | None): 欠陥種別ID。
        defect_type (str | None): 欠陥種別名称。
    """

    defect_type_id: int | None = None
    defect_type: str | None = None


# Defect Table data
class BoardSide(Enum):
    """基板面を表す列挙型。

    Attributes:
        TOP: 表面。
        BOTTOM: 裏面。
    """

    TOP = "top"
    BOTTOM = "bottom"


@dataclass
class Defect:
    """欠陥情報を表すデータクラス。

    Attributes:
        defect_id (int | None): 欠陥ID。
        board_side (BoardSide | None): 基板面（表面/裏面）。
        point (str | None): 検出位置座標等の文字列。
        area (int | None): 欠陥面積。
        defect_type_id (int | None): 欠陥種別ID。
        inspection_id (int | None): 関連検査ID。
    """

    defect_id: int | None = None
    board_side: BoardSide | None = None
    point: str | None = None
    area: int | None = None
    defect_type_id: int | None = None
    inspection_id: int | None = None

    def __post_init__(self):
        """文字列で渡されたEnum値を適切なEnumインスタンスに正規化・検証する。

        Raises:
            TypeError: board_side の値が無効な場合。
        """
        if isinstance(self.board_side, str):
            try:
                self.board_side = BoardSide(self.board_side.lower())
            except ValueError:
                raise TypeError(f"Invalid board_side: {self.board_side}")

        if self.board_side is not None and not isinstance(self.board_side, BoardSide):
            raise TypeError(f"Invalid board_side: {self.board_side}")

    def to_dict(self) -> dict[str, Any]:
        """オブジェクトを辞書形式に変換する。

        Returns:
            dict[str, Any]: 属性値を格納した辞書。
        """
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
    """欠陥画像情報を表すデータクラス。

    Attributes:
        image_id (int | None): 画像ID。
        defect_id (int | None): 関連欠陥ID。
        defect_image_path (str | None): 画像ファイルパス。
    """

    image_id: int | None = None
    defect_id: int | None = None
    defect_image_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """オブジェクトを辞書形式に変換する。

        Returns:
            dict[str, Any]: 属性値を格納した辞書。
        """
        return {
            "image_id": self.image_id,
            "defect_id": self.defect_id,
            "defect_image_path": self.defect_image_path,
        }
