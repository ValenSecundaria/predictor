'use client';
import 'bootstrap/dist/css/bootstrap.min.css';
import React, { useState, Fragment } from 'react';
import { ChakraProvider, Container, Heading, Button, Code, Box, Spinner, Alert, AlertIcon } from '@chakra-ui/react';

type Goal = {
  player: string;
  minute: number;
};

type Match = {
  team_a: string;
  team_b: string;
  score_a: number;
  score_b: number;
  goals: Goal[];
};

export default function Page() {
  const [mode, setMode] = useState<'usuario' | 'pruebas' | null>(null);
  const [data, setData] = useState<Match[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const consultar = async () => {
    try {
      setErr(null);
      setLoading(true);
      const res = await fetch('/api/v1/analisis', { cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as Match[];
      setData(json);
    } catch (e: any) {
      setErr(e?.message ?? 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChakraProvider>
      <Container maxW="container.md" className="pt-4">
        {mode === null && (
          <Box textAlign="center" py={10} px={6}>
            <Heading as="h2" size="xl" mt={6} mb={2}>
              Bienvenido al Predictor Mundial
            </Heading>
            <p className="mb-4">Selecciona un modo para continuar</p>
            <Button colorScheme="teal" onClick={() => setMode('usuario')} mr={3}>
              Modo Usuario
            </Button>
            <Button colorScheme="blue" onClick={() => setMode('pruebas')}>
              Modo pruebas
            </Button>
          </Box>
        )}

        {mode === 'usuario' && (
          <Box>
            <Alert status="info">
              <AlertIcon />
              En construcción
            </Alert>
            <Button mt={4} onClick={() => setMode(null)}>Volver</Button>
          </Box>
        )}

        {mode === 'pruebas' && (
          <Fragment>
            <Heading as="h1" size="lg" mb={4}>
              ⚽ Modo Pruebas: FastAPI + Next (Chakra + Bootstrap)
            </Heading>

            <div className="mb-3 d-flex align-items-center">
              <Button colorScheme="teal" onClick={consultar} isDisabled={loading} mr={4}>
                {loading ? 'Consultando…' : 'Consultar análisis'}
              </Button>
              <Button onClick={() => setMode(null)}>Volver</Button>
            </div>

            {loading && (
              <Box mb={3}>
                <Spinner mr={2} /> Ejecutando pipeline (extracción de txt → parseo)...
              </Box>
            )}

            {err && (
              <Alert status="error" mb={3}>
                <AlertIcon />
                {err}
              </Alert>
            )}

            {data && (
              <Box borderWidth="1px" borderRadius="lg" p={4}>
                <Heading as="h2" size="md" mb={2}>Respuesta</Heading>
                <Code whiteSpace="pre" width="100%" p={3}>
                  {JSON.stringify(data, null, 2)}
                </Code>
              </Box>
            )}
          </Fragment>
        )}
      </Container>
    </ChakraProvider>
  );
}
