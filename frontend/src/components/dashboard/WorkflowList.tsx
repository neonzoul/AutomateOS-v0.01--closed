import { useState, useEffect, useRef } from 'react';
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
    useDisclosure,
    AlertDialog,
    AlertDialogBody,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogContent,
    AlertDialogOverlay,
    useToast,
} from '@chakra-ui/react';
import { workflowService } from '../../services/api';
import { WorkflowCard } from './WorkflowCard';
import { CreateWorkflowModal } from './CreateWorkflowModal';

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
    const { open: isDeleteDialogOpen, onOpen: openDeleteDialog, onClose: closeDeleteDialog } = useDisclosure();
    const { open: isCreateModalOpen, onOpen: openCreateModal, onClose: closeCreateModal } = useDisclosure();
    const cancelRef = useRef<HTMLButtonElement>(null);
    const toast = useToast();

    const fetchWorkflows = async () => {
        try {
            setLoading(true);
            const data = await workflowService.getWorkflows();
            setWorkflows(data);
        } catch (error) {
            toast({
                title: 'Error fetching workflows',
                description: 'Failed to load your workflows. Please try again.',
                status: 'error',
                duration: 5000,
                isClosable: true,
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
            toast({
                title: 'Workflow deleted',
                description: 'The workflow has been successfully deleted.',
                status: 'success',
                duration: 3000,
                isClosable: true,
            });
        } catch (error) {
            toast({
                title: 'Error deleting workflow',
                description: 'Failed to delete the workflow. Please try again.',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setDeleteWorkflowId(null);
            closeDeleteDialog();
        }
    };

    const confirmDeleteWorkflow = (workflowId: number) => {
        setDeleteWorkflowId(workflowId);
        openDeleteDialog();
    };

    const handleEditWorkflow = (workflow: Workflow) => {
        // TODO: Navigate to workflow editor
        toast({
            title: 'Edit workflow',
            description: `Editing ${workflow.name} - Editor coming soon!`,
            status: 'info',
            duration: 3000,
            isClosable: true,
        });
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
                <Button colorScheme="blue" size="lg" onClick={openCreateModal}>
                    Create Your First Workflow
                </Button>

                <CreateWorkflowModal
                    isOpen={isCreateModalOpen}
                    onClose={closeCreateModal}
                    onWorkflowCreated={fetchWorkflows}
                />
            </Box>
        );
    }

    return (
        <Box>
            <HStack justify="space-between" mb={6}>
                <Heading size="lg">Your Workflows</Heading>
                <Button colorScheme="blue" onClick={openCreateModal}>
                    Create New Workflow
                </Button>
            </HStack>

            <Stack spacing="4">
                {workflows.map((workflow) => (
                    <WorkflowCard
                        key={workflow.id}
                        workflow={workflow}
                        onEdit={handleEditWorkflow}
                        onDelete={confirmDeleteWorkflow}
                    />
                ))}
            </Stack>

            {/* Delete Confirmation Dialog */}
            <AlertDialog
                isOpen={isDeleteDialogOpen}
                leastDestructiveRef={cancelRef}
                onClose={closeDeleteDialog}
            >
                <AlertDialogOverlay>
                    <AlertDialogContent>
                        <AlertDialogHeader fontSize="lg" fontWeight="bold">
                            Delete Workflow
                        </AlertDialogHeader>

                        <AlertDialogBody>
                            Are you sure you want to delete this workflow? This action cannot be undone.
                        </AlertDialogBody>

                        <AlertDialogFooter>
                            <Button ref={cancelRef} onClick={closeDeleteDialog}>
                                Cancel
                            </Button>
                            <Button colorScheme="red" onClick={handleDeleteWorkflow} ml={3}>
                                Delete
                            </Button>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialogOverlay>
            </AlertDialog>

            {/* Create Workflow Modal */}
            <CreateWorkflowModal
                isOpen={isCreateModalOpen}
                onClose={closeCreateModal}
                onWorkflowCreated={fetchWorkflows}
            />
        </Box>
    );
};