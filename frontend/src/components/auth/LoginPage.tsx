import { useState } from 'react';
import { Box, Heading, Text, Container, Button, HStack } from '@chakra-ui/react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';

export const LoginPage = () => {
    const [showRegister, setShowRegister] = useState(false);

    return (
        <Box minHeight="100vh" bg="gray.50" py={8}>
            <Container maxW="md">
                <Heading size="xl" textAlign="center" mb={2} color="blue.600">
                    AutomateOS
                </Heading>
                <Text textAlign="center" color="gray.600" mb={8}>
                    Your Personal Workflow Automation Platform
                </Text>

                {showRegister ? <RegisterForm /> : <LoginForm />}

                <Box mt={6} textAlign="center">
                    <HStack justify="center" gap={2}>
                        <Text color="gray.600">
                            {showRegister ? 'Already have an account?' : "Don't have an account?"}
                        </Text>
                        <Button
                            variant="ghost"
                            colorScheme="blue"
                            onClick={() => setShowRegister(!showRegister)}
                        >
                            {showRegister ? 'Sign In' : 'Sign Up'}
                        </Button>
                    </HStack>
                </Box>
            </Container>
        </Box>
    );
};