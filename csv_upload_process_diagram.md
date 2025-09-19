# CSV Upload Process Flow Diagram

```mermaid
graph TD
    A[User Uploads CSV File] --> B[Frontend: Next.js API Route]
    B --> C[Validate CSV Format]
    C --> D[Send to Backend: FastAPI]
    D --> E[Backend: /api/upload-from-frontend]
    E --> F[Check for Duplicate Upload]
    F --> G[Save File to Backend Directory]
    G --> H[Create File Upload Record in Database]
    H --> I[Start Celery Task: process_csv_file_task]
    
    I --> J[Parse CSV URLs]
    J --> K[Create Website Records in Database]
    K --> L[Start Scraping Task: scrape_websites_task]
    
    L --> M[For Each Website URL]
    M --> N[RobustWebScraper: Scrape Website]
    N --> O[Extract Contact Form Information]
    O --> P[Extract About Us Content]
    P --> Q[Update Website Record with Scraping Results]
    
    Q --> R[Check if AI Message Generation Needed]
    R --> S[Start AI Message Generation Task]
    S --> T[Business Content Analysis using Gemini]
    T --> U[Determine Actual Industry & Business Type]
    U --> V[Generate Industry-Specific Message using Gemini 1.5 Pro]
    V --> W[Update Website Record with Generated Message]
    
    W --> X[Start Form Submission Task]
    X --> Y[IntelligentFormSubmitter: Submit Contact Forms]
    
    Y --> Z[AI Strategy Selection]
    Z --> AA[Primary: Traditional Form Submission]
    AA --> BB[Enhanced Form Detection - 5 Strategies]
    BB --> CC[Strategy 1: AI-Detected Form Elements]
    BB --> DD[Strategy 2: Common Form Selectors]
    BB --> EE[Strategy 3: Find Any Form on Page]
    BB --> FF[Strategy 4: Trace Input Field Parents]
    BB --> GG[Strategy 5: Create Virtual Form from Inputs]
    
    CC --> HH[Enhanced Field Filling - 2 Strategies]
    DD --> HH
    EE --> HH
    FF --> HH
    GG --> HH
    
    HH --> II[Strategy 1: AI Field Mappings]
    HH --> JJ[Strategy 2: Enhanced Common Field Selectors]
    
    II --> KK[Enhanced Form Submission - 4 Strategies]
    JJ --> KK
    
    KK --> LL[Strategy 1: Common Submit Button Selectors]
    KK --> MM[Strategy 2: Find Buttons by Text Content]
    KK --> NN[Strategy 3: Find Clickable Elements]
    KK --> OO[Strategy 4: JavaScript Form Submission]
    
    LL --> PP[Form Submission Success?]
    MM --> PP
    NN --> PP
    OO --> PP
    
    PP -->|Yes| QQ[Verify Success with Response Analysis]
    PP -->|No| RR[Try AI-Recommended Fallback Strategy]
    
    QQ --> SS[Success Indicators Found?]
    SS -->|Yes| TT[Update Website Record: SUBMITTED]
    SS -->|No| RR
    
    RR --> UU[Fallback: AJAX Submission]
    RR --> VV[Fallback: Modal Submission]
    RR --> WW[Fallback: Alternative Contact Methods]
    
    UU --> XX[Fallback Success?]
    VV --> XX
    WW --> XX
    
    XX -->|Yes| TT
    XX -->|No| YY[Update Website Record: FAILED]
    
    TT --> AAA[Log Submission Results]
    YY --> AAA
    AAA --> BBB[Update File Upload Progress]
    BBB --> CCC[Check if All Websites Processed]
    CCC -->|No| M
    CCC -->|Yes| DDD[Complete File Upload Processing]
    
    DDD --> EEE[Update File Upload Status: COMPLETED]
    EEE --> FFF[Send Results to Frontend]
    FFF --> GGG[Display Results in UI]
    
    %% Error Handling
    N -->|Scraping Error| HHH[Update Website: Scraping Failed]
    T -->|AI Error| III[Update Website: Message Generation Failed]
    Y -->|Submission Error| JJJ[Update Website: Submission Failed]
    
    HHH --> BBB
    III --> BBB
    JJJ --> BBB
    
    %% Browser Selection Logic
    AA --> KKK[Browser Selection Strategy]
    KKK --> LLL[Dynamic Content Detected?]
    LLL -->|Yes| MMM[Use Firefox with Marionette Fixes]
    LLL -->|No| NNN[Use Chrome with Optimized Options]
    
    MMM --> BB
    NNN --> BB
    
    %% CAPTCHA Handling
    BB --> OOO[CAPTCHA Detected?]
    OOO -->|Yes| PPP[CaptchaHandler: Solve CAPTCHA]
    OOO -->|No| HH
    PPP -->|Success| HH
    PPP -->|Failed| QQQ[Update Website: CAPTCHA Failed]
    
    %% Smart Field Handling
    HH --> RRR[Unknown Required Fields?]
    RRR -->|Yes| SSS[SmartFieldHandler: Analyze Unknown Fields]
    RRR -->|No| KK
    SSS --> TTT[Generate Appropriate Values]
    TTT --> KK
    
    %% Styling
    classDef userAction fill:#e1f5fe
    classDef frontend fill:#f3e5f5
    classDef backend fill:#e8f5e8
    classDef database fill:#fff3e0
    classDef ai fill:#fce4ec
    classDef success fill:#c8e6c9
    classDef error fill:#ffcdd2
    classDef strategy fill:#fff9c4
    
    class A userAction
    class B,C frontend
    class D,E,G,H,I backend
    class F,K,Q,W,TT,YY,AAA,BBB,CCC,DDD,EEE,FFF,GGG database
    class T,U,V,PPP,SSS,TTT ai
    class TT,DDD,EEE,FFF,GGG success
    class HHH,III,JJJ,QQQ error
    class Y,Z,AA,BB,HH,KK,LL,MM,NN,OO,PP,QQ,RR,SS,UU,VV,WW,XX,KKK,LLL,MMM,NNN,OOO,RRR strategy
```

