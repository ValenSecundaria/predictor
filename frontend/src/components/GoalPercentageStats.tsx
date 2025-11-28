'use client';

import React from 'react';
import { GoalPercentageStats as GoalPercentageStatsType } from '../types';
import {
    Card,
    CardBody,
    Heading,
    Text,
    Stat,
    StatLabel,
    StatNumber,
    StatHelpText,
    Alert,
    AlertIcon,
} from '@chakra-ui/react';

interface GoalPercentageStatsProps {
    stats: GoalPercentageStatsType;
}

const GoalPercentageStats: React.FC<GoalPercentageStatsProps> = ({ stats }) => {
    if (!stats) return null;

    return (
        <Card mt={6} boxShadow="md">
            <CardBody>
                <Heading size="md" mb={4}>Porcentaje de Goles</Heading>

                {!stats.available ? (
                    <Alert status="info" borderRadius="md">
                        <AlertIcon />
                        {stats.message || "Datos no disponibles."}
                    </Alert>
                ) : (
                    <Stat>
                        <StatLabel>Promedio de Goles por Partido</StatLabel>
                        <StatNumber fontSize="3xl">{stats.goals_per_match}</StatNumber>
                        <StatHelpText>
                            {stats.total_goals} goles en {stats.matches_played} partidos
                        </StatHelpText>
                        <Text fontSize="xs" color="gray.500" mt={2}>
                            {stats.message}
                        </Text>
                    </Stat>
                )}
            </CardBody>
        </Card>
    );
};

export default GoalPercentageStats;
