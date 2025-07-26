import React from 'react';
import {
    VStack,
    HStack,
    Text,
    Input,
    NativeSelectRoot,
    NativeSelectField,
    Button,
    Box,
    IconButton,
    Separator,
} from '@chakra-ui/react';
import { LuPlus, LuTrash2 } from 'react-icons/lu';

export interface FilterCondition {
    field: string;
    operator: string;
    value: string;
    type: 'string' | 'number' | 'boolean';
}

export interface FilterConfig {
    conditions?: FilterCondition[];
    logic?: 'AND' | 'OR';
    continue_on?: boolean;
}

interface FilterNodeProps {
    config: FilterConfig;
    onConfigUpdate: (config: FilterConfig) => void;
}

const OPERATORS = {
    string: [
        { value: 'equals', label: 'equals' },
        { value: 'not_equals', label: 'not equals' },
        { value: 'contains', label: 'contains' },
        { value: 'not_contains', label: 'does not contain' },
        { value: 'starts_with', label: 'starts with' },
        { value: 'ends_with', label: 'ends with' },
        { value: 'is_empty', label: 'is empty' },
        { value: 'is_not_empty', label: 'is not empty' },
    ],
    number: [
        { value: 'equals', label: '=' },
        { value: 'not_equals', label: '≠' },
        { value: 'greater_than', label: '>' },
        { value: 'greater_than_or_equal', label: '≥' },
        { value: 'less_than', label: '<' },
        { value: 'less_than_or_equal', label: '≤' },
    ],
    boolean: [
        { value: 'is_true', label: 'is true' },
        { value: 'is_false', label: 'is false' },
    ],
};

