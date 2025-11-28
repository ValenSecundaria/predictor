'use client';

import React from 'react';
import { GraphStats as GraphStatsType } from '../types';
import {
    Box,
    Heading,
    Card,
    CardBody,
    Text,
    VStack,
    HStack,
    Badge,
    Icon,
    List,
    ListItem,
    ListIcon,
} from '@chakra-ui/react';
import { CheckCircleIcon, ArrowForwardIcon } from '@chakra-ui/icons';

interface GraphStatsProps {
    stats: GraphStatsType;
}

const GraphStats: React.FC<GraphStatsProps> = ({ stats }) => {
    if (!stats) return null;

    return (
        <Card mt={6} boxShadow="md">
            <CardBody>
                <Heading size="md" mb={2}>Análisis de Grafos: Dominancia Indirecta</Heading>
                <Text fontSize="sm" color="gray.500" mb={4}>
                    Equipos a los que no necesariamente ganaste directamente, pero venciste a alguien que sí lo hizo (Transitividad: A &gt; B &gt; C).
                </Text>

                {stats.total_indirect_wins === 0 ? (
                    <Text color="gray.500" fontStyle="italic">No se encontraron relaciones indirectas de segundo grado.</Text>
                ) : (
                    <VStack align="stretch" spacing={3} maxH="300px" overflowY="auto">
                        {stats.indirect_wins.map((relation, index) => (
                            <Box key={index} p={3} bg="gray.50" borderRadius="md" borderWidth="1px">
                                <HStack spacing={2} align="center">
                                    <Badge colorScheme="green">TÚ</Badge>
                                    <Icon as={ArrowForwardIcon} color="gray.400" />
                                    <Badge colorScheme="blue">{relation.intermediate_team}</Badge>
                                    <Icon as={ArrowForwardIcon} color="gray.400" />
                                    <Badge colorScheme="red">{relation.indirect_victim}</Badge>
                                </HStack>
                                <Text fontSize="xs" color="gray.500" mt={1}>
                                    Ganaste a {relation.intermediate_team}, quien ganó a {relation.indirect_victim}.
                                </Text>
                            </Box>
                        ))}
                    </VStack>
                )}
            </CardBody>
        </Card>
    );
};

export default GraphStats;
