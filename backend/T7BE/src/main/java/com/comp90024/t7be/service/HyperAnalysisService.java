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
import com.comp90024.t7be.model.analysis.AnalysisAiResult;
import com.comp90024.t7be.model.analysis.AnalysisCard;
import com.comp90024.t7be.model.enums.TopicCategory;
import com.comp90024.t7be.service.ai.impl.HyperAnalysisAiServiceImpl;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.model.embedding.EmbeddingModel;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.context.ApplicationContext;
import org.springframework.beans.factory.annotation.Qualifier;

import java.util.List;
import java.util.OptionalDouble;
import java.util.stream.Collectors;
import java.util.ArrayList;

/**
 * Advanced analysis service class.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class HyperAnalysisService {

    private final ElasticsearchService elasticsearchService;
    private final HyperAnalysisAiServiceImpl hyperAnalysisAiService;
    private final ApplicationContext applicationContext;
    
    @Qualifier("queryEmbeddingModel")
    private final EmbeddingModel embeddingModel;
    
    /**
     * Analyzes hot topics in a region.
     *
     * @param locPid Region ID
     * @param limit Number of latest comments, default is 10
     * @return Analysis result
     */
    public AnalysisCard analyzeLocalHotTopics(String locPid, int limit) {
        // Get the latest comments for the specified region from ES
        List<RedditComment> comments = elasticsearchService.getRecentCommentsByLocPid(locPid, limit);
        
        if (comments.isEmpty()) {
            return AnalysisCard.builder()
                    .locPid(locPid)
                    .location("Unknown")
                    .sentimentLabel("Neutral")
                    .sentimentScore(0.0)
                    .topicPoints(List.of())
                    .representativeViews(List.of("No comments found for this location."))
                    .build();
        }
        
        // Extract region name and comment texts
        String location = comments.get(0).getFirstLocation(); // Assuming comments from the same locPid have the same location
        List<String> commentTexts = extractCommentTexts(comments);
        
        // Calculate average sentiment score
        Double avgSentimentScore = calculateAverageSentimentScore(comments);
        
        // Analyze comments using AI service
        AnalysisAiResult aiResult = hyperAnalysisAiService.analyzeLocalHotTopics(commentTexts);
        
        // Merge data and build the complete AnalysisCard
        return AnalysisCard.builder()
                .locPid(locPid)
                .location(location)
                .sentimentScore(avgSentimentScore)
                .sentimentLabel(aiResult.getSentimentLabel())
                .topicPoints(aiResult.getTopicPoints())
                .representativeViews(aiResult.getRepresentativeViews())
                .build();
    }
    
    /**
     * Analyzes discussions on a specific topic.
     *
     * @param locPid Region ID
     * @param topicCategory Topic category
     * @param limit Number of latest comments, default is 10
     * @return Analysis result
     */
    public AnalysisCard analyzeTopicDiscussion(String locPid, TopicCategory topicCategory, int limit) {
        // Get the latest comments for the specified region and topic from ES
        List<RedditComment> comments = elasticsearchService.getCommentsByLocPidAndTopic(locPid, topicCategory, limit);
        
        if (comments.isEmpty()) {
            return AnalysisCard.builder()
                    .locPid(locPid)
                    .location("Unknown")
                    .topic(topicCategory.getDisplayName())
                    .sentimentLabel("Neutral")
                    .sentimentScore(0.0)
                    .topicPoints(List.of())
                    .representativeViews(List.of("No comments found for this location and topic."))
                    .build();
        }
        
        // Extract region name, topic name, and comment texts
        String location = comments.get(0).getFirstLocation(); // Assuming comments from the same locPid have the same location
        String topic = topicCategory.getDisplayName();
        List<String> commentTexts = extractCommentTexts(comments);
        
        // Calculate average sentiment score
        Double avgSentimentScore = calculateAverageSentimentScore(comments);
        
        // Analyze comments using AI service
        AnalysisAiResult aiResult = hyperAnalysisAiService.analyzeTopicDiscussion(topic, commentTexts);
        
        // Merge data and build the complete AnalysisCard
        return AnalysisCard.builder()
                .locPid(locPid)
                .location(location)
                .topic(topic)
                .sentimentScore(avgSentimentScore)
                .sentimentLabel(aiResult.getSentimentLabel())
                .topicPoints(aiResult.getTopicPoints())
                .representativeViews(aiResult.getRepresentativeViews())
                .build();
    }
    
    /**
     * Processes natural language queries using RAG technology.
     * 
     * @param queryText User query text
     * @param locPid Optional region PID filter
     * @param state Optional state/territory filter
     * @param location Optional location name filter 
     * @param topics Optional topic filter (comma-separated multiple topics)
     * @param limit Result count limit
     * @return Analysis result card
     */
    public AnalysisCard queryInsightsWithRag(String queryText, String locPid, String state, String location, String topics, int limit) {
        log.info("Starting to process natural language query: {}, Region PID: {}, State/Territory: {}, Location: {}, Topics: {}, Limit: {}", 
                queryText, locPid, state, location, topics, limit);
        
        // Generate embedding vector for the query
        List<Float> queryEmbedding = generateQueryEmbedding(queryText);
        
        if (queryEmbedding.isEmpty()) {
            log.error("Failed to generate embedding vector for the query");
            return createEmptyResult(queryText);
        }
        
        // Find relevant comments using vector search, with added geographic and topic constraints
        List<RedditComment> relevantComments = elasticsearchService.findSimilarCommentsByEmbedding(
                queryEmbedding, 0.3, limit, locPid, state, location, topics);
        log.info("Found {} relevant comments via embedding vector", relevantComments.size());
        
        if (relevantComments.isEmpty()) {
            return createEmptyResult(queryText);
        }
        
        // Extract comment texts
        List<String> commentTexts = extractCommentTexts(relevantComments);
        
        // Analyze retrieved content and answer the query using AI service
        AnalysisAiResult aiResult = hyperAnalysisAiService.queryInsights(queryText, commentTexts);
        log.info("AI analysis completed, generating result");
        
        // Build result card
        AnalysisCard result = AnalysisCard.builder()
                .query(queryText)
                .sentimentLabel(aiResult.getSentimentLabel())
                .sentimentScore(calculateAverageSentimentScore(relevantComments))
                .topicPoints(aiResult.getTopicPoints())
                .representativeViews(aiResult.getRepresentativeViews())
                .build();
                
        // If region information is available, add it to the result
        if (locPid != null && !locPid.isBlank()) {
            result.setLocPid(locPid);
            // Try to get region name
            String locationName = relevantComments.stream()
                .filter(c -> c.getLocPid() != null && !c.getLocPid().isEmpty() && locPid.equals(c.getFirstLocPid()))
                .findFirst()
                .map(RedditComment::getFirstLocation)
                .orElse("Unknown");
            result.setLocation(locationName);
        } else if (location != null && !location.isBlank()) {
            // If location name constraint exists, use it directly
            result.setLocation(location);
        } else if (state != null && !state.isBlank()) {
            // If state/territory constraint exists, set it as state/territory name
            result.setState(state);
        }
        
        return result;
    }
    
    /**
     * Backward compatibility method, internally calls the new implementation.
     */
    public AnalysisCard queryInsightsWithRag(String queryText, String locPid, int limit) {
        return queryInsightsWithRag(queryText, locPid, null, null, null, limit);
    }
    
    /**
     * Generates query embedding vector from text.
     * 
     * @param text Query text
     * @return List of floats representing the embedding vector
     */
    private List<Float> generateQueryEmbedding(String text) {
        try {
            if (text == null || text.trim().isEmpty()) {
                log.warn("Query text is empty, cannot generate embedding");
                return List.of();
            }
            
            // Generate text embedding using LangChain4j's EmbeddingModel
            Embedding embedding = embeddingModel.embed(text).content();
            List<Float> vectorValues = embedding.vectorAsList();
            
            log.info("Successfully generated embedding vector for text, dimension: {}", vectorValues.size());
            return vectorValues;
        } catch (Exception e) {
            log.error("Error generating text embedding: {}", e.getMessage(), e);
            return List.of();
        }
    }
    
    /**
     * Creates an empty result.
     */
    private AnalysisCard createEmptyResult(String queryText) {
        return AnalysisCard.builder()
                .query(queryText)
                .sentimentLabel("Neutral")
                .sentimentScore(0.0)
                .topicPoints(List.of())
                .representativeViews(List.of("No relevant content found for this query."))
                .build();
    }
    
    /**
     * Extracts text content from a list of comment objects.
     */
    private List<String> extractCommentTexts(List<RedditComment> comments) {
        return comments.stream()
                .map(comment -> {
                    List<String> texts = comment.getText();
                    return texts != null && !texts.isEmpty() ? texts.get(0) : "";
                })
                .filter(text -> !text.isEmpty())
                .collect(Collectors.toList());
    }
    
    /**
     * Calculates average sentiment score from a list of comment objects.
     */
    private Double calculateAverageSentimentScore(List<RedditComment> comments) {
        OptionalDouble avg = comments.stream()
                .map(RedditComment::getFirstSentimentScore)
                .filter(score -> score != null)
                .mapToDouble(Float::doubleValue)
                .average();
                
        return avg.isPresent() ? avg.getAsDouble() : 0.0;
    }
} 