export const FilterNode: React.FC<FilterNodeProps> = ({
    config,
    onConfigUpdate,
}) => {
    const conditions = config.conditions || [];
    const logic = config.logic || 'AND';
    const continueOn = config.continue_on !== false; // Default to true

    const addCondition = () => {
        const newCondition: FilterCondition = {
            field: '',
            operator: 'equals',
            value: '',
            type: 'string',
        };

        onConfigUpdate({
            ...config,
            conditions: [...conditions, newCondition],
        });
    };

    const updateCondition = (index: number, updates: Partial<FilterCondition>) => {
        const newConditions = [...conditions];
        newConditions[index] = { ...newConditions[index], ...updates };

        // Reset operator when type changes
        if (updates.type && updates.type !== newConditions[index].type) {
            newConditions[index].operator = OPERATORS[updates.type][0].value;
        }

        onConfigUpdate({
            ...config,
            conditions: newConditions,
        });
    };

    const removeCondition = (index: number) => {
        const newConditions = conditions.filter((_, i) => i !== index);
        onConfigUpdate({
            ...config,
            conditions: newConditions,
        });
    };

    const updateLogic = (newLogic: 'AND' | 'OR') => {
        onConfigUpdate({
            ...config,
            logic: newLogic,
        });
    };

    const updateContinueOn = (value: boolean) => {
        onConfigUpdate({
            ...config,
            continue_on: value,
        });
    };

    const needsValue = (operator: string) => {
        return !['is_empty', 'is_not_empty', 'is_true', 'is_false'].includes(operator);
    };

    return (
        <VStack align="stretch" gap={4}>
            <Text fontSize="sm" color="gray.600">
                Filter workflow execution based on conditions. The workflow continues only if conditions are met.
            </Text>

            <Box>
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Continue workflow when conditions are:
                </Text>
                <HStack>
                    <Button
                        size="sm"
                        variant={continueOn ? "solid" : "outline"}
                        colorPalette="green"
                        onClick={() => updateContinueOn(!continueOn)}
                    >
                        {continueOn ? 'Met (true)' : 'Not met (false)'}
                    </Button>
                </HStack>
            </Box>

            <Separator />

            <Box>
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Conditions
                </Text>
                <VStack align="stretch" gap={3}>
                    {conditions.map((condition, index) => (
                        <Box key={index}>
                            {index > 0 && (
                                <HStack justify="center" mb={2}>
                                    <Button
                                        size="xs"
                                        variant={logic === 'AND' ? 'solid' : 'outline'}
                                        colorPalette="blue"
                                        onClick={() => updateLogic('AND')}
                                    >
                                        AND
                                    </Button>
                                    <Button
                                        size="xs"
                                        variant={logic === 'OR' ? 'solid' : 'outline'}
                                        colorPalette="blue"
                                        onClick={() => updateLogic('OR')}
                                    >
                                        OR
                                    </Button>
                                </HStack>
                            )}

                            <HStack>
                                <Input
                                    placeholder="{{node_id.field}} or field_name"
                                    value={condition.field}
                                    onChange={(e) => updateCondition(index, { field: e.target.value })}
                                    size="sm"
                                    flex={2}
                                />

                                <NativeSelectRoot size="sm" flex={1}>
                                    <NativeSelectField
                                        value={condition.type}
                                        onChange={(e) => updateCondition(index, {
                                            type: e.target.value as FilterCondition['type']
                                        })}
                                    >
                                        <option value="string">Text</option>
                                        <option value="number">Number</option>
                                        <option value="boolean">Boolean</option>
                                    </NativeSelectField>
                                </NativeSelectRoot>

                                <NativeSelectRoot size="sm" flex={1}>
                                    <NativeSelectField
                                        value={condition.operator}
                                        onChange={(e) => updateCondition(index, { operator: e.target.value })}
                                    >
                                        {OPERATORS[condition.type].map((op) => (
                                            <option key={op.value} value={op.value}>
                                                {op.label}
                                            </option>
                                        ))}
                                    </NativeSelectField>
                                </NativeSelectRoot>

                                {needsValue(condition.operator) && (
                                    <Input
                                        placeholder="Value"
                                        value={condition.value}
                                        onChange={(e) => updateCondition(index, { value: e.target.value })}
                                        size="sm"
                                        flex={1}
                                        type={condition.type === 'number' ? 'number' : 'text'}
                                    />
                                )}

                                <IconButton
                                    aria-label="Remove condition"
                                    size="sm"
                                    variant="ghost"
                                    colorPalette="red"
                                    onClick={() => removeCondition(index)}
                                >
                                    <LuTrash2 />
                                </IconButton>
                            </HStack>
                        </Box>
                    ))}

                    <Button
                        size="sm"
                        variant="outline"
                        onClick={addCondition}
                    >
                        <LuPlus />
                        Add Condition
                    </Button>
                </VStack>
            </Box>

            {conditions.length > 0 && (
                <>
                    <Separator />
                    <Box bg="orange.50" p={3} borderRadius="md">
                        <Text fontSize="xs" color="orange.700" mb={2}>
                            <strong>Preview:</strong>
                        </Text>
                        <Text fontSize="xs" color="orange.600" fontFamily="mono">
                            {conditions.length === 0
                                ? 'No conditions defined'
                                : conditions.map((cond, i) => (
                                    <span key={i}>
                                        {i > 0 && ` ${logic} `}
                                        {cond.field} {OPERATORS[cond.type].find(op => op.value === cond.operator)?.label}
                                        {needsValue(cond.operator) && ` "${cond.value}"`}
                                    </span>
                                ))
                            }
                        </Text>
                        <Text fontSize="xs" color="orange.600" mt={1}>
                            → Continue workflow: {continueOn ? 'when TRUE' : 'when FALSE'}
                        </Text>
                    </Box>
                </>
            )}

            <Box bg="blue.50" p={3} borderRadius="md">
                <Text fontSize="xs" color="blue.700">
                    <strong>Dynamic Data:</strong> Use {`{{node_id.field}}`} syntax to reference data from previous nodes.
                    Example: {`{{http_request_1.status}}`} or {`{{webhook_trigger.payload.user_id}}`}
                </Text>
            </Box>
        </VStack>
    );
};