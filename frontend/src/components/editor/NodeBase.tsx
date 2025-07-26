import React from 'react';
import {
    Box,
    VStack,
    HStack,
    Text,
    IconButton,
    Badge,
    Separator,
} from '@chakra-ui/react';
import { LuTrash2 } from 'react-icons/lu';

export interface NodeConfig {
    id: string;
    type: 'webhook' | 'http_request' | 'filter';
    config: Record<string, any>;
}

export interface NodeValidation {
    isValid: boolean;
    errors: string[];
}

export interface NodeBaseProps {
    node: NodeConfig;
    onUpdate: (nodeId: string, config: Record<string, any>) => void;
    onDelete: (nodeId: string) => void;
    validation?: NodeValidation;
    children: React.ReactNode;
}

const NODE_TYPE_LABELS = {
    webhook: 'Webhook Trigger',
    http_request: 'HTTP Request',
    filter: 'Filter',
};

const NODE_TYPE_COLORS = {
    webhook: 'green',
    http_request: 'blue',
    filter: 'orange',
};

export const NodeBase: React.FC<NodeBaseProps> = ({
    node,
    onUpdate,
    onDelete,
    validation,
    children,
}) => {
    const handleConfigUpdate = (newConfig: Record<string, any>) => {
        onUpdate(node.id, { ...node.config, ...newConfig });
    };

    return (
        <Box
            borderWidth="1px"
            borderRadius="md"
            p={4}
            bg="white"
            shadow="sm"
            borderColor={validation?.isValid === false ? 'red.300' : 'gray.200'}
            _hover={{ shadow: 'md' }}
            transition="shadow 0.2s"
        >
            <VStack align="stretch" gap={3}>
                {/* Node Header */}
                <HStack justifyContent="space-between" align="center">
                    <HStack>
                        <Badge
                            colorPalette={NODE_TYPE_COLORS[node.type]}
                            variant="subtle"
                            fontSize="xs"
                        >
                            {NODE_TYPE_LABELS[node.type]}
                        </Badge>
                        <Text fontSize="sm" fontWeight="medium" color="gray.700">
                            {node.id}
                        </Text>
                    </HStack>
                    <IconButton
                        aria-label="Delete node"
                        size="sm"
                        variant="ghost"
                        colorPalette="red"
                        onClick={() => onDelete(node.id)}
                    >
                        <LuTrash2 />
                    </IconButton>
                </HStack>

                <Separator />

                {/* Node Configuration */}
                <Box>
                    {React.isValidElement(children)
                        ? React.cloneElement(children, {
                            config: node.config,
                            onConfigUpdate: handleConfigUpdate,
                        } as any)
                        : children
                    }
                </Box>

                {/* Validation Errors */}
                {validation && !validation.isValid && (
                    <Box>
                        <Separator />
                        <VStack align="stretch" gap={1} mt={2}>
                            {validation.errors.map((error, index) => (
                                <Text key={index} fontSize="xs" color="red.500">
                                    • {error}
                                </Text>
                            ))}
                        </VStack>
                    </Box>
                )}
            </VStack>
        </Box>
    );
};