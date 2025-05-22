/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.config;

import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.chat.request.ResponseFormat;
import dev.langchain4j.model.googleai.GoogleAiGeminiChatModel;
import dev.langchain4j.model.mistralai.MistralAiChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.beans.factory.annotation.Qualifier;

import java.time.Duration;
import java.util.Set;

import static dev.langchain4j.model.chat.Capability.RESPONSE_FORMAT_JSON_SCHEMA;
import static dev.langchain4j.model.chat.request.ResponseFormatType.JSON;

/**
 * LangChain4j配置类
 * 用于配置各种AI模型和嵌入存储
 */
@Configuration
public class LangChainConfig {

    // Mistral AI配置
    @Value("${langchain.ai.mistral.api-key: }")
    private String mistralApiKey;
    
    @Value("${langchain.ai.mistral.model:mistral-small-latest}")
    private String mistralModel;
    
    @Value("${langchain.ai.mistral.enabled:true}")
    private boolean mistralEnabled;
    
    // OpenAI配置
    @Value("${langchain.ai.openai.api-key:}")
    private String openaiApiKey;
    
    @Value("${langchain.ai.openai.model:gpt-3.5-turbo}")
    private String openaiModel;
    
    @Value("${langchain.ai.openai.api-url:https://api.openai.com}")
    private String openaiApiUrl;
    
    @Value("${langchain.ai.openai.enabled:false}")
    private boolean openaiEnabled;

    // Google Gemini 配置
    @Value("${langchain.ai.gemini.api-key:}")
    private String geminiApiKey;

    @Value("${langchain.ai.gemini.model:gemini-2.0-flash}")
    private String geminiModel;

    @Value("${langchain.ai.gemini.enabled:true}")
    private boolean geminiEnabled;
    
    // SiliconFlow配置（OpenAI兼容接口）
    @Value("${langchain.ai.siliconflow.api-key:}")
    private String siliconFlowApiKey;
    
    @Value("${langchain.ai.siliconflow.model:glm-4}")
    private String siliconFlowModel;
    
    @Value("${langchain.ai.siliconflow.api-url:https://api.siliconflow.cn/v1}")
    private String siliconFlowApiUrl;
    
    @Value("${langchain.ai.siliconflow.enabled:true}")
    private boolean siliconFlowEnabled;

    /**
     * 提供默认的ChatLanguageModel，用于非结构化文本输出
     * 优先顺序: SiliconFlow -> Google Gemini -> Mistral AI -> OpenAI
     */
    @Bean
    @Primary
    @Qualifier("defaultChatLanguageModel")
    public ChatLanguageModel defaultChatLanguageModel() {
        if (siliconFlowEnabled && !siliconFlowApiKey.isEmpty()) {
            return createSiliconFlowChatModel();
        } else if (geminiEnabled && !geminiApiKey.isEmpty()) {
            return createGoogleAiGeminiChatModel(false);
        } else if (mistralEnabled && !mistralApiKey.isEmpty()) {
            return createMistralAiChatModel(false);
        } else if (openaiEnabled && !openaiApiKey.isEmpty()) {
            return createOpenAiChatModel(false);
        }
        
        // 默认回退: 尝试SiliconFlow
        return createSiliconFlowChatModel();
    }

    /**
     * 创建支持JSON Schema的Mistral AI模型实例
     */
    @Bean
    @Qualifier("mistralAiChatModelWithJsonSchema")
    public MistralAiChatModel mistralAiChatModelWithJsonSchema() {
        return createMistralAiChatModel(true);
    }
    
    /**
     * 创建普通的Mistral AI模型实例
     */
    @Bean
    @Qualifier("mistralAiChatModel")
    public MistralAiChatModel mistralAiChatModel() {
        return createMistralAiChatModel(false);
    }
    
