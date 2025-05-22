# COMP90024_2025_SM1 Assignment 2 - Team 7

Zifei Li 1638553
Yunpeng Xiong 1513076
Tianyun Lei 1454701
Yongchun Li 1378156
Haowen Zhang 1635503

## Overview

This assignment is a web application that allows users to analyze social media data using natural language processing and machine learning techniques. The application provides a user-friendly interface for exploring and understanding social media conversations, and for conducting sentiment analysis on specific topics or keywords.

## Repo Structure

The repo is structured as follows:

- `backend/`: Contains the backend code and other related files for the application.
- `frontend/`: Contains the frontend code (notebook) for the application.
- `test/`: Contains the test code for the application.
- `data/`: Contains the sample data for the application.
- `database/`: contains our Elasticsearch queries and index mappings.
- `docs/`: contains our report.

There's no other docs apart from report in `docs/` as we would give everything in the report and in README.md under each folder.

## Deployment

0. Complete tutorial setup in GitLab
1. Deploy Jupyter Hub (Optional)
2. Upgrade Elasticsearch to 9.x, refer to `ElasticSearch Upgrade` in `backend/`. Becare: Elasticsearch might have different credentials with ours if you setup your own. Be sure to change the credentials in `backend/T7BE/src/main/resources/application.properties` and `backend/T7BE/src/main/resources/application-prod.properties` and `backend/harvesters/fission/functions/reddit-harvester/harvester.py`.
3. Build the Fission environment, refer to our report. You would want to refer to `fission-custom-images` in `backend/` for the custom images' Dockerfiles.
4. Run the Fission function (or set the time trigger) to load the data.
5. Deploy the backend API.
6. Run the integration test. (Optional)
7. Start Jupyter Hub or use the notebook in `frontend/` to interact with the deployed backend API. Besure to setup the correct backend API endpoint in the notebook - it default to the endpoint on remote kube cluster.
