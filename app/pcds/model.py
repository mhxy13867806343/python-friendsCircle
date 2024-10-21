
from typing import List, Tuple, Optional

from pydantic import BaseModel

class AddressModel(BaseModel):
    code: Optional[str] = ""

class PCDSModel(AddressModel):
    name:Optional[str] = ""
class ProvinceModel(PCDSModel):
    pass
class CityModel(AddressModel):
    pass
class DistrictModel(AddressModel):
    pass
class StreetModel(AddressModel):
    pass