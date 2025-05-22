/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.service;

import com.comp90024.t7be.model.RedditComment;
import com.comp90024.t7be.model.dto.*;
import com.comp90024.t7be.model.enums.TopicCategory;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.text.SimpleDateFormat;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Social media analysis service implementation.
 */
@Service
@RequiredArgsConstructor
public class SocialMediaAnalysisService implements ISocialMediaAnalysisService {

    private final IElasticsearchService elasticsearchService;
    
    @Override
    public PageResponseDTO<RedditComment> getCommentsByLocation(String location, int page, int size) {
        List<RedditComment> comments = elasticsearchService.searchByLocation(location);
        return createPageResponse(comments, page, size);
    }
    
    @Override
    public PageResponseDTO<RedditComment> getCommentsByState(String state, int page, int size) {
        List<RedditComment> comments = elasticsearchService.searchByState(state);
        return createPageResponse(comments, page, size);
    }
    
    @Override
    public PageResponseDTO<RedditComment> getCommentsByEmotionType(String emotionType, int page, int size) {
        List<RedditComment> comments = elasticsearchService.searchByEmotionType(emotionType);
        return createPageResponse(comments, page, size);
    }
    
    @Override
    public List<GeoSentimentDTO> getGeoSentimentAnalysis(String state, TopicCategory category) {
        // Use ES aggregation query instead of in-memory analysis
        return elasticsearchService.getGeoSentimentAggregation(state, category);
    }
    
    @Override
    public List<TopicSentimentDTO> getTopicSentimentDistribution(String state) {
        // Use ES aggregation query instead of in-memory analysis
        return elasticsearchService.getTopicSentimentAggregation(state);
    }
    
    @Override
    public Map<TopicCategory, Float> getTopicAverageSentiment(String state) {
        // Use ES aggregation query instead of in-memory analysis
        return elasticsearchService.getTopicAverageSentimentAggregation(state);
    }
    
    @Override
    public List<TimeSentimentDTO> getTimeSentimentTrend(String state, TopicCategory category, int monthCount) {
        // Calculate start date (current date minus monthCount months)
        Calendar calendar = Calendar.getInstance();
        calendar.add(Calendar.MONTH, -monthCount);
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        String startDate = sdf.format(calendar.getTime());
        String endDate = sdf.format(new Date());
        
        // 使用ES聚合查询替代内存中分析
        return elasticsearchService.getTimeSentimentAggregation(state, category, startDate, endDate);
    }
    
    @Override
    public List<CorrelationDTO> getTopicCorrelationAnalysis(String state) {
        // 获取所有地区各主题的平均情感分数
        List<GeoSentimentDTO> allGeoSentiments = new ArrayList<>();
        for (TopicCategory category : TopicCategory.values()) {
            List<GeoSentimentDTO> geoSentiments = elasticsearchService.getGeoSentimentAggregation(state, category);
            System.out.println("获取主题 " + category.getDisplayName() + " 的地理情感数据，找到 " + geoSentiments.size() + " 条记录");
            allGeoSentiments.addAll(geoSentiments);
        }
        
        // 按地区整理各主题的情感分数
        Map<String, Map<TopicCategory, Float>> locationTopicSentiments = new HashMap<>();
        for (GeoSentimentDTO geoSentiment : allGeoSentiments) {
            String location = geoSentiment.getLocation();
            TopicCategory category = TopicCategory.fromQueryKey(geoSentiment.getTopicCategory());
            if (category == null) {
                System.out.println("无法识别的主题类别: " + geoSentiment.getTopicCategory());
                continue;
            }
            
            locationTopicSentiments.computeIfAbsent(location, k -> new HashMap<>())
                    .put(category, geoSentiment.getSentimentScore());
        }
        
        System.out.println("按地区整理后得到 " + locationTopicSentiments.size() + " 个地区的数据");
        
        // 计算主题之间的相关性
        List<CorrelationDTO> result = new ArrayList<>();
        TopicCategory[] categories = TopicCategory.values();
        
        for (int i = 0; i < categories.length; i++) {
            for (int j = i; j < categories.length; j++) {  // 只计算上三角矩阵
                TopicCategory topicA = categories[i];
                TopicCategory topicB = categories[j];
                
                // 收集所有地区两个主题的情感分数
                List<Float> topicAScores = new ArrayList<>();
                List<Float> topicBScores = new ArrayList<>();
                
                for (Map<TopicCategory, Float> topicSentiments : locationTopicSentiments.values()) {
                    if (topicSentiments.containsKey(topicA) && topicSentiments.containsKey(topicB)) {
                        Float scoreA = topicSentiments.get(topicA);
                        Float scoreB = topicSentiments.get(topicB);
                        
                        // 确保分数不为null且非NaN
                        if (scoreA != null && !Float.isNaN(scoreA) && scoreB != null && !Float.isNaN(scoreB)) {
                            topicAScores.add(scoreA);
                            topicBScores.add(scoreB);
                        }
                    }
                }
                
                System.out.println("计算 " + topicA.getDisplayName() + " 和 " + topicB.getDisplayName() + 
                                   " 的相关性，有效数据点: " + topicAScores.size());
                
                // 计算相关系数
                float correlation = calculateCorrelation(topicAScores, topicBScores);
                
                // 构建结果DTO
                result.add(CorrelationDTO.builder()
                        .topicA(topicA.getDisplayName())
                        .topicB(topicB.getDisplayName())
                        .correlationCoefficient(correlation)
                        .build());
            }
        }
        
        return result;
    }
    
