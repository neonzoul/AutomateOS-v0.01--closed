import { useState } from 'react';
import {
    Button,
    FormControl,
    FormLabel,
    Input,
    Stack,
    Heading,
    useToast
} from '@chakra-ui/react';
import axios from 'axios';

export const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const toast = useToast();

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setIsLoading(true);

        // Create form data as required by OAuth2PasswordRequestForm
        const params = new URLSearchParams();
        params.append('username', email); // OAuth2 uses 'username' field for email
        params.append('password', password);

        try {
            const response = await axios.post('http://127.0.0.1:8000/auth/token', params, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            const accessToken = response.data.access_token;

            toast({
                title: 'Login Successful!',
                description: `Welcome back! Token received.`,
                status: 'success',
                duration: 5000,
                isClosable: true,
            });

            console.log('Access Token:', accessToken);
            console.log('Token Type:', response.data.token_type);

            // TODO: Store this token in localStorage or context for future API calls
            // localStorage.setItem('access_token', accessToken);

        } catch (error: any) {
            console.error('Login error:', error);

            let errorMessage = 'An unexpected error occurred.';
            if (error.response?.status === 401) {
                errorMessage = 'Incorrect email or password.';
            } else if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            }

            toast({
                title: 'Login Failed',
                description: errorMessage,
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <Stack spacing={4} width="350px" margin="auto" mt={10}>
                <Heading size="lg" textAlign="center">Log In</Heading>

                <FormControl isRequired>
                    <FormLabel>Email address</FormLabel>
                    <Input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter your email"
                        disabled={isLoading}
                    />
                </FormControl>

                <FormControl isRequired>
                    <FormLabel>Password</FormLabel>
                    <Input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter your password"
                        disabled={isLoading}
                    />
                </FormControl>

                <Button
                    type="submit"
                    colorScheme="blue"
                    isLoading={isLoading}
                    loadingText="Logging in..."
                >
                    Log In
                </Button>
            </Stack>
        </form>
    );
};