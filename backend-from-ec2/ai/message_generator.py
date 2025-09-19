"""
AI Message Generator using Google Gemini API
"""
import os
import logging
import google.generativeai as genai
from typing import Dict, List, Any, Tuple, Optional
import json
import time
import random
from database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class PredefinedMessageIntegration:
    """Integration class for predefined messages with AI generation"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_relevant_predefined_messages(self, website_data: Dict) -> List[Dict]:
        """Get relevant predefined messages based on website data"""
        
        # Get website industry and business type
        industry = website_data.get('industry', '').lower()
        business_type = website_data.get('businessType', '').lower()
        
        # Query predefined messages that match
        messages = self.db_manager.get_predefined_messages_by_criteria(
            industry=industry,
            businessType=business_type,
            status='ACTIVE'
        )
        
        return messages
    
    def create_ai_prompt_with_predefined_messages(self, website_data: Dict, message_type: str) -> str:
        """Create AI prompt that incorporates predefined messages as examples"""
        
        # Get relevant predefined messages
        predefined_messages = self.get_relevant_predefined_messages(website_data)
        
        # Create prompt with predefined messages as examples
        prompt = f"""
        Generate a personalized message for this business:
        
        Company: {website_data.get('companyName', '')}
        Industry: {website_data.get('industry', '')}
        Business Type: {website_data.get('businessType', '')}
        About Us: {website_data.get('aboutUsContent', '')[:500]}
        
        Message Type: {message_type}
        
        Here are some example messages for similar businesses (use as inspiration, don't copy):
        """
        
        for i, msg in enumerate(predefined_messages[:3], 1):
            prompt += f"""
        Example {i}:
        Industry: {msg['industry']}
        Service: {msg['service']}
        Tone: {msg['tone']}
        Message: {msg['message']}
        """
        
        prompt += f"""
        Now generate a unique, personalized message for this specific business.
        Make it relevant to their industry and business type.
        Keep the tone professional but engaging.
        Include specific details from their About Us content.
        """
        
        return prompt
    
    def select_best_predefined_message(self, messages: List[Dict], website_data: Dict) -> Optional[Dict]:
        """Select the best predefined message based on relevance scoring"""
        
        if not messages:
            return None
            
        scored_messages = []
        
        for msg in messages:
            score = 0
            
            # Industry match
            if msg['industry'] and msg['industry'].lower() in website_data.get('industry', '').lower():
                score += 10
            
            # Business type match
            if msg['service'] and msg['service'].lower() in website_data.get('businessType', '').lower():
                score += 8
            
            # Service match in about us content
            if msg['service'] and msg['service'].lower() in website_data.get('aboutUsContent', '').lower():
                score += 6
            
            # Tone preference
            if msg['tone'] == 'professional':
                score += 2
            
            # Usage count (prefer less used messages for variety)
            score -= min(msg['usageCount'], 10)
            
            scored_messages.append((msg, score))
        
        # Return message with highest score
        return max(scored_messages, key=lambda x: x[1])[0]
    
    def customize_with_ai(self, base_message: Dict, website_data: Dict, ai_generator) -> str:
        """Customize predefined message with AI for specific business"""
        
        prompt = f"""
        Customize this predefined message for a specific business:
        
        Original Message:
        {base_message['message']}
        
        Target Business:
        Company: {website_data.get('companyName', '')}
        Industry: {website_data.get('industry', '')}
        Business Type: {website_data.get('businessType', '')}
        About Us: {website_data.get('aboutUsContent', '')[:300]}
        
        Instructions:
        1. Keep the core message structure and tone
        2. Replace generic references with specific business details
        3. Add personalized elements from their About Us content
        4. Make it feel like it was written specifically for this business
        5. Maintain the original message type and intent
        
        Generate the customized message:
        """
        
        # Use AI to customize
        try:
            response = ai_generator.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error customizing message with AI: {e}")
            return base_message['message']
    
    def update_usage_count(self, message_id: str):
        """Update usage count for predefined message"""
        self.db_manager.increment_predefined_message_usage(message_id)

class GeminiMessageGenerator:
    """Enhanced Gemini message generator with predefined message integration"""
    
    def __init__(self, api_key: str = None, db_manager: DatabaseManager = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=self.api_key)
                # Try gemini-1.5-flash first (more quota-friendly)
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            logger.warning(f"Failed to initialize gemini-1.5-flash: {e}")
            # Fallback to gemini-1.5-pro
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Initialize predefined message integration
        self.db_manager = db_manager
        self.predefined_integration = PredefinedMessageIntegration(db_manager) if db_manager else None
        
        self.message_templates = {
            'general': {
                'prompt': """
                You are writing a professional business outreach message. Write a complete, ready-to-send message with NO placeholders or brackets.

                Company: {company_name}
                Industry: {industry}
                Business Type: {businessType}
                About Us: {aboutUsContent}

                CRITICAL: Analyze the "About Us" content carefully to understand what this business actually does. 
                Don't just use the industry field - look at the actual content to determine their real business focus.

                Write a professional business outreach message that:
                1. Uses {company_name} as the actual company name (not [Company Name])
                2. References their ACTUAL business based on the About Us content, not just the industry field
                3. Shows you understand what they actually do (real estate, insurance, automotive, etc.)
                4. Is professional, courteous, and outreach-focused
                5. Encourages scheduling appointments or meetings to discuss relevant services
                6. Has a clear call to action focused on collaboration opportunities
                7. Is 3-4 paragraphs maximum
                8. Is COMPLETE and ready to send - NO [Your Name], NO [Your Company], NO placeholders
                9. Sounds like a real business professional writing to them
                10. Emphasizes the value of meeting to discuss potential partnerships or services
                11. Maintains a tone that encourages response and engagement
                12. References specific aspects of their business from the About Us content

                IMPORTANT: 
                - Keep the message under 500 characters total
                - Focus on being concise yet professional
                - Make sure the message is relevant to their ACTUAL business, not just the industry field
                - If they're in real estate, talk about real estate services
                - If they're in insurance, talk about insurance-related services
                - If they're in automotive, talk about automotive services

                Write the entire message as if you are actually sending it. Make up realistic details for the sender but keep it professional and business-focused.
                """,
                'max_tokens': 200
            },
            'partnership': {
                'prompt': """
                You are writing a professional business partnership outreach message. Write a complete, ready-to-send message with NO placeholders or brackets.

                Company: {company_name}
                Industry: {industry}
                Business Type: {businessType}
                About Us: {aboutUsContent}

                Write a professional partnership outreach message that:
                1. Uses {company_name} as the actual company name
                2. References their {industry} industry and {businessType} business type
                3. Is professional and partnership-focused
                4. Encourages scheduling meetings to discuss collaboration opportunities
                5. Has a clear call to action for partnership discussions
                6. Is 3-4 paragraphs maximum
                7. Is COMPLETE and ready to send - NO placeholders
                8. Emphasizes mutual benefits and collaboration potential
                9. Maintains professional business tone

                IMPORTANT: Keep the message under 500 characters total. Focus on being concise yet professional.

                Write the entire message as if you are actually sending it. Keep it professional and business-focused.
                """,
                'max_tokens': 200
            },
            'inquiry': {
                'prompt': """
                You are writing a professional business inquiry message. Write a complete, ready-to-send message with NO placeholders or brackets.

                Company: {company_name}
                Industry: {industry}
                Business Type: {businessType}
                About Us: {aboutUsContent}

                Write a professional inquiry message that:
                1. Uses {company_name} as the actual company name
                2. References their {industry} industry and {businessType} business type
                3. Is professional and inquiry-focused
                4. Encourages scheduling appointments to discuss services
                5. Has a clear call to action for service discussions
                6. Is 3-4 paragraphs maximum
                7. Is COMPLETE and ready to send - NO placeholders
                8. Shows genuine interest in their business
                9. Maintains professional business tone

                IMPORTANT: Keep the message under 500 characters total. Focus on being concise yet professional.

                Write the entire message as if you are actually sending it. Keep it professional and business-focused.
                """,
                'max_tokens': 200
            }
        }
    
    def generate_message(self, website_data: Dict, message_type: str = "general") -> Tuple[str, float]:
        """Generate message with hybrid approach (predefined + AI)"""
        
        try:
            # Try hybrid approach first (if predefined integration is available)
            if self.predefined_integration:
                result = self.hybrid_message_generation(website_data, message_type)
                return result['message'], result['confidence_score']
            
            # Fallback to pure AI generation
            return self.generate_pure_ai_message(website_data, message_type)
            
        except Exception as e:
            logger.error(f"Error generating message: {e}")
            # Return empty string instead of fallback message
            return "", 0.0
    
    def hybrid_message_generation(self, website_data: Dict, message_type: str) -> Dict[str, Any]:
        """Generate message using both AI and predefined templates with improved content analysis"""
        
        # First analyze the business content to get accurate industry and business type
        actual_industry, actual_business_type = self._analyze_business_content(website_data)
        
        # Update website_data with analyzed content
        enhanced_website_data = website_data.copy()
        enhanced_website_data['industry'] = actual_industry
        enhanced_website_data['businessType'] = actual_business_type
        
        # Get relevant predefined messages based on analyzed content
        predefined_messages = self.predefined_integration.get_relevant_predefined_messages(enhanced_website_data)
        
        if predefined_messages:
            # Use predefined message as base and customize with AI
            base_message = self.predefined_integration.select_best_predefined_message(predefined_messages, enhanced_website_data)
            
            if base_message:
                customized_message = self.predefined_integration.customize_with_ai(base_message, enhanced_website_data, self)
                
                # Update usage count
                self.predefined_integration.update_usage_count(base_message['id'])
                
                return {
                    'success': True,
                    'message': customized_message,
                    'method': 'hybrid',
                    'base_predefined_message': base_message['id'],
                    'customization_level': 'high',
                    'confidence_score': self._calculate_confidence_score(customized_message, enhanced_website_data)
                }
        
        # Fallback to pure AI generation with analyzed content
        try:
            message, confidence = self.generate_pure_ai_message(enhanced_website_data, message_type)
            
            return {
                'success': True,
                'message': message,
                'method': 'pure_ai',
                'base_predefined_message': None,
                'customization_level': 'full',
                'confidence_score': confidence
            }
        except Exception as e:
            logger.error(f"Pure AI generation failed: {e}")
            return {
                'success': False,
                'message': "",
                'method': 'failed',
                'base_predefined_message': None,
                'customization_level': 'none',
                'confidence_score': 0.0
            }
    
    def generate_pure_ai_message(self, website_data: Dict, message_type: str) -> Tuple[str, float]:
        """Generate message using pure AI approach with improved content analysis"""
        
        # Analyze the actual business content to determine real industry and business type
        actual_industry, actual_business_type = self._analyze_business_content(website_data)
        
        template = self.message_templates.get(message_type, self.message_templates['general'])
        
        prompt = template['prompt'].format(
            company_name=website_data.get('companyName', ''),
            industry=actual_industry,  # Use analyzed industry
            businessType=actual_business_type,  # Use analyzed business type
            aboutUsContent=website_data.get('aboutUsContent', '')[:800]  # Use more content
        )
        
        try:
            response = self.model.generate_content(prompt)
            message = response.text
            
            # Check if the response is valid
            if not message or message.strip() == "":
                logger.warning("AI generated empty message")
                return "", 0.0
            
            confidence_score = self._calculate_confidence_score(message, website_data)
            return message, confidence_score
            
        except Exception as e:
            logger.error(f"Error generating AI message: {e}")
            
            # Check if it's a quota limit error
            if "quota" in str(e).lower() or "429" in str(e):
                logger.warning("Gemini API quota limit reached")
                return "", 0.0
            else:
                logger.error(f"AI generation failed with error: {e}")
                return "", 0.0
    
    def generate_with_predefined_examples(self, website_data: Dict, message_type: str) -> Tuple[str, float]:
        """Generate message using predefined messages as examples"""
        
        if not self.predefined_integration:
            return self.generate_pure_ai_message(website_data, message_type)
        
        prompt = self.predefined_integration.create_ai_prompt_with_predefined_messages(website_data, message_type)
        
        try:
            response = self.model.generate_content(prompt)
            message = response.text
            
            confidence_score = self._calculate_confidence_score(message, website_data)
            return message, confidence_score
            
        except Exception as e:
            logger.error(f"Error generating message with predefined examples: {e}")
            return self.generate_pure_ai_message(website_data, message_type)
    
    def _analyze_business_content(self, website_data: Dict) -> Tuple[str, str]:
        """Analyze actual business content to determine real industry and business type"""
        
        company_name = website_data.get('companyName', '')
        about_us_content = website_data.get('aboutUsContent', '')
        website_url = website_data.get('websiteUrl', '')
        
        # Create analysis prompt for Gemini
        analysis_prompt = f"""
        Analyze this business and determine their ACTUAL industry and business type based on the content provided.
        
        Company Name: {company_name}
        Website URL: {website_url}
        About Us Content: {about_us_content[:1000]}
        
        Based on the actual content, determine:
        1. What industry does this business actually operate in?
        2. What type of business is this?
        
        Look for keywords and context clues in the content, not just the company name.
        
        Return your analysis in this exact JSON format:
        {{
            "actual_industry": "the real industry they operate in",
            "actual_business_type": "the real type of business they are",
            "confidence": 0.0-1.0,
            "reasoning": "brief explanation of why you determined this"
        }}
        
        Examples:
        - If it's a real estate company, industry should be "Real Estate" not "Automotive"
        - If it's an insurance company, industry should be "Insurance" not "Automotive"
        - If it's a car dealership, industry should be "Automotive"
        - If it's a property management company, business_type should be "Property Management"
        """
        
        try:
            response = self.model.generate_content(analysis_prompt)
            analysis_text = response.text
            
            # Extract JSON from response
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
                actual_industry = analysis_data.get('actual_industry', website_data.get('industry', 'Business'))
                actual_business_type = analysis_data.get('actual_business_type', website_data.get('businessType', 'Business'))
                
                logger.info(f"Business analysis for {company_name}: {actual_industry} - {actual_business_type}")
                return actual_industry, actual_business_type
            else:
                logger.warning(f"Could not parse business analysis JSON for {company_name}")
                return website_data.get('industry', 'Business'), website_data.get('businessType', 'Business')
                
        except Exception as e:
            logger.error(f"Error analyzing business content for {company_name}: {e}")
            return website_data.get('industry', 'Business'), website_data.get('businessType', 'Business')
    
    def _calculate_confidence_score(self, message: str, context_data: Dict) -> float:
        """Calculate confidence score for generated message"""
        
        score = 0.5  # Base score
        
        # Length check
        if 100 <= len(message) <= 300:
            score += 0.1
        
        # Personalization check
        company_name = context_data.get('companyName', '').lower()
        if company_name and company_name in message.lower():
            score += 0.2
        
        # Industry mention
        industry = context_data.get('industry', '').lower()
        if industry and industry in message.lower():
            score += 0.1
        
        # Professional tone indicators
        professional_words = ['collaboration', 'partnership', 'opportunity', 'business', 'professional']
        if any(word in message.lower() for word in professional_words):
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_fallback_message(self, website_data: Dict, message_type: str) -> str:
        """Generate fallback message when AI fails - return empty string instead of hardcoded message"""
        
        # Return empty string instead of hardcoded fallback messages
        return ""
    
    def generate_batch_messages(self, websites_data: List[Dict], message_type: str = "general") -> List[Dict]:
        """Generate messages for multiple websites efficiently"""
        
        results = []
        
        for website in websites_data:
            try:
                message, confidence = self.generate_message(website, message_type)
                
                results.append({
                    'website_id': website.get('id'),
                    'website_url': website.get('website_url'),
                    'generatedMessage': message,
                    'confidence_score': confidence,
                    'message_type': message_type,
                    'success': True
                })
                
            except Exception as e:
                logger.error(f"Error generating message for {website.get('website_url')}: {e}")
                results.append({
                    'website_id': website.get('id'),
                    'website_url': website.get('website_url'),
                    'generatedMessage': "",  # Return empty string instead of fallback
                    'confidence_score': 0.0,  # Set confidence to 0 for failed generations
                    'message_type': message_type,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def test_connection(self) -> bool:
        """Test Gemini API connection"""
        try:
            response = self.model.generate_content("Hello, this is a test message.")
            return True
        except Exception as e:
            logger.error(f"Gemini API connection test failed: {e}")
            return False

# Global instance
gemini_generator = None

def get_gemini_generator() -> GeminiMessageGenerator:
    """Get or create Gemini message generator instance"""
    global gemini_generator
    if gemini_generator is None:
        gemini_generator = GeminiMessageGenerator()
    return gemini_generator 