    /**
     * 辅助方法：计算皮尔逊相关系数
     */
    private float calculateCorrelation(List<Float> xValues, List<Float> yValues) {
        if (xValues.size() != yValues.size() || xValues.isEmpty()) {
            return 0f;
        }
        
        int n = xValues.size();
        if (n < 2) {
            System.out.println("数据点不足，无法计算相关性: " + n);
            return 0f;
        }
        
        // 计算平均值
        float xMean = 0f, yMean = 0f;
        for (int i = 0; i < n; i++) {
            xMean += xValues.get(i);
            yMean += yValues.get(i);
        }
        xMean /= n;
        yMean /= n;
        
        System.out.println("均值 x: " + xMean + ", y: " + yMean);
        
        // 计算分子和分母
        float numerator = 0f, denominatorX = 0f, denominatorY = 0f;
        for (int i = 0; i < n; i++) {
            float xDiff = xValues.get(i) - xMean;
            float yDiff = yValues.get(i) - yMean;
            numerator += xDiff * yDiff;
            denominatorX += xDiff * xDiff;
            denominatorY += yDiff * yDiff;
        }
        
        System.out.println("分子: " + numerator + ", 分母X: " + denominatorX + ", 分母Y: " + denominatorY);
        
        // 计算相关系数
        if (denominatorX > 0 && denominatorY > 0) {
            float correlation = numerator / (float) Math.sqrt(denominatorX * denominatorY);
            System.out.println("计算得到相关系数: " + correlation);
            return correlation;
        } else {
            System.out.println("分母为零，无法计算相关系数");
            return 0f;
        }
    }
    
    /**
     * 辅助方法：获取布尔字段值
     */
    private boolean getBooleanValue(RedditComment comment, String booleanField) {
        switch (booleanField) {
            case "isGeneralHousing":
                return comment.getIsGeneralHousing() != null 
                        && !comment.getIsGeneralHousing().isEmpty() 
                        && comment.getIsGeneralHousing().get(0);
            case "isRental":
                return comment.getIsRental() != null 
                        && !comment.getIsRental().isEmpty() 
                        && comment.getIsRental().get(0);
            case "isMentalHealth":
                return comment.getIsMentalHealth() != null 
                        && !comment.getIsMentalHealth().isEmpty() 
                        && comment.getIsMentalHealth().get(0);
            case "isWage":
                return comment.getIsWage() != null 
                        && !comment.getIsWage().isEmpty() 
                        && comment.getIsWage().get(0);
            case "isImmigration":
                return comment.getIsImmigration() != null 
                        && !comment.getIsImmigration().isEmpty() 
                        && comment.getIsImmigration().get(0);
            default:
                return false;
        }
    }
    
    /**
     * 创建分页响应，使用已经获取的所有数据
     */
    private <T> PageResponseDTO<T> createPageResponse(List<T> data, int page, int size) {
        if (data == null) {
            data = Collections.emptyList();
        }
        
        int startIndex = (page - 1) * size;
        int endIndex = Math.min(startIndex + size, data.size());
        List<T> pageData = startIndex < data.size() ? data.subList(startIndex, endIndex) : Collections.emptyList();
        
        int totalPages = (int) Math.ceil((double) data.size() / size);
        
        return PageResponseDTO.<T>builder()
                .currentPage(page)
                .pageSize(size)
                .totalCount((long) data.size())
                .totalPages(totalPages)
                .data(pageData)
                .build();
    }
} 