'use client';

import React, { useState, useEffect } from 'react';
import {
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
  SimpleGrid,
} from '@chakra-ui/react';
import Link from 'next/link';
import HistoryStats from '../../components/HistoryStats';
import PredictionResult from '../../components/PredictionResult';
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
  const [prediction, setPrediction] = useState<any | null>(null);
  const [historyStats, setHistoryStats] = useState<HeadToHeadStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
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
      setError('Selecciona dos equipos distintos para comparar.');
      setHistoryStats(null);
      setPrediction(null);
      return;
    }

    setPrediction(null);
    setHistoryStats(null);
    setPredicting(true);
    setError(null);

    try {
      // 1. Fetch History
      const resHistory = await fetch(`/api/v1/predict/history/${teamA}/${teamB}`);
      if (resHistory.ok) {
        const data: HeadToHeadStats = await resHistory.json();
        setHistoryStats(data);
      }

      // 2. Fetch Prediction
      const resPredict = await fetch(`/api/v1/predict/match-prediction/${teamA}/${teamB}`);
      if (resPredict.ok) {
        const data = await resPredict.json();
        setPrediction(data);
      } else {
        throw new Error("Error al obtener la predicción");
      }

    } catch (e: any) {
      console.error(e);
      setError("Hubo un error al realizar la predicción. Inténtalo de nuevo.");
    } finally {
      setPredicting(false);
    }
  };

  const teamAName = teams.find(t => t.code === teamA)?.name || teamA;
  const teamBName = teams.find(t => t.code === teamB)?.name || teamB;

  return (
    <Container maxW="container.md" py={10}>
      <Box mb={6}>
        <HStack justify="space-between" align="flex-start">
          <Heading as="h2" size="lg">
            Predicción de Partido
          </Heading>
          <Link href="/">
            <Button variant="outline" size="sm">
              Volver al Menú
            </Button>
          </Link>
        </HStack>
        <Text mt={2} fontSize="sm" color="gray.600">
          Analiza el enfrentamiento entre dos equipos basado en estadísticas avanzadas.
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

      <Card mb={6} boxShadow="md">
        <CardBody>
          <VStack spacing={4} align="stretch">
            <SimpleGrid columns={2} spacing={4}>
              <Box>
                <Text mb={1} fontWeight="semibold">Local (Equipo A)</Text>
                <Select
                  value={teamA}
                  onChange={(e) => setTeamA(e.target.value)}
                  isDisabled={loading || predicting}
                >
                  {teams.map((team) => (
                    <option key={team.code} value={team.code}>
                      {team.name}
                    </option>
                  ))}
                </Select>
              </Box>

              <Box>
                <Text mb={1} fontWeight="semibold">Visitante (Equipo B)</Text>
                <Select
                  value={teamB}
                  onChange={(e) => setTeamB(e.target.value)}
                  isDisabled={loading || predicting}
                >
                  {teams.map((team) => (
                    <option key={team.code} value={team.code}>
                      {team.name}
                    </option>
                  ))}
                </Select>
              </Box>
            </SimpleGrid>

            <Button
              colorScheme="blue"
              size="lg"
              onClick={handleCompare}
              isLoading={predicting}
              loadingText="Analizando..."
              isDisabled={loading || !teamA || !teamB}
              bgGradient="linear(to-r, blue.500, blue.600)"
              _hover={{ bgGradient: "linear(to-r, blue.600, blue.700)" }}
            >
              Predecir Resultado
            </Button>
          </VStack>
        </CardBody>
      </Card>

      {prediction && (
        <PredictionResult
          prediction={prediction}
          teamAName={teamAName}
          teamBName={teamBName}
        />
      )}

      {historyStats && (
        <HistoryStats stats={historyStats} teamAName={teamAName} teamBName={teamBName} />
      )}

    </Container>
  );
}
