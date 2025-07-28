import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add JWT token to requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle authentication errors
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response?.status === 401) {
            // Token is invalid or expired
            localStorage.removeItem('token');
            // Optionally redirect to login page or trigger logout
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// API service functions
export const authService = {
    login: async (email: string, password: string) => {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        const response = await axios.post('/auth/token', params, {
            baseURL: 'http://127.0.0.1:8000',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        return response.data;
    },

    register: async (email: string, password: string) => {
        const response = await axios.post('/register/', {
            email,
            password
        }, {
            baseURL: 'http://127.0.0.1:8000',
        });
        return response.data;
    },

    getCurrentUser: async () => {
        const response = await api.get('/users/me');
        return response.data;
    },
};

export const workflowService = {
    getWorkflows: async () => {
        const response = await api.get('/workflows/');
        return response.data;
    },

    createWorkflow: async (workflow: any) => {
        const response = await api.post('/workflows/', workflow);
        return response.data;
    },

    getWorkflow: async (id: number) => {
        const response = await api.get(`/workflows/${id}`);
        return response.data;
    },

    updateWorkflow: async (id: number, workflow: any) => {
        const response = await api.put(`/workflows/${id}`, workflow);
        return response.data;
    },

    deleteWorkflow: async (id: number) => {
        const response = await api.delete(`/workflows/${id}`);
        return response.data;
    },

    getWorkflowLogs: async (id: number, params?: {
        status?: string;
        limit?: number;
        offset?: number;
    }) => {
        const queryParams = new URLSearchParams();
        if (params?.status) queryParams.append('status', params.status);
        if (params?.limit) queryParams.append('limit', params.limit.toString());
        if (params?.offset) queryParams.append('offset', params.offset.toString());

        const url = `/workflows/${id}/logs${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
        const response = await api.get(url);
        return response.data;
    },

    getWorkflowLogsCount: async (id: number, status?: string) => {
        const queryParams = new URLSearchParams();
        if (status) queryParams.append('status', status);

        const url = `/workflows/${id}/logs/count${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
        const response = await api.get(url);
        return response.data;
    },

    getExecutionLogDetail: async (logId: number) => {
        const response = await api.get(`/logs/${logId}`);
        return response.data;
    },
};

export default api;