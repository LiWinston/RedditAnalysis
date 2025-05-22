# 阶段1：构建应用
FROM maven:3.9.6-eclipse-temurin-17 as builder

# 设置工作目录
WORKDIR /app

# 复制Maven配置文件，便于依赖缓存
COPY pom.xml .
COPY .mvn/ .mvn/
COPY mvnw mvnw
COPY mvnw.cmd mvnw.cmd

# 下载依赖
RUN --mount=type=cache,target=/root/.m2 mvn dependency:go-offline -B

# 复制源代码
COPY src/ src/

# 构建应用
RUN --mount=type=cache,target=/root/.m2 mvn package -DskipTests

# 阶段2：运行时镜像
FROM eclipse-temurin:17-jre

# 设置工作目录
WORKDIR /app

# 设置JVM选项
ENV JAVA_OPTS=""

# 从构建阶段复制构建好的JAR文件
COPY --from=builder /app/target/*.jar app.jar

# 暴露应用端口
EXPOSE 8080

# 指定启动命令
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar --spring.profiles.active=prod"] 