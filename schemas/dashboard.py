from datetime import datetime, date
from typing import Optional, List, Union

from pydantic import BaseModel, ConfigDict, Field


# 查询参数
class QueryParams(BaseModel):
    page: Union[int, None] = Field(None, alias="page")
    page_size: Union[int, None] = Field(None, alias="pageSize")
    start_date: Optional[date] = Field(None, alias="startDate")
    end_date: Optional[date] = Field(None, alias="endDate")
