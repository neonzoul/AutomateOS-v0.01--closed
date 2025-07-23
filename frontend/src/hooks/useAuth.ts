import { useAuth as useAuthContext } from '../contexts/AuthContext';

// Re-export the useAuth hook for consistency
export const useAuth = useAuthContext;

// Additional authentication-related hooks can be added here
export const useIsAuthenticated = () => {
    const { token } = useAuthContext();
    return !!token;
};

export const useAuthToken = () => {
    const { token } = useAuthContext();
    return token;
};