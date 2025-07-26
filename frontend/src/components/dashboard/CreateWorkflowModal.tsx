import React from 'react';

interface CreateWorkflowModalProps {
    isOpen: boolean;
    onClose: () => void;
    onWorkflowCreated: () => void;
}

// This component is deprecated - we now navigate directly to the workflow editor
export const CreateWorkflowModal: React.FC<CreateWorkflowModalProps> = () => {
    return null;
};