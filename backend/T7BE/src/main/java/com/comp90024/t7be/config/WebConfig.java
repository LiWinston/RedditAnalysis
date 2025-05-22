/*
 * Team 7
 * Zifei Li 1638553
 * Yunpeng Xiong 1513076
 * Tianyun Lei 1454701
 * Yongchun Li 1378156
 * Haowen Zhang 1635503
 */
package com.comp90024.t7be.config;

import com.comp90024.t7be.model.enums.TopicCategory;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.convert.converter.Converter;
import org.springframework.format.FormatterRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web配置类
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    /**
     * 添加自定义转换器
     */
    @Override
    public void addFormatters(FormatterRegistry registry) {
        // 添加字符串到TopicCategory的转换器
        registry.addConverter(new StringToTopicCategoryConverter());
    }

    /**
     * 字符串到TopicCategory枚举的转换器
     */
    private static class StringToTopicCategoryConverter implements Converter<String, TopicCategory> {
        @Override
        public TopicCategory convert(String source) {
            // 使用枚举中定义的fromQueryKey方法进行转换
            TopicCategory category = TopicCategory.fromQueryKey(source);
            if (category == null) {
                throw new IllegalArgumentException("No enum constant " + 
                        TopicCategory.class.getName() + " for key: " + source);
            }
            return category;
        }
    }
} 