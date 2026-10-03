"""リクエストルーティングモジュール。

クライアントから受け取ったリクエスト（リソース種別、クエリ種別、生データ）を
対応するデータモデルにマッピングし、適切なサービス層のメソッドへディスパッチします。
"""

from enum import Enum
from logging import Logger
from typing import Any

from mariadb import Connection

from model import Defect, DefectType, Image, Inspection, InspectionRequest, Store, User
from service import (
    DefectService,
    DefectTypeService,
    ImageService,
    InspectionRequestService,
    InspectionService,
    StoreService,
    UserService,
)


class QueryType(Enum):
    """データベースに対するクエリ操作種別を表す列挙型。

    Attributes:
        CREATE: 作成 (INSERT)。
        READ: 読み取り (SELECT)。
        UPDATE: 更新 (UPDATE)。
        DELETE: 削除 (DELETE)。
    """

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class ResourceType(Enum):
    """リクエスト対象のサービスリソース種別を表す列挙型。

    Attributes:
        USER: ユーザーサービス (user_service)。
        INSPECTION: 検査サービス (inspection_service)。
        REQUEST: 検査要求サービス (request_service)。
        STORE: 保管庫サービス (store_service)。
        DEFECT: 欠陥サービス (defect_service)。
        DEFECTTYPE: 欠陥種別サービス (defect_type_service)。
        IMAGE: 画像サービス (image_service)。
    """

    USER = "user_service"
    INSPECTION = "inspection_service"
    REQUEST = "request_service"
    STORE = "store_service"
    DEFECT = "defect_service"
    DEFECTTYPE = "defect_type_service"
    IMAGE = "image_service"


ALL_QUERY_TYPES = {
    QueryType.CREATE,
    QueryType.READ,
    QueryType.UPDATE,
    QueryType.DELETE,
}

RESOURCE_MODEL_MAP = {
    ResourceType.USER: User,
    ResourceType.INSPECTION: Inspection,
    ResourceType.REQUEST: InspectionRequest,
    ResourceType.STORE: Store,
    ResourceType.DEFECT: Defect,
    ResourceType.DEFECTTYPE: DefectType,
    ResourceType.IMAGE: Image,
}


class RequestRouter:
    """受信リクエストを適切なサービスにルーティング・実行するクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _services (dict[ResourceType, Any]): リソース種別とサービスクラスインスタンスのマッピング。
        _allowed_query_types (dict[ResourceType, set[QueryType]]): リソースごとに許可されたクエリ種別セット。
    """

    def __init__(self, logger: Logger) -> None:
        """RequestRouterのインスタンスを初期化する。

        Args:
            logger (Logger): ロガーインスタンス。
        """
        self._logger = logger

        # サービスインスタンス
        self._services: dict[ResourceType, Any] = {
            ResourceType.USER: UserService(self._logger),
            ResourceType.INSPECTION: InspectionService(self._logger),
            ResourceType.REQUEST: InspectionRequestService(self._logger),
            ResourceType.STORE: StoreService(self._logger),
            ResourceType.DEFECT: DefectService(self._logger),
            ResourceType.DEFECTTYPE: DefectTypeService(self._logger),
            ResourceType.IMAGE: ImageService(self._logger),
        }

        # 許可する QueryType のマッピング
        self._allowed_query_types: dict[ResourceType, set[QueryType]] = {
            ResourceType.USER: ALL_QUERY_TYPES,
            ResourceType.INSPECTION: ALL_QUERY_TYPES,
            ResourceType.REQUEST: ALL_QUERY_TYPES,
            ResourceType.STORE: {QueryType.READ, QueryType.UPDATE},
            ResourceType.DEFECT: ALL_QUERY_TYPES,
            ResourceType.DEFECTTYPE: ALL_QUERY_TYPES,
            ResourceType.IMAGE: ALL_QUERY_TYPES,
        }

    def dispatch(
        self,
        request_resource_str: str,
        query_type_str: str,
        request_data: Any,
        conn: Connection,
    ) -> Any:
        """リクエストパラメータを検証・モデル化し、対応するサービスへディスパッチして結果を返す。

        Args:
            request_resource_str (str): リソース種別文字列 (例: "user_service")。
            query_type_str (str): クエリ種別文字列 (例: "read", "create")。
            request_data (Any): リクエストデータ辞書。
            conn (Connection): データベース接続オブジェクト。

        Returns:
            Any: サービス実行結果（作成/更新/削除のbool値、または取得されたモデルオブジェクト/リスト）。

        Raises:
            KeyError: リソース種別またはクエリ種別が無効な文字列の場合。
            ValueError: サービスが見つからない、クエリ種別がリソースに対して許可されていない、
                またはモデルクラスのマッピングが存在しない場合。
            RuntimeError: サービス層でデータベースエラー等が発生した場合。
        """
        try:
            request_resource: ResourceType = ResourceType(request_resource_str)
        except KeyError:
            self._logger.error(
                f"Invalid request resource: {request_resource_str}"
            )

            raise KeyError(f"Invalid request resource: {request_resource_str}")

        try:
            query_type: QueryType = QueryType(query_type_str)
        except KeyError:
            self._logger.error(
                f"Invalid query type: {query_type_str}"
            )

            raise KeyError(f"Invalid query type: {query_type_str}")

        try:
            service = self._services.get(request_resource)
            if service is None:
                raise ValueError(
                    f"Invalid request resource: {request_resource}")

            allowed_types = self._allowed_query_types.get(
                request_resource, set())
            if query_type not in allowed_types:
                raise ValueError(
                    f"Invalid query type for {request_resource.value}: {query_type}"
                )

            converted_data = None

            model_cls = RESOURCE_MODEL_MAP.get(request_resource)
            if model_cls is None:
                raise ValueError(
                    f"No model class found for resource: {request_resource}")

            converted_data = model_cls(**request_data)

            print(f"service: {service}")

            return self._dispatch_query_type(query_type, converted_data, conn, service)

        except ValueError as e:
            self._logger.error(
                f"Error dispatching request or processing data: {e}"
            )
            raise
        except RuntimeError:
            raise

    def _dispatch_query_type(
        self, query_type: QueryType, request_data: Any, conn: Connection, dao_service: Any
    ) -> Any:
        """クエリ種別に応じてサービスのCRUDメソッドを呼び出す。

        Args:
            query_type (QueryType): 実行するクエリ種別。
            request_data (Any): モデルインスタンス化されたリクエストデータ。
            conn (Connection): データベース接続オブジェクト。
            dao_service (Any): 呼び出し対象のサービスインスタンス。

        Returns:
            Any: 各サービスメソッドの戻り値。

        Raises:
            ValueError: クエリ種別が未知の場合。
        """
        print(request_data)
        print(f"query_type: {query_type}")

        if query_type == QueryType.CREATE:
            return dao_service.create(conn, request_data)
        elif query_type == QueryType.READ:
            return dao_service.read(conn, request_data)
        elif query_type == QueryType.UPDATE:
            return dao_service.update(conn, request_data)
        elif query_type == QueryType.DELETE:
            print("exec")
            return dao_service.delete(conn, request_data)
        else:
            raise ValueError(f"Invalid query type: {query_type}")

