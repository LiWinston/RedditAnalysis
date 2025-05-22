/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.model.enums;

import lombok.Getter;

/**
 * Topic category enumeration.
 */
@Getter
public enum TopicCategory {
    // Based on analysis goals, modified to four categories meeting business requirements
    HOUSING("general housing", "general housing", "isGeneralHousing"),
    RENTAL("rental", "rental", "isRental"),
    WAGE("wage", "wage", "isWage"),
    MENTAL_HEALTH("mental health", "mental health", "isMentalHealth"),
    IMMIGRATION("immigration", "immigration", "isImmigration");
    
    private final String displayName;
    private final String queryKey;
    private final String booleanField;
    
    TopicCategory(String displayName, String queryKey, String booleanField) {
        this.displayName = displayName;
        this.queryKey = queryKey;
        this.booleanField = booleanField;
    }
    
    /**
     * Get enum value from query key string.
     * @param key Query key.
     * @return Corresponding enum value, or null if no match.
     */
    public static TopicCategory fromQueryKey(String key) {
        if (key == null) {
            return null;
        }
        
        for (TopicCategory category : TopicCategory.values()) {
            if (category.getQueryKey().equalsIgnoreCase(key)) {
                return category;
            }
        }
        return null;
    }
} 