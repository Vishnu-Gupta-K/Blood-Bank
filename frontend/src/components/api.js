// API utility functions for the Blood Bank application

// Base URL for API requests
const API_BASE_URL = 'http://localhost:8000';

// Helper function for making API requests
async function apiRequest(endpoint, method = 'GET', data = null, token = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers = {
        'Content-Type': 'application/json',
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options = {
        method,
        headers,
        credentials: 'include',
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        
        // Handle non-JSON responses (like PDF)
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/pdf')) {
            return response.blob();
        }
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Something went wrong');
        }
        
        return result;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// Authentication functions
async function login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const url = `${API_BASE_URL}/token`;
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }
        
        // Store the token in localStorage
        localStorage.setItem('token', data.access_token);
        
        return data;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

async function register(username, email, password) {
    return apiRequest('/users/', 'POST', { username, email, password });
}

async function getCurrentUser() {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    return apiRequest('/users/me/', 'GET', null, token);
}

// Donor functions
async function createDonorProfile(donorData) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    return apiRequest('/donors/', 'POST', donorData, token);
}

async function getDonorProfile() {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    return apiRequest('/donors/me/', 'GET', null, token);
}

async function updateDonorProfile(donorData) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    return apiRequest('/donors/me/', 'PUT', donorData, token);
}

// Receiver functions
async function searchDonors(searchParams) {
    const queryParams = new URLSearchParams();
    
    if (searchParams.blood_group) {
        queryParams.append('blood_group', searchParams.blood_group);
    }
    if (searchParams.state) {
        queryParams.append('state', searchParams.state);
    }
    if (searchParams.district) {
        queryParams.append('district', searchParams.district);
    }
    if (searchParams.village) {
        queryParams.append('village', searchParams.village);
    }
    if (searchParams.is_available !== undefined) {
        queryParams.append('is_available', searchParams.is_available);
    }
    
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    return apiRequest(`/donors/search/?${queryParams}`, 'GET', null, token);
}

async function createReceiverRequest(requestData) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    return apiRequest('/receiver-requests/', 'POST', requestData, token);
}

async function getReceiverRequests() {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    return apiRequest('/receiver-requests/', 'GET', null, token);
}

// PDF Export function
async function exportDonorsToPDF(donorIds, title = 'Donor List', includeContactInfo = true) {
    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    const data = {
        donor_ids: donorIds,
        title,
        include_contact_info: includeContactInfo
    };
    
    const pdfBlob = await apiRequest('/export/donors-pdf/', 'POST', data, token);
    
    // Create a download link for the PDF
    const url = window.URL.createObjectURL(pdfBlob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `${title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
}

// Export all functions
export {
    login,
    register,
    getCurrentUser,
    createDonorProfile,
    getDonorProfile,
    updateDonorProfile,
    searchDonors,
    createReceiverRequest,
    getReceiverRequests,
    exportDonorsToPDF
};