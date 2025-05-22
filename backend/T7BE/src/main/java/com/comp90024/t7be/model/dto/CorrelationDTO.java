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
 * Topic correlation analysis data transfer object
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CorrelationDTO {
    /**
     * First topic category
     */
    private String topicA;
    
    /**
     * Second topic category
     */
    private String topicB;
    
    /**
     * Correlation coefficient (between -1 and 1)
     */
    private Float correlationCoefficient;
} 