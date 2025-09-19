# Testing Configuration for AI Messaging Tool

## Overview
This document explains the testing configuration options for limiting AI message generation during development and testing phases.

## Configuration Options

### 1. Testing Mode
**Environment Variable:** `TESTING_MODE_ENABLED`
**Default Value:** `true`
**Purpose:** Enables/disables testing mode with limited AI message generation

### 2. Maximum AI Messages Per File
**Environment Variable:** `MAX_AI_MESSAGES_PER_FILE`
**Default Value:** `2`
**Purpose:** Limits the number of AI-generated messages per CSV file upload

## How It Works

When `TESTING_MODE_ENABLED=true`:
- Only the first N successfully scraped websites will generate AI messages
- N is determined by `MAX_AI_MESSAGES_PER_FILE`
- Remaining websites will be skipped for AI message generation
- This helps control costs and test functionality with limited data

When `TESTING_MODE_ENABLED=false`:
- All successfully scraped websites will generate AI messages
- No limit is applied
- Full production behavior

## Environment Variable Setup

### Linux/Mac
```bash
# Enable testing mode with 2 messages per file
export TESTING_MODE_ENABLED=true
export MAX_AI_MESSAGES_PER_FILE=2

# Or disable testing mode for production
export TESTING_MODE_ENABLED=false
```

### Windows
```cmd
# Enable testing mode with 2 messages per file
set TESTING_MODE_ENABLED=true
set MAX_AI_MESSAGES_PER_FILE=2

# Or disable testing mode for production
set TESTING_MODE_ENABLED=false
```

### Docker/PM2
```bash
# Add to your environment configuration
TESTING_MODE_ENABLED=true
MAX_AI_MESSAGES_PER_FILE=2
```

## Example Scenarios

### Scenario 1: Testing with 2 Messages
```bash
export TESTING_MODE_ENABLED=true
export MAX_AI_MESSAGES_PER_FILE=2
```
**Result:** Upload CSV with 20 websites → Only first 2 successfully scraped websites get AI messages

### Scenario 2: Testing with 5 Messages
```bash
export TESTING_MODE_ENABLED=true
export MAX_AI_MESSAGES_PER_FILE=5
```
**Result:** Upload CSV with 20 websites → Only first 5 successfully scraped websites get AI messages

### Scenario 3: Production Mode
```bash
export TESTING_MODE_ENABLED=false
```
**Result:** Upload CSV with 20 websites → All successfully scraped websites get AI messages

## Benefits

1. **Cost Control:** Limits Gemini API calls during testing
2. **Faster Testing:** Quicker feedback on AI message quality
3. **Resource Management:** Prevents overwhelming the system during development
4. **Easy Configuration:** Simple environment variable control
5. **Production Ready:** Can be easily disabled for full functionality

## Monitoring

The system logs the testing limit status:
```
INFO: Testing mode enabled: true
INFO: Maximum AI messages per file: 2
INFO: Testing limit reached (2 messages). Skipping remaining websites.
INFO: Message generation completed. Processed 2/20 websites, Generated: 2/2, Failed: 0
```

## Recommendations

- **Development:** Use `TESTING_MODE_ENABLED=true` with `MAX_AI_MESSAGES_PER_FILE=2-5`
- **Staging:** Use `TESTING_MODE_ENABLED=true` with `MAX_AI_MESSAGES_PER_FILE=10-20`
- **Production:** Use `TESTING_MODE_ENABLED=false` for unlimited message generation
