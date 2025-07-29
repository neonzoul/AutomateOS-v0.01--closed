import { Box, Flex, Heading, Button, Text, Spacer, HStack } from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';

export const Header = () => {
    const { token, logout } = useAuth();

    return (
        <Box bg="white" px={{ base: 4, md: 6 }} py={3} borderBottomWidth="1px" borderColor="gray.200">
            <Flex alignItems="center">
                <Heading size={{ base: "sm", md: "md" }} color="blue.600">
                    AutomateOS
                </Heading>
                <Spacer />
                {token ? (
                    <HStack gap={{ base: 2, md: 4 }}>
                        <Text
                            color="gray.600"
                            fontSize="sm"
                            display={{ base: "none", sm: "block" }}
                        >
                            Welcome back!
                        </Text>
                        <Button
                            size={{ base: "xs", md: "sm" }}
                            variant="outline"
                            onClick={logout}
                        >
                            Logout
                        </Button>
                    </HStack>
                ) : (
                    <Text
                        color="gray.600"
                        fontSize="sm"
                        display={{ base: "none", sm: "block" }}
                    >
                        Please log in
                    </Text>
                )}
            </Flex>
        </Box>
    );
};