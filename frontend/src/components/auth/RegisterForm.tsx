import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Button,
    Input,
    VStack,
    Heading,
    createToaster,
    Text,
    Icon
} from '@chakra-ui/react';
import {
    TooltipContent,
    TooltipRoot,
    TooltipTrigger,
} from '@chakra-ui/react';
import {
    AlertRoot,
    AlertDescription,
} from '@chakra-ui/react';
import { LuInfo } from 'react-icons/lu';
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
    const toaster = createToaster({
        placement: 'top',
    });

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

                    <AlertRoot status="info" borderRadius="md">
                        <Icon as={LuInfo} color="blue.500" />
                        <AlertDescription fontSize="sm">
                            Create your AutomateOS account to start building workflow automations.
                        </AlertDescription>
                    </AlertRoot>

                    <Box width="full">
                        <Box mb={2} fontWeight="medium" display="flex" alignItems="center" gap={2}>
                            Email address *
                            <TooltipRoot>
                                <TooltipTrigger asChild>
                                    <Icon as={InfoIcon} color="gray.400" boxSize={3} />
                                </TooltipTrigger>
                                <TooltipContent>
                                    This will be your login username. Choose a valid email address you have access to.
                                </TooltipContent>
                            </TooltipRoot>
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
                            <TooltipRoot>
                                <TooltipTrigger asChild>
                                    <Icon as={InfoIcon} color="gray.400" boxSize={3} />
                                </TooltipTrigger>
                                <TooltipContent>
                                    Choose a strong password with at least 8 characters for better security
                                </TooltipContent>
                            </TooltipRoot>
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
                            <TooltipRoot>
                                <TooltipTrigger asChild>
                                    <Icon as={InfoIcon} color="gray.400" boxSize={3} />
                                </TooltipTrigger>
                                <TooltipContent>
                                    Re-enter your password to make sure it's correct
                                </TooltipContent>
                            </TooltipRoot>
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