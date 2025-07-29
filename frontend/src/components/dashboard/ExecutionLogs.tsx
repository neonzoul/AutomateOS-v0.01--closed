import { useState, useEffect } from 'react';
import {
    Box,
    Heading,
    VStack,
    HStack,
    Text,
    Badge,
    Button,
    Spinner,
    Alert,
    createToaster,
    Card,
    CardBody,
    CardHeader,
    NativeSelectRoot,
    NativeSelectField,
} from '@chakra-ui/react';
import { workflowService } from '../../services/api';
import { ExecutionLogSummary, ExecutionLogFilters } from '../../types/executionLog';
import { ExecutionLogDetail } from './ExecutionLogDetail';

interface ExecutionLogsProps {
    workflowId: number;
    workflowName: string;
}

const toaster = createToaster({
    placement: 'top',
});

export const ExecutionLogs = ({ workflowId, workflowName }: ExecutionLogsProps) => {
    const [logs, setLogs] = useState<ExecutionLogSummary[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedLogId, setSelectedLogId] = useState<number | null>(null);
    const [filters, setFilters] = useState<ExecutionLogFilters>({
        limit: 20,
        offset: 0,
    });
    const [totalCount, setTotalCount] = useState(0);
    const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

    // Load execution logs
    const loadLogs = async (showLoading = true) => {
        try {
            if (showLoading) setLoading(true);
            setError(null);

            const [logsData, countData] = await Promise.all([
                workflowService.getWorkflowLogs(workflowId, filters),
                workflowService.getWorkflowLogsCount(workflowId, filters.status),
            ]);

            setLogs(logsData);
            setTotalCount(countData.count);
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || 'Failed to load execution logs';
            setError(errorMessage);
            toaster.create({
                title: 'Error loading logs',
                description: errorMessage,
                type: 'error',
                duration: 5000,
            });
        } finally {
            if (showLoading) setLoading(false);
        }
    };

    // Initial load and setup polling
    useEffect(() => {
        loadLogs();

        // Set up polling for real-time updates
        const interval = setInterval(() => {
            loadLogs(false); // Don't show loading spinner for polling updates
        }, 5000); // Poll every 5 seconds

        setPollingInterval(interval);

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [workflowId, filters]);

    // Clean up polling on unmount
    useEffect(() => {
        return () => {
            if (pollingInterval) clearInterval(pollingInterval);
        };
    }, [pollingInterval]);

    const handleStatusFilterChange = (status: string) => {
        setFilters(prev => ({
            ...prev,
            status: status === 'all' ? undefined : status as 'success' | 'failed' | 'running',
            offset: 0, // Reset pagination when filtering
        }));
    };

    const handleLoadMore = () => {
        setFilters(prev => ({
            ...prev,
            offset: (prev.offset || 0) + (prev.limit || 20),
        }));
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'success':
                return 'green';
            case 'failed':
                return 'red';
            case 'running':
                return 'blue';
            default:
                return 'gray';
        }
    };

    const formatDuration = (startedAt: string, completedAt?: string) => {
        const start = new Date(startedAt);
        const end = completedAt ? new Date(completedAt) : new Date();
        const duration = end.getTime() - start.getTime();

        if (duration < 1000) return `${duration}ms`;
        if (duration < 60000) return `${Math.round(duration / 1000)}s`;
        return `${Math.round(duration / 60000)}m`;
    };

    const formatTimestamp = (timestamp: string) => {
        return new Date(timestamp).toLocaleString();
    };

    if (selectedLogId) {
        return (
            <ExecutionLogDetail
                logId={selectedLogId}
                onBack={() => setSelectedLogId(null)}
            />
        );
    }

    return (
        <Card>
            <CardHeader>
                <HStack justify="space-between" align="center">
                    <VStack align="start" gap="1">
                        <Heading size="lg">Execution Logs</Heading>
                        <Text color="gray.600" fontSize="sm">
                            {workflowName} • {totalCount} total executions
                        </Text>
                    </VStack>

                    <HStack gap="3">
                        <Text fontSize="sm" color="gray.600">Filter by status:</Text>
                        <NativeSelectRoot size="sm" width="120px">
                            <NativeSelectField
                                value={filters.status || 'all'}
                                onChange={(e) => handleStatusFilterChange(e.target.value)}
                            >
                                <option value="all">All</option>
                                <option value="success">Success</option>
                                <option value="failed">Failed</option>
                                <option value="running">Running</option>
                            </NativeSelectField>
                        </NativeSelectRoot>
                    </HStack>
                </HStack>
            </CardHeader>

            <CardBody>
                {loading && logs.length === 0 ? (
                    <VStack py="8">
                        <Spinner size="lg" />
                        <Text color="gray.600">Loading execution logs...</Text>
                    </VStack>
                ) : error ? (
                    <Alert status="error">
                        <Text>{error}</Text>
                    </Alert>
                ) : logs.length === 0 ? (
                    <VStack py="12" gap="4">
                        <Text fontSize="lg" color="gray.600">
                            No executions found
                        </Text>
                        <Text color="gray.500" textAlign="center">
                            This workflow hasn't been executed yet.
                            {!filters.status && (
                                <> Try triggering it using the webhook URL.</>
                            )}
                        </Text>
                    </VStack>
                ) : (
                    <VStack gap="3" align="stretch">
                        {logs.map((log) => (
                            <Box
                                key={log.id}
                                p="4"
                                border="1px"
                                borderColor="gray.200"
                                borderRadius="md"
                                bg="white"
                                _hover={{ bg: 'gray.50', cursor: 'pointer' }}
                                onClick={() => setSelectedLogId(log.id)}
                                transition="background-color 0.2s"
                            >
                                <HStack justify="space-between" align="start">
                                    <VStack align="start" gap="2" flex="1">
                                        <HStack gap="3">
                                            <Badge
                                                colorPalette={getStatusColor(log.status)}
                                                variant="subtle"
                                                textTransform="capitalize"
                                            >
                                                {log.status}
                                            </Badge>
                                            <Text fontSize="sm" color="gray.600">
                                                Execution #{log.id}
                                            </Text>
                                            <Text fontSize="sm" color="gray.500">
                                                Duration: {formatDuration(log.started_at, log.completed_at)}
                                            </Text>
                                        </HStack>

                                        <Text fontSize="sm" color="gray.700">
                                            Started: {formatTimestamp(log.started_at)}
                                            {log.completed_at && (
                                                <> • Completed: {formatTimestamp(log.completed_at)}</>
                                            )}
                                        </Text>

                                        {log.error_message && (
                                            <Text fontSize="sm" color="red.600" noOfLines={2}>
                                                Error: {log.error_message}
                                            </Text>
                                        )}
                                    </VStack>

                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        colorPalette="blue"
                                    >
                                        View Details
                                    </Button>
                                </HStack>
                            </Box>
                        ))}

                        {logs.length < totalCount && (
                            <Button
                                variant="outline"
                                onClick={handleLoadMore}
                                loading={loading}
                                alignSelf="center"
                                mt="4"
                            >
                                Load More ({totalCount - logs.length} remaining)
                            </Button>
                        )}
                    </VStack>
                )}
            </CardBody>
        </Card>
    );
};