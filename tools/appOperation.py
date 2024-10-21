from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy import desc
# 通用过滤函数
def apply_filters(query, model, **kwargs):
    """
    向查询中动态添加过滤条件。
    :param query: 当前的 SQLAlchemy 查询对象。
    :param model: 要查询的 SQLAlchemy 模型类。
    :param kwargs: 动态过滤条件。
    :return: 过滤后的查询对象。
    """
    for attr, value in kwargs.items():
        if hasattr(model, attr):  # 确保模型中有这个属性
            if value is not None:
                if isinstance(value, str):
                    query = query.filter(getattr(model, attr).like(f"%{value}%"))
                else:
                    query = query.filter(getattr(model, attr) == value)
            else:
                query = query.filter(getattr(model, attr).is_(None))
    return query

# 支持分页的查询函数
def getPaginatedList(model, session: Session, pageNum: int = 1, pageSize: int = 20, **kwargs):
    """
    获取分页的结果列表。
    :param model: 要查询的 SQLAlchemy 模型类。
    :param session: 数据库会话对象。
    :param pageNum: 当前页码，默认为 1。
    :param pageSize: 每页的记录数，默认为 20。
    :param kwargs: 动态过滤条件。
    :return: 包含分页信息的结果字典。
    """
    offset = (pageNum - 1) * pageSize
    query = session.query(model)

    # 应用动态过滤
    query = apply_filters(query, model, **kwargs)

    # 检查模型是否有 createTime 字段，并进行排序
    model_columns = inspect(model).columns
    if 'createTime' in model_columns:
        query = query.order_by(desc(getattr(model, 'createTime')))

    # 获取总数和分页后的数据
    total = query.count()
    items = query.offset(offset).limit(pageSize).all()

    return {
        "total": total,
        "pageNum": pageNum,
        "pageSize": pageSize,
        "data": items,
    }

# 不支持分页的查询函数
def getFilteredList(model, session: Session, **kwargs):
    """
    获取不带分页的结果列表。
    :param model: 要查询的 SQLAlchemy 模型类。
    :param session: 数据库会话对象。
    :param kwargs: 动态过滤条件。
    :return: 查询的结果列表。
    """
    query = session.query(model)

    # 应用动态过滤
    query = apply_filters(query, model, **kwargs)

    # 检查模型是否有 createTime 字段，并进行排序
    model_columns = inspect(model).columns
    if 'createTime' in model_columns:
        query = query.order_by(desc(getattr(model, 'createTime')))

    return query.all()