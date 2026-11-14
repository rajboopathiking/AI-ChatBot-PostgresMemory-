from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore,PoolConfig

from psycopg.types.json import Jsonb
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from dotenv import load_dotenv
load_dotenv()

import os
import structlog

logger = structlog.get_logger(__name__)

class PostgresResource:
  def __init__(self,db_uri:str = os.getenv("DB_URL")):
    self.db_uri = db_uri

  async def start(self):
    self.pool = AsyncConnectionPool(
          conninfo=self.db_uri,
          max_size=3,min_size=1,
          kwargs = {
            "autocommit":True,
            "row_factory":dict_row
          },
          open=False
        )
    
    self.checkpointer = AsyncPostgresSaver(self.pool)
    self.store_cm = AsyncPostgresStore.from_conn_string(
          self.db_uri,
          pool_config = PoolConfig(
            max_size=3,min_size=1,
          )
        )

    await self.pool.open()
    await self.checkpointer.setup()

    self.store = await self.store_cm.__aenter__()
    await self.store.setup()

    if self.store and self.checkpointer:
      logger.info("Setup Iniatializaed")
    else:
      logger.warning("setup not intialized")

  async def close(self):
    if self.pool is not None:
      await self.pool.close()
    if self.store is not None:
      await self.store_cm.__aexit__(None,None,None)
      
    logger.info("closed sucessfully")


class Store:
  def __init__(self,store,id):
    self.id = id
    self.store = store
    self.namespace = ("user",id)

  async def put(self,value,category:str="information"):
    await self.store.aput(
      self.namespace,
      category,
      value
    )
    logger.info("information stored in pg store")

  async def get(self,category:str="information"):
    data = await self.store.aget(
      self.namespace,
      category
    )
    return data.value if data else None

  async def search(self,query:str):
    data = await self.store.asearch(
      self.namespace,
      query=query,
      limit=5

    )
    return [d.value for d in data]



