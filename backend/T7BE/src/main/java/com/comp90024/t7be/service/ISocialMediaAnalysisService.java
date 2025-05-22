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

import java.util.List;
import java.util.Map;

/**
 * Social media analysis service interface
 */
public interface ISocialMediaAnalysisService {

    /**
     * Get original post data (paginated)
     * @param location geographic location
     * @param page page number
     * @param size items per page
     * @return paginated post data
     */
    PageResponseDTO<RedditComment> getCommentsByLocation(String location, int page, int size);
    
    /**
     * Get original post data (paginated)
     * @param state state/province
     * @param page page number
     * @param size items per page
     * @return paginated post data
     */
    PageResponseDTO<RedditComment> getCommentsByState(String state, int page, int size);
    
    /**
     * Get posts with specific emotion type (paginated)
     * @param emotionType emotion type
     * @param page page number
     * @param size items per page
     * @return paginated post data
     */
    PageResponseDTO<RedditComment> getCommentsByEmotionType(String emotionType, int page, int size);
    
    /**
     * Get sentiment analysis data for geographic regions
     * @param state state/province
     * @param category topic category (can be null for all topics)
     * @return list of geographic region sentiment analysis data
     */
    List<GeoSentimentDTO> getGeoSentimentAnalysis(String state, TopicCategory category);
    
    /**
     * Get topic sentiment analysis data (pie chart data)
     * @param state state/province
     * @return list of topic sentiment analysis data
     */
    List<TopicSentimentDTO> getTopicSentimentDistribution(String state);
    
    /**
     * Get average sentiment scores for multiple topics (radar chart data)
     * @param state state/province
     * @return mapping from topic to average sentiment score
     */
    Map<TopicCategory, Float> getTopicAverageSentiment(String state);
    
    /**
     * Get time series sentiment analysis data (line chart data)
     * @param state state/province
     * @param category topic category
     * @param monthCount number of months
     * @return list of time series sentiment analysis data
     */
    List<TimeSentimentDTO> getTimeSentimentTrend(String state, TopicCategory category, int monthCount);
    
    /**
     * Get topic correlation analysis data (heatmap data)
     * @param state state/province
     * @return list of topic correlation analysis data
     */
    List<CorrelationDTO> getTopicCorrelationAnalysis(String state);
} 