/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Geographic region sentiment analysis data transfer object
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GeoSentimentDTO {
    /**
     * Geographic region name
     */
    private String location;
    
    /**
     * Location identifier (used for mapping to geographic boundaries)
     */
    private String locPid;
    
    /**
     * Topic category (living cost, traffic accident, employment rate, crime rate)
     */
    private String topicCategory;
    
    /**
     * Sentiment score (between -1 and 1)
     */
    private Float sentimentScore;
    
    /**
     * Discussion volume/post count
     */
    private Long postCount;
    
    /**
     * Positive sentiment posts ratio
     */
    private Float positiveRatio;
    
    /**
     * Negative sentiment posts ratio
     */
    private Float negativeRatio;
    
    /**
     * Neutral sentiment posts ratio
     */
    private Float neutralRatio;
} 