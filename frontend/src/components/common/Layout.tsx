import type { ReactNode } from 'react';
import { Box } from '@chakra-ui/react';
import { Header } from './Header';

interface LayoutProps {
    children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
    return (
        <Box minHeight="100vh" bg="gray.50">
            <Header />
            <Box py={8}>
                {children}
            </Box>
        </Box>
    );
};