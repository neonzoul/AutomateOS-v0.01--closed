import React, { useState } from 'react';
import {
    VStack,
    HStack,
    Text,
    Input,
    NativeSelectRoot,
    NativeSelectField,
    Textarea,
    Button,
    Box,
    IconButton,
    Separator,
} from '@chakra-ui/react';
import { LuPlus, LuTrash2 } from 'react-icons/lu';

export interface HTTPRequestConfig {
    url?: string;
    method?: string;
    headers?: Record<string, string>;
    body?: string;
    timeout?: number;
}

interface HTTPRequestNodeProps {
    config: HTTPRequestConfig;
    onConfigUpdate: (config: HTTPRequestConfig) => void;
}

const HTTP_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'];

export const HTTPRequestNode: React.FC<HTTPRequestNodeProps> = ({
    config,
    onConfigUpdate,
}) => {
    const [newHeaderKey, setNewHeaderKey] = useState('');
    const [newHeaderValue, setNewHeaderValue] = useState('');

    const headers = config.headers || {};

    const handleFieldChange = (field: keyof HTTPRequestConfig, value: any) => {
        onConfigUpdate({
            ...config,
            [field]: value,
        });
    };

    const addHeader = () => {
        if (newHeaderKey.trim() && newHeaderValue.trim()) {
            handleFieldChange('headers', {
                ...headers,
                [newHeaderKey.trim()]: newHeaderValue.trim(),
            });
            setNewHeaderKey('');
            setNewHeaderValue('');
        }
    };

    const removeHeader = (key: string) => {
        const newHeaders = { ...headers };
        delete newHeaders[key];
        handleFieldChange('headers', newHeaders);
    };

    const updateHeader = (oldKey: string, newKey: string, newValue: string) => {
        const newHeaders = { ...headers };
        if (oldKey !== newKey) {
            delete newHeaders[oldKey];
        }
        newHeaders[newKey] = newValue;
        handleFieldChange('headers', newHeaders);
    };

    return (
        <VStack align="stretch" gap={4}>
            <Text fontSize="sm" color="gray.600">
                Make an HTTP request to an external API or service.
            </Text>

            <HStack>
                <Box flex={1}>
                    <Text fontSize="sm" fontWeight="medium" mb={2}>
                        Method
                    </Text>
                    <NativeSelectRoot size="sm">
                        <NativeSelectField
                            value={config.method || 'GET'}
                            onChange={(e) => handleFieldChange('method', e.target.value)}
                        >
                            {HTTP_METHODS.map((method) => (
                                <option key={method} value={method}>
                                    {method}
                                </option>
                            ))}
                        </NativeSelectField>
                    </NativeSelectRoot>
                </Box>

                <Box flex={3}>
                    <Text fontSize="sm" fontWeight="medium" mb={2}>
                        URL
                    </Text>
                    <Input
                        placeholder="https://api.example.com/endpoint"
                        value={config.url || ''}
                        onChange={(e) => handleFieldChange('url', e.target.value)}
                        size="sm"
                    />
                </Box>
            </HStack>

            <Box>
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Headers
                </Text>
                <VStack align="stretch" gap={2}>
                    {Object.entries(headers).map(([key, value]) => (
                        <HStack key={key}>
                            <Input
                                placeholder="Header name"
                                value={key}
                                onChange={(e) => updateHeader(key, e.target.value, value)}
                                size="sm"
                                flex={1}
                            />
                            <Input
                                placeholder="Header value"
                                value={value}
                                onChange={(e) => updateHeader(key, key, e.target.value)}
                                size="sm"
                                flex={1}
                            />
                            <IconButton
                                aria-label="Remove header"
                                size="sm"
                                variant="ghost"
                                colorPalette="red"
                                onClick={() => removeHeader(key)}
                            >
                                <LuTrash2 />
                            </IconButton>
                        </HStack>
                    ))}

                    <HStack>
                        <Input
                            placeholder="Header name"
                            value={newHeaderKey}
                            onChange={(e) => setNewHeaderKey(e.target.value)}
                            size="sm"
                            flex={1}
                        />
                        <Input
                            placeholder="Header value"
                            value={newHeaderValue}
                            onChange={(e) => setNewHeaderValue(e.target.value)}
                            size="sm"
                            flex={1}
                        />
                        <Button
                            size="sm"
                            onClick={addHeader}
                            disabled={!newHeaderKey.trim() || !newHeaderValue.trim()}
                        >
                            <LuPlus />
                            Add
                        </Button>
                    </HStack>
                </VStack>
            </Box>

            {(config.method === 'POST' || config.method === 'PUT' || config.method === 'PATCH') && (
                <Box>
                    <Text fontSize="sm" fontWeight="medium" mb={2}>
                        Request Body
                    </Text>
                    <Textarea
                        placeholder='{"key": "value"} or use {{previous_node.data}} for dynamic data'
                        value={config.body || ''}
                        onChange={(e) => handleFieldChange('body', e.target.value)}
                        size="sm"
                        rows={4}
                        fontFamily="mono"
                    />
                </Box>
            )}

            <Box>
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Timeout (seconds)
                </Text>
                <Input
                    type="number"
                    placeholder="30"
                    value={config.timeout || ''}
                    onChange={(e) => handleFieldChange('timeout', parseInt(e.target.value) || 30)}
                    size="sm"
                    min={1}
                    max={300}
                />
            </Box>

            <Separator />

            <Box bg="blue.50" p={3} borderRadius="md">
                <Text fontSize="xs" color="blue.700">
                    <strong>Dynamic Data:</strong> Use {`{{node_id.field}}`} syntax to reference data from previous nodes.
                    The response will be available as data for subsequent nodes.
                </Text>
            </Box>
        </VStack>
    );
};