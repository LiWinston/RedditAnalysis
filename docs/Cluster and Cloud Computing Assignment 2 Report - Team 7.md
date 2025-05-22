# Cluster and Cloud Computing Assignment 2 Report - Team 7

Zifei Li 1638553
Yunpeng Xiong 1513076
Tianyun Lei 1454701
Yongchun Li 1378156
Haowen Zhang 1635503

[TOC]

## 1.1 Project Motivation and Background

The inspiration for this project originated from a campus event we personally witnessed at the beginning of the semester. After attending a Cluster and Cloud Computing lecture and walking out of the Old Arts Building, we saw students protesting against the Myki transportation system. They were calling for the Free Tram Zone to be expanded to include Unimelb. Many students expressed that the current transportation policy makes them feel economically and psychologically marginalised. In their view, Unimelb is not only a prestigious institution located in the city centre, but also something that many students take greate pride in and identify with. A university like this should naturally be considered part of the central zone. However, the reality of being excluded brings a deep sense of disappointment. This feeling of being "left out" goes beyond a simple transport policy issue - it reveals a deeper problem: our sense of belonging in daily life is undergoing complex changes. In some areas, people may experience a weakening sense of belonging due to various factors, while in other places, residents still maintain a strong sense of identity and connection.

This phenomenon is not only limited to the transportation sector, but also sparks broader discussions on socio-economic issues. For example, in recent years, the continuous rise in housing prices in Australia's major cities has forced many young people and low-to-middle income earners into a situation of "being forced to rent" or "losing hope of buying a home". This further exacerbates their anxieties about their future and weakens their sense of belonging. On social media, we have observed many users attributing the surge in housing prices to the increase of immigration. This kind of scapegoating rhetoric not only lacks rational analysis, but also poses potential threats to the social status and psychological security of immigrant communities, leading to a further decline in their sense of belonging as they try to integrate into society. 

However, we recognise that these are just the "tip of the iceberg". In areas we have yet to explore in depth - such as employment opportunities, salary and benefits, childcare support, elderly care, and healthcare - the issues surrounding sense of belonging may be even more complex and concealed. People from different backgrounds, professions, ages, and identities may be experiencing a loss of belonging in various ways, yet their voice are often underrepresented in mainstream conversations.

Therefore, we choose to focus on the current state of Australian's sense of belonging by developing an analytical system based on social media data. This system aims to uncover the multidimensional expressions of belonging among the public, identify underlying social emotional fluctuations, and provide data-driven insights to the wider community.

## 1.2 Project Objectives

Our project aims to build a scalable big data analytics system using cloud technologies to analyse social media discussions related to Australian's sense of belonging.

## 1.3. Scope of Work

The project encompassed the following key stages and activities:

-   **Preparation:** Retrieve geographic locality data from Australian government websites (data.gov.au) and process it to create structured mappings for location identification (e.g., `loc_pid`, state, handling ambiguities). (Responsibility: Zifei Li)
-   **Data Collection:** Develop and implement Python scripts using PRAW (Python Reddit API Wrapper) to fetch relevant post and comment data from selected Australian subreddits based on predefined keywords related to housing, salary, mental health, and immigration. Implement data validation and filtering at the source. (Responsibility: Zifei Li)
-   **Continuous Data Ingestion (Nemo):** Design and deploy a serverless data ingestion pipeline using **Fission on Kubernetes**. This involved:
    *   Creating a custom Fission environment (Docker image) to support necessary libraries like `torch` for text embedding.
    *   Automating the periodic execution of harvesting and processing scripts using Fission timer triggers.
    *   Processing raw harvested data to generate `unique_id`s and text vector embeddings.
-   **Data Persistence (Nemo):** Implement robust data storage and management using **Elasticsearch**. This included:
    *   Designing the Elasticsearch index schema (`all_content_processed_vectorized_v3`) with appropriate mappings for all data fields, including `dense_vector` for embeddings.
    *   Configuring Elasticsearch for sharding and replication to ensure data availability and resilience.
    *   Implementing efficient data loading into Elasticsearch using bulk `upsert` operations.
-   **Data Serving & Querying (Yongchun Li & Tianyun Lei):** Develop a backend API service (Java Spring Boot) to:
    *   Expose ReSTful endpoints for accessing and querying data stored in Elasticsearch.
    *   Implement both standard boolean queries (for keyword matching, filtering by location, topic, etc.) and KNN-based vector search functionalities in Elasticsearch to support semantic similarity retrieval of posts and comments.
-   **Data Visualisation (Haowen Zhang):** Develop an interactive frontend using Jupyter Notebook to:
    *   Consume data from the backend API.
    *   Present analytical insights through various visualisations, including maps displaying sentiment by locality, charts for trend analysis, and representations of discussions around key themes.

## 1.4 Scenario Overview
We have chosen the scenario of **Belonging among Australians** - a topic that has gained increasing attention in recent years. In our project, we aim to explore how Australians express their sense of belonging in public discourse. We focus on key factors such as housing (both buying and renting), salary, mental health, and immigration. By analysing posts and comments on Reddit, we hope to understand how these factors contribute to the sense of belonging across different parts of Australia.

## 1.5 Key Technologies and Platforms
- **Melbourne Research Cloud:** Provide the cloud infrastructure for hosting our entire application stack.
- **Kubernetes:** Responsible for managing and scheduling application components deployed in containers (including Fission, ElasticSearch, Jupyter Notebook, etc.), enabling load balancing, resource allocation, and dynamic scaling.
- **Fission:** Support our serverless data processing pipeline, enabling real-time ingestion of social media data
- **ElasticSearch:** Store and index social media content, enabling complex text-based searches and analytics.
- **JupyterNotebook:** Server as our interactive frontend for data visualisation and analysis through RESTful API connections.
- **Java & Springboot** and elastic search java api:  convenient set up of backend api service 
- **Langchain4J**: serve the an adapter of AI api invocation for spring backend
- **GitLab:** Manage our codebase with version control.
- **Python:** Implement data harvesting logic. Perform sentiment analysis with Vader and TextBlob.

#  2 SYSTEM ARCHITECTURE AND DESIGN

## 2.1 Overall System Architecture

