import json

from app.pcds.model import Province, City, District, Street
from extend.db import LOCSESSION

# with open('./city_modified.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)
# 定义递归导入函数
def insert_location(data, parent_id=None, level=0 ,session=LOCSESSION()):
    if level == 0:  # 省级
        for province_data in data:
            province = Province(code=province_data['code'], name=province_data['name'])
            session.add(province)
            session.commit()  # 提交到数据库以获取 province.id
            insert_location(province_data.get('children', []), parent_id=province.id, level=level + 1)

    elif level == 1:  # 市级
        for city_data in data:
            city = City(code=city_data['code'], name=city_data['name'], province_id=parent_id)
            session.add(city)
            session.commit()  # 提交到数据库以获取 city.id
            insert_location(city_data.get('children', []), parent_id=city.id, level=level + 1)

    elif level == 2:  # 区/县级
        for district_data in data:
            district = District(code=district_data['code'], name=district_data['name'], city_id=parent_id)
            session.add(district)
            session.commit()  # 提交到数据库以获取 district.id
            insert_location(district_data.get('children', []), parent_id=district.id, level=level + 1)

    elif level == 3:  # 街道级
        for street_data in data:
            street = Street(code=street_data['code'], name=street_data['name'], district_id=parent_id)
            session.add(street)
            session.commit()

# 调用函数从省级开始递归插入
#insert_location(data)