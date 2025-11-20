"use client";

import { useState, useEffect } from 'react';
import {
  ChakraProvider, Container, Heading, Button, Box, Spinner, Alert, AlertIcon, Text,
  Progress, Stat, StatLabel, StatNumber, StatGroup,
  Select, VStack, HStack
} from '@chakra-ui/react';
import Link from 'next/link';

// Tipo para los equipos que vienen de la API
type Team = {
  name: string;
  code: string;
};

// Tipo para las estadísticas que vienen de la API
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

const worldCupYears = [
  1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978,
  1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022
];

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [stats, setStats] = useState<TeamStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  // Estados para los nuevos filtros de año
  const [fromYear, setFromYear] = useState('');
  const [toYear, setToYear] = useState('');
  const [yearError, setYearError] = useState<string | null>(null);

  // 1. Cargar la lista de equipos cuando el componente se monta
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        setLoading(true);
        const res = await fetch('/api/v1/teams');
        if (!res.ok) throw new Error(`HTTP ${res.status} al obtener equipos`);
        const teamsData = (await res.json()) as Team[];
        setTeams(teamsData);
      } catch (e: any) {
        setErr(e?.message ?? 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };
    fetchTeams();
  }, []); 

  // 2. Cargar las estadísticas del equipo seleccionado cada vez que cambie
  useEffect(() => {
    if (!selectedTeam) {
      setStats(null);
      return;
    }

    const fetchStatsByTeam = async () => {
      try {
        setErr(null);
        setLoading(true);
        const res = await fetch(`/api/v1/stats/${selectedTeam}`, { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status} al obtener estadísticas`);
        const statsData = (await res.json()) as TeamStats;
        setStats(statsData);
      } catch (e: any) {
        setErr(e?.message ?? 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    fetchStatsByTeam();
  }, [selectedTeam]);

  // 3. Validar el rango de años cada vez que cambian
  useEffect(() => {
    if (fromYear && toYear && parseInt(fromYear) > parseInt(toYear)) {
      setYearError('El año "Desde" no puede ser mayor que el año "Hasta".');
    } else {
      setYearError(null);
    }
  }, [fromYear, toYear]);

  const handleApplyFilter = () => {
    // Lógica para aplicar el filtro (se implementará más adelante)
    console.log(`Aplicando filtro de años: Desde ${fromYear} hasta ${toYear}`);
  };

  return (
    <ChakraProvider>
      <Container maxW="container.lg" className="pt-4">
        <Heading as="h1" size="lg" mb={4}>
          Estadísticas de Equipos
        </Heading>

        <VStack spacing={4} align="stretch">
          <HStack spacing={4} justify="space-between">
            <Link href="/pruebas" passHref>
              <Button as="a">Volver a Pruebas</Button>
            </Link>

            {/* NUEVOS FILTROS DE AÑO */}
            <VStack align="flex-end" spacing={1}>
              <HStack spacing={2}>
                <Text fontSize="sm" fontWeight="medium" whiteSpace="nowrap">Filtrar por año:</Text>
                <Select 
                  placeholder="Desde" 
                  size="sm" 
                  w="110px"
                  value={fromYear}
                  onChange={(e) => setFromYear(e.target.value)}
                  isInvalid={!!yearError}
                >
                  {worldCupYears.map(year => <option key={year} value={year}>{year}</option>)}
                </Select>
                <Select 
                  placeholder="Hasta" 
                  size="sm" 
                  w="110px"
                  value={toYear}
                  onChange={(e) => setToYear(e.target.value)}
                  isInvalid={!!yearError}
                >
                  {worldCupYears.map(year => <option key={year} value={year}>{year}</option>)}
                </Select>
                <Button size="sm" colorScheme="blue" onClick={handleApplyFilter} isDisabled={!!yearError || !fromYear}>Aplicar</Button>
              </HStack>
              {yearError && (
                <Text fontSize="xs" color="red.500" pr="4.5rem">
                  {yearError}
                </Text>
              )}
            </VStack>
          </HStack>

          <Box>
            <Heading as="h2" size="md" mb={2}>Selecciona un equipo</Heading>
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
                    <StatNumber color="green.500">{stats.wins}</StatNumber>
                    </Stat>
                    <Stat>
                    <StatLabel>Derrotas</StatLabel>
                    <StatNumber color="red.500">{stats.losses}</StatNumber>
                    </Stat>
                    <Stat>
                    <StatLabel>Empates</StatLabel>
                    <StatNumber color="gray.500">{stats.draws}</StatNumber>
                    </Stat>
                    <Stat>
                      <StatLabel>Goles a Favor</StatLabel>
                      <StatNumber color="green.500">{stats.goals_for}</StatNumber>
                    </Stat>
                    <Stat>
                      <StatLabel>Goles en Contra</StatLabel>
                      <StatNumber color="red.500">{stats.goals_against}</StatNumber>
                    </Stat>
                </StatGroup>

                <Box mt={4}>
                    {/* Etiquetas de porcentaje arriba de la barra */}
                    <HStack justify="space-between" mb={2} fontSize="sm" fontWeight="bold">
                        <Box color="green.600">{stats.win_percentage.toFixed(2)}% Victorias</Box>
                        <Box color="red.600">{stats.loss_percentage.toFixed(2)}% Derrotas</Box>
                    </HStack>

                    {/* BARRA UNIFICADA PERSONALIZADA */}
                    <Box 
                    w="100%" 
                    h="24px" 
                    bg="gray.100" 
                    borderRadius="full" 
                    overflow="hidden" 
                    display="flex"
                    boxShadow="inner"
                    >
                    {/* Segmento Verde (Victorias) */}
                    <Box 
                        w={`${stats.win_percentage.toFixed(2)}%`} 
                        h="100%" 
                        bg="green.400"
                        transition="width 0.5s ease"
                        title={`Victorias: ${stats.win_percentage.toFixed(2)}%`}
                    />
                    
                    {/* Segmento Gris (Empates - Importante para que la matemática visual cuadre) */}
                    {/* Si no hay empates, el ancho será 0% y no se verá */}
                    <Box 
                        w={`${stats.draw_percentage.toFixed(2)}%`} 
                        h="100%" 
                        bg="gray.300"
                        transition="width 0.5s ease"
                        title={`Empates: ${stats.draw_percentage.toFixed(2)}%`}
                    />

                    {/* Segmento Rojo (Derrotas) */}
                    <Box 
                        w={`${stats.loss_percentage.toFixed(2)}%`} 
                        h="100%" 
                        bg="red.400"
                        transition="width 0.5s ease"
                        title={`Derrotas: ${stats.loss_percentage.toFixed(2)}%`}
                    />
                    </Box>
                    
                    {/* Opcional: Mostrar el porcentaje de empates abajo si existe */}
                    {stats.draw_percentage > 0 && (
                        <Box textAlign="center" fontSize="xs" color="gray.500" mt={1}>
                            Empates: {stats.draw_percentage.toFixed(2)}%
                        </Box>
                    )}
                </Box>
                </Box>
            )}
        </VStack>
      </Container>
    </ChakraProvider>
  );
}
