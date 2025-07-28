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
    Card,
    CardBody,
    CardHeader,
    Collapsible,
    createToaster,
    Code,
    Separator,
} from '@chakra-ui/react';
import { LuChevronLeft, LuChevronDown, LuChevronRight } from 'react-icons/lu';
import { workflowService } from '../../services/api';
import { ExecutionLogDetail as ExecutionLogDetailType } from '../../types/executionLog';

interface ExecutionLogDetailProps {
    logId: number;
    onBack: () => void;
}

const toaster = createToaster({
    placement: 'top',
});

export const ExecutionLogDetail = ({ logId, onBack }: ExecutionLogDetailProps) => {
    const [log, setLog] = useState<ExecutionLogDetailType | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [expandedSections, setExpandedSections] = useState({
        payload: false,
        result: false,
        error: false,
    });

    useEffect(() => {
        const loadLogDetail = async () => {
            try {
                setLoading(true);
                setError(null);
                const logData = await workflowService.getExecutionLogDetail(logId);
                setLog(logData);
            } catch (err: any) {
                const errorMessage = err.response?.data?.detail || 'Failed to load execution log details';
                setError(errorMessage);
                toaster.create({
                    title: 'Error loading log details',
                    description: errorMessage,
                    type: 'error',
                    duration: 5000,
                });
            } finally {
                setLoading(false);
            }
        };

        loadLogDetail();
    }, [logId]);

    const toggleSection = (section: keyof typeof expandedSections) => {
        setExpandedSections(prev => ({
            ...prev,
            [section]: !prev[section],
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

    const formatJson = (obj: any) => {
        return JSON.stringify(obj, null, 2);
    };

    if (loading) {
        return (
            <Card>
                <CardBody>
                    <VStack py="8">
                        <Spinner size="lg" />
                        <Text color="gray.600">Loading execution details...</Text>
                    </VStack>
                </CardBody>
            </Card>
        );
    }

    if (error || !log) {
        return (
            <Card>
                <CardBody>
                    <Alert status="error">
                        <VStack align="start">
                            <Text>{error || 'Execution log not found'}</Text>
                            <Button variant="outline" onClick={onBack} size="sm">
                                Back to Logs
                            </Button>
                        </VStack>
                    </Alert>
                </CardBody>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <HStack justify="space-between" align="center">
                    <HStack gap="3">
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={onBack}
                        >
                            <LuChevronLeft />
                            Back to Logs
                        </Button>
                        <Separator orientation="vertical" height="6" />
                        <VStack align="start" gap="1">
                            <Heading size="lg">Execution #{log.id}</Heading>
                            <HStack gap="3">
                                <Badge
                                    colorPalette={getStatusColor(log.status)}
                                    variant="subtle"
                                    textTransform="capitalize"
                                >
                                    {log.status}
                                </Badge>
                                <Text fontSize="sm" color="gray.600">
                                    Duration: {formatDuration(log.started_at, log.completed_at)}
                                </Text>
                            </HStack>
                        </VStack>
                    </HStack>
                </HStack>
            </CardHeader>

            <CardBody>
                <VStack gap="6" align="stretch">
                    {/* Execution Timeline */}
                    <Box>
                        <Heading size="md" mb="3">Execution Timeline</Heading>
                        <VStack align="start" gap="2">
                            <HStack gap="3">
                                <Text fontSize="sm" fontWeight="medium" color="gray.700">
                                    Started:
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                    {formatTimestamp(log.started_at)}
                                </Text>
                            </HStack>
                            {log.completed_at && (
                                <HStack gap="3">
                                    <Text fontSize="sm" fontWeight="medium" color="gray.700">
                                        Completed:
                                    </Text>
                                    <Text fontSize="sm" color="gray.600">
                                        {formatTimestamp(log.completed_at)}
                                    </Text>
                                </HStack>
                            )}
                            <HStack gap="3">
                                <Text fontSize="sm" fontWeight="medium" color="gray.700">
                                    Total Duration:
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                    {formatDuration(log.started_at, log.completed_at)}
                                </Text>
                            </HStack>
                        </VStack>
                    </Box>

                    <Separator />

                    {/* Input Payload */}
                    <Box>
                        <Button
                            variant="ghost"
                            onClick={() => toggleSection('payload')}
                            size="sm"
                            mb="3"
                        >
                            {expandedSections.payload ? <LuChevronDown /> : <LuChevronRight />}
                            <Heading size="md">Input Payload</Heading>
                        </Button>

                        <Collapsible.Root open={expandedSections.payload}>
                            <Collapsible.Content>
                                <Box
                                    p="4"
                                    bg="gray.50"
                                    borderRadius="md"
                                    border="1px"
                                    borderColor="gray.200"
                                >
                                    <Code
                                        display="block"
                                        whiteSpace="pre-wrap"
                                        fontSize="sm"
                                        bg="transparent"
                                        p="0"
                                    >
                                        {formatJson(log.payload)}
                                    </Code>
                                </Box>
                            </Collapsible.Content>
                        </Collapsible.Root>
                    </Box>

                    {/* Execution Result */}
                    {log.result && (
                        <>
                            <Separator />
                            <Box>
                                <Button
                                    variant="ghost"
                                    onClick={() => toggleSection('result')}
                                    size="sm"
                                    mb="3"
                                >
                                    {expandedSections.result ? <LuChevronDown /> : <LuChevronRight />}
                                    <Heading size="md">Execution Result</Heading>
                                </Button>

                                <Collapsible.Root open={expandedSections.result}>
                                    <Collapsible.Content>
                                        <Box
                                            p="4"
                                            bg="green.50"
                                            borderRadius="md"
                                            border="1px"
                                            borderColor="green.200"
                                        >
                                            <Code
                                                display="block"
                                                whiteSpace="pre-wrap"
                                                fontSize="sm"
                                                bg="transparent"
                                                p="0"
                                            >
                                                {formatJson(log.result)}
                                            </Code>
                                        </Box>
                                    </Collapsible.Content>
                                </Collapsible.Root>
                            </Box>
                        </>
                    )}

                    {/* Error Details */}
                    {log.error_message && (
                        <>
                            <Separator />
                            <Box>
                                <Button
                                    variant="ghost"
                                    onClick={() => toggleSection('error')}
                                    size="sm"
                                    mb="3"
                                >
                                    {expandedSections.error ? <LuChevronDown /> : <LuChevronRight />}
                                    <Heading size="md" color="red.600">Error Details</Heading>
                                </Button>

                                <Collapsible.Root open={expandedSections.error}>
                                    <Collapsible.Content>
                                        <Box
                                            p="4"
                                            bg="red.50"
                                            borderRadius="md"
                                            border="1px"
                                            borderColor="red.200"
                                        >
                                            <Text
                                                fontSize="sm"
                                                color="red.800"
                                                whiteSpace="pre-wrap"
                                                fontFamily="mono"
                                            >
                                                {log.error_message}
                                            </Text>
                                        </Box>
                                    </Collapsible.Content>
                                </Collapsible.Root>
                            </Box>
                        </>
                    )}
                </VStack>
            </CardBody>
        </Card>
    );
};