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
    Tooltip,
    Icon,
    Alert,
    AlertIcon,
} from '@chakra-ui/react';
import { LuPlus, LuSave, LuPlay, LuArrowLeft, LuArrowUp, LuArrowDown, LuHistory, LuSettings, LuInfo } from 'react-icons/lu';
import { Layout } from '../common/Layout';
import { NodeBase } from './NodeBase';
import type { NodeConfig, NodeValidation } from './NodeBase';
import { WebhookTriggerNode } from './nodes/WebhookTriggerNode';
import { HTTPRequestNode } from './nodes/HTTPRequestNode';
import { FilterNode } from './nodes/FilterNode';
import { validateNode } from './nodeValidation';
import { workflowService } from '../../services/api';
import { ExecutionLogs } from '../dashboard/ExecutionLogs';

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
    const [activeTab, setActiveTab] = useState<'editor' | 'logs'>('editor');

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
            <VStack align="stretch" gap={{ base: 4, md: 6 }}>
                {/* Header */}
                <VStack align="stretch" gap={4}>
                    <HStack justifyContent="space-between" align="center" flexWrap="wrap">
                        <HStack minW="0" flex={1}>
                            <Button
                                variant="ghost"
                                onClick={() => navigate('/')}
                                size={{ base: "sm", md: "md" }}
                            >
                                <LuArrowLeft />
                                <Text display={{ base: "none", sm: "inline" }}>Back to Dashboard</Text>
                                <Text display={{ base: "inline", sm: "none" }}>Back</Text>
                            </Button>
                            <Text
                                fontSize={{ base: "lg", md: "2xl" }}
                                fontWeight="bold"
                                noOfLines={1}
                                minW="0"
                            >
                                {isEditing ? workflow.name || 'Edit Workflow' : 'Create Workflow'}
                            </Text>
                        </HStack>

                        <HStack gap={{ base: 2, md: 3 }} flexShrink={0}>
                            <Button
                                onClick={testWorkflow}
                                variant="outline"
                                colorPalette="blue"
                                disabled={testing || workflow.definition.nodes.length === 0}
                                size={{ base: "sm", md: "md" }}
                            >
                                <LuPlay />
                                <Text display={{ base: "none", sm: "inline" }}>
                                    {testing ? 'Testing...' : 'Test'}
                                </Text>
                            </Button>
                            <Button
                                onClick={saveWorkflow}
                                colorPalette="green"
                                disabled={saving}
                                size={{ base: "sm", md: "md" }}
                            >
                                <LuSave />
                                <Text display={{ base: "none", sm: "inline" }}>
                                    {saving ? 'Saving...' : 'Save'}
                                </Text>
                            </Button>
                        </HStack>
                    </HStack>
                </VStack>

                {/* Tab Navigation */}
                <HStack borderBottom="1px" borderColor="gray.200" mb={6}>
                    <Button
                        variant={activeTab === 'editor' ? 'solid' : 'ghost'}
                        onClick={() => setActiveTab('editor')}
                        size="sm"
                    >
                        <LuSettings />
                        Editor
                    </Button>
                    {isEditing && workflow.id && (
                        <Button
                            variant={activeTab === 'logs' ? 'solid' : 'ghost'}
                            onClick={() => setActiveTab('logs')}
                            size="sm"
                        >
                            <LuHistory />
                            Execution Logs
                        </Button>
                    )}
                </HStack>

                {/* Tab Content */}
                {activeTab === 'editor' && (
                    <VStack align="stretch" gap={6}>

                        {/* Workflow Basic Info */}
                        <Box borderWidth="1px" borderRadius="md" p={4} bg="gray.50">
                            <VStack align="stretch" gap={3}>
                                <HStack align="center" gap={2}>
                                    <Text fontSize="lg" fontWeight="medium">Workflow Information</Text>
                                    <Tooltip
                                        label="Configure basic workflow settings including name, description, and activation status"
                                        placement="top"
                                    >
                                        <Icon as={LuInfo} color="gray.400" boxSize={4} />
                                    </Tooltip>
                                </HStack>

                                <VStack align="stretch" gap={3}>
                                    <Box>
                                        <HStack align="center" gap={2} mb={1}>
                                            <Text fontSize="sm" fontWeight="medium">Name *</Text>
                                            <Tooltip
                                                label="Choose a descriptive name that helps you identify this workflow's purpose"
                                                placement="top"
                                            >
                                                <Icon as={LuInfo} color="gray.400" boxSize={3} />
                                            </Tooltip>
                                        </HStack>
                                        <Input
                                            placeholder="e.g., Send Welcome Email, Process Order"
                                            value={workflow.name}
                                            onChange={(e) => setWorkflow(prev => ({ ...prev, name: e.target.value }))}
                                            bg="white"
                                        />
                                    </Box>
                                    <Box>
                                        <HStack align="center" gap={2} mb={1}>
                                            <Text fontSize="sm" fontWeight="medium">Status</Text>
                                            <Tooltip
                                                label="Active workflows can be triggered via webhook. Inactive workflows are disabled."
                                                placement="top"
                                            >
                                                <Icon as={LuInfo} color="gray.400" boxSize={3} />
                                            </Tooltip>
                                        </HStack>
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
                                </VStack>

                                <Box>
                                    <HStack align="center" gap={2} mb={1}>
                                        <Text fontSize="sm" fontWeight="medium">Description</Text>
                                        <Tooltip
                                            label="Optional description to document what this workflow does and when it should be used"
                                            placement="top"
                                        >
                                            <Icon as={LuInfo} color="gray.400" boxSize={3} />
                                        </Tooltip>
                                    </HStack>
                                    <Textarea
                                        placeholder="e.g., Automatically sends a welcome email when a new user registers via webhook"
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
                            <HStack align="center" gap={2} mb={3}>
                                <Text fontSize="lg" fontWeight="medium">Add Node</Text>
                                <Tooltip
                                    label="Nodes are the building blocks of your workflow. Add them in the order you want them to execute."
                                    placement="top"
                                >
                                    <Icon as={LuInfo} color="gray.400" boxSize={4} />
                                </Tooltip>
                            </HStack>

                            <VStack align="stretch" gap={3}>
                                <HStack wrap="wrap" gap={2}>
                                    {NODE_TYPES.map((nodeType) => (
                                        <Tooltip
                                            key={nodeType.value}
                                            label={nodeType.description}
                                            placement="top"
                                        >
                                            <Button
                                                onClick={() => addNode(nodeType.value as NodeConfig['type'])}
                                                variant="outline"
                                                size="sm"
                                            >
                                                <LuPlus />
                                                {nodeType.label}
                                            </Button>
                                        </Tooltip>
                                    ))}
                                </HStack>

                                {workflow.definition.nodes.length === 0 && (
                                    <Alert status="info" borderRadius="md">
                                        <AlertIcon />
                                        <VStack align="start" gap={1}>
                                            <Text fontSize="sm" fontWeight="medium">
                                                Getting Started
                                            </Text>
                                            <Text fontSize="sm">
                                                1. Start by adding a <strong>Webhook Trigger</strong> to define how your workflow will be triggered<br />
                                                2. Add <strong>HTTP Request</strong> nodes to call external APIs<br />
                                                3. Use <strong>Filter</strong> nodes to add conditional logic
                                            </Text>
                                        </VStack>
                                    </Alert>
                                )}

                                {workflow.definition.nodes.length > 0 && workflow.definition.nodes[0].type !== 'webhook' && (
                                    <Alert status="warning" borderRadius="md">
                                        <AlertIcon />
                                        <Text fontSize="sm">
                                            <strong>Important:</strong> The first node should be a Webhook Trigger to define how your workflow starts.
                                        </Text>
                                    </Alert>
                                )}
                            </VStack>
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
                )}

                {activeTab === 'logs' && isEditing && workflow.id && (
                    <ExecutionLogs
                        workflowId={workflow.id}
                        workflowName={workflow.name}
                    />
                )}
            </VStack >
        </Layout >
    );
};