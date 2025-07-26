import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Heading,
    Text,
    Button,
    HStack,
    VStack,
    Badge,
    createToaster,
} from '@chakra-ui/react';

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
    onDelete: (workflowId: number) => void;
}

const toaster = createToaster({
    placement: 'top',
});

export const WorkflowCard = ({ workflow, onDelete }: WorkflowCardProps) => {
    const [copying, setCopying] = useState(false);
    const [formattedDates, setFormattedDates] = useState({ created: '', updated: '' });
    const navigate = useNavigate();

    // Format dates when workflow changes
    useEffect(() => {
        setFormattedDates({
            created: new Date(workflow.created_at).toLocaleDateString(),
            updated: new Date(workflow.updated_at).toLocaleDateString()
        });
    }, [workflow]);

    const copyWebhookUrl = async () => {
        try {
            setCopying(true);
            const fullUrl = `${window.location.origin}${workflow.webhook_url}`;
            await navigator.clipboard.writeText(fullUrl);
            toaster.create({
                title: 'Webhook URL copied',
                description: 'The webhook URL has been copied to your clipboard.',
                type: 'success',
                duration: 2000,
            });
        } catch (error) {
            toaster.create({
                title: 'Copy failed',
                description: 'Failed to copy the webhook URL to clipboard.',
                type: 'error',
                duration: 2000,
            });
        } finally {
            setCopying(false);
        }
    };

    const handleEdit = () => {
        navigate(`/workflows/${workflow.id}/edit`);
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
                            colorPalette={workflow.is_active ? "green" : "gray"}
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
                            colorPalette="blue"
                            onClick={copyWebhookUrl}
                            loading={copying}
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

                <HStack gap="2">
                    <Button
                        variant="outline"
                        colorPalette="blue"
                        size="sm"
                        onClick={handleEdit}
                    >
                        Edit
                    </Button>
                    <Button
                        variant="outline"
                        colorPalette="red"
                        size="sm"
                        onClick={() => onDelete(workflow.id)}
                    >
                        Delete
                    </Button>
                </HStack>
            </HStack>
        </Box>
    );
};