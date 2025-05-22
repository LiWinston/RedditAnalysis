import unittest
import os
import pandas as pd
import pickle
from collections import defaultdict
from unittest.mock import patch, mock_open


# add import path
import sys
sys.path.append("../../backend/harvesters/fission/functions/reddit-harvester/")

# Import modules to test
from locality_resolver import create_location_to_state_mapping, resolve_ambiguous_locations, state_indicators
from category_indicator_processor import process_csv, CATEGORIES


class TestLocalityResolver(unittest.TestCase):
    """Test cases for locality_resolver.py functions"""
    
    def setUp(self):
        """Set up test data for locality resolver tests"""
        # Mock location data for testing
        self.test_ambiguous_locations = {
            "richmond": ["VIC", "NSW", "QLD"],
            "springfield": ["QLD", "NSW"]
        }
        self.test_location_pids = {
            "richmond": ["VIC123", "NSW456", "QLD789"],
            "springfield": ["QLD321", "NSW654"],
            "melbourne": ["VIC999"]
        }
        self.test_location_states = {
            "richmond": ["VIC", "NSW", "QLD"],
            "springfield": ["QLD", "NSW"],
            "melbourne": ["VIC"]
        }
        
        # Create a mock directory for pickle files
        if not os.path.exists("final_locations"):
            os.makedirs("final_locations")

    def tearDown(self):
        """Clean up test data"""
        # Clean up pickle files created during testing
        pickle_files = [
            os.path.join("final_locations", "ambiguous_locations.pkl"),
            os.path.join("final_locations", "location_pids.pkl"),
            os.path.join("final_locations", "location_states.pkl")
        ]
        
        for file_path in pickle_files:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    @patch('os.path.exists')
    @patch('pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_location_to_state_mapping_with_existing_pickle(self, mock_file, mock_pickle_load, mock_exists):
        """Test create_location_to_state_mapping when pickle files exist"""
        # Mock os.path.exists to return True for pickle files
        mock_exists.return_value = True
        
        # Set up mock return values for pickle.load
        mock_pickle_load.side_effect = [
            self.test_ambiguous_locations,
            self.test_location_pids,
            self.test_location_states
        ]
        
        # Call function
        ambiguous_locations, location_pids, location_states = create_location_to_state_mapping()
        
        # Assert results
        self.assertEqual(ambiguous_locations, self.test_ambiguous_locations)
        self.assertEqual(location_pids, self.test_location_pids)
        self.assertEqual(location_states, self.test_location_states)
    
    @patch('os.path.exists')
    @patch('pandas.read_csv')
    @patch('pickle.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_location_to_state_mapping_without_pickle(self, mock_file, mock_pickle_dump, mock_read_csv, mock_exists):
        """Test create_location_to_state_mapping when pickle files don't exist"""
        # Mock os.path.exists to return False (no pickle files)
        mock_exists.return_value = False
        
        # Mock DataFrame for each state file
        vic_df = pd.DataFrame({
            'Locality': ['Melbourne', 'Richmond'],
            'LOC_PID': ['VIC999', 'VIC123']
        })
        nsw_df = pd.DataFrame({
            'Locality': ['Richmond', 'Springfield'],
            'LOC_PID': ['NSW456', 'NSW654']
        })
        qld_df = pd.DataFrame({
            'Locality': ['Richmond', 'Springfield'],
            'LOC_PID': ['QLD789', 'QLD321']
        })
        
        # Set up mock return values for pd.read_csv
        mock_read_csv.side_effect = [vic_df, nsw_df, qld_df, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]
        
        # Call function
        ambiguous_locations, location_pids, location_states = create_location_to_state_mapping()
        
        # Assert that location_states has the expected structure
        self.assertIn('richmond', location_states)
        self.assertIn('melbourne', location_states)
        self.assertIn('springfield', location_states)
        
        # Check that ambiguous_locations only includes locations in multiple states
        self.assertIn('richmond', ambiguous_locations)
        self.assertIn('springfield', ambiguous_locations)
        self.assertNotIn('melbourne', ambiguous_locations)
        
    def test_resolve_ambiguous_locations_with_state_indicator(self):
        """Test resolving ambiguous locations when state indicators are present"""
        # Test with direct state mention
        text = "I live in Richmond, Victoria and it's nice."
        location = "richmond"
        result = resolve_ambiguous_locations(text, location)
        self.assertEqual(result, "richmond|VIC")
        
        # Test with abbreviated state
        text = "Richmond NSW is different from the one in VIC."
        location = "richmond"
        result = resolve_ambiguous_locations(text, location)
        self.assertEqual(result, "richmond|NSW")
        
        # Test with state indicator
        text = "Springfield near Brisbane has good weather."
        location = "springfield"
        result = resolve_ambiguous_locations(text, location)
        self.assertEqual(result, "springfield|QLD")
    
    def test_resolve_ambiguous_locations_without_indicators(self):
        """Test resolving ambiguous locations when no state indicators are present"""
        text = "I went to Richmond yesterday. It was great."
        location = "richmond"
        result = resolve_ambiguous_locations(text, location)
        self.assertEqual(result, "richmond (ambiguous locations)")
        
        # Test with non-ambiguous location
        text = "Melbourne is a nice city."
        location = "melbourne"
        # Assume melbourne is not ambiguous in our test data
        with patch('locality_resolver.ambiguous_locations', {'richmond': ['VIC', 'NSW']}):
            result = resolve_ambiguous_locations(text, location)
            self.assertEqual(result, "melbourne")


class TestCategoryIndicatorProcessor(unittest.TestCase):
    """Test cases for category_indicator_processor.py functions"""
    
    def setUp(self):
        """Set up test data for category indicator processor tests"""
        # Create a test DataFrame
        self.test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'text': ['Housing crisis in Australia', 
                      'Mental health and rental stress',
                      'Immigration policy impact',
                      'Wage growth and housing affordability',
                      'General post with no categories'],
            'category': ['general housing', 
                         'mental health, rental',
                         'immigration',
                         'wage, general housing',
                         '']
        })
        
        # Define expected column names after processing
        self.expected_columns = ['id', 'text', 'isGeneralHousing', 'isImmigration', 
                                 'isRental', 'isWage', 'isMentalHealth']
    
    def test_process_csv(self):
        """Test the process_csv function"""
        # Create temporary input/output files
        input_file = 'test_input.csv'
        output_file = 'test_output.csv'
        
        try:
            # Write test data to input file
            self.test_data.to_csv(input_file, index=False)
            
            # Process the CSV
            process_csv(input_file, output_file)
            
            # Read the output file
            result_df = pd.read_csv(output_file)
            
            # Verify the result
            self.assertEqual(list(result_df.columns), self.expected_columns)
            self.assertEqual(len(result_df), len(self.test_data))
            
            # Check that indicator columns were correctly populated
            self.assertEqual(result_df.iloc[0]['isGeneralHousing'], 1)
            self.assertEqual(result_df.iloc[1]['isMentalHealth'], 1)
            self.assertEqual(result_df.iloc[1]['isRental'], 1)
            self.assertEqual(result_df.iloc[2]['isImmigration'], 1)
            self.assertEqual(result_df.iloc[3]['isWage'], 1)
            self.assertEqual(result_df.iloc[3]['isGeneralHousing'], 1)
            self.assertEqual(result_df.iloc[4]['isGeneralHousing'], 0)
            
        finally:
            # Clean up test files
            if os.path.exists(input_file):
                os.remove(input_file)
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def test_process_csv_empty_input(self):
        """Test process_csv with empty input"""
        empty_df = pd.DataFrame(columns=['id', 'text', 'category'])
        input_file = 'empty_input.csv'
        output_file = 'empty_output.csv'
        
        try:
            # Write empty data to input file
            empty_df.to_csv(input_file, index=False)
            
            # Process the CSV
            process_csv(input_file, output_file)
            
            # Read the output file
            result_df = pd.read_csv(output_file)
            
            # Verify the result - should have expected columns but no rows
            self.assertTrue(all(col in result_df.columns for col in self.expected_columns))
            self.assertEqual(len(result_df), 0)
            
        finally:
            # Clean up test files
            if os.path.exists(input_file):
                os.remove(input_file)
            if os.path.exists(output_file):
                os.remove(output_file)


if __name__ == '__main__':
    unittest.main()

