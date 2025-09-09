class WebSocketManager {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private clientId: string;
  private eventListeners: Map<string, Set<(data: any) => void>> = new Map();

  constructor() {
    this.clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.initializeSocket();
  }

  private initializeSocket() {
    try {
      const wsUrl = process.env.NEXT_PUBLIC_BACKEND_WS_URL || 'ws://103.215.159.51:8001';
      this.socket = new WebSocket(`${wsUrl}/ws/${this.clientId}`);

      this.setupEventListeners();
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
    }
  }

  private setupEventListeners() {
    if (!this.socket) return;

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.socket.onclose = (event) => {
      console.log('WebSocket disconnected:', event.reason);
      this.scheduleReconnect();
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
      }
    };

    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  }

  private handleMessage(message: any) {
    const { type, data } = message;
    
    // Handle system metrics broadcast
    if (type === 'system_metrics') {
      const listeners = this.eventListeners.get('system_metrics');
      if (listeners) {
        listeners.forEach(callback => callback(data));
      }
    }
    
    // Handle task progress updates
    if (type === 'task_progress') {
      const listeners = this.eventListeners.get(`task_progress_${data.task_id}`);
      if (listeners) {
        listeners.forEach(callback => callback(data));
      }
    }
    
    // Handle file upload progress
    if (type === 'file_upload_progress') {
      const listeners = this.eventListeners.get(`file_upload_progress_${data.file_upload_id}`);
      if (listeners) {
        listeners.forEach(callback => callback(data));
      }
    }
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        console.log(`Attempting to reconnect... (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
        this.initializeSocket();
      }, this.reconnectDelay * (this.reconnectAttempts + 1));
    }
  }

  // Subscribe to system metrics
  public subscribeToSystemMetrics(callback: (data: any) => void) {
    this.addEventListener('system_metrics', callback);
  }

  // Subscribe to task progress updates
  public subscribeToTaskProgress(taskId: string, callback: (data: any) => void) {
    this.addEventListener(`task_progress_${taskId}`, callback);
    
    // Send subscription message to server
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'subscribe_task',
        task_id: taskId
      }));
    }
  }

  // Subscribe to file upload progress
  public subscribeToFileUploadProgress(fileUploadId: string, callback: (data: any) => void) {
    this.addEventListener(`file_upload_progress_${fileUploadId}`, callback);
    
    // Send subscription message to server
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'subscribe_file_upload',
        file_upload_id: fileUploadId
      }));
    }
  }

  // Subscribe to scraping job updates
  public subscribeToScrapingJob(jobId: string, callback: (data: any) => void) {
    this.addEventListener(`scraping_job_update_${jobId}`, callback);
    
    // Send subscription message to server
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'subscribe_scraping_job',
        job_id: jobId
      }));
    }
  }

  // Subscribe to message generation updates
  public subscribeToMessageGeneration(fileUploadId: string, callback: (data: any) => void) {
    this.addEventListener(`message_generation_update_${fileUploadId}`, callback);
    
    // Send subscription message to server
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'subscribe_message_generation',
        file_upload_id: fileUploadId
      }));
    }
  }

  // Subscribe to form submission updates
  public subscribeToFormSubmission(fileUploadId: string, callback: (data: any) => void) {
    this.addEventListener(`form_submission_update_${fileUploadId}`, callback);
    
    // Send subscription message to server
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'subscribe_form_submission',
        file_upload_id: fileUploadId
      }));
    }
  }

  private addEventListener(event: string, callback: (data: any) => void) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    this.eventListeners.get(event)!.add(callback);
  }

  // Unsubscribe from updates
  public unsubscribe(event: string) {
    this.eventListeners.delete(event);
  }

  // Disconnect WebSocket
  public disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  // Get connection status
  public isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}

// Create singleton instance
const websocketManager = new WebSocketManager();

export default websocketManager; 