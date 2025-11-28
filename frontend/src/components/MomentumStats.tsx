'use client';

import React from 'react';
import { MomentumStats as MomentumStatsType } from '../types';
import {
    Box,
    Heading,
    Stat,
    StatLabel,
    StatNumber,
    StatHelpText,
    Card,
    CardBody,
    Text,
    VStack,
    HStack,
    Badge,
    Tooltip,
} from '@chakra-ui/react';

interface MomentumStatsProps {
    stats: MomentumStatsType;
}

const MomentumStats: React.FC<MomentumStatsProps> = ({ stats }) => {
    if (!stats) return null;

    // Normalizar momentum para color (0-3)
    const getMomentumColor = (score: number) => {
        if (score >= 2.0) return 'green.500';
        if (score >= 1.0) return 'yellow.500';
        return 'red.500';
    };

    const getResultColor = (result: string) => {
        switch (result) {
            case 'W': return 'green';
            case 'D': return 'gray';
            case 'L': return 'red';
            default: return 'gray';
        }
    };

    return (
        <Card mt={6} boxShadow="md">
            <CardBody>
                <Heading size="md" mb={4}>Momentum (EMA)</Heading>
                <Text fontSize="sm" color="gray.500" mb={4}>
                    Media Móvil Exponencial de los puntos obtenidos en los últimos partidos.
                </Text>

                <Stat mb={6}>
                    <StatLabel>Score Actual</StatLabel>
                    <StatNumber color={getMomentumColor(stats.current_momentum)}>
                        {stats.current_momentum.toFixed(2)}
                    </StatNumber>
                    <StatHelpText>Escala 0-3 (3 = Racha perfecta)</StatHelpText>
                </Stat>

                <Box>
                    <Heading size="sm" mb={3} color="gray.600">Evolución Reciente</Heading>
                    <VStack align="stretch" spacing={2}>
                        {stats.history.slice().reverse().map((match, index) => (
                            <HStack key={index} justify="space-between" p={2} bg="gray.50" borderRadius="md">
                                <HStack>
                                    <Badge colorScheme={getResultColor(match.result)} w="20px" textAlign="center">
                                        {match.result}
                                    </Badge>
                                    <Text fontSize="sm">vs {match.opponent}</Text>
                                </HStack>
                                <HStack>
                                    <Text fontSize="xs" color="gray.400">{match.year}</Text>
                                    <Tooltip label={`Momentum después del partido: ${match.momentum_score.toFixed(2)}`}>
                                        <Badge variant="outline" colorScheme={match.momentum_score >= 1.5 ? 'green' : 'gray'}>
                                            {match.momentum_score.toFixed(2)}
                                        </Badge>
                                    </Tooltip>
                                </HStack>
                            </HStack>
                        ))}
                    </VStack>
                </Box>
            </CardBody>
        </Card>
    );
};

export default MomentumStats;
