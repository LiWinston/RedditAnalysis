/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.service.ai.impl;

import com.comp90024.t7be.model.analysis.AnalysisAiResult;
import com.comp90024.t7be.service.ai.HyperAnalysisAiService;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.service.AiServices;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * Implementation class for the HyperAnalysisAiService interface.
 * Uses the Gemini model for analysis.
 */
@Service
public class HyperAnalysisAiServiceImpl {

    private final HyperAnalysisAiService hyperAnalysisAiService;

    // Alternative: googleAiGeminiChatModelWithJsonSchema
    public HyperAnalysisAiServiceImpl(@Qualifier("HyperAnalysisGeminiChatModel") ChatLanguageModel chatLanguageModel) {
        // Create service instance using AiServices tool and Gemini model
        this.hyperAnalysisAiService = AiServices.builder(HyperAnalysisAiService.class)
                .chatLanguageModel(chatLanguageModel)
                .build();
    }

    /**
     * Delegates the call to the interface method to analyze local hot topics.
     */
    public AnalysisAiResult analyzeLocalHotTopics(List<String> comments) {
        return hyperAnalysisAiService.analyzeLocalHotTopics(comments);
    }

    /**
     * Delegates the call to the interface method to analyze discussions on a specific topic.
     */
    public AnalysisAiResult analyzeTopicDiscussion(String topic, List<String> comments) {
        return hyperAnalysisAiService.analyzeTopicDiscussion(topic, comments);
    }
    
    /**
     * Delegates the call to the interface method to answer user queries based on retrieved content.
     */
    public AnalysisAiResult queryInsights(String query, List<String> retrievedContents) {
        return hyperAnalysisAiService.queryInsights(query, retrievedContents);
    }
} 