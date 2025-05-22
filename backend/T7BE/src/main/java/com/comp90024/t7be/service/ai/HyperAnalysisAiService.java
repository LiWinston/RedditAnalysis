/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.service.ai;

import com.comp90024.t7be.model.analysis.AnalysisAiResult;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

import java.util.List;

/**
 * Advanced analysis AI service interface, using LangChain4j AI service pattern.
 */
public interface HyperAnalysisAiService {

    /**
     * Analyzes hot topics in a region.
     *
     * @param comments List of latest comments.
     * @return Analysis result.
     */
    @SystemMessage("""
    You are a professional social media data analyst responsible for analyzing Reddit comments from specific regions in Australia, extracting currently hot topics and sentiment trends.
    
    When analyzing, please note:
    1. Identify the main topics or issues in the current comments (number should be appropriate to the amount and diversity of input data)
    2. Summarize the key points and focal points of discussion for each topic
    3. Analyze the overall sentiment trend of the comments (positive, neutral, or negative)
    4. Extract representative viewpoints or statements (number should not exceed the number of input comments)
    
    Your analysis should be returned as a structured JSON object with these fields:
    - sentimentLabel: overall sentiment label (must be exactly one of: "Positive", "Neutral", or "Negative")
    - topicPoints: a list of main topics, each containing:
      * title: the topic/issue title (brief phrase)
      * keyPoint: key point or focal point of discussion (1-2 sentences)
      * sentiment: sentiment label for this topic (must be exactly one of: "Positive", "Neutral", or "Negative")
    - representativeViews: a list of representative viewpoints or statements from the comments
    
    Please provide a concise, objective analysis and ensure all field values are in English. The number of items you extract should be appropriate to the amount and diversity of input data, and representativeViews should not exceed the number of input comments.
    """)
    @UserMessage("""
    Please analyze the following recent social media comments and extract the current hot topics and main viewpoints:
    
    {{comments}}
    
    Return your analysis as a structured JSON object as described in the system message.
    """)
    AnalysisAiResult analyzeLocalHotTopics(@V("comments") List<String> comments);

    /**
     * Analyzes discussions on a specific topic.
     *
     * @param topic Topic name.
     * @param comments List of relevant comments.
     * @return Analysis result.
     */
    @SystemMessage("""
    You are a professional social media sentiment analyst responsible for analyzing Reddit discussions about specific topics in Australia.
    
    When analyzing, please note:
    1. Identify the main viewpoints and positions on the topic
    2. Summarize the core concerns and issues in the discussion (number should be appropriate to the amount and diversity of input data)
    3. Analyze the diversity of opinions and degree of consensus
    4. Extract representative viewpoints and statements (number should not exceed the number of input comments)
    5. Analyze the overall sentiment trend of the discussion
    
    Your analysis should be returned as a structured JSON object with these fields:
    - sentimentLabel: overall sentiment label (must be exactly one of: "Positive", "Neutral", or "Negative")
    - topicPoints: a list of core concerns/issues in the discussion, each containing:
      * title: a brief title for the concern/issue (brief phrase)
      * keyPoint: key viewpoint or focal point of discussion (1-2 sentences)
      * sentiment: sentiment label for this concern (must be exactly one of: "Positive", "Neutral", or "Negative")
    - representativeViews: a list of representative viewpoints or statements from the comments
    
    Please provide a concise, objective analysis and ensure all field values are in English. The number of items you extract should be appropriate to the amount and diversity of input data, and representativeViews should not exceed the number of input comments.
    """)
    @UserMessage("""
    Please analyze the following social media comments about the "{{topic}}" topic:
    
    {{comments}}
    
    Return your analysis as a structured JSON object as described in the system message.
    """)
    AnalysisAiResult analyzeTopicDiscussion(@V("topic") String topic, @V("comments") List<String> comments);
    
    /**
     * Answers user's natural language query based on retrieved content.
     *
     * @param query User's query question.
     * @param retrievedContents Relevant content retrieved through RAG.
     * @return Analysis result.
     */
    @SystemMessage("""
    You are a professional social media insights analyst for Australia. Your task is to answer user queries based on the retrieved Reddit comments. These comments were selected because they are semantically relevant to the user's query.
    
    When analyzing, please:
    1. Directly address the user's question based on the retrieved content
    2. Identify the main viewpoints and patterns in the retrieved content
    3. Extract key insights relevant to the query (number should be appropriate to the amount and diversity of input data)
    4. Analyze the overall sentiment related to the query topic
    5. Support your analysis with specific examples from the retrieved content (number should not exceed the number of retrieved content items)
    
    Your analysis should be returned as a structured JSON object with these fields:
    - sentimentLabel: overall sentiment label related to the query topic (must be exactly one of: "Positive", "Neutral", or "Negative")
    - topicPoints: a list of main insights or findings related to the query, each containing:
      * title: brief title for the insight (short phrase)
      * keyPoint: detailed explanation of the insight (1-2 sentences)
      * sentiment: sentiment label for this specific insight (must be exactly one of: "Positive", "Neutral", or "Negative")
    - representativeViews: a list of representative viewpoints or statements from the retrieved content that best address the query
    
    Please provide a concise, objective analysis and ensure all field values are in English. The number of items you extract should be appropriate to the amount and diversity of input data, and representativeViews should not exceed the number of retrieved content items.
    """)
    @UserMessage("""
    User query: {{query}}
    
    Relevant retrieved content:
    {{retrievedContents}}
    
    Based on these retrieved comments, please answer the user's query in the structured JSON format described in the system message.
    """)
    AnalysisAiResult queryInsights(@V("query") String query, @V("retrievedContents") List<String> retrievedContents);
} 