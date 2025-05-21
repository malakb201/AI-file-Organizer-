import openai
from typing import List, Dict
import json

class AICategorizer:
    def __init__(self, api_key: str, logger):
        self.api_key = api_key
        self.logger = logger
        openai.api_key = api_key
    
    def generate_categories(self, files: List[Dict]) -> Dict:
        """Generate custom categories based on file content"""
        if not self.api_key:
            return {"error": "API key not configured"}
        
        try:
            # Prepare file information for AI
            file_info = "\n".join([
                f"{file['name']} (Type: {file['type']}, Size: {file['size']} bytes)"
                for file in files[:20]  # Limit to 20 files for the prompt
            ])
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that suggests logical folder structures for organizing files."},
                    {"role": "user", "content": f"""Based on these files, suggest a folder structure that would make sense for organization.
                    Files:
                    {file_info}
                    
                    Please respond with a JSON object containing a 'categories' key with an array of category names,
                    and a 'files' key that maps each filename to one of these categories.
                    """}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        
        except Exception as e:
            self.logger.error(f"AI categorization error: {e}")
            return {"error": str(e)}