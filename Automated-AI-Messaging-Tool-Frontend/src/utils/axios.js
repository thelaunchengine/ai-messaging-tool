const axios = require('axios');

// Use Python backend URL from environment variables
const pythonBackendUrl = process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL || 'http://localhost:8001';
const axiosServices = axios.create({ baseURL: pythonBackendUrl });

module.exports = axiosServices;
