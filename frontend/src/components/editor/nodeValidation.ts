import type { NodeConfig, NodeValidation } from './NodeBase';
import type { WebhookConfig } from './nodes/WebhookTriggerNode';
import type { HTTPRequestConfig } from './nodes/HTTPRequestNode';
import type { FilterConfig } from './nodes/FilterNode';

export const validateWebhookNode = (config: WebhookConfig): NodeValidation => {
    const errors: string[] = [];

    if (!config.path || config.path.trim() === '') {
        errors.push('Webhook path is required');
    } else if (!config.path.startsWith('/')) {
        errors.push('Webhook path must start with "/"');
    }

    return {
        isValid: errors.length === 0,
        errors,
    };
};

export const validateHTTPRequestNode = (config: HTTPRequestConfig): NodeValidation => {
    const errors: string[] = [];

    if (!config.url || config.url.trim() === '') {
        errors.push('URL is required');
    } else {
        try {
            new URL(config.url);
        } catch {
            errors.push('URL must be a valid URL');
        }
    }

    if (!config.method) {
        errors.push('HTTP method is required');
    }

    // Validate headers
    if (config.headers) {
        Object.entries(config.headers).forEach(([key, value]) => {
            if (!key.trim()) {
                errors.push('Header names cannot be empty');
            }
            if (!value.trim()) {
                errors.push(`Header "${key}" cannot have empty value`);
            }
        });
    }

    // Validate JSON body for POST/PUT/PATCH requests
    if (config.body && ['POST', 'PUT', 'PATCH'].includes(config.method || '')) {
        const bodyStr = config.body.trim();
        if (bodyStr && !bodyStr.startsWith('{{') && !bodyStr.endsWith('}}')) {
            try {
                JSON.parse(bodyStr);
            } catch {
                errors.push('Request body must be valid JSON or use template syntax {{node.field}}');
            }
        }
    }

    // Validate timeout
    if (config.timeout !== undefined && (config.timeout < 1 || config.timeout > 300)) {
        errors.push('Timeout must be between 1 and 300 seconds');
    }

    return {
        isValid: errors.length === 0,
        errors,
    };
};

export const validateFilterNode = (config: FilterConfig): NodeValidation => {
    const errors: string[] = [];

    if (!config.conditions || config.conditions.length === 0) {
        errors.push('At least one condition is required');
        return { isValid: false, errors };
    }

    config.conditions.forEach((condition, index) => {
        if (!condition.field || condition.field.trim() === '') {
            errors.push(`Condition ${index + 1}: Field is required`);
        }

        if (!condition.operator) {
            errors.push(`Condition ${index + 1}: Operator is required`);
        }

        // Check if value is required for this operator
        const needsValue = !['is_empty', 'is_not_empty', 'is_true', 'is_false'].includes(condition.operator);
        if (needsValue && (!condition.value || condition.value.trim() === '')) {
            errors.push(`Condition ${index + 1}: Value is required for this operator`);
        }

        // Validate number values
        if (condition.type === 'number' && needsValue) {
            const value = condition.value;
            if (value && !value.startsWith('{{') && !value.endsWith('}}')) {
                if (isNaN(Number(value))) {
                    errors.push(`Condition ${index + 1}: Value must be a number or template`);
                }
            }
        }
    });

    return {
        isValid: errors.length === 0,
        errors,
    };
};

export const validateNode = (node: NodeConfig): NodeValidation => {
    switch (node.type) {
        case 'webhook':
            return validateWebhookNode(node.config as WebhookConfig);
        case 'http_request':
            return validateHTTPRequestNode(node.config as HTTPRequestConfig);
        case 'filter':
            return validateFilterNode(node.config as FilterConfig);
        default:
            return {
                isValid: false,
                errors: [`Unknown node type: ${node.type}`],
            };
    }
};