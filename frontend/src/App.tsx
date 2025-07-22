import { Box, Heading, Text } from '@chakra-ui/react';
import { LoginForm } from './components/auth/LoginForm';

function App() {
  return (
    <Box minHeight="100vh" bg="gray.50" py={8}>
      <Box maxWidth="md" mx="auto">
        <Heading size="xl" textAlign="center" mb={2} color="blue.600">
          AutomateOS
        </Heading>
        <Text textAlign="center" color="gray.600" mb={8}>
          Your Personal Workflow Automation Platform
        </Text>

        <LoginForm />
      </Box>
    </Box>
  );
}

export default App
