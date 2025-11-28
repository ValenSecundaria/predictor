'use client';

import React from 'react';
import { HeadToHeadStats } from '../types';
import { Box, Text, VStack, HStack, Badge, Card, CardBody, Heading, Divider } from '@chakra-ui/react';

interface HistoryStatsProps {
    stats: HeadToHeadStats;
    teamAName: string;
    teamBName: string;
}

const HistoryStats: React.FC<HistoryStatsProps> = ({ stats, teamAName, teamBName }) => {
    if (!stats || stats.total_matches === 0) {
        return (
            <Box p={4} borderWidth="1px" borderRadius="lg" bg="gray.50">
                <Text>No hay historial registrado entre estos equipos.</Text>
            </Box>
        );
    }

    return (
        <Card variant="outline" mt={6} boxShadow="sm">
            <CardBody>
                <Heading size="md" mb={4}>Historial entre ellos</Heading>

                <HStack spacing={8} justify="center" mb={6}>
                    <VStack>
                        <Text fontWeight="bold" fontSize="2xl" color="blue.500">{stats.wins_a}</Text>
                        <Text fontSize="sm" color="gray.600">Victorias {teamAName}</Text>
                    </VStack>
                    <VStack>
                        <Text fontWeight="bold" fontSize="2xl" color="gray.500">{stats.draws}</Text>
                        <Text fontSize="sm" color="gray.600">Empates</Text>
                    </VStack>
                    <VStack>
                        <Text fontWeight="bold" fontSize="2xl" color="red.500">{stats.wins_b}</Text>
                        <Text fontSize="sm" color="gray.600">Victorias {teamBName}</Text>
                    </VStack>
                </HStack>

                <Divider mb={4} />

                <Heading size="sm" mb={3}>Últimos enfrentamientos</Heading>
                <VStack align="stretch" spacing={2}>
                    {stats.recent_matches.map((match, index) => (
                        <Box key={index} p={2} bg="gray.50" borderRadius="md">
                            <HStack justify="space-between">
                                <Badge colorScheme="purple">{match.year}</Badge>
                                <Text fontWeight="bold">
                                    {match.team_a} {match.score_a} - {match.score_b} {match.team_b}
                                </Text>
                                <Badge variant="outline">{match.competition}</Badge>
                            </HStack>
                        </Box>
                    ))}
                </VStack>
            </CardBody>
        </Card>
    );
};

export default HistoryStats;
