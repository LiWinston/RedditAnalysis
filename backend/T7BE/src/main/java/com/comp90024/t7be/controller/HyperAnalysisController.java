/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.controller;

import com.comp90024.t7be.model.analysis.AnalysisCard;
import com.comp90024.t7be.model.enums.TopicCategory;
import com.comp90024.t7be.service.HyperAnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 高级分析控制器
 */
@RestController
@RequestMapping("/api/analysis/hyper")
@RequiredArgsConstructor
@CrossOrigin(origins = "*", maxAge = 3600)
public class HyperAnalysisController {

    private final HyperAnalysisService hyperAnalysisService;

    /**
     * 分析地区热议内容
     *
     * @param locPid 地区ID
     * @param limit 最新评论条数，可选，默认10
     * @return 分析结果卡片
     */
    @GetMapping("/local-hot-topics")
    public ResponseEntity<AnalysisCard> analyzeLocalHotTopics(
            @RequestParam String locPid,
            @RequestParam(required = false, defaultValue = "10") int limit) {
        
        AnalysisCard result = hyperAnalysisService.analyzeLocalHotTopics(locPid, limit);
        return ResponseEntity.ok(result);
    }

    /**
     * 分析特定主题的讨论
     *
     * @param locPid 地区ID
     * @param topic 主题类别，可用值：general_housing, rental, wage, mental_health, immigration
     * @param limit 最新评论条数，可选，默认10
     * @return 分析结果卡片
     */
    @GetMapping("/topic-discussion")
    public ResponseEntity<AnalysisCard> analyzeTopicDiscussion(
            @RequestParam String locPid,
            @RequestParam TopicCategory topic,
            @RequestParam(required = false, defaultValue = "10") int limit) {
        
        AnalysisCard result = hyperAnalysisService.analyzeTopicDiscussion(locPid, topic, limit);
        return ResponseEntity.ok(result);
    }
    
    /**
     * 自然语言查询接口，通过RAG获取关于特定问题的洞察
     * 
     * 此接口支持多种灵活的地理约束和主题过滤选项：
     * 
     * 地理约束（三选一，优先级从高到低）：
     * - locPid：精确的地区编码过滤
     * - state：州/领地名称过滤
     * - location：位置名称过滤
     * 
     * 主题过滤：
     * - topics：以逗号分隔的主题列表，例如"rental,wage,mental_health"
     * - 筛选包含任一指定主题的内容（OR关系）
     * 
     * 所有过滤条件均为可选项。如不指定，将基于纯语义相关性检索内容。
     * 
     * @param queryRequest 查询请求对象，包含查询文本和各种过滤条件
     * @return 分析结果卡片
     */
    @PostMapping("/query-insights")
    public ResponseEntity<AnalysisCard> queryInsights(
            @RequestBody QueryRequest queryRequest) {
        
        AnalysisCard result = hyperAnalysisService.queryInsightsWithRag(
            queryRequest.getQuery(), 
            queryRequest.getLocPid(),
            queryRequest.getState(),
            queryRequest.getLocation(),
            queryRequest.getTopics(),
            queryRequest.getLimit() != null ? queryRequest.getLimit() : 10
        );
        return ResponseEntity.ok(result);
    }
    
    /**
     * 查询请求对象
     * 
     * 封装了自然语言查询的各种参数，包括：
     * - 查询文本
     * - 地理约束（locPid、state、location三选一）
     * - 主题过滤（逗号分隔的多个主题，是OR关系）
     * - 结果数量限制
     */
    public static class QueryRequest {
        private String query;
        private String locPid;
        private String state;
        private String location;
        private String topics;
        private Integer limit;
        
        public String getQuery() {
            return query;
        }
        
        public void setQuery(String query) {
            this.query = query;
        }
        
        public String getLocPid() {
            return locPid;
        }
        
        public void setLocPid(String locPid) {
            this.locPid = locPid;
        }
        
        public String getState() {
            return state;
        }
        
        public void setState(String state) {
            this.state = state;
        }
        
        public String getLocation() {
            return location;
        }
        
        public void setLocation(String location) {
            this.location = location;
        }
        
        public String getTopics() {
            return topics;
        }
        
        public void setTopics(String topics) {
            this.topics = topics;
        }
        
        public Integer getLimit() {
            return limit;
        }
        
        public void setLimit(Integer limit) {
            this.limit = limit;
        }
    }
} 