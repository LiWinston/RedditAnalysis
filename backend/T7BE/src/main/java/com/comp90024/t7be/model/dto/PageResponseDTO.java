/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Generic paginated response data transfer object
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PageResponseDTO<T> {
    /**
     * Current page number
     */
    private Integer currentPage;
    
    /**
     * Page size
     */
    private Integer pageSize;
    
    /**
     * Total record count
     */
    private Long totalCount;
    
    /**
     * Total page count
     */
    private Integer totalPages;
    
    /**
     * Page data
     */
    private List<T> data;
} 