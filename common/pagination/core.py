import logging
from typing import Callable, Type

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from common.pagination.schemas import LimitOffsetPaginatedResponse, PagePaginatedResponse


logger = logging.getLogger(__name__)

class PaginationManager:

    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def limit_offset_paginated_response(
        self,
        limit: int,
        offset: int,
        count_stmt,
        instances_stmt,
        response_class: LimitOffsetPaginatedResponse,
        item_class: BaseModel,
        select_mappings_mode: bool = False,
        func_to_pend_instance: Callable = None,
        func_to_pend_instances: Callable = None,
        *args,
        **kwargs,
    ) -> LimitOffsetPaginatedResponse:
        async def __dummy(x, *arg, **kwargs):
            return x

        if func_to_pend_instance is None:
            func_to_pend_instance = __dummy

        if func_to_pend_instances is None:
            func_to_pend_instances = __dummy

        total = await self.session.execute(count_stmt)
        total = total.scalar_one()

        instances_stmt = instances_stmt.limit(limit).offset(offset)

        result = await self.session.execute(instances_stmt)
        kwargs["session"] = self.session
        results = []

        rows = result.mappings() if select_mappings_mode else result.scalars()

        for row in rows:
            if not select_mappings_mode:
                self.session.expunge(row)

            row = await func_to_pend_instance(row, *args, **kwargs)

            results.append(item_class.model_validate(row))

        result = await func_to_pend_instances(results, *args, **kwargs)

        additional_response_kwargs = kwargs.get("additional_response_kwargs")

        if not isinstance(additional_response_kwargs, dict):
            additional_response_kwargs = {}

        return response_class(
            total=total,
            limit=limit,
            offset=offset,
            results=results,
            **additional_response_kwargs,
        )

    async def page_paginated_response(
        self,
        page: int,
        page_size: int,
        count_stmt,
        instances_stmt,
        response_class: PagePaginatedResponse,
        item_class: BaseModel,
        select_mappings_mode: bool = False,
        func_to_pend_instance: Callable | None = None,
        func_to_pend_instances: Callable | None = None,
        *args,
        **kwargs,
    ) -> PagePaginatedResponse:
        async def __dummy(x, *_, **__):
            return x

        if func_to_pend_instance is None:
            func_to_pend_instance = __dummy

        if func_to_pend_instances is None:
            func_to_pend_instances = __dummy

        total = await self.session.execute(count_stmt)
        total = total.scalar_one()

        if page < 1:
            raise ValueError("`page` must be ≥ 1")

        offset = (page - 1) * page_size
        instances_stmt = instances_stmt.limit(page_size).offset(offset)

        result = await self.session.execute(instances_stmt)
        kwargs["session"] = self.session
        results = []

        rows = result.mappings() if select_mappings_mode else result.scalars()

        for row in rows:
            if not select_mappings_mode:
                self.session.expunge(row)

            row = await func_to_pend_instance(row, *args, **kwargs)

            results.append(item_class.model_validate(row))

        results = await func_to_pend_instances(results, *args, **kwargs)

        pages = (total + page_size - 1) // page_size if page_size else 0

        additional_response_kwargs = kwargs.get("additional_response_kwargs")

        if not isinstance(additional_response_kwargs, dict):
            additional_response_kwargs = {}

        return response_class(
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            results=results,
            **additional_response_kwargs,
        )

    async def limit_offset_paginated_response_from_items_list(
            self,
            limit: int,
            offset: int,
            all_items: list[dict],
            response_class: Type[LimitOffsetPaginatedResponse],
            item_class: Type[BaseModel]
    ) -> LimitOffsetPaginatedResponse:
        total = len(all_items)

        paginated_slice = all_items[offset: offset + limit]

        results = []
        for item_dict in paginated_slice:
            try:
                validated_item = item_class.model_validate(item_dict)
                results.append(validated_item)
            except Exception as e:
                logger.warning("Error validating item %s: %s", item_dict, e)
                continue

        return response_class(
            total=total,
            limit=limit,
            offset=offset,
            results=results
        )
