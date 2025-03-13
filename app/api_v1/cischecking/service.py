from sqlalchemy import select, insert
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
        stmt = insert(Checking).values([cis.dict() for cis in cis_in])





async def check(cis_dict: dict, token: str, start):

    body = list(cis_dict.keys())
    headers = {"Authorization": f"Bearer {token}"}
    cis_dict_child = {}

    if start == 2:
        pprint(cis_dict)
        print(body)
        return

    async with aiohttp.ClientSession() as session:
        async with session.post(
            cis_settings.url_cis_info, json=body, headers=headers
        ) as response:
            if response.status == 200:
                result = await response.json()

                for cis_info in result:

                    try:
                        response_model = CisResponse(**cis_info["cisInfo"])
                        response_model.delivery_id = cis_dict[response_model.cis][
                            "delivery_id"
                        ]
                        response_model.parent_id = cis_dict[response_model.cis]["id"]
                        response_model.product_id = cis_dict[response_model.cis][
                            "product_id"
                        ]
                    except ValueError as e:
                        print(f"Ошибка валидации данных: {e}")
                    finally:
                        for child_cis in response_model.child:
                            cis_dict_child[child_cis] = {
                                "id": response_model.parent_id,
                                "delivery_id": response_model.delivery_id,
                                "product_id": response_model.product_id,
                            }

                start += 1

                await check(cis_dict_child, token, start)

            else:
                print(f"Ошибка {response.status}: {await response.text()}")
                return None


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
                        "delivery_id": cis.delivery_id,
                        "product_id": cis.product_id,
                    }
                    for cis in items
                }

            await check(cis_dict, token, 1)


if __name__ == "__main__":
    asyncio.run(start_checking())