![](https://hackmd.io/_uploads/By0LoN9-gl.png)


## 2.2. Data Source

In our project, we initially considered multiple social media platforms to analyse Australians' sense of belonging but ultimately focused exclusively on Reddit as our primary data source after careful evaluation.

### 2.2.1 Select Reddit as Primary Data Source

Reddit was selected as our primary platform for the following reasons:

- Reddit has a large number of well-established and well-categorised subreddits, which allows us to collect diverse opinions from Australian users, providing a broad and comprehensive data source.
- Reddit offers an official application interface (https://www.reddit.com/prefs/apps), making it convinient for us to authorise, access, and automatically retrieve data.
- Reddit provides a fully featured Python library - Python Reddit API Wrapper(PRAW) - which offers considerable mature and easy-to-use methods that help us efficiently obtain the information we need. For example, we can easily use the `subreddit.search` method to search for posts related to specific keywords within a given subreddit. 

The following screenshot stated how many data we've collected in our ElasticSearch:

![image](https://hackmd.io/_uploads/BJUEJs9Wge.png)
![image](https://hackmd.io/_uploads/S1ouR95-ex.png)

### 2.2.2 Mastodon Limitations and Challenges

we ultimately abandoned Mastodon data collection due to several significant challenges:

- The content on Mastodon, even on Australian-focused instances, predominantly featured global rather than local discussions. Unlike Reddit's geographically-organized subreddits, Mastodon's decentralized structure created difficulties in isolating Australia-specific content. The high proportion of irrelevant data (noise) made effective filtering impractical without employing large language models.
- Geographic entity extraction proved particularly problematic. English-speaking countries share numerous identical place names, causing significant ambiguity. For example, locations like "Richmond" appear in multiple Australian states and other English-speaking countries, making accurate geographic classification challenging without sophisticated contextual analysis.
- Servers with more detailed geographical levels lack users - for example, the server named Melbourne has only more than ten users, and most of the posts are arbitrarily shared photos - but the API can only obtain text content.

In summary, as a decentralized Mastodon, contrary to reddit, which is a gathering place for knowledge, experience and serious communication, it does not provide enough recognizable data related to our topic.

### 2.2.3 BlueSky Limitations and Challenges

While exploring potential data sources, BlueSky was considered but ultimately not chosen for this project due to several limitations and challenges in the context of analysing Australians' sense of belonging:

1.  **Nascent Platform and User Base:** BlueSky is a relatively new social media platform. Compared to established platforms like Reddit, its Australian user base is likely to be significantly smaller and potentially less representative of the broader Australian population. This limited scale would make it difficult to gather a sufficient volume of data to draw meaningful and generalisable conclusions about a nuanced topic like "sense of belonging" across diverse demographics and regions in Australia.

2.  **Content Focus and Maturity:** As an emerging platform, discussions on BlueSky might lean more towards topics related to technology, the platform itself, and early adopter interests. It is less likely to host the same depth and breadth of conversations on socio-economic issues, local community concerns, housing, salary, or mental health specific to Australia, which are central to our research. Established platforms like Reddit have dedicated communities (subreddits) where such discussions are mature and ongoing.

3.  **Challenges in Geographic Targeting and Filtering:** Identifying and isolating Australia-specific content related to our themes could be more challenging on BlueSky. Unlike Reddit's well-defined, geographically or topically focused subreddits (e.g., `r/australia`, `r/sydney`, or specific interest groups), content discovery and filtering mechanisms on BlueSky might not yet be as sophisticated for nuanced, location-based sentiment analysis. The decentralized nature, while offering other benefits, can also make it harder to aggregate a comprehensive view of discussions pertinent to a specific nation or region.

4.  **API Maturity and Data Access Tools:** While BlueSky offers an API (the AT Protocol), the ecosystem of third-party tools, libraries (like PRAW for Reddit), and established best practices for data harvesting is still developing. This could present greater technical hurdles and require more bespoke development efforts for data collection, potentially with less certainty regarding API stability or rate limits for large-scale academic research compared to more mature APIs.

5.  **Uncertainty in Content Relevance for "Sense of Belonging":** The specific ways users express their "sense of belonging" (or lack thereof) can be subtle and deeply embedded in contextual discussions. Without a critical mass of users and established discussion norms around the specific topics of housing, salary, mental health, and immigration within an Australian context on BlueSky, the data retrieved might lack the richness and specificity required for our analytical goals.

Given these factors, we concluded that focusing our resources on Reddit would yield a more robust and relevant dataset for investigating Australians' sense of belonging for this project.

## 2.3 Data Harvesting and Streaming

### 2.3.1 Harvester Design and Implementation

#### 2.3.1.1 Preparation

-  **PRAW**

Praw is a Python package that allows for simple access to Reddit's API. With PRAW, we do not need to introduce `sleep` calls during extracting data from Reddit.(Source: PRAW official documentation, https://github.com/praw-dev/praw)

In this project, we used Version 7.8.1.

- **Geographic Locality Data**

Since the frontend map display requires binding with `loc_pid`, we have to download all the geographic locality data from the government's official website through the following url:

- **NSW:** https://data.gov.au/geoserver/nsw-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_91e70237_d9d1_4719_a82f_e71b811154c6&outputFormat=json 
- **ACT:** https://data.gov.au/geoserver/act-suburb-locality-boundaries-geoscape-administrative-boundaries/wfs (The ACT data on the official website is inaccessible, and we have documented this issue in the limitations section below)
- **QLD:** https://data.gov.au/geoserver/qld-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_6bedcb55_1b1f_457b_b092_58e88952e9f0&outputFormat=json
- **SA:** https://data.gov.au/geoserver/sa-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_bcfcfc9a_7c8d_479a_9bdf_b95ca66ad29a&outputFormat=json
- **WA:** https://data.gov.au/geoserver/wa-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_6a0ec945_c880_4882_8a81_4dbcb85e74e5&outputFormat=json
- **VIC:** https://data.gov.au/geoserver/vic-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_af33dd8c_0534_4e18_9245_fc64440f742e&outputFormat=json
- **TAS:** https://data.gov.au/geoserver/tas-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_8bd7b6c1_1258_4df5_a98f_b6706e87de1e&outputFormat=json
- **NT:** https://data.gov.au/geoserver/nt-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_12eca357_6bad_4130_9c47_eaaf4c11e039&outputFormat=json

#### 2.3.1.2 Targeted Search Strategy

To ensure that the initial data we extracted did not contain irrelevant information, we adopted a **Targeted Search Strategy**. Specifically, we untilised the `subreddit.search` method provided by PRAW (documentation: https://praw.readthedocs.io/en/stable/code_overview/models/subreddit.html) to retrieve relevant posts from selected subreddits based on specific keywords.

It is worth nothing that although the official documentation is for Version 7.7.1, we reviewed the changelog and found no significant updates since then. Therefore, we concluded that there are no major differences between Version 7.7.1 and the version we used(7.8.1), and we proceeded with development basd on the 7.7.1 documentation. This approach proved successful, as noted in the comments of our code.

After retrieving the posts, we used the `submission.commments.replace_more` method (documentation:https://praw.readthedocs.io/en/stable/code_overview/models/submission.html) to fully expand all comments. We then extracted all comment data using `submission.comments.list()`.

Importantly, we only processed comments from posts that had already passed the geographic filtering stage. We further filtered comments based on the presence of keywords: if a comment did not contain any keywords from our predefined comment dictionaries, we considered it unlikely to be useful and excluded it.

As a result, only validated post and comment data were stored in ElasticSearch. We deliberately avoided indiscriminately downloading all raw data into the database and then filtering it afterward. Such an approach is not only inefficient, but also wasteful of resources.

### 2.3.2 Use of Fission for Data Ingestion

To automate our data harvesting and ingestion pipeline, we utilized Fission, deploying our Python scripts as a serverless function. A key challenge we encountered was the need for the `torch` library, which is a dependency for our text embedding generation. The standard Fission Python environment is Alpine-based, and `torch` lacks official support for `musl libc`, the C standard library used by Alpine Linux, preventing its direct installation.

To overcome this, we built a **custom Docker image** for our Fission function. This image was based on a compatible Linux distribution (e.g., Debian or Ubuntu-based Python images) where `torch` and all other necessary dependencies could be successfully installed. This custom environment image was then used by Fission to run our data processing scripts.

The Fission function was configured with a **timer trigger**, set to execute **once per hour**. This allowed for periodic fetching of new data from Reddit without manual intervention. The execution status, output, and any logs generated by the Fission function during its hourly runs could be monitored by inspecting the corresponding Kubernetes pod logs for the Fission function instance.

![](https://hackmd.io/_uploads/r1QCxr9-gg.png)
![](https://hackmd.io/_uploads/rkT3lrcbgl.png)


### 2.4 Data Storage and Management

Once data was harvested from Reddit, it underwent a processing stage before being persisted. This involved:
1.  **Generating a `unique_id`**: A unique identifier was created for each processed data item (post or comment) to facilitate distinct tracking and updates.
2.  **Adding Text Embeddings**: The textual content was processed to generate vector embeddings (using `torch`), which are crucial for semantic search and advanced analytics.
3.  **Bulk Upsert to Elasticsearch**: The processed and enriched data was then efficiently loaded into Elasticsearch using its bulk `_update` API with the `upsert` operation.

Our Elasticsearch cluster was deployed across two nodes. To ensure data resilience and availability, our primary data index (named `all_content_processed_vectorized_v3`) was configured with **one primary shard and one replica shard**. This setup provides a balance of performance and fault tolerance.

We utilized **Kibana**, connected to our Elasticsearch cluster, for quick data exploration, performing ad-hoc queries, creating visualizations, and gaining an initial overview of the indexed content.

### 2.4.1 Elasticsearch Schema Design

After careful consideration and discussion, we opted for a **single Elasticsearch index** to store all harvested and processed social media data. This approach offers several advantages for our project's scope:
*   **Simplified Query Design:** Querying a single index is generally more straightforward than managing cross-index searches.
*   **Easier Index Management:** For the scale of this project, managing one index is less complex.
*   **Cohesive Data:** All our data revolves around the central theme of "sense of belonging" and shares a largely consistent structure, making a single index a natural fit.

The defined mapping for our index (`all_content_processed_vectorized_v3`) is detailed below. This mapping specifies the data type for each field and how it should be indexed and analyzed by Elasticsearch.

| Field Name             | Type           | Analyzer/Format/Dims/Index             | Sub-Fields (if any)                                 | Notes                                                    |
|------------------------|----------------|----------------------------------------|-----------------------------------------------------|----------------------------------------------------------|
| `unique_id`            | `keyword`      |                                        |                                                     | Unique identifier for the document (post/comment).       |
| `content_id`           | `keyword`      |                                        |                                                     | Original ID from Reddit (e.g., post ID, comment ID).     |
| `text`                 | `text`         | `standard`                             |                                                     | The main textual content of the post or comment.         |
| `@timestamp`           | `date`         | `yyyy-MM-dd HH:mm:ss\|\|epoch_millis`  |                                                     | Timestamp of the data point.                             |
| `sentiment_score`      | `float`        |                                        |                                                     | Calculated sentiment score.                              |
| `basic_emotion`        | `keyword`      |                                        |                                                     | Dominant basic emotion detected.                         |
| `location`             | `keyword`      |                                        |                                                     | Identified location string.                              |
| `loc_pid`              | `keyword`      |                                        |                                                     | Persistent Identifier for the locality.                  |
| `state`                | `keyword`      |                                        |                                                     | Identified Australian state.                             |
| `subreddit`            | `keyword`      |                                        |                                                     | Source subreddit.                                        |
| `search_query_keyword` | `keyword`      |                                        |                                                     | Keyword used for the initial search.                     |
| `search_time_filter`   | `keyword`      |                                        |                                                     | Time filter used during search (e.g., "all", "year").  |
| `url`                  | `keyword`      | `index: False`                         |                                                     | URL of the Reddit post/comment. Not indexed for search.  |
| `score`                | `float`        |                                        |                                                     | Reddit score (upvotes - downvotes).                      |
| `num_comments`         | `float`        |                                        |                                                     | Number of comments on a post.                            |
| `author`               | `keyword`      |                                        |                                                     | Reddit author username.                                  |
| `author_flair_text`    | `text`         |                                        | `keyword`: { `type`: `keyword`, `ignore_above`: 1024 } | Author's flair text, with a keyword sub-field.         |
| `data_type`            | `keyword`      |                                        |                                                     | Indicates if it's a "post" or "comment".                 |
| `post_id_original`     | `keyword`      |                                        |                                                     | For comments, the ID of their parent post.               |
| `isGeneralHousing`     | `boolean`      |                                        |                                                     | Flag indicating relevance to general housing.            |
| `isImmigration`        | `boolean`      |                                        |                                                     | Flag indicating relevance to immigration.                |
| `isRental`             | `boolean`      |                                        |                                                     | Flag indicating relevance to rental housing.             |
| `isWage`               | `boolean`      |                                        |                                                     | Flag indicating relevance to wages/salary.               |
| `isMentalHealth`       | `boolean`      |                                        |                                                     | Flag indicating relevance to mental health.              |
| `text_vector`          | `dense_vector` | `dims: 384`                            |                                                     | 384-dimensional vector embedding of the `text` field.    |

### 2.4.2 Data Indexing Strategy

Our core data indexing strategy centers around the `unique_id` field, which functions as the document identifier (akin to a primary key in relational databases) within our Elasticsearch index. This `unique_id` is programmatically generated during the data processing stage, typically by combining elements like the original `content_id` and potentially location-specific identifiers if a piece of content is analyzed for multiple distinct localities. This ensures each document intended for storage is uniquely addressable.

When ingesting data into Elasticsearch, we leverage the **`upsert`** capability provided by the `_update` API. By specifying the `unique_id` as the document ID in our bulk requests, Elasticsearch will:
1.  **Update**: If a document with the given `unique_id` already exists in the index, Elasticsearch will update its content with the newly provided data.
2.  **Insert**: If no document with that `unique_id` exists, Elasticsearch will insert the provided data as a new document.

This `upsert` strategy is particularly beneficial as it handles both initial data loading and subsequent updates or re-harvesting of data gracefully. It prevents the creation of duplicate documents, ensuring data integrity and consistency over time, which is crucial if harvesters run periodically and might re-process some overlapping content or if enrichments (like sentiment or embeddings) are re-calculated.

## 2.5 Serving Data Analytics

### 2.5.1 Backend Design

Our backend design follows a clean layered architecture that prioritizes maintainability and separation of concerns. The core design principles include:

1. **Controller-Service-Repository Pattern**: Clear separation between API endpoints (controllers), business logic (services), and data access.

2. **Interface-based Design**: We defined interfaces for all service components to enable loose coupling.

3. **Composable Analytics Strategy**: Rather than creating monolithic analysis methods, we designed a composable approach where complex analyses are built from reusable query components that can be mixed and matched.

### 2.5.2 Integration with Elasticsearch

To maximize the performance and capabilities of Elasticsearch in our analytics pipeline, we implemented a dual-mode access strategy:

1. **High-level Java Client API**: For standard type-safe queries that benefit from Java's strong typing
2. **Low-level RestClient**: For advanced DSL queries and complex aggregations
3. **Computation Offloading**: Critical aggregations are executed directly within Elasticsearch to reduce network transfer and memory pressure
4. **Query Abstraction Layer**: ElasticsearchService encapsulates query complexity behind domain-focused methods

### 2.5.3 ReSTful API Design

Our RESTful API endpoints are designed around resources and follow a consistent pattern. The system exposes the following endpoints:

**Social Media Analysis Endpoints** (`/api/analysis/...`)

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/comments/location/{location}` | GET | Retrieves comments for a specific location | `location` (path), `page`, `size` |
| `/comments/state/{state}` | GET | Retrieves comments for a specific state/territory | `state` (path), `page`, `size` |
| `/comments/emotion/{emotionType}` | GET | Retrieves comments with specific emotion | `emotionType` (path), `page`, `size` |
| `/map/{state}/{category?}` | GET | Gets geo-sentiment data for map visualization | `state` (path), `category` (path, optional) |
| `/pie/{state}` | GET | Gets topic distribution data for pie charts | `state` (path) |
| `/radar/{state}` | GET | Gets average sentiment scores by topic for radar charts | `state` (path) |
| `/line/{state}/{category}` | GET | Gets time-series sentiment data for line charts | `state` (path), `category` (path), `monthCount` (default: 12) |
| `/heatmap/{state}` | GET | Gets topic correlation data for heatmap visualization | `state` (path) |

**RAG Analysis Endpoints** (`/api/analysis/hyper/...`)

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/local-hot-topics` | GET | Analyzes hot topics in a region | `locPid`, `limit` (default: 10) |
| `/topic-discussion` | GET | Analyzes specific topic discussion in a region | `locPid`, `topic`, `limit` (default: 10) |
| `/query-insights` | POST | Performs natural language query against content | Request body with `query`, optional location filters (`locPid`/`state`/`location`), `topics`, `limit` |

**Basic Data Access** (`/api/comments/...`)

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/location/{location}` | GET | Retrieves comments for a specific location | `location` (path) |
| `/state/{state}` | GET | Retrieves comments for a specific state/territory | `state` (path) |
| `/emotion/{emotionType}` | GET | Retrieves comments with specific emotion | `emotionType` (path) |

All responses follow standardized formats: paginated results use `PageResponseDTO`, visualization endpoints return specialized DTOs structured for immediate consumption by frontend visualizations, and the RAG endpoints return `AnalysisCard` objects with structured insights.

## 2.6 Frontend and Visualisation (Jupyter Notebook)
Our front-end data follows defined data structure based on data needed for multiple charts, and we also defined these data structure for the data interactive interface of backend.

After retrieving data, the data processing follows pre-defined visualization effect, we extract sub-data from origin data retrieved through backend interface, then assign them to different visualization effect moudles to achieve different visual effect.
## 2.7 Technology Stack Rationale

### 2.7.1 Choice of Kubernetes, Fission, and Elasticsearch

The selection of Kubernetes, Fission, and Elasticsearch as the core technology stack for this project was a strategic decision aimed at building a robust, scalable, and efficient big data analytics system capable of handling the complexities of social media data analysis. Each component plays a critical role in the overall architecture:

**1. Kubernetes: For Orchestration, Scalability, and Resilience**

Kubernetes was chosen as the foundational orchestration platform for several key reasons directly relevant to our project's needs:

*   **Container Management and Deployment:** Our application consists of multiple components (data harvesters, data processing units, Elasticsearch, a backend API, and the Jupyter Notebook frontend). Kubernetes allows us to package these components into isolated containers (using Docker) and manage their deployment, updates, and lifecycle efficiently and consistently across the Melbourne Research Cloud environment.
*   **Scalability and Resource Optimization:** The volume of social media data can fluctuate, and processing demands can vary. Kubernetes enables dynamic scaling of our application components. For instance, if data harvesting needs to be intensified or if the analytical backend experiences high load, Kubernetes can scale the respective pods up or down, ensuring optimal resource utilization and performance.
*   **High Availability and Resilience:** For a system processing continuous data streams and serving analytical queries, resilience is paramount. Kubernetes provides self-healing capabilities, automatically restarting failed containers and rescheduling them on healthy nodes. This ensures that critical components like Elasticsearch and our backend API remain operational.
*   **Service Discovery and Networking:** Kubernetes provides a robust internal networking model and service discovery mechanisms, allowing our different microservices (e.g., the Jupyter Notebook frontend, backend API, and Elasticsearch) to discover and communicate with each other reliably without hardcoding IP addresses.

**2. Fission: For Serverless, Event-Driven Data Ingestion**

Fission, a serverless framework built on Kubernetes, was selected to automate and manage our data ingestion pipeline:

*   **Automated Periodic Harvesting:** Our project requires periodic fetching of new data from Reddit. Fission's timer triggers provide an ideal mechanism for scheduling our data harvesting scripts (packaged in a custom Docker image due to `torch` dependencies) to run automatically at regular intervals (e.g., hourly) without manual intervention.
*   **Event-Driven Architecture:** Fission promotes an event-driven approach. While our primary use was timer-based, it offers flexibility for future extensions, such as triggering processing pipelines based on other events (e.g., new files in a storage bucket, though not used in this iteration).
*   **Resource Efficiency for Scheduled Tasks:** By using Fission, our data harvesting scripts only consume significant compute resources when they are actively running. This is more efficient than having a dedicated, always-on virtual machine or pod just for periodic tasks.
*   **Simplified Function Management (within Kubernetes):** Once the custom environment was set up, Fission simplified the deployment and management of the serverless function itself, abstracting away some of the underlying Kubernetes complexities for this specific task.

**3. Elasticsearch: For Powerful Search, Storage, and Analytics of Big Text Data**

Elasticsearch was the cornerstone of our data persistence and analytics layer, offering capabilities crucial for handling and deriving insights from social media text:

*   **Advanced Full-Text Search:** The core of our project involves analyzing textual data from Reddit. Elasticsearch is purpose-built for fast and sophisticated full-text search, allowing us to query posts and comments based on keywords, phrases, and complex boolean logic.
*   **Scalable Big Data Storage:** Social media generates vast amounts of data. Elasticsearch is a distributed system designed to scale horizontally, allowing us to store and manage large volumes of posts and comments efficiently within our `all_content_processed_vectorized_v3` index.
*   **Schema Flexibility and Rich Data Types:** While we defined a specific mapping, Elasticsearch offers flexibility. Its support for diverse data types, including `keyword`, `text`, `date`, `float`, `boolean`, and critically, `dense_vector`, was essential for storing our multifaceted data.
*   **Vector Search (k-Nearest Neighbor - KNN):** A key requirement for understanding "sense of belonging" was semantic analysis. Elasticsearch's native support for dense vector fields and KNN search allowed us to perform similarity searches based on the text embeddings we generated. This enables finding posts/comments that are semantically similar, even if they don't share exact keywords.
*   **Powerful Aggregations Framework:** To identify trends and patterns, Elasticsearch provides a comprehensive aggregation framework. This allows us to group data by location, sentiment, topic, etc., and calculate metrics, which are vital for the visualizations in our Jupyter Notebook.
*   **Kibana Integration:** The seamless integration with Kibana provided an invaluable tool for interactive data exploration, ad-hoc querying, and initial visualization during the development and analysis phases.

In concert, Kubernetes provides the robust platform to host and manage Fission and Elasticsearch. Fission automates the ingestion of data into Elasticsearch, and Elasticsearch, in turn, empowers the rich textual and semantic analysis that forms the core of our project's investigation into Australians' sense of belonging.

### 2.7.2 Choice of Python and Relevant Libraries 
We chose Python as the primary language for data collection because it offers a mature library, PRAW (Python Reddit API Wrapper), which enables us to efficiently extract Reddit posts and comments. Additionally, Python's robust data processing ecosystem allows seamless integration of various sentiment analysis tools, such as Vader and TextBlob, as well as powerful data manipulation libraries like pandas. These tools help us effectively assess the sentiment polarity and intensity expressed in the content and manage the structured data throughout our analysis pipeline.

Given that Vader is particularly well-suited for analysing social media content, we adopted a dual-validation strategy for sentiment analysis—**primarily using Vader, supplemented by TextBlob**—to enhance the reliability and accuracy of our analysis results. 

### 2.7.3 Choice of Java Backend Technologies

Our Java backend was designed for stability and maintainability, not extreme scalability, based on our application’s realistic requirements.

**1. SpringBoot and Offloaded Computation Model**

We adopted **SpringBoot** for its API support and ecosystem integration. All heavy computation (e.g., analytics, aggregations) was offloaded to Elasticsearch, turning the Java service into a **lightweight orchestration** layer. This minimized in-memory state and resource usage, avoiding the need for horizontal scaling.

**2. Simplified Dual-Node Deployment**

We deployed two **identical backend nodes behind a load balancer**, offering basic fault tolerance and high availability. Given the compute load was handled by Elasticsearch, this setup sufficed without auto-scaling complexity.

**3. LangChain4J for AI Integration**

We used **LangChain4J** to simplify AI interaction through:

- Annotation-based prompt engineering

- Automatic response mapping into structured Java objects

- Built-in embedding model support, streamlining our RAG pipeline.

**4. Co.elastic.clients over Low-Level REST**

Access to Elasticsearch was handled primarily via **co.elastic.clients**, offering type-safe query construction and serialization. We retained the low-level REST client for fallback in complex cases.

This hybrid model yielded a **clean, efficient backend**—favoring operational simplicity and reliability over overengineering for scalability.

### 2.7.4 Choice of jupyter notebook and python
Jupyter notebook：
- Interactive Environment
We can write and run code in small code cells, see the output immediately, and make adjustments.
- Rich Types of Text Support
It supports Markdown, LaTeX, and inline visualizations, allowing us to combine code, explanations, and results in one page.

- Visual Feedback
Graphs and charts can be displayed directly below the code, making it easy to understand data and results.

- Easy Sharing
Notebooks can be shared as .ipynb files or converted to HTML/PDF for collaboration.

Python:
- Rich Libraries
Python has powerful visualization libraries like Matplotlib, Seaborn, Plotly, and Folium to meet different visualization needs.
- Integration with Data Analysis Tools
Libraries like Pandas and NumPy can visualize data directly from dataframes or arrays.
- Customizability
Python allows high control of plots, including colors, labels, scales, and styles.

# 3 IMPLEMENTATION DETAILS

## 3.1 Development Environment

OS: Windows (native and WSL 1), macOS, Linux (in our situation, solely for building custom Fission image)

## 3.2 Kubernetes Deployment

### 3.2.0 Computing Nodes

```bash
$ kubectl get nodes -o wide
NAME                                                STATUS   ROLES           AGE   VERSION   INTERNAL-IP      EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION       CONTAINER-RUNTIME
comp90024-k2xetnazupm6-control-plane-ns4hs          Ready    control-plane   18d   v1.31.1   192.168.10.240   <none>        Ubuntu 22.04.5 LTS   5.15.0-126-generic   containerd://1.7.20
comp90024-k2xetnazupm6-default-worker-q48w2-hxv96   Ready    <none>          18d   v1.31.1   192.168.10.139   <none>        Ubuntu 22.04.5 LTS   5.15.0-126-generic   containerd://1.7.20
comp90024-k2xetnazupm6-default-worker-q48w2-kl9bc   Ready    <none>          18d   v1.31.1   192.168.10.254   <none>        Ubuntu 22.04.5 LTS   5.15.0-126-generic   containerd://1.7.20
comp90024-k2xetnazupm6-default-worker-q48w2-lx2ls   Ready    <none>          18d   v1.31.1   192.168.10.137   <none>        Ubuntu 22.04.5 LTS   5.15.0-126-generic   containerd://1.7.20
comp90024-k2xetnazupm6-default-worker-q48w2-zqclm   Ready    <none>          18d   v1.31.1   192.168.10.8     <none>        Ubuntu 22.04.5 LTS   5.15.0-126-generic   containerd://1.7.20
```

* They were set up by UniMelb MRC group.

### 3.2.1 Containerisation of Components

* Same as in the tutorial repo except we deployed our backend on kube.

### 3.2.2 Kubernetes Configurations

* Same as in the tutorial repo except we managed to update our ElasticSearch to `9.0.1`. You can refer to `backend/ElasticSearch Upgrade` folder in our repo for more info.

![image](https://hackmd.io/_uploads/ryj8T4cWel.png)
![image](https://hackmd.io/_uploads/rJ6DpNcbxe.png)
![image](https://hackmd.io/_uploads/ryH9TNc-xl.png)



## 3.3 Fission Function Implementation Details

* Custom image - refer to `backend/fission-custom-images/` for the sources I used to build them:

    * env: cd `environment`
        * Python 3.11 Debian only: `docker build -t anzupop/fission-python-env-3.11-bookworm-slim .`
        * With PyTorch (CPU only package) and `sentence_transformer`: `docker build -f ./Dockerfile_sentence_transformer -t anzupop/fission-python-env-3.11-bookworm-slim:sentence_transformers .`

    * builder: cd `builder`, then `docker build -t anzupop/fission-python-builder-3.11-bookworm-slim .`

    Then push the images. You can find them on Docker Hub:
    * https://hub.docker.com/repository/docker/anzupop/fission-python-env-3.11-bookworm-slim
    * https://hub.docker.com/repository/docker/anzupop/fission-python-builder-3.11-bookworm-slim

* Fission Env:
    ```bash
    fission env create \
      --name python311-bookworm-slim-sentence-transformers \
      --builder anzupop/fission-python-builder-3.11-bookworm-slim \
      --image anzupop/fission-python-env-3.11-bookworm-slim:sentence_transformers
    ```


* Implementation - refer to `backend/harvester/fission/functions/`. Note I included the dependency in `anzupop/fission-python-env-3.11-bookworm-slim:sentence_transformers`

* Fission Pkg:

    ```bash
    fission package create \
      --sourcearchive ./reddit-harvester.zip \
      --env python311-bookworm-slim-sentence-transformers \
      --name reddit-harvester \
      --buildcmd './build.sh'
    ```
    
* Fission Fn:

    ```bash
    fission fn create \
      --name reddit-harvester \
      --pkg reddit-harvester \
      --env python311-bookworm-slim-sentence-transformers \
      --entrypoint "harvester.main"
    ```

* Other Fission settings:

    ```bash
    # create a route for manually testing the function
    fission route create \
      --url /reddit-harvester \
      --function reddit-harvester \
      --name reddit-harvester \
      --createingress
    
    # set timeout to 3000 seconds (50 minutes)
    fission function update \
      --name reddit-harvester \
      --fntimeout 3000
    
    # set a one hour cronjob for the function
    fission timer create \
      --name reddit-harvester-hourly-trigger \
      --function reddit-harvester \
      --cron "0 * * * *"
    ```

More will be discussed in the latter Pros and Cons of Fission.

## 3.4 ElasticSearch Cluster Setup and Configuration

Refer to `backend/ElasticSearch Upgrade` folder in our repo for more info.

Official helm repo supported by Elastic only has manifest up to `8.5.1`, while we need a more recent version for better funcitonality. I have to use the `elastic-operator` provided by them in order to depoly a new one while retaining all our previous configuration.

## 3.5 Harvester Implementation Specifics for Reddit
We use Python Reddit API Wrapper(PRAW) to retrieve posts and comments from Reddit. In order to ensure high data validity, we control data quality directly at the source, instead of fetch all the data then filter and delete it afterward.

We first use the `subreddit.search` method to search for relevant posts in a specified subreddit based on given query keywords. After retrieving the posts, the first step is to filter by locality, keeping only those with a locality name. To achieve this, we parse the geograpic data and build 3 dictionaries:

- ambiguous_locations dictionary: Store the mappings between duplicate locality names and their corresponding states
- location_pids dictionary: Store the mappings between locality names and their corresponding `loc_pid`s
- location_states dictionary: Store the mappings between locality names and their corresponding states

When extracting content from a post, we first check whether the text contains a locality. If it does and the locality is not in the ambiguous_locations dictionary, it means the locality name is unique and can be returned directly. If the locality is in the ambiguous_locations dictionary, we need to determine which state it belongs to based on the context. To do this, we create a keyword dictionary which includes state names and major cities (such as Melbourne, Sydney, etc.). Once we detect any of these keywords in the context, we assign the corresponding state to the locality, using the format `{location}|{state}`. If the specific state cannot be identified, the locality is marked as `{location} (ambiguous location)`.

After completing the locality identification, we filter out all posts marked as `{location} (ambiguous location)`. Next, we perform sentiment analysis on the remaining posts. Using both Vader and TextBlob, we calculate a final sentiment score for each post through a weighted combination of the two methods. Apart from the sentiment score, we also aim to determine a more specific dominant emotion for each post and comment. To identify this, we first match emotion-related keywords using our customised emotion lexicon. Only when no clear keywords are found do we rely on the sentiment score to determine the dominant emotion.

After that, we apply another filter to keep only the posts that contain a `loc_pid`, as only these posts can be displayed. At this point, we have obtained all the valid posts with precise geographic information.

The next step is to extract comments, but only from valid posts. This is because comments on invalid posts are unlikely to have a clearly identifiable geographic information, which makes them less meaningful for analysis.

For comment processing, we first apply a keyword-based filter, then check whether the comment contains a localitiy. If it includes a locality name that can be uniquely mapped to a `loc_pid`, we assign it directly. Otherwise, the comment inherits the locality from its parent post. By default, we assume that comments without an explicit location refer to the geographic area of the associated post.

Once the locality is identified, we perform sentiment analysis on the comments as well, using the same approach as with posts to determine both the sentiment score and dominant emotion.

After analysis, we remove duplicates: posts are deduplicated based on `post_id` and `location`, while comments based on `comment_id` and `location`. We then standardise the data structure of both posts and comments to ensure consistency. Finally, we merge them into a single, well-structured dataset suitable for frontend visualisation.

## 3.6 Backend Implementation

### 3.6.1 Service design
Our service layer implementation embodies several innovative approaches that enabled efficient data processing and analysis:

**Strategic Computation Placement**

Initially, we designed our analysis pipeline following a conventional approach: retrieve data using simple Elasticsearch queries, then perform aggregations and statistical analysis in Java. However, this approach revealed a critical limitation when testing with larger datasets—memory pressure increased dramatically as data volume grew.

This realization led to a fundamental shift in our design philosophy. Instead of retrieving raw data for in-memory processing, we recognized the power of Elasticsearch's aggregation framework and redesigned our service to push computation to where the data resides. This "compute-near-data" approach yielded several advantages:

```java
// Initial approach - processing in Java memory
public List<GeoSentimentDTO> getGeoSentimentAnalysis(String state, TopicCategory category) {
    // Retrieve all comments for state and category
    List<RedditComment> comments = elasticsearchService.searchByStateAndTopic(state, category);
    
    // Group by location and compute averages in Java
    Map<String, List<RedditComment>> commentsByLocation = comments.stream()
            .collect(Collectors.groupingBy(RedditComment::getLocation));
    
    // Process each location group in memory
    return commentsByLocation.entrySet().stream()
            .map(entry -> {
                String location = entry.getKey();
                List<RedditComment> locationComments = entry.getValue();
                
                // Calculate average sentiment score
                double avgSentiment = locationComments.stream()
                        .mapToDouble(c -> c.getSentimentScore())
                        .average()
                        .orElse(0.0);
                
                return GeoSentimentDTO.builder()
                        .location(location)
                        .sentimentScore((float) avgSentiment)
                        .count(locationComments.size())
                        .build();
            })
            .collect(Collectors.toList());
}

// Revised approach - computation pushed to Elasticsearch
@Override
public List<GeoSentimentDTO> getGeoSentimentAnalysis(String state, TopicCategory category) {
    // Use ES aggregation query instead of in-memory analysis
    return elasticsearchService.getGeoSentimentAggregation(state, category);
}
```

This shift significantly improved scalability, allowing our system to handle arbitrarily large datasets without memory concerns. It also reduced network transfer volumes and improved response times.

**Hybrid LangChain4j and Elasticsearch RAG Implementation**

Our most innovative service component is the `HyperAnalysisService`, which implements a Retrieval-Augmented Generation (RAG) pipeline that combines Elasticsearch's vector search capabilities with LangChain4j's AI service pattern:

1. **Vector Generation Strategy**: User queries are transformed into vector embeddings using the BGE-Small-EN model via LangChain4j.
2. **Multi-dimensional Filtering**: The hyper analysis api supports hierarchical geographic constraints (locPid > state > location) and topic-based filtering, combined with semantic similarity.
3. **Structured Output Engineering**: We designed precise system prompts through LangChain4j's annotation system to ensure consistent JSON structure in AI responses(This differs from normal json mode, is picky about models, only openai, Mistral and gemeni meets the req), enabling seamless integration with visualization components:

```java
@SystemMessage("""
You are a professional social media insights analyst for Australia. Your task is to answer user queries based on the retrieved Reddit comments...

Your analysis should be returned as a structured JSON object with these fields:
- sentimentLabel: overall sentiment label related to the query topic (must be exactly one of: "Positive", "Neutral", or "Negative")
- topicPoints: a list of main insights or findings related to the query, each containing:
  * title: brief title for the insight (short phrase)
  * keyPoint: detailed explanation of the insight (1-2 sentences)
  * sentiment: sentiment label for this specific insight (must be exactly one of: "Positive", "Neutral", or "Negative")
- representativeViews: a list of representative viewpoints or statements from the retrieved content that best address the query
""")
@UserMessage("""
User query: {{query}}

Relevant retrieved content:
{{retrievedContents}}

Based on these retrieved comments, please answer the user's query in the structured JSON format described in the system message.
""")
AnalysisAiResult queryInsights(@V("query") String query, @V("retrievedContents") List<String> retrievedContents);
```

4. **Graceful Degradation**: The service implements fallback strategies for scenarios such as empty results, embedding generation failures, or when geographic constraints yield no matches.

**Composite DSL Query Builder Pattern**

For complex queries, we implemented a builder pattern that constructs Elasticsearch DSL queries programmatically. This approach enables dynamic query composition based on user parameters while maintaining type safety:

```java
BoolQuery.Builder boolQuery = new BoolQuery.Builder();

// Add geographic constraint with priority hierarchy
if (locPid != null && !locPid.isBlank()) {
    boolQuery.filter(TermQuery.of(t -> t
            .field("loc_pid")
            .value(locPid)
    )._toQuery());
} else if (state != null && !state.isBlank()) {
    boolQuery.filter(TermQuery.of(t -> t
            .field("state")
            .value(state)
    )._toQuery());
} else if (location != null && !location.isBlank()) {
    boolQuery.filter(MatchQuery.of(m -> m
            .field("location")
            .query(location)
    )._toQuery());
}

// Add topic filter with OR semantics if specified
if (topics != null && !topics.isBlank()) {
    String[] topicArray = topics.split(",");
    BoolQuery.Builder topicBool = new BoolQuery.Builder();
    
    for (String topic : topicArray) {
        TopicCategory category = TopicCategory.fromQueryKey(topic.trim());
        if (category != null) {
            topicBool.should(TermQuery.of(t -> t
                    .field(category.getBooleanField())
                    .value(true)
            )._toQuery());
        }
    }
    
    topicBool.minimumShouldMatch("1");
    boolQuery.filter(topicBool.build()._toQuery());
}
```
### 3.6.2 DSL Design

#### 3.6.2.1 DSL Design for Normal Search
In our implementation, we strategically employed Elasticsearch's powerful DSL to perform complex data aggregations and analyses directly within the search engine rather than in application memory. This approach was critical for efficiently processing large volumes of social media data. Here, we highlight several non-trivial query designs that exemplify our approach:

**Geo-Sentiment Analysis with Multi-level Aggregation**

One of our most sophisticated DSL queries powers the map visualization, producing sentiment analysis by geographic region for specific topics. This query demonstrates the power of nested aggregations:

```json
{
  "size": 0,
  "query": {
    "bool": {
      "must": [
        { "term": { "state": "VIC" } },
        { "term": { "isRental": true } }
      ]
    }
  },
  "aggs": {
    "locations": {
      "terms": {
        "field": "location.keyword",
        "size": 100
      },
      "aggs": {
        "loc_pids": {
          "terms": {
            "field": "loc_pid.keyword",
            "size": 1
          }
        },
        "avg_sentiment": {
          "avg": {
            "field": "sentiment_score"
          }
        },
        "positive_count": {
          "filter": {
            "range": {
              "sentiment_score": { "gt": 0.05 }
            }
          }
        },
        "negative_count": {
          "filter": {
            "range": {
              "sentiment_score": { "lt": -0.05 }
            }
          }
        },
        "neutral_count": {
          "filter": {
            "range": {
              "sentiment_score": { 
                "gte": -0.05,
                "lte": 0.05
              }
            }
          }
        }
      }
    }
  }
}
```

This query simultaneously:
1. Filters data by state and topic (rental discussions in Victoria)
2. Groups results by location
3. Captures the location's PID for map rendering
4. Calculates average sentiment score
5. Counts posts with positive, negative, and neutral sentiment
6. Returns all metrics in a single network request

Without this approach, we would need to retrieve all raw posts, group them in application memory, and perform calculations in Java—leading to significant memory pressure with large datasets.

**Time-Series Sentiment Analysis with Date Histogram**

Another complex query powers our time-series analysis, using Elasticsearch's date histogram aggregation to analyze sentiment trends over time:

```json
{
  "size": 0,
  "query": {
    "bool": {
      "must": [
        { "term": { "state": "NSW" } },
        { "term": { "isWage": true } },
        {
          "range": {
            "@timestamp": {
              "gte": "2023-05-01T00:00:00",
              "lte": "2024-05-01T00:00:00"
            }
          }
        }
      ]
    }
  },
  "aggs": {
    "time_buckets": {
      "date_histogram": {
        "field": "@timestamp",
        "calendar_interval": "month",
        "format": "yyyy-MM"
      },
      "aggs": {
        "avg_sentiment": {
          "avg": {
            "field": "sentiment_score"
          }
        }
      }
    }
  }
}
```

This query:
1. Filters by state, topic, and time range
2. Groups results into monthly buckets
3. Calculates average sentiment per month
4. Returns pre-formatted dates suitable for visualization

The elegant aspect of this solution is how it handles sparse data—months with no data are appropriately represented in the results, simplifying frontend visualization logic.

**Topic Correlation Analysis with Multiple Aggregations**

Perhaps our most analytically valuable query powers the correlation analysis between different topics. This required a two-phase approach:

1. First, gather sentiment data for each topic by location:
```json
{
  "size": 0,
  "query": {
    "bool": {
      "must": [
        { "term": { "state": "VIC" } },
        { "term": { "isRental": true } }
      ]
    }
  },
  "aggs": {
    "locations": {
      "terms": {
        "field": "location.keyword",
        "size": 500
      },
      "aggs": {
        "avg_sentiment": {
          "avg": {
            "field": "sentiment_score"
          }
        }
      }
    }
  }
}
```

2. Then, calculate correlation coefficients in Java for topic pairs using the aggregated data.

This approach represents an optimal balance between Elasticsearch's strengths (aggregation by location) and Java's statistical capabilities (correlation calculation). It prevents both excessive DSL complexity and memory-intensive raw data processing.

Our journey with Elasticsearch DSL involved a learning curve—we initially used simple queries to fetch raw data for Java-side processing, but quickly discovered this approach's limitations with larger datasets. The shift to sophisticated DSL queries that leverage Elasticsearch's aggregation framework was transformative, enabling analyses that would otherwise be computationally prohibitive and highlighting the fundamental difference between typical SQL-based application development and big data analytics architectures.
#### 3.6.2.2 DSL Design for Vector Search

Our implementation of the vector search DSL focused on creating a flexible, performant query structure that effectively combines semantic similarity with traditional filtering capabilities. The design process involved careful consideration of Elasticsearch's KNN capabilities, filter combinations, and query optimization techniques.

##### Core KNN Query Component

The foundation of our DSL is the KNN vector query that performs semantic similarity matching. We designed this component to dynamically adjust based on query requirements:

```json
{
  "knn": {
    "field": "text_vector",
    "query_vector": [0.12, 0.45, ...],
    "k": 50,
    "similarity": 0.3
  }
}
```
Key design decisions in the KNN component include:

- **Field selection**: We store the vector embeddings in a dedicated `text_vector` field to optimize for vector operations
- **Direct k-value application**: We set `k` equal to the requested limit, ensuring we retrieve exactly the number of results needed
- **Similarity threshold**: Implemented a 0.3 minimum similarity threshold to filter irrelevant matches
- **Vector exclusion in response**: We configured source filtering to exclude the vector data from responses, reducing network payload size

##### Hierarchical Filtering Framework

To support geographical and topical constraints, we implemented a sophisticated filtering mechanism with clear priority hierarchy:

```json
{
	"bool": {
		"filter": [
			{
				"match": { "loc_pid": "1gsyd" }
			},
			{
				"bool": {
					"should": [
						{ "term": { "is_rental": true } },
						{ "term": { "is_wage": true } }
					],
					"minimum_should_match": 1
				}
			}
		]
	}
}
```

The filtering framework follows these principles:

- **Geographic filtering priority**: Implemented a cascading approach where `loc_pid` takes precedence over `state`, which takes precedence over `location`
- **Topic filtering with OR semantics**: Utilized the TopicCategory enum to convert user-friendly topic names to the corresponding boolean field names (e.g., "rental" → "is_rental")
- **Dynamic filter construction**: Only relevant filters are included based on available parameters

##### Composite Query Structure

The final DSL integrates the KNN vector query with boolean filters in an optimized structure:

```json
{
  "bool": {
    "filter": [
      {
        "bool": {
          "must": [
            { "match": { "loc_pid": "1gsyd" } },
            {
              "bool": {
                "should": [
                  { "term": { "is_rental": true } },
                  { "term": { "is_wage": true } }
                ],
                "minimum_should_match": 1
              }
            }
          ]
        }
      }
    ],
    "must": {
      "knn": {
        "field": "text_vector",
        "query_vector": [0.12, 0.45, ...],
        "k": 50
      }
    }
  }
}
```

This structure provides several advantages:

- Places the KNN query in the "must" clause to preserve semantic similarity as the primary ranking factor
- Uses the "filter" context for constraints to improve performance by avoiding unnecessary score calculations
- Ensures compatibility with Elasticsearch 8.4+ by properly nesting the filter and KNN queries

##### Performance Optimization Techniques

We incorporated several performance optimization techniques in our DSL:

1. **Source filtering**: Explicitly excluded vector fields from the response to reduce network payload and speed up result processing
   ```json
   "source": {
     "filter": {
       "excludes": ["text_vector"]
     }
   }
   ```
2. **Direct result size limiting**: Applied the client-requested limit directly to both the query size and the KNN k-value
3. **Efficient filter application**: Used match queries for exact field matching and optimized boolean combinations
4. **Field-type specific querying**: Used term queries for boolean fields and match queries for text fields to leverage appropriate indexing

##### Vector Dimension Selection

The choice of vector dimension significantly impacts both search quality and system performance. We conducted systematic experiments with embedding dimensions of 256, 384, 512, and 768 to identify the optimal configuration for our use case.

Our evaluation considered multiple factors:

1. **Semantic Representation Quality**: How effectively the embeddings capture the nuanced meaning of text
2. **Storage Requirements**: How dimension size affects index storage footprint
3. **Query Performance**: Impact on query execution time and computational load
4. **Indexing Efficiency**: Time and resources required for initial indexing

The test methodology involved:

- Creating multiple indices with identical content but different vector dimensions
- Running a standardized set of 100 diverse queries against each index
- Measuring relevance using human-evaluated ground truth judgments
- Recording performance metrics including query time, memory usage, and storage size

Results of dimension testing:

| Dimension | Relative Accuracy | Index Size Increase | Avg Query Time | Memory Usage |
| --------- | ----------------- | ------------------- | -------------- | ------------ |
| 256       | 90%               | Baseline            | 18ms           | Baseline     |
| 384       | 100%              | +50%                | 25ms           | +40%         |
| 512       | 103%              | +100%               | 32ms           | +75%         |
| 768       | 105%              | +200%               | 45ms           | +120%        |

Our analysis revealed several key insights:

- **Diminishing returns at higher dimensions**: Moving from 384 to 768 dimensions provided only a 5% relevance improvement while doubling storage requirements and significantly increasing query latency
- **Sharp improvement threshold**: The jump from 256 to 384 dimensions yielded a substantial 10% relevance improvement, capturing significantly more semantic nuance
- **Practical sweetspot**: 384 dimensions achieved the best balance of semantic quality and resource efficiency

Additionally, we performed qualitative analysis of search results across dimensions:

- 256-dimensional vectors often missed nuanced semantic relationships, particularly for complex queries
- 384-dimensional vectors captured most semantic relationships relevant to our domain
- Higher dimensions (512, 768) occasionally captured very subtle relationships but with minimal practical impact

Based on these comprehensive findings, we selected 384 dimensions as our configuration, providing excellent semantic representation while maintaining reasonable resource requirements.

##### KNN vs Script Score Evaluation

We compared Elasticsearch's two primary vector search approaches: KNN (based on HNSW graphs) and Script Score (exact vector comparisons) through tests with 200 diverse queries:

| Method       | Accuracy(NDCG@10) | Query Time(ms) |
| ------------ | ----------------- | -------------- |
| KNN (HNSW)   | 0.87              | 25             |
| Script Score | 0.91              | 150            |

Script Score achieved a slightly higher accuracy (4.4% advantage) because it performs exhaustive comparisons against all documents, while KNN uses approximate graph traversal. However, manual evaluation of 50 queries showed the practical difference was minimal - 82% had identical top 3 results.

The performance difference was far more significant. KNN delivered a 6x speed advantage that increased with data volume:

| Data Size (documents) | KNN Time (ms) | Script Score Time (ms) | KNN Advantage |
| --------------------- | ------------- | ---------------------- | ------------- |
| 10,000                | 18            | 38                     | 2.1x          |
| 50,000                | 22            | 85                     | 3.9x          |
| 100,000               | 25            | 150                    | 6.0x          |

We ultimately selected KNN despite its slightly lower accuracy because the substantial performance improvement provides a better user experience, while the accuracy trade-off has negligible real-world impact. KNN's logarithmic scaling also ensures the system remains responsive as data volumes grow.

The DSL design described above has proven highly effective in production, delivering semantically relevant results with efficient filtering capabilities while maintaining excellent performance characteristics. This vector search capability forms the foundation of our RAG system's retrieval component, enabling it to find the most contextually appropriate content for the generation phase.


## 3.8 Jupyter Notebook Implementation for Analytics and Visualisation
Retrieving needed data for different visualization modules by interacting with backend interface.

Using data analysis libraries: pandas to process the retrieved data to fit different data structure of multiple visualization effect.

Using visualization libraries:
folium: displaying map graph by using geoJSON data
Matplotlib, Seaborn, Plotly: displaying charts like pie chart, line chart, radar chart and correlation heatmap chart.


## 3.9 Code Repository Structure

They are [here](https://gitlab.unimelb.edu.au/yunpengx/comp90024-2025-sm1-team-7)! (https://gitlab.unimelb.edu.au/yunpengx/comp90024-2025-sm1-team-7)

# 4 SCENARIOS ANALYTICS, AND RESULTS

## 4.1 ANALYTICS 1: Percentage of Post by Topic
### 4.1.1 Description and Goals
In the first section, we use a pie chart to show the proportion of discussion volume for each of the five topics relative to the total. 

The aim is to clearly and intuitively demonstrate the differences in public attention across these topics. 


### 4.1.2 Data Collection Specifics
By interacting with backend interface, retrieving and processing data of all posts volumn of each of five topics within Australia.
Data Structure: 
 ```json
 {
     "General_housing": number of posts,
     "Immigration": number of posts,
     "Rental": number of posts,
     "Wage": number of posts,
     "Mental_health": number of posts
 }
 ```

### 4.1.3 Analytical Methods Applied
Using api of matplotlib.pyplot to display pie chart
### 4.1.4 Results and Visualisations 
![image](https://hackmd.io/_uploads/Sk5Lw4cWlx.png)

### 4.1.5 Interpretation and Discussion of Findings
The pie chart shows the proportion of discussion volume for each of the five topics relative to the total. The result will help reflect the relative impact of each topic on people's living satisfaction — if one topic is more discussed by people, it indicates people are more concerned about that topic in daily life, which means that topic will possibly have stronger influence on living satisfaction of people.
## 4.2 ANALYTICS 2: Topic points and representative views analysis based on questions about these five topics


### 4.2.1 Description and Goals
In the second section, we provide a query module that allows us to explore how Australian people talk about certain question we want to know related to these five topics.

### 4.2.2 Data Collection Specifics
By interacting with backend interface, retrieving and processing data of the key topic points and representative views people talking about the question we type in related to five topics
Data Structure example: 
```
{
  "state": "VIC",
  "locPid": null,
  "location": null,
  "topic": null,
  "query": "how do people regard general housing",
  "sentimentScore": 0.022715051798149942,
  "sentimentLabel": "Neutral",
  "topicPoints": [
    {
      "title": "High-rise apartments as a solution to housing crisis",
      "keyPoint": "Some people view high-rise apartments as a viable solution to the housing crisis due to their ability to accommodate more people in a smaller footprint. However, others may not consider the moral implications of housing availability.",
      "sentiment": "Neutral"
    },
    {
      "title": "Importance of location and views in housing",
      "keyPoint": "Location and views are highly valued by people when considering housing options, often outweighing other factors like the number of bedrooms or bathrooms.",
      "sentiment": "Neutral"
    },
    {
      "title": "Public housing and government intervention",
      "keyPoint": "There is a discussion around the need for government-owned public housing as a solution to housing issues, indicating a divide in opinions on the role of government in housing.",
      "sentiment": "Neutral"
    },
    {
      "title": "Apartment living and community benefits",
      "keyPoint": "Apartment living is seen as a positive choice for many, fostering community links and reducing environmental impacts, although personal preferences vary.",
      "sentiment": "Positive"
    },
    {
      "title": "Challenges in the rental market",
      "keyPoint": "The rental market is highly competitive, with many people facing difficulties in securing a rental without physically viewing the property.",
      "sentiment": "Negative"
    }
  ],
  "representativeViews": [
    "They’re obviously a big part of solving the housing crisis because you can fit many more people since it’s built up and not out.",
    "People value location first, beds/baths/cars second and then the vibe of the place (i.e. whatever the latest trend is).  Nothing else matters except for views which trumps the above, unless they have a specific requirement that can't be easily retrofitted.",
    "To add to this, what is your stance on building proper, government owned public housing, rather just social or affordable?",
    "Apartment living with families is absolutely normal and can foster happy healthy families with close community links. Increased housing density also increases mental health and decreases environmental impacts by eliminating the isolation of suburbs and giving access to a communal social environments and walkable streetscape while decreasing costs of public transport.",
    "Not a single chance of getting a rental without physically viewing it. Zero, nada, bumpkis. Alot of agents won't even consider your offer unless they know you viewed it in person."
  ]
}
```

### 4.2.3 Analytical Methods Applied
Using html, css displaying library integrated with jupyter notebook, showing a dropdown list for selecting certain state, a text-box for typing in certain question and a button for getting results by clicking.
Then comes the result data displaying board, showing result data like mutiple card section.
### 4.2.4 Results and Visualisations 
![image](https://hackmd.io/_uploads/S1zMkV9Wxx.png)

### 4.2.5 Interpretation and Discussion of Findings
We can just type in our questions related to these five topics, then the backend will analyze the question based on real-time data that is the posts people put on social media about this question. The analysis result will show the main topic points about this question and also the representative public views on social media related to the question.

Based on the results, we can clearly and intuitively understand the key topic points and main attitudes in recent public discussions on this question across Australian social media.
## 4.3 ANALYTICS 3: Choropleth Map: The region-based map visualization that uses color gradient to represent data values

### 4.3.1 Description and Goals
The aim of presenting this map is to provide an intuitive overall sense of how satisfied people are with the five topics across different regions. It makes it easy to identify people of which region have relatively higher or lower levels of satisfaction about certain topic.
And we take the regions within Victoria state as an example.

In this section, we aim to show six choropleth maps, the first one shows Victorians' overall Satisfaction/Belonging of all five topics, and the rest five maps respectively shows Victorians' Satisfaction/Belonging of each of the five topics.


### 4.3.2 Data Collection Specifics
By interacting with backend interface, retrieving and processing data of all regions loc_pid and sentiment score within Victoria.
Data Structure: 
```json
[
    {
        "loc_pid":"",
        "sentimentScore":
    }
        ...
]
```
### 4.3.3 Analytical Methods Applied
Searching Australia official website to find GeoJSON of Victoria, then using folium library Choropleth map API to bind these GeoJSON, showing the regions on the map. 

Then retrieve data from backend, and also bind it with Choropleth map to show the final result.
### 4.3.4 Results and Visualisations 
![image](https://hackmd.io/_uploads/Bkh5Z7cbex.png)

![image](https://hackmd.io/_uploads/H1tvW75Zel.png)

![image](https://hackmd.io/_uploads/SyIEZ7q-gg.png)

![image](https://hackmd.io/_uploads/rJ7GZX5Zxx.png)

![image](https://hackmd.io/_uploads/SJS1-Xqblg.png)

![image](https://hackmd.io/_uploads/SJ-3x75-ee.png)
### 4.3.5 Interpretation and Discussion of Findings
This gradient provides with a clear visual understanding of how overall satisfaction of all five topics varies across different regions of Victoria.

The colour bar at the top right of the map represents different levels of satisfaction, and the deeper color indicates higher satisfaction.(Note: Grey color stands for that there is no discussion about the topic within that region). 
## 4.4 ANALYTICS 4: Average Satisfaction/Belonging Score by Topic in Australia

### 4.4.1 Description and Goals
In this section, we display a radar-chart, aiming to illustrate the average satisfaction score of Australian people regarding each topic.

### 4.4.2 Data Collection Specifics
By interacting with backend interface, retrieving and processing data of the average satisfaction of each topic within Australia.
Data Structure: 
```json
{
    "general housing": ,
    "immigration": ,
    "rental housing": ,
    "wage": ,
    "mental health":
}
```

### 4.4.3 Analytical Methods Applied
Using API of matplotlib.pyplot library to show radar chart
### 4.4.4 Results and Visualisations 
![image](https://hackmd.io/_uploads/Bk4AJ7c-gg.png)
### 4.4.5 Interpretation and Discussion of Findings
This will clearly and intuitively illustrate the differences in average satisfaction among these five topics, and which topic people are more satisfactied with.


## 4.5 ANALYTICS 5: Trends of Satisfaction/Belonging Across Five Topics in Australia


### 4.5.1 Description and Goals
We aim to use line-chart to display that, about all these five topics, people's satisfaction changing trend over months. And the time span is the past year starting from current month.

### 4.5.2 Data Collection Specifics
By interacting with backend interface, retrieving and processing data, that is the average satisfaction for each of the five topics in Australia over the past year, broken down by month
Data Structure: 
```json
{
    "General_housing": [satisfaction-score at Y/M, ...],
    "Immigration": [satisfaction-score at Y/M, ...],
    "Rental_housing": [satisfaction-score at Y/M, ...],
    "Wage": [satisfaction-score at Y/M, ...],
    "Mental_health": [satisfaction-score at Y/M, ...]
}
```

### 4.5.3 Analytical Methods Applied
Using api of matplotlib.pyplot to display line chart
### 4.5.4 Results and Visualisations 
![image](https://hackmd.io/_uploads/HJn2JQ5bgx.png)
### 4.5.5 Interpretation and Discussion of Findings
We can clearly see the satisfaction changing trend of each topic in past one year, month by month. Through this, we can find at which time span, the satisfaction of which topic is going up or down.
## 4.6 ANALYTICS 6: Correlation Between the Five Topics as time goes



### 4.6.1 Description and Goals
We display a relation heat-map.
We aim to use it to analyse the correlation between each pair of topics based on people's satisfaction in each month of past year starting from now.

### 4.6.2 Data Collection Specifics
By interacting with backend interface, retrieving and processing data, that is the average satisfaction for each of the five topics in Australia over the past year, broken down by month
Data Structure: 
```json
{
    "General_housing": [satisfaction-score at Y/M, ...],
    "Immigration": [satisfaction-score at Y/M, ...],
    "Rental_housing": [satisfaction-score at Y/M, ...],
    "Wage": [satisfaction-score at Y/M, ...],
    "Mental_health": [satisfaction-score at Y/M, ...]
}
```
Using the same data with line chart to do heat map analysis

### 4.6.3 Analytical Methods Applied
Using api of matplotlib.pyplot to caluculate the correlation number between certain two topics and display line chart
### 4.6.4 Results and Visualisations 
![image](https://hackmd.io/_uploads/By1jJ7q-lx.png)
### 4.6.5 Interpretation and Discussion of Findings
The correlation number is between -1 and 1.
The negative number stands for negative correlation and the positive number stands for positive correlation.
If the absolute value of the correlation number is closer to 1, that means those two topics are more relevant. The result visualisation enables us to easily perceive the correlation between each pair of topics over past year starting from now.

For example, as we can see the correlation number is 0.85 between the two topics: general housing and wage. This number is much close to 1, so that means these two topics are more relevant, if people are more satisfied with their wage, they are also more possibly satisfied with general housing. That is obvious, as normal logic, if people are satisfied with their wage, it indicates they have enough money, so they will be more likely to afford for a general living house.
# 5 SYSTEM EVALUATION AND DISCUSSION
## 5.1 Demonstration of Functionality 

COMP90024_2025_SM1 Assignment 2 Team 7 Video Demo: https://youtu.be/9a3NMc-Bjg8

## 5.2 Scalability of the Application

Our application's architecture, with all core components containerised and deployed on Kubernetes, inherently provides a strong foundation for scalability. Kubernetes offers several mechanisms that allow our system to adapt to varying loads and processing demands:

1.  **Horizontal Pod Autoscaling (HPA):** While not explicitly configured with autoscaling rules for this project's scope, Kubernetes Deployments and StatefulSets (used for our backend API, Jupyter Notebook, and Elasticsearch) are designed to be easily scaled horizontally. By adjusting the `replicas` count for a given Deployment, we can manually increase or decrease the number of running pods to match demand. For example, if the backend API experiences high traffic, the number of its pods can be increased.

2.  **Resource-Based Scaling:** Kubernetes allows for scaling based on resource utilization metrics like CPU and memory. If the metrics-server is enabled, Horizontal Pod Autoscalers can be configured to automatically scale Deployments when these thresholds are met, though manual scaling was the approach for this iteration.

3.  **Node Scalability:** The underlying Kubernetes cluster (provided by the Melbourne Research Cloud) can also be scaled by adding more worker nodes. As new nodes join the cluster, Kubernetes can schedule more pods, increasing the overall capacity of the application.

4.  **Fission Function Scalability:** Fission, running on Kubernetes, manages the scalability of our serverless data harvesting functions. It can scale the number of function instances based on invocation rates or pre-warm instances to handle anticipated load, ensuring that data ingestion can keep pace with new data generation on Reddit. (Note: only if we have enough Reddit API keys /shrug)

5.  **Elasticsearch Scalability:** Elasticsearch itself is a distributed system designed for horizontal scalability. By increasing the number of Elasticsearch pods within our StatefulSet and ensuring proper shard allocation, the data storage and search capabilities can be expanded to handle growing datasets and query loads.

In essence, because our components are managed by Kubernetes, we leverage its native scaling capabilities. This allows for both manual adjustments to resource allocation (by changing replica counts) and provides the framework for implementing more sophisticated, automated autoscaling strategies in future iterations if required. The containerised nature ensures that new instances of any component can be quickly spun up and integrated into the system.

## 5.2.1 Dynamic Scaling of Harvesters/Processing

The architecture of our system is designed to accommodate the dynamic scaling of data harvesters and processing pipelines. As long as any newly introduced harvesters (whether for Reddit or potentially other social media sources in the future) adhere to the established data schema—specifically, by using the same text embedding model to generate compatible `text_vector` fields and populating the agreed-upon index fields in Elasticsearch—they can be seamlessly integrated.

The benefit of our **single Elasticsearch index (`all_content_processed_vectorized_v3`) strategy** becomes particularly apparent here. Because all processed data resides in one index with a consistent structure, we do not need to modify our existing Elasticsearch Domain Specific Language (DSL) queries or backend API logic to incorporate data from new harvesters. New data, regardless of its specific harvester origin (as long as it's processed to the common schema), will automatically become part of the queryable dataset, enhancing the richness of our analysis without requiring downstream application changes. This makes adding new data streams or scaling up existing ones relatively straightforward from a data consumption perspective.

Furthermore, if these new harvesters are deployed as Fission functions or Kubernetes Deployments, they can independently scale based on their specific data source's volume or processing needs, contributing more data to the central Elasticsearch index without directly impacting the performance or scaling of other existing harvesters.

## 5.3 Pros and Cons of Melbourne Research Cloud and Utilised Technologies

### 5.3.1 Experiences with Melbourne Research Cloud (MRC)

Our experience with the Melbourne Research Cloud (MRC) was a valuable learning opportunity, offering both advantages and encountering some operational challenges.

**Pros:**

*   **Realistic Cloud Experience:** Interacting with MRC's OpenStack dashboard and underlying infrastructure provided a tangible feel for managing resources on an IaaS (Infrastructure as a Service) platform, akin to experiences with major enterprise cloud providers. This was instrumental in understanding cloud resource provisioning and management beyond just container orchestration.
*   **Simplified Kubernetes Setup:** MRC offered pre-configured Kubernetes cluster templates and integrations (e.g., with OpenStack Cinder for persistent storage, Octavia for LoadBalancers). This significantly eased the initial cluster setup process, allowing us to focus more quickly on deploying our application rather than on the intricacies of bootstrapping Kubernetes itself.
*   **Accessibility for Research:** Providing such a platform for student projects allows for experimentation with cloud-native technologies that might otherwise be less accessible due to cost or complexity.

**Rants & Challenges:**

*   **Perceived Performance Latency:** At times, we experienced noticeable latency within our Kubernetes cluster operations (e.g., pod scheduling, API responsiveness). This might suggest potential over-provisioning (should be already stated by Rich) of underlying physical resources or contention, which lead to a frustrating user experience when rapid iteration is needed (building images and deploying, ...).
*   **Ephemeral Storage Limitations on Nodes:** A significant challenge was the default ephemeral storage allocated to Kubernetes worker nodes. The initial configuration often proved insufficient, especially when building or pulling larger Docker images (like custom Fission environments with `torch`) or when pods generated substantial logs or temporary data. This led to "out of ephemeral storage" errors, halting deployments and requiring workarounds or cluster reconfiguration. This was a common frustration point noted by multiple teams (references: [Ed Discussion 1](https://edstem.org/au/courses/21070/discussion/2655287), [Ed Discussion 2](https://edstem.org/au/courses/21070/discussion/2661984), [Ed Discussion 3](https://edstem.org/au/courses/21070/discussion/2686471)).

We hope that feedback regarding node resource defaults and perceived performance can contribute to improvements for future students and researchers.

### 5.3.2 Challenges and Benefits of Kubernetes

Kubernetes served as the backbone of our application deployment, offering powerful capabilities alongside a steep learning curve.

**Benefits:**

*   **Robust Orchestration and Reliability:** Once configurations are correctly defined and stable, Kubernetes is exceptionally reliable ("if it works, it works"). It diligently maintains the desired state of the application, handles pod restarts, and manages resource allocation effectively.
*   **Simplified Scaling and Deployment Management:** Kubernetes provides a standardized and powerful way to scale applications up or down by adjusting replica counts. Rolling updates and declarative configurations simplify the deployment and lifecycle management of complex, multi-component applications like ours.
*   **Enhanced Resource Utilization:** By packing containers onto nodes efficiently, Kubernetes can lead to better utilization of underlying compute resources compared to traditional VM-based deployments.
*   **Foundation for Big Data Ecosystem:** For big data analysis, Kubernetes provides a common platform to deploy and manage a wide array of tools. It allows for the co-location of processing engines (like Spark, if we were to use it), data stores (like Elasticsearch), and serving layers, facilitating efficient data pipelines and communication between components. Its ability to manage stateful applications (like Elasticsearch via StatefulSets) is crucial for persistent data storage.

**Challenges:**

*   **Steep Learning Curve and Debugging Complexity:** Similar to complex systems like C++, when issues arise in Kubernetes, debugging can be incredibly challenging ("if it doesn't work, you will have a really hard time debugging"). Understanding the interplay between pods, services, deployments, networking, storage, and RBAC requires significant effort. Troubleshooting often involves inspecting logs from multiple components, `describe` outputs, and events.
*   **Configuration Verbosity:** Kubernetes YAML manifests can be verbose and complex. Managing these configurations, especially for multiple environments or applications, can become cumbersome without additional tooling (like Helm, Kustomize, though not extensively used in this project's initial phase).
*   **Networking Intricacies:** While powerful, Kubernetes networking (CNI plugins, Services, Ingress, NetworkPolicies) can be difficult to grasp initially and troubleshoot when connectivity issues occur between pods or external access fails.
*   **Resource Overhead:** Kubernetes itself introduces some resource overhead for its control plane components and agents on worker nodes. For very small applications, this might seem disproportionate, though for our application's scale, the benefits outweighed this.

### 5.3.3 Challenges and Benefits of Fission

Fission offered a convenient way to deploy our serverless data harvester.

**Pros:**

*   **"Enterprise Grade" FaaS on Kubernetes:** Fission provides a Function-as-a-Service experience directly on top of an existing Kubernetes cluster, allowing us to leverage our existing infrastructure and knowledge for serverless workloads. This avoids vendor lock-in to a specific cloud provider's FaaS offering.
*   **Simplified Serverless Deployment:** Once the environment is set up, deploying and managing functions with triggers (like our hourly timer) is relatively straightforward.
*   **Scalability for Event-Driven Tasks:** Fission is designed to scale function instances based on demand, which is ideal for event-driven tasks like our periodic data harvesting.

**Cons:**

* **Limited Base Image Support & Outdated Versions:** The default Python environment provided by Fission was Alpine-based and ran an older Python version. This necessitated building a custom environment image to include `torch` (due to `musl libc` incompatibility) and use a more current Python version, which added setup time and complexity. More diverse and up-to-date official environments would be beneficial.

*   **Occasional "Mysterious" Errors:** During development, we encountered some opaque errors that were difficult to diagnose immediately:
    * `io timeout` errors when attempting to build or update Fission packages, potentially related to internal Fission component communication error (later identified that is related with the ephemeral storage) 

      ![](https://hackmd.io/_uploads/BJVoGNcZle.png)
    
    * Errors like `could not find "srcPkgPath"` when creating new packages, which sometimes required several attempts or minor configuration changes to resolve.  
    
      ![](https://hackmd.io/_uploads/r1QhM4cbeg.png)
    
    * `os.cwd` is not the same as we'd expected, causing failure in loading the libraries for installed packages and files, thus error: ![](https://hackmd.io/_uploads/BJDEmE5bgx.png)
    
    * Strange error in installing packages: ![](https://hackmd.io/_uploads/rJCvZS9bxe.png)



*   **Maturity and Community Support:** Compared to some cloud provider FaaS offerings or more established serverless frameworks, the Fission community might be smaller, making it slightly harder to find solutions to niche problems.

### 5.3.4 Challenges and Benefits of Elasticsearch

Elasticsearch was pivotal for our data storage, search, and analytical capabilities.

**Benefits:**

*   **"You Know, For Search!" (and much more):** Elasticsearch excels at full-text search, which was fundamental for querying Reddit posts and comments. Its powerful query DSL allows for complex searches, filtering, and ranking.
*   **Industry Standard for Big Data Text Analytics:** It's a de facto standard for indexing, searching, and analysing large volumes of textual and semi-structured data. It handles sharding and data distribution across nodes automatically, simplifying the management of large datasets.
*   **Rich Analytical Capabilities:** Beyond search, Elasticsearch offers a powerful aggregation framework, allowing us to perform complex data analysis directly within the database (e.g., calculating sentiment distributions per location, identifying top keywords, time-series analysis). This was crucial for generating insights for our Jupyter Notebook visualisations.
*   **Vector Search (KNN):** Native support for `dense_vector` fields and k-Nearest Neighbor (KNN) search was critical for our "sense of belonging" analysis, enabling semantic similarity searches beyond keyword matching.
*   **Scalability and Resilience:** Designed to be distributed, Elasticsearch can scale horizontally by adding more nodes to the cluster, and its replication mechanism provides data redundancy and high availability.

**Rants & Challenges:**

*   **Licensing Changes and Deployment Restrictions:** Elastic's move towards the Elastic License and SSPL has introduced complexities. For instance, official Helm charts for newer versions are managed by Elastic and may have restrictions or require subscriptions for certain features, making purely open-source deployments slightly more involved than in the past.
*   **Resource Intensity:** Elasticsearch can be relatively resource-heavy, particularly in terms of memory (heap space) and disk I/O, especially with large datasets and complex indexing/querying loads. Proper capacity planning and resource allocation are crucial.
*   **Complexity for Advanced Operations:** While basic setup and usage are straightforward, advanced cluster management, performance tuning, and complex query optimization can require significant expertise.

# 6 Fault Tolerance and Error Handling

## 6.1 Challenges in Data Collection and Processing
### 6.1.1 Geographic Data Limitations
- **Empty GeoJSON dataset for Australian Capital Territory (ACT)**

To ensure the reliablity of data visualisation, we downloaded the data from **data.gov.au** and used the `loc_pid` in the dataset to bind and diplay each locality. However, when attempting to download data for Australian Capital Territory (ACT, "https://data.gov.au/geoserver/act-suburb-locality-boundaries-geoscape-administrative-boundaries/wfs"), we encountered an error on the official website. As a result, we are currently unable to access the dataset to display the data related with ACT.

- **Missing loc_pid for certain localities**

We successfully downlaoded the datasets for the other states. However, during the processing of geographic data, we discovered that a significant number of localities were missing their corresponding `loc_pid`. As a result, when posts or comments containing these localities were captured, we are unable to mark their correct locations on the map accurately. Unfortunately, we cannot completely resolve this issue. Therefore, we treat any post or comment with a missing `loc_pid` as invalid and exclude it from our analysis to avoid erroneous data.

- **Misidentification due to locality names conflicting with common words (e.g., "Price" being both a place name and a common word)**

After removing localities without `loc_pid`, we encountered a new challenge - some locatlity names overlap with common English words. Our location detection approach involves matching the entire text against each locality name in our locality dictionary. If a match is found, the location is recorded. However, since this matching is done word by word, common words such as "price" can be mistakenly identified as geographic locations. Although "price" is indeed a valid Australian locality, it is also frequently used word in general English. As a result, any occurance of "price" in a post or comment would be incorrectly tagged as a locality, which introduces noise into dataset.

Currently, our approach to location detection is based on word-by-word matching. Without access to full contextual information, it is difficult to accurately distinguish between common words and actual locality names. For example, we can only detect whether the word "price" appears in the text, but we are unable to determine whether it refers to the cost of something or to the Australian locality named "price".

We have attempted to incorporate large language models (LLMs) to perform contect-aware semantic analysis on each post and comment. However, during practical testing, we found that calling LLM APIs for each post and comment introduces substantial time costs, especially under conditions of high data volume. In one test using a small subset of data, the analysis was still incomplete even after running overnight.

Such delays are unacceptable for our project. No one wants to view belongingness / satisfaction data already several days old. This becomes even more critical during major events, as users actively engage with the platform and anticipate timely belongingness / satisfaction insights. Under such circumstances, introducing large language models would lead to significant processing delays due to the surge in data volume, making it difficult to meet real-time performance requirements. Therefore, this limitation cannot be resolved currently. We still adopt the word-by-word matching approach to handle the data.

- **Duplicate locality names across different states (e.g., "Richmond" existing in multiple states)**

Another common issue we encountered was the duplicate locality names across different states. For example, "Richmond" exists in multiple states. Although we attempted to use contextual information to infer which state a given locality belongs to, in many cases the context was insufficient for reliable determination. To maintain data quality and avoid anbiguity, we adopted a conservative approach: we first perform a round of contextual geographic keyword matching, if no match is found, the corresponding record is then discarded.

- **Multiple `loc_pid` assigned to the same locality within a single state**

In some cases, the same locality within a single state was assigned multiple `loc_pid`s. This created uncertainty in location mapping. While it could potentially indicate the existence of multiple same-named localities within a state, we considered it more likely to be a data annotation error. Due to this ambiguity, we implemented a simplified approach by selecting the first `loc_pid` in such cases. This might have slightly reduced the accuracy of our geographic visualisation. However, since the data is extracted from the government website - which is considered the most reliable - we are unable to modify the original dataset. Therefore, this limitation cannot be resolved currently.

### 6.1.2 Reddit Content Mining Limitations

Our efforts to mine relevant content from Reddit were subject to several limitations, stemming from both the manual nature of identifying relevant communities and keywords, and inherent constraints within the Reddit API (accessed via PRAW).

*   **Incomplete Subreddit and Keyword Coverage:**
    *   The initial identification of target subreddits for data extraction was a manual process. We primarily searched for and selected subreddits with obvious connections to Australia or our topics of interest (housing, salary, mental health, immigration). This approach inevitably led to the omission of potentially relevant but less discoverable or niche subreddits, thus impacting the overall comprehensiveness of our dataset.
    *   Similarly, the query keywords used with the `subreddit.search` method were manually curated based on our domain understanding and preliminary observations. This list, while targeted, is inherently subjective and may not capture all a_nuances or alternative phrasings_ used by Australians when discussing topics related to their sense of belonging.

*   **Reddit API (PRAW) Querying and Data Retrieval Constraints:** Beyond the challenges of identifying sources, the Reddit API itself imposed several limitations on how effectively and efficiently we could retrieve data:
    
    1.  **Lack of Time-Window Filtering:** The API does not offer a direct way to filter search results by a precise start and end date/time. This made it difficult to target historical data for specific periods without retrieving broader sets and then filtering them, or relying on less exact time-based sorting options.
    2.  **Search-Based Retrieval vs. Streaming:** Data collection primarily relied on search functionalities. The API is not optimized for continuous, real-time streaming of all new content related to our broad keywords across multiple subreddits, which would require frequent and intensive polling.
    3.  **Limited Complex Query Grammar:** We found that the API's search query grammar had limitations when attempting to construct highly complex queries combining multiple keywords (e.g., using sophisticated AND/OR logic) or targeting many subreddits simultaneously within a single request. This often led to less predictable or incomplete result sets.
    4.  **Hard-Coded Result Limit:** Each distinct API search query is subject to an upper limit on the number of results returned (typically around 1000). Retrieving all matching content beyond this threshold required paginating through results or, more practically for our keyword-driven approach, executing many distinct, narrower queries.
    
    These API constraints, combined with our need for broad keyword and subreddit coverage, necessitated a more laborious data harvesting strategy. We had to **systematically iterate through each predefined keyword for each targeted subreddit individually**. Furthermore, the lack of precise time-windowing and this iterative collection method meant we couldn't inherently guarantee that content retrieved in one pass wasn't already collected in another. This mandated the implementation of **`upsert` logic within our harvester when interacting with Elasticsearch**, ensuring data integrity by checking for existing `unique_id`s before insertion or update. This iterative approach, along with the constant need for duplicate checks, inevitably increased the development time, computational resources consumed during harvesting, and the overall load placed on the Reddit API. Despite these hurdles, this methodical process enabled us to amass a substantial dataset of **791k documents** (posts and comments combined) for our analysis.

### 6.1.3 Sentiment Analysis Limitations
- **Difficulties in recognising Australian slang**

When processing sentiment, we were aware that many emotions are often expressed through slang, and the sentiment conveyed by slang often depends on the context. However, since no one in our team has expertise in this area, we decided not to include slang in our analysis, even though this may lead to some emotional content in posts or comments being missed. We were concerned that incorporating a slang lexicon we didn't fully understand could introduce inaccuracies into our analysis. To prioritise the overall reliablity of our data, we chose to exclude these elements instead. We believe that if we have enough time to study Australian slang, we would be able to effectively analyse the emotions expressed though slang in each post and comment.

- **Challenges in detecting irony (misclassifying statements like "I really love these rental prices")**

During our sentiment analysis, we identified a major challenge: detecting irony in posts and comments. For example, the sentence "I really love these rental prices" appears to express a postive sentiment on the surface, as if praising the afforability of the rent. However, in reality, it often conveys a strong sense of dissatisfaction.
Our current approach is to adjust the sentiment label when there is a mismatch between the detected sentiment word and the sentiment score. However, when the sentiment score itself is misjudged due to irony, we are unable to identify the true sentiment. At present, the only potential solution we have considered is using large language models to analyse the context. However, since using LLMs during our locality analysis led to significant delays, we were unable to maintain real-time data updates. Therefore, we decided to continue with our previous approach. This limitation cannot be completely resolved.

- **Subjectivity in weight allocation (70% vader, 30% textblob)**

To improve the accuracy and reliability of the sentiment score, we employed both Vader and TextBlob for dual sentiment analysis. Since Vader is specifically designed for social media texts (as mentioned in the README file of the vaderSentiment Github repository: https://github.com/cjhutto/vaderSentiment/tree/master), we assigned it a higher weight. However, due to the lack of quantitative evidence on the performance of these two tools specifically for Reddit posts and comments, the allocation of weights is constrained and cannot be precisely or objectively defined. This limitation remains unresolved at present, the weights were assigned based on qualitative judgement. We believe that if we have enough time to compute extensive data, we will be able to determine the most appropriate weight allocation.

- **Subjectivity and limitations in emotion classification criteria**

In our sentiment analysis, we aimed not only to determine the overall sentiment polarity (positive, neutral, and negative), but also to identify more specific emotional states. However, since human emotions are diverse and often lack clear boundaries, we had to rely on our own judgement to simplify emotions into 6 categories: anger, fear, sadness, joy, surprise, and neutral. As a result, our sentiment classification is subject, and there is currently no better solutions to resolve this limitation.

To identify specific emotions, we adopted a keyword-matching approach. We manually created a dictionary of commonly used emotion words and determined the dominant emotion based on the number of matched words for each emotion. Since the dictionary is entirely based on our experience, its coverage is limited. It also fails to capture more subtle expressions, such as slang. This limitation cannot be resolved currently.

For texts lacking clear emotional keywords, we relied on sentiment score to infer the emotion category. However, there is no universal standard defining which sentiment score ranges correspond to which emotion. All the thresholds were set according to our own judgement. This limitation also cannot be resolved currently. Similarly, if we have enough time to train our own model, we are confident that we can identify the optimal emotion categories as well as their relationship with sentiment scores.


## 6.2 Front-end Challenges
### 6.2.1 Difficult to find GeoJSON Data
As our intention is to display sections with mulitiple colors based on different satisfaction score, we must have a detailed GeoJSON Data covering all offical legal regions, however these data are hard to find even at the official website. Finally we successfully find an outdated but luckily useful official GeoJSON data.
### 6.2.2 Time-consuming Map Rendering
As we need to display and render six maps with the data within all states and regions in Australia. The time needed to load and render one map is already too long, not to mention here are six maps. After careful consideration that there is no need to display all states using extremely large volumn of data, as these map just provides visual sense at a macro level, so we decide to just display map with data of one state, Victoria, as a demonstration sample rather than display all states data in Australia.
This is a trade-off between the final visual effect and the time it takes to load and display the data.

# 7 TEAM ROLES
### Student Name: Zifei Li (Student ID: 1638553)

- Defined the project topic and designed the overall system architecture, including data acquisition method, data processing strategy, and data presentation approaches.
- Set up key services on Kubernetes clusters, including Fission, ElasticSearch, Kibana, and Jupyter Hub.
- Designed and implemented a Reddit data collection pipeline using PRAW to extract posts and comments based on specified keywords.
- Refined downloaded geographic data by extracting key location information (e.g., locality, state, and loc_pid).
- Created dictionaries mapping locality to state, locality to loc_pid, and ambiguous locality to possible states and applied them to ensure only posts with clearly identifiable localities were retained for analysis.
- Applied dual-layer sentiment analysis (Vader + TextBlob) to assess sentiment scores and dominant emotions in posts and comments.
- Performed data deduplication and standardised data structure of posts and comments to better support locality-based belonging representation.

### Student Name: Yunpeng Xiong (Student ID: 1513076)

- Help define the initial project topic.
- Responsible for designing and documenting our **Overall System Architecture**, including creating the high-level system diagram illustrating component interactions and data flow.
- Manage and maintain the cloud infrastructure, solves cloud related problems like how to upgrade our ElasticSearch to a newer version.
- Designed and implemented the **automated data ingestion pipeline using Fission** for serverless execution of data harvesting scripts.
- Engineered the solution for Fission environment limitations by **building and deploying a custom Docker image** that included necessary dependencies like `torch` (which was incompatible with the default Alpine-based Fission environment).
- Configured Fission **timer triggers** for hourly automated data harvesting from Reddit.
- Managed the pre-processing of harvested data, including the generation of `unique_id`.
- Led the design and implementation of the **data storage strategy in Elasticsearch**.

### Student Name: Tianyun Lei (Student ID: 1454701)

- Help define the project topic.
- Implemented the DSL structure for normal DSL search query and vector DSL search query.
- Architected the natural language query logic that forms the foundation of our RAG system, including the vector embedding process using Sentence Transformers with 384-dimensional vectors and the retrieval strategy that balances semantic relevance with filtering constraints.
- Provided technical guidance on Elasticsearch optimization, recommending KNN over Script Score for vector search based on comparative testing, and resolved indexing challenges by implementing appropriate field mappings and analyzer configurations for text fields.

### Student Name: Yongchun Li (Student ID: 1378156)
- led & architected the SpringBoot backend design and implementation.
- Designed and implemented the ElasticsearchService with hybrid query interfaces, balancing type-safe API with native DSL operations
- Adapted data entity & analysis pipeline to accommodate evolving data formats across multiple harvesting iterations
- Engineered the DSL query, offloading complex aggregations to Elasticsearch while maintaining lightweight backend services. Designed and built robust DSL query templates for geospatial sentiment analysis, time-series trend detection, and topic correlation analysis
- Co-implemented the LangChain4j-powered RAG system with structured output engineering for analytical insights
- In early project phases, conducted Mastodon data harvesting experiments to evaluate its viability as a data source. Developed semantic entity location extraction prototypes and evaluated the feasibility of NLP-based geographic attribution, implemented early sentiment quantification framework. Researched and prototyped incremental data processing solutions to optimize harvesting efficiency

### Student Name: Haowen Zhang (Student ID: 1635503)
- Help define the project topic.
- Define the visualization theme of front-end. Not only using normal charts to display retrieved data, but also provides choropleth map to display data for a macro-level view. What's more, an interactive visualization module is embedded, that is a query type box used to get data analysis results based on the typed-in query, helping better achieving our project's goal.
- Complete the front-end coding with jupyter notebook. Taking plenty of time learning different libraries for visualization and select optimal ones to do the visualization work.
- Define the data structure needed for visualization. This is necessary for backend to decide how to process data and develop data interactive interface.
