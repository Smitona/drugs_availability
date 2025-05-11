import asyncio

from db import create_tables, return_data_from_DB
from api_requests import make_request, write_data


async def main() -> None:
    #await create_tables()
    #await write_data(await make_request('ранвэк'))
    await return_data_from_DB('ранвэк', '15 мг')


if __name__ == "__main__":
    asyncio.run(main())

