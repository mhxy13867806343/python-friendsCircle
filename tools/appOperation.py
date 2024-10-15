from sqlalchemy.orm import Session
from models.sysDict.model import SysDict,SysDictChild

def getPaginatedList(model, session: Session, pageNum: int = 1, pageSize: int = 20, **kwargs):

    offset = (pageNum - 1) * pageSize
    query = session.query(model)

    # 动态过滤条件
    for attr, value in kwargs.items():
        if value is not None:
            if isinstance(value, str):
                query = query.filter(getattr(model, attr).like(f"%{value}%"))
            else:
                query = query.filter(getattr(model, attr) == value)
        else:
            query = query.filter(getattr(model, attr).is_(None))
    total = query.count()
    items = query.order_by(model.createTime.desc()).offset(offset).limit(pageSize).all()
    return {
        "total": total,
        "pageNum": pageNum,
        "pageSize": pageSize,
        "data": items,
    }