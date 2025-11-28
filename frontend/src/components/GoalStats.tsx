'use client';

import React from 'react';
import { GoalStats as GoalStatsType } from '../types';
import {
    Box,
    Heading,
    SimpleGrid,
    Stat,
    StatLabel,
    StatNumber,
    StatHelpText,
    StatArrow,
    Card,
    CardBody,
    Tabs,
    TabList,
    TabPanels,
    Tab,
    TabPanel,
    Table,
    Thead,
    Tbody,
    Tr,
    Th,
    Td,
    TableContainer,
} from '@chakra-ui/react';

interface GoalStatsProps {
    stats: GoalStatsType;
}

const GoalStats: React.FC<GoalStatsProps> = ({ stats }) => {
    if (!stats) return null;

    return (
        <Card mt={6} boxShadow="md">
            <CardBody>
                <Heading size="md" mb={4}>Estadísticas de Goles</Heading>

                <Tabs variant="enclosed" colorScheme="teal">
                    <TabList>
                        <Tab>Global</Tab>
                        <Tab>Por Competición</Tab>
                    </TabList>

                    <TabPanels>
                        <TabPanel>
                            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={5}>
                                <Stat>
                                    <StatLabel>Goles a Favor (Total)</StatLabel>
                                    <StatNumber color="green.500">{stats.global.goals_for}</StatNumber>
                                    <StatHelpText>Promedio: {stats.global.avg_goals_for}</StatHelpText>
                                </Stat>
                                <Stat>
                                    <StatLabel>Goles en Contra (Total)</StatLabel>
                                    <StatNumber color="red.500">{stats.global.goals_against}</StatNumber>
                                    <StatHelpText>Promedio: {stats.global.avg_goals_against}</StatHelpText>
                                </Stat>
                                <Stat>
                                    <StatLabel>Diferencia de Goles</StatLabel>
                                    <StatNumber>
                                        <StatArrow type={stats.global.goal_difference >= 0 ? 'increase' : 'decrease'} />
                                        {stats.global.goal_difference}
                                    </StatNumber>
                                </Stat>
                            </SimpleGrid>
                        </TabPanel>

                        <TabPanel>
                            <TableContainer>
                                <Table variant="simple" size="sm">
                                    <Thead>
                                        <Tr>
                                            <Th>Competición</Th>
                                            <Th isNumeric>PJ</Th>
                                            <Th isNumeric>GF</Th>
                                            <Th isNumeric>GC</Th>
                                            <Th isNumeric>Dif</Th>
                                            <Th isNumeric>Prom GF</Th>
                                            <Th isNumeric>Prom GC</Th>
                                        </Tr>
                                    </Thead>
                                    <Tbody>
                                        {Object.entries(stats.by_competition).map(([comp, data]) => (
                                            <Tr key={comp}>
                                                <Td fontWeight="medium">{comp}</Td>
                                                <Td isNumeric>{data.matches_played}</Td>
                                                <Td isNumeric color="green.600">{data.goals_for}</Td>
                                                <Td isNumeric color="red.600">{data.goals_against}</Td>
                                                <Td isNumeric fontWeight="bold">
                                                    {data.goal_difference > 0 ? `+${data.goal_difference}` : data.goal_difference}
                                                </Td>
                                                <Td isNumeric>{data.avg_goals_for}</Td>
                                                <Td isNumeric>{data.avg_goals_against}</Td>
                                            </Tr>
                                        ))}
                                    </Tbody>
                                </Table>
                            </TableContainer>
                        </TabPanel>
                    </TabPanels>
                </Tabs>
            </CardBody>
        </Card>
    );
};

export default GoalStats;
