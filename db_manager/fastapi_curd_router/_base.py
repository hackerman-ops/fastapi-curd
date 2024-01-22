from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, List, Optional, Type, Union

from fastapi import APIRouter, HTTPException
from fastapi.types import DecoratedCallable
from pydantic import create_model
from fastapi_pagination import Page

from .curd_types import T, DEPENDENCIES, Sequence
from ._utils import schema_factory
from .curd_types import DBSchemas, RouteDependencies, ResponseStruct

NOT_FOUND = HTTPException(404, "Item not found")


class CRUDGenerator(Generic[T], APIRouter, ABC):
    schema: Type[T]
    create_schema: Type[T]
    update_schema: Type[T]
    _base_path: str = "/"

    def __init__(
        self,
        schemas: DBSchemas,
        route_dependencies: RouteDependencies,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.schema = schemas.db_schema
        self._pk: str = self._pk if hasattr(self, "_pk") else "id"
        self.create_schema = (
            schemas.create_schema
            if schemas.create_schema
            else schema_factory(self.schema, pk_field_name=self._pk, name="Create")
        )
        self.update_schema = (
            schemas.update_schema
            if schemas.update_schema
            else schema_factory(self.schema, pk_field_name=self._pk, name="Update")
        )

        prefix = str(prefix if prefix else self.schema.__name__).lower()
        prefix = self._base_path + prefix.strip("/")
        tags = tags or [prefix.strip("/").capitalize()]

        super().__init__(prefix=prefix, tags=tags, **kwargs)
        dependencies = route_dependencies.common_dependencies
        get_all_route = route_dependencies.get_all_route
        get_one_route = route_dependencies.get_one_route
        create_route = route_dependencies.create_route
        update_route = route_dependencies.update_route
        delete_one_route = route_dependencies.delete_one_route
        tag_delete_one_route = route_dependencies.tag_delete_one_route
        if get_all_route:
            get_all_route = (
                get_all_route if isinstance(get_all_route, Sequence) else dependencies
            )
            self._add_api_route(
                "/query",
                self._get_all(),
                methods=["POST"],
                response_model=create_model(
                    f"GetAll{self.schema.__name__}",
                    data=(Optional[Page[self.schema]], ...),
                    __base__=ResponseStruct,
                ),  # type: ignore
                summary="Get All",
                dependencies=get_all_route,
            )

        if create_route:
            create_route = (
                create_route if isinstance(create_route, Sequence) else dependencies
            )
            self._add_api_route(
                "",
                self._create(),
                methods=["POST"],
                response_model=create_model(
                    f"Create{self.schema.__name__}",
                    data=(self.schema, ...),
                    __base__=ResponseStruct,
                ),
                summary="Create One",
                dependencies=create_route,
            )

        if get_one_route:
            get_one_route = (
                get_one_route if isinstance(get_one_route, Sequence) else dependencies
            )
            self._add_api_route(
                "/{item_id}",
                self._get_one(),
                methods=["GET"],
                response_model=create_model(
                    f"GetOne{self.schema.__name__}",
                    data=(self.schema, ...),
                    __base__=ResponseStruct,
                ),
                summary="Get One",
                dependencies=get_one_route,
                error_responses=[NOT_FOUND],
            )

        if update_route:
            update_route = (
                update_route if isinstance(update_route, Sequence) else dependencies
            )
            self._add_api_route(
                "/{item_id}",
                self._update(),
                methods=["PUT"],
                response_model=create_model(
                    f"Update{self.schema.__name__}",
                    data=(self.schema, ...),
                    __base__=ResponseStruct,
                ),
                summary="Update One",
                dependencies=update_route,
                error_responses=[NOT_FOUND],
            )

        if delete_one_route:
            delete_one_route = (
                delete_one_route
                if isinstance(delete_one_route, Sequence)
                else dependencies
            )
            self._add_api_route(
                "/{item_id}",
                self._delete_one(),
                methods=["DELETE"],
                response_model=ResponseStruct,
                summary="实际删除一条记录",
                dependencies=delete_one_route,
                error_responses=[NOT_FOUND],
            )
        if tag_delete_one_route:
            tag_delete_one_route = (
                tag_delete_one_route
                if isinstance(tag_delete_one_route, Sequence)
                else dependencies
            )
            self._add_api_route(
                "/tag_delete/{item_id}",
                self._tag_delete_one(),
                methods=["DELETE"],
                response_model=ResponseStruct,
                summary="标记删除，表字段deleted=True",
                dependencies=tag_delete_one_route,
                error_responses=[NOT_FOUND],
            )
        count_route = route_dependencies.count_route
        if count_route:
            count_route = (
                count_route if isinstance(count_route, Sequence) else dependencies
            )
            self._add_api_route(
                "/count",
                self._count(),
                methods=["POST"],
                response_model=ResponseStruct,
                summary="统计",
                dependencies=count_route,
            )
        change_status_route = route_dependencies.change_status_route
        if change_status_route:
            change_status_route = (
                change_status_route
                if isinstance(change_status_route, Sequence)
                else dependencies
            )
            self._add_api_route(
                "/{item_id}/change_status",
                self._change_status(),
                methods=["POST"],
                response_model=ResponseStruct,
                summary="上架下架",
                dependencies=change_status_route,
            )
        if export_route := route_dependencies.export_route:
            export_route = (
                export_route if isinstance(export_route, Sequence) else dependencies
            )
            self._add_api_route(
                "/export",
                self._export(),
                methods=["POST"],
                response_model=ResponseStruct,
                summary="导出",
                dependencies=export_route,
            )

    def _add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        dependencies: Union[bool, DEPENDENCIES],
        error_responses: Optional[List[HTTPException]] = None,
        **kwargs: Any,
    ) -> None:
        dependencies = [] if isinstance(dependencies, bool) else dependencies
        responses: Any = (
            {err.status_code: {"detail": err.detail} for err in error_responses}
            if error_responses
            else None
        )

        super().add_api_route(
            path, endpoint, dependencies=dependencies, responses=responses, **kwargs
        )

    def api_route(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """Overrides and exiting route if it exists"""
        methods = kwargs["methods"] if "methods" in kwargs else ["GET"]
        self.remove_api_route(path, methods)
        return super().api_route(path, *args, **kwargs)

    def get(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["Get"])
        return super().get(path, *args, **kwargs)

    def post(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["POST"])
        return super().post(path, *args, **kwargs)

    def put(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["PUT"])
        return super().put(path, *args, **kwargs)

    def delete(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["DELETE"])
        return super().delete(path, *args, **kwargs)

    def remove_api_route(self, path: str, methods: List[str]) -> None:
        methods_ = set(methods)

        for route in self.routes:
            if (
                route.path == f"{self.prefix}{path}"  # type: ignore
                and route.methods == methods_  # type: ignore
            ):
                self.routes.remove(route)

    @abstractmethod
    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _create(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _update(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _tag_delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _count(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _change_status(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _export(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    def _raise(self, e: Exception, status_code: int = 422) -> HTTPException:
        raise HTTPException(422, ", ".join(e.args)) from e

    @staticmethod
    def get_routes() -> List[str]:
        return ["get_all", "create", "get_one", "update", "delete_one"]
