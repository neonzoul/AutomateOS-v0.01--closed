import type { ReactNode } from 'react';
import { Box, Spinner, Text, VStack } from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
    children: ReactNode;
    fallback?: ReactNode;
}

export const ProtectedRoute = ({ children, fallback }: ProtectedRouteProps) => {
    const { token } = useAuth();

    if (!token) {
        return fallback || (
            <Box minHeight="100vh" bg="gray.50" display="flex" alignItems="center" justifyContent="center">
                <VStack gap={4}>
                    <Text fontSize="lg" color="gray.600">
                        Please log in to access this page
                    </Text>
                </VStack>
            </Box>
        );
    }

    return <>{children}</>;
};

// Loading component for when checking authentication status
export const AuthLoadingSpinner = () => (
    <Box minHeight="100vh" bg="gray.50" display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
            <Spinner size="xl" color="blue.500" />
            <Text fontSize="lg" color="gray.600">
                Loading...
            </Text>
        </VStack>
    </Box>
);