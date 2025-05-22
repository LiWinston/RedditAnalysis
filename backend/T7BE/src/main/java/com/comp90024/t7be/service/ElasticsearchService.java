/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.service;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.query_dsl.*;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.aggregations.*;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.elasticsearch.core.SearchResponse;
import co.elastic.clients.elasticsearch._types.Script;
import co.elastic.clients.json.JsonData;
import co.elastic.clients.util.ObjectBuilder;
import co.elastic.clients.elasticsearch.core.search.TotalHits;
import com.comp90024.t7be.model.RedditComment;
import com.comp90024.t7be.model.dto.GeoSentimentDTO;
import com.comp90024.t7be.model.dto.TopicSentimentDTO;
import com.comp90024.t7be.model.dto.TimeSentimentDTO;
import com.comp90024.t7be.model.enums.TopicCategory;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.HttpEntity;
import org.apache.http.entity.ContentType;
import org.apache.http.nio.entity.NStringEntity;
import org.apache.http.util.EntityUtils;
import org.elasticsearch.client.Request;
import org.elasticsearch.client.Response;
import org.elasticsearch.client.RestClient;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.Objects;

/**
 * Elasticsearch service implementation.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ElasticsearchService implements IElasticsearchService {

    private final ElasticsearchClient elasticsearchClient;
    private final RestClient restClient;
    private final ObjectMapper objectMapper;
    private static final String INDEX_NAME = "all_content_processed_vectorized_v3";
    
    /**
     * Executes a native DSL query using the low-level RestClient to send REST requests.
     *
     * @param endpoint Request endpoint, e.g., "/indexName/_search"
     * @param dslJson DSL query JSON string
     * @return Response result as JsonNode
     * @throws IOException if the request fails
     */
    private JsonNode executeNativeQuery(String endpoint, String dslJson) throws IOException {
        // Create request
        Request request = new Request("POST", endpoint);
        HttpEntity entity = new NStringEntity(dslJson, ContentType.APPLICATION_JSON);
        request.setEntity(entity);
        
        // Execute request
        Response response = restClient.performRequest(request);
        
        // Parse response
        String responseBody = EntityUtils.toString(response.getEntity());
        return objectMapper.readTree(responseBody);
    }
    
    /**
     * Extracts a list of RedditComment from the ES response JsonNode.
     * 
     * @param responseJson ES response JsonNode
     * @return List of RedditComment
     */
    private List<RedditComment> extractCommentsFromResponse(JsonNode responseJson) {
        List<RedditComment> comments = new ArrayList<>();
        
        // 提取hits数组
        JsonNode hits = responseJson.path("hits").path("hits");
        for (JsonNode hit : hits) {
            try {
                // 从_source字段解析RedditComment
                JsonNode source = hit.path("_source");
                if (source.isObject()) {
                    RedditComment comment = objectMapper.treeToValue(source, RedditComment.class);
                    comments.add(comment);
                }
            } catch (JsonProcessingException e) {
                e.printStackTrace();
            }
        }
        
        return comments;
    }

    /**
     * 获取指定地区最新的评论
     * @param locPid 地区ID
     * @param limit 返回条数
     * @return 评论列表
     */
    public List<RedditComment> getRecentCommentsByLocPid(String locPid, int limit) {
        try {
            Query query = TermQuery.of(t -> t
                    .field("loc_pid")
                    .value(locPid)
            )._toQuery();

            SearchResponse<RedditComment> response = elasticsearchClient.search(s -> s
                    .index(INDEX_NAME)
                    .query(query)
                    .sort(sort -> sort
                            .field(f -> f
                                    .field("@timestamp")
                                    .order(SortOrder.Desc)
                            )
                    )
                    .size(limit),
                    RedditComment.class
            );

            return response.hits().hits().stream()
                    .map(hit -> hit.source())
                    .toList();
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }

    /**
     * 获取指定地区和主题的评论
     * @param locPid 地区ID
     * @param category 主题类别
     * @param limit 返回条数
     * @return 评论列表
     */
    public List<RedditComment> getCommentsByLocPidAndTopic(String locPid, TopicCategory category, int limit) {
        try {
            BoolQuery.Builder boolQuery = new BoolQuery.Builder();
            
            // 添加地区ID查询
            boolQuery.must(TermQuery.of(t -> t
                    .field("loc_pid")
                    .value(locPid)
            )._toQuery());
            
            // 添加主题类别查询
            boolQuery.must(TermQuery.of(t -> t
                    .field(category.getBooleanField())
                    .value(true)
            )._toQuery());

            SearchResponse<RedditComment> response = elasticsearchClient.search(s -> s
                    .index(INDEX_NAME)
                    .query(boolQuery.build()._toQuery())
                    .sort(sort -> sort
                            .field(f -> f
                                    .field("@timestamp")
                                    .order(SortOrder.Desc)
                            )
                    )
                    .size(limit),
                    RedditComment.class
            );

            return response.hits().hits().stream()
                    .map(hit -> hit.source())
                    .toList();
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }

    @Override
    public List<RedditComment> searchByLocation(String location) {
        try {
            // 构建DSL查询字符串，使用用户指定的分页大小
            String dslQuery = String.format("""
                {
                  "query": {
                    "match": {
                      "location": "%s"
                    }
                  },
                  "size": 1000
                }
                """, location);
            
            // 使用RestClient执行查询
            JsonNode response = executeNativeQuery("/" + INDEX_NAME + "/_search", dslQuery);
            
            // 从响应中提取评论
            return extractCommentsFromResponse(response);
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }

    @Override
    public List<RedditComment> searchByState(String state) {
        try {
            // 构建DSL查询字符串，使用用户指定的分页大小
            String dslQuery = String.format("""
                {
                  "query": {
                    "match": {
                      "state": "%s"
                    }
                  },
                  "size": 1000
                }
                """, state);
            
            // 使用RestClient执行查询
            JsonNode response = executeNativeQuery("/" + INDEX_NAME + "/_search", dslQuery);
            
            // 从响应中提取评论
            return extractCommentsFromResponse(response);
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }

    @Override
    public List<RedditComment> searchByEmotionType(String emotionType) {
        try {
            // 构建DSL查询字符串，使用更大的分页大小
            String dslQuery = String.format("""
                {
                  "query": {
                    "match": {
                      "basic_emotion": "%s"
                    }
                  },
                  "size": 1000
                }
                """, emotionType);
            
            // 使用RestClient执行查询
            JsonNode response = executeNativeQuery("/" + INDEX_NAME + "/_search", dslQuery);
            
            // 从响应中提取评论
            return extractCommentsFromResponse(response);
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }
    
    /**
     * 按主题类别搜索
     * @param category 主题类别
     * @return 匹配的评论列表
     */
    @Override
    public List<RedditComment> searchByTopicCategory(TopicCategory category) {
        try {
            // 构建DSL查询字符串，调整布尔值查询和分页大小
            String dslQuery = String.format("""
                {
                  "query": {
                    "term": {
                      "%s": true
                    }
                  },
                  "size": 1000
                }
                """, category.getBooleanField());
            
            // 输出DSL查询以便调试
            System.out.println("执行主题类别查询: " + dslQuery);
            
            // 使用RestClient执行查询
            JsonNode response = executeNativeQuery("/" + INDEX_NAME + "/_search", dslQuery);
            
            // 从响应中提取评论
            return extractCommentsFromResponse(response);
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }
    
    /**
     * 按时间范围和主题类别搜索评论
     * @param startDate 开始日期（格式：yyyy-MM-dd'T'HH:mm:ss.SSS'Z'）
     * @param endDate 结束日期（格式：yyyy-MM-dd'T'HH:mm:ss.SSS'Z'）
     * @param category 主题类别
     * @return 匹配的评论列表
     */
    @Override
    public List<RedditComment> searchByTimeRangeAndTopic(String startDate, String endDate, TopicCategory category) {
        try {
            // 构建DSL查询字符串
            String dslQuery = String.format("""
                {
                  "query": {
                    "bool": {
                      "must": [
                        {
                          "term": {
                            "%s": true
                          }
                        },
                        {
                          "range": {
                            "@timestamp": {
                              "gte": "%s",
                              "lte": "%s"
                            }
                          }
                        }
                      ]
                    }
                  },
                  "size": 1000
                }
                """, category.getBooleanField(), startDate, endDate);
            
            // 使用RestClient执行查询
            JsonNode response = executeNativeQuery("/" + INDEX_NAME + "/_search", dslQuery);
            
            // 从响应中提取评论
            return extractCommentsFromResponse(response);
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }
    
    /**
     * 按位置和主题类别搜索评论
     * @param location 位置
     * @param category 主题类别
     * @return 评论列表
     */
    @Override
    public List<RedditComment> searchByLocationAndTopic(String location, TopicCategory category) {
        try {
            // 构建DSL查询字符串
            String dslQuery = String.format("""
                {
                  "query": {
                    "bool": {
                      "must": [
                        { "match": { "location": "%s" } },
                        { "term": { "%s": true } }
                      ]
                    }
                  },
                  "size": 1000
                }
                """, location, category.getBooleanField());
            
            // 输出DSL查询以便调试
            System.out.println("执行位置主题查询: " + dslQuery);
            
            // 使用RestClient执行查询
            JsonNode response = executeNativeQuery("/" + INDEX_NAME + "/_search", dslQuery);
            
            // 从响应中提取评论
            return extractCommentsFromResponse(response);
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }
    
    /**
     * 按州和主题类别搜索
     * @param state 州名称
     * @param category 主题类别
     * @return 匹配的评论列表
     */
    @Override
    public List<RedditComment> searchByStateAndTopic(String state, TopicCategory category) {
        try {
            // 构建DSL查询字符串
            String dslQuery = String.format("""
                {
                  "query": {
                    "bool": {
                      "must": [
                        { "match": { "state": "%s" } },
                        { "term": { "%s": true } }
                      ]
                    }
                  },
                  "size": 1000
                }
                """, state, category.getBooleanField());
            
            // 输出DSL查询以便调试
            System.out.println("执行州主题查询: " + dslQuery);
            
            // 使用RestClient执行查询
            JsonNode response = executeNativeQuery("/" + INDEX_NAME + "/_search", dslQuery);
            
            // 从响应中提取评论
            return extractCommentsFromResponse(response);
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }

    /**
     * 更新评论的嵌入向量字段
     *
     * @param commentId 评论ID
     * @param embedding 嵌入向量
     * @return 更新是否成功
     */
    public boolean updateCommentEmbedding(String commentId, List<Float> embedding) {
        try {
            // 使用JSON格式存储向量
            Map<String, Object> updateDoc = new HashMap<>();
            updateDoc.put("text_vector", embedding);
            
            // 使用ES客户端更新文档
            JsonData jsonData = JsonData.of(updateDoc);
            elasticsearchClient.update(u -> u
                    .index(INDEX_NAME)
                .id(commentId)
                .doc(jsonData), 
                Void.class
            );
            
            return true;
        } catch (Exception e) {
            return false;
        }
    }
    
    /**
     * 使用向量搜索找到与查询向量相似的评论
     * 
     * @param queryEmbedding 查询向量
     * @param minScore 最小相似度分数
     * @param limit 结果数量限制
     * @param locPid 可选的地区PID过滤
     * @param state 可选的州/领地过滤
     * @param location 可选的位置名称过滤
     * @param topics 可选的主题过滤（逗号分隔的主题列表，如"rental,wage"）
     * @return 相似评论列表
     */
    public List<RedditComment> findSimilarCommentsByEmbedding(
            List<Float> queryEmbedding, 
            double minScore, 
            int limit,
            String locPid,
            String state,
            String location,
            String topics) {
        try {
            if (queryEmbedding == null || queryEmbedding.isEmpty()) {
                log.error("查询向量为空，无法执行向量搜索");
                return Collections.emptyList();
            }
            
            log.info("执行向量搜索，查询向量维度: {}, 最小分数: {}, 限制: {}", 
                    queryEmbedding.size(), minScore, limit);
            log.info("地理约束 - locPid: {}, state: {}, location: {}, 主题过滤: {}", 
                    locPid, state, location, topics);
            
            // 构建过滤条件（如果有）
            boolean hasFilters = locPid != null || state != null || location != null || topics != null;
            final Query[] filterQueryHolder = new Query[1]; // 使用数组保存，确保变量是effectively final的
            
            if (hasFilters) {
                List<Query> filterQueries = new ArrayList<>();
                
                // 地理约束 (三选一)
                if (locPid != null && !locPid.isBlank()) {
                    filterQueries.add(MatchQuery.of(m -> m
                        .field("loc_pid")
                        .query(locPid)
                    )._toQuery());
                } else if (state != null && !state.isBlank()) {
                    filterQueries.add(MatchQuery.of(m -> m
                        .field("state")
                        .query(state)
                    )._toQuery());
                } else if (location != null && !location.isBlank()) {
                    filterQueries.add(MatchQuery.of(m -> m
                        .field("location")
                        .query(location)
                    )._toQuery());
                }
                
                // 主题约束 (多选，以逗号分隔，是或的关系)
                if (topics != null && !topics.isBlank()) {
                    String[] topicArray = topics.split(",");
                    if (topicArray.length > 0) {
                        List<Query> topicQueries = new ArrayList<>();
                        
                        for (String topicKey : topicArray) {
                            String trimmedTopicKey = topicKey.trim();
                            if (!trimmedTopicKey.isEmpty()) {
                                // 将主题关键字转换为TopicCategory枚举
                                TopicCategory category = TopicCategory.fromQueryKey(trimmedTopicKey);
                                if (category != null) {
                                    // 使用布尔字段名称构建查询
                                    String booleanField = category.getBooleanField();
                                    log.debug("添加主题过滤，字段: {}, 值: true", booleanField);
                                    
                                    topicQueries.add(TermQuery.of(t -> t
                                        .field(booleanField)
                                        .value(true)
                                    )._toQuery());
                                } else {
                                    log.warn("未知主题关键字: {}", trimmedTopicKey);
                                }
                            }
                        }
                        
                        if (!topicQueries.isEmpty()) {
                            // 将所有主题条件以OR关系组合
                            filterQueries.add(BoolQuery.of(b -> b
                                .should(topicQueries)
                                .minimumShouldMatch("1")
                            )._toQuery());
                        }
                    }
                }
                
                // 将所有过滤条件组合起来
                if (!filterQueries.isEmpty()) {
                    filterQueryHolder[0] = BoolQuery.of(b -> b
                        .must(filterQueries)
                    )._toQuery();
                }
            }
            
            SearchRequest.Builder searchRequestBuilder;
            
            if (hasFilters && filterQueryHolder[0] != null) {
                // 方法1：使用bool查询结合filter子句和knn子句
                // 注意：这种方法仅在Elasticsearch 8.4及以上版本支持
                searchRequestBuilder = new SearchRequest.Builder()
                    .index(INDEX_NAME)
                    .query(q -> q
                        .bool(b -> b
                            .filter(filterQueryHolder[0])
                            .must(m -> m
                                .knn(knn -> knn
                                    .field("text_vector")
                                    .queryVector(queryEmbedding)
                                    .k(limit) // 保持k值与limit一致
//                                    .numCandidates(limit * 100)
//                                    .similarity((float)minScore)
                                )
                            )
                        )
                    )
                    .source(source -> source
                        .filter(f -> f
                            .excludes("text_vector")
                        )
                    )
                    .size(limit);
            } else {
                // 无过滤条件时的纯KNN查询
                searchRequestBuilder = new SearchRequest.Builder()
                    .index(INDEX_NAME)
                    .query(q -> q
                        .knn(knn -> knn
                            .field("text_vector")
                            .queryVector(queryEmbedding)
                            .k(limit)
//                            .numCandidates(Math.max(limit * 100, 100))
                            .similarity((float)minScore)
                        )
                    )
                    .source(source -> source
                        .filter(f -> f
                            .excludes("text_vector")
                        )
                    )
                    .size(limit);
            }
            
            log.debug("执行查询: {}", searchRequestBuilder);
            
            SearchResponse<RedditComment> response = elasticsearchClient.search(
                searchRequestBuilder.build(),
                RedditComment.class
            );
            
            List<RedditComment> results = response.hits().hits().stream()
                .map(hit -> hit.source())
                .filter(Objects::nonNull)
                .collect(Collectors.toList());
            
            log.info("向量搜索找到 {} 条结果", results.size());
            
            // 添加调试日志，打印结果文本内容，便于评估相关性
            if (!results.isEmpty()) {
                log.info("===== 搜索结果文本内容预览 =====");
                int previewCount = results.size();
                for (int i = 0; i < previewCount; i++) {
                    RedditComment comment = results.get(i);
                    String text = comment.getText() != null && !comment.getText().isEmpty() ? 
                            comment.getText().get(0) : "[空文本]";
                    
                    // 如果文本太长，截断显示
                    String previewText = text.length() > 300 ? 
                            text.substring(0, 297) + "..." : text;
                    
                    log.info("结果 #{}: {}", i + 1, previewText.replaceAll("\\s+", " ").trim());
                    
                    // 显示情感得分和主题标签
                    Float sentimentScore = comment.getFirstSentimentScore();
                    log.info("     情感得分: {}, 地区: {}, 州: {}", 
                            sentimentScore != null ? sentimentScore : "未知", 
                            comment.getFirstLocation(), 
                            comment.getState() != null ? comment.getState().get(0) : "未知");
                    
                    // 显示主题标签
                    List<String> topicLabels = new ArrayList<>();
                    if (comment.getIsGeneralHousing() != null && !comment.getIsGeneralHousing().isEmpty() && comment.getIsGeneralHousing().get(0)) {
                        topicLabels.add("general housing");
                    }
                    if (comment.getIsRental() != null && !comment.getIsRental().isEmpty() && comment.getIsRental().get(0)) {
                        topicLabels.add("rental");
                    }
                    if (comment.getIsWage() != null && !comment.getIsWage().isEmpty() && comment.getIsWage().get(0)) {
                        topicLabels.add("wage");
                    }
                    if (comment.getIsMentalHealth() != null && !comment.getIsMentalHealth().isEmpty() && comment.getIsMentalHealth().get(0)) {
                        topicLabels.add("mental health");
                    }
                    if (comment.getIsImmigration() != null && !comment.getIsImmigration().isEmpty() && comment.getIsImmigration().get(0)) {
                        topicLabels.add("immigration");
                    }
                    log.info("     主题标签: {}", String.join(", ", topicLabels));
                    log.info("--------------------------");
                }
                log.info("===== 预览结束 =====");
            }
            
            return results;
        } catch (Exception e) {
            log.error("向量搜索执行失败: {}", e.getMessage(), e);
            return Collections.emptyList();
        }
    }
    
    // 保留原始方法，但内部调用新的实现
    public List<RedditComment> findSimilarCommentsByEmbedding(List<Float> queryEmbedding, double minScore, int limit) {
        // 调用扩展版本，但不指定地理和主题约束
        return findSimilarCommentsByEmbedding(queryEmbedding, minScore, limit, null, null, null, null);
    }
    
    /**
     * 使用ES聚合获取地理区域情感分析
     * @param state 州名称
     * @param category 主题类别
     * @return 按地区分组的情感统计数据列表
     */
    @Override
    public List<GeoSentimentDTO> getGeoSentimentAggregation(String state, TopicCategory category) {
        try {
            String categoryDisplayName = category != null ? category.getDisplayName() : "所有主题";
            System.out.println("开始查询州 " + state + " 的 " + categoryDisplayName + " 主题数据...");
            
            // 首先获取一些示例文档，检查它们的实际结构
            String sampleDslQuery;
            
            if (category != null) {
                // 有主题过滤
                sampleDslQuery = String.format("""
                    {
                      "query": {
                        "bool": {
                          "must": [
                            { "match": { "state": "%s" } },
                            { "term": { "%s": true } }
                          ]
                        }
                      },
                      "size": 3,
                      "_source": ["location", "loc_pid", "suburb", "sentiment_score", "state"]
                    }
                    """, state, category.getBooleanField());
            } else {
                // 无主题过滤，获取所有帖子
                sampleDslQuery = String.format("""
                    {
                      "query": {
                        "bool": {
                          "must": [
                            { "match": { "state": "%s" } }
                          ]
                        }
                      },
                      "size": 3,
                      "_source": ["location", "loc_pid", "suburb", "sentiment_score", "state"]
                    }
                    """, state);
            }
            
            System.out.println("执行示例数据查询: " + sampleDslQuery);
            JsonNode sampleResponse = executeNativeQuery("/" + INDEX_NAME + "/_search", sampleDslQuery);
            JsonNode sampleHits = sampleResponse.path("hits").path("hits");
            
            // 检查是否有文档返回
            if (sampleHits.size() > 0) {
                System.out.println("返回的示例文档数: " + sampleHits.size());
                // 输出第一个文档的内容以检查字段
                System.out.println("示例文档内容: " + sampleHits.get(0).path("_source").toString());
                
                // 检查location字段是否存在
                if (sampleHits.get(0).path("_source").has("location")) {
                    System.out.println("文档包含location字段");
                } else {
                    System.out.println("文档不包含location字段，检查替代字段");
                }
                
                // 检查suburb字段是否存在作为替代
                if (sampleHits.get(0).path("_source").has("suburb")) {
                    System.out.println("文档包含suburb字段，可以作为替代");
                }
            }
            
            // 确定使用哪个字段作为位置聚合字段
            String locationField = "location";  // 直接使用location字段（是数组类型）
            String locationFieldType = "location";
            
            // 如果没有location字段，尝试使用suburb字段
            if (sampleHits.size() > 0 && !sampleHits.get(0).path("_source").has("location") && 
                sampleHits.get(0).path("_source").has("suburb")) {
                locationField = "suburb";
                locationFieldType = "suburb";
                System.out.println("将使用suburb字段代替location字段进行聚合");
            }
            
            // 根据数据样例修改DSL查询，针对数组字段进行聚合
            String dslQuery;
            
            if (category != null) {
                // 有主题过滤
                dslQuery = String.format("""
                    {
                      "query": {
                        "bool": {
                          "must": [
                            { "match": { "state": "%s" } },
                            { "term": { "%s": true } }
                          ]
                        }
                      },
                      "size": 0,
                      "aggs": {
                        "locations": {
                          "terms": {
                            "field": "location",
                            "size": 1000
                          },
                          "aggs": {
                            "avg_sentiment": {
                              "avg": {
                                "field": "sentiment_score"
                              }
                            },
                            "pos_count": {
                              "filter": {
                                "range": {
                                  "sentiment_score": {
                                    "gt": 0.2
                                  }
                                }
                              }
                            },
                            "neg_count": {
                              "filter": {
                                "range": {
                                  "sentiment_score": {
                                    "lt": -0.2
                                  }
                                }
                              }
                            },
                            "loc_pid": {
                              "terms": {
                                "field": "loc_pid",
                                "size": 10
                              }
                            }
                          }
                        }
                      }
                    }
                    """, state, category.getBooleanField());
            } else {
                // 无主题过滤，获取所有帖子
                dslQuery = String.format("""
                    {
                      "query": {
                        "bool": {
                          "must": [
                            { "match": { "state": "%s" } }
                          ]
                        }
                      },
                      "size": 0,
                      "aggs": {
                        "locations": {
                          "terms": {
                            "field": "location",
                            "size": 1000
                          },
                          "aggs": {
                            "avg_sentiment": {
                              "avg": {
                                "field": "sentiment_score"
                              }
                            },
                            "pos_count": {
                              "filter": {
                                "range": {
                                  "sentiment_score": {
                                    "gt": 0.2
                                  }
                                }
                              }
                            },
                            "neg_count": {
                              "filter": {
                                "range": {
                                  "sentiment_score": {
                                    "lt": -0.2
                                  }
                                }
                              }
                            },
                            "loc_pid": {
                              "terms": {
                                "field": "loc_pid",
                                "size": 10
                              }
                            }
                          }
                        }
                      }
                    }
                    """, state);
            }
            
            // 输出DSL查询以便调试
            System.out.println("执行聚合DSL查询: " + dslQuery);
            
            // 使用RestClient执行查询
            JsonNode response = executeNativeQuery("/" + INDEX_NAME + "/_search", dslQuery);
            System.out.println("查询执行完毕，开始解析结果...");
            
            // 输出聚合结构，帮助理解
            if (response.has("aggregations")) {
                System.out.println("聚合结构: " + response.path("aggregations").toString().substring(0, Math.min(500, response.path("aggregations").toString().length())));
                
                if (response.path("aggregations").has("locations")) {
                    System.out.println("locations聚合存在");
                    
                    JsonNode buckets = response.path("aggregations").path("locations").path("buckets");
                    System.out.println("位置桶数量: " + buckets.size());
                    
                    if (buckets.size() > 0) {
                        System.out.println("第一个桶键值: " + buckets.get(0).path("key").asText());
                        System.out.println("第一个桶文档数: " + buckets.get(0).path("doc_count").asLong());
                    }
                } else {
                    System.out.println("locations聚合不存在，检查聚合结构");
                }
            } else {
                System.out.println("响应中不包含aggregations字段");
            }
            
            // 检查总命中数
            long totalHits = response.path("hits").path("total").path("value").asLong();
            System.out.println("总命中文档数: " + totalHits);
            
            // 如果没有文档，提前返回空列表
            if (totalHits == 0) {
                System.out.println("没有找到匹配的文档，返回空列表");
                return Collections.emptyList();
            }
            
            // 解析聚合结果
            List<GeoSentimentDTO> results = new ArrayList<>();
            JsonNode locationBuckets = response.path("aggregations")
                                            .path("locations")
                                            .path("buckets");
            
            System.out.println("发现位置桶数量: " + locationBuckets.size());
            
            // 正常处理位置桶
            for (JsonNode bucket : locationBuckets) {
                String location = bucket.path("key").asText();
                long totalPosts = bucket.path("doc_count").asLong();
                
                // 获取平均情感分数
                float avgSentiment = 0.0f;
                if (!bucket.path("avg_sentiment").path("value").isNull()) {
                    avgSentiment = (float) bucket.path("avg_sentiment").path("value").asDouble();
                }
                
                // 获取正面评论数量
                long posCount = bucket.path("pos_count").path("doc_count").asLong();
                
                // 获取负面评论数量
                long negCount = bucket.path("neg_count").path("doc_count").asLong();
                
                // 计算中性评论数量
                long neutralCount = totalPosts - posCount - negCount;
                
                // 获取loc_pid
                String locPid = "";
                JsonNode locPidBuckets = bucket.path("loc_pid").path("buckets");
                if (locPidBuckets.isArray() && locPidBuckets.size() > 0) {
                    locPid = locPidBuckets.get(0).path("key").asText();
                } else {
                    // 如果没有loc_pid，使用位置名称作为ID
                    locPid = location + "_" + locationFieldType;
                }
                
                // 计算比例
                float positiveRatio = totalPosts > 0 ? (float) posCount / totalPosts : 0;
                float negativeRatio = totalPosts > 0 ? (float) negCount / totalPosts : 0;
                float neutralRatio = totalPosts > 0 ? (float) neutralCount / totalPosts : 0;
                
                System.out.println("位置: " + location + ", 帖子数: " + totalPosts + 
                                  ", 情感分数: " + avgSentiment + ", locPid: " + locPid);
                
                results.add(GeoSentimentDTO.builder()
                        .location(location)
                        .locPid(locPid)
                        .topicCategory(category != null ? category.getDisplayName() : "ALL")
                        .sentimentScore(avgSentiment)
                        .postCount(totalPosts)
                        .positiveRatio(positiveRatio)
                        .negativeRatio(negativeRatio)
                        .neutralRatio(neutralRatio)
                        .build());
            }
            
            // 如果没有找到任何结果，返回空列表
            if (results.isEmpty()) {
                System.out.println("没有找到任何地理情感数据，返回空列表");
                return Collections.emptyList();
            }
            
            System.out.println("成功构建 " + results.size() + " 条地理情感数据");
            return results;
        } catch (IOException e) {
            System.err.println("获取地理情感数据失败: " + e.getMessage());
            e.printStackTrace();
            return Collections.emptyList();
        }
    }
    
    /**
     * 使用ES聚合获取主题情感分布
     * @param state 州名称
     * @return 各主题的情感统计数据列表
     */
    @Override
    public List<TopicSentimentDTO> getTopicSentimentAggregation(String state) {
        try {
            // 获取州内总帖子数
            String totalDslQuery = String.format("""
                {
                  "query": {
                    "match": {
                      "state": "%s"
                    }
                  },
                  "size": 0
                }
                """, state);
            
            JsonNode totalResponse = executeNativeQuery("/" + INDEX_NAME + "/_search", totalDslQuery);
            long totalPosts = totalResponse.path("hits").path("total").path("value").asLong();
            
            List<TopicSentimentDTO> results = new ArrayList<>();
            
            // 为每个主题执行单独的聚合查询
            for (TopicCategory category : TopicCategory.values()) {
                // 构建DSL查询字符串
                String dslQuery = String.format("""
                    {
                      "query": {
                        "bool": {
                          "must": [
                            { "match": { "state": "%s" } },
                            { "term": { "%s": true } }
                          ]
                        }
                      },
                      "size": 0,
                      "aggs": {
                        "avg_sentiment": {
                          "avg": {
                            "field": "sentiment_score"
                          }
                        }
                      }
                    }
                    """, state, category.getBooleanField());
                
                // 输出DSL查询以便调试
                System.out.println("执行主题分布DSL查询: " + dslQuery);
                
                // 使用RestClient执行查询
                JsonNode response = executeNativeQuery("/" + INDEX_NAME + "/_search", dslQuery);
                
                // 提取统计信息
                long topicPostCount = response.path("hits").path("total").path("value").asLong();
                float percentage = totalPosts > 0 ? (float) topicPostCount / totalPosts : 0;
                
                // 获取平均情感分数
                float avgSentiment = 0.0f;
                JsonNode avgNode = response.path("aggregations")
                                         .path("avg_sentiment")
                                         .path("value");
                
                if (!avgNode.isNull()) {
                    avgSentiment = (float) avgNode.asDouble();
                }
                
                results.add(TopicSentimentDTO.builder()
                        .topicCategory(category.getDisplayName())
                        .postCount(topicPostCount)
                        .averageSentiment(avgSentiment)
                        .percentage(percentage)
                        .build());
            }
            
            return results;
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }
    
    /**
     * 使用ES聚合获取时间情感趋势
     * @param state 州名称
     * @param category 主题类别
     * @param startDate 开始日期
     * @param endDate 结束日期
     * @return 按时间点分组的情感统计数据列表
     */
    @Override
    public List<TimeSentimentDTO> getTimeSentimentAggregation(String state, TopicCategory category, String startDate, String endDate) {
        try {
            // 构建DSL查询字符串
            String dslQuery = String.format("""
                {
                  "query": {
                    "bool": {
                      "must": [
                        { "match": { "state": "%s" } },
                        { "term": { "%s": true } },
                        {
                          "range": {
                            "@timestamp": {
                              "format": "yyyy-MM-dd HH:mm:ss",
                              "gte": "%s",
                              "lte": "%s"
                            }
                          }
                        }
                      ]
                    }
                  },
                  "size": 0,
                  "aggs": {
                    "by_month": {
                      "date_histogram": {
                        "field": "@timestamp",
                        "calendar_interval": "month",
                        "format": "yyyy-MM"
                      },
                      "aggs": {
                        "avg_sentiment": {
                          "avg": {
                            "field": "sentiment_score"
                          }
                        }
                      }
                    }
                  }
                }
                """, state, category.getBooleanField(), startDate, endDate);
            
            // 输出DSL查询以便调试
            System.out.println("执行时间趋势DSL查询: " + dslQuery);
            
            // 使用RestClient执行查询
            JsonNode response = executeNativeQuery("/" + INDEX_NAME + "/_search", dslQuery);
            
            // 解析聚合结果
            List<TimeSentimentDTO> results = new ArrayList<>();
            JsonNode monthBuckets = response.path("aggregations")
                                           .path("by_month")
                                           .path("buckets");
            
            // 遍历每个月份的桶
            for (JsonNode bucket : monthBuckets) {
                String timePoint = bucket.path("key_as_string").asText();
                long postCount = bucket.path("doc_count").asLong();
                
                // 获取平均情感分数
                float avgSentiment = 0.0f;
                if (!bucket.path("avg_sentiment").path("value").isNull()) {
                    avgSentiment = (float) bucket.path("avg_sentiment").path("value").asDouble();
                }
                
                results.add(TimeSentimentDTO.builder()
                        .timePoint(timePoint)
                        .topicCategory(category.getDisplayName())
                        .averageSentiment(avgSentiment)
                        .postCount(postCount)
                        .build());
            }
            
            // 按时间排序
            Collections.sort(results, Comparator.comparing(TimeSentimentDTO::getTimePoint));
            
            return results;
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }

    /**
     * 使用ES聚合获取所有主题的平均情感分数
     * @param state 州名称
     * @return 各主题的平均情感分数
     */
    @Override
    public Map<TopicCategory, Float> getTopicAverageSentimentAggregation(String state) {
        try {
            Map<TopicCategory, Float> result = new HashMap<>();
            
            // 为每个主题执行单独的聚合查询
            for (TopicCategory category : TopicCategory.values()) {
                // 构建DSL查询字符串
                String dslQuery = String.format("""
                    {
                      "query": {
                        "bool": {
                          "must": [
                            { "match": { "state": "%s" } },
                            { "term": { "%s": true } }
                          ]
                        }
                      },
                      "size": 0,
                      "aggs": {
                        "avg_sentiment": {
                          "avg": {
                            "field": "sentiment_score"
                          }
                        }
                      }
                    }
                    """, state, category.getBooleanField());
                
                // 输出DSL查询以便调试
                System.out.println("执行平均情感DSL查询: " + dslQuery);
                
                // 使用RestClient执行查询
                JsonNode response = executeNativeQuery("/" + INDEX_NAME + "/_search", dslQuery);
                
                // 解析聚合结果
                float avgSentiment = 0.0f;
                JsonNode avgNode = response.path("aggregations")
                                         .path("avg_sentiment")
                                         .path("value");
                
                if (!avgNode.isNull()) {
                    avgSentiment = (float) avgNode.asDouble();
                }
                
                result.put(category, avgSentiment);
            }
            
            return result;
        } catch (IOException e) {
            e.printStackTrace();
            return Collections.emptyMap();
        }
    }
} 