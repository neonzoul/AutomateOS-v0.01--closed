import { useState, useEffect } from 'react';
import {
    Button,
    Input,
    Textarea,
    VStack,
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
    FormControl,
    FormLabel,
    Switch,
    useToast,
} from '@chakra-ui/react';
import { workflowService } from '../../services/api';

interface CreateWorkflowModalProps {
    open: boolean;
    onClose: () => void;
    onWorkflowCreated: () => void;
}

export const CreateWorkflowModal = ({ open, onClose, onWorkflowCreated }: CreateWorkflowModalProps) => {
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        is_active: true,
    });
    const [loading, setLoading] = useState(false);
    const toast = useToast();

    // Reset form when modal opens/closes
    useEffect(() => {
        if (open) {
            setFormData({
                name: '',
                description: '',
                is_active: true,
            });
        }
    }, [open]);

    const handleSubmit = async () => {
        if (!formData.name.trim()) {
            toast({
                title: 'Validation Error',
                description: 'Workflow name is required.',
                status: 'error',
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        try {
            setLoading(true);
            // Create the workflow using createWorkflow API
            await workflowService.createWorkflow({
                name: formData.name.trim(),
                description: formData.description.trim() || undefined,
                definition: {
                    nodes: [],
                    connections: []
                },
                is_active: formData.is_active,
            });

            toast({
                title: 'Workflow created',
                description: 'Your new workflow has been created successfully.',
                status: 'success',
                duration: 3000,
                isClosable: true,
            });

            // Reset form
            setFormData({
                name: '',
                description: '',
                is_active: true,
            });

            onWorkflowCreated();
            onClose();
        } catch (error) {
            toast({
                title: 'Error creating workflow',
                description: 'Failed to create the workflow. Please try again.',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        if (!loading) {
            setFormData({
                name: '',
                description: '',
                is_active: true,
            });
            onClose();
        }
    };

    return (
        <Modal isOpen={open} onClose={handleClose} size="md">
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>Create New Workflow</ModalHeader>
                <ModalCloseButton />

                <ModalBody>
                    <VStack gap="4">
                        <FormControl isRequired>
                            <FormLabel>Workflow Name</FormLabel>
                            <Input
                                placeholder="Enter workflow name"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                disabled={loading}
                            />
                        </FormControl>

                        <FormControl>
                            <FormLabel>Description</FormLabel>
                            <Textarea
                                placeholder="Describe what this workflow does (optional)"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                disabled={loading}
                                rows={3}
                            />
                        </FormControl>

                        <FormControl display="flex" alignItems="center">
                            <FormLabel htmlFor="is-active" mb="0">
                                Active
                            </FormLabel>
                            <Switch
                                id="is-active"
                                isChecked={formData.is_active}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                                    setFormData({ ...formData, is_active: e.target.checked })
                                }
                                disabled={loading}
                            />
                        </FormControl>
                    </VStack>
                </ModalBody>

                <ModalFooter>
                    <Button variant="ghost" mr={3} onClick={handleClose} disabled={loading}>
                        Cancel
                    </Button>
                    <Button
                        colorScheme="blue"
                        onClick={handleSubmit}
                        isLoading={loading}
                    >
                        Create Workflow
                    </Button>
                </ModalFooter>
            </ModalContent>
        </Modal>
    );
};