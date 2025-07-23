import { useState } from 'react';
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

export const RegisterForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { login } = useAuth();

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

            toaster.create({
                title: 'Registration Successful.',
                description: 'Welcome to AutomateOS!',
                type: 'success',
                duration: 3000,
            });

        } catch (error: any) {
            console.error('Registration error:', error);

            let errorMessage = 'An unexpected error occurred.';
            if (error.response?.status === 400) {
                errorMessage = 'Email already registered or invalid data.';
            } else if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            }

            setError(errorMessage);

            toaster.create({
                title: 'Registration Failed',
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
                    <Heading size="lg" textAlign="center">Sign Up</Heading>

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
                            minLength={6}
                        />
                    </Box>

                    <Box width="full">
                        <Box mb={2} fontWeight="medium">Confirm Password *</Box>
                        <Input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="Confirm your password"
                            disabled={loading}
                            required
                            minLength={6}
                        />
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