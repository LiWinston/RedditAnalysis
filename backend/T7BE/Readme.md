# T7BE 后端 API 文档

## 1. 通用说明

*   **CORS**: 所有API端点均已配置 `CrossOrigin(origins = "*")`，允许跨域请求。
*   **基础路径**: 除非另有说明，所有API路径均以 `/api` 开头。
*   **分页参数**: 对于分页的接口，通常使用以下查询参数：
    *   `page`: 当前页码 (可选, 整数, 默认: 1)
    *   `size`: 每页记录数 (可选, 整数, 默认: 10)
*   **`TopicCategory` 枚举**: 在路径参数或查询参数中使用的主题类别 (`category` 或 `topicCategory`)，其可能值为：
    *   `general_housing`
    *   `rental`
    *   `wage`
    *   `mental_health`
    *   `immigration`

## 2. 公共数据结构 (DTO)

#### 2.1. `RedditComment`

代表一条 Reddit 评论/帖子的结构。

```json
{
  "id": "string",                   // 唯一ID
  "author": "string",               // 作者
  "title": "string",                // 标题 (如果适用)
  "text": "string",                 // 内容文本
  "created_utc": "number",          // 创建时间的UTC时间戳 (秒)
  "url": "string",                  // 原始URL
  "loc_pid": "string",              // 地理位置ID
  "state": "string",                // 州/省份
  "sentiment_score": "number",      // 情感得分 (-1.0 到 1.0)
  "sentiment_magnitude": "number",  // 情感强度
  "emotion": "string",              // 主要情感 (例如: JOY, ANGER, SADNESS)
  "topic_category": "string"        // 主题分类 (例如: general_housing, rental)
}
```

#### 2.2. `PageResponseDTO<T>`

用于分页响应的通用数据结构，其中 `T` 代表具体的数据类型 (例如 `RedditComment`)。

```json
{
  "currentPage": "integer",         // 当前页码
  "pageSize": "integer",            // 每页大小
  "totalCount": "long",             // 总记录数
  "totalPages": "integer",          // 总页数
  "data": [                         // 当前页的数据列表
    // T 类型的对象列表，例如 RedditComment 对象
  ]
}
```

## 3. 控制器 API

#### 3.1. `SocialMediaAnalysisController`

*   **基础路径**: `/api/analysis`

##### 3.1.1. 获取指定地理位置的帖子数据（分页）

*   **GET** `/comments/location/{location}`
*   **描述**: 根据地理位置ID获取相关的帖子或评论，结果分页。
*   **路径参数**:
    *   `location` (string, 必选): 地理位置ID (`loc_pid`)。
*   **查询参数**:
    *   `page` (integer, 可选, 默认: 1): 请求的页码。
    *   `size` (integer, 可选, 默认: 10): 每页的记录数量。
*   **成功响应 (200 OK)**:
    *   类型: `PageResponseDTO<RedditComment>`
    *   **JSON 示例**:
        ```json
        {
          "currentPage": 1,
          "pageSize": 10,
          "totalCount": 50,
          "totalPages": 5,
          "data": [
            {
              "id": "comment123",
              "author": "userA",
              "title": "Great place!",
              "text": "I really enjoyed my time here.",
              "created_utc": 1678886400,
              "url": "http://reddit.com/r/example/comment123",
              "loc_pid": "G012345",
              "state": "VIC",
              "sentiment_score": 0.8,
              "sentiment_magnitude": 0.9,
              "emotion": "JOY",
              "topic_category": "general_housing"
            }
            // ... 更多 RedditComment 对象
          ]
        }
        ```

##### 3.1.2. 获取指定州/省的帖子数据（分页）

*   **GET** `/comments/state/{state}`
*   **描述**: 根据州/省份获取相关的帖子或评论，结果分页。
*   **路径参数**:
    *   `state` (string, 必选): 州/省份的名称 (例如: "VIC", "NSW")。
