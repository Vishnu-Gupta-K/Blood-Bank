// config.js
// This file manages the API Base URL for different environments (local vs. production).

const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : 'https://blood-bank-backend-YOUR_RENDER_ID.onrender.com'; // Replace with your actual Render backend URL

// Make it available globally
window.API_BASE_URL = API_BASE_URL;
