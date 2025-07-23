import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

export const ProtectedRoute = () => {
    const { token } = useAuth();

    if (!token) {
        // If no token, redirect to the login page
        return <Navigate to="/login" />;
    }

    // If token exists, render the child routes
    return <Outlet />;
};