/**
 * Status normalization utilities for consistent status display across the application
 */

export type NormalizedStatus = 'pending' | 'processing' | 'completed' | 'partially-completed' | 'failed';

export interface StatusInfo {
  status: NormalizedStatus;
  label: string;
  color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
}

/**
 * Normalizes backend status codes to user-friendly statuses
 * @param status - Raw backend status string
 * @returns Normalized status information
 */
export function normalizeStatus(status: string): StatusInfo {
  if (!status) {
    return {
      status: 'pending',
      label: 'Pending',
      color: 'default'
    };
  }
  
  const statusLower = status.toLowerCase();
  
  // PENDING statuses - not started yet
  if (statusLower.includes('pending') || 
      statusLower.includes('uploaded') ||
      statusLower.includes('queued')) {
    return {
      status: 'pending',
      label: 'Pending',
      color: 'default'
    };
  }
  
  // PROCESSING statuses - currently in progress
  if (statusLower.includes('processing') || 
      statusLower.includes('uploading') ||
      statusLower.includes('scraping') ||
      statusLower.includes('in_progress')) {
    return {
      status: 'processing',
      label: 'Processing',
      color: 'warning'
    };
  }
  
  // COMPLETED statuses - fully successful
  if (statusLower.includes('completed') && 
      !statusLower.includes('partial') &&
      !statusLower.includes('failed')) {
    return {
      status: 'completed',
      label: 'Completed',
      color: 'success'
    };
  }
  
  // PARTIALLY COMPLETED statuses - some success, some failure
  if (statusLower.includes('partial') ||
      statusLower.includes('some') ||
      (statusLower.includes('completed') && statusLower.includes('partial')) ||
      statusLower.includes('contact_form_submission_partial')) {
    return {
      status: 'partially-completed',
      label: 'Partially Completed',
      color: 'info'
    };
  }
  
  // FAILED statuses - complete failure
  if (statusLower.includes('failed') || 
      statusLower.includes('error') ||
      statusLower.includes('fail') ||
      statusLower.includes('ai_generation_failed') ||
      statusLower.includes('contact_form_submission_failed') ||
      statusLower.includes('scraping_failed')) {
    return {
      status: 'failed',
      label: 'Failed',
      color: 'error'
    };
  }
  
  // Default to pending for unknown statuses
  return {
    status: 'pending',
    label: 'Pending',
    color: 'default'
  };
}

/**
 * Gets the appropriate color for a normalized status
 * @param status - Normalized status
 * @returns Material-UI color string
 */
export function getStatusColor(status: NormalizedStatus): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' {
  switch (status) {
    case 'completed':
      return 'success';
    case 'processing':
      return 'warning';
    case 'partially-completed':
      return 'info';
    case 'failed':
      return 'error';
    case 'pending':
    default:
      return 'default';
  }
}

/**
 * Determines the overall status based on individual component statuses
 * @param scrapingStatus - Status of scraping phase
 * @param aiStatus - Status of AI message generation phase  
 * @param formStatus - Status of form submission phase
 * @returns Overall normalized status
 */
export function determineOverallStatus(
  scrapingStatus: string,
  aiStatus: string,
  formStatus: string
): StatusInfo {
  const scraping = normalizeStatus(scrapingStatus);
  const ai = normalizeStatus(aiStatus);
  const form = normalizeStatus(formStatus);
  
  // If any phase is still processing, overall is processing
  if (scraping.status === 'processing' || ai.status === 'processing' || form.status === 'processing') {
    return {
      status: 'processing',
      label: 'Processing',
      color: 'warning'
    };
  }
  
  // If all phases are completed, overall is completed
  if (scraping.status === 'completed' && ai.status === 'completed' && form.status === 'completed') {
    return {
      status: 'completed',
      label: 'Completed',
      color: 'success'
    };
  }
  
  // If any phase failed but others succeeded, it's partially completed
  if (scraping.status === 'failed' || ai.status === 'failed' || form.status === 'failed') {
    return {
      status: 'partially-completed',
      label: 'Partially Completed',
      color: 'info'
    };
  }
  
  // If all phases failed, overall is failed
  if (scraping.status === 'failed' && ai.status === 'failed' && form.status === 'failed') {
    return {
      status: 'failed',
      label: 'Failed',
      color: 'error'
    };
  }
  
  // Default to pending
  return {
    status: 'pending',
    label: 'Pending',
    color: 'default'
  };
}
