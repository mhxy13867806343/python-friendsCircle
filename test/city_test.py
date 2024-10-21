import json

# 读取 JSON 文件
with open('./city.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 递归函数来添加 `lv` 字段
def add_level(data, level=0):
    for item in data:
        item['lv'] = level
        if 'children' in item:
            add_level(item['children'], level=level + 1)

# 调用递归函数从根节点开始添加 `lv` 字段
add_level(data)

# 写回到 JSON 文件中
with open('city_modified.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

print("修改后的 JSON 数据已保存到 'city_modified.json'")
