from sqlalchemy import select, insert, update
from sqlalchemy.engine import Result
import aiohttp
from typing import Optional, List
from api_v1.cischecking.models import Checking
from api_v1.delivery.models import Delivery
from api_v1.cischecking.schemas import CisResponse
from core.models.db_helper import db_helper
from config.config import cis_settings


async def get_token() -> Optional[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(cis_settings.url_token) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def add_to_db(cis_in: List[CisResponse]):

    chunks = split_list_into_chunks(cis_in)

    item_list = []
    for cis_in_chunk in chunks:
        async with db_helper.session_dependency() as session:
            stmt = (
                insert(Checking)
                .values(
                    [cis.model_dump(exclude={"child", "id"}) for cis in cis_in_chunk]
                )
                .returning(Checking)
            )
            result = await session.execute(stmt)
            await session.commit()

            items = result.scalars().all()
            for item in items:
                item_list.append(item)

    return list(item_list)


async def update_db(cis_in: List[CisResponse], ownerinn: str):
    async with db_helper.session_dependency() as session:
        for item in cis_in:
            stmt = (
                update(Checking)
                .where(Checking.id == item.id)
                .values(
                    quantity=len(item.child),
                    status=item.status,
                    gtin=item.gtin,
                    produceddate=item.produceddate,
                    ownerinn=item.ownerinn,
                    ownername=item.ownername,
                    packagetype=item.packagetype,
                    ownererror=item.ownerinn != ownerinn,
                    statuserror=item.ownerinn != ownerinn,
                    checked=True,
                )
            )
            await session.execute(stmt)
        await session.commit()


def split_list_into_chunks(input_list, chunk_size=1000):
    return [
        input_list[i : i + chunk_size] for i in range(0, len(input_list), chunk_size)
    ]


async def send_post_request(token: str, cis_dict: dict, ownerinn: str):

    cis_list = list(cis_dict.keys())

    chunks = split_list_into_chunks(cis_list)

    model_list = []

    status_list = ["INTRODUCED", "APPLIED"]

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
                            response_model.statuserror = (
                                response_model.status not in status_list
                            )
                            response_model.ownererror = (
                                response_model.ownerinn != ownerinn
                            )
                            response_model.quantity = (
                                len(response_model.child)
                                if len(response_model.child) > 0
                                else 1
                            )
                            response_model.checked = True
                        except ValueError as e:
                            print(cis_info)
                            print(f"Ошибка валидации данных: {e}")
                        finally:
                            model_list.append(response_model)
                else:
                    print(f"Статус ответа {response.status}")
    return model_list


async def get_checking(cis_dict: dict, token: str, start, ownerinn: str):

    if len(cis_dict) == 0:
        return
    else:
        cis_list = await send_post_request(token, cis_dict, ownerinn)
        if start == 1:
            await update_db(cis_list, ownerinn=ownerinn)
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

        await get_checking(cis_dict, token, start, ownerinn)


async def start_checking(delivery_id):

    token_response = await get_token()

    if token_response is not None:
        token = token_response["data"][0]["jwt_token"]

        if token:
            async with db_helper.session_dependency() as session:
                stmt = (
                    select(
                        Checking.id,
                        Checking.product_id,
                        Checking.delivery_id,
                        Checking.parent_id,
                        Checking.cis,
                        Delivery.supplierinn,
                    )
                    .join(Delivery)
                    .where(Checking.delivery_id == delivery_id)
                    .where(Checking.checked.is_(False))
                )
                result: Result = await session.execute(stmt)
                items = result.all()

                ownerinn = ""
                if items:
                    ownerinn = items[0].supplierinn
                cis_dict = {
                    str(cis.cis): {
                        "id": cis.id,
                        "parent_id": cis.parent_id,
                        "delivery_id": cis.delivery_id,
                        "product_id": cis.product_id,
                    }
                    for cis in items
                }

            await get_checking(cis_dict, token, 1, ownerinn)


if __name__ == "__main__":
    ...
