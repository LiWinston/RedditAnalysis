/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.config;

import dev.langchain4j.data.document.DocumentSplitter;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.rag.content.Content;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.store.embedding.EmbeddingStore;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * LangChain4j RAG (检索增强生成) 配置
 */
@Configuration
@Slf4j
public class LangChainRagConfig {

    @Value("${langchain.rag.max-results:5}")
    private int maxResults;

    @Value("${langchain.rag.min-score:0.3}")
    private double minScore;

    /**
     * 文档分割器 - 将大文档分割成适合嵌入的文本段
     */
    @Bean
    public DocumentSplitter documentSplitter() {
        return DocumentSplitters.recursive(500, 0);
    }
    
    /**
     * 创建基于嵌入存储的内容检索器
     */
    @Bean
    @Qualifier("embeddingStoreContentRetriever")
    public ContentRetriever embeddingStoreContentRetriever(
            EmbeddingStore<TextSegment> embeddingStore,
            EmbeddingModel embeddingModel) {
        
        log.info("正在配置EmbeddingStoreContentRetriever，最大结果数: {}, 最小相似度分数: {}", 
                maxResults, minScore);
        
        return EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .maxResults(maxResults)
                .minScore(minScore)
                .build();
    }
} 