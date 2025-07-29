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
    Icon
} from '@chakra-ui/react';
import { InfoIcon } from '@chakra-ui/icons';
import { useAuth } from '../../contexts/AuthContext';
import { authService } from '../../services/api';

export const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();
    const toast = useToast();

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await authService.login(email, password);
            const accessToken = response.access_token;
            login(accessToken);

            toast({
                title: 'Login Successful.',
                status: 'success',
                duration: 3000,
                isClosable: true,
            });

            // Navigate to dashboard after successful login
            navigate('/');

        } catch (error: any) {
            console.error('Login error:', error);

            let errorMessage = 'An unexpected error occurred.';
            if (error.response?.status === 401) {
                errorMessage = 'Incorrect email or password.';
            } else if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            }

            setError(errorMessage);

            toast({
                title: 'Login Failed',
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
                    <Heading size="lg" textAlign="center">Log In</Heading>

                    {error && (
                        <Box p={3} bg="red.100" borderRadius="md" color="red.800" width="full">
                            {error}
                        </Box>
                    )}

                    <Box width="full">
                        <Box mb={2} fontWeight="medium" display="flex" alignItems="center" gap={2}>
                            Email address *
                            <Tooltip
                                label="Enter the email address you used to register your account"
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
                    </Box>

                    <Box width="full">
                        <Box mb={2} fontWeight="medium" display="flex" alignItems="center" gap={2}>
                            Password *
                            <Tooltip
                                label="Enter your account password"
                                placement="top"
                            >
                                <Icon as={InfoIcon} color="gray.400" boxSize={3} />
                            </Tooltip>
                        </Box>
                        <Input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            disabled={loading}
                            required
                        />
                        <Text fontSize="sm" color="gray.500" mt={1}>
                            Forgot your password? Contact support for assistance.
                        </Text>
                    </Box>

                    <Button
                        type="submit"
                        colorScheme="blue"
                        width="full"
                        disabled={loading}
                    >
                        {loading ? 'Logging in...' : 'Log In'}
                    </Button>
                </VStack>
            </form>
        </Box>
    );
};