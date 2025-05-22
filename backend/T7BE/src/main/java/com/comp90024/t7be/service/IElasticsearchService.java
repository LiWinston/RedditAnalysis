package com.comp90024.t7be.service;

import com.comp90024.t7be.model.RedditComment;
import com.comp90024.t7be.model.dto.GeoSentimentDTO;
import com.comp90024.t7be.model.dto.TimeSentimentDTO;
import com.comp90024.t7be.model.dto.TopicSentimentDTO;
import com.comp90024.t7be.model.enums.TopicCategory;

import java.util.List;
import java.util.Map;

/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */

/**
 * Elasticsearch service interface.
 */
public interface IElasticsearchService {

    /**
     * Searches comments by location.
     * @param location Location identifier.
     * @return List of comments.
     */
    List<RedditComment> searchByLocation(String location);
    
    /**
     * Searches comments by state.
     * @param state State identifier.
     * @return List of comments.
     */
    List<RedditComment> searchByState(String state);
    
    /**
     * Searches comments by emotion type.
     * @param emotionType Emotion type identifier.
     * @return List of comments.
     */
    List<RedditComment> searchByEmotionType(String emotionType);
    
    /**
     * Searches comments by topic category.
     * @param category Topic category.
     * @return List of comments.
     */
    List<RedditComment> searchByTopicCategory(TopicCategory category);
    
    /**
     * Searches comments by time range and topic category.
     * @param startDate Start date.
     * @param endDate End date.
     * @param category Topic category.
     * @return List of comments.
     */
    List<RedditComment> searchByTimeRangeAndTopic(String startDate, String endDate, TopicCategory category);
    
    /**
     * Searches comments by location and topic category.
     * @param location Location.
     * @param category Topic category.
     * @return List of comments.
     */
    List<RedditComment> searchByLocationAndTopic(String location, TopicCategory category);
    
    /**
     * Searches comments by state and topic category.
     * @param state State.
     * @param category Topic category.
     * @return List of comments.
     */
    List<RedditComment> searchByStateAndTopic(String state, TopicCategory category);
    
    /**
     * Gets the latest comments for a specified region.
     * @param locPid Region ID.
     * @param limit Number of comments to return.
     * @return List of comments.
     */
    List<RedditComment> getRecentCommentsByLocPid(String locPid, int limit);
    
    /**
     * Gets comments for a specified region and topic.
     * @param locPid Region ID.
     * @param category Topic category.
     * @param limit Number of comments to return.
     * @return List of comments.
     */
    List<RedditComment> getCommentsByLocPidAndTopic(String locPid, TopicCategory category, int limit);
    
    /**
     * Gets geographic region sentiment analysis using ES aggregation.
     * @param state State name.
     * @param category Topic category (can be null, meaning all topics).
     * @return List of sentiment statistics grouped by region.
     */
    List<GeoSentimentDTO> getGeoSentimentAggregation(String state, TopicCategory category);
    
    /**
     * Gets topic sentiment distribution using ES aggregation.
     * @param state State name.
     * @return List of sentiment statistics for each topic.
     */
    List<TopicSentimentDTO> getTopicSentimentAggregation(String state);
    
    /**
     * Gets time sentiment trend using ES aggregation.
     * @param state State name.
     * @param category Topic category.
     * @param startDate Start date.
     * @param endDate End date.
     * @return List of sentiment statistics grouped by time point.
     */
    List<TimeSentimentDTO> getTimeSentimentAggregation(String state, TopicCategory category, String startDate, String endDate);
    
    /**
     * Gets average sentiment scores for all topics using ES aggregation.
     * @param state State name.
     * @return Average sentiment scores for each topic.
     */
    Map<TopicCategory, Float> getTopicAverageSentimentAggregation(String state);
} 