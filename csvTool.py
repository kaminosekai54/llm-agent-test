import pandas as pd
from crewai_tools import BaseTool
import os
import glob

class csvTool(BaseTool):
    name: str = "Ultimate CSV Manipulation Tool"
    description: str = (
        "A comprehensive tool for extensive manipulation of CSV files, "
        "supporting operations such as reading, writing, modifying, merging, "
        "concatenating, filtering, deduplicating, and more. Designed for automation "
        "and scripting, it allows for seamless CSV file handling including "
        "modifications of columns and rows, adding or removing columns or rows, "
        "merging multiple files based on key columns, concatenating files with identical structures, "
        "and extracting subsets based on conditions. This tool ensures a broad spectrum of "
        "data processing capabilities, making it essential for data analysis, preparation, "
        "and transformation tasks."
    )

    def _run(self, operation: str, **kwargs) -> str:
        # Dynamically call the method based on the operation argument
        method = getattr(self, operation, self.invalid_operation)
        return method(**kwargs)

    def invalid_operation(self, **kwargs):
        return "Invalid operation specified"

    def read_csv(self, file_path):
        df = pd.read_csv(file_path)
        return df.to_json()

    def write_csv(self, df_json, file_path):
        df = pd.read_json(df_json)
        df.to_csv(file_path, index=False)
        return "CSV file written successfully"

    def save_csv(self, df_json, file_path):
        df = pd.read_json(df_json)
        df.to_csv(file_path, index=False)
        return "CSV file saved successfully"

    def merge_csv(self, file_path1, file_path2, on, how='inner'):
        df1 = pd.read_csv(file_path1)
        df2 = pd.read_csv(file_path2)
        merged_df = pd.merge(df1, df2, on=on, how=how)
        return merged_df.to_json()

    def concatenate_csvs(self, directory_path, output_file_path):
        all_files = glob.glob(os.path.join(directory_path, "*.csv"))
        all_dfs = [pd.read_csv(f) for f in all_files]
        concatenated_df = pd.concat(all_dfs, ignore_index=True)
        concatenated_df.to_csv(output_file_path, index=False)
        return "CSV files concatenated successfully"

    def filter_rows(self, df_json, conditions):
        df = pd.read_json(df_json)
        filtered_df = df.query(conditions)
        return filtered_df.to_json()

    def find_duplicates(self, df_json, subset=None):
        df = pd.read_json(df_json)
        duplicates_df = df[df.duplicated(subset=subset, keep=False)]
        return duplicates_df.to_json()

    def drop_duplicates(self, df_json, subset=None, keep='first'):
        df = pd.read_json(df_json)
        dedup_df = df.drop_duplicates(subset=subset, keep=keep)
        return dedup_df.to_json()

    def add_column(self, df_json, column_name, values):
        df = pd.read_json(df_json)
        df[column_name] = values
        return df.to_json()

    def remove_column(self, df_json, column_name):
        df = pd.read_json(df_json)
        df.drop(column_name, axis=1, inplace=True)
        return df.to_json()

    def add_row(self, df_json, row_values):
        df = pd.read_json(df_json)
        new_row = pd.DataFrame([row_values], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        return df.to_json()

    def remove_row(self, df_json, index):
        df = pd.read_json(df_json)
        df.drop(index, inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df.to_json()

    def get_subset(self, df_json, conditions):
        df = pd.read_json(df_json)
        subset_df = df.query(conditions)
        return subset_df.to_json()