    /**
     * 创建Mistral AI模型工厂方法
     */
    private MistralAiChatModel createMistralAiChatModel(boolean withJsonSchema) {
        var builder = MistralAiChatModel.builder()
                .apiKey(mistralApiKey)
                .modelName(mistralModel)
                .timeout(Duration.ofSeconds(90))
                .logRequests(true)
                .logResponses(true);
                
        if (withJsonSchema) {
            builder.responseFormat(ResponseFormat.JSON)
                   .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA);
        }
        
        return builder.build();
    }

    /**
     * 创建支持JSON Schema的Google AI Gemini模型实例
     */
    @Bean
    @Qualifier("googleAiGeminiChatModelWithJsonSchema")
    public GoogleAiGeminiChatModel googleAiGeminiChatModelWithJsonSchema() {
        return createGoogleAiGeminiChatModel(true);
    }
    
    /**
     * 创建普通的Google AI Gemini模型实例
     */
    @Bean
    @Qualifier("googleAiGeminiChatModel")
    public GoogleAiGeminiChatModel googleAiGeminiChatModel() {
        return createGoogleAiGeminiChatModel(false);
    }
    
    /**
     * 创建Google AI Gemini模型工厂方法
     */
    private GoogleAiGeminiChatModel createGoogleAiGeminiChatModel(boolean withJsonSchema) {
        var builder = GoogleAiGeminiChatModel.builder()
                .apiKey(geminiApiKey)
                .modelName(geminiModel)
                .logRequestsAndResponses(true);
                
        if (withJsonSchema) {
            builder.responseFormat(ResponseFormat.builder().type(JSON).build());
        }
        
        return builder.build();
    }
    
    /**
     * 创建支持JSON Schema的OpenAI模型实例
     */
    @Bean
    @Qualifier("openAiChatModelWithJsonSchema")
    public OpenAiChatModel openAiChatModelWithJsonSchema() {
        return createOpenAiChatModel(true);
    }
    
    /**
     * 创建普通的OpenAI模型实例
     */
    @Bean
    @Qualifier("openAiChatModel")
    public OpenAiChatModel openAiChatModel() {
        return createOpenAiChatModel(false);
    }
    
    /**
     * 创建OpenAI模型工厂方法
     */
    private OpenAiChatModel createOpenAiChatModel(boolean withJsonSchema) {
        var builder = OpenAiChatModel.builder()
                .apiKey(openaiApiKey)
                .modelName(openaiModel)
                .baseUrl(openaiApiUrl)
                .logRequests(true)
                .logResponses(true);
                
        if (withJsonSchema) {
            builder.supportedCapabilities(Set.of(RESPONSE_FORMAT_JSON_SCHEMA))
                   .strictJsonSchema(true);
        }
        
        return builder.build();
    }
    
    /**
     * 创建SiliconFlow模型实例（使用OpenAI兼容接口）
     */
    @Bean
    @Qualifier("siliconFlowChatModel")
    public OpenAiChatModel createSiliconFlowChatModel() {
        return OpenAiChatModel.builder()
                .apiKey(siliconFlowApiKey)
                .modelName(siliconFlowModel)
                .baseUrl(siliconFlowApiUrl)
                .logRequests(true)
                .logResponses(true)
                .build();
    }

    /**
     * 创建Gemini HyperAnalysisGeminiChatModel特化模型，专门用于结构化JSON输出
     * 这是我们高级分析服务使用的模型
     */
    @Bean
    @Qualifier("HyperAnalysisGeminiChatModel")
    public ChatLanguageModel geminiChatModel() {
        return GoogleAiGeminiChatModel.builder()
                .apiKey(geminiApiKey)
                .modelName(geminiModel) 
                .temperature(0.2) // 降低温度以获得更确定性的输出
                .topP(0.9) 
                .responseFormat(ResponseFormat.builder().type(JSON).build()) // 启用JSON响应
                .maxOutputTokens(10240) // 设置足够的输出令牌以容纳完整分析
                .logRequestsAndResponses(true)
                .build();
    }
} 