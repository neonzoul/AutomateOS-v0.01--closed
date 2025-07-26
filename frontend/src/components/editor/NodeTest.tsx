import React, { useState } from 'react';
import { VStack, Container, Heading } from '@chakra-ui/react';
import { NodeBase, WebhookTriggerNode, HTTPRequestNode, FilterNode, validateNode } from './index';
import type { NodeConfig } from './index';

const NodeTest: React.FC = () => {
    const [webhookNode] = useState<NodeConfig>({
        id: 'webhook-1',
        type: 'webhook',
        config: { path: '/webhook/test' }
    });

    const [httpNode] = useState<NodeConfig>({
        id: 'http-1',
        type: 'http_request',
        config: {
            url: 'https://api.example.com/test',
            method: 'GET',
            headers: {},
            timeout: 30
        }
    });

    const [filterNode] = useState<NodeConfig>({
        id: 'filter-1',
        type: 'filter',
        config: {
            conditions: [],
            logic: 'AND',
            continue_on: true
        }
    });

    const updateNode = (nodeId: string, config: Record<string, any>) => {
        console.log('Update node:', nodeId, config);
    };

    const deleteNode = (nodeId: string) => {
        console.log('Delete node:', nodeId);
    };

    return (
        <Container maxW="4xl" py={8}>
            <VStack align="stretch" gap={6}>
                <Heading size="lg">Node Components Test</Heading>

                <NodeBase
                    node={webhookNode}
                    onUpdate={updateNode}
                    onDelete={deleteNode}
                    validation={validateNode(webhookNode)}
                >
                    <WebhookTriggerNode
                        config={webhookNode.config}
                        onConfigUpdate={() => { }}
                    />
                </NodeBase>

                <NodeBase
                    node={httpNode}
                    onUpdate={updateNode}
                    onDelete={deleteNode}
                    validation={validateNode(httpNode)}
                >
                    <HTTPRequestNode
                        config={httpNode.config}
                        onConfigUpdate={() => { }}
                    />
                </NodeBase>

                <NodeBase
                    node={filterNode}
                    onUpdate={updateNode}
                    onDelete={deleteNode}
                    validation={validateNode(filterNode)}
                >
                    <FilterNode
                        config={filterNode.config}
                        onConfigUpdate={() => { }}
                    />
                </NodeBase>
            </VStack>
        </Container>
    );
};

export default NodeTest;