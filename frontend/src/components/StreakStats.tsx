'use client';

import React from 'react';
import { StreakStats as StreakStatsType } from '../types';
import {
    Box,
    Heading,
    SimpleGrid,
    Stat,
    StatLabel,
    StatNumber,
    StatHelpText,
    Card,
    CardBody,
    Alert,
    AlertIcon,
    Text,
    Badge,
    VStack,
    HStack,
    Progress,
    Tooltip,
} from '@chakra-ui/react';

interface StreakStatsProps {
    stats: StreakStatsType;
}

const StreakStats: React.FC<StreakStatsProps> = ({ stats }) => {
    if (!stats) return null;

    const getStreakLabel = (type: string | null) => {
        switch (type) {
            case 'W': return 'Victorias';
            case 'D': return 'Empates';
            case 'L': return 'Derrotas';
            default: return 'Sin Racha';
        }
    };

    const getStreakColor = (type: string | null) => {
        switch (type) {
            case 'W': return 'green';
            case 'D': return 'gray';
            case 'L': return 'red';
            default: return 'gray';
        }
    };

    return (
        <Card mt={6} boxShadow="md">
            <CardBody>
                <Heading size="md" mb={4}>Patrones de Rachas</Heading>

                <Alert status="warning" mb={6} borderRadius="md">
                    <AlertIcon />
                    <Text fontSize="sm">
                        Advertencia: El tamaño de la muestra es limitado (Mundiales 2014 y 2018).
                        Las probabilidades pueden no ser estadísticamente significativas.
                    </Text>
                </Alert>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8} mb={8}>
                    {/* Rachas Actuales y Más Largas */}
                    <Box>
                        <Heading size="sm" mb={4} color="gray.600">Rachas</Heading>
                        <VStack align="stretch" spacing={4}>
                            <Box p={4} bg="gray.50" borderRadius="md" borderWidth="1px">
                                <Text fontSize="sm" color="gray.500" mb={1}>Racha Actual</Text>
                                <HStack>
                                    <Badge colorScheme={getStreakColor(stats.current_streak.type)} fontSize="xl" px={2} borderRadius="md">
                                        {stats.current_streak.type || '-'}
                                    </Badge>
                                    <Text fontWeight="bold" fontSize="xl">{stats.current_streak.count} partidos</Text>
                                </HStack>
                            </Box>

                            <SimpleGrid columns={2} spacing={4}>
                                <Stat>
                                    <StatLabel>Máx Victorias</StatLabel>
                                    <StatNumber color="green.500">{stats.longest_streaks.W}</StatNumber>
                                </Stat>
                                <Stat>
                                    <StatLabel>Máx Invicto</StatLabel>
                                    <StatNumber color="blue.500">{stats.longest_streaks.Unbeaten}</StatNumber>
                                </Stat>
                                <Stat>
                                    <StatLabel>Máx Derrotas</StatLabel>
                                    <StatNumber color="red.500">{stats.longest_streaks.L}</StatNumber>
                                </Stat>
                                <Stat>
                                    <StatLabel>Máx Empates</StatLabel>
                                    <StatNumber color="gray.500">{stats.longest_streaks.D}</StatNumber>
                                </Stat>
                            </SimpleGrid>
                        </VStack>
                    </Box>

                    {/* Probabilidades de Transición */}
                    <Box>
                        <Heading size="sm" mb={4} color="gray.600">¿Qué pasa después de...?</Heading>
                        <VStack align="stretch" spacing={5}>
                            {['W', 'D', 'L'].map((prevRes) => {
                                const trans = stats.transitions[prevRes];
                                if (!trans || trans.sample_size === 0) return null;

                                const label = prevRes === 'W' ? 'una Victoria' : prevRes === 'D' ? 'un Empate' : 'una Derrota';
                                const color = prevRes === 'W' ? 'green.500' : prevRes === 'D' ? 'gray.500' : 'red.500';

                                return (
                                    <Box key={prevRes}>
                                        <Text fontSize="sm" fontWeight="bold" mb={2} color={color}>Después de {label} (n={trans.sample_size})</Text>
                                        <HStack spacing={1} h="20px" borderRadius="full" overflow="hidden">
                                            {trans.W > 0 && (
                                                <Tooltip label={`Gana: ${(trans.W * 100).toFixed(0)}%`}>
                                                    <Box w={`${trans.W * 100}%`} h="100%" bg="green.400" />
                                                </Tooltip>
                                            )}
                                            {trans.D > 0 && (
                                                <Tooltip label={`Empata: ${(trans.D * 100).toFixed(0)}%`}>
                                                    <Box w={`${trans.D * 100}%`} h="100%" bg="gray.400" />
                                                </Tooltip>
                                            )}
                                            {trans.L > 0 && (
                                                <Tooltip label={`Pierde: ${(trans.L * 100).toFixed(0)}%`}>
                                                    <Box w={`${trans.L * 100}%`} h="100%" bg="red.400" />
                                                </Tooltip>
                                            )}
                                        </HStack>
                                        <HStack justify="space-between" fontSize="xs" color="gray.500" mt={1}>
                                            <Text>Gana: {(trans.W * 100).toFixed(0)}%</Text>
                                            <Text>Empata: {(trans.D * 100).toFixed(0)}%</Text>
                                            <Text>Pierde: {(trans.L * 100).toFixed(0)}%</Text>
                                        </HStack>
                                    </Box>
                                );
                            })}
                        </VStack>
                    </Box>
                </SimpleGrid>
            </CardBody>
        </Card>
    );
};

export default StreakStats;
