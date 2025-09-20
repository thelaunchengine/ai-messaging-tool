"""
Form detection utilities to avoid circular imports
"""
from bs4 import BeautifulSoup
from typing import Dict, Any

def is_contact_form(form) -> bool:
    """Better classification of contact forms vs other forms"""
    form_text = form.get_text().lower()
    form_action = form.get('action', '').lower()
    form_id = form.get('id', '').lower()
    form_class = ' '.join(form.get('class', [])).lower()
    
    # Exclude search forms
    if any(keyword in form_text for keyword in ['search', 'find', 'look for', 'query']):
        return False
    
    # Exclude newsletter forms
    if any(keyword in form_text for keyword in ['newsletter', 'subscribe', 'email list', 'sign up']):
        return False
    
    # Exclude pincode/zipcode forms
    if any(keyword in form_text for keyword in ['pincode', 'zipcode', 'postal code', 'delivery']):
        return False
    
    # Exclude login forms
    if any(keyword in form_text for keyword in ['login', 'sign in', 'password', 'username']):
        return False
    
    # Look for contact-specific keywords
    contact_keywords = ['contact', 'message', 'inquiry', 'reach', 'get in touch', 'send message']
    return any(keyword in form_text for keyword in contact_keywords) or \
           any(keyword in form_action for keyword in contact_keywords) or \
           any(keyword in form_id for keyword in contact_keywords) or \
           any(keyword in form_class for keyword in contact_keywords)

def detect_wordpress_cf7_form(form) -> bool:
    """Detect if this is a WordPress Contact Form 7 form"""
    form_class = ' '.join(form.get('class', [])).lower()
    form_action = form.get('action', '').lower()
    
    # CF7 forms have specific class patterns
    cf7_indicators = ['wpcf7-form', 'contact-form-7', 'wpcf7']
    
    return any(indicator in form_class for indicator in cf7_indicators) or \
           '#wpcf7-' in form_action

def handle_wordpress_cf7_form(form, form_url: str, base_url: str) -> Dict[str, Any]:
    """Handle WordPress Contact Form 7 forms with AJAX submission"""
    try:
        # Extract form ID from action or class
        form_action = form.get('action', '')
        form_class = ' '.join(form.get('class', []))
        
        # Find the form ID
        form_id = None
        if '#wpcf7-' in form_action:
            form_id = form_action.split('#wpcf7-')[1].split('-')[0]
        elif 'wpcf7-form' in form_class:
            # Try to extract from class or hidden inputs
            hidden_inputs = form.find_all('input', {'type': 'hidden'})
            for inp in hidden_inputs:
                if inp.get('name') == '_wpcf7':
                    form_id = inp.get('value')
                    break
        
        if not form_id:
            return {'success': False, 'error': 'Could not extract CF7 form ID'}
        
        # Create the AJAX submission URL
        ajax_url = f"{base_url}/wp-json/contact-form-7/v1/contact-forms/{form_id}/feedback"
        
        # Extract form data
        form_data = {}
        inputs = form.find_all(['input', 'textarea', 'select'])
        
        for inp in inputs:
            name = inp.get('name')
            if name:
                value = inp.get('value', '')
                if inp.name == 'textarea':
                    value = inp.get_text()
                elif inp.get('type') == 'checkbox':
                    value = '1' if inp.get('checked') else '0'
                elif inp.get('type') == 'radio':
                    if inp.get('checked'):
                        form_data[name] = value
                else:
                    form_data[name] = value
        
        # Add required CF7 fields if missing
        if '_wpcf7' not in form_data:
            form_data['_wpcf7'] = form_id
        if '_wpcf7_version' not in form_data:
            form_data['_wpcf7_version'] = '5.7.7'
        if '_wpcf7_locale' not in form_data:
            form_data['_wpcf7_locale'] = 'en_US'
        if '_wpcf7_unit_tag' not in form_data:
            form_data['_wpcf7_unit_tag'] = f'wpcf7-f{form_id}-p1-o1'
        
        return {
            'success': True,
            'ajax_url': ajax_url,
            'form_data': form_data,
            'form_id': form_id,
            'method': 'ajax'
        }
        
    except Exception as e:
        return {'success': False, 'error': f'CF7 form handling error: {str(e)}'}
