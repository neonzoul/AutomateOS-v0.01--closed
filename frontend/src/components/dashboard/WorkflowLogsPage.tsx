import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Box,
    VStack,
    HStack,
    Text,
    Button,
    Spinner,
    Alert,
    createToaster,
} from '@chakra-ui/react';
import { LuChevronLeft } from 'react-icons/lu';
import { Layout } from '../common/Layout';
import { ExecutionLogs } from './ExecutionLogs';
import { workflowService } from '../../services/api';

interface Workflow {
    id: number;
    name: string;
    description?: string;
    is_active: boolean;
}

const toaster = createToaster({
    placement: 'top',
});

export const WorkflowLogsPage = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [workflow, setWorkflow] = useState<Workflow | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadWorkflow = async () => {
            if (!id) {
                setError('Workflow ID is required');
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError(null);
                const workflowData = await workflowService.getWorkflow(parseInt(id));
                setWorkflow(workflowData);
            } catch (err: any) {
                const errorMessage = err.response?.data?.detail || 'Failed to load workflow';
                setError(errorMessage);
                toaster.create({
                    title: 'Error loading workflow',
                    description: errorMessage,
                    type: 'error',
                    duration: 5000,
                });
            } finally {
                setLoading(false);
            }
        };

        loadWorkflow();
    }, [id]);

    if (loading) {
        return (
            <Layout>
                <VStack py="8">
                    <Spinner size="lg" />
                    <Text color="gray.600">Loading workflow...</Text>
                </VStack>
            </Layout>
        );
    }

    if (error || !workflow) {
        return (
            <Layout>
                <VStack py="8" gap="4">
                    <Alert status="error">
                        <Text>{error || 'Workflow not found'}</Text>
                    </Alert>
                    <Button variant="outline" onClick={() => navigate('/')}>
                        Back to Dashboard
                    </Button>
                </VStack>
            </Layout>
        );
    }

    return (
        <Layout>
            <VStack align="stretch" gap={6} maxWidth="1200px" mx="auto" p={4}>
                {/* Header */}
                <HStack justify="space-between" align="center">
                    <HStack gap="3">
                        <Button
                            variant="ghost"
                            onClick={() => navigate('/')}
                        >
                            <LuChevronLeft />
                            Back to Dashboard
                        </Button>
                        <VStack align="start" gap="1">
                            <Text fontSize="2xl" fontWeight="bold">
                                Execution Logs
                            </Text>
                            <Text color="gray.600" fontSize="sm">
                                {workflow.name}
                            </Text>
                        </VStack>
                    </HStack>

                    <HStack gap="2">
                        <Button
                            variant="outline"
                            colorPalette="blue"
                            onClick={() => navigate(`/workflows/${workflow.id}/edit`)}
                        >
                            Edit Workflow
                        </Button>
                    </HStack>
                </HStack>

                {/* Execution Logs */}
                <ExecutionLogs
                    workflowId={workflow.id}
                    workflowName={workflow.name}
                />
            </VStack>
        </Layout>
    );
};