*   **查询参数**:
    *   `page` (integer, 可选, 默认: 1): 请求的页码。
    *   `size` (integer, 可选, 默认: 10): 每页的记录数量。
*   **成功响应 (200 OK)**:
    *   类型: `PageResponseDTO<RedditComment>` (结构同上 3.1.1)

##### 3.1.3. 获取指定情感类型的帖子数据（分页）

*   **GET** `/comments/emotion/{emotionType}`
*   **描述**: 根据情感类型获取相关的帖子或评论，结果分页。
*   **路径参数**:
    *   `emotionType` (string, 必选): 情感类型 (例如: "JOY", "ANGER", "SADNESS")。
*   **查询参数**:
    *   `page` (integer, 可选, 默认: 1): 请求的页码。
    *   `size` (integer, 可选, 默认: 10): 每页的记录数量。
*   **成功响应 (200 OK)**:
    *   类型: `PageResponseDTO<RedditComment>` (结构同上 3.1.1)

##### 3.1.4. 获取地图分析数据 - 特定主题各地区情感分析

*   **GET** `/map/{state}/{category}`
*   **描述**: 获取用于地图可视化的数据，展示特定州内不同地区关于特定主题的平均情感和帖子数量。
*   **路径参数**:
    *   `state` (string, 必选): 州/省份的名称。
    *   `category` (string, 必选): 主题类别 (参见 1. 通用说明中的 `TopicCategory` 枚举值)。
*   **成功响应 (200 OK)**:
    *   类型: `List<GeoSentimentDTO>`
    *   **`GeoSentimentDTO` 结构**:
        ```json
        {
          "locPid": "string",           // 地理位置ID
          "locationName": "string",     // 地理位置名称
          "averageSentiment": "number", // 平均情感得分
          "postCount": "integer"        // 帖子数量
        }
        ```
    *   **JSON 示例**:
        ```json
        [
          {
            "locPid": "G012345",
            "locationName": "Melbourne CBD",
            "averageSentiment": 0.65,
            "postCount": 150
          },
          {
            "locPid": "G067890",
            "locationName": "Sydney CBD",
            "averageSentiment": -0.2,
            "postCount": 95
          }
          // ... 更多 GeoSentimentDTO 对象
        ]
        ```

##### 3.1.5. 获取饼图数据 - 主题讨论量分布

*   **GET** `/pie/{state}`
*   **描述**: 获取用于饼图可视化的数据，展示特定州内不同主题的讨论量和平均情感。
*   **路径参数**:
    *   `state` (string, 必选): 州/省份的名称。
*   **成功响应 (200 OK)**:
    *   类型: `List<TopicSentimentDTO>`
    *   **`TopicSentimentDTO` 结构**:
        ```json
        {
          "topic": "string",            // 主题类别 (例如: "general_housing")
          "postCount": "integer",       // 帖子数量
          "averageSentiment": "number"  // 该主题的平均情感得分
        }
        ```
    *   **JSON 示例**:
        ```json
        [
          {
            "topic": "general_housing",
            "postCount": 250,
            "averageSentiment": 0.5
          },
          {
            "topic": "rental",
            "postCount": 180,
            "averageSentiment": -0.1
          }
          // ... 更多 TopicSentimentDTO 对象
        ]
        ```

##### 3.1.6. 获取雷达图数据 - 主题平均情感得分

*   **GET** `/radar/{state}`
*   **描述**: 获取用于雷达图可视化的数据，展示特定州内各个主题的平均情感得分。
*   **路径参数**:
    *   `state` (string, 必选): 州/省份的名称。
*   **成功响应 (200 OK)**:
    *   类型: `Map<String, Float>` (键为主题类别，值为平均情感得分)
    *   **JSON 示例**:
        ```json
        {
          "general_housing": 0.5,
          "rental": -0.2,
          "wage": 0.1,
          "mental_health": 0.8,
          "immigration": -0.5
        }
        ```

