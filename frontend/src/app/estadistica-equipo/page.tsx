'use client';

import { useState, useEffect } from 'react';
import {
  ChakraProvider,
  Container,
  Heading,
  Button,
  Box,
  Spinner,
  Alert,
  AlertIcon,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  SimpleGrid,
  Flex,
  Select,
  VStack,
  HStack,
} from '@chakra-ui/react';
import Link from 'next/link';
import GoalStats from '../../components/GoalStats';
import StreakStats from '../../components/StreakStats';
import HomeAwayStats from '../../components/HomeAwayStats';
import MomentumStats from '../../components/MomentumStats';
import GraphStats from '../../components/GraphStats';
import GoalPercentageStats from '../../components/GoalPercentageStats';
import EffectivenessStats from '../../components/EffectivenessStats';
import PossessionStats from '../../components/PossessionStats';

import {
  GoalStats as GoalStatsType,
  StreakStats as StreakStatsType,
  HomeAwayStats as HomeAwayStatsType,
  MomentumStats as MomentumStatsType,
  GraphStats as GraphStatsType,
  GoalPercentageStats as GoalPercentageStatsType,
  EffectivenessStats as EffectivenessStatsType,
  PossessionStats as PossessionStatsType
} from '../../types';

// Tipos de datos que vienen de la API
type Team = {
  name: string;
  code: string;
};

type TeamStats = {
  wins: number;
  losses: number;
  draws: number;
  total_matches: number;
  win_percentage: number;
  loss_percentage: number;
  draw_percentage: number;
  goals_for: number;
  goals_against: number;
};

