'use client';

import React from 'react';
import {
    Box,
    Heading,
    Text,
    Progress,
    VStack,
    HStack,
    Badge,
    Card,
    CardBody,
    Stat,
    StatLabel,
    StatNumber,
    StatHelpText,
    SimpleGrid,
    Icon,
} from '@chakra-ui/react';
import { FaChartLine, FaHistory, FaFutbol, FaFire } from 'react-icons/fa';

interface PredictionResultProps {
    prediction: {
        team_a: string;
        team_b: string;
        probability_a: number;
        probability_b: number;
        details: {
            h2h_score_a: number;
            h2h_score_b: number;
            momentum_score_a: number;
            momentum_score_b: number;
            goal_power_a: number;
            goal_power_b: number;
            streak_score_a: number;
            streak_score_b: number;
        };
    };
    teamAName: string;
    teamBName: string;
}

const PredictionResult: React.FC<PredictionResultProps> = ({ prediction, teamAName, teamBName }) => {
    const { probability_a, probability_b, details } = prediction;

    const winner = probability_a > probability_b ? teamAName : teamBName;
    const winnerProb = probability_a > probability_b ? probability_a : probability_b;
    const isDraw = Math.abs(probability_a - probability_b) < 1.0;

    return (
        <VStack spacing={6} align="stretch" mt={6}>
            <Card
                bgGradient="linear(to-r, blue.600, purple.600)"
                color="white"
                boxShadow="xl"
                borderRadius="xl"
                overflow="hidden"
            >
                <CardBody textAlign="center" py={8}>
                    <Text fontSize="sm" textTransform="uppercase" letterSpacing="wider" opacity={0.8} mb={2}>
                        Predicción del Partido
                    </Text>
                    <Heading size="2xl" mb={4}>
                        {isDraw ? "Empate Técnico" : `${winner} gana`}
                    </Heading>
                    <Text fontSize="xl" fontWeight="medium">
                        {isDraw
                            ? "Las probabilidades están muy igualadas."
                            : `con una probabilidad del ${winnerProb}%`}
                    </Text>
                </CardBody>
            </Card>

            <Card boxShadow="lg" borderRadius="xl">
                <CardBody>
                    <VStack spacing={6}>
                        <Box w="100%">
                            <HStack justify="space-between" mb={2}>
                                <Text fontWeight="bold" fontSize="lg">{teamAName}</Text>
                                <Text fontWeight="bold" fontSize="lg">{probability_a}%</Text>
                            </HStack>
                            <Progress
                                value={probability_a}
                                colorScheme="blue"
                                height="24px"
                                borderRadius="full"
                                hasStripe
                                isAnimated
                            />
                        </Box>

                        <Box w="100%">
                            <HStack justify="space-between" mb={2}>
                                <Text fontWeight="bold" fontSize="lg">{teamBName}</Text>
                                <Text fontWeight="bold" fontSize="lg">{probability_b}%</Text>
                            </HStack>
                            <Progress
                                value={probability_b}
                                colorScheme="purple"
                                height="24px"
                                borderRadius="full"
                                hasStripe
                                isAnimated
                            />
                        </Box>
                    </VStack>
                </CardBody>
            </Card>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <FactorCard
                    icon={FaHistory}
                    title="Historial Directo"
                    scoreA={details.h2h_score_a}
                    scoreB={details.h2h_score_b}
                    teamAName={teamAName}
                    teamBName={teamBName}
                />
                <FactorCard
                    icon={FaChartLine}
                    title="Momentum (Forma)"
                    scoreA={details.momentum_score_a}
                    scoreB={details.momentum_score_b}
                    teamAName={teamAName}
                    teamBName={teamBName}
                />
                <FactorCard
                    icon={FaFutbol}
                    title="Poder de Gol"
                    scoreA={details.goal_power_a}
                    scoreB={details.goal_power_b}
                    teamAName={teamAName}
                    teamBName={teamBName}
                />
                <FactorCard
                    icon={FaFire}
                    title="Racha Actual"
                    scoreA={details.streak_score_a}
                    scoreB={details.streak_score_b}
                    teamAName={teamAName}
                    teamBName={teamBName}
                />
            </SimpleGrid>
        </VStack>
    );
};

const FactorCard = ({ icon, title, scoreA, scoreB, teamAName, teamBName }: any) => {
    const total = scoreA + scoreB;
    const pctA = total === 0 ? 50 : (scoreA / total) * 100;
    const pctB = total === 0 ? 50 : (scoreB / total) * 100;

    return (
        <Card variant="outline" borderRadius="lg">
            <CardBody p={4}>
                <HStack mb={3}>
                    <Icon as={icon} color="blue.500" />
                    <Text fontWeight="bold">{title}</Text>
                </HStack>
                <HStack justify="space-between" fontSize="xs" mb={1}>
                    <Text>{teamAName}</Text>
                    <Text>{teamBName}</Text>
                </HStack>
                <Progress value={pctA} colorScheme="blue" size="sm" borderRadius="full" mb={2} />
                <HStack justify="space-between" fontSize="xs" color="gray.500">
                    <Text>{scoreA.toFixed(2)}</Text>
                    <Text>{scoreB.toFixed(2)}</Text>
                </HStack>
            </CardBody>
        </Card>
    );
};

export default PredictionResult;
