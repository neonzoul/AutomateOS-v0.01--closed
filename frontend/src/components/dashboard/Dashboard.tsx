import { useState, useEffect } from 'react';
import { Box, Button, Heading, HStack, Container, useToast } from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';
import { WorkflowList } from './WorkflowList';
import { workflowService } from '../../services/api';

export const Dashboard = () => {
    const { logout } = useAuth();
    const [loading, setLoading] = useState(false);
    const toast = useToast();

    // Check API connection on mount
    useEffect(() => {
        const checkApiConnection = async () => {
            try {
                setLoading(true);
                await workflowService.getWorkflows();
                // Connection successful, no need to show a message
            } catch (error) {
                toast({
                    title: 'API Connection Error',
                    description: 'Could not connect to the backend API. Please ensure the server is running.',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
            } finally {
                setLoading(false);
            }
        };

        checkApiConnection();
    }, [toast]);

    return (
        <Box minHeight="100vh" bg="gray.50">
            {/* Header */}
            <Box bg="white" shadow="sm" borderBottom="1px" borderColor="gray.200">
                <Container maxW="7xl" py={4}>
                    <HStack justify="space-between">
                        <Heading size="lg" color="blue.600">
                            AutomateOS
                        </Heading>
                        <Button variant="ghost" colorScheme="red" onClick={logout}>
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