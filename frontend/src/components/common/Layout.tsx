import type { ReactNode } from 'react';
import { Box, Container } from '@chakra-ui/react';
import { Header } from './Header';

interface LayoutProps {
    children: ReactNode;
    maxWidth?: string;
}

export const Layout = ({ children, maxWidth = "1200px" }: LayoutProps) => {
    return (
        <Box minHeight="100vh" bg="gray.50">
            <Header />
            <Container
                maxW={maxWidth}
                py={{ base: 4, md: 8 }}
                px={{ base: 4, md: 6 }}
            >
                {children}
            </Container>
        </Box>
    );
};