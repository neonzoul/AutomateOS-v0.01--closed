import { useState, useEffect } from 'react';
import {
    Box,
    Heading,
    Text,
    Button,
    ButtonGroup,
    HStack,
    VStack,
    Badge,
    useToast,
    Spinner,
} from '@chakra-ui/react';
import { workflowService } from '../../services/api';

interface Workflow {
    id: number;
    name: string;
    description?: string;
    webhook_url: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

interface WorkflowCardProps {
    workflow: Workflow;
    onEdit: (workflow: Workflow) => void;
    onDelete: (workflowId: number) => void;
}

export const WorkflowCard = ({ workflow, onEdit, onDelete }: WorkflowCardProps) => {
    const [copying, setCopying] = useState(false);
    const [formattedDates, setFormattedDates] = useState({ created: '', updated: '' });
    const toast = useToast();

    // Format dates when workflow changes
    useEffect(() => {
        setFormattedDates({
            created: new Date(workflow.created_at).toLocaleDateString(),
            updated: new Date(workflow.updated_at).toLocaleDateString()
        });

        // Verify workflow exists in the backend
        const verifyWorkflow = async () => {
            try {
                await workflowService.getWorkflow(workflow.id);
            } catch (error) {
                console.error('Error verifying workflow:', error);
            }
        };

        verifyWorkflow();
    }, [workflow]);

    const copyWebhookUrl = async () => {
        try {
            setCopying(true);
            const fullUrl = `${window.location.origin}${workflow.webhook_url}`;
            await navigator.clipboard.writeText(fullUrl);
            toast({
                title: 'Webhook URL copied',
                description: 'The webhook URL has been copied to your clipboard.',
                status: 'success',
                duration: 2000,
                isClosable: true,
            });
        } catch (error) {
            toast({
                title: 'Copy failed',
                description: 'Failed to copy the webhook URL to clipboard.',
                status: 'error',
                duration: 2000,
                isClosable: true,
            });
        } finally {
            setCopying(false);
        }
    };

    return (
        <Box
            p={5}
            shadow="md"
            borderWidth="1px"
            borderRadius="md"
            bg="white"
            _hover={{ shadow: "lg" }}
            transition="shadow 0.2s"
        >
            <HStack justifyContent="space-between" align="start">
                <VStack align="start" gap="2" flex={1}>
                    <HStack>
                        <Heading fontSize="xl" color="gray.800">
                            {workflow.name}
                        </Heading>
                        <Badge
                            colorScheme={workflow.is_active ? "green" : "gray"}
                            variant="subtle"
                        >
                            {workflow.is_active ? "Active" : "Inactive"}
                        </Badge>
                    </HStack>

                    <Text color="gray.600" fontSize="sm">
                        {workflow.description || 'No description provided.'}
                    </Text>

                    <HStack gap="2">
                        <Text color="gray.500" fontSize="xs">
                            Webhook: {workflow.webhook_url}
                        </Text>
                        <Button
                            size="xs"
                            variant="ghost"
                            colorScheme="blue"
                            onClick={copyWebhookUrl}
                            isLoading={copying}
                            loadingText="Copying..."
                        >
                            Copy
                        </Button>
                    </HStack>

                    <Text color="gray.400" fontSize="xs">
                        Created: {formattedDates.created}
                        {workflow.updated_at !== workflow.created_at && (
                            <> • Updated: {formattedDates.updated}</>
                        )}
                    </Text>
                </VStack>

                <ButtonGroup size="sm" gap="2">
                    <Button
                        variant="outline"
                        colorScheme="blue"
                        onClick={() => onEdit(workflow)}
                    >
                        View/Edit
                    </Button>
                    <Button
                        variant="outline"
                        colorScheme="red"
                        onClick={() => onDelete(workflow.id)}
                    >
                        Delete
                    </Button>
                </ButtonGroup>
            </HStack>
        </Box>
    );
};