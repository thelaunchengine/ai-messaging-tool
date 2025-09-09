# 🚀 AI Messaging Tool - API Documentation

## 📋 **Overview**

This document provides a comprehensive list of all available APIs for both the **Frontend (Next.js)** and **Backend (Python/FastAPI)** components of the AI Messaging Tool.

### **Base URLs**
- **Backend**: `http://103.215.159.51:8000`
- **Frontend**: `http://103.215.159.51:3001`

---

## 🔧 **Backend APIs (Python/FastAPI)**

### **Health & System**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/` | Root endpoint |
| `GET` | `/api/monitoring/system-metrics` | Get system metrics |
| `GET` | `/api/monitoring/task-metrics` | Get task metrics |
| `GET` | `/api/monitoring/detailed-activities` | Get detailed system activities |
| `GET` | `/api/config/testing` | Get testing configuration |

### **File Upload & Processing**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload-file` | Upload file for processing |
| `POST` | `/api/upload-from-frontend` | Upload file from frontend |
| `POST` | `/api/process-file` | Process uploaded file |
| `POST` | `/api/process-chunk` | Process file chunk |
| `GET` | `/api/upload` | Get file uploads with pagination |
| `GET` | `/api/upload/{fileUploadId}/websites` | Get websites for specific upload |
| `GET` | `/api/file-uploads/history` | Get file upload history |

### **Website Scraping**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/scrape` | Trigger website scraping |
| `GET` | `/api/scraping/results/{fileUploadId}` | Get scraping results |
| `POST` | `/api/scraping/trigger-manual/{fileUploadId}` | Manually trigger scraping |
| `GET` | `/api/monitoring/website-activities/{fileUploadId}` | Get website activities |
| `GET` | `/api/monitoring/website-details/{fileUploadId}` | Get detailed website info |

### **AI Message Generation**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate-messages` | Generate AI messages |
| `POST` | `/api/workflow/trigger-ai-generation` | Trigger AI generation workflow |
| `POST` | `/api/ai/generate-single-message` | Generate single AI message |
| `POST` | `/api/ai/generate-preview` | Generate message preview |
| `POST` | `/api/message-generation/hybrid` | Hybrid message generation |
| `POST` | `/api/message-generation/with-predefined-examples` | Generate with predefined examples |
| `POST` | `/api/message-generation/generate-for-selected` | Generate for selected websites |
| `POST` | `/api/message-generation/bulk-generate` | Bulk message generation |

### **Predefined Messages**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/predefined-messages` | Get all predefined messages |
| `POST` | `/api/predefined-messages` | Create predefined message |
| `GET` | `/api/predefined-messages/{message_id}` | Get specific predefined message |
| `PUT` | `/api/predefined-messages/{message_id}` | Update predefined message |
| `DELETE` | `/api/predefined-messages/{message_id}` | Delete predefined message |
| `GET` | `/api/predefined-messages/statistics` | Get message statistics |

### **Website Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/websites/with-messages` | Get websites with messages |
| `GET` | `/api/websites/without-messages` | Get websites without messages |
| `GET` | `/api/websites/by-file-upload/{fileUploadId}` | Get websites by file upload |

### **Form Submission**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/submit-forms` | Submit contact forms |
| `GET` | `/api/form-submission/status/{task_id}` | Get form submission status |
| `POST` | `/api/form-submission/submit-for-selected` | Submit forms for selected websites |

### **Contact Inquiries**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/contact-inquiries/website/{website_id}` | Get inquiries by website |
| `GET` | `/api/contact-inquiries/user/{userId}` | Get inquiries by user |
| `GET` | `/api/contact-inquiries/statistics` | Get inquiry statistics |

### **Task Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tasks` | Get all tasks |
| `DELETE` | `/api/task/{task_id}` | Delete specific task |
| `GET` | `/api/task-status/{task_id}` | Get task status |

### **Workflow Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/workflow/progress/{fileUploadId}` | Get workflow progress |

---

## 🎨 **Frontend APIs (Next.js)**

### **Authentication**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | User login |
| `POST` | `/api/auth/register` | User registration |
| `POST` | `/api/auth/forgot-password` | Forgot password |
| `POST` | `/api/auth/reset-password` | Reset password |
| `GET` | `/api/auth/protected` | Check protected route access |

### **User Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users` | Get all users |
| `POST` | `/api/users` | Create new user |
| `GET` | `/api/users/[id]` | Get user by ID |
| `PUT` | `/api/users/[id]` | Update user |
| `DELETE` | `/api/users/[id]` | Delete user |

### **File Upload Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload file |
| `GET` | `/api/upload` | Get uploads with pagination |
| `GET` | `/api/upload/[id]` | Get specific upload |
| `DELETE` | `/api/upload/[id]` | Delete upload |
| `GET` | `/api/upload/[id]/websites` | Get websites for upload |
| `GET` | `/api/upload/[id]/download` | Download upload file |

### **Website Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/websites/by-file-upload/[fileUploadId]` | Get websites by file upload |
| `GET` | `/api/websites/with-messages` | Get websites with messages |
| `GET` | `/api/websites/without-messages` | Get websites without messages |

### **Message Generation**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate-messages` | Generate messages |
| `POST` | `/api/message-generation/generate-for-selected` | Generate for selected websites |
| `POST` | `/api/workflow/trigger-ai-generation` | Trigger AI generation workflow |

