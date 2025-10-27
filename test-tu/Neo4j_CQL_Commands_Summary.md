# Neo4j CQL (Cypher Query Language) 指令总结

## 目录
1. [基础查询指令](#基础查询指令)
2. [数据操作指令](#数据操作指令)
3. [条件过滤指令](#条件过滤指令)
4. [排序和限制指令](#排序和限制指令)
5. [聚合函数指令](#聚合函数指令)
6. [索引和约束指令](#索引和约束指令)
7. [高级查询指令](#高级查询指令)

---

## 基础查询指令

### 1. MATCH - 匹配节点和关系

**指令定义**: MATCH用于在图中查找匹配指定模式的节点和关系。

**MATCH命令语法**:
```cypher
MATCH (<node-name>:<Label-name>)
MATCH (<node1-name>:<Label1-name>)-[<relationship-name>:<Relationship-label-name>]->(<node2-name>:<Label2-name>)
MATCH (<node1-name>:<Label1-name>)-[<relationship-name>*<min-hops>..<max-hops>]->(<node2-name>:<Label2-name>)
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用匹配的节点 |
| `<Label-name>` | 节点标签，用于过滤特定类型的节点 |
| `<relationship-name>` | 关系变量名，用于引用匹配的关系 |
| `<Relationship-label-name>` | 关系类型，用于过滤特定类型的关系 |
| `<min-hops>` | 可变长度路径的最小跳数 |
| `<max-hops>` | 可变长度路径的最大跳数 |

**指令案例**:
```cypher
// 查找所有Person节点
MATCH (p:Person)
RETURN p

// 查找特定名称的人
MATCH (p:Person {name: "Alice"})
RETURN p

// 查找关系
MATCH (p:Person)-[r:KNOWS]->(friend:Person)
RETURN p, r, friend

// 查找可变长度路径
MATCH (p:Person)-[r:KNOWS*1..3]->(friend:Person)
RETURN p, friend
```

### 2. RETURN - 返回结果

**指令定义**: RETURN用于指定查询返回的结果。

**RETURN命令语法**:
```cypher
RETURN 
   <node-name>.<property1-name>,
   ........
   <node-name>.<propertyn-name>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用要返回的节点 |
| `<property1-name>...<propertyn-name>` | 属性名称，定义要返回的节点属性 |
| `AS alias` | 可选的别名，用于重命名返回的列 |
| `DISTINCT` | 可选关键字，用于去除重复结果 |

**指令案例**:
```cypher
// 返回所有节点
MATCH (n)
RETURN n

// 返回特定属性
MATCH (p:Person)
RETURN p.name, p.age

// 返回去重结果
MATCH (p:Person)
RETURN DISTINCT p.city

// 使用别名
MATCH (p:Person)
RETURN p.name AS person_name, p.age AS person_age
```

### 3. CREATE - 创建节点和关系

**指令定义**: CREATE用于创建新的节点和关系。

**CREATE命令语法**:
```cypher
CREATE (<node-name>:<label-name>
{
   <property1-name>:<property1-value>
   ........
   <propertyn-name>:<propertyn-value>
})
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用创建的节点 |
| `<label-name>` | 节点标签，定义节点的类型 |
| `<property1-name>...<propertyn-name>` | 属性名称，定义要分配给创建节点的属性名称 |
| `<property1-value>...<propertyn-value>` | 属性值，定义要分配给创建节点的属性值 |

**指令案例**:
```cypher
// 创建单个节点
CREATE (p:Person {name: "Alice", age: 30})

// 创建带关系的节点
CREATE (p:Person {name: "Bob"})-[:KNOWS {since: 2020}]->(f:Person {name: "Charlie"})

// 创建多个节点和关系
CREATE (a:Person {name: "Alice"}),
       (b:Person {name: "Bob"}),
       (a)-[:KNOWS]->(b)
```

---

## 数据操作指令

### 4. DELETE - 删除节点和关系

**指令定义**: DELETE用于删除节点和关系。

**DELETE命令语法**:
```cypher
DELETE <node-name-list>
DELETE <node-name>.<property1-name>,<node-name>.<property2-name>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name-list>` | 要删除的节点变量列表，用逗号分隔 |
| `<node-name>` | 节点变量名，用于引用要删除属性的节点 |
| `<property1-name>...<propertyn-name>` | 属性名称，定义要删除的节点属性 |
| `DETACH DELETE` | 删除节点及其所有关系 |

**指令案例**:
```cypher
// 删除节点（必须先删除关系）
MATCH (p:Person {name: "Alice"})
DETACH DELETE p

// 删除关系
MATCH (p:Person)-[r:KNOWS]->(f:Person)
WHERE p.name = "Alice"
DELETE r

// 删除属性
MATCH (p:Person {name: "Alice"})
DELETE p.age
```

### 5. SET - 设置属性

**指令定义**: SET用于设置或更新节点和关系的属性。

**SET命令语法**:
```cypher
SET <node-name>.<property1-name> = <value1>
SET <node-name>.<property1-name> = <value1>, <node-name>.<property2-name> = <value2>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用要设置属性的节点 |
| `<property1-name>...<propertyn-name>` | 属性名称，定义要设置的节点属性名称 |
| `<value1>...<valuen>` | 属性值，定义要分配给节点属性的值 |
| `=` | 赋值操作符 |

**指令案例**:
```cypher
// 设置单个属性
MATCH (p:Person {name: "Alice"})
SET p.age = 31

// 设置多个属性
MATCH (p:Person {name: "Alice"})
SET p.age = 31, p.city = "New York"

// 设置关系属性
MATCH (p:Person)-[r:KNOWS]->(f:Person)
WHERE p.name = "Alice"
SET r.since = 2021
```

### 6. REMOVE - 移除属性

**指令定义**: REMOVE用于移除节点和关系的属性。

**REMOVE命令语法**:
```cypher
REMOVE <node-name>.<property1-name>
REMOVE <node-name>.<property1-name>, <node-name>.<property2-name>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用要移除属性的节点 |
| `<property1-name>...<propertyn-name>` | 属性名称，定义要移除的节点属性名称 |

**指令案例**:
```cypher
// 移除单个属性
MATCH (p:Person {name: "Alice"})
REMOVE p.age

// 移除多个属性
MATCH (p:Person {name: "Alice"})
REMOVE p.age, p.city
```

### 7. MERGE - 合并节点和关系

**指令定义**: MERGE用于创建节点或关系，如果已存在则匹配。

**MERGE命令语法**:
```cypher
MERGE (<node-name>:<label-name>
{
   <property1-name>:<property1-value>
   ........
   <propertyn-name>:<propertyn-value>
})
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用要合并的节点 |
| `<label-name>` | 节点标签，定义节点的类型 |
| `<property1-name>...<propertyn-name>` | 属性名称，定义要分配给节点的属性名称 |
| `<property1-value>...<propertyn-value>` | 属性值，定义要分配给节点的属性值 |
| `ON CREATE SET` | 仅在创建时执行的设置 |
| `ON MATCH SET` | 仅在匹配时执行的设置 |

**指令案例**:
```cypher
// 合并节点
MERGE (p:Person {name: "Alice"})
ON CREATE SET p.created = timestamp()
ON MATCH SET p.last_seen = timestamp()

// 合并关系
MATCH (p:Person {name: "Alice"})
MERGE (p)-[:KNOWS]->(f:Person {name: "Bob"})
```

---

## 条件过滤指令

### 8. WHERE - 条件过滤

**指令定义**: WHERE用于添加条件来过滤查询结果。

**WHERE命令语法**:
```cypher
WHERE <condition>
WHERE <condition1> AND <condition2>
WHERE <condition1> OR <condition2>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<condition>` | 过滤条件，用于限制查询结果 |
| `<condition1>...<conditionn>` | 多个过滤条件 |
| `AND` | 逻辑与操作符，所有条件都必须为真 |
| `OR` | 逻辑或操作符，任一条件为真即可 |

**指令案例**:
```cypher
// 基本条件
MATCH (p:Person)
WHERE p.age > 25
RETURN p

// 多个条件
MATCH (p:Person)
WHERE p.age > 25 AND p.city = "New York"
RETURN p

// 字符串匹配
MATCH (p:Person)
WHERE p.name STARTS WITH "A"
RETURN p

// 存在性检查
MATCH (p:Person)
WHERE EXISTS(p.email)
RETURN p
```

### 9. OPTIONAL MATCH - 可选匹配

**指令定义**: OPTIONAL MATCH用于匹配可能不存在的模式。

**OPTIONAL MATCH命令语法**:
```cypher
OPTIONAL MATCH (<node-name>:<label-name>)
OPTIONAL MATCH (<node1-name>:<label1-name>)-[<relationship-name>]->(<node2-name>:<label2-name>)
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用匹配的节点 |
| `<label-name>` | 节点标签，用于过滤特定类型的节点 |
| `<relationship-name>` | 关系变量名，用于引用匹配的关系 |
| `OPTIONAL` | 可选关键字，表示匹配可能不存在 |

**指令案例**:
```cypher
// 查找所有人员及其朋友（如果有的话）
MATCH (p:Person)
OPTIONAL MATCH (p)-[:KNOWS]->(friend:Person)
RETURN p, friend

// 查找所有人员及其工作（如果有的话）
MATCH (p:Person)
OPTIONAL MATCH (p)-[:WORKS_AT]->(company:Company)
RETURN p, company
```

---

## 排序和限制指令

### 10. ORDER BY - 排序

**指令定义**: ORDER BY用于对查询结果进行排序。

**ORDER BY命令语法**:
```cypher
ORDER BY <node-name>.<property-name> [ASC|DESC]
ORDER BY <node-name1>.<property1-name>, <node-name2>.<property2-name>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用要排序的节点 |
| `<property-name>` | 属性名称，定义要排序的节点属性 |
| `ASC` | 升序排序（默认） |
| `DESC` | 降序排序 |

**指令案例**:
```cypher
// 按年龄升序排序
MATCH (p:Person)
RETURN p
ORDER BY p.age

// 按年龄降序排序
MATCH (p:Person)
RETURN p
ORDER BY p.age DESC

// 多字段排序
MATCH (p:Person)
RETURN p
ORDER BY p.city, p.age DESC
```

### 11. LIMIT - 限制结果数量

**指令定义**: LIMIT用于限制返回结果的数量。

**LIMIT命令语法**:
```cypher
LIMIT <number>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<number>` | 数字，定义要返回的最大结果数量 |

**指令案例**:
```cypher
// 限制返回前10个结果
MATCH (p:Person)
RETURN p
ORDER BY p.age
LIMIT 10

// 结合排序和限制
MATCH (p:Person)
RETURN p
ORDER BY p.age DESC
LIMIT 5
```

### 12. SKIP - 跳过结果

**指令定义**: SKIP用于跳过指定数量的结果。

**SKIP命令语法**:
```cypher
SKIP <number>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<number>` | 数字，定义要跳过的结果数量 |

**指令案例**:
```cypher
// 跳过前5个结果
MATCH (p:Person)
RETURN p
ORDER BY p.age
SKIP 5
LIMIT 10
```

---

## 聚合函数指令

### 13. COUNT - 计数

**指令定义**: COUNT用于计算结果的数量。

**COUNT命令语法**:
```cypher
COUNT(<node-name>)
COUNT(DISTINCT <node-name>.<property-name>)
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用要计数的节点 |
| `<property-name>` | 属性名称，定义要计数的节点属性 |
| `DISTINCT` | 可选关键字，用于去除重复结果 |

**指令案例**:
```cypher
// 计算节点数量
MATCH (p:Person)
RETURN COUNT(p)

// 计算不同城市的数量
MATCH (p:Person)
RETURN COUNT(DISTINCT p.city)

// 按城市分组计数
MATCH (p:Person)
RETURN p.city, COUNT(p) AS person_count
```

### 14. SUM - 求和

**指令定义**: SUM用于计算数值的总和。

**SUM命令语法**:
```cypher
SUM(<node-name>.<property-name>)
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用要计算的节点 |
| `<property-name>` | 属性名称，定义要计算的数值属性 |

**指令案例**:
```cypher
// 计算所有人员年龄总和
MATCH (p:Person)
RETURN SUM(p.age)

// 按城市计算年龄总和
MATCH (p:Person)
RETURN p.city, SUM(p.age) AS total_age
```

### 15. AVG - 平均值

**指令定义**: AVG用于计算数值的平均值。

**AVG命令语法**:
```cypher
AVG(<node-name>.<property-name>)
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用要计算的节点 |
| `<property-name>` | 属性名称，定义要计算平均值的数值属性 |

**指令案例**:
```cypher
// 计算平均年龄
MATCH (p:Person)
RETURN AVG(p.age)

// 按城市计算平均年龄
MATCH (p:Person)
RETURN p.city, AVG(p.age) AS avg_age
```

### 16. MIN/MAX - 最小值/最大值

**指令定义**: MIN和MAX用于查找最小值和最大值。

**MIN/MAX命令语法**:
```cypher
MIN(<node-name>.<property-name>)
MAX(<node-name>.<property-name>)
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<node-name>` | 节点变量名，用于引用要计算的节点 |
| `<property-name>` | 属性名称，定义要查找最值的数值属性 |

**指令案例**:
```cypher
// 查找最小和最大年龄
MATCH (p:Person)
RETURN MIN(p.age) AS min_age, MAX(p.age) AS max_age

// 按城市查找最小年龄
MATCH (p:Person)
RETURN p.city, MIN(p.age) AS min_age
```

---

## 索引和约束指令

### 17. CREATE INDEX - 创建索引

**指令定义**: CREATE INDEX用于创建索引以提高查询性能。

**CREATE INDEX命令语法**:
```cypher
CREATE INDEX <index-name> FOR (<node-name>:<label-name>) ON (<node-name>.<property-name>)
CREATE INDEX <index-name> FOR (<node-name>:<label-name>) ON (<node-name>.<property1-name>, <node-name>.<property2-name>)
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<index-name>` | 索引名称，用于标识创建的索引 |
| `<node-name>` | 节点变量名，用于引用要创建索引的节点 |
| `<label-name>` | 节点标签，定义要创建索引的节点类型 |
| `<property-name>` | 属性名称，定义要创建索引的节点属性 |

**指令案例**:
```cypher
// 创建单属性索引
CREATE INDEX person_name_index FOR (p:Person) ON (p.name)

// 创建复合索引
CREATE INDEX person_city_age_index FOR (p:Person) ON (p.city, p.age)
```

### 18. DROP INDEX - 删除索引

**指令定义**: DROP INDEX用于删除索引。

**DROP INDEX命令语法**:
```cypher
DROP INDEX <index-name>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<index-name>` | 索引名称，定义要删除的索引名称 |

**指令案例**:
```cypher
// 删除索引
DROP INDEX person_name_index
```

### 19. CREATE CONSTRAINT - 创建约束

**指令定义**: CREATE CONSTRAINT用于创建约束以确保数据完整性。

**CREATE CONSTRAINT命令语法**:
```cypher
CREATE CONSTRAINT <constraint-name> FOR (<node-name>:<label-name>) REQUIRE <node-name>.<property-name> IS UNIQUE
CREATE CONSTRAINT <constraint-name> FOR (<node-name>:<label-name>) REQUIRE <node-name>.<property-name> IS NOT NULL
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<constraint-name>` | 约束名称，用于标识创建的约束 |
| `<node-name>` | 节点变量名，用于引用要创建约束的节点 |
| `<label-name>` | 节点标签，定义要创建约束的节点类型 |
| `<property-name>` | 属性名称，定义要创建约束的节点属性 |
| `IS UNIQUE` | 唯一约束，确保属性值唯一 |
| `IS NOT NULL` | 非空约束，确保属性值不为空 |

**指令案例**:
```cypher
// 创建唯一约束
CREATE CONSTRAINT person_email_unique FOR (p:Person) REQUIRE p.email IS UNIQUE

// 创建非空约束
CREATE CONSTRAINT person_name_not_null FOR (p:Person) REQUIRE p.name IS NOT NULL
```

---

## 高级查询指令

### 20. WITH - 管道操作

**指令定义**: WITH用于将查询结果传递给下一个查询部分。

**WITH命令语法**:
```cypher
WITH <expression> AS <alias>
WITH <expression1>, <expression2>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<expression>` | 表达式，定义要传递的查询结果 |
| `<alias>` | 别名，用于重命名传递的表达式 |

**指令案例**:
```cypher
// 使用WITH进行复杂查询
MATCH (p:Person)
WITH p, p.age * 2 AS double_age
WHERE double_age > 50
RETURN p, double_age

// 使用WITH进行聚合
MATCH (p:Person)
WITH p.city AS city, COUNT(p) AS person_count
WHERE person_count > 10
RETURN city, person_count
```

### 21. UNWIND - 展开列表

**指令定义**: UNWIND用于将列表展开为单独的行。

**UNWIND命令语法**:
```cypher
UNWIND <list> AS <item>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<list>` | 列表表达式，定义要展开的列表 |
| `<item>` | 项目变量名，用于引用展开后的每个项目 |

**指令案例**:
```cypher
// 展开列表
UNWIND [1, 2, 3, 4, 5] AS number
RETURN number

// 展开节点属性列表
MATCH (p:Person)
UNWIND p.hobbies AS hobby
RETURN p.name, hobby
```

### 22. FOREACH - 循环操作

**指令定义**: FOREACH用于对列表中的每个元素执行操作。

**FOREACH命令语法**:
```cypher
FOREACH (<item> IN <list> | <operation>)
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<item>` | 项目变量名，用于引用列表中的每个元素 |
| `<list>` | 列表表达式，定义要遍历的列表 |
| `<operation>` | 操作表达式，定义要对每个元素执行的操作 |

**指令案例**:
```cypher
// 为每个节点设置属性
MATCH (p:Person)
FOREACH (n IN [p] | SET n.updated = timestamp())

// 批量创建关系
MATCH (p:Person)
FOREACH (hobby IN p.hobbies | 
  MERGE (h:Hobby {name: hobby})
  MERGE (p)-[:INTERESTED_IN]->(h)
)
```

### 23. CALL - 调用过程

**指令定义**: CALL用于调用存储过程或用户定义的过程。

**CALL命令语法**:
```cypher
CALL <procedure-name>(<parameters>)
CALL <procedure-name>(<parameters>) YIELD <result>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<procedure-name>` | 过程名称，定义要调用的存储过程或用户定义过程 |
| `<parameters>` | 参数列表，定义传递给过程的参数 |
| `<result>` | 结果变量名，用于接收过程的返回结果 |

**指令案例**:
```cypher
// 调用APOC过程
CALL apoc.create.node(['Person'], {name: 'Alice'})

// 调用过程并获取结果
CALL apoc.path.subgraphAll(startNode, {maxLevel: 3}) YIELD nodes, relationships
RETURN nodes, relationships
```

### 24. UNION - 合并结果

**指令定义**: UNION用于合并多个查询的结果。

**UNION命令语法**:
```cypher
<query1>
UNION
<query2>
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<query1>` | 第一个查询，定义要合并的第一个查询结果 |
| `<query2>` | 第二个查询，定义要合并的第二个查询结果 |

**指令案例**:
```cypher
// 合并两个查询的结果
MATCH (p:Person)
RETURN p.name AS name
UNION
MATCH (c:Company)
RETURN c.name AS name
```

---

## 常用查询模式

### 25. 最短路径查询

**指令定义**: 使用shortestPath函数查找两个节点之间的最短路径。

**最短路径查询命令语法**:
```cypher
MATCH (<start-node>:<start-label>), (<end-node>:<end-label>), 
      path = shortestPath((<start-node>)-[*]-(<end-node>))
RETURN path
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<start-node>` | 起始节点变量名，用于引用路径的起始节点 |
| `<start-label>` | 起始节点标签，定义起始节点的类型 |
| `<end-node>` | 结束节点变量名，用于引用路径的结束节点 |
| `<end-label>` | 结束节点标签，定义结束节点的类型 |
| `shortestPath()` | 最短路径函数，用于查找两个节点之间的最短路径 |

**指令案例**:
```cypher
// 查找两个人员之间的最短路径
MATCH (p1:Person {name: "Alice"}), (p2:Person {name: "Bob"}),
      path = shortestPath((p1)-[*]-(p2))
RETURN path

// 查找所有最短路径
MATCH (p1:Person {name: "Alice"}), (p2:Person {name: "Bob"}),
      paths = allShortestPaths((p1)-[*]-(p2))
RETURN paths
```

### 26. 路径查询

**指令定义**: 使用可变长度路径查找连接。

**路径查询命令语法**:
```cypher
MATCH path = (<start-node>)-[*<min-hops>..<max-hops>]-(<end-node>)
RETURN path
```

**语法说明**:
| 语法元素 | 描述 |
|---------|------|
| `<start-node>` | 起始节点变量名，用于引用路径的起始节点 |
| `<end-node>` | 结束节点变量名，用于引用路径的结束节点 |
| `<min-hops>` | 最小跳数，定义路径的最小长度 |
| `<max-hops>` | 最大跳数，定义路径的最大长度 |

**指令案例**:
```cypher
// 查找1到3跳的路径
MATCH path = (p:Person {name: "Alice"})-[*1..3]-(friend:Person)
RETURN path

// 查找特定关系类型的路径
MATCH path = (p:Person)-[:KNOWS*1..2]-(friend:Person)
RETURN path
```

---

## 总结

Neo4j CQL提供了丰富的查询和操作指令，包括：

1. **基础查询**: MATCH, RETURN, CREATE
2. **数据操作**: DELETE, SET, REMOVE, MERGE
3. **条件过滤**: WHERE, OPTIONAL MATCH
4. **排序限制**: ORDER BY, LIMIT, SKIP
5. **聚合函数**: COUNT, SUM, AVG, MIN, MAX
6. **索引约束**: CREATE INDEX, DROP INDEX, CREATE CONSTRAINT
7. **高级查询**: WITH, UNWIND, FOREACH, CALL, UNION
8. **路径查询**: shortestPath, allShortestPaths

这些指令可以组合使用，构建复杂的图数据库查询和操作。掌握这些指令是使用Neo4j进行图数据库开发的基础。

---

*文档创建时间: 2024年*
*基于Neo4j官方文档和W3CSchool教程整理*
