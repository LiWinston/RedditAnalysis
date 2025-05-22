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
 * Time series sentiment analysis data transfer object
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TimeSentimentDTO {
    /**
     * Time point (usually month format: YYYY-MM)
     */
    private String timePoint;
    
    /**
     * Topic category
     */
    private String topicCategory;
    
    /**
     * Average sentiment score
     */
    private Float averageSentiment;
    
    /**
     * Discussion volume/post count
     */
    private Long postCount;
} 