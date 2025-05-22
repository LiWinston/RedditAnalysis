/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.util;

import co.elastic.clients.elasticsearch._types.aggregations.*;
import co.elastic.clients.elasticsearch._types.query_dsl.*;
import co.elastic.clients.json.JsonData;
import lombok.experimental.UtilityClass;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

/**
 * Elasticsearch query builder utility class
 */
@UtilityClass
public class ElasticsearchQueryBuilder {

    private static final String DATE_FORMAT = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";
    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern(DATE_FORMAT);

    /**
     * Build pagination query
     * @param page page number (starting from 1)
     * @param size page size
     * @return pagination query object
     */
    public static Query buildPaginationQuery(int page, int size) {
        return Query.of(q -> q
                .bool(b -> b
                        .must(m -> m
                                .matchAll(MatchAllQuery.of(ma -> ma))
                        )
                )
        );
    }

    /**
     * Build location query
     * @param location location
     * @return query object
     */
    public static Query buildLocationQuery(String location) {
        return Query.of(q -> q
                .match(m -> m
                        .field("postcode_pid")
                        .query(location)
                )
        );
    }

    /**
     * Build state/province query
     * @param state state/province
     * @return query object
     */
    public static Query buildStateQuery(String state) {
        return Query.of(q -> q
                .match(m -> m
                        .field("state")
                        .query(state)
                )
        );
    }

    /**
     * Build emotion type query
     * @param emotionType emotion type
     * @return query object
     */
    public static Query buildEmotionTypeQuery(String emotionType) {
        return Query.of(q -> q
                .match(m -> m
                        .field("emotion_type")
                        .query(emotionType)
                )
        );
    }

    /**
     * Build date range query
     * @param startDate start date
     * @param endDate end date
     * @return query object
     */
    public static Query buildDateRangeQuery(LocalDate startDate, LocalDate endDate) {
        String startDateStr = startDate.atStartOfDay().format(formatter);
        String endDateStr = endDate.plusDays(1).atStartOfDay().minusNanos(1).format(formatter);
        
        RangeQuery rangeQuery = RangeQuery.of(r -> r.date(d -> d
                .field("@timestamp")
                .gte(startDateStr)
                .lte(endDateStr)
        ));
        
        return Query.of(q -> q.range(rangeQuery));
    }

    /**
     * Build monthly aggregation
     * @param aggregationName aggregation name
     * @return aggregation object
     */
    public static Aggregation buildMonthlyAggregation(String aggregationName) {
        return Aggregation.of(a -> a
                .dateHistogram(d -> d
                        .field("@timestamp")
                        .calendarInterval(CalendarInterval.Month)
                        .format("yyyy-MM")
                        .minDocCount(0)
                )
        );
    }

    /**
     * Build average sentiment score aggregation
     * @param aggregationName aggregation name
     * @return aggregation object
     */
    public static Aggregation buildAvgSentimentAggregation(String aggregationName) {
        return Aggregation.of(a -> a
                .avg(av -> av
                        .field("sentiment_score")
                )
        );
    }

    /**
     * Build location aggregation
     * @param aggregationName aggregation name
     * @return aggregation object
     */
    public static Aggregation buildLocationAggregation(String aggregationName) {
        return Aggregation.of(a -> a
                .terms(t -> t
                        .field("postcode_pid")
                        .size(100)
                )
        );
    }
} 