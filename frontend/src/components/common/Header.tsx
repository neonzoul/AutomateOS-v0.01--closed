import { Box, Flex, Heading, Button, Text, Spacer } from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';

export const Header = () => {
    const { token, logout } = useAuth();

    return (
        <Box bg="white" px={4} py={3} borderBottomWidth="1px" borderColor="gray.200">
            <Flex alignItems="center">
                <Heading size="md" color="blue.600">
                    AutomateOS
                </Heading>
                <Spacer />
                {token ? (
                    <Flex alignItems="center" gap={4}>
                        <Text color="gray.600" fontSize="sm">
                            Welcome back!
                        </Text>
                        <Button size="sm" variant="outline" onClick={logout}>
                            Logout
                        </Button>
                    </Flex>
                ) : (
                    <Text color="gray.600" fontSize="sm">
                        Please log in
                    </Text>
                )}
            </Flex>
        </Box>
    );
};