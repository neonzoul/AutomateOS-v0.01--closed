import { useEffect } from 'react';
import { Box, Button, Heading, HStack, Container, createToaster } from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';
import { WorkflowList } from './WorkflowList';
import { workflowService } from '../../services/api';

const toaster = createToaster({
    placement: 'top',
});

export const Dashboard = () => {
    const { logout } = useAuth();

    // Check API connection on mount
    useEffect(() => {
        const checkApiConnection = async () => {
            try {
                await workflowService.getWorkflows();
                // Connection successful, no need to show a message
            } catch (error) {
                toaster.create({
                    title: 'API Connection Error',
                    description: 'Could not connect to the backend API. Please ensure the server is running.',
                    type: 'error',
                    duration: 5000,
                });
            }
        };

        checkApiConnection();
    }, []);

    return (
        <Box minHeight="100vh" bg="gray.50">
            {/* Header */}
            <Box bg="white" shadow="sm" borderBottom="1px" borderColor="gray.200">
                <Container maxW="7xl" py={4}>
                    <HStack justify="space-between">
                        <Heading size="lg" color="blue.600">
                            AutomateOS
                        </Heading>
                        <Button variant="ghost" colorPalette="red" onClick={logout}>
                            Log Out
                        </Button>
                    </HStack>
                </Container>
            </Box>

            {/* Main Content */}
            <Container maxW="7xl" py={8}>
                <WorkflowList />
            </Container>
        </Box>
    );
};