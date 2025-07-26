import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Box,
    VStack,
    HStack,
    Text,
    Button,
    Input,
    Textarea,
    NativeSelectRoot,
    NativeSelectField,


    createToaster,
    Spinner,
} from '@chakra-ui/react';
import { LuPlus, LuSave, LuPlay, LuArrowLeft, LuArrowUp, LuArrowDown } from 'react-icons/lu';
import { Layout } from '../common/Layout';
import { NodeBase } from './NodeBase';
import type { NodeConfig, NodeValidation } from './NodeBase';
import { WebhookTriggerNode } from './nodes/WebhookTriggerNode';
import { HTTPRequestNode } from './nodes/HTTPRequestNode';
import { FilterNode } from './nodes/FilterNode';
import { validateNode } from './nodeValidation';
import { workflowService } from '../../services/api';

interface WorkflowDefinition {
    nodes: NodeConfig[];
    connections: Array<{ from: string; to: string }>;
}

interface WorkflowData {
    id?: number;
    name: string;
    description: string;
    definition: WorkflowDefinition;
    is_active: boolean;
}

const NODE_TYPES = [
    { value: 'webhook', label: 'Webhook Trigger', description: 'Triggers workflow from external HTTP requests' },
    { value: 'http_request', label: 'HTTP Request', description: 'Make HTTP calls to external APIs' },
    { value: 'filter', label: 'Filter', description: 'Apply conditional logic to workflow execution' },
];

const toaster = createToaster({
    placement: 'top',
});

