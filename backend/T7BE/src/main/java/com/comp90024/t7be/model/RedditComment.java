/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Reddit评论实体类 - 基于新的ES数据结构
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RedditComment {
    @JsonProperty("_id")
    private String id;
    
    @JsonProperty("_index")
    private String index;
    
    @JsonProperty("_score")
    private Float _score;
    
    @JsonProperty("_version")
    private Integer version;
    
    @JsonProperty("@timestamp")
    private List<String> timestamp;
    
    @JsonProperty("basic_emotion")
    private List<String> basicEmotion;
    
    @JsonProperty("author")
    private List<String> author;
    
    @JsonProperty("author_flair_text")
    private List<String> authorFlairText;
    
    @JsonProperty("category")
    private List<String> category;
    
    @JsonProperty("category.keyword")
    private List<String> categoryKeyword;
    
    @JsonProperty("isGeneralHousing")
    private List<Boolean> isGeneralHousing;
    
    @JsonProperty("isRental")
    private List<Boolean> isRental;
    
    @JsonProperty("isMentalHealth")
    private List<Boolean> isMentalHealth;
    
    @JsonProperty("isWage")
    private List<Boolean> isWage;
    
    @JsonProperty("isImmigration")
    private List<Boolean> isImmigration;
    
    @JsonProperty("loc_pid")
    private List<String> locPid;
    
    @JsonProperty("location")
    private List<String> location;
    
    @JsonProperty("content_id")
    private List<String> contentId;
    
    @JsonProperty("post_id_original")
    private List<String> postIdOriginal;
    
    @JsonProperty("data_type")
    private List<String> dataType;
    
    @JsonProperty("sentiment_score")
    private List<Float> sentimentScore;
    
    @JsonProperty("score")
    private List<Float> score;
    
    @JsonProperty("num_comments")
    private List<Integer> numComments;
    
    @JsonProperty("state")
    private List<String> state;
    
    @JsonProperty("text")
    private List<String> text;
    
    @JsonProperty("sort")
    private List<Long> sort;
    
    @JsonProperty("embedding")
    private List<Float> embedding;
    
    @JsonProperty("text_vector")
    private List<Float> textVector;
    
    @JsonProperty("unique_id")
    private List<String> uniqueId;
    
    @JsonProperty("subreddit")
    private List<String> subreddit;
    
    @JsonProperty("search_query_keyword")
    private List<String> searchQueryKeyword;
    
    @JsonProperty("search_time_filter")
    private List<String> searchTimeFilter;
    
    @JsonProperty("url")
    private List<String> url;
    
    /**
     * 获取第一个类别
     */
    public String getFirstCategory() {
        return category != null && !category.isEmpty() ? category.get(0) : null;
    }
    
    /**
     * 获取第一个情感分数
     */
    public Float getFirstSentimentScore() {
        return sentimentScore != null && !sentimentScore.isEmpty() ? sentimentScore.get(0) : null;
    }
    
    /**
     * 获取第一个州/地区
     */
    public String getFirstState() {
        return state != null && !state.isEmpty() ? state.get(0) : null;
    }
    
    /**
     * 获取第一个位置
     */
    public String getFirstLocation() {
        return location != null && !location.isEmpty() ? location.get(0) : null;
    }
    
    /**
     * 获取第一个区域ID
     */
    public String getFirstLocPid() {
        return locPid != null && !locPid.isEmpty() ? locPid.get(0) : null;
    }
    
    /**
     * 获取第一个时间戳
     */
    public String getFirstTimestamp() {
        return timestamp != null && !timestamp.isEmpty() ? timestamp.get(0) : null;
    }
    
    /**
     * 获取第一个内容ID
     */
    public String getFirstContentId() {
        return contentId != null && !contentId.isEmpty() ? contentId.get(0) : null;
    }
    
    /**
     * 获取第一个唯一ID
     */
    public String getFirstUniqueId() {
        return uniqueId != null && !uniqueId.isEmpty() ? uniqueId.get(0) : null;
    }
    
    /**
     * 获取第一个子版块
     */
    public String getFirstSubreddit() {
        return subreddit != null && !subreddit.isEmpty() ? subreddit.get(0) : null;
    }
    
    /**
     * 获取第一个URL
     */
    public String getFirstUrl() {
        return url != null && !url.isEmpty() ? url.get(0) : null;
    }
    
    /**
     * 获取第一个分数
     */
    public Float getFirstScore() {
        return score != null && !score.isEmpty() ? score.get(0) : null;
    }
    
    /**
     * 获取第一个评论数量
     */
    public Integer getFirstNumComments() {
        return numComments != null && !numComments.isEmpty() ? numComments.get(0) : null;
    }
    
    /**
     * 获取第一个作者
     */
    public String getFirstAuthor() {
        return author != null && !author.isEmpty() ? author.get(0) : null;
    }
    
    /**
     * 获取第一个作者标签文本
     */
    public String getFirstAuthorFlairText() {
        return authorFlairText != null && !authorFlairText.isEmpty() ? authorFlairText.get(0) : null;
    }
} 