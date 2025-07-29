import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Button,
    Input,
    VStack,
    Heading,
    useToast,
    Text,
    Tooltip,
    Icon,
    Alert,
    AlertIcon
} from '@chakra-ui/react';
import { InfoIcon } from '@chakra-ui/icons';
import { useAuth } from '../../contexts/AuthContext';
import { authService } from '../../services/api';

export const RegisterForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();
    const toast = useToast();

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError('');

        // Validate password confirmation
        if (password !== confirmPassword) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        try {
            await authService.register(email, password);

            // After successful registration, automatically log in
            const loginResponse = await authService.login(email, password);
            const accessToken = loginResponse.access_token;
            login(accessToken);

            toast({
                title: 'Registration Successful.',
                description: 'Welcome to AutomateOS!',
                status: 'success',
                duration: 3000,
                isClosable: true,
            });

            // Navigate to dashboard after successful registration
            navigate('/');

        } catch (error: any) {
            console.error('Registration error:', error);

            let errorMessage = 'An unexpected error occurred.';
            if (error.response?.status === 400) {
                errorMessage = 'Email already registered or invalid data.';
            } else if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            }

            setError(errorMessage);

            toast({
                title: 'Registration Failed',
                description: errorMessage,
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box
            borderWidth="1px"
            borderRadius="lg"
            p={6}
            boxShadow="lg"
            bg="white"
        >
            <form onSubmit={handleSubmit}>
                <VStack gap={4}>
                    <Heading size="lg" textAlign="center">Sign Up</Heading>

                    {error && (
                        <Box p={3} bg="red.100" borderRadius="md" color="red.800" width="full">
                            {error}
                        </Box>
                    )}

                    <Alert status="info" borderRadius="md">
                        <AlertIcon />
                        <Text fontSize="sm">
                            Create your AutomateOS account to start building workflow automations.
                        </Text>
                    </Alert>

                    <Box width="full">
                        <Box mb={2} fontWeight="medium" display="flex" alignItems="center" gap={2}>
                            Email address *
                            <Tooltip
                                label="This will be your login username. Choose a valid email address you have access to."
                                placement="top"
                            >
                                <Icon as={InfoIcon} color="gray.400" boxSize={3} />
                            </Tooltip>
                        </Box>
                        <Input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email address"
                            disabled={loading}
                            required
                        />
                        <Text fontSize="sm" color="gray.500" mt={1}>
                            We'll never share your email with anyone else.
                        </Text>
                    </Box>

                    <Box width="full">
                        <Box mb={2} fontWeight="medium" display="flex" alignItems="center" gap={2}>
                            Password *
                            <Tooltip
                                label="Choose a strong password with at least 8 characters for better security"
                                placement="top"
                            >
                                <Icon as={InfoIcon} color="gray.400" boxSize={3} />
                            </Tooltip>
                        </Box>
                        <Input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Create a secure password"
                            disabled={loading}
                            required
                            minLength={8}
                        />
                        <Text fontSize="sm" color="gray.500" mt={1}>
                            Minimum 8 characters. Use a mix of letters, numbers, and symbols.
                        </Text>
                    </Box>

                    <Box width="full">
                        <Box mb={2} fontWeight="medium" display="flex" alignItems="center" gap={2}>
                            Confirm Password *
                            <Tooltip
                                label="Re-enter your password to make sure it's correct"
                                placement="top"
                            >
                                <Icon as={InfoIcon} color="gray.400" boxSize={3} />
                            </Tooltip>
                        </Box>
                        <Input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="Confirm your password"
                            disabled={loading}
                            required
                            minLength={8}
                        />
                        {password && confirmPassword && password !== confirmPassword && (
                            <Text fontSize="sm" color="red.500" mt={1}>
                                Passwords do not match
                            </Text>
                        )}
                    </Box>

                    <Button
                        type="submit"
                        colorScheme="blue"
                        width="full"
                        disabled={loading}
                    >
                        {loading ? 'Creating Account...' : 'Sign Up'}
                    </Button>
                </VStack>
            </form>
        </Box>
    );
};