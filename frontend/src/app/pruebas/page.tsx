"use client";

import { useState, useEffect } from 'react';
import {
  ChakraProvider, Container, Heading, Button, Box, Spinner, Alert, AlertIcon,
  Progress, Stat, StatLabel, StatNumber, StatGroup,
  Select, Table, Thead, Tbody, Tr, Th, Td, TableContainer, VStack, HStack
} from '@chakra-ui/react';
import Link from 'next/link';

type Goal = {
  player: string;
  minute: number;
};

// Nuevo tipo para los equipos que vendrán del API
type Team = {
  name: string;
  code: string;
};

// Actualizamos el tipo Match para incluir los códigos de equipo, que son necesarios para el filtrado
type Match = {
  team_a: string;
  team_b: string;
  team_a_code: string;
  team_b_code: string;
  score_a: number;
  score_b: number;
  goals: Goal[];
};

// Nuevo tipo para las estadísticas que vendrán del API
type TeamStats = {
  wins: number;
  losses: number;
  draws: number;
  total_matches: number;
  win_percentage: number;
  loss_percentage: number;
  draw_percentage: number;
};

export default function PruebasPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [data, setData] = useState<Match[] | null>(null);
  const [stats, setStats] = useState<TeamStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(false);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const consultar = async () => {
    try {
      setErr(null);
      setLoading(true);
      const res = await fetch('/api/v1/analisis', { cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as Match[]; // Esto es para el botón de "ver JSON"
      setData(json);
    } catch (e: any) {
      setErr(e?.message ?? 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const consultarEstadisticas = async () => {
    if (!selectedTeam) return;
    try {
      setErr(null);
      setLoadingStats(true);
      const res = await fetch(`/api/v1/stats/${selectedTeam}`, { cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status} al obtener estadísticas`);
      const statsData = (await res.json()) as TeamStats;
      setStats(statsData);
    } catch (e: any) {
      setErr(e?.message ?? 'Error desconocido');
    } finally {
      setLoadingStats(false);
    }
  };


  // --- NUEVA LÓGICA ---

  // 1. Cargar la lista de equipos cuando el componente se monta
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const res = await fetch('/api/v1/teams');
        if (!res.ok) throw new Error(`HTTP ${res.status} al obtener equipos`);
        const teamsData = (await res.json()) as Team[];
        setTeams(teamsData);
      } catch (e: any) {
        setErr(e?.message ?? 'Error desconocido');
      }
    };
    fetchTeams();
  }, []); // El array vacío asegura que esto se ejecute solo una vez

  // 2. Cargar los partidos del equipo seleccionado cada vez que cambie
  useEffect(() => {
    if (!selectedTeam) {
      setData(null); // Limpiamos los datos si no hay equipo seleccionado
      setStats(null); // Limpiamos las estadísticas también
      return;
    }

    const fetchMatchesByTeam = async () => {
      try {
        setErr(null);
        setLoading(true);
        const res = await fetch(`/api/v1/analisis/${selectedTeam}`, { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as Match[];
        setData(json);
      } catch (e: any) {
        setErr(e?.message ?? 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    fetchMatchesByTeam();
  }, [selectedTeam]); // Este efecto se ejecuta cada vez que `selectedTeam` cambia

  return (
    <ChakraProvider>
      <Container maxW="container.lg" className="pt-4">
        <Heading as="h1" size="lg" mb={4}>
          ⚽ Modo Pruebas: FastAPI + Next (Chakra + Bootstrap)
        </Heading>

        <VStack spacing={4} align="stretch">
          <HStack spacing={4}>
            <Link href="/" passHref>
              <Button as="a">Volver</Button>
            </Link>
            <Button colorScheme="blue" onClick={consultar} isDisabled={loading}>
              Ver JSON Completo
            </Button>
          </HStack>

          {/* --- NUEVO COMPONENTE: Selector de Equipo --- */}
          <Box>
            <Heading as="h2" size="md" mb={2}>Filtrar por equipo</Heading>
            <Select
              placeholder="Selecciona un equipo"
              value={selectedTeam}
              onChange={(e) => setSelectedTeam(e.target.value)}
              isDisabled={teams.length === 0}
            >
              {teams.map((team) => (
                <option key={team.code} value={team.code}>
                  {team.name}
                </option>
              ))}
            </Select>
          </Box>

          {/* --- NUEVO COMPONENTE: Botón y Display de Estadísticas --- */}
          {selectedTeam && (
            <Box>
              <Button colorScheme="green" onClick={consultarEstadisticas} isDisabled={loadingStats || !selectedTeam} isLoading={loadingStats}>
                Calcular Estadísticas
              </Button>
            </Box>
          )}


          {loading && (
            <Box mb={3}>
              <Spinner mr={2} /> Cargando datos...
            </Box>
          )}

          {err && (
            <Alert status="error" mb={3}>
              <AlertIcon />
              {err}
            </Alert>
          )}

          {stats && (
            <Box borderWidth="1px" borderRadius="lg" p={4}>
              <Heading as="h3" size="md" mb={4}>Estadísticas</Heading>
              <StatGroup mb={4}>
                <Stat>
                  <StatLabel>Victorias</StatLabel>
                  <StatNumber>{stats.wins}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Derrotas</StatLabel>
                  <StatNumber>{stats.losses}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Empates</StatLabel>
                  <StatNumber>{stats.draws}</StatNumber>
                </Stat>
              </StatGroup>
              <Box>
                <Progress value={stats.win_percentage} colorScheme="green" size="lg" hasStripe isAnimated />
                <Progress value={stats.loss_percentage} colorScheme="red" size="lg" hasStripe isAnimated mt={2} />
              </Box>
            </Box>
          )}

          {/* --- NUEVO COMPONENTE: Tabla de Resultados --- */}
          {data && data.length > 0 && !('wins' in data[0]) && ( // Condición para no mostrar la tabla si data es el JSON completo
            <Box borderWidth="1px" borderRadius="lg" p={4}>
              <Heading as="h2" size="md" mb={4}>
                Resultados
              </Heading>
              <TableContainer>
                <Table variant="striped" colorScheme="gray">
                  <Thead>
                    <Tr>
                      <Th>Equipo Local</Th>
                      <Th>Equipo Visitante</Th>
                      <Th isNumeric>Resultado</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {data.map((match, index) => (
                      <Tr key={index}>
                        <Td>{match.team_a}</Td>
                        <Td>{match.team_b}</Td>
                        <Td isNumeric>{`${match.score_a} - ${match.score_b}`}</Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </VStack>
      </Container>
    </ChakraProvider>
  );
}
