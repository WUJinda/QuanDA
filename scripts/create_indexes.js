// MongoDB索引优化脚本
// 在MongoDB shell中执行以下命令

use quanda

// 为期货日线数据创建复合索引
db.future_day.createIndex({ "code": 1, "date": -1 })

// 为期货分钟数据创建复合索引
db.future_min.createIndex({ "code": 1, "datetime": -1 })

// 查看索引创建结果
db.future_day.getIndexes()
db.future_min.getIndexes()

print("索引创建完成！")
