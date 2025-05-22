/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.model.analysis;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import dev.langchain4j.model.output.structured.Description;
import java.util.List;

/**
 * 分析卡片实体类，用于前端展示
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AnalysisCard {
    
    /**
     * 地区ID
     */
    @JsonProperty("locPid")
    private String locPid;
    
    /**
     * 地区名称
     */
    @JsonProperty("location")
    private String location;
    
    /**
     * 主题 (可选，只在topic-discussion接口中返回)
     */
    @JsonProperty("topic")
    private String topic;
    
    /**
     * 用户查询 (可选，只在query-insights接口中返回)
     */
    @JsonProperty("query")
    private String query;
    
    /**
     * 总体情感分数 (-1.0 至 1.0)
     * -1.0 表示极度负面
     * 0.0 表示中性
     * 1.0 表示极度正面
     */
    @JsonProperty("sentimentScore")
    private Double sentimentScore;
    
    /**
     * 总体情感标签 (Positive/Neutral/Negative)
     */
    @JsonProperty("sentimentLabel")
    private String sentimentLabel;
    
    /**
     * 热点话题/核心问题列表
     */
    @JsonProperty("topicPoints")
    private List<TopicPoint> topicPoints;
    
    /**
     * 代表性观点列表
     */
    @JsonProperty("representativeViews")
    private List<String> representativeViews;
    
    /**
     * 添加州/领地字段
     */
    private String state;
    
    /**
     * 热点话题/核心问题
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class TopicPoint {
        /**
         * 话题/问题标题
         */
        @JsonProperty("title")
        @Description("Title of the topic/issue")
        private String title;
        
        /**
         * 关键观点/讨论焦点
         */
        @JsonProperty("keyPoint")
        @Description("Key point or focal point of discussion")
        private String keyPoint;
        
        /**
         * 情感标签 (Positive/Neutral/Negative)
         */
        @JsonProperty("sentiment")
        @Description("Sentiment label for this topic")
        private String sentiment;
    }
} 