export default function EstadisticaEquipoPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [stats, setStats] = useState<TeamStats | null>(null);
  const [goalStats, setGoalStats] = useState<GoalStatsType | null>(null);
  const [streakStats, setStreakStats] = useState<StreakStatsType | null>(null);
  const [homeAwayStats, setHomeAwayStats] = useState<HomeAwayStatsType | null>(null);
  const [momentumStats, setMomentumStats] = useState<MomentumStatsType | null>(null);
  const [graphStats, setGraphStats] = useState<GraphStatsType | null>(null);
  const [goalPercentageStats, setGoalPercentageStats] = useState<GoalPercentageStatsType | null>(null);
  const [effectivenessStats, setEffectivenessStats] = useState<EffectivenessStatsType | null>(null);
  const [possessionStats, setPossessionStats] = useState<PossessionStatsType | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 1. Cargar la lista de equipos cuando el componente se monta
  useEffect(() => {
    const fetchTeams = async () => {
      setLoading(true);
      try {
        const res = await fetch('/api/v1/teams');
        if (!res.ok) throw new Error(`Error al obtener equipos: HTTP ${res.status}`);
        const teamsData: Team[] = await res.json();
        setTeams(teamsData);
      } catch (e: any) {
        setError(e?.message ?? 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };
    fetchTeams();
  }, []);

  // 2. Cargar las estadísticas cuando se selecciona un equipo
  useEffect(() => {
    if (!selectedTeam) {
      setStats(null);
      setGoalStats(null);
      setStreakStats(null);
      setHomeAwayStats(null);
      setMomentumStats(null);
      setGraphStats(null);
      setGoalPercentageStats(null);
      setEffectivenessStats(null);
      setPossessionStats(null);
      return;
    }

    const fetchStatsByTeam = async () => {
      setError(null);
      setLoading(true);
      try {
        // Fetch existing stats
        const resStats = await fetch(`/api/v1/stats/${selectedTeam}`, { cache: 'no-store' });
        if (!resStats.ok) throw new Error(`Error al obtener estadísticas generales: HTTP ${resStats.status}`);
        const statsData: TeamStats = await resStats.json();
        setStats(statsData);

        // Fetch new goal stats
        const resGoalStats = await fetch(`/api/v1/predict/stats/goals/${selectedTeam}`, { cache: 'no-store' });
        if (resGoalStats.ok) setGoalStats(await resGoalStats.json());

        // Fetch new streak stats
        const resStreakStats = await fetch(`/api/v1/predict/stats/streaks/${selectedTeam}`, { cache: 'no-store' });
        if (resStreakStats.ok) setStreakStats(await resStreakStats.json());

        // Fetch new home/away stats
        const resHomeAwayStats = await fetch(`/api/v1/predict/stats/home-away/${selectedTeam}`, { cache: 'no-store' });
        if (resHomeAwayStats.ok) setHomeAwayStats(await resHomeAwayStats.json());

        // Fetch new momentum stats
        const resMomentumStats = await fetch(`/api/v1/predict/stats/momentum/${selectedTeam}`, { cache: 'no-store' });
        if (resMomentumStats.ok) setMomentumStats(await resMomentumStats.json());

        // Fetch new graph stats
        const resGraphStats = await fetch(`/api/v1/predict/stats/graph/${selectedTeam}`, { cache: 'no-store' });
        if (resGraphStats.ok) setGraphStats(await resGraphStats.json());

        // Fetch future features
        const resGoalPercentage = await fetch(`/api/v1/predict/stats/goal-percentage/${selectedTeam}`, { cache: 'no-store' });
        if (resGoalPercentage.ok) setGoalPercentageStats(await resGoalPercentage.json());

        const resEffectiveness = await fetch(`/api/v1/predict/stats/effectiveness/${selectedTeam}`, { cache: 'no-store' });
        if (resEffectiveness.ok) setEffectivenessStats(await resEffectiveness.json());

        const resPossession = await fetch(`/api/v1/predict/stats/possession/${selectedTeam}`, { cache: 'no-store' });
        if (resPossession.ok) setPossessionStats(await resPossession.json());

      } catch (e: any) {
        setError(e?.message ?? 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    fetchStatsByTeam();
  }, [selectedTeam]);

  return (
    <ChakraProvider>
      <Container maxW="container.lg" py={10}>
        <VStack spacing={6} align="stretch">
          <HStack justify="space-between">
            <Heading as="h1" size="lg">
              Estadísticas por Equipo
            </Heading>
            <Link href="/">
              <Button variant="outline">Volver al Menú</Button>
            </Link>
          </HStack>

          <Box>
            <Text mb={2} fontWeight="semibold">Selecciona un equipo para ver su rendimiento histórico:</Text>
            <Select
              placeholder="Selecciona un equipo"
              value={selectedTeam}
              onChange={(e) => setSelectedTeam(e.target.value)}
              isDisabled={teams.length === 0 || loading}
            >
              {teams.map((team) => (
                <option key={team.code} value={team.code}>
                  {team.name}
                </option>
              ))}
            </Select>
          </Box>

          {loading && (
            <Box textAlign="center" p={5}>
              <Spinner size="xl" />
              <Text mt={2}>Cargando datos...</Text>
            </Box>
          )}

          {error && (
            <Alert status="error">
              <AlertIcon />
              {error}
            </Alert>
          )}

          {stats && !loading && (
            <Box borderWidth="1px" borderRadius="lg" p={6} bg="gray.50" boxShadow="md">
              <Heading as="h3" size="lg" mb={6} textAlign="center" color="gray.700">
                Rendimiento Histórico
              </Heading>

              <SimpleGrid columns={{ base: 2, md: 3, lg: 5 }} spacing={5}>
                <StatCard color="green.500" label="Victorias" value={stats.wins} />
                <StatCard color="red.500" label="Derrotas" value={stats.losses} />
                <StatCard color="gray.500" label="Empates" value={stats.draws} />
                <StatCard color="blue.500" label="Goles a Favor" value={stats.goals_for} />
                <StatCard color="orange.500" label="Goles en Contra" value={stats.goals_against} />
              </SimpleGrid>
            </Box>
          )}

          {goalStats && !loading && <GoalStats stats={goalStats} />}
          {homeAwayStats && !loading && <HomeAwayStats stats={homeAwayStats} />}
          {streakStats && !loading && <StreakStats stats={streakStats} />}
          {momentumStats && !loading && <MomentumStats stats={momentumStats} />}
          {graphStats && !loading && <GraphStats stats={graphStats} />}

          {/* Future Features */}
          {goalPercentageStats && !loading && <GoalPercentageStats stats={goalPercentageStats} />}
          {effectivenessStats && !loading && <EffectivenessStats stats={effectivenessStats} />}
          {possessionStats && !loading && <PossessionStats stats={possessionStats} />}

        </VStack>
      </Container>
    </ChakraProvider>
  );
}

// Componente reutilizable para las tarjetas de estadísticas
const StatCard = ({ color, label, value }: { color: string, label: string, value: number | string }) => (
  <Stat
    p={4}
    borderWidth="1px"
    borderColor="gray.200"
    borderRadius="lg"
    bg="white"
    boxShadow="sm"
    textAlign="center"
    _hover={{ transform: 'translateY(-5px)', boxShadow: 'lg', transition: 'all 0.2s' }}
  >
    <Flex justify="center" align="center" direction="column">
      <StatLabel fontSize="md" color="gray.600">{label}</StatLabel>
      <StatNumber fontSize="2xl" fontWeight="bold" color={color}>{value}</StatNumber>
    </Flex>
  </Stat>
);