export const WorkflowEditor: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const isEditing = Boolean(id);

    const [workflow, setWorkflow] = useState<WorkflowData>({
        name: '',
        description: '',
        definition: { nodes: [], connections: [] },
        is_active: true,
    });

    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [testing, setTesting] = useState(false);
    const [validationResults, setValidationResults] = useState<Record<string, NodeValidation>>({});

    // Load workflow if editing
    useEffect(() => {
        if (isEditing && id) {
            loadWorkflow(parseInt(id));
        }
    }, [id, isEditing]);

    // Validate all nodes whenever workflow definition changes
    useEffect(() => {
        const results: Record<string, NodeValidation> = {};
        workflow.definition.nodes.forEach(node => {
            results[node.id] = validateNode(node);
        });
        setValidationResults(results);
    }, [workflow.definition.nodes]);

    const loadWorkflow = async (workflowId: number) => {
        try {
            setLoading(true);
            const data = await workflowService.getWorkflow(workflowId);
            setWorkflow(data);
        } catch (error) {
            console.error('Failed to load workflow:', error);
            toaster.create({
                title: 'Error',
                description: 'Failed to load workflow',
                type: 'error',
            });
        } finally {
            setLoading(false);
        }
    };

    const generateNodeId = (type: string): string => {
        const existingIds = workflow.definition.nodes
            .filter(node => node.type === type)
            .map(node => node.id);

        let counter = 1;
        let newId = `${type}_${counter}`;
        while (existingIds.includes(newId)) {
            counter++;
            newId = `${type}_${counter}`;
        }
        return newId;
    };

    const addNode = (type: NodeConfig['type']) => {
        const newNode: NodeConfig = {
            id: generateNodeId(type),
            type,
            config: {},
        };

        setWorkflow(prev => ({
            ...prev,
            definition: {
                ...prev.definition,
                nodes: [...prev.definition.nodes, newNode],
            },
        }));
    };

    const updateNode = (nodeId: string, config: Record<string, any>) => {
        setWorkflow(prev => ({
            ...prev,
            definition: {
                ...prev.definition,
                nodes: prev.definition.nodes.map(node =>
                    node.id === nodeId ? { ...node, config } : node
                ),
            },
        }));
    };

    const deleteNode = (nodeId: string) => {
        setWorkflow(prev => ({
            ...prev,
            definition: {
                ...prev.definition,
                nodes: prev.definition.nodes.filter(node => node.id !== nodeId),
                connections: prev.definition.connections.filter(
                    conn => conn.from !== nodeId && conn.to !== nodeId
                ),
            },
        }));
    };

    const moveNode = (nodeId: string, direction: 'up' | 'down') => {
        const nodes = [...workflow.definition.nodes];
        const currentIndex = nodes.findIndex(node => node.id === nodeId);

        if (currentIndex === -1) return;

        const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;

        if (newIndex < 0 || newIndex >= nodes.length) return;

        // Swap nodes
        [nodes[currentIndex], nodes[newIndex]] = [nodes[newIndex], nodes[currentIndex]];

        setWorkflow(prev => ({
            ...prev,
            definition: {
                ...prev.definition,
                nodes,
            },
        }));
    };

    const validateWorkflow = (): boolean => {
        const nodes = workflow.definition.nodes;

        if (nodes.length === 0) {
            toaster.create({
                title: 'Validation Error',
                description: 'Workflow must have at least one node',
                type: 'error',
            });
            return false;
        }

        // Check if first node is a webhook trigger
        if (nodes[0].type !== 'webhook') {
            toaster.create({
                title: 'Validation Error',
                description: 'First node must be a Webhook Trigger',
                type: 'error',
            });
            return false;
        }

        // Check all nodes are valid
        const invalidNodes = Object.entries(validationResults)
            .filter(([_, validation]) => !validation.isValid)
            .map(([nodeId]) => nodeId);

        if (invalidNodes.length > 0) {
            toaster.create({
                title: 'Validation Error',
                description: `Invalid configuration in nodes: ${invalidNodes.join(', ')}`,
                type: 'error',
            });
            return false;
        }

        if (!workflow.name.trim()) {
            toaster.create({
                title: 'Validation Error',
                description: 'Workflow name is required',
                type: 'error',
            });
            return false;
        }

        return true;
    };

    const saveWorkflow = async () => {
        if (!validateWorkflow()) return;

        try {
            setSaving(true);

            if (isEditing && workflow.id) {
                await workflowService.updateWorkflow(workflow.id, workflow);
                toaster.create({
                    title: 'Success',
                    description: 'Workflow updated successfully',
                    type: 'success',
                });
            } else {
                const newWorkflow = await workflowService.createWorkflow(workflow);
                setWorkflow(newWorkflow);
                toaster.create({
                    title: 'Success',
                    description: 'Workflow created successfully',
                    type: 'success',
                });
                // Navigate to edit mode with the new ID
                navigate(`/workflows/${newWorkflow.id}/edit`, { replace: true });
            }
        } catch (error) {
            console.error('Failed to save workflow:', error);
            toaster.create({
                title: 'Error',
                description: 'Failed to save workflow',
                type: 'error',
            });
        } finally {
            setSaving(false);
        }
    };

    const testWorkflow = async () => {
        if (!validateWorkflow()) return;

        try {
            setTesting(true);

            // For testing, we'll validate the workflow structure and show a preview
            const testResults = {
                isValid: true,
                nodeCount: workflow.definition.nodes.length,
                hasWebhookTrigger: workflow.definition.nodes[0]?.type === 'webhook',
                validNodes: Object.values(validationResults).filter(v => v.isValid).length,
                totalNodes: workflow.definition.nodes.length,
            };

            toaster.create({
                title: 'Test Results',
                description: `Workflow is valid with ${testResults.nodeCount} nodes. All nodes configured correctly.`,
                type: 'success',
            });
        } catch (error) {
            console.error('Failed to test workflow:', error);
            toaster.create({
                title: 'Test Error',
                description: 'Failed to test workflow',
                type: 'error',
            });
        } finally {
            setTesting(false);
        }
    };

    const renderNode = (node: NodeConfig) => {
        let NodeComponent;
        switch (node.type) {
            case 'webhook':
                NodeComponent = WebhookTriggerNode;
                break;
            case 'http_request':
                NodeComponent = HTTPRequestNode;
                break;
            case 'filter':
                NodeComponent = FilterNode;
                break;
            default:
                return null;
        }

        const nodeIndex = workflow.definition.nodes.findIndex(n => n.id === node.id);
        const canMoveUp = nodeIndex > 0;
        const canMoveDown = nodeIndex < workflow.definition.nodes.length - 1;

        return (
            <Box key={node.id} position="relative">
                {/* Node ordering controls */}
                <HStack position="absolute" top={2} right={2} zIndex={1}>
                    <Button
                        size="xs"
                        variant="ghost"
                        onClick={() => moveNode(node.id, 'up')}
                        disabled={!canMoveUp}
                    >
                        <LuArrowUp />
                    </Button>
                    <Button
                        size="xs"
                        variant="ghost"
                        onClick={() => moveNode(node.id, 'down')}
                        disabled={!canMoveDown}
                    >
                        <LuArrowDown />
                    </Button>
                </HStack>

                <NodeBase
                    node={node}
                    onUpdate={updateNode}
                    onDelete={deleteNode}
                    validation={validationResults[node.id]}
                >
                    <NodeComponent
                        config={node.config}
                        onConfigUpdate={(config: Record<string, any>) => updateNode(node.id, config)}
                    />
                </NodeBase>
            </Box>
        );
    };

    if (loading) {
        return (
            <Layout>
                <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                    <Spinner size="lg" />
                </Box>
            </Layout>
        );
    }

    return (
        <Layout>
            <VStack align="stretch" gap={6} maxWidth="800px" mx="auto" p={4}>
                {/* Header */}
                <HStack justifyContent="space-between" align="center">
                    <HStack>
                        <Button
                            variant="ghost"
                            onClick={() => navigate('/')}
                        >
                            <LuArrowLeft />
                            Back to Dashboard
                        </Button>
                        <Text fontSize="2xl" fontWeight="bold">
                            {isEditing ? 'Edit Workflow' : 'Create Workflow'}
                        </Text>
                    </HStack>

                    <HStack>
                        <Button
                            onClick={testWorkflow}
                            variant="outline"
                            colorPalette="blue"
                            disabled={testing || workflow.definition.nodes.length === 0}
                        >
                            <LuPlay />
                            {testing ? 'Testing...' : 'Test'}
                        </Button>
                        <Button
                            onClick={saveWorkflow}
                            colorPalette="green"
                            disabled={saving}
                        >
                            <LuSave />
                            {saving ? 'Saving...' : 'Save'}
                        </Button>
                    </HStack>
                </HStack>

                {/* Workflow Basic Info */}
                <Box borderWidth="1px" borderRadius="md" p={4} bg="gray.50">
                    <VStack align="stretch" gap={3}>
                        <Text fontSize="lg" fontWeight="medium">Workflow Information</Text>

                        <HStack>
                            <Box flex={2}>
                                <Text fontSize="sm" fontWeight="medium" mb={1}>Name</Text>
                                <Input
                                    placeholder="My Workflow"
                                    value={workflow.name}
                                    onChange={(e) => setWorkflow(prev => ({ ...prev, name: e.target.value }))}
                                    bg="white"
                                />
                            </Box>
                            <Box flex={1}>
                                <Text fontSize="sm" fontWeight="medium" mb={1}>Status</Text>
                                <NativeSelectRoot>
                                    <NativeSelectField
                                        value={workflow.is_active ? 'active' : 'inactive'}
                                        onChange={(e) => setWorkflow(prev => ({
                                            ...prev,
                                            is_active: e.target.value === 'active'
                                        }))}
                                        bg="white"
                                    >
                                        <option value="active">Active</option>
                                        <option value="inactive">Inactive</option>
                                    </NativeSelectField>
                                </NativeSelectRoot>
                            </Box>
                        </HStack>

                        <Box>
                            <Text fontSize="sm" fontWeight="medium" mb={1}>Description</Text>
                            <Textarea
                                placeholder="Describe what this workflow does..."
                                value={workflow.description}
                                onChange={(e) => setWorkflow(prev => ({ ...prev, description: e.target.value }))}
                                bg="white"
                                rows={2}
                            />
                        </Box>
                    </VStack>
                </Box>

                {/* Node Addition Interface */}
                <Box borderWidth="1px" borderRadius="md" p={4}>
                    <Text fontSize="lg" fontWeight="medium" mb={3}>Add Node</Text>
                    <HStack wrap="wrap" gap={2}>
                        {NODE_TYPES.map((nodeType) => (
                            <Button
                                key={nodeType.value}
                                onClick={() => addNode(nodeType.value as NodeConfig['type'])}
                                variant="outline"
                                size="sm"
                                title={nodeType.description}
                            >
                                <LuPlus />
                                {nodeType.label}
                            </Button>
                        ))}
                    </HStack>

                    {workflow.definition.nodes.length === 0 && (
                        <Box bg="blue.50" p={3} borderRadius="md" mt={3}>
                            <Text fontSize="sm" color="blue.700">
                                Start by adding a Webhook Trigger node to define how your workflow will be triggered.
                            </Text>
                        </Box>
                    )}
                </Box>

                {/* Workflow Nodes */}
                {workflow.definition.nodes.length > 0 && (
                    <Box>
                        <Text fontSize="lg" fontWeight="medium" mb={4}>
                            Workflow Nodes ({workflow.definition.nodes.length})
                        </Text>

                        <VStack align="stretch" gap={4}>
                            {workflow.definition.nodes.map((node, index) => (
                                <Box key={node.id}>
                                    {index > 0 && (
                                        <Box textAlign="center" py={2}>
                                            <Text fontSize="sm" color="gray.500">↓ then</Text>
                                        </Box>
                                    )}
                                    {renderNode(node)}
                                </Box>
                            ))}
                        </VStack>
                    </Box>
                )}

                {/* Workflow JSON Preview (for debugging) */}
                {workflow.definition.nodes.length > 0 && (
                    <Box borderWidth="1px" borderRadius="md" p={4} bg="gray.50">
                        <Text fontSize="sm" fontWeight="medium" mb={2}>Workflow Definition (JSON)</Text>
                        <Box
                            bg="white"
                            p={3}
                            borderRadius="md"
                            fontSize="xs"
                            fontFamily="mono"
                            maxHeight="200px"
                            overflowY="auto"
                        >
                            <pre>{JSON.stringify(workflow.definition, null, 2)}</pre>
                        </Box>
                    </Box>
                )}
            </VStack>
        </Layout>
    );
};