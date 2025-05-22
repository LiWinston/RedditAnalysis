/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.config;

import co.elastic.clients.elasticsearch._types.mapping.DenseVectorSimilarity;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.bgesmallen.BgeSmallEnEmbeddingModel;
import dev.langchain4j.model.embedding.onnx.bgesmallenq.BgeSmallEnQuantizedEmbeddingModel;
import dev.langchain4j.model.embedding.onnx.bgesmallenv15.BgeSmallEnV15EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.elasticsearch.ElasticsearchEmbeddingStore;
import dev.langchain4j.store.embedding.elasticsearch.ElasticsearchConfigurationKnn;
// import dev.langchain4j.store.embedding.elasticsearch.ElasticsearchStoreConfig; // 可能不存在，暂时注释
import org.elasticsearch.client.RestClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import co.elastic.clients.elasticsearch.ElasticsearchClient;

import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

/**
 * LangChain4j嵌入和嵌入存储配置类
 */
@Configuration
public class LangChainEmbeddingConfig {

    private static final Logger log = LoggerFactory.getLogger(LangChainEmbeddingConfig.class);

    // ElasticSearch 配置
    @Value("${elasticsearch.index-name:all_content_processed_vectorized_v3}")
    private String indexName;

    // 嵌入模型配置
    @Value("${langchain.embedding.use-parallel:true}")
    private boolean useParallel;

    @Value("${langchain.embedding.thread-count:4}")
    private int threadCount;

    @Value("${langchain.embedding.dimensions:384}")
    private int dimensions;

    @Value("${langchain.embedding.vector-field:vector_}")
    private String vectorField;

    /**
     * 创建并发执行器，用于并行处理嵌入生成
     */
    @Bean
    public Executor embeddingExecutor() {
        if (useParallel) {
            return Executors.newFixedThreadPool(threadCount);
        } else {
            return Executors.newSingleThreadExecutor();
        }
    }

    /**
     * 创建文档编码器 - 用于处理文档内容
     * 使用BGE小型模型标准版(非量化版)
     */
    @Bean(name = "documentEmbeddingModel")
    @Primary
    public EmbeddingModel documentEmbeddingModel(Executor embeddingExecutor) {
        log.info("初始化文档编码器 BGE Small EN V1.5");
        return new BgeSmallEnV15EmbeddingModel(embeddingExecutor);
    }
    
    /**
     * 创建查询编码器 - 用于处理用户查询
     * 使用BGE小型模型查询优化版(-q)
     */
    @Bean(name = "queryEmbeddingModel")
    public EmbeddingModel queryEmbeddingModel(Executor embeddingExecutor) {
        log.info("初始化查询编码器 BGE Small EN V1.5");
        return new BgeSmallEnV15EmbeddingModel(embeddingExecutor); // BgeSmallEnQuantizedEmbeddingModel
    }

    /**
     * 创建ElasticSearch嵌入存储
     * 使用ElasticsearchConfigurationKnn利用ES 9.0.1原生KNN支持
     */
    @Bean
    @Primary
    public EmbeddingStore<TextSegment> embeddingStore(RestClient restClient) {
        // 创建嵌入存储
        ElasticsearchEmbeddingStore store = ElasticsearchEmbeddingStore.builder()
                .restClient(restClient)
                .indexName(indexName) // 确保索引名称正确
                .configuration(ElasticsearchConfigurationKnn.builder().build())
                .build();
        
        log.info("已配置ElasticsearchEmbeddingStore，索引名: {}", indexName);
        
        return store;
    }
    
    /**
     * 在应用启动后创建向量索引
     */
    /*
    @Bean
    public CommandLineRunner createEmbeddingIndex(ElasticsearchClient esClient) {
        return args -> {
            try {
                // 检查索引是否存在
                boolean indexExists = esClient.indices().exists(b -> b.index(indexName)).value();
                
                if (!indexExists) {
                    log.info("创建向量索引: {}", indexName);
                    // 创建索引
                    esClient.indices().create(c -> c
                        .index(indexName)
                        .mappings(m -> m
                            .properties("embedding", p -> p
                                .denseVector(v -> v
                                    .dims(384)
                                    .similarity(DenseVectorSimilarity.Cosine)
                                    .index(true)
                                )
                            )
                        )
                    );
                    log.info("向量索引创建成功: {}", indexName);
                } else {
                    log.info("向量索引已存在: {}", indexName);
                }
            } catch (Exception e) {
                log.error("创建向量索引失败: {}", e.getMessage(), e);
            }
        };
    }
    */
} 