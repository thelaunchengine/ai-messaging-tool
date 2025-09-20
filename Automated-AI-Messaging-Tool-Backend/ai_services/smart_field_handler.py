"""
Smart Field Handler for Form Submission
Intelligently handles unknown mandatory fields using AI
"""

import os
import json
import logging
import google.generativeai as genai
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from ai_services.robust_json_parser import RobustJSONParser, ParseResult

logger = logging.getLogger(__name__)

@dataclass
class FieldInfo:
    """Information about a form field"""
    name: str
    field_type: str
    is_required: bool
    placeholder: Optional[str] = None
    options: List[str] = None
    validation_pattern: Optional[str] = None
    suggested_value: Optional[str] = None
    confidence: float = 0.0

@dataclass
class FieldHandlingResult:
    """Result of field handling attempt"""
    success: bool
    field_name: str
    value: Optional[str] = None
    method_used: str = "unknown"
    confidence: float = 0.0
    error_message: Optional[str] = None

class SmartFieldHandler:
    """AI-powered field handler for unknown form fields"""
    
    def __init__(self):
        """Initialize the smart field handler"""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Initialize robust JSON parser
        self.json_parser = RobustJSONParser()
        
        # Predefined field mappings and fallbacks
        self.known_field_patterns = {
            'name': ['name', 'full_name', 'first_name', 'last_name', 'contact_name'],
            'email': ['email', 'email_address', 'e_mail', 'contact_email'],
            'phone': ['phone', 'telephone', 'mobile', 'cell', 'contact_phone'],
            'subject': ['subject', 'topic', 'inquiry_type', 'reason'],
            'message': ['message', 'comment', 'inquiry', 'description', 'details'],
            'company': ['company', 'business', 'organization', 'firm'],
            'budget': ['budget', 'price_range', 'cost', 'investment'],
            'timeline': ['timeline', 'deadline', 'when', 'schedule'],
            'referral': ['referral', 'source', 'how_did_you_hear', 'found_us'],
            'industry': ['industry', 'sector', 'business_type', 'field'],
            'size': ['size', 'employees', 'company_size', 'team_size']
        }
        
        # Fallback values for common field types
        self.fallback_values = {
            'budget': ['Please contact for pricing', 'Not specified', 'Flexible'],
            'timeline': ['ASAP', 'Within 30 days', 'Flexible', 'Not urgent'],
            'referral': ['Google', 'Website', 'Search', 'Online'],
            'industry': ['Technology', 'Business', 'General', 'Not specified'],
            'size': ['Small-Medium', 'Medium', 'Not specified'],
            'urgency': ['Normal', 'Medium', 'Not urgent'],
            'preferred_contact': ['Email', 'Phone', 'Either'],
            'project_type': ['General Inquiry', 'Consultation', 'Service Request']
        }
    
    def analyze_unknown_fields(self, form_html: str, page_context: str, page_url: str) -> List[FieldInfo]:
        """
        Use AI to analyze unknown form fields and suggest values
        
        Args:
            form_html: HTML content of the form
            page_context: Additional context about the page
            page_url: URL of the page
            
        Returns:
            List of FieldInfo objects for unknown fields
        """
        try:
            logger.info(f"🔍 Analyzing unknown fields for {page_url}")
            
            prompt = f"""
            Analyze this form HTML and identify all fields that are not standard contact form fields.
            
            Page URL: {page_url}
            Page Context: {page_context}
            Form HTML: {form_html[:3000]}...
            
            Standard fields (ignore these): name, email, phone, subject, message, company
            
            For each non-standard field, provide:
            1. Field name and purpose
            2. Field type (text, select, radio, checkbox, textarea)
            3. Whether it's required
            4. Placeholder text or options
            5. Suggested appropriate value
            6. Confidence in the suggestion
            
            Return JSON:
            {{
                "unknown_fields": [
                    {{
                        "name": "budget",
                        "field_type": "select",
                        "is_required": true,
                        "placeholder": "Select budget range",
                        "options": ["$1k-5k", "$5k-10k", "$10k+"],
                        "suggested_value": "$5k-10k",
                        "confidence": 0.8,
                        "reasoning": "Middle range for business inquiry"
                    }}
                ]
            }}
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            # Parse AI response with robust parsing
            expected_structure = {
                'unknown_fields': list
            }
            
            parse_result = self.json_parser.parse_ai_response(response.text, expected_structure)
            
            if parse_result.success:
                data = parse_result.data or {}
                fields = []
                for field_data in data.get('unknown_fields', []):
                    field = FieldInfo(
                        name=field_data.get('name', ''),
                        field_type=field_data.get('field_type', 'text'),
                        is_required=field_data.get('is_required', False),
                        placeholder=field_data.get('placeholder'),
                        options=field_data.get('options', []),
                        suggested_value=field_data.get('suggested_value'),
                        confidence=field_data.get('confidence', 0.0)
                    )
                    fields.append(field)
                
                logger.info(f"✅ Analyzed {len(fields)} unknown fields using {parse_result.method_used}")
                return fields
            else:
                logger.warning(f"AI field analysis parsing failed: {parse_result.error_message}")
                return []
            
        except Exception as e:
            logger.error(f"Error analyzing unknown fields: {e}")
        
        return []
    
    def generate_field_value(self, field_info: FieldInfo, context: Dict[str, Any]) -> FieldHandlingResult:
        """
        Generate appropriate value for an unknown field
        
        Args:
            field_info: Information about the field
            context: Additional context (website industry, form purpose, etc.)
            
        Returns:
            FieldHandlingResult with generated value
        """
        try:
            logger.info(f"🎯 Generating value for field: {field_info.name}")
            
            # Try to match field to known patterns
            matched_pattern = self._match_field_pattern(field_info.name)
            if matched_pattern:
                return self._generate_value_for_pattern(matched_pattern, field_info, context)
            
            # Use AI to generate contextually appropriate value
            if self.gemini_api_key:
                return self._generate_value_with_ai(field_info, context)
            
            # Fallback to generic values
            return self._generate_fallback_value(field_info, context)
            
        except Exception as e:
            logger.error(f"Error generating value for field {field_info.name}: {e}")
            return FieldHandlingResult(
                success=False,
                field_name=field_info.name,
                error_message=str(e)
            )
    
    def _match_field_pattern(self, field_name: str) -> Optional[str]:
        """Match field name to known patterns"""
        field_lower = field_name.lower()
        
        for pattern, keywords in self.known_field_patterns.items():
            if any(keyword in field_lower for keyword in keywords):
                return pattern
        
        return None
    
    def _generate_value_for_pattern(self, pattern: str, field_info: FieldInfo, context: Dict[str, Any]) -> FieldHandlingResult:
        """Generate value for a known field pattern"""
        try:
            if pattern == 'budget':
                value = self._generate_budget_value(field_info, context)
            elif pattern == 'timeline':
                value = self._generate_timeline_value(field_info, context)
            elif pattern == 'referral':
                value = self._generate_referral_value(field_info, context)
            elif pattern == 'industry':
                value = self._generate_industry_value(field_info, context)
            elif pattern == 'size':
                value = self._generate_size_value(field_info, context)
            else:
                value = self._generate_generic_value(field_info, context)
            
            return FieldHandlingResult(
                success=True,
                field_name=field_info.name,
                value=value,
                method_used=f"pattern_match_{pattern}",
                confidence=0.8
            )
            
        except Exception as e:
            return FieldHandlingResult(
                success=False,
                field_name=field_info.name,
                error_message=f"Pattern generation failed: {e}"
            )
    
    def _generate_value_with_ai(self, field_info: FieldInfo, context: Dict[str, Any]) -> FieldHandlingResult:
        """Use AI to generate contextually appropriate value"""
        try:
            prompt = f"""
            Generate an appropriate value for this form field:
            
            Field Name: {field_info.name}
            Field Type: {field_info.field_type}
            Is Required: {field_info.is_required}
            Placeholder: {field_info.placeholder or 'None'}
            Options: {field_info.options or 'None'}
            
            Context:
            - Website Industry: {context.get('industry', 'Unknown')}
            - Form Purpose: {context.get('purpose', 'General inquiry')}
            - Company Type: {context.get('company_type', 'Business')}
            
            Generate a realistic, appropriate value that would be suitable for a business inquiry.
            Consider the field type and available options.
            
            Return only the value, nothing else.
            """
            
            response = self.gemini_model.generate_content(prompt)
            value = response.text.strip()
            
            if value and len(value) > 0:
                return FieldHandlingResult(
                    success=True,
                    field_name=field_info.name,
                    value=value,
                    method_used="ai_generation",
                    confidence=0.7
                )
            
        except Exception as e:
            logger.error(f"AI value generation failed: {e}")
        
        return self._generate_fallback_value(field_info, context)
    
    def _generate_fallback_value(self, field_info: FieldInfo, context: Dict[str, Any]) -> FieldHandlingResult:
        """Generate fallback value when AI fails"""
        try:
            # Try to find appropriate fallback based on field name
            field_lower = field_info.name.lower()
            
            for fallback_type, values in self.fallback_values.items():
                if fallback_type in field_lower:
                    value = values[0]  # Use first fallback value
                    return FieldHandlingResult(
                        success=True,
                        field_name=field_info.name,
                        value=value,
                        method_used="fallback_value",
                        confidence=0.5
                    )
            
            # Generic fallback
            if field_info.field_type == 'select' and field_info.options:
                value = field_info.options[0]
            elif field_info.field_type == 'radio' and field_info.options:
                value = field_info.options[0]
            elif field_info.field_type == 'checkbox':
                value = 'on'
            else:
                value = 'Not specified'
            
            return FieldHandlingResult(
                success=True,
                field_name=field_info.name,
                value=value,
                method_used="generic_fallback",
                confidence=0.3
            )
            
        except Exception as e:
            return FieldHandlingResult(
                success=False,
                field_name=field_info.name,
                error_message=f"Fallback generation failed: {e}"
            )
    
    def _generate_budget_value(self, field_info: FieldInfo, context: Dict[str, Any]) -> str:
        """Generate appropriate budget value"""
        if field_info.options:
            # Choose middle option if available
            if len(field_info.options) >= 3:
                return field_info.options[len(field_info.options) // 2]
            else:
                return field_info.options[0]
        
        return "Please contact for pricing"
    
    def _generate_timeline_value(self, field_info: FieldInfo, context: Dict[str, Any]) -> str:
        """Generate appropriate timeline value"""
        if field_info.options:
            return field_info.options[0]
        
        return "Within 30 days"
    
    def _generate_referral_value(self, field_info: FieldInfo, context: Dict[str, Any]) -> str:
        """Generate appropriate referral source value"""
        if field_info.options:
            # Prefer common sources
            preferred = ['Google', 'Website', 'Search', 'Online']
            for pref in preferred:
                if pref in field_info.options:
                    return pref
            return field_info.options[0]
        
        return "Google"
    
    def _generate_industry_value(self, field_info: FieldInfo, context: Dict[str, Any]) -> str:
        """Generate appropriate industry value"""
        if field_info.options:
            return field_info.options[0]
        
        return context.get('industry', 'Technology')
    
    def _generate_size_value(self, field_info: FieldInfo, context: Dict[str, Any]) -> str:
        """Generate appropriate company size value"""
        if field_info.options:
            return field_info.options[0]
        
        return "Small-Medium"
    
    def _generate_generic_value(self, field_info: FieldInfo, context: Dict[str, Any]) -> str:
        """Generate generic value for unknown field type"""
        if field_info.options:
            return field_info.options[0]
        
        return "Not specified"
    
    def can_handle_field(self, field_info: FieldInfo) -> bool:
        """Check if we can handle this field type"""
        # We can handle most field types
        return field_info.field_type in ['text', 'email', 'tel', 'select', 'radio', 'checkbox', 'textarea']
    
    def get_field_handling_strategies(self) -> Dict[str, List[str]]:
        """Get available field handling strategies"""
        return {
            'pattern_matching': [
                'Match field names to known patterns',
                'Use predefined fallback values',
                'High confidence for known field types'
            ],
            'ai_generation': [
                'Use Gemini AI to generate contextually appropriate values',
                'Consider website industry and form purpose',
                'Medium confidence, good for complex fields'
            ],
            'fallback_values': [
                'Use generic fallback values',
                'Select first available option',
                'Low confidence but always provides a value'
            ],
            'skip_and_report': [
                'Skip fields that cannot be handled',
                'Report detailed error messages',
                'Used as last resort for critical fields'
            ]
        }
