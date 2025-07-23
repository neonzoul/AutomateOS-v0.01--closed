import { useState } from 'react';
import { Box, Heading, Text, Container, Button, VStack, HStack } from '@chakra-ui/react';
import { LoginForm } from './components/auth/LoginForm';
import { RegisterForm } from './components/auth/RegisterForm';
import { Layout } from './components/common/Layout';
import { useAuth } from './contexts/AuthContext';

function App() {
  const { token } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  // If user is authenticated, show the main dashboard
  if (token) {
    return (
      <Layout>
        <Container maxW="4xl">
          <VStack gap={8}>
            <Box textAlign="center">
              <Heading size="xl" mb={2} color="blue.600">
                Welcome to AutomateOS
              </Heading>
              <Text color="gray.600">
                Your workflows will appear here once you create them.
              </Text>
            </Box>

            <Box p={6} bg="white" borderRadius="lg" borderWidth="1px" w="full">
              <Text fontSize="lg" fontWeight="medium" mb={4}>
                Dashboard
              </Text>
              <Text color="gray.600">
                This is where your workflow management interface will be implemented.
                The authentication system is now working and your token is stored securely.
              </Text>
            </Box>
          </VStack>
        </Container>
      </Layout>
    );
  }

  // If user is not authenticated, show login/register forms
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
}

export default App;