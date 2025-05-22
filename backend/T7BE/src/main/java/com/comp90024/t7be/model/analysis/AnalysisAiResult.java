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
 * AI分析结果DTO，仅包含需要AI生成的字段
 * 其他字段(如locPid、location、topic、sentimentScore等)将从其他来源获取后合并到最终的AnalysisCard中
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AnalysisAiResult {
    
    /**
     * 总体情感标签 (Positive/Neutral/Negative)
     */
    @JsonProperty("sentimentLabel")
    @Description("Overall sentiment label")
    private String sentimentLabel;
    
    /**
     * 热点话题/核心问题列表
     */
    @JsonProperty("topicPoints")
    @Description("List of hot topics/core issues")
    private List<AnalysisCard.TopicPoint> topicPoints;
    
    /**
     * 代表性观点列表
     */
    @JsonProperty("representativeViews")
    @Description("List of representative viewpoints")
    private List<String> representativeViews;
} 