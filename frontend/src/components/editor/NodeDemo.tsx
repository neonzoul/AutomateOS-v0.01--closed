import React, { useState } from 'react';
import {
    VStack,
    HStack,
    Button,
    Container,
    Heading,
    Separator,
} from '@chakra-ui/react';
import {
    NodeBase,
    WebhookTriggerNode,
    HTTPRequestNode,
    FilterNode,
    validateNode
} from './index';
import type { NodeConfig } from './index';

const NodeDemo: React.FC = () => {
    const [nodes, setNodes] = useState<NodeConfig[]>([]);
    const [nodeCounter, setNodeCounter] = useState(1);

    const addNode = (type: NodeConfig['type']) => {
        const newNode: NodeConfig = {
            id: `${type}_${nodeCounter}`,
            type,
            config: getDefaultConfig(type),
        };

        setNodes([...nodes, newNode]);
        setNodeCounter(nodeCounter + 1);
    };

    const getDefaultConfig = (type: NodeConfig['type']) => {
        switch (type) {
            case 'webhook':
                return { path: `/webhook/${Date.now()}` };
            case 'http_request':
                return {
                    url: '',
                    method: 'GET',
                    headers: {},
                    timeout: 30
                };
            case 'filter':
                return {
                    conditions: [],
                    logic: 'AND',
                    continue_on: true
                };
            default:
                return {};
        }
    };

    const updateNode = (nodeId: string, config: Record<string, any>) => {
        setNodes(nodes.map(node =>
            node.id === nodeId
                ? { ...node, config }
                : node
        ));
    };

    const deleteNode = (nodeId: string) => {
        setNodes(nodes.filter(node => node.id !== nodeId));
    };

    const renderNodeContent = (node: NodeConfig) => {
        switch (node.type) {
            case 'webhook':
                return <WebhookTriggerNode config={node.config} onConfigUpdate={() => { }} />;
            case 'http_request':
                return <HTTPRequestNode config={node.config} onConfigUpdate={() => { }} />;
            case 'filter':
                return <FilterNode config={node.config} onConfigUpdate={() => { }} />;
            default:
                return null;
        }
    };

    return (
        <Container maxW="4xl" py={8}>
            <VStack align="stretch" gap={6}>
                <Heading size="lg">Node Configuration Components Demo</Heading>

                <HStack>
                    <Button onClick={() => addNode('webhook')} colorPalette="green">
                        Add Webhook Trigger
                    </Button>
                    <Button onClick={() => addNode('http_request')} colorPalette="blue">
                        Add HTTP Request
                    </Button>
                    <Button onClick={() => addNode('filter')} colorPalette="orange">
                        Add Filter
                    </Button>
                </HStack>

                <Separator />

                <VStack align="stretch" gap={4}>
                    {nodes.map((node) => (
                        <NodeBase
                            key={node.id}
                            node={node}
                            onUpdate={updateNode}
                            onDelete={deleteNode}
                            validation={validateNode(node)}
                        >
                            {renderNodeContent(node)}
                        </NodeBase>
                    ))}
                </VStack>

                {nodes.length === 0 && (
                    <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
                        Add a node to get started
                    </div>
                )}
            </VStack>
        </Container>
    );
};

export default NodeDemo;