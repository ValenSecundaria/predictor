'use client';

import React, { useState, useEffect } from 'react';
import {
  ChakraProvider,
  Container,
  Heading,
  Box,
  Select,
  Button,
  Text,
  VStack,
  HStack,
  Card,
  CardBody,
  Spinner,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import Link from 'next/link';
import HistoryStats from '../../components/HistoryStats';
import { HeadToHeadStats } from '../../types';

// Tipo para los equipos que vienen de la API
type Team = {
  name: string;
  code: string;
};

export default function EquipoGanadorPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [teamA, setTeamA] = useState<string>('');
  const [teamB, setTeamB] = useState<string>('');
  const [result, setResult] = useState<string | null>(null);
  const [historyStats, setHistoryStats] = useState<HeadToHeadStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch('/api/v1/teams');
        if (!res.ok) {
          throw new Error(`Error al obtener los equipos: HTTP ${res.status}`);
        }
        const data: Team[] = await res.json();
        setTeams(data);
        // Inicializar los select con los dos primeros equipos si existen
        if (data.length >= 2) {
          setTeamA(data[0].code);
          setTeamB(data[1].code);
        }
      } catch (e: any) {
        setError(e.message ?? 'Ocurrió un error inesperado.');
      } finally {
        setLoading(false);
      }
    };

    fetchTeams();
  }, []);

  const handleCompare = async () => {
    if (teamA === teamB) {
      setResult('Selecciona dos equipos distintos para comparar.');
      setHistoryStats(null);
      return;
    }

    setResult(null);
    setHistoryStats(null);

    try {
      const res = await fetch(`/api/v1/predict/history/${teamA}/${teamB}`);
      if (res.ok) {
        const data: HeadToHeadStats = await res.json();
        setHistoryStats(data);
      } else {
        console.error("Error fetching history stats");
      }
    } catch (e) {
      console.error(e);
    }

    const teamAName = teams.find(t => t.code === teamA)?.name;
    const teamBName = teams.find(t => t.code === teamB)?.name;
    const winner = (teamAName ?? '').localeCompare(teamBName ?? '') < 0 ? teamAName : teamBName;
    setResult(
      `Según este mock de datos, ${winner} tiene una ligera ventaja histórica sobre su rival.`
    );
  };

  const teamAName = teams.find(t => t.code === teamA)?.name || teamA;
  const teamBName = teams.find(t => t.code === teamB)?.name || teamB;

  return (
    <ChakraProvider>
      <Container maxW="container.md" py={10}>
        <Box mb={6}>
          <HStack justify="space-between" align="flex-start">
            <Heading as="h2" size="lg">
              Comparar equipos - Mock
            </Heading>
            <Link href="/">
              <Button variant="outline" size="sm">
                Volver al Menú
              </Button>
            </Link>
          </HStack>
          <Text mt={2} fontSize="sm" color="gray.600">
            Selecciona dos equipos para ver un ejemplo de comparación (mock).
          </Text>
        </Box>

        {loading && (
          <Box textAlign="center" p={5}>
            <Spinner size="xl" />
            <Text mt={2}>Cargando equipos...</Text>
          </Box>
        )}

        {error && (
          <Alert status="error" mb={6}>
            <AlertIcon />
            {error}
          </Alert>
        )}

        <Card mb={6}>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Box>
                <Text mb={1} fontWeight="semibold">
                  Equipo A
                </Text>
                <Select
                  value={teamA}
                  onChange={(e) => setTeamA(e.target.value)}
                  isDisabled={loading || !!error}
                >
                  {teams.map((team) => (
                    <option key={team.code} value={team.code}>
                      {team.name}
                    </option>
                  ))}
                </Select>
              </Box>

              <Box>
                <Text mb={1} fontWeight="semibold">
                  Equipo B
                </Text>
                <Select
                  value={teamB}
                  onChange={(e) => setTeamB(e.target.value)}
                  isDisabled={loading || !!error}
                >
                  {teams.map((team) => (
                    <option key={team.code} value={team.code}>
                      {team.name}
                    </option>
                  ))}
                </Select>
              </Box>

              <Button colorScheme="teal" onClick={handleCompare} isDisabled={loading || !!error || !teamA || !teamB}>
                Comparar equipos
              </Button>
            </VStack>
          </CardBody>
        </Card>

        {historyStats && (
          <HistoryStats stats={historyStats} teamAName={teamAName} teamBName={teamBName} />
        )}

        {result && (
          <Card mt={6}>
            <CardBody>
              <Text fontWeight="bold" mb={2}>
                Resultado (mock):
              </Text>
              <Text>{result}</Text>
            </CardBody>
          </Card>
        )}
      </Container>
    </ChakraProvider>
  );
}
