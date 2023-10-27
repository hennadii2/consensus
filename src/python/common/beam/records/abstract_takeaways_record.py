from typing import Optional

import pyarrow  # type: ignore
from pydantic import BaseModel


class AbstractTakeawayRecord(BaseModel):
    paper_id: str
    abstract_takeaway: str
    takeaway_to_title_abstract_r1r: Optional[float]
    takeaway_length: int
    takeaway_distinct_pct: Optional[float]
    takeaway_non_special_char_pct: Optional[float]
    abstract_length: int
    abstract_distinct_pct: Optional[float]
    abstract_non_special_char_pct: Optional[float]


AbstractTakeawayRecordParquetSchema = pyarrow.schema(
    [
        ("paper_id", pyarrow.string()),
        ("abstract_takeaway", pyarrow.string()),
        ("takeaway_to_title_abstract_r1r", pyarrow.float32()),
        ("takeaway_length", pyarrow.int16()),
        ("takeaway_distinct_pct", pyarrow.float32()),
        ("takeaway_non_special_char_pct", pyarrow.float32()),
        ("abstract_length", pyarrow.int16()),
        ("abstract_distinct_pct", pyarrow.float32()),
        ("abstract_non_special_char_pct", pyarrow.float32()),
    ]
)