## Process Flow Summary

### 1. **CSV Upload Phase**
- User uploads CSV file through frontend
- Frontend validates and sends to backend
- Backend saves file and creates database records
- Celery task starts processing

### 2. **Website Scraping Phase**
- Parse CSV to extract website URLs
- For each URL: scrape website content
- Extract contact form information and about us content
- Update database with scraping results

### 3. **AI Message Generation Phase (Enhanced)**
- **Business Content Analysis:** Use Gemini to analyze actual business content
- **Industry Detection:** Determine real industry from About Us content (not just field values)
- **Business Type Analysis:** Identify actual business type from scraped content
- **Industry-Specific Generation:** Generate messages relevant to actual business focus
- **Enhanced Prompts:** Use detailed prompts with more content (800 chars vs 500)
- Update database with generated messages

### 4. **Form Submission Phase (Enhanced with Multiple Strategies)**

#### **Primary Strategy: Traditional Form Submission (Enhanced)**
- **Form Detection (5 Strategies):**
  1. AI-detected form elements
  2. Common form selectors (expanded patterns)
  3. Find any form on page
  4. Trace input field parents to find forms
  5. Create virtual forms from input fields

- **Field Filling (2 Strategies):**
  1. AI field mappings
  2. Enhanced common field selectors (expanded patterns for name, email, message, phone, company)

- **Form Submission (4 Strategies):**
  1. Common submit button selectors (expanded)
  2. Find buttons by text content (expanded keywords)
  3. Find clickable elements that might submit
  4. JavaScript form submission

- **Success Verification:**
  - Check for success indicators in response
  - Verify URL changes
  - Analyze response content for errors

#### **Fallback Strategies:**
- AJAX submission
- Modal submission
- Alternative contact methods (email)

### 5. **Browser Selection Logic**
- Dynamic content detected → Firefox with Marionette fixes
- Standard content → Chrome with optimized options
- Automatic fallback between browsers

### 6. **Advanced Features**
- **CAPTCHA Handling:** Automatic detection and solving
- **Smart Field Handling:** AI analysis of unknown required fields
- **Error Recovery:** Multiple fallback strategies
- **Progress Tracking:** Real-time status updates

### 7. **Result Processing**
- Update website records with submission results
- Track success/failure rates
- Complete file upload processing
- Display results in frontend UI
