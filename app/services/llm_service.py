import google.generativeai as genai
import os
from typing import List, Dict, Any

class GeminiWrapper:
    def __init__(self, model_name="gemini-pro"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None

    def generate_content(self, prompt: str) -> str:
        if not self.model:
            return f"Mock response: Processed '{prompt}'"
        response = self.model.generate_content(prompt)
        return response.text

    def plan_dq_checks(self, user_query: str, schema_info: List[str]) -> str:
        prompt = f"""
        Given the user query: "{user_query}"
        And available schemas: {schema_info}
        Plan a series of Data Quality checks.
        Return the plan as a list of steps.
        """
        return self.generate_content(prompt)

    def generate_dq_sql(self, check_description: str, table_name: str) -> str:
        prompt = f"""
        Generate SQL for the following DQ check: "{check_description}"
        Target table: {table_name}
        Dialect: Databricks SQL
        """
        return self.generate_content(prompt)
