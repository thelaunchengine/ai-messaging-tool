"""
Robust JSON Parser for AI Responses
Handles malformed JSON responses from AI models with multiple fallback strategies
"""

import json
import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ParseResult:
    """Result of JSON parsing attempt"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    method_used: str = "unknown"
    confidence: float = 0.0

class RobustJSONParser:
    """Robust JSON parser with multiple fallback strategies"""
    
    def __init__(self):
        """Initialize the robust JSON parser"""
        self.max_retries = 3
        self.common_fixes = [
            self._fix_trailing_commas,
            self._fix_missing_commas,
            self._fix_unquoted_keys,
            self._fix_single_quotes,
            self._fix_boolean_values,
            self._fix_numeric_values,
            self._fix_escape_sequences,
            self._fix_nested_quotes
        ]
    
    def parse_ai_response(self, response_text: str, expected_structure: Dict[str, Any] = None) -> ParseResult:
        """
        Parse AI response with multiple fallback strategies
        
        Args:
            response_text: Raw response text from AI
            expected_structure: Expected JSON structure for validation
            
        Returns:
            ParseResult with parsing details
        """
        if not response_text or not response_text.strip():
            return ParseResult(
                success=False,
                error_message="Empty response text",
                method_used="validation"
            )
        
        # Try direct parsing first
        result = self._try_direct_parse(response_text)
        if result.success:
            return result
        
        # Try extraction and parsing
        result = self._try_extract_and_parse(response_text)
        if result.success:
            return result
        
        # Try common fixes
        for fix_method in self.common_fixes:
            result = self._try_with_fix(response_text, fix_method)
            if result.success:
                return result
        
        # Try partial parsing
        result = self._try_partial_parse(response_text, expected_structure)
        if result.success:
            return result
        
        # Try reconstruction
        result = self._try_reconstruct(response_text, expected_structure)
        if result.success:
            return result
        
        return ParseResult(
            success=False,
            error_message="All parsing methods failed",
            method_used="all_failed"
        )
    
    def _try_direct_parse(self, text: str) -> ParseResult:
        """Try direct JSON parsing"""
        try:
            data = json.loads(text)
            return ParseResult(
                success=True,
                data=data,
                method_used="direct_parse",
                confidence=1.0
            )
        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                error_message=f"Direct parse failed: {str(e)}",
                method_used="direct_parse"
            )
    
    def _try_extract_and_parse(self, text: str) -> ParseResult:
        """Extract JSON from text and parse"""
        try:
            # Find JSON object boundaries
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start == -1 or json_end <= json_start:
                return ParseResult(
                    success=False,
                    error_message="No JSON object found",
                    method_used="extract_parse"
                )
            
            json_str = text[json_start:json_end]
            data = json.loads(json_str)
            
            return ParseResult(
                success=True,
                data=data,
                method_used="extract_parse",
                confidence=0.9
            )
            
        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                error_message=f"Extract parse failed: {str(e)}",
                method_used="extract_parse"
            )
    
    def _try_with_fix(self, text: str, fix_method) -> ParseResult:
        """Try parsing with a specific fix method"""
        try:
            fixed_text = fix_method(text)
            data = json.loads(fixed_text)
            
            return ParseResult(
                success=True,
                data=data,
                method_used=f"fix_{fix_method.__name__}",
                confidence=0.7
            )
            
        except (json.JSONDecodeError, Exception) as e:
            return ParseResult(
                success=False,
                error_message=f"Fix {fix_method.__name__} failed: {str(e)}",
                method_used=f"fix_{fix_method.__name__}"
            )
    
    def _try_partial_parse(self, text: str, expected_structure: Dict[str, Any] = None) -> ParseResult:
        """Try to parse partial JSON and reconstruct missing parts"""
        try:
            # Extract what we can parse
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start == -1 or json_end <= json_start:
                return ParseResult(success=False, error_message="No JSON boundaries found")
            
            json_str = text[json_start:json_end]
            
            # Try to parse line by line and reconstruct
            lines = json_str.split('\n')
            parsed_lines = []
            
            for line in lines:
                line = line.strip()
                if not line or line in ['{', '}']:
                    parsed_lines.append(line)
                    continue
                
                # Try to fix common line issues
                if line.endswith(','):
                    parsed_lines.append(line)
                elif not line.endswith(',') and not line.endswith('}') and not line.endswith('{'):
                    parsed_lines.append(line + ',')
                else:
                    parsed_lines.append(line)
            
            reconstructed = '\n'.join(parsed_lines)
            data = json.loads(reconstructed)
            
            return ParseResult(
                success=True,
                data=data,
                method_used="partial_parse",
                confidence=0.6
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Partial parse failed: {str(e)}",
                method_used="partial_parse"
            )
    
    def _try_reconstruct(self, text: str, expected_structure: Dict[str, Any] = None) -> ParseResult:
        """Try to reconstruct JSON from text patterns"""
        try:
            if not expected_structure:
                return ParseResult(success=False, error_message="No expected structure provided")
            
            # Extract key-value pairs using regex
            data = {}
            
            # Find key-value pairs
            pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
            matches = re.findall(pattern, text)
            
            for key, value in matches:
                data[key] = value
            
            # Find boolean values
            bool_pattern = r'"([^"]+)"\s*:\s*(true|false)'
            bool_matches = re.findall(bool_pattern, text)
            
            for key, value in bool_matches:
                data[key] = value.lower() == 'true'
            
            # Find numeric values
            num_pattern = r'"([^"]+)"\s*:\s*(\d+(?:\.\d+)?)'
            num_matches = re.findall(num_pattern, text)
            
            for key, value in num_matches:
                data[key] = float(value) if '.' in value else int(value)
            
            # Find array values
            array_pattern = r'"([^"]+)"\s*:\s*\[([^\]]*)\]'
            array_matches = re.findall(array_pattern, text)
            
            for key, value in array_matches:
                # Simple array parsing
                items = [item.strip().strip('"') for item in value.split(',') if item.strip()]
                data[key] = items
            
            if data:
                return ParseResult(
                    success=True,
                    data=data,
                    method_used="reconstruct",
                    confidence=0.5
                )
            
            return ParseResult(success=False, error_message="No data extracted")
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Reconstruct failed: {str(e)}",
                method_used="reconstruct"
            )
    
    # Common fix methods
    def _fix_trailing_commas(self, text: str) -> str:
        """Fix trailing commas in JSON"""
        # Remove trailing commas before closing braces/brackets
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        return text
    
    def _fix_missing_commas(self, text: str) -> str:
        """Fix missing commas between JSON elements"""
        # Add commas between key-value pairs
        text = re.sub(r'"\s*\n\s*"', '",\n"', text)
        text = re.sub(r'}\s*\n\s*"', '},\n"', text)
        text = re.sub(r']\s*\n\s*"', '],\n"', text)
        return text
    
    def _fix_unquoted_keys(self, text: str) -> str:
        """Fix unquoted keys in JSON"""
        # Quote unquoted keys
        text = re.sub(r'(\w+):', r'"\1":', text)
        return text
    
    def _fix_single_quotes(self, text: str) -> str:
        """Fix single quotes to double quotes"""
        # Replace single quotes with double quotes (carefully)
        text = re.sub(r"'([^']*)':", r'"\1":', text)  # Keys
        text = re.sub(r':\s*\'([^\']*)\'', r': "\1"', text)  # Values
        return text
    
    def _fix_boolean_values(self, text: str) -> str:
        """Fix boolean values"""
        text = re.sub(r':\s*True\b', ': true', text)
        text = re.sub(r':\s*False\b', ': false', text)
        text = re.sub(r':\s*None\b', ': null', text)
        return text
    
    def _fix_numeric_values(self, text: str) -> str:
        """Fix numeric values"""
        # Ensure numbers are not quoted
        text = re.sub(r':\s*"(\d+(?:\.\d+)?)"', r': \1', text)
        return text
    
    def _fix_escape_sequences(self, text: str) -> str:
        """Fix escape sequences"""
        # Fix common escape sequence issues
        text = text.replace('\\"', '"')
        text = text.replace('\\n', '\n')
        text = text.replace('\\t', '\t')
        return text
    
    def _fix_nested_quotes(self, text: str) -> str:
        """Fix nested quote issues"""
        # This is more complex and would need specific handling
        # For now, just return the text
        return text
    
    def validate_structure(self, data: Dict[str, Any], expected_structure: Dict[str, Any]) -> bool:
        """Validate that parsed data matches expected structure"""
        if not expected_structure:
            return True
        
        try:
            for key, expected_type in expected_structure.items():
                if key not in data:
                    logger.warning(f"Missing expected key: {key}")
                    return False
                
                if isinstance(expected_type, type):
                    if not isinstance(data[key], expected_type):
                        logger.warning(f"Type mismatch for {key}: expected {expected_type}, got {type(data[key])}")
                        return False
                elif isinstance(expected_type, dict):
                    if not isinstance(data[key], dict):
                        logger.warning(f"Expected dict for {key}, got {type(data[key])}")
                        return False
                    if not self.validate_structure(data[key], expected_type):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Structure validation failed: {e}")
            return False
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        return {
            'max_retries': self.max_retries,
            'available_fixes': len(self.common_fixes),
            'fix_methods': [method.__name__ for method in self.common_fixes]
        }
