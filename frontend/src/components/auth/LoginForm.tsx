import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Button,
    Input,
    VStack,
    Heading,
    createToaster
} from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';
import { authService } from '../../services/api';

const toaster = createToaster({
    placement: 'top',
});

export const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await authService.login(email, password);
            const accessToken = response.access_token;
            login(accessToken);

            toaster.create({
                title: 'Login Successful.',
                type: 'success',
                duration: 3000,
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

            toaster.create({
                title: 'Login Failed',
                description: errorMessage,
                type: 'error',
                duration: 5000,
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
                        <Box mb={2} fontWeight="medium">Email address *</Box>
                        <Input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email"
                            disabled={loading}
                            required
                        />
                    </Box>

                    <Box width="full">
                        <Box mb={2} fontWeight="medium">Password *</Box>
                        <Input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            disabled={loading}
                            required
                        />
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