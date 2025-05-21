import openai
from typing import List, Dict

class AISuggester:
    def __init__(self, api_key: str, logger):
        self.api_key = api_key
        self.logger = logger
        openai.api_key = api_key
    
    def get_suggestions(self, files: List[Dict], dest_dir: str) -> List[str]:
        """Get AI suggestions for file organization"""
        if not self.api_key:
            return ["AI suggestions disabled - no API key configured"]
        
        try:
            # Prepare file information for AI
            file_info = "\n".join([
                f"{file['name']} (Type: {file['type']}, Size: {file['size']} bytes)"
                for file in files
            ])
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides suggestions for organizing files."},
                    {"role": "user", "content": f"""I'm organizing these files into {dest_dir}. 
                    Can you provide 3-5 suggestions for how I might better organize these files?
                    Files:
                    {file_info}
                    
                    Please provide concise suggestions in a bulleted list.
                    """}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            suggestions = response.choices[0].message.content.split('\n')
            return [s.strip() for s in suggestions if s.strip()]
        
        except Exception as e:
            self.logger.error(f"AI suggestions error: {e}")
            return [f"Error getting suggestions: {str(e)}"]