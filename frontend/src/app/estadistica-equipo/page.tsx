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
      return;
    }

    const fetchStatsByTeam = async () => {
      setError(null);
      setLoading(true);
      try {
        const res = await fetch(`/api/v1/stats/${selectedTeam}`, { cache: 'no-store' });
        if (!res.ok) throw new Error(`Error al obtener estadísticas: HTTP ${res.status}`);
        const statsData: TeamStats = await res.json();
        setStats(statsData);
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
