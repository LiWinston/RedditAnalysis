/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.config;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.json.jackson.JacksonJsonpMapper;
import co.elastic.clients.transport.ElasticsearchTransport;
import co.elastic.clients.transport.rest_client.RestClientTransport;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.apache.http.HttpHost;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.nio.client.HttpAsyncClientBuilder;
import org.apache.http.ssl.SSLContexts;
import org.elasticsearch.client.RestClient;
import org.elasticsearch.client.RestClientBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

import javax.net.ssl.SSLContext;
import java.security.KeyManagementException;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;

@Configuration
@RequiredArgsConstructor
public class ElasticsearchConfig {

    @Value("${elasticsearch.host}")
    private String host;

    @Value("${elasticsearch.port}")
    private int port;

    @Value("${elasticsearch.username}")
    private String username;

    @Value("${elasticsearch.password}")
    private String password;

    @Value("${elasticsearch.use-ssl}")
    private boolean useSsl;
    
    @Value("${elasticsearch.connect-timeout:5000}")
    private int connectTimeout;
    
    @Value("${elasticsearch.socket-timeout:60000}")
    private int socketTimeout;
    
    @Autowired
    private ObjectMapper objectMapper;

    @Bean
    @Primary
    public RestClient restClient() throws KeyStoreException, NoSuchAlgorithmException, KeyManagementException {
        final CredentialsProvider credentialsProvider = new BasicCredentialsProvider();
        credentialsProvider.setCredentials(
                AuthScope.ANY,
                new UsernamePasswordCredentials(username, password)
        );

        SSLContext sslContext = SSLContexts.custom()
                .loadTrustMaterial(null, (x509Certificates, s) -> true)
                .build();
                
        RestClientBuilder builder;
        if (useSsl) {
            builder = RestClient.builder(new HttpHost(host, port, "https"));
        } else {
            builder = RestClient.builder(new HttpHost(host, port, "http"));
        }
        
        // 配置连接超时与Socket超时
        builder.setRequestConfigCallback(
            (RequestConfig.Builder requestConfigBuilder) -> requestConfigBuilder
                .setConnectTimeout(connectTimeout)
                .setSocketTimeout(socketTimeout)
        );
        
        // 配置HTTP客户端
        builder.setHttpClientConfigCallback(
            (HttpAsyncClientBuilder httpClientBuilder) -> {
                if (useSsl) {
                    httpClientBuilder
                        .setDefaultCredentialsProvider(credentialsProvider)
                        .setSSLContext(sslContext)
                        .setSSLHostnameVerifier((hostname, session) -> true);
                } else {
                    httpClientBuilder
                        .setDefaultCredentialsProvider(credentialsProvider);
                }
                return httpClientBuilder;
            }
        );
        
        return builder.build();
    }

    @Bean
    public ElasticsearchClient elasticsearchClient(RestClient restClient) {
        // Create JacksonJsonpMapper using the configured ObjectMapper
        JacksonJsonpMapper jacksonJsonpMapper = new JacksonJsonpMapper(objectMapper);
        ElasticsearchTransport transport = new RestClientTransport(restClient, jacksonJsonpMapper);
        return new ElasticsearchClient(transport);
    }
} 