### **Predefined Messages**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/predefined-messages` | Get all predefined messages |
| `POST` | `/api/predefined-messages` | Create predefined message |
| `GET` | `/api/predefined-messages/[id]` | Get specific predefined message |
| `PUT` | `/api/predefined-messages/[id]` | Update predefined message |
| `DELETE` | `/api/predefined-messages/[id]` | Delete predefined message |

### **Scraping Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/scraping/jobs` | Get scraping jobs |
| `POST` | `/api/scraping/jobs` | Create scraping job |
| `GET` | `/api/scraping/jobs/[id]` | Get specific scraping job |
| `PATCH` | `/api/scraping/jobs/[id]` | Update scraping job |
| `DELETE` | `/api/scraping/jobs/[id]` | Delete scraping job |
| `POST` | `/api/scraping/jobs/[id]/start` | Start scraping job |
| `POST` | `/api/scraping/jobs/[id]/stop` | Stop scraping job |
| `POST` | `/api/scraping/jobs/[id]/pause` | Pause scraping job |
| `POST` | `/api/scraping/jobs/[id]/resume` | Resume scraping job |
| `POST` | `/api/scraping/trigger-manual/[fileUploadId]` | Trigger manual scraping |
| `GET` | `/api/scraping/config` | Get scraping configuration |
| `POST` | `/api/scraping/config` | Update scraping configuration |

### **Form Submission**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/form-submission/submit-for-selected` | Submit forms for selected websites |
| `POST` | `/api/contact` | Submit contact form |

### **Monitoring & Analytics**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/monitoring/system-metrics` | Get system metrics |
| `GET` | `/api/monitoring/task-metrics` | Get task metrics |
| `GET` | `/api/monitoring/detailed-activities` | Get detailed activities |
| `GET` | `/api/monitoring/website-details/[fileUploadId]` | Get website details |

### **Admin Functions**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/admin/dashboard/stats` | Get admin dashboard statistics |
| `GET` | `/api/admin/reports` | Get admin reports |
| `GET` | `/api/admin/reports/user/[userId]/download` | Download user report |
| `GET` | `/api/admin/history` | Get admin history |
| `GET` | `/api/admin/history/[id]/download` | Download history file |
| `POST` | `/api/admin/upload` | Admin file upload |
| `GET` | `/api/admin/upload` | Get admin uploads |
| `GET` | `/api/admin/upload/[fileUploadId]/progress` | Get upload progress |
| `GET` | `/api/admin/upload/[fileUploadId]/download` | Download admin upload |
| `POST` | `/api/admin/upload/[fileUploadId]/batch/[batchNumber]/start-scraping` | Start batch scraping |
| `POST` | `/api/admin/upload/[fileUploadId]/batch/[batchNumber]/stop-scraping` | Stop batch scraping |

### **Workflow Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/workflow/progress/[fileUploadId]` | Get workflow progress |

### **Debug & Testing**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/debug-session` | Get debug session info |
| `GET` | `/api/test` | Test endpoint |

---

## 🔄 **API Integration Patterns**

### **Frontend → Backend Communication**
- Frontend makes API calls to backend at `http://103.215.159.51:8000`
- Backend processes requests and returns responses
- Frontend handles responses and updates UI accordingly

### **Data Flow**
1. **File Upload**: Frontend → Backend API → Database
2. **Website Scraping**: Backend → External websites → Database
3. **AI Generation**: Backend → Gemini API → Database
4. **Data Display**: Backend → Frontend → UI Components

### **Error Handling**
- Backend returns appropriate HTTP status codes
- Frontend handles errors gracefully with user-friendly messages
- Logging and monitoring for debugging

---

## 📊 **Response Formats**

### **Standard Response Structure**
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully",
  "pagination": {
    "page": 1,
    "limit": 10,
    "totalCount": 100,
    "totalPages": 10,
    "hasNextPage": true,
    "hasPreviousPage": false
  }
}
```

### **Error Response Structure**
```json
{
  "success": false,
  "error": "Error message",
  "details": "Additional error details",
  "statusCode": 400
}
```

---

## 🚀 **Usage Examples**

### **Upload File**
```bash
curl -X POST http://103.215.159.51:8000/api/upload-file \
  -F "file=@websites.csv" \
  -F "userId=user123"
```

### **Generate AI Messages**
```bash
curl -X POST http://103.215.159.51:8000/api/generate-messages \
  -H "Content-Type: application/json" \
  -d '{
    "websites": ["example.com"],
    "messageType": "general"
  }'
```

### **Get File Uploads**
```bash
curl "http://103.215.159.51:8000/api/upload?userId=user123&page=1&limit=10"
```

---

## 📝 **Notes**

- **Authentication**: Most endpoints require valid user session
- **Rate Limiting**: Backend implements rate limiting for API calls
- **CORS**: Backend configured to accept requests from frontend
- **WebSocket**: Real-time updates available at `/ws/{client_id}`
- **File Types**: Supports CSV, Excel files for website processing
- **AI Models**: Currently uses Google Gemini API for message generation

---

## 🔧 **Development & Testing**

### **Local Development**
- **Backend**: `http://localhost:8000`
- **Frontend**: `http://localhost:3001`

### **Health Checks**
```bash
# Backend health
curl http://103.215.159.51:8000/health

# Frontend health
curl http://103.215.159.51:3001
```

### **Monitoring**
- Use `/api/monitoring/*` endpoints for system health
- Check PM2 logs for service status
- Monitor database connections and performance

---

*Last Updated: December 2024*
*Version: 1.0.0*
