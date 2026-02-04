import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const AdminService = {
    // Users
    getUsers: async () => {
        const response = await api.get('/users');
        return response.data;
    },

    // Families
    getFamilies: async () => {
        const response = await api.get('/shop/families');
        return response.data;
    },

    // Approve Family (Mock function for now)
    approveFamily: async (familyId: number) => {
        // In real app: await api.post(`/admin/families/${familyId}/approve`);
        console.log(`Approving family ${familyId}`);
        return true;
    },

    // Products
    getProducts: async () => {
        // Assuming endpoint exists or we filter by family client-side for now if not
        try {
            const response = await api.get('/shop/products'); // Requires backend endpoint implementation or route
            return response.data;
        } catch (error) {
            console.error("Failed to fetch products", error);
            return [];
        }
    },

    // Orders
    createOrder: async (orderData: any) => {
        const response = await api.post('/orders', orderData);
        return response.data;
    },

    // Product Management
    deleteProduct: async (id: number) => {
        const response = await api.delete(`/shop/products/${id}`);
        return response.data;
    },

    updateProduct: async (id: number, data: any) => {
        const response = await api.put(`/shop/products/${id}`, data);
        return response.data;
    },

    // Auth & Registration
    registerUser: async (userData: any) => {
        const response = await api.post('/users/register', userData);
        return response.data;
    },

    createFamily: async (familyData: any) => {
        const response = await api.post('/shop/families', familyData);
        return response.data;
    },

    // Ads
    getFeaturedAds: async () => {
        const response = await api.get('/shop/ads');
        return response.data;
    },

    // Auth
    login: async (credentials: any) => {
        const response = await api.post('/users/login', credentials);
        return response.data;
    }
};

export default api;