##### 3.1.7. 获取折线图数据 - 情感随时间变化趋势

*   **GET** `/line/{state}/{category}`
*   **描述**: 获取用于折线图可视化的数据，展示特定州内特定主题的情感随时间（按月）的变化趋势。
*   **路径参数**:
    *   `state` (string, 必选): 州/省份的名称。
    *   `category` (string, 必选): 主题类别 (参见 1. 通用说明中的 `TopicCategory` 枚举值)。
*   **查询参数**:
    *   `monthCount` (integer, 可选, 默认: 12): 要获取的最近月份数量。
*   **成功响应 (200 OK)**:
    *   类型: `List<TimeSentimentDTO>`
    *   **`TimeSentimentDTO` 结构**:
        ```json
        {
          "date": "string",             // 日期 (通常为月份，例如 "YYYY-MM")
          "averageSentiment": "number", // 该月份的平均情感得分
          "postCount": "integer"        // 该月份的帖子数量
        }
        ```
    *   **JSON 示例**:
        ```json
        [
          {
            "date": "2024-03",
            "averageSentiment": 0.7,
            "postCount": 30
          },
          {
            "date": "2024-04",
            "averageSentiment": 0.6,
            "postCount": 45
          }
          // ... 更多 TimeSentimentDTO 对象
        ]
        ```

##### 3.1.8. 获取热力图数据 - 主题相关性分析

*   **GET** `/heatmap/{state}`
*   **描述**: 获取用于热力图可视化的数据，展示特定州内不同主题之间的相关性。
*   **路径参数**:
    *   `state` (string, 必选): 州/省份的名称。
*   **成功响应 (200 OK)**:
    *   类型: `List<CorrelationDTO>`
    *   **`CorrelationDTO` 结构**:
        ```json
        {
          "topic1": "string",       // 第一个主题类别
          "topic2": "string",       // 第二个主题类别
          "correlation": "number"   // 两个主题之间的相关系数
        }
        ```
    *   **JSON 示例**:
        ```json
        [
          {
            "topic1": "general_housing",
            "topic2": "rental",
            "correlation": 0.65
          },
          {
            "topic1": "general_housing",
            "topic2": "wage",
            "correlation": 0.4
          }
          // ... 更多 CorrelationDTO 对象
        ]
        ```

#### 3.2. `RedditCommentController`

*   **基础路径**: `/api/comments`
*   **注意**: 此控制器的接口返回原始评论列表，不进行分页。

##### 3.2.1. 获取指定地理位置的评论

*   **GET** `/location/{location}`
*   **描述**: 根据地理位置ID获取所有相关的帖子或评论。
*   **路径参数**:
    *   `location` (string, 必选): 地理位置ID (`loc_pid`)。
*   **成功响应 (200 OK)**:
    *   类型: `List<RedditComment>`
    *   **JSON 示例**:
        ```json
        [
          {
            "id": "comment123",
            "author": "userA",
            "title": "Great place!",
            "text": "I really enjoyed my time here.",
            "created_utc": 1678886400,
            "url": "http://reddit.com/r/example/comment123",
            "loc_pid": "G012345",
            "state": "VIC",
            "sentiment_score": 0.8,
            "sentiment_magnitude": 0.9,
            "emotion": "JOY",
            "topic_category": "general_housing"
          },
          {
            "id": "comment456",
            "author": "userB",
            "title": "Not so great.",
            "text": "I had a bad experience.",
            "created_utc": 1678886500,
            "url": "http://reddit.com/r/example/comment456",
            "loc_pid": "G012346",
            "state": "NSW",
            "sentiment_score": -0.5,
            "sentiment_magnitude": 0.7,
            "emotion": "ANGER",
            "topic_category": "rental"
          }
        ]
        ```

##### 3.2.2. 获取指定州的评论

