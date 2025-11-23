"""
LLM Processor Module
Handles interaction with OpenRouter API to extract structured data
"""

import requests
import json
from typing import Dict, List

def call_openrouter_api(prompt: str, api_key: str, model: str = "deepseek/deepseek-r1") -> str:
    """
    Call OpenRouter API with a prompt.
    
    Args:
        prompt: The prompt to send to the LLM
        api_key: OpenRouter API key
        model: Model to use (default: deepseek-r1, free tier)
        
    Returns:
        str: LLM response text
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,  # Low temperature for consistency
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except (KeyError, IndexError) as e:
        raise Exception(f"Unexpected API response format: {str(e)}")


def extract_fields_from_text(placeholders: List[str], extracted_text: str, api_key: str) -> Dict[str, str]:
    """
    Use LLM to extract field values from text based on placeholders.
    
    Args:
        placeholders: List of placeholder names (e.g., ['ClaimantName', 'AccidentDate'])
        extracted_text: Text extracted from PDF reports
        api_key: OpenRouter API key
        
    Returns:
        dict: Mapping of placeholder to extracted value
    """
    
    # Create the prompt
    prompt = f"""You are an AI assistant helping to extract information from insurance photo reports to fill out a claim form.

I have the following fields that need to be filled:
{', '.join(placeholders)}

Here is the text extracted from the insurance photo reports:

---
{extracted_text}
---

Please analyze the text and extract the appropriate value for each field. Return your response as a JSON object with the field names as keys and the extracted values as values.

If a field cannot be found in the text, use "Not Found" as the value.

Important guidelines:
- Extract exact values when available
- For dates, use a consistent format (YYYY-MM-DD if possible)
- For monetary amounts, include currency symbols
- For names, use full names if available
- Be concise and accurate

Return ONLY the JSON object, no additional text or explanation.

Example format:
{{
    "ClaimantName": "John Doe",
    "AccidentDate": "2025-01-15",
    "DamageEstimate": "$4,200"
}}"""

    try:
        # Call the LLM
        response = call_openrouter_api(prompt, api_key)
        
        # Parse the JSON response
        # Clean up the response (remove markdown code blocks if present)
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        response = response.strip()
        
        # Parse JSON
        extracted_data = json.loads(response)
        
        # Ensure all placeholders are in the result
        result = {}
        for placeholder in placeholders:
            result[placeholder] = extracted_data.get(placeholder, "Not Found")
        
        return result
    
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse LLM response as JSON: {str(e)}\nResponse: {response}")
    except Exception as e:
        raise Exception(f"Error during field extraction: {str(e)}")


def validate_api_key(api_key: str) -> bool:
    """
    Validate if the OpenRouter API key works.
    
    Args:
        api_key: OpenRouter API key
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        test_prompt = "Say 'OK' if you receive this message."
        response = call_openrouter_api(test_prompt, api_key)
        return len(response) > 0
    except:
        return False