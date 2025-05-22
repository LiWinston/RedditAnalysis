'''
Author: Zifei Li
'''
import pandas as pd

CATEGORIES = [
    "general housing",
    "immigration",
    "rental",
    "wage",
    "mental health"
]

def process_csv(input_file, output_file):
    """
    Process CSV file and add category indicator columns

    Args:
        input_file (str): Path to the input csv file
        output_file (str): Path to the output csv file
    """
    df = pd.read_csv(input_file)

    for category in CATEGORIES:
        column_name = "is" + "".join(word.capitalize() for word in category.split())

        df[column_name] = df['category'].apply(
            lambda cats: 1 if isinstance(cats, str) and category in [c.strip() for c in cats.split(',')] else 0
        )

    df = df.drop(columns=['category'])

    df.to_csv(output_file, index=False)