from sqlalchemy import select, insert, update
from sqlalchemy.engine import Result
import asyncio
import aiohttp
from typing import Optional, List
from app.api_v1.cischecking.models import Checking
from app.api_v1.cischecking.schemas import CisResponse
from core.models.db_helper import db_helper
from config.config import cis_settings
from pprint import pprint


async def get_token() -> Optional[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(cis_settings.url_token) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def add_to_db(cis_in: List[CisResponse]):
    async with db_helper.session_dependency() as session:
        stmt = (
            insert(Checking)
            .values([cis.model_dump(exclude={"child", "id"}) for cis in cis_in])
            .returning(Checking)
        )
        result = await session.execute(stmt)
        await session.commit()

        items = result.scalars().all()
        return list(items)


async def update_db(cis_in: List[CisResponse]):
    async with db_helper.session_dependency() as session:
        for item in cis_in:
            stmt = (
                update(Checking)
                .where(Checking.id == item.id)
                .values(quantity=len(item.child))
            )
            await session.execute(stmt)
        await session.commit()


def split_list_into_chunks(input_list, chunk_size=1000):
    return [
        input_list[i : i + chunk_size] for i in range(0, len(input_list), chunk_size)
    ]


async def send_post_request(token: str, cis_dict: dict):

    cis_list = list(cis_dict.keys())

    chunks = split_list_into_chunks(cis_list)

    model_list = []

    for body in chunks:

        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                cis_settings.url_cis_info, json=body, headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    for cis_info in result:

                        try:
                            response_model = CisResponse(**cis_info["cisInfo"])
                            response_model.id = cis_dict[response_model.cis]["id"]
                            response_model.delivery_id = cis_dict[response_model.cis][
                                "delivery_id"
                            ]
                            response_model.parent_id = cis_dict[response_model.cis][
                                "parent_id"
                            ]
                            response_model.product_id = cis_dict[response_model.cis][
                                "product_id"
                            ]
                            response_model.quantity = (
                                len(response_model.child)
                                if len(response_model.child) > 0
                                else 1
                            )
                        except ValueError as e:
                            print(f"Ошибка валидации данных: {e}")
                        finally:
                            model_list.append(response_model)

    return model_list


async def get_checking(cis_dict: dict, token: str, start):

    if len(cis_dict) == 0:
        return
    else:
        cis_list = await send_post_request(token, cis_dict)
        if start == 1:
            await update_db(cis_list)
        else:
            items = await add_to_db(cis_list)
            cis_new_items_dict = {}
            for item in items:
                cis_new_items_dict[item.cis] = {
                    "id": item.id,
                    "parent_id": item.parent_id,
                    "delivery_id": item.delivery_id,
                    "product_id": item.product_id,
                }

            for cis in cis_list:
                cis.id = cis_new_items_dict[cis.cis]["id"]
                cis.parent_id = cis_new_items_dict[cis.cis]["parent_id"]

        cis_dict = {}
        for cis in cis_list:
            for cis_child in cis.child:
                cis_dict[str(cis_child)] = {
                    "id": "",
                    "parent_id": cis.id,
                    "delivery_id": cis.delivery_id,
                    "product_id": cis.product_id,
                }

        start += 1

        await get_checking(cis_dict, token, start)


async def start_checking():

    token_response = await get_token()

    if token_response is not None:
        token = token_response["data"][0]["jwt_token"]

        if token:
            async with db_helper.session_dependency() as session:
                stmt = select(Checking)
                result: Result = await session.execute(stmt)
                items = result.scalars().all()
                cis_dict = {
                    str(cis.cis): {
                        "id": cis.id,
                        "parent_id": cis.parent_id,
                        "delivery_id": cis.delivery_id,
                        "product_id": cis.product_id,
                    }
                    for cis in items
                }

            await get_checking(cis_dict, token, 1)


if __name__ == "__main__":
    asyncio.run(start_checking())
