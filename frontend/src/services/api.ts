import axios from 'axios';
import { TeamRequest } from '@/types/api';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

export const recommendTeams = async (request: TeamRequest) => {
    const { data } = await api.post('/api/recommend', request);
    return data.dossiers;
};

export const getLinchpins = async () => {
    const { data } = await api.get('/api/linchpins');
    return data.linchpins;
};

export const getMissionProfiles = async () => {
    const { data } = await api.get('/api/mission-profiles');
    return data.profiles;
};

export const getEmployees = async () => {
    const { data } = await api.get('/employees');
    return data.employees;
};

export default api;
