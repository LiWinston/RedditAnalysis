import unittest
import requests
import json
import math
import re
from typing import Dict, List, Any

class BackendAPIIntegrationTest(unittest.TestCase):
    """Integration tests for the T7BE Backend API."""
    
    # Base URL for the backend API
    BASE_URL = "http://localhost:8080"
    
    def setUp(self):
        """Set up test fixtures before test execution."""
        # Test if the server is reachable
        try:
            response = requests.get(f"{self.BASE_URL}/actuator/health")
            if response.status_code != 200:
                self.skipTest("Backend server is not available or not healthy")
        except requests.exceptions.RequestException:
            self.skipTest("Backend server is not reachable")
    
    def test_comments_by_location_format(self):
        """Test retrieving comments by location."""
        location = "Melbourne"
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/comments/location/{location}",
            params={"page": 1, "size": 5}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("totalCount", data)
        self.assertIn("totalPages", data)
        
    def test_comments_by_state_format(self):
        """Test retrieving comments by state."""
        state = "VIC"
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/comments/state/{state}",
            params={"page": 1, "size": 5}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("totalCount", data)
        self.assertIn("totalPages", data)
        
    def test_comments_by_emotion_format(self):
        """Test retrieving comments by emotion type."""
        emotion_type = "positive"
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/comments/emotion/{emotion_type}",
            params={"page": 1, "size": 5}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("totalCount", data)
        self.assertIn("totalPages", data)
        
    def test_map_data_format(self):
        """Test retrieving map data for a state."""
        state = "VIC"
        response = requests.get(f"{self.BASE_URL}/api/analysis/map/{state}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("location", data[0])
            self.assertIn("sentimentScore", data[0])
            self.assertIn("locPid", data[0])
            
    def test_map_data_with_category_format(self):
        """Test retrieving map data for a state with specific category."""
        state = "VIC"
        category = "rental"
        response = requests.get(f"{self.BASE_URL}/api/analysis/map/{state}/{category}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("location", data[0])
            self.assertIn("sentimentScore", data[0])
            self.assertIn("locPid", data[0])
            
    def test_pie_chart_data_format(self):
        """Test retrieving pie chart data for a state."""
        state = "VIC"
        response = requests.get(f"{self.BASE_URL}/api/analysis/pie/{state}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("topicCategory", data[0])
            self.assertIn("postCount", data[0])
            
    def test_radar_chart_data_format(self):
        """Test retrieving radar chart data for a state."""
        state = "VIC"
        response = requests.get(f"{self.BASE_URL}/api/analysis/radar/{state}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        # Check that the response contains at least one entry
        self.assertTrue(len(data) > 0)
            
    def test_line_chart_data_format(self):
        """Test retrieving line chart data for a state and category."""
        state = "VIC"
        category = "rental"
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/line/{state}/{category}",
            params={"monthCount": 6}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("timePoint", data[0])
            self.assertIn("averageSentiment", data[0])
            
    def test_heatmap_data_format(self):
        """Test retrieving heatmap data for a state."""
        state = "VIC"
        response = requests.get(f"{self.BASE_URL}/api/analysis/heatmap/{state}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("topicA", data[0])
            self.assertIn("topicB", data[0])
            self.assertIn("correlationCoefficient", data[0])
            
    def test_local_hot_topics_format(self):
        """Test retrieving local hot topics analysis."""
        loc_pid = "2GMEL"  # Melbourne location ID
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/hyper/local-hot-topics",
            params={"locPid": loc_pid, "limit": 5}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("locPid", data)
        self.assertIn("sentimentScore", data)
        self.assertIn("representativeViews", data)
        
    def test_topic_discussion_format(self):
        """Test retrieving topic discussion analysis."""
        loc_pid = "2GMEL"  # Melbourne location ID
        topic = "rental"
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/hyper/topic-discussion",
            params={"locPid": loc_pid, "topic": topic, "limit": 5}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("locPid", data)
        self.assertIn("topic", data)
        self.assertIn("representativeViews", data)
        
    def test_query_insights_format(self):
        """Test the natural language query insights API."""
        payload = {
            "query": "What are people saying about rental prices in Melbourne?",
            "locPid": "2GMEL",
            "topics": "rental",
            "limit": 5
        }
        response = requests.post(
            f"{self.BASE_URL}/api/analysis/hyper/query-insights",
            json=payload
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("query", data)
        self.assertIn("sentimentScore", data)
        self.assertIn("representativeViews", data)
        
    def test_basic_comments_endpoints_format(self):
        """Test the basic data access endpoints for comments."""
        # Test location endpoint
        location = "Melbourne"
        response = requests.get(f"{self.BASE_URL}/api/comments/location/{location}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        
        # Test state endpoint
        state = "VIC"
        response = requests.get(f"{self.BASE_URL}/api/comments/state/{state}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        
        # Test emotion endpoint
        emotion = "positive"
        response = requests.get(f"{self.BASE_URL}/api/comments/emotion/{emotion}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_comments_by_location(self):
        """Test retrieving comments by location."""
        location = "Melbourne"
        page_size = 5
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/comments/location/{location}",
            params={"page": 1, "size": page_size}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check basic structure
        self.assertIn("data", data)
        self.assertIn("totalCount", data)
        self.assertIn("totalPages", data)
        self.assertIn("currentPage", data)
        self.assertIn("pageSize", data)
        
        # Check data types
        self.assertIsInstance(data["data"], list)
        self.assertIsInstance(data["totalCount"], int)
        self.assertIsInstance(data["totalPages"], int)
        self.assertIsInstance(data["currentPage"], int)
        self.assertIsInstance(data["pageSize"], int)
        
        # Check values
        self.assertEqual(data["pageSize"], page_size)
        self.assertEqual(data["currentPage"], 1)
        
        # Check pagination math
        if data["totalCount"] > 0:
            self.assertEqual(data["totalPages"], math.ceil(data["totalCount"] / data["pageSize"]))
        else:
            self.assertEqual(data["totalPages"], 0)
        
        # Check item structure if data exists
        if data["data"]:
            item = data["data"][0]
            self.assertIn("firstLocation", item)
            self.assertIn("firstState", item)
            self.assertIn("firstSentimentScore", item)
            self.assertIn("text", item)
            
            # Verify sentiment score is in valid range
            self.assertTrue(-1.0 <= item["firstSentimentScore"] <= 1.0)
        
    def test_comments_by_state(self):
        """Test retrieving comments by state."""
        state = "VIC"
        page_size = 5
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/comments/state/{state}",
            params={"page": 1, "size": page_size}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check basic structure
        self.assertIn("data", data)
        self.assertIn("totalCount", data)
        self.assertIn("totalPages", data)
        self.assertIn("currentPage", data)
        self.assertIn("pageSize", data)
        
        # Check data types
        self.assertIsInstance(data["data"], list)
        self.assertIsInstance(data["totalCount"], int)
        self.assertIsInstance(data["totalPages"], int)
        self.assertIsInstance(data["currentPage"], int)
        self.assertIsInstance(data["pageSize"], int)
        
        # Check values
        self.assertEqual(data["pageSize"], page_size)
        self.assertEqual(data["currentPage"], 1)
        
        # Check pagination math
        if data["totalCount"] > 0:
            self.assertEqual(data["totalPages"], math.ceil(data["totalCount"] / data["pageSize"]))
        else:
            self.assertEqual(data["totalPages"], 0)
        
        # Check item structure if data exists
        if data["data"]:
            item = data["data"][0]
            self.assertIn("firstState", item)
            self.assertEqual(item["firstState"], state)
        
    def test_comments_by_emotion(self):
        """Test retrieving comments by emotion type."""
        emotion_type = "positive"
        page_size = 5
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/comments/emotion/{emotion_type}",
            params={"page": 1, "size": page_size}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check basic structure
        self.assertIn("data", data)
        self.assertIn("totalCount", data)
        self.assertIn("totalPages", data)
        self.assertIn("currentPage", data)
        self.assertIn("pageSize", data)
        
        # Check data types
        self.assertIsInstance(data["data"], list)
        self.assertIsInstance(data["totalCount"], int)
        self.assertIsInstance(data["totalPages"], int)
        self.assertIsInstance(data["currentPage"], int)
        self.assertIsInstance(data["pageSize"], int)
        
        # Check values
        self.assertEqual(data["pageSize"], page_size)
        self.assertEqual(data["currentPage"], 1)
        
        # Check pagination math
        if data["totalCount"] > 0:
            self.assertEqual(data["totalPages"], math.ceil(data["totalCount"] / data["pageSize"]))
        else:
            self.assertEqual(data["totalPages"], 0)
        
    def test_map_data(self):
        """Test retrieving map data for a state."""
        state = "VIC"
        response = requests.get(f"{self.BASE_URL}/api/analysis/map/{state}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        if data:
            item = data[0]
            self.assertIn("location", item)
            self.assertIn("sentimentScore", item)
            self.assertIn("locPid", item)
            self.assertIn("postCount", item)
            self.assertIn("positiveRatio", item)
            self.assertIn("negativeRatio", item)
            self.assertIn("neutralRatio", item)
            
            # Check data types
            self.assertIsInstance(item["location"], str)
            self.assertIsInstance(item["sentimentScore"], float)
            self.assertIsInstance(item["locPid"], str)
            self.assertIsInstance(item["postCount"], int)
            self.assertIsInstance(item["positiveRatio"], float)
            self.assertIsInstance(item["negativeRatio"], float)
            self.assertIsInstance(item["neutralRatio"], float)
            
            # Verify sentimentScore is in valid range
            self.assertTrue(-1.0 <= item["sentimentScore"] <= 1.0)
            
            # Verify postCount is non-negative
            self.assertGreaterEqual(item["postCount"], 0)
            
            # Verify ratio values are between 0 and 1
            self.assertTrue(0.0 <= item["positiveRatio"] <= 1.0)
            self.assertTrue(0.0 <= item["negativeRatio"] <= 1.0)
            self.assertTrue(0.0 <= item["neutralRatio"] <= 1.0)
            
            # Verify ratio sum is approximately 1.0 (allowing for floating point imprecision)
            ratio_sum = item["positiveRatio"] + item["negativeRatio"] + item["neutralRatio"]
            self.assertAlmostEqual(ratio_sum, 1.0, delta=0.01)
            
    def test_map_data_with_category(self):
        """Test retrieving map data for a state with specific category."""
        state = "VIC"
        category = "rental"
        response = requests.get(f"{self.BASE_URL}/api/analysis/map/{state}/{category}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        if data:
            item = data[0]
            self.assertIn("location", item)
            self.assertIn("sentimentScore", item)
            self.assertIn("locPid", item)
            self.assertIn("topicCategory", item)
            
            # Verify category in response matches requested category
            self.assertEqual(item["topicCategory"].lower(), category.lower())
            
    def test_pie_chart_data(self):
        """Test retrieving pie chart data for a state."""
        state = "VIC"
        response = requests.get(f"{self.BASE_URL}/api/analysis/pie/{state}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        if data:
            # Check data structure
            item = data[0]
            self.assertIn("topicCategory", item)
            self.assertIn("postCount", item)
            self.assertIn("percentage", item)
            self.assertIn("averageSentiment", item)
            
            # Check data types
            self.assertIsInstance(item["topicCategory"], str)
            self.assertIsInstance(item["postCount"], int)
            self.assertIsInstance(item["percentage"], float)
            self.assertIsInstance(item["averageSentiment"], float)
            
            # Verify postCount is non-negative
            self.assertGreaterEqual(item["postCount"], 0)
            
            # Verify percentage is between 0 and 1
            self.assertTrue(0.0 <= item["percentage"] <= 1.0)
            
            # Verify sentimentScore is in valid range
            self.assertTrue(-1.0 <= item["averageSentiment"] <= 1.0)
            
    def test_radar_chart_data(self):
        """Test retrieving radar chart data for a state."""
        state = "VIC"
        response = requests.get(f"{self.BASE_URL}/api/analysis/radar/{state}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        
        # Check that the response contains at least one entry
        self.assertTrue(len(data) > 0)
        
        # Verify all sentiment scores are in valid range
        for category, sentiment in data.items():
            self.assertIsInstance(sentiment, float)
            self.assertTrue(-1.0 <= sentiment <= 1.0)
            
    def test_line_chart_data(self):
        """Test retrieving line chart data for a state and category."""
        state = "VIC"
        category = "rental"
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/line/{state}/{category}",
            params={"monthCount": 6}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        if data:
            item = data[0]
            self.assertIn("timePoint", item)
            self.assertIn("averageSentiment", item)
            self.assertIn("postCount", item)
            self.assertIn("topicCategory", item)
            
            # Check data types
            self.assertIsInstance(item["timePoint"], str)
            self.assertIsInstance(item["averageSentiment"], float)
            self.assertIsInstance(item["postCount"], int)
            self.assertIsInstance(item["topicCategory"], str)
            
            # Verify timePoint format (YYYY-MM)
            self.assertTrue(re.match(r"^\d{4}-\d{2}$", item["timePoint"]))
            
            # Verify sentimentScore is in valid range
            self.assertTrue(-1.0 <= item["averageSentiment"] <= 1.0)
            
            # Verify postCount is non-negative
            self.assertGreaterEqual(item["postCount"], 0)
            
            # Verify category in response matches requested category
            self.assertEqual(item["topicCategory"].lower(), category.lower())
            
    def test_heatmap_data(self):
        """Test retrieving heatmap data for a state."""
        state = "VIC"
        response = requests.get(f"{self.BASE_URL}/api/analysis/heatmap/{state}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        if data:
            item = data[0]
            self.assertIn("topicA", item)
            self.assertIn("topicB", item)
            self.assertIn("correlationCoefficient", item)
            
            # Check data types
            self.assertIsInstance(item["topicA"], str)
            self.assertIsInstance(item["topicB"], str)
            self.assertIsInstance(item["correlationCoefficient"], float)
            
            # Verify correlation coefficient is between -1 and 1
            self.assertTrue(-1.0 <= item["correlationCoefficient"] <= 1.0)
            
            # Check self-correlation equals 1.0
            if item["topicA"] == item["topicB"]:
                self.assertEqual(item["correlationCoefficient"], 1.0)
            
    def test_local_hot_topics(self):
        """Test retrieving local hot topics analysis."""
        loc_pid = "2GMEL"  # Melbourne location ID
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/hyper/local-hot-topics",
            params={"locPid": loc_pid, "limit": 5}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check basic structure
        self.assertIn("locPid", data)
        self.assertIn("sentimentScore", data)
        self.assertIn("representativeViews", data)
        self.assertIn("sentimentLabel", data)
        self.assertIn("topicPoints", data)
        
        # Check data types
        self.assertIsInstance(data["locPid"], str)
        self.assertIsInstance(data["sentimentScore"], float)
        self.assertIsInstance(data["representativeViews"], list)
        self.assertIsInstance(data["sentimentLabel"], str)
        self.assertIsInstance(data["topicPoints"], list)
        
        # Verify locPid matches requested
        self.assertEqual(data["locPid"], loc_pid)
        
        # Verify sentimentScore is in valid range
        self.assertTrue(-1.0 <= data["sentimentScore"] <= 1.0)
        
        # Verify sentimentLabel is one of expected values
        self.assertIn(data["sentimentLabel"], ["Positive", "Negative", "Neutral"])
        
    def test_topic_discussion(self):
        """Test retrieving topic discussion analysis."""
        loc_pid = "2GMEL"  # Melbourne location ID
        topic = "rental"
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/hyper/topic-discussion",
            params={"locPid": loc_pid, "topic": topic, "limit": 5}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check basic structure
        self.assertIn("locPid", data)
        self.assertIn("topic", data)
        self.assertIn("representativeViews", data)
        self.assertIn("sentimentScore", data)
        self.assertIn("sentimentLabel", data)
        
        # Check data types
        self.assertIsInstance(data["locPid"], str)
        self.assertIsInstance(data["topic"], str)
        self.assertIsInstance(data["representativeViews"], list)
        self.assertIsInstance(data["sentimentScore"], float)
        self.assertIsInstance(data["sentimentLabel"], str)
        
        # Verify locPid and topic match requested
        self.assertEqual(data["locPid"], loc_pid)
        self.assertEqual(data["topic"], topic)
        
        # Verify sentimentScore is in valid range
        self.assertTrue(-1.0 <= data["sentimentScore"] <= 1.0)
        
    def test_query_insights(self):
        """Test the natural language query insights API."""
        query = "What are people saying about rental prices in Melbourne?"
        payload = {
            "query": query,
            "locPid": "2GMEL",
            "topics": "rental",
            "limit": 5
        }
        response = requests.post(
            f"{self.BASE_URL}/api/analysis/hyper/query-insights",
            json=payload
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check basic structure
        self.assertIn("query", data)
        self.assertIn("sentimentScore", data)
        self.assertIn("representativeViews", data)
        self.assertIn("sentimentLabel", data)
        
        # Check data types
        self.assertIsInstance(data["query"], str)
        self.assertIsInstance(data["sentimentScore"], float)
        self.assertIsInstance(data["representativeViews"], list)
        self.assertIsInstance(data["sentimentLabel"], str)
        
        # Verify query matches requested
        self.assertEqual(data["query"], query)
        
        # Verify sentimentScore is in valid range
        self.assertTrue(-1.0 <= data["sentimentScore"] <= 1.0)
        
    def test_basic_comments_endpoints(self):
        """Test the basic data access endpoints for comments."""
        # Test location endpoint
        location = "melbourne"
        response = requests.get(f"{self.BASE_URL}/api/comments/location/{location}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        if data:
            item = data[0]
            self.assertIn("firstLocation", item)
            self.assertIn("firstState", item)
            self.assertIn("firstSentimentScore", item)
            self.assertIn("text", item)
            
            # Check that location matches requested
            location_values = [loc.lower() for loc in item["location"]]
            self.assertIn(location.lower(), location_values)
            
            # Verify sentimentScore is in valid range
            self.assertTrue(-1.0 <= item["firstSentimentScore"] <= 1.0)
        
        # Test state endpoint
        state = "VIC"
        response = requests.get(f"{self.BASE_URL}/api/comments/state/{state}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        if data:
            item = data[0]
            self.assertIn("firstState", item)
            
            # Check that state matches requested
            self.assertEqual(item["firstState"], state)
        
        # Test emotion endpoint
        emotion = "positive"
        response = requests.get(f"{self.BASE_URL}/api/comments/emotion/{emotion}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

if __name__ == "__main__":
    unittest.main()
