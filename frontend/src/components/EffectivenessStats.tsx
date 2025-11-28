'use client';

import React from 'react';
import { EffectivenessStats as EffectivenessStatsType } from '../types';
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

interface EffectivenessStatsProps {
    stats: EffectivenessStatsType;
}

const EffectivenessStats: React.FC<EffectivenessStatsProps> = ({ stats }) => {
    if (!stats) return null;

    return (
        <Card mt={6} boxShadow="md">
            <CardBody>
                <Heading size="md" mb={4}>Efectividad (Goles / Tiros)</Heading>

                {!stats.available ? (
                    <Alert status="warning" borderRadius="md">
                        <AlertIcon />
                        {stats.message || "Datos no disponibles."}
                    </Alert>
                ) : (
                    <Stat>
                        <StatLabel>Efectividad de Tiro</StatLabel>
                        <StatNumber>{stats.effectiveness_percentage}%</StatNumber>
                    </Stat>
                )}
            </CardBody>
        </Card>
    );
};

export default EffectivenessStats;
