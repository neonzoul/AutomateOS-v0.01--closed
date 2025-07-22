import { useState } from 'react';
import {
    Box,
    Button,
    Input,
    VStack,
    Heading
} from '@chakra-ui/react';
import axios from 'axios';

export const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError('');

        // Create form data as required by OAuth2PasswordRequestForm
        const params = new URLSearchParams();
        params.append('username', email); // OAuth2 uses 'username' field for email
        params.append('password', password);

        try {
            const response = await axios.post('http://127.0.0.1:8080/auth/token', params, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            const accessToken = response.data.access_token;

            // Show success message in console for now
            console.log('✅ Login Successful! Welcome back!');

            console.log('Access Token:', accessToken);
            console.log('Token Type:', response.data.token_type);

            // Store token in localStorage for future API calls
            localStorage.setItem('access_token', accessToken);

        } catch (error: any) {
            console.error('Login error:', error);

            let errorMessage = 'An unexpected error occurred.';
            if (error.response?.status === 401) {
                errorMessage = 'Incorrect email or password.';
            } else if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            }

            setError(errorMessage);

            // Show error message in console for now
            console.log('❌ Login Failed:', errorMessage);
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