'use client';
import 'bootstrap/dist/css/bootstrap.min.css';
import React, { useState } from 'react';
import { ChakraProvider, Container, Heading, Button, Code, Box, Spinner, Alert, AlertIcon } from '@chakra-ui/react';

type Analitica = {
  total_registros: number;
  registros_validos: number;
  goles_por_equipo: Record<string, number>;
};

export default function Page() {
  const [data, setData] = useState<Analitica | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const consultar = async () => {
    try {
      setErr(null);
      setLoading(true);
      const res = await fetch('/api/v1/analisis', { cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as Analitica;
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
        <Heading as="h1" size="lg" mb={4}>
          ⚽ Plantilla: FastAPI + Next (Chakra + Bootstrap)
        </Heading>

        <div className="mb-3">
          <Button colorScheme="teal" onClick={consultar} isDisabled={loading}>
            {loading ? 'Consultando…' : 'Consultar análisis'}
          </Button>
        </div>

        {loading && (
          <Box mb={3}>
            <Spinner mr={2} /> Ejecutando pipeline (extracción → limpieza → analítica)...
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

        <Box mt={6} className="alert alert-info">
          Bootstrap activo (alert) + Chakra activo (Componentes). Ambos conviven sin conflicto.
        </Box>
      </Container>
    </ChakraProvider>
  );
}
