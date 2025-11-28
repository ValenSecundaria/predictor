'use client';

import React from 'react';
import { PossessionStats as PossessionStatsType } from '../types';
import {
    Card,
    CardBody,
    Heading,
    Stat,
    StatLabel,
    StatNumber,
    Alert,
    AlertIcon,
} from '@chakra-ui/react';

interface PossessionStatsProps {
    stats: PossessionStatsType;
}

const PossessionStats: React.FC<PossessionStatsProps> = ({ stats }) => {
    if (!stats) return null;

    return (
        <Card mt={6} boxShadow="md">
            <CardBody>
                <Heading size="md" mb={4}>Posesión en 3/4 de Cancha</Heading>

                {!stats.available ? (
                    <Alert status="warning" borderRadius="md">
                        <AlertIcon />
                        {stats.message || "Datos no disponibles."}
                    </Alert>
                ) : (
                    <Stat>
                        <StatLabel>Posesión Promedio</StatLabel>
                        <StatNumber>{stats.possession_3rd_quarter_avg}%</StatNumber>
                    </Stat>
                )}
            </CardBody>
        </Card>
    );
};

export default PossessionStats;
