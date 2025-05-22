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
import com.comp90024.t7be.service.ElasticsearchService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/comments")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class RedditCommentController {

    private final ElasticsearchService elasticsearchService;

    @GetMapping("/location/{location}")
    public ResponseEntity<List<RedditComment>> getCommentsByLocation(@PathVariable String location) {
        List<RedditComment> comments = elasticsearchService.searchByLocation(location);
        return ResponseEntity.ok(comments);
    }

    @GetMapping("/state/{state}")
    public ResponseEntity<List<RedditComment>> getCommentsByState(@PathVariable String state) {
        List<RedditComment> comments = elasticsearchService.searchByState(state);
        return ResponseEntity.ok(comments);
    }

    @GetMapping("/emotion/{emotionType}")
    public ResponseEntity<List<RedditComment>> getCommentsByEmotionType(@PathVariable String emotionType) {
        List<RedditComment> comments = elasticsearchService.searchByEmotionType(emotionType);
        return ResponseEntity.ok(comments);
    }
} 