*   **GET** `/state/{state}`
*   **描述**: 根据州/省份获取所有相关的帖子或评论。
*   **路径参数**:
    *   `state` (string, 必选): 州/省份的名称。
*   **成功响应 (200 OK)**:
    *   类型: `List<RedditComment>` (结构同上 3.2.1)

##### 3.2.3. 获取指定情感类型的评论

*   **GET** `/emotion/{emotionType}`
*   **描述**: 根据情感类型获取所有相关的帖子或评论。
*   **路径参数**:
    *   `emotionType` (string, 必选): 情感类型。
*   **成功响应 (200 OK)**:
    *   类型: `List<RedditComment>` (结构同上 3.2.1)

#### 3.3. `HyperAnalysisController`

*   **基础路径**: `/api/analysis/hyper`
*   **描述**: 提供基于AI的高级分析功能。

##### 3.3.1. 分析地区热议内容

*   **GET** `/local-hot-topics`
*   **描述**: 对指定地区的最新评论进行AI分析，生成热点话题摘要、关键点等。
*   **查询参数**:
    *   `locPid` (string, 必选): 地区ID。
    *   `limit` (integer, 可选, 默认: 10): 用于分析的最新评论条数。
*   **成功响应 (200 OK)**:
    *   类型: `AnalysisCard`
    *   **`AnalysisCard` 结构 (示例)**:
        ```json
        {
          "title": "string",                // 分析卡片标题 (例如: "墨尔本市中心近期热议话题")
          "summary": "string",              // AI生成的摘要
          "keyPoints": ["string"],          // AI提取的关键点列表
          "sentimentDistribution": {        // 情感分布 (结构可能依实现而定)
            "positive": "integer",
            "neutral": "integer",
            "negative": "integer"
          },
          "representativeComments": [       // 代表性评论列表
            {
              "text": "string",             // 评论文本
              "sentiment": "string"         // 评论情感
            }
          ],
          "averageSentimentScore": "number",// 平均情感得分
          "relatedTopics": ["string"]       // AI识别的相关主题列表
        }
        ```
    *   **JSON 示例**:
        ```json
        {
          "title": "墨尔本市中心近期热议话题分析",
          "summary": "近期讨论主要集中在生活成本和交通问题上，多数评论表达了对当前状况的担忧，但也有部分积极反馈指向城市文化活动。",
          "keyPoints": [
            "生活成本持续上升是主要担忧。",
            "公共交通的可靠性受到质疑。",
            "对城市文化和夜生活表示满意。"
          ],
          "sentimentDistribution": {
            "positive": 20,
            "neutral": 30,
            "negative": 50
          },
          "representativeComments": [
            {
              "text": "房租太高了，简直活不下去！",
              "sentiment": "negative"
            },
            {
              "text": "昨晚的音乐节太棒了！",
              "sentiment": "positive"
            }
          ],
          "averageSentimentScore": -0.15,
          "relatedTopics": ["cost_of_living", "public_transport", "city_events"]
        }
        ```

##### 3.3.2. 分析特定主题的讨论

*   **GET** `/topic-discussion`
*   **描述**: 对指定地区关于特定主题的最新评论进行AI分析。
*   **查询参数**:
    *   `locPid` (string, 必选): 地区ID。
    *   `topicCategory` (string, 必选): 主题类别 (参见 1. 通用说明中的 `TopicCategory` 枚举值)。
    *   `limit` (integer, 可选, 默认: 10): 用于分析的最新评论条数。
*   **成功响应 (200 OK)**:
    *   类型: `AnalysisCard` (结构同上 3.3.1)

#### 3.4. `HealthCheckController`

*   **基础路径**: `/api`

##### 3.4.1. 健康检查

*   **GET** `/health`
*   **描述**: 检查应用后端服务的健康状态。
*   **成功响应 (200 OK)**:
    *   **JSON 示例**:
        ```json
        {
          "status": "UP",
          "message": "Spring Boot application is running"
        }
        ```
