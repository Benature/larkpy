from __future__ import annotations
from typing import List, Dict
from typing_extensions import Literal, TypeAlias

UserId: TypeAlias = Literal["open_id", "union_id", "user_id"]
BitTableOperator: TypeAlias = Literal["is", "isNot", "contains",
                                      "doesNotContain", "isEmpty",
                                      "isNotEmpty", "isGreater",
                                      "isGreaterEqual", "isLess",
                                      "isLessEqual", "like", "in"]
