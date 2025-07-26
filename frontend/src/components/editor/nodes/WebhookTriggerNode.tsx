import React, { useState } from 'react';
import {
    VStack,
    HStack,
    Text,
    Input,
    Button,
    Code,
    Box,
    createToaster,
} from '@chakra-ui/react';
import { LuCopy } from 'react-icons/lu';

export interface WebhookConfig {
    method?: string;
    path?: string;
}

interface WebhookTriggerNodeProps {
    config: WebhookConfig;
    onConfigUpdate: (config: WebhookConfig) => void;
}

const toaster = createToaster({
    placement: 'top',
});

export const WebhookTriggerNode: React.FC<WebhookTriggerNodeProps> = ({
    config,
    onConfigUpdate,
}) => {
    const [copying, setCopying] = useState(false);

    const webhookPath = config.path || '/webhook/default';
    const fullWebhookUrl = `${window.location.origin}/api/v1${webhookPath}`;

    const handlePathChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const newPath = event.target.value;
        onConfigUpdate({
            ...config,
            path: newPath.startsWith('/') ? newPath : `/${newPath}`,
        });
    };

    const copyWebhookUrl = async () => {
        try {
            setCopying(true);
            await navigator.clipboard.writeText(fullWebhookUrl);
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

    return (
        <VStack align="stretch" gap={4}>
            <Text fontSize="sm" color="gray.600">
                This node triggers the workflow when a webhook is called.
            </Text>

            <Box>
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Webhook Path
                </Text>
                <Input
                    placeholder="/webhook/my-trigger"
                    value={config.path || ''}
                    onChange={handlePathChange}
                    size="sm"
                />
            </Box>

            <Box>
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Generated Webhook URL:
                </Text>
                <HStack>
                    <Code
                        p={2}
                        fontSize="xs"
                        bg="gray.50"
                        borderRadius="md"
                        flex={1}
                        wordBreak="break-all"
                    >
                        {fullWebhookUrl}
                    </Code>
                    <Button
                        size="sm"
                        onClick={copyWebhookUrl}
                        variant="outline"
                        disabled={copying}
                    >
                        <LuCopy />
                        Copy
                    </Button>
                </HStack>
            </Box>

            <Box bg="blue.50" p={3} borderRadius="md">
                <Text fontSize="xs" color="blue.700">
                    <strong>Usage:</strong> Send a POST request to this URL to trigger the workflow.
                    The request body will be available as data in subsequent nodes.
                </Text>
            </Box>
        </VStack>
    );
};