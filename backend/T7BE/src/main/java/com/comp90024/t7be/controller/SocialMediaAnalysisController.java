/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.controller;

import com.comp90024.t7be.model.RedditComment;
import com.comp90024.t7be.model.dto.*;
import com.comp90024.t7be.model.enums.TopicCategory;
import com.comp90024.t7be.service.ISocialMediaAnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 社交媒体分析控制器
 */
@RestController
@RequestMapping("/api/analysis")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class SocialMediaAnalysisController {

    private final ISocialMediaAnalysisService socialMediaAnalysisService;

    /**
     * 获取地理位置的帖子数据（分页）
     */
    @GetMapping("/comments/location/{location}")
    public ResponseEntity<PageResponseDTO<RedditComment>> getCommentsByLocation(
            @PathVariable String location,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ResponseEntity.ok(socialMediaAnalysisService.getCommentsByLocation(location, page, size));
    }

    /**
     * 获取州/省的帖子数据（分页）
     */
    @GetMapping("/comments/state/{state}")
    public ResponseEntity<PageResponseDTO<RedditComment>> getCommentsByState(
            @PathVariable String state,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ResponseEntity.ok(socialMediaAnalysisService.getCommentsByState(state, page, size));
    }

    /**
     * 获取情感类型的帖子数据（分页）
     */
    @GetMapping("/comments/emotion/{emotionType}")
    public ResponseEntity<PageResponseDTO<RedditComment>> getCommentsByEmotionType(
            @PathVariable String emotionType,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ResponseEntity.ok(socialMediaAnalysisService.getCommentsByEmotionType(emotionType, page, size));
    }

    /**
     * 获取地图分析数据 - 特定主题各地区情感分析
     */
    @GetMapping({"/map/{state}/{category}", "/map/{state}"})
    public ResponseEntity<List<GeoSentimentDTO>> getMapAnalysisData(
            @PathVariable String state,
            @PathVariable(required = false) TopicCategory category) {
        return ResponseEntity.ok(socialMediaAnalysisService.getGeoSentimentAnalysis(state, category));
    }

    /**
     * 获取饼图数据 - 主题讨论量分布
     */
    @GetMapping("/pie/{state}")
    public ResponseEntity<List<TopicSentimentDTO>> getPieChartData(
            @PathVariable String state) {
        return ResponseEntity.ok(socialMediaAnalysisService.getTopicSentimentDistribution(state));
    }

    /**
     * 获取雷达图数据 - 主题平均情感得分
     */
    @GetMapping("/radar/{state}")
    public ResponseEntity<Map<TopicCategory, Float>> getRadarChartData(
            @PathVariable String state) {
        return ResponseEntity.ok(socialMediaAnalysisService.getTopicAverageSentiment(state));
    }

    /**
     * 获取折线图数据 - 情感随时间变化趋势
     */
    @GetMapping("/line/{state}/{category}")
    public ResponseEntity<List<TimeSentimentDTO>> getLineChartData(
            @PathVariable String state,
            @PathVariable TopicCategory category,
            @RequestParam(defaultValue = "12") int monthCount) {
        return ResponseEntity.ok(socialMediaAnalysisService.getTimeSentimentTrend(state, category, monthCount));
    }

    /**
     * 获取热力图数据 - 主题相关性分析
     */
    @GetMapping("/heatmap/{state}")
    public ResponseEntity<List<CorrelationDTO>> getHeatmapData(
            @PathVariable String state) {
        return ResponseEntity.ok(socialMediaAnalysisService.getTopicCorrelationAnalysis(state));
    }
} 