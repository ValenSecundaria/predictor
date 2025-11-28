'use client';

import React from 'react';
import { HomeAwayStats as HomeAwayStatsType } from '../types';
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
    Text,
    VStack,
    HStack,
    Progress,
    Divider,
} from '@chakra-ui/react';

interface HomeAwayStatsProps {
    stats: HomeAwayStatsType;
}

const HomeAwayStats: React.FC<HomeAwayStatsProps> = ({ stats }) => {
    if (!stats) return null;

    const renderConditionStats = (title: string, data: any, colorScheme: string) => (
        <Box p={4} borderWidth="1px" borderRadius="lg" bg="white">
            <Heading size="sm" mb={4} color={`${colorScheme}.600`}>{title}</Heading>

            <SimpleGrid columns={2} spacing={4} mb={4}>
                <Stat size="sm">
                    <StatLabel>Partidos</StatLabel>
                    <StatNumber>{data.matches_played}</StatNumber>
                </Stat>
                <Stat size="sm">
                    <StatLabel>Win Rate</StatLabel>
                    <StatNumber>{data.win_percentage}%</StatNumber>
                </Stat>
            </SimpleGrid>

            <VStack align="stretch" spacing={3}>
                <Box>
                    <HStack justify="space-between" mb={1}>
                        <Text fontSize="xs">Victorias</Text>
                        <Text fontSize="xs" fontWeight="bold">{data.wins}</Text>
                    </HStack>
                    <Progress value={(data.wins / data.matches_played) * 100} size="sm" colorScheme="green" borderRadius="full" />
                </Box>
                <Box>
                    <HStack justify="space-between" mb={1}>
                        <Text fontSize="xs">Empates</Text>
                        <Text fontSize="xs" fontWeight="bold">{data.draws}</Text>
                    </HStack>
                    <Progress value={(data.draws / data.matches_played) * 100} size="sm" colorScheme="gray" borderRadius="full" />
                </Box>
                <Box>
                    <HStack justify="space-between" mb={1}>
                        <Text fontSize="xs">Derrotas</Text>
                        <Text fontSize="xs" fontWeight="bold">{data.losses}</Text>
                    </HStack>
                    <Progress value={(data.losses / data.matches_played) * 100} size="sm" colorScheme="red" borderRadius="full" />
                </Box>
            </VStack>

            <Divider my={4} />

            <SimpleGrid columns={2} spacing={2}>
                <Box>
                    <Text fontSize="xs" color="gray.500">Goles a Favor</Text>
                    <Text fontWeight="bold">{data.avg_goals_for} <Text as="span" fontSize="xs" fontWeight="normal">/ part</Text></Text>
                </Box>
                <Box>
                    <Text fontSize="xs" color="gray.500">Goles en Contra</Text>
                    <Text fontWeight="bold">{data.avg_goals_against} <Text as="span" fontSize="xs" fontWeight="normal">/ part</Text></Text>
                </Box>
            </SimpleGrid>
        </Box>
    );

    return (
        <Card mt={6} boxShadow="md" bg="gray.50">
            <CardBody>
                <Heading size="md" mb={2}>Rendimiento Local vs Visitante</Heading>
                <Text fontSize="sm" color="gray.500" mb={6}>
                    Nota: En torneos como el Mundial, la condición de "Local" o "Visitante" es administrativa.
                </Text>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                    {renderConditionStats("Como Local (Team A)", stats.home, "blue")}
                    {renderConditionStats("Como Visitante (Team B)", stats.away, "purple")}
                </SimpleGrid>
            </CardBody>
        </Card>
    );
};

export default HomeAwayStats;
