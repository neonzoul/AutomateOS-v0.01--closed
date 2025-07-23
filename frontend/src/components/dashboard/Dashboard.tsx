import { Box, Button, Heading, Text } from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';

export const Dashboard = () => {
    const { logout } = useAuth();

    return (
        <Box p={8}>
            <Heading>Welcome to Your Dashboard</Heading>
            <Text mt={4}>You are successfully logged in.</Text>
            <Button mt={6} colorScheme="red" onClick={logout}>
                Log Out
            </Button>
        </Box>
    );
};