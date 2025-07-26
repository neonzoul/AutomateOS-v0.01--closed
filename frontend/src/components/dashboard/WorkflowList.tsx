import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Heading,
    Text,
    Stack,
    Button,
    HStack,
    VStack,
    Spinner,
    Center,
    createToaster,
} from '@chakra-ui/react';
import {
    DialogActionTrigger,
    DialogBody,
    DialogCloseTrigger,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTitle,
} from '@chakra-ui/react';
import { workflowService } from '../../services/api';
import { WorkflowCard } from './WorkflowCard';

const toaster = createToaster({
    placement: 'top',
});

interface Workflow {
    id: number;
    name: string;
    description?: string;
    webhook_url: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export const WorkflowList = () => {
    const [workflows, setWorkflows] = useState<Workflow[]>([]);
    const [loading, setLoading] = useState(true);
    const [deleteWorkflowId, setDeleteWorkflowId] = useState<number | null>(null);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const navigate = useNavigate();

    const fetchWorkflows = async () => {
        try {
            setLoading(true);
            const data = await workflowService.getWorkflows();
            setWorkflows(data);
        } catch (error) {
            toaster.create({
                title: 'Error fetching workflows',
                description: 'Failed to load your workflows. Please try again.',
                type: 'error',
                duration: 5000,
            });
        } finally {
            setLoading(false);
        }
    };

    // Removed unused createWorkflow function

    const handleDeleteWorkflow = async () => {
        if (!deleteWorkflowId) return;

        try {
            await workflowService.deleteWorkflow(deleteWorkflowId);
            setWorkflows(workflows.filter(w => w.id !== deleteWorkflowId));
            toaster.create({
                title: 'Workflow deleted',
                description: 'The workflow has been successfully deleted.',
                type: 'success',
                duration: 3000,
            });
        } catch (error) {
            toaster.create({
                title: 'Error deleting workflow',
                description: 'Failed to delete the workflow. Please try again.',
                type: 'error',
                duration: 5000,
            });
        } finally {
            setDeleteWorkflowId(null);
            setIsDeleteDialogOpen(false);
        }
    };

    const confirmDeleteWorkflow = (workflowId: number) => {
        setDeleteWorkflowId(workflowId);
        setIsDeleteDialogOpen(true);
    };

    const handleCreateWorkflow = () => {
        navigate('/workflows/new');
    };

    useEffect(() => {
        fetchWorkflows();
    }, []);

    if (loading) {
        return (
            <Center py={8}>
                <VStack gap="4">
                    <Spinner size="lg" color="blue.500" />
                    <Text color="gray.600">Loading workflows...</Text>
                </VStack>
            </Center>
        );
    }

    if (workflows.length === 0) {
        return (
            <Box textAlign="center" py={8}>
                <Heading size="md" color="gray.600" mb={4}>
                    No workflows yet
                </Heading>
                <Text color="gray.500" mb={6}>
                    Create your first workflow to get started with automation.
                </Text>
                <Button colorPalette="blue" size="lg" onClick={handleCreateWorkflow}>
                    Create Your First Workflow
                </Button>
            </Box>
        );
    }

    return (
        <Box>
            <HStack justify="space-between" mb={6}>
                <Heading size="lg">Your Workflows</Heading>
                <Button colorPalette="blue" onClick={handleCreateWorkflow}>
                    Create New Workflow
                </Button>
            </HStack>

            <Stack gap="4">
                {workflows.map((workflow) => (
                    <WorkflowCard
                        key={workflow.id}
                        workflow={workflow}
                        onDelete={confirmDeleteWorkflow}
                    />
                ))}
            </Stack>

            {/* Delete Confirmation Dialog */}
            <DialogRoot open={isDeleteDialogOpen} onOpenChange={(e) => setIsDeleteDialogOpen(e.open)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Delete Workflow</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        Are you sure you want to delete this workflow? This action cannot be undone.
                    </DialogBody>
                    <DialogFooter>
                        <DialogActionTrigger asChild>
                            <Button variant="outline">Cancel</Button>
                        </DialogActionTrigger>
                        <Button colorPalette="red" onClick={handleDeleteWorkflow}>
                            Delete
                        </Button>
                    </DialogFooter>
                    <DialogCloseTrigger />
                </DialogContent>
            </DialogRoot>
        </Box>
    );
};